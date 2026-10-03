"""The adapter, through a real ASGI app, plus the shared corpus.

A test client connects from ``testclient``/``127.0.0.1``, which is a bogon and is
answered locally without a request. Anything that needs a served answer therefore has
to arrive wearing a public address, through a selector.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

import httpx
import pytest
from fastapi import Depends, FastAPI
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from vpndetection import AsyncVPNDetection

from vpndetection_fastapi import (
    VPNDetectionMiddleware,
    block_if,
    header_ip_selector,
    lookup,
    xff_ip_selector,
)

PUBLIC_IP = "45.83.91.1"
CORPUS = json.loads(
    (pathlib.Path(__file__).parent.parent / "testdata/testdata.json").read_text()
)
MIDDLEWARE = CORPUS["middleware"]


def serving(body: dict[str, Any], *, status: int = 200) -> AsyncVPNDetection:
    """A client whose every answer is ``body``, recording what it was asked about."""

    async def handle(request: httpx.Request) -> httpx.Response:
        ip = request.url.path.lstrip("/")
        asked.append(ip)
        return httpx.Response(status, json={"ip": ip, **body})

    asked: list[str] = []
    client = AsyncVPNDetection(cache=False, retries=0, transport=httpx.MockTransport(handle))
    client.asked = asked  # type: ignore[attr-defined]
    return client


async def index(request: Request) -> JSONResponse:
    found = lookup(request)
    return JSONResponse(
        {
            "ip": found.ip if found else None,
            "is_vpn": found.result.is_vpn if found and found.result else None,
            "is_bogon": found.result.is_bogon if found and found.result else None,
            "error": type(found.error).__name__ if found and found.error else None,
            "attached": found is not None,
        }
    )


def app_with(**options: Any) -> Starlette:
    app = Starlette(routes=[Route("/", index)])
    app.add_middleware(VPNDetectionMiddleware, **options)
    return app


def get(app: Starlette, headers: dict[str, str] | None = None) -> tuple[int, dict[str, Any]]:
    # A real peer address, because TestClient's default is the literal string
    # "testclient" - which is not an address at all, so it is not a bogon and would be
    # sent to the API as if it were one.
    with TestClient(app, client=("127.0.0.1", 12345)) as client:
        response = client.get("/", headers=headers or {})
    return response.status_code, response.json()


def fixed_ip(_request: Any) -> str:
    return PUBLIC_IP


def test_enriches_the_request_and_leaves_the_decision_to_the_app() -> None:
    client = serving({"is_vpn": True, "vpn": {"provider": "nordvpn"}})
    status, body = get(app_with(client=client, ip_selector=fixed_ip))
    assert status == 200
    assert body["attached"] is True and body["is_vpn"] is True and body["ip"] == PUBLIC_IP
    assert client.asked == [PUBLIC_IP]


def test_blocks_when_the_condition_matches_and_the_endpoint_never_runs() -> None:
    vpn = serving({"is_vpn": True, "vpn": {"provider": "nordvpn"}})
    status, body = get(
        app_with(client=vpn, ip_selector=fixed_ip, block_condition={"is_vpn": True})
    )
    assert status == 403
    assert body == {"error": "access denied"}

    clean = serving({"is_vpn": False, "vpn": {}})
    status, _ = get(
        app_with(client=clean, ip_selector=fixed_ip, block_condition={"is_vpn": True})
    )
    assert status == 200


def test_a_condition_reaches_the_evidence_fields() -> None:
    nord = serving({"is_vpn": True, "vpn": {"provider": "nordvpn"}})
    status, _ = get(
        app_with(
            client=nord, ip_selector=fixed_ip, block_condition={"vpn": {"provider": "mullvad"}}
        )
    )
    assert status == 200, "a different provider must not match"

    mullvad = serving({"is_vpn": True, "vpn": {"provider": "MULLVAD"}})
    status, _ = get(
        app_with(
            client=mullvad,
            ip_selector=fixed_ip,
            block_condition={"vpn": {"provider": "mullvad"}},
        )
    )
    assert status == 403, "a provider must compare without case"


def test_on_blocked_replaces_the_refusal() -> None:
    client = serving({"is_vpn": True, "vpn": {"provider": "nordvpn"}})
    status, body = get(
        app_with(
            client=client,
            ip_selector=fixed_ip,
            block_condition={"is_vpn": True},
            on_blocked=lambda request, found: JSONResponse(
                {"why": found.result.vpn.provider}, status_code=451
            ),
        )
    )
    assert status == 451
    assert body == {"why": "nordvpn"}


def test_skip_leaves_the_request_untouched() -> None:
    client = serving({"is_vpn": True})
    status, body = get(
        app_with(
            client=client,
            ip_selector=fixed_ip,
            block_condition={"is_vpn": True},
            skip=lambda request: request.url.path == "/",
        )
    )
    assert status == 200 and body["attached"] is False
    assert client.asked == []


def test_a_failing_lookup_lets_the_visitor_through() -> None:
    failing = serving({"error": "boom"}, status=500)
    status, body = get(
        app_with(client=failing, ip_selector=fixed_ip, block_condition={"is_vpn": True})
    )
    assert status == 200
    assert body["error"] == "VPNDetectionError"


# The test that matters. Every other assertion here would pass whether or not the
# selector is right, because a direct connection has nothing to confuse.
def test_a_forged_x_forwarded_for_is_ignored_by_default() -> None:
    client = serving({"is_vpn": True})
    _, body = get(app_with(client=client), {"X-Forwarded-For": PUBLIC_IP})
    assert body["ip"] == "127.0.0.1", "client.host is the peer; the header is a forgery"
    assert client.asked == [], "and a bogon is answered locally, so nothing was asked"

    explicit = serving({"is_vpn": True})
    _, body = get(
        app_with(client=explicit, ip_selector=xff_ip_selector()), {"X-Forwarded-For": PUBLIC_IP}
    )
    assert body["ip"] == PUBLIC_IP
    assert explicit.asked == [PUBLIC_IP]


def test_a_header_selector_reads_the_edge_that_writes_it() -> None:
    client = serving({"is_vpn": True})
    _, body = get(
        app_with(client=client, ip_selector=header_ip_selector("CF-Connecting-IP")),
        {"CF-Connecting-IP": "45.83.91.9"},
    )
    assert body["ip"] == "45.83.91.9"
    assert client.asked == ["45.83.91.9"]


def test_depth_counts_trusted_hops_from_the_right() -> None:
    client = serving({"is_vpn": True})
    get(
        app_with(client=client, ip_selector=xff_ip_selector(1)),
        {"X-Forwarded-For": f"{PUBLIC_IP}, 70.41.3.18, 150.172.238.178"},
    )
    assert client.asked == ["150.172.238.178"]


def test_a_private_client_address_is_answered_locally_and_never_blocks() -> None:
    client = serving({"is_vpn": True})
    status, body = get(
        app_with(
            client=client,
            block_condition={"is_vpn": True},
            ip_selector=lambda request: "10.0.0.7",
        )
    )
    assert status == 200, "local development must not lock you out of your own app"
    assert body["is_bogon"] is True
    assert client.asked == []


def test_a_condition_that_constrains_nothing_is_refused_at_construction() -> None:
    with pytest.raises(ValueError, match="constrains nothing"):
        VPNDetectionMiddleware(
            lambda scope, receive, send: None, block_condition={"is_vpn": False}
        )


def test_a_sync_client_is_refused_by_the_async_middleware() -> None:
    from vpndetection import VPNDetection as SyncClient

    with pytest.raises(TypeError, match="use Core"):
        VPNDetectionMiddleware(lambda scope, receive, send: None, client=SyncClient())


@pytest.mark.parametrize("case", MIDDLEWARE["conditions"], ids=lambda c: c["name"])
def test_corpus_conditions(case: dict[str, Any]) -> None:
    ip = case.get("bogon") or case["body"]["ip"]
    client = serving({k: v for k, v in (case.get("body") or {}).items() if k != "ip"})
    warnings: list[str] = []
    status, _ = get(
        app_with(
            client=client,
            ip_selector=lambda _request, ip=ip: ip,
            block_condition=case["condition"],
            on_warn=warnings.append,
        )
    )
    assert status == (403 if case["expect"]["blocked"] else 200), case["why"]
    reported = [w for w in warnings if "does not include" in w]
    assert len(reported) == (1 if case["expect"]["missing"] else 0), case["why"]
    for member in case["expect"]["missing"]:
        assert member in reported[0], case["why"]


def fastapi_with(guard: dict[str, Any] | None = None, **options: Any) -> FastAPI:
    """A FastAPI app with the middleware, whose ``/guarded`` depends on
    ``block_if(**guard)`` and ``/`` on nothing."""
    app = FastAPI()
    # A default rather than Annotated: under postponed annotations FastAPI resolves an
    # annotation in module globals, where this per-app dependency does not live.
    check = block_if(**(guard or {"condition": {"is_vpn": True}}))
    app.add_api_route("/", index)

    @app.get("/guarded")
    async def guarded(found: Any = Depends(check)) -> dict[str, Any]:  # noqa: B008
        return {"attached": found is not None, "ip": found.ip if found else None}

    app.add_middleware(VPNDetectionMiddleware, **options)
    return app


def fetch(app: Any, url: str) -> tuple[int, dict[str, Any]]:
    with TestClient(app, client=("127.0.0.1", 12345)) as client:
        response = client.get(url)
    return response.status_code, response.json()


def test_block_if_refuses_only_the_endpoint_that_depends_on_it() -> None:
    vpn = serving({"is_vpn": True, "vpn": {"provider": "nordvpn"}})
    app = fastapi_with(client=vpn, ip_selector=fixed_ip)
    status, body = fetch(app, "/guarded")
    assert status == 403
    assert body == {"detail": "access denied"}
    status, body = fetch(app, "/")
    assert status == 200, "the middleware itself has no condition, so other endpoints are open"
    assert body["is_vpn"] is True
    assert vpn.asked == [PUBLIC_IP, PUBLIC_IP], "one lookup per request, none by the dependency"

    clean = serving({"is_vpn": False, "vpn": {}})
    status, body = fetch(fastapi_with(client=clean, ip_selector=fixed_ip), "/guarded")
    assert status == 200
    assert body == {"attached": True, "ip": PUBLIC_IP}, "the dependency hands over the answer"


def test_block_if_takes_its_status_and_detail() -> None:
    vpn = serving({"is_vpn": True, "vpn": {"provider": "nordvpn"}})
    guard = {"condition": {"is_vpn": True}, "status_code": 451, "detail": "not from a VPN"}
    status, body = fetch(fastapi_with(guard, client=vpn, ip_selector=fixed_ip), "/guarded")
    assert status == 451
    assert body == {"detail": "not from a VPN"}


def test_block_if_lets_a_skipped_request_through() -> None:
    vpn = serving({"is_vpn": True})
    app = fastapi_with(client=vpn, ip_selector=fixed_ip, skip=lambda request: True)
    status, body = fetch(app, "/guarded")
    assert status == 200
    assert body == {"attached": False, "ip": None}
    assert vpn.asked == []


def test_block_if_fails_open_unless_told_to_fail_closed() -> None:
    failing = serving({"error": "boom"}, status=500)
    status, _ = fetch(fastapi_with(client=failing, ip_selector=fixed_ip), "/guarded")
    assert status == 200

    guard = {"condition": {"is_vpn": True}, "fail_closed": True}
    status, body = fetch(fastapi_with(guard, client=failing, ip_selector=fixed_ip), "/guarded")
    assert status == 403
    assert body == {"detail": "access denied"}


def test_block_if_without_the_middleware_is_an_error() -> None:
    app = FastAPI()
    check = block_if({"is_vpn": True})

    @app.get("/guarded")
    async def guarded(found: Any = Depends(check)) -> None:  # noqa: B008
        return None

    with pytest.raises(RuntimeError, match="add VPNDetectionMiddleware"):
        fetch(app, "/guarded")


def test_block_if_refuses_a_condition_that_constrains_nothing() -> None:
    with pytest.raises(ValueError, match="constrains nothing"):
        block_if({"is_vpn": False})


def test_block_if_warns_once() -> None:
    free = serving({"is_vpn": True})
    warnings: list[str] = []
    guard = {"condition": {"is_hosting": True}, "on_warn": warnings.append}
    app = fastapi_with(guard, client=free, ip_selector=fixed_ip)
    fetch(app, "/guarded")
    fetch(app, "/guarded")
    assert len(warnings) == 1
    assert warnings[0].startswith("block_if names is_hosting")


@pytest.mark.parametrize("case", MIDDLEWARE["conditions"], ids=lambda c: c["name"])
def test_corpus_conditions_through_block_if(case: dict[str, Any]) -> None:
    ip = case.get("bogon") or case["body"]["ip"]
    client = serving({k: v for k, v in (case.get("body") or {}).items() if k != "ip"})
    warnings: list[str] = []
    app = fastapi_with(
        {"condition": case["condition"], "on_warn": warnings.append},
        client=client,
        ip_selector=lambda _request, ip=ip: ip,
    )
    status, _ = fetch(app, "/guarded")
    assert status == (403 if case["expect"]["blocked"] else 200), case["why"]
    reported = [w for w in warnings if "does not include" in w]
    assert len(reported) == (1 if case["expect"]["missing"] else 0), case["why"]
    for member in case["expect"]["missing"]:
        assert member in reported[0], case["why"]
