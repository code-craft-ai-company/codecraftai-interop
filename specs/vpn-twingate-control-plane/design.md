# Design

## Overview

`TwingateControlPlane` is a `RestClientBase` subclass wrapping the Twingate
admin GraphQL API at `/api/graphql/`. It implements `IVPNControlPlane`.
Because Twingate's model is resource-scoped rather than flat-mesh, several
`IVPNControlPlane` methods do not map 1:1 onto Twingate calls — the client
exposes the closest faithful translation and raises `SemanticError` early when
a caller asks for behaviour Twingate cannot provide (e.g., reusable connector
tokens).

**See Also:**
- [vpn-twingate-client](../vpn-twingate-client/design.md) — local-daemon
  counterpart.
- [vpn-tailscale-control-plane](../vpn-tailscale-control-plane/design.md) —
  sibling, mesh-style control plane.
- automojo-restclient-base — `RestClientBase`, `AspectsRest`,
  `GraphQLApiGroup` helper (added under the `restapigroup-enhancements`
  feature).

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Caller (provisioning bootstrap, landscape coupling)         │
└──────────────────────────────┬───────────────────────────────┘
                               │ IVPNControlPlane
                               ▼
┌──────────────────────────────────────────────────────────────┐
│         TwingateControlPlane(RestClientBase)                 │
│  interop/vpn/twingate/twingatecontrolplane.py                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ apigroups/                                             │  │
│  │  ├── ConnectorsGroup (mint tokens, delete, list)       │  │
│  │  ├── ResourcesGroup  (create/update/list)              │  │
│  │  ├── GroupsGroup     (create/update/list)              │  │
│  │  └── AccessGroup     (resourceAccessAdd/Remove)        │  │
│  └────────────────────────────────────────────────────────┘  │
│  _authenticate()  →  bearer + X-Network-Slug header set      │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTPS POST GraphQL queries
                               ▼
              <network>.twingate.com/api/graphql/
```

---

## Data Model

Shared `VPNDeviceRecord` is reused; Twingate connector records have empty
`addresses`. New types:

```python
@dataclass
class TwingateConnector:
    connector_id: str
    name: str
    remote_network_id: str
    state: str

@dataclass
class TwingateResource:
    resource_id: str
    name: str
    address: str   # FQDN or CIDR
    protocols: Dict[str, List[int]]

@dataclass
class TwingateGroup:
    group_id: str
    name: str
    user_ids: List[str]
```

Exceptions reused:
`VPNControlPlaneAuthKeyError`, `VPNControlPlaneQueryError`,
`VPNControlPlaneMutationError`, `VPNControlPlaneACLError`.

`AspectsTwingate(AspectsRest)` adds `mutation_dependency_pause_seconds`
(default 0.5) to space out dependent mutations when the API surfaces eventual
consistency lag. `DEFAULT_TWINGATE_ASPECTS` materialises with sane defaults.

---

## Module Layout

```
source/packages/automojo/interop/vpn/twingate/
├── twingatecontrolplane.py
├── aspectstwingate.py
├── model/
│   ├── twingateconnector.py
│   ├── twingateresource.py
│   └── twingategroup.py
└── apigroups/
    ├── connectorsgroup.py
    ├── resourcesgroup.py
    ├── groupsgroup.py
    └── accessgroup.py
```

Tests:

```
source/testroots/.../twingate/
├── test_twingatecontrolplane.py
├── test_connectorsgroup.py
├── test_resourcesgroup.py
├── test_accessgroup.py
└── fixtures/
    ├── generate_tokens_response.json
    ├── connectors_list_response.json
    └── connector_not_found_error.json
```

---

## GraphQL Operations

| Operation | GraphQL |
|---|---|
| `mint_authkey` | `mutation connectorGenerateTokens(connectorId)` |
| `list_devices` | `query { connectors { edges { node { ... } } } }` |
| `delete_device` | `mutation connectorDelete(id)` |
| `apply_acl` create resource | `mutation resourceCreate(...)` |
| `apply_acl` update resource | `mutation resourceUpdate(...)` |
| `apply_acl` group create | `mutation groupCreate(...)` |
| `apply_acl` access add | `mutation resourceAccessAdd(...)` |

---

## Idempotent RBAC Apply Algorithm

`apply_acl` proceeds in three phases:

1. Resource phase: for each declared resource, look up by `name`; if absent,
   `resourceCreate`; if present, `resourceUpdate` only when payload differs.
2. Group phase: same pattern with `groupCreate` / `groupUpdate`.
3. Assignment phase: for each `(group, resource)` tuple in `assignments`,
   issue `resourceAccessAdd` if absent.

Between phases the client pauses
`aspects.mutation_dependency_pause_seconds` to accommodate eventual
consistency.

---

## Testing Strategy

- Fake GraphQL transport returns canned response bodies keyed by operation
  name extracted from the request body.
- `mint_authkey` tests cover happy path, empty-tags raising `SemanticError`,
  reusable/ephemeral raising `SemanticError`, and 4xx mutation error path.
- `list_devices` test parses a fixture covering connectors and remote
  networks combined.
- `delete_device` tests assert both the success path and the not-found path
  return `None`.
- `apply_acl` tests assert phase ordering and idempotent skip behaviour when
  resources/groups already exist.
- Authentication test asserts both `Authorization` and `X-Network-Slug`
  headers are set.
