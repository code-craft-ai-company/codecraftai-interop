# Design

## Overview

`TailscaleClient` is a `VPNClientBase` subclass that drives the `tailscale` CLI
through an injected `ICommandRunner`. It satisfies `IVPNClient` and is the
canonical local-daemon interface for Tailscale-joined hosts. The class never
talks to `api.tailscale.com` directly; that surface belongs to
`TailscaleControlPlane` (see [vpn-tailscale-control-plane](../vpn-tailscale-control-plane/design.md)).

The same instance works against a local runner and a remote SSH runner with no
code changes, which lets sysman, landscaping, and provisioning all use one type
to drive Tailscale on any reachable host.

**See Also:**
- [vpn-tailscale-control-plane](../vpn-tailscale-control-plane/design.md) — REST
  client for tailnet administration.
- [ssh-address-plane-awareness](../ssh-address-plane-awareness/design.md) — uses
  `self_address()` to source the OVERLAY plane address.
- [overlay-dns-resolver](../overlay-dns-resolver/design.md) — consumes
  `peer_addresses()` for MagicDNS-style resolution.

---

## Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                       Caller                                  │
│  (sysman.vpnclientmanagement / landscaping.vpncoupling /      │
│   provisioning.bootstrap_vpn)                                 │
└──────────────────────────────┬────────────────────────────────┘
                               │  IVPNClient
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                  TailscaleClient                              │
│  interop/vpn/tailscale/tailscaleclient.py                     │
│   bring_up(authkey, hostname, advertise_tags, aspects)        │
│   bring_down(aspects)                                         │
│   status(aspects)            → VPNStatus                      │
│   self_address()             → Optional[str]                  │
│   peer_addresses()           → Dict[str, str]                 │
└──────────────────────────────┬────────────────────────────────┘
                               │ ICommandRunner.run(args, elevated, ...)
                               ▼
        ┌──────────────────────┴───────────────────────┐
        ▼                                              ▼
┌──────────────────────┐                  ┌──────────────────────┐
│ LocalCommandRunner   │                  │ SSHCommandRunner     │
└──────────────────────┘                  └──────────────────────┘
```

---

## Data Model

```python
@dataclass
class VPNStatus:
    running: bool
    backend_state: Optional[str]   # "Running", "NeedsLogin", "Stopped", ...
    self_address: Optional[str]    # 100.x.x.x or None
    hostname: Optional[str]
    tags: List[str]
    detail: Optional[str]

class VPNBringUpError(Exception):
    """Raised when `tailscale up` returns non-zero."""

class VPNBringDownError(Exception):
    """Raised when `tailscale down` returns non-zero."""

class VPNStatusError(Exception):
    """Raised when `tailscale status --json` output cannot be parsed."""
```

`Aspects` for VPN clients (`AspectsVPNClient`) extends the base `Aspects`
with `dry_run`, `elevated`, `command_timeout_seconds`, `status_refresh_seconds`.
`DEFAULT_VPN_CLIENT_ASPECTS` materialises with `dry_run=False`,
`elevated=False`, `command_timeout_seconds=30`, `status_refresh_seconds=10`.

---

## Module Layout

```
source/packages/automojo/interop/vpn/
├── __init__.py
├── vpnclientbase.py            ← VPNClientBase(IVPNClient) abstract
├── aspectsvpnclient.py
└── tailscale/
    ├── __init__.py
    ├── tailscaleclient.py      ← TailscaleClient
    ├── statusparser.py         ← parse `tailscale status --json`
    └── exceptions.py
```

Tests:

```
source/testroots/.../interop/vpn/tailscale/
├── test_tailscaleclient.py
├── test_statusparser.py
└── fixtures/
    ├── status_running.json
    ├── status_logged_out.txt
    └── status_with_peers.json
```

---

## Command Mappings

| Operation | Command |
|---|---|
| `bring_up` | `tailscale up --authkey=<k> [--hostname=<h>] [--advertise-tags=<csv>]` |
| `bring_down` | `tailscale down` |
| `status` | `tailscale status --json` |

Write operations honour `aspects.elevated`. Reads never elevate.

---

## Testing Strategy

- Mock runner returns canned `RunResult` objects keyed on the first three argv
  tokens.
- Status parser tests use real captured `tailscale status --json` fixtures
  covering: a single-node tailnet, a multi-peer tailnet, a logged-out node, and
  a corrupt-JSON degraded case.
- `bring_up` tests cover the four flag-combination shapes (`hostname` ±,
  `advertise_tags` ±) and verify exact argv composition.
- `bring_up` dry-run test asserts the runner is never invoked.
- Error path tests verify each typed exception carries `exit_code` and
  `stderr`.
- Aspects test verifies elevation passes through for writes and is suppressed
  for reads regardless of `aspects.elevated`.
- No test requires a live `tailscaled` daemon.
