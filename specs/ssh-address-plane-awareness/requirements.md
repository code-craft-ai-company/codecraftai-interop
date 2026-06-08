# Requirements

## Introduction

The `ssh-address-plane-awareness` feature extends `codecraftai-interop`'s SSH
client base so callers can request the address plane (`PUBLIC`, `PRIVATE`,
`OVERLAY`) used to resolve the connect target. The selection threads through
to the device's `IDeviceAddressSet`; the existing behaviour (callers passing a
literal hostname / IP) is preserved as the default.

Address plane selection is the connective tissue between landscaping
(`device-address-set`, `vpn-coordinator-coupling`) and VPN clients
(`vpn-tailscale-client`, `vpn-twingate-client`). Without this feature, the
landscape's plane choice cannot reach the SSH layer.

All public methods take named parameters. The new parameter is opt-in with a
default that does not change existing call sites.

---

## Requirements

### Requirement 1: `connect` Accepts an Address Plane

**User Story:** As a coordinator, I want to ask the SSH client to dial a host
on a specific address plane so my landscape's preferred plane is honoured.

#### Acceptance Criteria

1. THE SYSTEM SHALL extend `SSHBase.connect(...)` with a keyword-only
   parameter `address_plane: AddressPlane = AddressPlane.PUBLIC`.
2. WHEN `connect(host=...)` is called with a literal host string and no
   `device` argument THE SYSTEM SHALL behave identically to the pre-feature
   client (no plane resolution occurs).
3. WHEN `connect(device=..., address_plane=plane)` is called with an
   `IDeviceAddressSet`-bearing device THE SYSTEM SHALL look up
   `device.addresses().resolve(plane)` and SHALL use the returned address as
   the dial target.
4. IF the plane resolves to `None` AND no fall-through plane is configured
   THEN THE SYSTEM SHALL raise `SSHAddressPlaneUnavailableError` with the
   device name and requested plane in the message.

### Requirement 2: Fall-Through Plane Ordering

**User Story:** As an operator with mixed-mesh landscapes, I want a
configurable fall-through ordering so a device that lacks the preferred plane
still connects via a sensible alternate.

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `fallback_planes: Optional[List[AddressPlane]] = None`
   on `connect(...)`.
2. WHEN `fallback_planes` is `None` THE SYSTEM SHALL NOT fall through; an
   unavailable preferred plane raises per Req 1.4.
3. WHEN `fallback_planes` is non-empty AND the preferred plane is unavailable
   THE SYSTEM SHALL try each fallback in declared order, returning the first
   non-`None` address.
4. WHEN every plane in the fallback list is also unavailable THE SYSTEM SHALL
   raise `SSHAddressPlaneUnavailableError` with the full attempted sequence
   listed in the message.

### Requirement 3: Plane Selection Is Total and Deterministic

**User Story:** As a test author, I want plane selection to be a pure,
deterministic function of `(device_address_set, preferred_plane,
fallback_planes)` so I can write property tests against it without mocking
the network.

#### Acceptance Criteria

1. THE SYSTEM SHALL implement the resolution as a free function
   `resolve_dial_target(address_set, preferred_plane, fallback_planes)`
   that performs no I/O.
2. THE SYSTEM SHALL return either a non-empty string or raise
   `SSHAddressPlaneUnavailableError`; no other return shape is permitted.
3. THE SYSTEM SHALL produce the same output for the same input across
   processes (no time, no randomness, no environment lookups inside the
   resolver).

### Requirement 4: Aspects on the Connect Call

#### Acceptance Criteria

1. THE SYSTEM SHALL continue to accept `aspects: AspectsSSH` on `connect`,
   defaulting to `DEFAULT_SSH_ASPECTS`.
2. THE SYSTEM SHALL NOT use behaviour-modifying decorators.

### Requirement 5: Logging of Plane Choice

**User Story:** As an operator triaging a connect failure, I want the SSH
client to log which plane was used so I can correlate the failure with the
overlay state.

#### Acceptance Criteria

1. WHEN a `connect(device=...)` call resolves to a dial target THE SYSTEM
   SHALL log at INFO the device name, preferred plane, plane actually used,
   and dial target address.
2. WHEN fall-through is exercised THE SYSTEM SHALL log at WARNING the planes
   that were skipped.
