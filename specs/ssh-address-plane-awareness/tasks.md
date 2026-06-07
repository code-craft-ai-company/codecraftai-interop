# Implementation Plan — SSH Address-Plane Awareness

- [x] 1. Add `SSHAddressPlaneUnavailableError` to
  `ccai/interop/protocols/ssh/exceptions.py`.
- [x] 2. Create `ccai/interop/protocols/ssh/planeresolver.py`:
  - [x] 2a. Implement `resolve_dial_target(*, address_set, preferred_plane,
    fallback_planes)` as a pure function.
  - [x] 2b. Raise `SSHAddressPlaneUnavailableError` with the attempted list
    when nothing resolves.
- [x] 3. Update `ccai/interop/protocols/ssh/sshbase.py`:
  - [x] 3a. Add keyword-only params `device`, `address_plane`,
    `fallback_planes` to `connect(...)`.
  - [x] 3b. Raise `SemanticError` when both `host` and `device` are supplied.
  - [x] 3c. Branch: literal-`host` path is unchanged; `device` path calls
    `resolve_dial_target`.
  - [x] 3d. Log at INFO the device name, preferred plane, plane used, and
    dial target.
  - [x] 3e. Log at WARNING any skipped planes.
- [x] 4. Apply project coding standards (named-only, explicit returns).
- [x] 5. Tests — example-based:
  - [x] 5a. `test_connect_with_literal_host_ignores_plane`.
  - [x] 5b. `test_connect_with_host_and_device_raises_semantic`.
  - [x] 5c. `test_connect_default_plane_uses_public_address`.
  - [x] 5d. `test_connect_overlay_plane_uses_overlay_address`.
  - [x] 5e. `test_connect_falls_through_to_first_available`.
  - [x] 5f. `test_connect_no_plane_available_raises`.
  - [x] 5g. `test_logging_captures_plane_choice_and_skips`.
- [x] 6. Tests for `resolve_dial_target`:
  - [x] 6a. Each plane present alone — returns that address.
  - [x] 6b. Preferred absent, fallback present — returns fallback.
  - [x] 6c. Empty string address treated as absent.
  - [x] 6d. All absent raises typed error.
- [x] 7. Cross-reference `device-address-set` property tests for the broader
  totality coverage; assert here that the integration code path delegates to
  the same resolver (no copy-paste of the algorithm).
- [x] 8. Update the SSHBase class docstring to describe the new parameters
  and link to the `device-address-set` spec.
