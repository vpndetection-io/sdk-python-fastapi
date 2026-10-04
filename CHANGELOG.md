# Changelog

What each release changed for you, newest first. Each line is a commit's summary, linked to its full description and diff. Releases before 2.0.5 are described by their release commits.

## 2.1.1 - 2026-10-04

### Fixes

- Require vpndetection 5.6.1, re-pinned to spec 2026.10.03 ([`8184aea`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/8184aeab72f9a64b9abc2eb8ae6e550e05941e1f))

## 2.1.0 - 2026-10-03

### Features

- Add block_if, a FastAPI dependency refusing one endpoint to a matching visitor ([`c91eb21`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/c91eb2118550e18ba6a5072193717c0e97f4f81c))

## 2.0.9 - 2026-10-02

### Fixes

- Require vpndetection 5.5.3: a long Retry-After or timeout no longer raises OverflowError ([`7805671`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/78056714706cbadef865a8b1888209fae061a796))

## 2.0.8 - 2026-09-29

### Fixes

- Require vpndetection 5.5.2: 26 more reserved ranges are answered locally ([`73b34b6`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/73b34b6ca355cc56fcfcbf159a241ec114541c78))

## 2.0.7 - 2026-09-28

### Fixes

- Require vpndetection 5.5.1: IPv4-mapped visitors are looked up, not waved through ([`976dc44`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/976dc44ca5a65d2a13d6ce1d366a4582de24db89))

## 2.0.6 - 2026-09-27

### Features

- Require vpndetection 5.5.0: OauthMetadata carries client_id_metadata_document_supported ([`21a3979`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/21a3979ec7ed49fb55e88e0a16a32ccefc0bf61f))

## 2.0.5 - 2026-09-25

### Fixes

- Raise the base floor to vpndetection 5.4.2 ([`fb4525a`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/fb4525a2d8ab530939a3a157675c937fd22cf71a))
