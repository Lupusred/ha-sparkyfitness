# Validation report

2026-11-05, Python 3.13.16, Home Assistant 2026.2.3,
pytest-homeassistant-custom-component 0.13.316.

Executed final checks:

- `python -m pytest -q --timeout=30 --cov=custom_components.sparkyfitness --cov-report=term-missing`:
  **42 passed**, 0 failed, 0 skipped, 91% statement coverage (363 statements).
- `ruff check custom_components tests`: passed.
- `ruff format --check custom_components tests`: 11 files already formatted.
- `python -m compileall -q custom_components`: passed.
- `git diff --check`: passed.
- JSON parse, English/German sensor-translation key parity, single-integration
  HACS layout and brand icon dimensions: passed.

Coverage includes valid/invalid authentication, optional missing endpoints,
server/network/JSON errors, redirect rejection, rate-limit cooldown, credential-free
error messages, account identity mismatch, numerical validation, macro scaling,
goals and units, missing data, custom numeric/text categories, latest samples,
category discovery and rename stability, two real HA config entries and entity
registries, reconnect, session cleanup, configuration/options/reauthentication,
DST/calendar boundaries, timed coordinator polling and midnight failure handling.
A local aiohttp server verifies real GET requests with synthetic responses; no
production server is involved. Energy and volume sensors intentionally omit state
classes to avoid invalid statistics semantics; other numeric sensors use measurement.

The first test run found two fixture assumptions about current HA config-entry
APIs; they were corrected. HA warnings exposed improper session closure and
energy/volume state classes; implementation was corrected and all checks rerun.
The initial system Python lacked C extension headers; a managed Python 3.13
installation fixed dependency installation. Sandbox execution stalled HA's async
fixture initialization; final tests ran through the approved execution route,
without removing tests or assertions.

Not executed: HACS installation in a user's HA instance, GitHub Actions HACS and
hassfest jobs, testing on other HA/SparkyFitness versions, actual Garmin payloads,
real TLS/reverse-proxy deployments, and fresh cloud-task snapshot restoration.
The official HACS structure/manifest/brand requirements were checked from source;
a full passing HACS/hassfest validator run is not claimed. No public release or
HACS default-catalogue submission has been made.

The integration is a tested initial release candidate, not a guarantee of
production compatibility. Live test instructions and minimum requested deployment
information are in UNRAID.md. Never commit API keys or real health-data fixtures.

GitHub repository metadata confirms `Lupusred/ha-sparkyfitness` is private.
Implementation and documentation are committed locally; no remote push was made.
The cloud environment draft now contains reproducible install/start instructions;
publishing that environment remains a separate user action.
