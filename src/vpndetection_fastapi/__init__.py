"""Official FastAPI and Starlette middleware for the VPNDetection API.

Classifies the visitor behind each request and hangs the answer off
``request.state.vpndetection``, where your endpoints can read it. Blocking is opt-in, for
every endpoint or, in FastAPI, for one with the :func:`block_if` dependency.

    from fastapi import FastAPI
    from vpndetection_fastapi import VPNDetectionMiddleware

    app = FastAPI()
    app.add_middleware(VPNDetectionMiddleware, api_key=os.environ["VPNDETECTION_API_KEY"])

Pure ASGI, so this covers Starlette and Litestar too, not only FastAPI. The
framework-agnostic half lives in ``vpndetection.middleware``.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send
from vpndetection.middleware import (
    AsyncCore,
    Conditions,
    Guard,
    IpSelector,
    Lookup,
    MissingFieldAction,
    Options,
    RequestView,
    Selectors,
    bind_selectors,
)

__all__ = [
    "VPNDetectionMiddleware",
    "block_if",
    "default_ip_selector",
    "header_ip_selector",
    "lookup",
    "xff_ip_selector",
]

__version__ = "2.1.2"

# Set on a request ``skip`` claimed, so block_if can tell it from one the middleware
# never saw.
_SKIPPED = "_vpndetection_skipped"

_SELECTORS: Selectors[Request] = bind_selectors(
    lambda request: RequestView(
        header=lambda name: request.headers.get(name),
        framework_ip=lambda: request.client.host if request.client else None,
    )
)

#: ``request.client.host``. uvicorn reads proxy headers into it by default, but only
#: from a peer ``--forwarded-allow-ips`` trusts, which defaults to ``127.0.0.1,::1``.
#:
#: Behind a proxy anywhere else, every visitor looks like the proxy, usually a private
#: address that is answered locally, so nobody is flagged and the private-address
#: warning is the only sign. Pass ``--forwarded-allow-ips=<your proxy's address or
#: subnet>``, never ``*``, which takes the left-most ``X-Forwarded-For`` entry a visitor
#: can forge, or use :func:`header_ip_selector`.
default_ip_selector: IpSelector[Request] = _SELECTORS.default

#: An address from ``X-Forwarded-For``.
#:
#: The LEFT-MOST entry (``depth`` 0) is whatever the caller sent, because proxies
#: append to this header. It is only trustworthy when an edge you control overwrites
#: it. When you know how many proxies sit in front, count from the right:
#: ``xff_ip_selector(1)`` is the address your nearest proxy saw.
xff_ip_selector = _SELECTORS.xff

#: An address from a single-value header your edge writes -
#: ``header_ip_selector("CF-Connecting-IP")`` behind Cloudflare. Falls back to
#: ``request.client.host`` when the header is absent.
header_ip_selector = _SELECTORS.header


def lookup(request: Request) -> Lookup | None:
    """What the middleware found out about this visitor.

    None when the middleware has not run for this route, or when ``skip`` claimed it.
    """
    return getattr(request.state, "vpndetection", None)


def block_if(
    condition: Conditions,
    *,
    status_code: int = 403,
    detail: Any = "access denied",
    fail_closed: bool = False,
    on_missing_field: MissingFieldAction = "warn",
    on_warn: Callable[[str], None] | None = None,
) -> Callable[[Request], Awaitable[Lookup | None]]:
    """A FastAPI dependency refusing one endpoint to a visitor matching ``condition``.

    The middleware's ``block_condition`` refuses on every endpoint; this refuses on the
    path operations, routers or apps that depend on it, with an ``HTTPException`` of
    ``status_code`` and ``detail``::

        @app.get("/checkout", dependencies=[Depends(block_if({"is_vpn": True}))])
        async def checkout(): ...

    As a parameter it hands the endpoint the answer, or None for a request ``skip``
    claimed. It judges the answer the middleware already attached, so the visitor is not
    looked up again, and a member your plan does not serve is reported once, as the
    middleware's own condition reports it. A condition that constrains nothing is
    refused when the dependency is built.

    A request ``skip`` claimed carries no answer and reaches the endpoint, and so does
    one whose lookup failed unless you set ``fail_closed``. A request the middleware
    never saw raises ``RuntimeError``: a check that silently never ran would be worse
    than none.
    """
    guard = Guard(
        condition,
        fail_closed=fail_closed,
        on_missing_field=on_missing_field,
        on_warn=on_warn,
        name="block_if",
    )

    async def dependency(request: Request) -> Lookup | None:
        found = lookup(request)
        if found is None:
            if getattr(request.state, _SKIPPED, False):
                return None
            raise RuntimeError(
                "vpndetection: block_if found no answer on this request; add "
                "VPNDetectionMiddleware to the app"
            )
        if guard.blocks(found):
            raise HTTPException(status_code=status_code, detail=detail)
        return found

    return dependency


class VPNDetectionMiddleware:
    """Classify the visitor, and optionally refuse the request.

    Takes everything :class:`vpndetection.middleware.Options` does, plus ``on_blocked``.

    Written as raw ASGI rather than on ``BaseHTTPMiddleware``, which wraps the response
    in a streaming bridge that breaks background tasks and server-sent events - a cost
    no middleware that only reads the request should impose.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        on_blocked: Callable[[Request, Lookup], Response | Awaitable[Response]] | None = None,
        **options: Any,
    ) -> None:
        self.app = app
        self._on_blocked = on_blocked or _refuse
        self._core: AsyncCore[Request] = AsyncCore(Options(**options), default_ip_selector)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive=receive)
        found = await self._core.evaluate(request)
        if found is None:
            setattr(request.state, _SKIPPED, True)
            await self.app(scope, receive, send)
            return
        # request.state is backed by scope["state"], so this reaches the Request the
        # endpoint builds later over the same scope even though it is a different
        # object.
        request.state.vpndetection = found
        if found.blocked:
            response = self._on_blocked(request, found)
            if isinstance(response, Response):
                await response(scope, receive, send)
            else:
                await (await response)(scope, receive, send)
            return
        await self.app(scope, receive, send)


def _refuse(_request: Request, _lookup: Lookup) -> Response:
    return JSONResponse({"error": "access denied"}, status_code=403)
