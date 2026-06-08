# Design

## Overview

`TwingateClient` is a `VPNClientBase` subclass that drives the Twingate
connector service through an `ICommandRunner`. It implements `IVPNClient` while
honestly modelling the protocol's asymmetry vs Tailscale — connectors do not
have overlay IPs and do not enumerate peers from the local daemon.

Twingate network administration (resources, groups, service accounts, ACL) is
out of scope for this client; it belongs to
[vpn-twingate-control-plane](../vpn-twingate-control-plane/design.md). Install
and service-unit ownership lives in the per-OS sysman packages.

**See Also:**
- [vpn-twingate-control-plane](../vpn-twingate-control-plane/design.md)
- [vpn-tailscale-client](../vpn-tailscale-client/design.md) — sibling, mesh-style
  alternative.
- [ssh-address-plane-awareness](../ssh-address-plane-awareness/design.md) — how
  callers degrade gracefully when `self_address()` is `None`.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         Caller                               │
└──────────────────────────────┬───────────────────────────────┘
                               │ IVPNClient
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    TwingateClient                            │
│  interop/vpn/twingate/twingateclient.py                      │
│   bring_up(authkey, hostname, advertise_tags, aspects)       │
│   bring_down(aspects)                                        │
│   status(aspects)            → VPNStatus                     │
│   self_address()             → None                          │
│   peer_addresses()           → {}                            │
└──────────────────────────────┬───────────────────────────────┘
                               │ ICommandRunner.run(...)
                               ▼
                ┌──────────────┴───────────────┐
                ▼                              ▼
        ┌──────────────────┐           ┌──────────────────┐
        │ LocalRunner      │           │ SSHRunner        │
        └──────────────────┘           └──────────────────┘
```

---

## Data Model

Uses the shared `VPNStatus` dataclass and the
`VPNBringUpError` / `VPNBringDownError` exceptions defined alongside
`TailscaleClient`. No Twingate-specific types are introduced — that surface
lives in the control-plane spec.

`AspectsVPNClient` is reused; `DEFAULT_VPN_CLIENT_ASPECTS` applies.

---

## Module Layout

```
source/packages/ccai/interop/vpn/twingate/
├── __init__.py
├── twingateclient.py
├── connectorinvocation.py   ← argv composition per OS family
└── exceptions.py            ← re-exports shared VPN errors
```

Tests:

```
source/testroots/.../interop/vpn/twingate/
├── test_twingateclient.py
├── test_connectorinvocation.py
└── fixtures/
    ├── systemctl_is_active.txt
    └── connector_setup_failure.txt
```

---

## Command Mappings

| Operation | Command sequence |
|---|---|
| `bring_up` | `twingate-connector setup --access-token=<a> --refresh-token=<r> [--name=<h>]` then `systemctl start twingate-connector` |
| `bring_down` | `systemctl stop twingate-connector` |
| `status` | `systemctl is-active twingate-connector` |

The connector token bundle (`authkey`) is parsed as a single
`"<access>:<refresh>"` string by `connectorinvocation.compose_setup_argv`.

---

## Provider Asymmetry — Documented

Twingate's hub-and-spoke topology means:

- The connector host does not get an overlay IP. `self_address()` returns
  `None` permanently.
- Clients reach *resources* by FQDN through the connector. Peer enumeration
  belongs on the control plane (resource discovery), not the local daemon.
  `peer_addresses()` returns `{}`.

This is a deliberate design choice from §3 of the master plan, not a TODO.
Consumers (landscaping `DeviceAddressSet.overlay()`, provisioning validation)
branch on the returned `None` and fall back to private-plane addressing.

---

## Testing Strategy

- Mock runner returns canned `RunResult` objects keyed by command prefix.
- Setup argv test verifies token splitting and `--name` inclusion.
- Status parser tests cover `active`, `inactive`, `failed`, `unknown`.
- `self_address()` test asserts the returned value is always `None`.
- `peer_addresses()` test asserts the returned mapping is always empty and
  asserts the DEBUG log fires exactly once across multiple calls.
- Dry-run test asserts the runner is never invoked.
- Aspects test verifies elevation for writes and no elevation for reads.
- No test requires a live connector daemon.
