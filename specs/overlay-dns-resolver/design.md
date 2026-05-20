# Design

## Overview

`OverlayDNSResolver` maps short / MagicDNS / Twingate-resource names to
overlay addresses by walking a registered list of `IVPNClient`s and
`IVPNControlPlane`s and falling through to the standard system resolver when
no overlay match is found. The matching predicate is a pure, total,
deterministic function; the resolver is the I/O-bound shell wrapping it.

**See Also:**
- [vpn-tailscale-client](../vpn-tailscale-client/design.md) — provides
  `peer_addresses()` consumed by the resolver.
- [vpn-tailscale-control-plane](../vpn-tailscale-control-plane/design.md) —
  provides `list_devices()` consumed by the resolver.
- [ssh-address-plane-awareness](../ssh-address-plane-awareness/design.md) —
  the SSH-side analog of plane-aware addressing.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│   Caller (resolution.py in automojo-networking)              │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  OverlayDNSResolver                          │
│  interop/protocols/dns/overlaydnsresolver.py                 │
│                                                              │
│  resolve(name, plane, aspects) → str                         │
│   │                                                          │
│   ├── PUBLIC / PRIVATE → standard resolver                   │
│   │                                                          │
│   └── OVERLAY                                                │
│       │                                                      │
│       ▼                                                      │
│   ┌──────────────────────────────────────┐                  │
│   │ for client in vpn_clients:           │                  │
│   │   peers = client.peer_addresses()    │                  │
│   │   for (host, addr) in peers.items(): │                  │
│   │     if is_match(name, host): return  │                  │
│   │                                      │                  │
│   │ for cp in control_planes:            │                  │
│   │   for dev in cp.list_devices():      │                  │
│   │     if is_match(name, dev): return   │                  │
│   │                                      │                  │
│   │ if fall_through: stdlib_resolve(name)│                  │
│   │ else: raise NoMatch                  │                  │
│   └──────────────────────────────────────┘                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Model

```python
@dataclass
class OverlayCandidate:
    short_hostname: str
    magicdns_name: Optional[str]      # e.g., "host.tailnet.ts.net"
    addresses: List[str]
    provider: str                     # "tailscale" / "twingate"

class OverlayDNSNoMatchError(Exception):
    """Raised when no overlay or fall-through resolution succeeds."""

class OverlayDNSError(Exception):
    """Raised when an underlying provider call fails irrecoverably."""

@dataclass
class AspectsOverlayDNS:
    fall_through_standard_dns: bool = True
    query_timeout_seconds: float = 5.0
    case_sensitive: bool = False
    cache_ttl_seconds: float = 0.0

DEFAULT_OVERLAY_DNS_ASPECTS = AspectsOverlayDNS()
```

---

## Module Layout

```
source/packages/automojo/interop/protocols/dns/
├── overlaydnsresolver.py
├── matchpredicate.py         ← pure is_match()
├── aspectsoverlaydns.py
├── overlaycandidate.py
└── exceptions.py
```

Tests:

```
source/testroots/.../dns/
├── test_overlaydnsresolver.py
├── test_matchpredicate.py
└── property/
    ├── test_matchpredicate_properties.py    ← hypothesis
    └── test_resolver_properties.py          ← hypothesis
```

---

## Matching Predicate

`is_match(query, candidate)` rules:

1. Normalise: lowercase both inputs unless `aspects.case_sensitive`.
2. Return `True` if `query == candidate.short_hostname`.
3. Return `True` if `candidate.magicdns_name` is non-empty and starts with
   `query + "."`.
4. Otherwise return `False`.

The function never raises. It performs no I/O. It does not consult time,
environment, or random state. Property tests assert these invariants.

---

## Resolver Algorithm

```
def resolve(name, plane, aspects):
    if plane in {PUBLIC, PRIVATE}:
        return _stdlib_resolve(name, aspects)

    if plane == OVERLAY:
        if len(self._vpn_clients) == 0 and len(self._control_planes) == 0:
            raise SemanticError("no overlay providers registered")

        cached = self._cache_lookup(name, plane, aspects)
        if cached is not None:
            return cached

        for client in self._vpn_clients:
            peers = client.peer_addresses()
            for (host, addr) in peers.items():
                cand = OverlayCandidate(host, None, [addr], client.provider_name)
                if is_match(name, cand, aspects):
                    self._cache_store(name, plane, addr, aspects)
                    return addr

        for cp in self._control_planes:
            for dev in cp.list_devices(aspects=aspects):
                cand = _candidate_from_device_record(dev)
                if is_match(name, cand, aspects):
                    addr = cand.addresses[0]
                    self._cache_store(name, plane, addr, aspects)
                    return addr

        if aspects.fall_through_standard_dns:
            return _stdlib_resolve(name, aspects)

        raise OverlayDNSNoMatchError(...)
```

Totality property: the inner loops either return a string or fall through;
the fall-through branches either return a string or raise exactly one typed
exception. No path silently returns `None`.

---

## Testing Strategy

- Example tests using fake `IVPNClient` and `IVPNControlPlane` doubles:
  - Single tailscale client, single peer match → returns the overlay IP.
  - Multi-client priority: first registered wins.
  - Control-plane fallback when no client matches.
  - Stdlib fall-through path with mocked stdlib resolver.
  - `NoMatch` raised when fall-through is disabled and nothing matches.
  - `SemanticError` raised when OVERLAY is requested with zero providers.
  - Cache TTL test: second call within TTL skips providers; second call after
    TTL re-queries.

- **Property tests (`hypothesis`):**
  - `test_is_match_is_total`: for all `(str, OverlayCandidate)` pairs,
    `is_match` returns a bool and never raises.
  - `test_is_match_is_deterministic`: invoking `is_match` twice on the same
    input returns the same value.
  - `test_is_match_reflexive_on_short_hostname`: for any
    `OverlayCandidate c`, `is_match(c.short_hostname, c) is True`.
  - `test_resolver_outcome_is_one_of_three`: for any randomly generated
    `(name, vpn_clients, control_planes, fall_through_disabled)` fixture,
    `resolve(...)` either returns a non-empty string or raises one of
    `OverlayDNSNoMatchError` / `OverlayDNSError` / `SemanticError`.
  - `test_resolver_match_priority`: a generated candidate set with multiple
    matches always returns the address from the earliest-registered provider.
- No test requires a live daemon or network DNS.
