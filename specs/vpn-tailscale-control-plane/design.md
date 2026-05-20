# Design

## Overview

`TailscaleControlPlane` is a `RestClientBase` subclass that wraps the public
Tailscale REST API. It satisfies `IVPNControlPlane` and is the canonical
administration surface for tailnets — minting auth keys, enumerating devices,
deleting devices, and applying ACL documents.

It is paired with [vpn-tailscale-client](../vpn-tailscale-client/design.md)
which talks to the local daemon. Together they cover the two distinct
Tailscale interaction styles. Provisioning uses the control plane to mint
short-lived auth keys per instance; landscaping uses it for peer discovery on
landscapes where no daemon is reachable locally.

**See Also:**
- [vpn-tailscale-client](../vpn-tailscale-client/design.md)
- automojo-restclient-base (`RestClientBase`, `AspectsRest`, `RestApiGroup`)
- automojo-credentials specs for `TailscaleAuthKeyCredential` and
  `TailscaleOAuthCredential`.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Caller (provisioning bootstrap, landscape coupling)         │
└──────────────────────────────┬───────────────────────────────┘
                               │ IVPNControlPlane
                               ▼
┌──────────────────────────────────────────────────────────────┐
│             TailscaleControlPlane(RestClientBase)            │
│  interop/vpn/tailscale/tailscalecontrolplane.py              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ apigroups/                                             │  │
│  │  ├── KeysGroup       (mint_authkey)                    │  │
│  │  ├── DevicesGroup    (list_devices, delete_device)     │  │
│  │  └── ACLGroup        (apply_acl)                       │  │
│  └────────────────────────────────────────────────────────┘  │
│  _authenticate()  →  OAuth token mint OR static key passthru │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTPS, bearer auth
                               ▼
                    api.tailscale.com
```

---

## Data Model

```python
@dataclass
class VPNDeviceRecord:
    device_id: str
    hostname: str
    name: str                  # MagicDNS name
    addresses: List[str]       # may contain v4 + v6 overlay IPs
    tags: List[str]
    last_seen: Optional[str]   # ISO8601 from API
    os: Optional[str]
    user: Optional[str]

class VPNControlPlaneAuthKeyError(Exception):
    """Raised when mint_authkey fails."""

class VPNControlPlaneQueryError(Exception):
    """Raised when list_devices or similar reads fail."""

class VPNControlPlaneMutationError(Exception):
    """Raised when a mutation (delete) fails."""

class VPNControlPlaneACLError(Exception):
    """Raised when apply_acl fails."""
```

`AspectsTailscale` extends `AspectsRest` with `tailnet_default_ttl_seconds`
and `oauth_refresh_margin_seconds`. `DEFAULT_TAILSCALE_ASPECTS` sets
`tailnet_default_ttl_seconds=900` (15 minutes), per the §5 decision in
PLAN-VPN-AND-CLOUD-PROVISIONING.

---

## Module Layout

```
source/packages/automojo/interop/vpn/tailscale/
├── tailscalecontrolplane.py
├── aspectstailscale.py
├── model/
│   ├── vpndevicerecord.py
│   └── vpnauthkey.py
└── apigroups/
    ├── keysgroup.py
    ├── devicesgroup.py
    └── aclgroup.py
```

Tests:

```
source/testroots/.../tailscale/
├── test_tailscalecontrolplane.py
├── test_keysgroup.py
├── test_devicesgroup.py
├── test_aclgroup.py
└── fixtures/
    ├── mint_key_response.json
    ├── list_devices_response.json
    └── oauth_token_response.json
```

---

## Endpoint Mappings

| Method | HTTP | Path |
|---|---|---|
| `mint_authkey` | POST | `/api/v2/tailnet/<tailnet>/keys?all=true` |
| `list_devices` | GET | `/api/v2/tailnet/<tailnet>/devices?fields=all` |
| `delete_device` | DELETE | `/api/v2/device/<device_id>` |
| `apply_acl` | POST | `/api/v2/tailnet/<tailnet>/acl` |
| `_mint_oauth_token` | POST | `/api/v2/oauth/token` |

The `<tailnet>` value is sourced from the credential's `tailnet` field at
client construction.

---

## Authentication Flow

1. If credential is `TailscaleAuthKeyCredential`: use `key.value` as the bearer
   token for every request. No caching needed.
2. If credential is `TailscaleOAuthCredential`: maintain
   `(token, expires_at_epoch)` in instance state. Before each request, check
   `time.time() + aspects.oauth_refresh_margin_seconds >= expires_at_epoch`;
   if so, POST client credentials to `/api/v2/oauth/token`, parse
   `access_token` and `expires_in`, update state.

The 404-on-delete idempotency exception is implemented in `DevicesGroup` by
catching `HttpNotFoundError` and returning `None`.

---

## Testing Strategy

- A fake transport (`FakeRestTransport`) returns canned `RestResponse` objects
  keyed by `(method, path)`.
- `mint_authkey` test asserts request body shape — `reusable`, `ephemeral`,
  `preauthorized=true`, `tags`, `expirySeconds`.
- `list_devices` test parses the fixture response into the expected
  `VPNDeviceRecord` set.
- `delete_device` test exercises both the 200 and 404 paths and verifies
  neither raises.
- `apply_acl` test asserts JSON content-type and POST body.
- OAuth flow tests assert exactly one token-mint call across multiple
  consecutive requests and exactly two when the refresh margin is crossed.
- Negative path tests for each typed exception, asserting it carries response
  body text.
- `mint_authkey` with non-positive `ttl_seconds` asserts `SemanticError` is
  raised before any HTTP traffic.
