# Implementation Plan — Twingate Control Plane

- [x] 1. Create `ccai/interop/vpn/twingate/aspectstwingate.py` with
  `AspectsTwingate` and `DEFAULT_TWINGATE_ASPECTS`.
- [x] 2. Create model dataclasses (`TwingateConnector`, `TwingateResource`,
  `TwingateGroup`).
- [x] 3. Create `apigroups/connectorsgroup.py`:
  - [x] 3a. `generate_tokens(*, connector_id, aspects)`.
  - [x] 3b. `list(*, aspects)`.
  - [x] 3c. `delete(*, connector_id, aspects)` — swallows not-found errors.
- [x] 4. Create `apigroups/resourcesgroup.py` with create/update/list.
- [x] 5. Create `apigroups/groupsgroup.py` with create/update/list.
- [x] 6. Create `apigroups/accessgroup.py` with `add(*, group_id, resource_id, aspects)`
  and `remove(...)`.
- [x] 7. Create `twingatecontrolplane.py`:
  - [x] 7a. `__init__(*, credential, aspects=DEFAULT_TWINGATE_ASPECTS)` —
    composes base URL from `credential.network_slug`.
  - [x] 7b. Override `_authenticate(...)` — bearer + `X-Network-Slug` header.
  - [x] 7c. `mint_authkey(*, reusable, ephemeral, tags, ttl_seconds, aspects)` —
    raises `SemanticError` on `reusable=True` or `ephemeral=True` or empty
    tags, then delegates to `connectorsgroup.generate_tokens` and returns the
    `"<access>:<refresh>"` string.
  - [x] 7d. `list_devices(*, aspects)` — composes connector list into
    `List[VPNDeviceRecord]` with empty `addresses`.
  - [x] 7e. `delete_device(*, device_id, aspects)`.
  - [x] 7f. `apply_acl(*, acl_doc, aspects)` — three-phase idempotent apply.
- [x] 8. Apply project coding standards.
- [x] 9. Tests — example-based:
  - [x] 9a. `test_mint_authkey_combines_tokens`.
  - [x] 9b. `test_mint_authkey_empty_tags_raises_semantic`.
  - [x] 9c. `test_mint_authkey_reusable_raises_semantic`.
  - [x] 9d. `test_mint_authkey_ephemeral_raises_semantic`.
  - [x] 9e. `test_list_devices_parses_connectors_fixture`.
  - [x] 9f. `test_delete_device_ok`.
  - [x] 9g. `test_delete_device_not_found_returns_none`.
  - [x] 9h. `test_delete_device_other_error_raises_mutation_error`.
  - [x] 9i. `test_apply_acl_creates_then_assigns`.
  - [x] 9j. `test_apply_acl_updates_existing_resource_in_place`.
  - [x] 9k. `test_authentication_sets_bearer_and_slug_headers`.
- [x] 10. Capture three fixtures (generate tokens, connectors list, not-found
  error).
- [x] 11. Export `TwingateControlPlane` from the package `__init__.py`.
