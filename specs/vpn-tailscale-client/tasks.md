# Implementation Plan — Tailscale Client

- [x] 1. Create `automojo/interop/vpn/` package with `__init__.py`.
- [x] 2. Create `vpnclientbase.py` with `VPNClientBase(IVPNClient)` abstract,
  accepting `command_runner: ICommandRunner`, `file_operator: IFileOperator`,
  `credential: BaseCredential` in `__init__`.
- [x] 3. Create `aspectsvpnclient.py` with `AspectsVPNClient` and the
  `DEFAULT_VPN_CLIENT_ASPECTS` constant.
- [x] 4. Create `tailscale/exceptions.py` with `VPNBringUpError`,
  `VPNBringDownError`, `VPNStatusError`.
- [x] 5. Create `tailscale/statusparser.py` that maps `tailscale status --json`
  output to `VPNStatus`. Handle the `Logged out` non-zero case as
  `running=False` without raising.
- [x] 6. Create `tailscale/tailscaleclient.py`:
  - [x] 6a. `bring_up(*, authkey, hostname=None, advertise_tags=None, aspects=DEFAULT_VPN_CLIENT_ASPECTS)`.
  - [x] 6b. `bring_down(*, aspects=DEFAULT_VPN_CLIENT_ASPECTS)`.
  - [x] 6c. `status(*, aspects=DEFAULT_VPN_CLIENT_ASPECTS) -> VPNStatus`.
  - [x] 6d. `self_address() -> Optional[str]` — caches last `VPNStatus`.
  - [x] 6e. `peer_addresses() -> Dict[str, str]` — refreshes status, parses
    peer map, picks the first CGNAT (`100.64.0.0/10`) address per peer.
- [x] 7. Apply project coding standards — explicit returns, named-only params,
  no decorators that modify behaviour.
- [x] 8. Add `BringUpResult` rendering for dry-run path returning a sentinel
  `VPNStatus(running=False, detail="dry-run")`.
- [x] 9. Tests — example-based:
  - [x] 9a. `test_bring_up_composes_argv_with_all_flags`.
  - [x] 9b. `test_bring_up_omits_hostname_when_none`.
  - [x] 9c. `test_bring_up_omits_tags_when_empty`.
  - [x] 9d. `test_bring_up_dry_run_does_not_invoke_runner`.
  - [x] 9e. `test_bring_up_non_zero_raises_VPNBringUpError`.
  - [x] 9f. `test_bring_down_invokes_tailscale_down`.
  - [x] 9g. `test_status_parses_running_fixture`.
  - [x] 9h. `test_status_handles_logged_out_without_raising`.
  - [x] 9i. `test_status_corrupt_json_raises_VPNStatusError`.
  - [x] 9j. `test_self_address_returns_cached_value`.
  - [x] 9k. `test_peer_addresses_picks_cgnat_address`.
  - [x] 9l. `test_writes_elevate_when_aspect_set`.
  - [x] 9m. `test_reads_never_elevate`.
- [x] 10. Capture three real-world `tailscale status --json` fixtures and add to
  test resources.
- [x] 11. Wire `TailscaleClient` into the `automojo.interop.vpn` package
  `__init__.py` for direct import.
