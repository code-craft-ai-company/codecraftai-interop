# Requirements

## Introduction

The `overlay-dns-resolver` feature provides a DNS resolver under
`automojo-interop/protocols/dns/` that maps short names (MagicDNS,
Twingate FQDNs) to overlay addresses by querying the local VPN daemon or the
VPN control plane. When no overlay match is found, it falls through to the
standard system resolver.

The resolver is deterministic — the same `(name, providers, fall-through
DNS)` always produces the same answer for the same upstream state. The
matching predicate is total: for every input there is exactly one of
`Resolved`, `NoMatch`, or `Error`.

This determinism is contract-relevant — provisioning verification, landscape
boot-up, and SSH dial-target selection all depend on it. The feature therefore
requires `hypothesis` property tests in addition to example-based tests.

All methods take named parameters. Aspects ride on every call. No
behaviour-modifying decorators.

---

## Requirements

### Requirement 1: Resolve a Name on a Specific Overlay

**User Story:** As a coordinator, I want to resolve `myhost` to its Tailscale
overlay IP so I can dial it without leaking the request to public DNS.

#### Acceptance Criteria

1. WHEN `resolve(name, plane=OVERLAY, aspects)` is called THE SYSTEM SHALL
   query each registered `IVPNClient` in registration order, returning the
   first non-`None` address whose peer hostname matches `name`.
2. WHEN no IVPNClient returns a match THE SYSTEM SHALL query each registered
   `IVPNControlPlane` in registration order and SHALL match `name` against the
   device record's `hostname` and `name` (MagicDNS) fields.
3. WHEN no match is found AND `aspects.fall_through_standard_dns` is `True`
   THE SYSTEM SHALL invoke the standard DNS resolver and return its answer.
4. WHEN no match is found AND fall-through is disabled THE SYSTEM SHALL raise
   `OverlayDNSNoMatchError` with the attempted-provider list in the message.

### Requirement 2: Matching Predicate Is Total and Deterministic

**User Story:** As a test author, I want the match predicate to be a pure
function over `(query, candidate)` so property tests cover it without mocking
the network.

#### Acceptance Criteria

1. THE SYSTEM SHALL implement `is_match(query, candidate)` as a free function
   in `matchpredicate.py` performing no I/O.
2. THE SYSTEM SHALL normalise both inputs to lowercase ASCII before comparing.
3. THE SYSTEM SHALL treat `query` matching when it equals the candidate's
   short hostname OR when the candidate's MagicDNS name starts with the query
   followed by a `.`.
4. THE SYSTEM SHALL return `True` or `False`; no exception is ever raised
   from the predicate. The predicate is total.

### Requirement 3: Plane Selection Honoured

#### Acceptance Criteria

1. WHEN `plane=PUBLIC` or `plane=PRIVATE` THE SYSTEM SHALL skip the overlay
   path entirely and SHALL invoke the standard resolver directly.
2. WHEN `plane=OVERLAY` AND no overlay providers are registered THE SYSTEM
   SHALL raise `SemanticError` — calling for OVERLAY resolution on an
   unconfigured resolver is a caller bug.

### Requirement 4: Aspects on Every Call

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: AspectsOverlayDNS` defaulting to
   `DEFAULT_OVERLAY_DNS_ASPECTS`.
2. `AspectsOverlayDNS` SHALL include `fall_through_standard_dns: bool`,
   `query_timeout_seconds: float`, `case_sensitive: bool`.
3. THE SYSTEM SHALL NOT use behaviour-modifying decorators.

### Requirement 5: Caching Is Optional and Bounded

**User Story:** As a coordinator running many lookups in a tight loop, I want
to cache hot answers but not stale ones.

#### Acceptance Criteria

1. WHERE `aspects.cache_ttl_seconds > 0` THE SYSTEM SHALL cache resolved
   `(name, plane) → address` entries with a TTL bound by the aspect.
2. WHERE `aspects.cache_ttl_seconds == 0` THE SYSTEM SHALL NOT cache.
3. WHEN a cache entry expires THE SYSTEM SHALL re-query the providers.

### Requirement 6: Property Tests Required

#### Acceptance Criteria

1. THE SYSTEM SHALL include `hypothesis` property tests asserting:
   - `is_match` is total over all `(str, candidate)` pairs.
   - `is_match` is deterministic — same input, same output, across runs.
   - `is_match` is reflexive on the candidate's own short hostname.
   - `is_match` is asymmetric — `is_match(q, c)` does not imply
     `is_match(c.short_hostname, build_candidate(q))` unless q==c.short.
2. THE SYSTEM SHALL include `hypothesis` property tests asserting:
   - For any randomly generated provider list + name, `resolve(...)`
     either returns a non-empty string OR raises exactly one of the typed
     resolver exceptions; no other outcome is possible.
