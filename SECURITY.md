# Security and privacy

This is an independent Home Assistant custom integration. Security testing is
bounded to source review, synthetic regression tests and static analysis; it is
not an external audit or a guarantee that the integration or server is vulnerability-free.

## Trust boundaries

- Only the configured HTTP(S) server is contacted. TLS verification is enabled.
  Redirects are rejected for reads and writes. Local HTTP is explicitly supported
  for trusted LANs, but does not encrypt the API key or health values in transit.
- URL userinfo, query/fragment credentials and control characters are rejected.
  The server URL is configured by the HA administrator, not supplied in actions.
- Dedicated cookie-free aiohttp sessions prevent cookie-based user switching.
  Expected authenticated and active user IDs must match. Identity is checked
  before writes and each polling cycle. No family impersonation headers/IDs.
- Writes are disabled by default and independently enabled per config entry.
  Interactive actions require HA administrator rights. HA automations without a
  user context are trusted; limit who can edit/invoke scripts and automations.
- Six fixed POST paths with allowlisted payload fields. No arbitrary request,
  endpoint, headers, deletion, user_id, credential or generic health payload input.
  Category ownership is checked using the authenticated account's catalogue.
- Numeric values must be finite and within explicit bounds. Date/time inputs are
  validated; no future measurements, offset-free sleep timestamps or null deletes.
- Writes are serialized per account. Reads still run normally. No automatic retry
  of POST requests after timeouts/5xx/uncertain responses. A write may have reached
  the server even if the response was lost; inspect the server before repeating.
- HTTP 429 prevents requests during the server retry window. 403 on writes reports
  missing write permission without turning a valid read key into a login failure.
- Health-data ingestion HTTP 200 is checked for per-record failure/skips. Successful
  writes remain reported successful when only the subsequent refresh fails.

## Storage and logging

Home Assistant stores API keys in config-entry storage; this integration does not
encrypt those files. Secure `/config`, backups and administrator accounts. No key
is stored in automation YAML. The integration never logs keys, raw API payloads,
server error bodies or personal values. Responses to actions contain only save/
refresh status. HA Recorder and automation traces may store sensor states/action
inputs; control their retention and access separately.

**Upstream limitation observed:** SparkyFitness 1.11.0 logs incoming check-in
measurements in `measurementRepository.ts` and food-entry payloads in
`foodEntryService.ts`. This integration cannot suppress server-side logs. Secure
SparkyFitness logs/backups and review its logging configuration; do not share them
unredacted. No upstream production code was changed during this review.

## Remaining risks and constraints

- The integration trusts the configured server and its authorization enforcement.
  A compromised server/key or HA administrator is outside the client boundary.
- Food, exercise and All/Unlimited custom entries can duplicate on an intentional
  repeated action. The server does not expose a uniform idempotency contract for
  these dedicated routes. Water uses namespaced stable record IDs.
- Body writes can replace same-day imported values for explicitly supplied fields.
  Later Garmin syncs may overwrite them again. Writes are never automatic by default.
- Arbitrary custom category labels/units are server-controlled; only stored/displayed
  through HA entity APIs, never executed or used to construct endpoint paths.
- APIs and response shapes are verified against pinned SparkyFitness 1.11.0 source.
  Live write/TLS/Reverse-Proxy tests and other server versions remain unverified.
- The integration has no third-party runtime requirements beyond Home Assistant's
  aiohttp/voluptuous. Development dependencies and CI actions require normal
  maintenance; automated dependency update PRs are configured.

## Reporting

For a suspected vulnerability do not post credentials, personal data or a working
exploit publicly. Use GitHub's private vulnerability reporting if enabled for the
repository, or contact the repository owner privately first. Public distribution was explicitly requested by the repository owner.
Before publication, the complete local Git history is checked for secrets;
this does not replace careful review of future contributions.
