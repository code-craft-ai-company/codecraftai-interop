# Implementation Plan — Twingate Client

- [x] 1. Create `automojo/interop/vpn/twingate/` package.
- [x] 2. Create `connectorinvocation.py`:
  - [x] 2a. `compose_setup_argv(authkey, hostname)` — splits the combined token
    string, returns argv list.
  - [x] 2b. `compose_service_argv(action)` — `systemctl <action> twingate-connector`.
- [x] 3. Create `twingateclient.py`:
  - [x] 3a. `bring_up(*, authkey, hostname=None, advertise_tags=None, aspects=DEFAULT_VPN_CLIENT_ASPECTS)`.
  - [x] 3b. `bring_down(*, aspects=DEFAULT_VPN_CLIENT_ASPECTS)`.
  - [x] 3c. `status(*, aspects=DEFAULT_VPN_CLIENT_ASPECTS)`.
  - [x] 3d. `self_address() -> None` (returns `None` unconditionally).
  - [x] 3e. `peer_addresses() -> Dict[str, str]` — returns `{}`, emits a
    process-once DEBUG log.
- [x] 4. Document the provider asymmetry in the class docstring.
- [x] 5. Apply project coding standards (named-only params, explicit returns,
  no behaviour-modifying decorators).
- [x] 6. Tests — example-based:
  - [x] 6a. `test_bring_up_invokes_setup_then_start`.
  - [x] 6b. `test_bring_up_includes_name_flag_when_hostname_supplied`.
  - [x] 6c. `test_bring_up_setup_failure_raises_VPNBringUpError`.
  - [x] 6d. `test_bring_up_start_failure_raises_VPNBringUpError`.
  - [x] 6e. `test_bring_up_dry_run_does_not_invoke_runner`.
  - [x] 6f. `test_bring_down_invokes_systemctl_stop`.
  - [x] 6g. `test_status_maps_active_to_running_true`.
  - [x] 6h. `test_status_maps_inactive_to_running_false`.
  - [x] 6i. `test_self_address_is_none_always`.
  - [x] 6j. `test_peer_addresses_is_empty_and_debug_logged_once`.
  - [x] 6k. `test_writes_elevate_when_aspect_set`.
  - [x] 6l. `test_reads_never_elevate`.
- [x] 7. Capture two fixture outputs (`systemctl is-active`, connector setup
  failure) and add to test resources.
- [x] 8. Export `TwingateClient` from `automojo.interop.vpn` `__init__.py`.
