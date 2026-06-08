# Requirements

## Introduction

The `vpn-twingate-client` feature provides `codecraftai-interop` with a host-local
client that drives the Twingate connector through an `ICommandRunner`. It
implements `IVPNClient` from `codecraftai-interfaces`. Unlike Tailscale, Twingate
is hub-and-spoke and resource-scoped: a connector host does not receive a
mesh-style overlay IP. The client surfaces this asymmetry honestly — `self_address`
returns `None` and `peer_addresses` returns an empty mapping — rather than
synthesising fake data.

The client speaks to the local `twingate` CLI / connector service only. Twingate
network administration (resources, groups, ACL) lives in
`TwingateControlPlane` (see [vpn-twingate-control-plane](../vpn-twingate-control-plane/design.md)).
Install and service control live in the per-OS sysman packages.

All methods take named parameters. Behaviour-modifying parameters ride on
`Aspects`; there are no `@retry` or similar decorators.

---

## Requirements

### Requirement 1: Bring the Twingate Connector Up

**User Story:** As a coordinator, I want to register a connector with a Twingate
network using a connector token so the host begins routing for declared
resources.

#### Acceptance Criteria

1. WHEN `bring_up(authkey, hostname, advertise_tags, aspects)` is called with a
   non-empty `authkey` (connector token) THE SYSTEM SHALL invoke the connector
   `setup` and `start` commands via the command runner.
2. WHERE the runner OS is Linux THE SYSTEM SHALL invoke
   `twingate-connector setup --access-token=<k> --refresh-token=<r>` then
   `systemctl start twingate-connector` through the runner.
3. IF `hostname` is provided THEN THE SYSTEM SHALL pass `--name=<hostname>` to
   the connector setup command.
4. WHEN the commands exit zero THE SYSTEM SHALL return `VPNStatus(running=True,
   self_address=None, hostname=hostname, tags=advertise_tags or [],
   backend_state="Connected")`.
5. IF either command exits non-zero THEN THE SYSTEM SHALL raise
   `VPNBringUpError` carrying the failing argv, exit code, and stderr.
6. WHEN `aspects.dry_run` is `True` THE SYSTEM SHALL NOT execute any command
   and SHALL return `VPNStatus(running=False, detail="dry-run")`.

### Requirement 2: Bring the Connector Down

**User Story:** As a coordinator, I want to stop the local connector cleanly so
it stops routing traffic.

#### Acceptance Criteria

1. WHEN `bring_down(aspects)` is called THE SYSTEM SHALL invoke
   `systemctl stop twingate-connector` via the runner.
2. IF the stop command exits non-zero THEN THE SYSTEM SHALL raise
   `VPNBringDownError`.

### Requirement 3: Report Connector Status

**User Story:** As a coordinator, I want to know whether the connector service
is running.

#### Acceptance Criteria

1. WHEN `status(aspects)` is called THE SYSTEM SHALL invoke
   `systemctl is-active twingate-connector` via the runner.
2. WHEN stdout is the literal `active` THE SYSTEM SHALL return
   `VPNStatus(running=True, self_address=None, backend_state="active")`.
3. WHEN stdout is `inactive`, `failed`, or `unknown` THE SYSTEM SHALL return
   `VPNStatus(running=False, backend_state=<stdout>)` without raising.

### Requirement 4: Self Address Is Always `None`

**User Story:** As a consumer, I want a deterministic `None` for the connector
self-address so I don't accidentally route traffic through a non-existent
overlay IP.

#### Acceptance Criteria

1. THE SYSTEM SHALL return `None` from `self_address()` unconditionally.
2. THE SYSTEM SHALL document this in the class docstring.

### Requirement 5: Peer Addresses Is Always Empty

**User Story:** As a consumer, I want `peer_addresses()` on a Twingate client
to return an empty mapping so callers can use the same `IVPNClient` shape
without branching on provider.

#### Acceptance Criteria

1. THE SYSTEM SHALL return an empty `Dict[str, str]` from `peer_addresses()`.
2. THE SYSTEM SHALL log a single DEBUG message per process noting that peer
   enumeration is not supported on Twingate.

### Requirement 6: Aspects on Every Behaviour-Bearing Call

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: Aspects` on `bring_up`, `bring_down`, and
   `status`, defaulting to `DEFAULT_VPN_CLIENT_ASPECTS`.
2. THE SYSTEM SHALL NOT use any behaviour-modifying decorators.
3. WHERE `aspects.elevated` is `True` THE SYSTEM SHALL pass `elevated=True` for
   write operations (`setup`, `start`, `stop`).
4. THE SYSTEM SHALL NOT elevate `is-active` reads.
