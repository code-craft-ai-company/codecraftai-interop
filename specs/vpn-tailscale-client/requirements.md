# Requirements

## Introduction

The `vpn-tailscale-client` feature provides `automojo-interop` with a host-local
client that drives the `tailscale` CLI through an `ICommandRunner`. It implements
the `IVPNClient` protocol from `automojo-interfaces` so consumers (sysman
managers, landscaping coordinators, provisioning verifiers) can bring a node up
on a tailnet, query its overlay address, and enumerate peer overlay addresses
without depending on the local installation pattern.

The client is transport-neutral: the same class works against `LocalCommandRunner`
for the executing host and against `SSHCommandRunner` for a remote host. All
behaviour-modifying parameters (timeouts, retry, elevation, persistence) ride on
an `Aspects` argument; there are no `@retry` decorators on any method.

All methods accept named parameters only. State queries parse `tailscale status
--json` output. The client does NOT install `tailscaled`; install/service control
is owned by the per-OS sysman packages.

---

## Requirements

### Requirement 1: Bring the Tailscale Daemon Up

**User Story:** As a coordinator, I want to bring a host up on a tailnet using a
supplied auth key so the host becomes addressable on the overlay plane.

#### Acceptance Criteria

1. WHEN `bring_up(authkey, hostname, advertise_tags, aspects)` is called with a
   non-empty `authkey` THE SYSTEM SHALL invoke `tailscale up --authkey=<key>
   --hostname=<hostname> --advertise-tags=<csv>` via the command runner.
2. IF `hostname` is `None` THEN THE SYSTEM SHALL omit the `--hostname` flag.
3. IF `advertise_tags` is `None` or empty THEN THE SYSTEM SHALL omit the
   `--advertise-tags` flag.
4. WHEN the command exits zero THE SYSTEM SHALL parse `tailscale status --json`
   and return the resulting `VPNStatus` populated from the local node entry.
5. IF the command exits non-zero THEN THE SYSTEM SHALL raise
   `VPNBringUpError` carrying the exit code and captured stderr.
6. WHEN `aspects.dry_run` is `True` THE SYSTEM SHALL NOT execute any command
   and SHALL return a `VPNStatus` with `running=False` and `detail="dry-run"`.

### Requirement 2: Bring the Tailscale Daemon Down

**User Story:** As a coordinator, I want to gracefully disconnect a host from
the tailnet so its overlay address is released.

#### Acceptance Criteria

1. WHEN `bring_down(aspects)` is called THE SYSTEM SHALL invoke
   `tailscale down` via the command runner.
2. IF the command exits non-zero THEN THE SYSTEM SHALL raise `VPNBringDownError`
   with the exit code and captured stderr.
3. WHEN `aspects.dry_run` is `True` THE SYSTEM SHALL NOT execute any command.

### Requirement 3: Report Daemon Status

**User Story:** As a coordinator, I want to query the current Tailscale status
so I can decide whether further action is required.

#### Acceptance Criteria

1. WHEN `status(aspects)` is called THE SYSTEM SHALL invoke
   `tailscale status --json` via the command runner without elevation.
2. WHEN the JSON parses successfully THE SYSTEM SHALL return a `VPNStatus`
   with `running`, `self_address`, `hostname`, `tags`, and `backend_state`.
3. IF the JSON cannot be parsed THEN THE SYSTEM SHALL raise `VPNStatusError`
   with the raw stdout body attached as context.
4. IF `tailscale status --json` exits non-zero with the literal substring
   `Logged out` THEN THE SYSTEM SHALL return `VPNStatus(running=False)`
   without raising.

### Requirement 4: Report Local Overlay Address

**User Story:** As a coordinator, I want the local Tailscale overlay IP so I
can register it on a landscape device.

#### Acceptance Criteria

1. WHEN `self_address()` is called and the cached status has a `self_address`
   THE SYSTEM SHALL return that address as a string.
2. IF no cached status is available THEN THE SYSTEM SHALL call `status(aspects)`
   first with default aspects.
3. IF the node has no allocated overlay address THEN THE SYSTEM SHALL return
   `None`.

### Requirement 5: Enumerate Peer Overlay Addresses

**User Story:** As a coordinator, I want a `{hostname: overlay_ip}` mapping of
peers so I can resolve overlay names without contacting the control plane.

#### Acceptance Criteria

1. WHEN `peer_addresses()` is called THE SYSTEM SHALL parse the `Peer` map from
   `tailscale status --json` and SHALL return a `Dict[str, str]` keyed by peer
   short hostname.
2. WHERE a peer has multiple IPs THE SYSTEM SHALL select the first entry from
   the `100.64.0.0/10` CGNAT range.
3. WHEN no peers are present THE SYSTEM SHALL return an empty dict.

### Requirement 6: Aspects on Every Behaviour-Bearing Call

**User Story:** As a consumer, I want to control timeouts, retry, logging, and
elevation per call so behaviour is never baked into the client.

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: Aspects` on `bring_up`, `bring_down`, and
   `status`, defaulting to `DEFAULT_VPN_CLIENT_ASPECTS` when omitted.
2. THE SYSTEM SHALL NOT use any behaviour-modifying decorators (`@retry`,
   `@cached`, `@timeout`) on any method.
3. WHERE `aspects.elevated` is `True` THE SYSTEM SHALL pass `elevated=True` to
   the command runner for write operations (`up`, `down`).
4. THE SYSTEM SHALL NOT elevate read operations (`status`).
