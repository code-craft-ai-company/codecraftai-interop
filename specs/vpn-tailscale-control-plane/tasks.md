# Implementation Plan — Tailscale Control Plane

- [x] 1. Create `ccai/interop/vpn/tailscale/aspectstailscale.py` with
  `AspectsTailscale` and `DEFAULT_TAILSCALE_ASPECTS`.
- [x] 2. Create `model/vpndevicerecord.py` with the `VPNDeviceRecord`
  dataclass (move to shared location if already defined upstream).
- [x] 3. Create `model/vpnauthkey.py` — value object covering API response
  shape for minted keys.
- [x] 4. Create exceptions: `VPNControlPlaneAuthKeyError`,
  `VPNControlPlaneQueryError`, `VPNControlPlaneMutationError`,
  `VPNControlPlaneACLError`.
- [x] 5. Create `apigroups/keysgroup.py`:
  - [x] 5a. `mint(*, reusable, ephemeral, tags, ttl_seconds, aspects)`.
  - [x] 5b. Compose JSON body per design.
  - [x] 5c. Raise `SemanticError` on non-positive TTL before HTTP.
- [x] 6. Create `apigroups/devicesgroup.py`:
  - [x] 6a. `list(*, aspects)` — parses devices array.
  - [x] 6b. `delete(*, device_id, aspects)` — swallows 404 as idempotent.
- [x] 7. Create `apigroups/aclgroup.py`:
  - [x] 7a. `apply(*, acl_doc, aspects)`.
- [x] 8. Create `tailscalecontrolplane.py`:
  - [x] 8a. `__init__(*, credential, base_url="https://api.tailscale.com", aspects=DEFAULT_TAILSCALE_ASPECTS)`.
  - [x] 8b. Override `_authenticate(...)` — branches by credential class.
  - [x] 8c. Wire `Keys`, `Devices`, `ACL` property accessors returning the
    matching `*Group`.
  - [x] 8d. Implement OAuth mint-and-cache with the refresh-margin check.
  - [x] 8e. `mint_authkey`, `list_devices`, `delete_device`, `apply_acl`
    delegate to their groups.
- [x] 9. Apply project coding standards — named-only params, explicit returns,
  no behaviour-modifying decorators.
- [x] 10. Tests — example-based:
  - [x] 10a. `test_mint_authkey_body_shape`.
  - [x] 10b. `test_mint_authkey_ttl_zero_raises_semantic`.
  - [x] 10c. `test_mint_authkey_4xx_raises_typed_error`.
  - [x] 10d. `test_list_devices_parses_fixture`.
  - [x] 10e. `test_delete_device_204_returns_none`.
  - [x] 10f. `test_delete_device_404_returns_none`.
  - [x] 10g. `test_delete_device_500_raises`.
  - [x] 10h. `test_apply_acl_posts_json`.
  - [x] 10i. `test_oauth_token_minted_once_when_cached`.
  - [x] 10j. `test_oauth_token_refreshed_after_margin_crossed`.
  - [x] 10k. `test_static_authkey_credential_bypasses_oauth_path`.
- [x] 11. Capture three fixtures (mint key, list devices, oauth token).
- [x] 12. Export `TailscaleControlPlane` from the package `__init__.py`.
