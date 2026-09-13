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
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from vpndetection import AsyncVPNDetection

from vpndetection_fastapi import (
    VPNDetectionMiddleware,
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
