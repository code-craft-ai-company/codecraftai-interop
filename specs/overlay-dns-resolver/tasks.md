# Implementation Plan — Overlay DNS Resolver

- [x] 1. Create `automojo/interop/protocols/dns/aspectsoverlaydns.py` with
  `AspectsOverlayDNS` and `DEFAULT_OVERLAY_DNS_ASPECTS`.
- [x] 2. Create `overlaycandidate.py` with the `OverlayCandidate` dataclass.
- [x] 3. Create `exceptions.py` with `OverlayDNSNoMatchError` and
  `OverlayDNSError`.
- [x] 4. Create `matchpredicate.py`:
  - [x] 4a. `is_match(*, query, candidate, aspects) -> bool` pure function.
  - [x] 4b. No I/O, no time, no randomness.
- [x] 5. Create `overlaydnsresolver.py`:
  - [x] 5a. `__init__(*, vpn_clients=None, control_planes=None,
    stdlib_resolver=None)`.
  - [x] 5b. `register_vpn_client(*, client)` / `register_control_plane(*, cp)`.
  - [x] 5c. `resolve(*, name, plane, aspects=DEFAULT_OVERLAY_DNS_ASPECTS) -> str`.
  - [x] 5d. Cache structure keyed on `(name, plane)` with `expires_at`.
  - [x] 5e. Raise `SemanticError` for OVERLAY plane with zero providers.
- [x] 6. Apply project coding standards.
- [x] 7. Tests — example-based:
  - [x] 7a. `test_resolve_via_first_vpn_client_match`.
  - [x] 7b. `test_resolve_via_control_plane_when_no_client_match`.
  - [x] 7c. `test_resolve_stdlib_fall_through`.
  - [x] 7d. `test_resolve_no_match_raises_when_fall_through_disabled`.
  - [x] 7e. `test_resolve_overlay_no_providers_raises_semantic`.
  - [x] 7f. `test_resolve_public_plane_skips_overlay_path`.
  - [x] 7g. `test_cache_hit_skips_providers`.
  - [x] 7h. `test_cache_expired_re_queries_providers`.
- [x] 8. Property tests (`hypothesis`):
  - [x] 8a. `test_is_match_is_total`.
  - [x] 8b. `test_is_match_is_deterministic`.
  - [x] 8c. `test_is_match_reflexive_on_short_hostname`.
  - [x] 8d. `test_is_match_asymmetric_in_general`.
  - [x] 8e. `test_resolver_outcome_is_one_of_three`.
  - [x] 8f. `test_resolver_match_priority`.
- [x] 9. Add `hypothesis` to the package test dependencies if not already
  present.
- [x] 10. Export `OverlayDNSResolver` from
  `automojo/interop/protocols/dns/__init__.py`.
