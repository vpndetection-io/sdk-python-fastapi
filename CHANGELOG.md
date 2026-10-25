# Changelog

What each release changed for you, newest first. Each line is a commit's summary, linked to its full description and diff. Releases before 2.0.5 are described by their release commits.

## 2.1.12 - 2026-10-25

### Fixes

- Require vpndetection 5.12.1: retry counts and dates are checked ([`34f2386`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/34f23860aa37be0df41e6728a04b461f36c27f62))

## 2.1.11 - 2026-10-23

### Fixes

- Require vpndetection 5.12.0, which adds oauth.register ([`a63aa00`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/a63aa0036f8874e770d4be65c63500f7f1436919))

## 2.1.10 - 2026-10-22

### Fixes

- Require vpndetection 5.11.1: a wrong-typed member is a server_error ([`e36e37e`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/e36e37e1a469440872d2d01768dc0359242740c1))

## 2.1.9 - 2026-10-20

### Features

- Require vpndetection 5.11.0: lookup results carry location and asn ([`ada4345`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/ada4345bde920539b2f279f03d790ae42a74998d))

## 2.1.8 - 2026-10-19

### Fixes

- Require vpndetection 5.10.0: num_ports and num_proxies in the pubproxy detail ([`c5fa5cb`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/c5fa5cb80237225ebb3d7aee077094549fbf9451))

## 2.1.7 - 2026-10-18

### Fixes

- Require vpndetection 5.9.0: is_pubproxy and the pubproxy detail ([`f307abd`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/f307abded300ba66edf95e82bc692451a661d3c0))

## 2.1.6 - 2026-10-17

### Features

- Require vpndetection 5.8.0: OauthMetadata carries registration_endpoint ([`e912868`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/e91286800be6db8f33012ff373a54fcb607ba889))

## 2.1.5 - 2026-10-16

### Fixes

- Require vpndetection 5.7.3: the spec re-pinned to 2026.10.15 ([`70f11ea`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/70f11eaaa1bd8e776917f0e535b9d4efb0fe2fb4))

## 2.1.4 - 2026-10-15

### Fixes

- Require vpndetection 5.7.2: Retry-After, the key, the base URL and unreadable answers ([`4d74c45`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/4d74c456bb11419cb181d5f7c911913a84398ca3))

## 2.1.3 - 2026-10-10

### Fixes

- Require vpndetection 5.7.1: the spec re-pinned to 2026.10.09 ([`62563b2`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/62563b2ec2b31e6b317d836c229f939bb9f0ec30))

## 2.1.2 - 2026-10-06

### Features

- Require vpndetection 5.7.0: the authorization code sign-in ([`982b9a6`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/982b9a6908973744a6eef5fdbf6171d5541422b8))

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
