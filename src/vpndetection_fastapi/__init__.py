"""Official FastAPI and Starlette middleware for the VPNDetection API.

Classifies the visitor behind each request and hangs the answer off
``request.state.vpndetection``, where your endpoints can read it. Blocking is opt-in.

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

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send
from vpndetection.middleware import (
    AsyncCore,
    IpSelector,
    Lookup,
    Options,
    RequestView,
    Selectors,
    bind_selectors,
)

__all__ = [
    "VPNDetectionMiddleware",
    "default_ip_selector",
    "header_ip_selector",
    "lookup",
    "xff_ip_selector",
]

__version__ = "2.0.3"

_SELECTORS: Selectors[Request] = bind_selectors(
    lambda request: RequestView(
        header=lambda name: request.headers.get(name),
        framework_ip=lambda: request.client.host if request.client else None,
    )
)

#: ``request.client.host``, which is the socket peer unless the app was started with
#: uvicorn's ``--proxy-headers``.
#:
#: Behind a load balancer without it, every visitor looks like the load balancer - a
#: datacenter address a hosting rule would block them all for. If you are behind one,
#: pass ``--proxy-headers --forwarded-allow-ips=<your proxy>`` (the server's own answer,
#: and the one that knows your topology) or use :func:`header_ip_selector`.
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
