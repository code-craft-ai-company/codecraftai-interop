# Requirements

## Introduction

The `vpn-tailscale-control-plane` feature provides `codecraftai-interop` with a
REST client that talks to `api.tailscale.com` to mint auth keys, enumerate
tailnet devices, delete devices, and apply ACL documents. It implements the
`IVPNControlPlane` protocol from `codecraftai-interfaces`.

The client is built on `RestClientBase` from `codecraftai-restclient-base` and
uses an `AspectsRest` subclass so every call accepts caller-controlled
retry, timeout, and logging behaviour. Authentication uses either a
`TailscaleAuthKeyCredential` (tagged service key) or a
`TailscaleOAuthCredential` (preferred for production — mints short-lived
keys on demand).

All methods take named parameters. No `@retry` or other behaviour-modifying
decorators are used.

---

## Requirements

### Requirement 1: Mint an Auth Key

**User Story:** As a provisioning engine, I want to mint a short-lived,
preauthorized, ephemeral auth key per cloud instance so per-instance cloud-init
secrets are scoped and disposable.

#### Acceptance Criteria

1. WHEN `mint_authkey(reusable, ephemeral, tags, ttl_seconds, aspects)` is
   called THE SYSTEM SHALL POST to
   `/api/v2/tailnet/<tailnet>/keys?all=true` with a JSON body containing
   `capabilities.devices.create.reusable`, `ephemeral`, `preauthorized=true`,
   `tags`, plus the `expirySeconds` field set to `ttl_seconds`.
2. WHEN the response is 2xx THE SYSTEM SHALL return the `key` value from the
   parsed JSON body.
3. IF the response is 4xx THEN THE SYSTEM SHALL raise
   `VPNControlPlaneAuthKeyError` carrying the request body and parsed response
   body.
4. IF `ttl_seconds` is `0` or negative THEN THE SYSTEM SHALL raise
   `SemanticError` before issuing the request.
5. WHEN `tags` is empty THE SYSTEM SHALL omit the `tags` field from the body.

### Requirement 2: List Tailnet Devices

**User Story:** As a landscape coordinator, I want to list every device in the
tailnet with its overlay IPs and hostname so I can attach overlay addresses to
landscape devices.

#### Acceptance Criteria

1. WHEN `list_devices(aspects)` is called THE SYSTEM SHALL GET
   `/api/v2/tailnet/<tailnet>/devices?fields=all`.
2. WHEN the response is 2xx THE SYSTEM SHALL return a `List[VPNDeviceRecord]`
   with each entry populated from `id`, `hostname`, `name`, `addresses`,
   `tags`, `lastSeen`.
3. IF the response is not 2xx THEN THE SYSTEM SHALL raise
   `VPNControlPlaneQueryError`.

### Requirement 3: Delete a Device

**User Story:** As a provisioning engine running `destroy`, I want to remove a
torn-down instance from the tailnet so the device list does not grow stale.

#### Acceptance Criteria

1. WHEN `delete_device(device_id, aspects)` is called THE SYSTEM SHALL DELETE
   `/api/v2/device/<device_id>`.
2. WHEN the response is 2xx or 404 THE SYSTEM SHALL return `None`
   (404 is treated as already-removed, satisfying idempotency).
3. IF the response is any other non-2xx THEN THE SYSTEM SHALL raise
   `VPNControlPlaneMutationError` carrying the response body.

### Requirement 4: Apply an ACL Document

**User Story:** As a landscape administrator, I want to push a tailnet-wide
ACL JSON document so tag-based access policy reflects the current landscape.

#### Acceptance Criteria

1. WHEN `apply_acl(acl_doc, aspects)` is called THE SYSTEM SHALL POST the
   document to `/api/v2/tailnet/<tailnet>/acl` with
   `Content-Type: application/json`.
2. WHEN the response is 2xx THE SYSTEM SHALL return `None`.
3. IF the response is 4xx with a parsed `message` body THEN THE SYSTEM SHALL
   raise `VPNControlPlaneACLError` carrying the message.

### Requirement 5: OAuth-Based Authentication

**User Story:** As an operator, I want OAuth-minted short-lived bearer tokens
to authenticate the client so static API keys do not have to be checked in or
distributed.

#### Acceptance Criteria

1. WHERE the configured credential is `TailscaleOAuthCredential` THE SYSTEM
   SHALL POST `client_id` and `client_secret` to `/api/v2/oauth/token` and
   cache the returned `access_token` until 60 seconds before its `expires_in`.
2. WHEN the cached token is within 60 seconds of expiry THE SYSTEM SHALL
   re-mint a new token before issuing the next request.
3. WHERE the configured credential is `TailscaleAuthKeyCredential` THE SYSTEM
   SHALL use the credential value directly as the bearer token.

### Requirement 6: Aspects on Every Call

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: AspectsRest` on every public method,
   defaulting to `DEFAULT_TAILSCALE_ASPECTS`.
2. THE SYSTEM SHALL NOT use any behaviour-modifying decorators.
3. THE SYSTEM SHALL inherit retry/backoff and `raise_for_http_status` from
   `RestClientBase`.
