# [<img src="https://s3.vpndetection.io/vpndetection-public/brand/mark.svg" alt="VPNDetection" height="28"/>](https://vpndetection.io/) VPNDetection FastAPI Middleware

[![PyPI](https://img.shields.io/pypi/v/vpndetection-fastapi.svg)](https://pypi.org/project/vpndetection-fastapi/)
[![license](https://img.shields.io/pypi/l/vpndetection-fastapi.svg)](LICENSE)

The official FastAPI middleware for the [VPNDetection](https://vpndetection.io) API: it checks each visitor's IP for VPN, Tor and proxy use, and can block them with a 403.

It classifies the visitor behind each request: VPN, residential proxy, Tor, hosting, CDN or relay. Then it hands the answer to your code. Blocking is opt-in.

## Getting Started

```bash
pip install vpndetection-fastapi
```

Requires Python 3.11 or newer.

No API key needed to start. Without one, a lookup is on Unlimited, the free plan, which answers VPN, Tor and relay detection with no daily or monthly cap. A paid plan's key adds the hosting, CDN and proxy flags and the provider behind each flag: create one in the [console](https://app.vpndetection.io). A free account tries every field.

```python
from fastapi import FastAPI
from vpndetection_fastapi import VPNDetectionMiddleware

app = FastAPI()
app.add_middleware(VPNDetectionMiddleware, api_key=os.environ["VPNDETECTION_API_KEY"])
```

Pure ASGI, so this works on Starlette and Litestar too, not only FastAPI.

```python
from fastapi import Request
from vpndetection_fastapi import lookup


@app.get("/")
async def index(request: Request):
    found = lookup(request)
    return {"vpn": found.result.is_vpn}
```

A request your `skip` claims gets no answer, and `lookup(request)` is `None` for it.

By default nothing is blocked. Every request gets an answer and your own code decides what to do with it, since whether a VPN visitor is a problem depends on what they're doing.

## Blocking

Pass a `block_condition` and a matching request is answered with `403` and never reaches your code.

```python
block_condition = {"is_vpn": True}
```

A condition is written in the shape of a result, keyed by the same names the API uses, and only the members you name are considered. That lets it reach the evidence, not just the flags:

```python
{"is_vpn": True, "vpn": {"provider": "nordvpn"}}  # one provider
{"is_resproxy": True, "resproxy": {"hits": {"gte": 5}}}  # a numeric threshold
{"vpn": {"confidence": ["high", "medium"]}}  # any of these
[{"is_tor": True}, {"is_resproxy": True}]  # a list is OR
```

Values are matched by equality, strings without regard to case. A list means any-of. A dict of `gte`/`gt`/`lte`/`lt` compares numbers, and every bound you give must hold, so two of them are a range. A member the answer holds as a list (`web`, `pubproxy.protocols`, `bittorrent.clients`, `bot.agents`, `bot.categories`) is never matched, so block on its flag alone. Members set to `False` or `None` are ignored, so a condition states the signals you act on; one that constrains nothing would match every request, and is refused when the middleware is built rather than silently blocking all your traffic.

Replace the refusal with `on_blocked`.

### Blocking one endpoint

`block_condition` applies to every endpoint. In FastAPI, refuse a visitor on some endpoints only with the `block_if` dependency, on a path operation, a router or the app:

```python
from fastapi import Depends
from vpndetection_fastapi import block_if


@app.get("/checkout", dependencies=[Depends(block_if({"is_vpn": True}))])
async def checkout(): ...
```

A refused request gets an `HTTPException`, `403` with `{"detail": "access denied"}` unless you pass `status_code` and `detail`. Declared as a parameter, the dependency hands the endpoint the answer. `block_if` takes the same condition, `fail_closed` and `on_missing_field`. It judges the answer the middleware already attached, so a visitor is looked up once however many endpoints check them, and it warns once for a member your plan doesn't include. A request `skip` claimed reaches the endpoint. The middleware still has to be added: without it, the dependency raises `RuntimeError` instead of letting everyone through.

## Where the client address comes from

Get this setting right, or none of the above works.

By default the middleware uses `request.client.host`. uvicorn, and `fastapi run` with it, reads proxy headers by default, but only from a peer that `--forwarded-allow-ips` trusts, and that defaults to `127.0.0.1,::1` (or `$FORWARDED_ALLOW_IPS`). So behind a proxy on the same machine, the visitor's address arrives with no setup. Behind one anywhere else, such as nginx in its own container or a load balancer in a VPC, every visitor looks like the proxy. That address is usually a private one, which the middleware answers locally: nobody is flagged, nothing is blocked, and the private-address warning below is the only sign. Name your proxy, by its address or its subnet: `--forwarded-allow-ips=172.28.5.0/28`. gunicorn's own `--forwarded-allow-ips` works the same way. Never pass `*`. It trusts every peer, so the left-most `X-Forwarded-For` entry wins, and that is whatever the visitor sent: someone on a VPN who sends `X-Forwarded-For: 1.1.1.1` is looked up as `1.1.1.1`.

For an edge that writes the address into its own header, name the header:

```python
from vpndetection_fastapi import header_ip_selector

ip_selector = header_ip_selector("CF-Connecting-IP")  # or True-Client-IP, or your own
```

`xff_ip_selector()` reads `X-Forwarded-For` directly. The left-most entry is whatever the caller sent, since proxies append to that header, so trust it only when an edge you control overwrites it. If you know how many proxies sit in front, count from the right instead: `xff_ip_selector(1)` is the address your nearest proxy saw.

Anything else, pass your own callable. It receives the request and returns an address.

If the address resolves to a private one, the middleware says so once through the `vpndetection` logger. That is expected on localhost and is the signal to fix your configuration anywhere else.

## When a lookup fails

The request is let through, and the reason is recorded on the answer's `error`. Our outage should not become yours, so a network failure, an exhausted quota or a rejected key all fail open. Pass `fail_closed=True` to block instead. Private addresses are answered locally and never fail, so this will not lock you out in development.

## Cost and latency

Answers are cached for an hour, so a returning visitor costs nothing, and private addresses never leave the process. A cache miss is one request to our API, bounded at 2.5 seconds by default and not retried: on a request path, failing open fast beats holding a visitor while we retry. Both are adjustable, as is the cache, through a `vpndetection` client you build yourself and pass as `client`.

Skip what you do not care about:

```python
skip = lambda request: request.url.path.startswith("/static")
```

Beyond a few million distinct visitors a day, stop calling the API per request: [download the dataset](https://vpndetection.io/#databases) and look addresses up locally instead.

## Absent is not false

Unlimited, with a key or without one, leaves out `is_hosting`, `is_cdn`, the four proxy flags, the carrier, satellite and service flags, `bot`, `company` and `abuse`, and of the detail behind each flag it answers only Tor's and relay's. A field your plan does not include is `None`, which means "not in your plan" rather than "checked, and no".

```python
lookup(request).result.is_hosting  # None when your plan does not include it
```

A `block_condition` naming a member your plan does not serve can never match, so the middleware warns once instead of failing silently. Pass `on_missing_field="raise"` to make it an error.

## Other Libraries

There are official VPNDetection client libraries available for many languages including PHP, Python, Go, Java, Ruby, and many popular frameworks such as Django, Rails, and Laravel. See our GitHub at https://github.com/vpndetection-io for more.

## About VPNDetection

VPN Detection API: Accurate anonymity detection identifying VPNs, residential proxies, hosting servers, Tor nodes, CDNs, relays and more.

[<img src="https://s3.vpndetection.io/vpndetection-public/brand/mark.svg" alt="VPNDetection" height="64"/>](https://vpndetection.io/)

## License

This project is licensed under the [MIT License](LICENSE).
