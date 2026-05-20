# Requirements

## Introduction

The `vpn-twingate-control-plane` feature provides `automojo-interop` with a
REST/GraphQL client that talks to the Twingate admin API. It implements
`IVPNControlPlane` from `automojo-interfaces`. Twingate's API is GraphQL at
`/api/graphql/`; the client is built on `RestClientBase` and wraps GraphQL
queries/mutations through a `GraphQLApiGroup` helper.

Twingate's data model differs from Tailscale's: there are *resources*
(addressable things like FQDNs, CIDRs), *groups*, and *service accounts*.
There is no flat-mesh ACL document, and there is no per-device overlay IP. The
client's `apply_acl` method maps onto the closest analog — applying a
resource-and-group RBAC bundle — and is documented as a shape adjustment, not
a 1:1 of the Tailscale call.

All methods take named parameters. Behaviour rides on `aspects`. No
`@retry` or similar decorators are used.

---

## Requirements

### Requirement 1: Mint a Connector Auth Token

**User Story:** As a provisioning engine, I want to mint a connector token
pair (access + refresh) per connector host so each provisioned connector has
distinct, revocable credentials.

#### Acceptance Criteria

1. WHEN `mint_authkey(reusable, ephemeral, tags, ttl_seconds, aspects)` is
   called THE SYSTEM SHALL issue a GraphQL `connectorGenerateTokens` mutation
   against a connector identified by the first entry of `tags`
   (treated as the connector name).
2. WHEN the mutation returns successfully THE SYSTEM SHALL return the combined
   `"<accessToken>:<refreshToken>"` string for direct consumption by
   `TwingateClient.bring_up(authkey=...)`.
3. IF `tags` is empty THEN THE SYSTEM SHALL raise `SemanticError` — Twingate
   requires a connector identity, unlike Tailscale's tagless flow.
4. WHERE `reusable=True` or `ephemeral=True` are requested THE SYSTEM SHALL
   raise `SemanticError` — Twingate connector tokens are neither (decision
   surfaced honestly, not silently coerced).
5. IF the mutation returns errors THEN THE SYSTEM SHALL raise
   `VPNControlPlaneAuthKeyError`.

### Requirement 2: List Twingate Devices (Connectors and Clients)

**User Story:** As a landscape coordinator, I want to enumerate Twingate
connectors and registered clients so I can match them against landscape
devices by name/tag.

#### Acceptance Criteria

1. WHEN `list_devices(aspects)` is called THE SYSTEM SHALL issue the
   `connectors` and `remoteNetworks` queries and SHALL return a combined
   `List[VPNDeviceRecord]`.
2. WHERE a device record represents a connector THE SYSTEM SHALL leave
   `addresses` empty (Twingate connectors do not get overlay IPs).
3. IF the queries fail THEN THE SYSTEM SHALL raise
   `VPNControlPlaneQueryError`.

### Requirement 3: Delete a Device

**User Story:** As a provisioning engine running `destroy`, I want to remove a
torn-down connector from the Twingate admin console.

#### Acceptance Criteria

1. WHEN `delete_device(device_id, aspects)` is called THE SYSTEM SHALL issue
   the `connectorDelete` mutation with `id=device_id`.
2. WHEN the response reports `ok=true` THE SYSTEM SHALL return `None`.
3. WHEN the response reports a `not found` error THE SYSTEM SHALL return
   `None` (idempotent destroy semantics).
4. IF any other error is returned THEN THE SYSTEM SHALL raise
   `VPNControlPlaneMutationError`.

### Requirement 4: Apply an RBAC Policy

**User Story:** As a landscape administrator, I want to push a resource +
group RBAC bundle so access policy reflects current landscape membership.

#### Acceptance Criteria

1. WHEN `apply_acl(acl_doc, aspects)` is called THE SYSTEM SHALL interpret
   `acl_doc` as a dictionary with keys `resources`, `groups`, `assignments`
   and SHALL issue the matching `resourceCreate` / `groupCreate` /
   `resourceAccessAdd` mutations in dependency order.
2. WHERE a resource or group already exists by `name` THE SYSTEM SHALL update
   it instead of failing (idempotent apply).
3. IF any mutation in the sequence errors THEN THE SYSTEM SHALL raise
   `VPNControlPlaneACLError` carrying the failing mutation name and message.
4. THE SYSTEM SHALL document in the docstring that this method does NOT
   shape-match the Tailscale `apply_acl` JSON document.

### Requirement 5: Service Account Authentication

#### Acceptance Criteria

1. THE SYSTEM SHALL authenticate using the `TwingateServiceAccountCredential`
   (API token + network slug) and SHALL set
   `Authorization: Bearer <token>` on every request.
2. THE SYSTEM SHALL set `X-Network-Slug` header from the credential.

### Requirement 6: Aspects on Every Call

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: AspectsRest` on every public method
   defaulting to `DEFAULT_TWINGATE_ASPECTS`.
2. THE SYSTEM SHALL NOT use behaviour-modifying decorators.
