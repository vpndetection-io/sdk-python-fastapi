# Changelog

What each release changed for you, newest first. Each line is a commit's summary, linked to its full description and diff. Releases before 2.0.5 are described by their release commits.

## 2.2.5 - 2026-11-26

### Fixes

- Require vpndetection 5.23.1: a condition on the verdict is no plan gap for a request that sent no agent ([`59d3529`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/59d352919428e28d9a5929edaa2366f214a1a447))

## 2.2.4 - 2026-11-26

### Features

- Require vpndetection 5.23.0: allowBots sends only a crawler's User-Agent, at most four an address ([`be55736`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/be5573675f8c80ddff18ac8518abb4f6c51528e5))

## 2.2.3 - 2026-11-25

### Fixes

- Require vpndetection 5.22.1: doc comments name a paid plan, the entitlement example the Data plan ([`44915d4`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/44915d411f41db3af686d89cf59e2d31defbd6f1))

## 2.2.2 - 2026-11-24

### Fixes

- Require vpndetection 5.22.0: a condition on a list member, such as pubproxy.protocols or a web row's port, matches any element ([`bfe0e1a`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/bfe0e1ac6111078fdcabd598da0024ab6ec0c06e))

## 2.2.1 - 2026-11-24

### Fixes

- Require vpndetection 5.21.1: a detail's first_seen or last_seen that is not a day is refused ([`e6d0d01`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/e6d0d0119c78c510d7b912223c1b0ed13438e6d5))

## 2.2.0 - 2026-11-23

### Features

- Require vpndetection 5.21.0: a user agent with a lookup, and allow_bots in the middleware core ([`a7e8d80`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/a7e8d80b886c987c7358a028499ff2697fe8c58c))
- Let a verified crawler through with allow_bots ([`c7dd247`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/c7dd247cb47bd55acd35cadca44b5d6e4c131265))

## 2.1.29 - 2026-11-22

### Features

- Require vpndetection 5.20.0: is_bot and bot, and the AS's country and RPKI status required ([`6448579`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/64485792c122bfe1c5a8684a9ec5ed9fd3896056))

## 2.1.28 - 2026-11-20

### Features

- Require vpndetection 5.19.0: the network, service, company and abuse members ([`66c0b08`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/66c0b080a273e783c306e546c3bca48f31532123))

## 2.1.27 - 2026-11-19

### Fixes

- Require vpndetection 5.18.1: re-pinned to spec 2026.11.18 ([`08cf64c`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/08cf64c199c9c5a6cb2438e77b562580f371e084))

## 2.1.26 - 2026-11-18

### Fixes

- Require vpndetection 5.18.0: cap_reached past a paid plan's overage cap ([`66d91f9`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/66d91f9003bd1904aa445be8791b60fb38c7b528))

## 2.1.25 - 2026-11-17

### Fixes

- Require vpndetection 5.17.0: a vocabulary value it was not built with comes back as served, and the plan's name ([`2ff2529`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/2ff25290b808f244558e63abb21367f0320d6a56))

## 2.1.24 - 2026-11-14

### Fixes

- Require vpndetection 5.16.0: is_bogon on every answer, and provider_name beside each provider ([`ab65ea3`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/ab65ea35cc70d2e6659b8bf9dae125d90a3c8442))

## 2.1.23 - 2026-11-11

### Fixes

- Require vpndetection 5.15.2: Unlimited, the free plan, never the Unlimited tier ([`d1e07ae`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/d1e07ae3d77f129bfa36cfee5eaa8edff1ffc83a))

## 2.1.22 - 2026-11-11

### Fixes

- Require vpndetection 5.15.1: the free plan's daily trial, never a trial key ([`46742f4`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/46742f4a2b4c9a43af7fd7ca49938c9b60f28694))

## 2.1.21 - 2026-11-11

### Features

- Require vpndetection 5.15.0: trial_expired on a trial key's answers ([`24fa4aa`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/24fa4aaa83e87cbf43203aaf71d9686e7ba2c9f2))

## 2.1.20 - 2026-11-11

### Fixes

- Require vpndetection 5.14.2: the Unlimited tier and its terms ([`2796643`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/2796643453d9724b284c1c9faf9599c923cd3795))

## 2.1.19 - 2026-11-11

### Fixes

- Require vpndetection 5.14.1: plainer words on lookups without a key ([`f7ca8d9`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/f7ca8d936a040cff06b2f11f0d424f64b6cef606))

## 2.1.18 - 2026-11-11

### Features

- Require vpndetection 5.14.0: a lookup without a key answers more ([`3161128`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/3161128e6758efdb9ba3ccc546b8f328db8c73a3))

## 2.1.17 - 2026-11-11

### Fixes

- Require vpndetection 5.13.1: a client concurrency is checked where it is set ([`9fe9b92`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/9fe9b924446f4c8fdd4358a0f78b754d00b56ef0))

## 2.1.16 - 2026-11-07

### Features

- Require vpndetection 5.13.0: downloads take the build a webhook names ([`0a2600a`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/0a2600a7da8d15b512d890ce5c070fcbffc1f01f))

## 2.1.15 - 2026-11-06

### Fixes

- Require vpndetection 5.12.4: a device poll ends at its deadline ([`c542cec`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/c542cecbdf525b47356f37402c2eba4d9f2d44a3))

## 2.1.14 - 2026-10-28

### Fixes

- Require vpndetection 5.12.3: a date-time whose T or Z is lowercase is read ([`c262d4b`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/c262d4b600d3878b89feacb2893c9d9180f7cdee))

## 2.1.13 - 2026-10-26

### Fixes

- Require vpndetection 5.12.2: re-pinned to the 2026.10.25 spec ([`bf0476c`](https://github.com/vpndetection-io/sdk-python-fastapi/commit/bf0476cc252ff14f2857aeab9b3611fefee9818f))

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
