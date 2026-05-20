# Design

## Overview

This feature adds an `address_plane` parameter (and an optional
`fallback_planes` list) to `SSHBase.connect(...)`. Plane resolution is
extracted into a pure function so it is independently testable and so the
selection logic stays out of the network-bound class. The default value
(`AddressPlane.PUBLIC`) keeps every existing caller bit-identical.

**See Also:**
- [device-address-set](../../../automojo-landscaping/specs/device-address-set/design.md)
  defines `IDeviceAddressSet` and the plane-resolution semantics.
- [vpn-tailscale-client](../vpn-tailscale-client/design.md) supplies the
  overlay address consumed when `OVERLAY` is requested.
- [overlay-dns-resolver](../overlay-dns-resolver/design.md) is the DNS-side
  analog of this feature.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│   Caller (test framework, landscaping coordinator)           │
│   ssh.connect(device=dev, address_plane=OVERLAY,             │
│               fallback_planes=[PRIVATE, PUBLIC], aspects=…)  │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                       SSHBase                                │
│  interop/protocols/ssh/sshbase.py                            │
│   connect(host?, device?, address_plane, fallback_planes,    │
│           aspects)                                            │
│        │                                                     │
│        ├─► resolve_dial_target(...)  (pure)                  │
│        │                                                     │
│        ▼                                                     │
│   _open_session(target, aspects)                             │
└──────────────────────────────────────────────────────────────┘
```

`resolve_dial_target` is the pivot point. It takes only data structures and
enums and returns a string or raises.

---

## Data Model and Signatures

```python
from automojo.interfaces.addressplane import AddressPlane
from automojo.interfaces.deviceaddressset import IDeviceAddressSet

class SSHAddressPlaneUnavailableError(Exception):
    """Raised when no requested address plane resolves on the device."""

def resolve_dial_target(
    *,
    address_set: IDeviceAddressSet,
    preferred_plane: AddressPlane,
    fallback_planes: Optional[List[AddressPlane]],
) -> str:
    ...

class SSHBase:
    def connect(
        self,
        *,
        host: Optional[str] = None,
        device: Optional["LandscapeDevice"] = None,
        address_plane: AddressPlane = AddressPlane.PUBLIC,
        fallback_planes: Optional[List[AddressPlane]] = None,
        aspects: AspectsSSH = DEFAULT_SSH_ASPECTS,
    ) -> "SSHSession":
        ...
```

`host` and `device` are mutually exclusive. Passing both raises
`SemanticError` (caller bug).

---

## Resolution Algorithm

```
def resolve_dial_target(address_set, preferred_plane, fallback_planes):
    attempted = [preferred_plane] + (fallback_planes or [])
    skipped = []
    for plane in attempted:
        addr = address_set.resolve(plane)
        if addr is not None and len(addr) > 0:
            return addr
        skipped.append(plane)
    raise SSHAddressPlaneUnavailableError(
        "no usable plane for {dev}; attempted={attempted}".format(...)
    )
```

The algorithm is total over the input space defined in
[device-address-set](../../../automojo-landscaping/specs/device-address-set/design.md):
either it returns a non-empty string or it raises a single typed exception.

---

## Module Layout

```
source/packages/automojo/interop/protocols/ssh/
├── sshbase.py            ← gains keyword params; minimal change
├── planeresolver.py      ← resolve_dial_target() pure function
└── exceptions.py         ← adds SSHAddressPlaneUnavailableError
```

Tests:

```
source/testroots/.../ssh/
├── test_planeresolver.py
└── test_sshbase_plane_integration.py
```

---

## Backwards Compatibility

- Existing call sites passing only `host=` continue to work — the
  `address_plane` default of `PUBLIC` is ignored when no `device` is supplied.
- Existing call sites passing `device=` without `address_plane` connect on the
  PUBLIC plane, matching today's behaviour.
- A landscape opting in to OVERLAY-first behaviour sets the plane at the
  landscape level; the SSH layer simply consumes the value passed in.

---

## Testing Strategy

- **Example tests** for the `SSHBase` integration:
  - `connect(host="1.2.3.4")` ignores plane resolution.
  - `connect(host=..., device=...)` raises `SemanticError`.
  - `connect(device=...)` with the default plane dials the PUBLIC address.
  - `connect(device=..., address_plane=OVERLAY)` dials the overlay address.
  - Fall-through walks the fallback list in order and stops at the first
    available plane.
  - Logging assertions cover INFO for the chosen plane and WARNING for any
    skipped planes.
- **Plane selection unit tests** for `resolve_dial_target` cover the cartesian
  product of plane-present / plane-absent combinations.
- Property-style coverage of `resolve_dial_target` lives in the
  `device-address-set` spec (since the semantics belong to the
  `IDeviceAddressSet` contract). The SSH-side tests assert integration only.
