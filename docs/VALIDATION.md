# Validation report — 0.2.0

2026-11-05: **80 passed**, 0 failed/skipped, 89% statement coverage
(538 integration statements). Ruff lint/format, compile checks, package integrity
and Bandit 1.8.6 static security scan passed (no findings).

New coverage: opt-in writes, admin restriction, foreign account/category rejection,
value/date validation, HTTP POST round trips, redirect/key isolation, no retry on
uncertain writes, response confirmation, successful-save/failed-refresh distinction,
key reconfiguration, official logo hashes and deterministic install ZIP contents.
All requests use synthetic data. No live writes or production modifications.

## Public validation — 2026-11-06

Repository visibility is public. PR #1 has been merged with explicit owner
approval. GitHub recognizes the MIT code license; separate notices retain the
non-commercial upstream artwork terms.

[Validate 42179011923](https://github.com/Lupusred/ha-sparkyfitness/actions/runs/42179011923)
passed all tests, Ruff, Bandit, packaging, Hassfest and the public HACS validator
on release commit `3f0a1a021d7c64f39295b05800c133eff060ca67`.
The isolated three distribution tests also pass after adding the MIT code license
and artwork-scope notice to the installed integration folder.

[Release v0.2.0](https://github.com/Lupusred/ha-sparkyfitness/releases/tag/v0.2.0)
is public. [Release workflow 42179203911](https://github.com/Lupusred/ha-sparkyfitness/actions/runs/42179203911)
successfully built and uploaded sparkyfitness.zip from the tag. Its public download
was verified byte-for-byte against the local package: 214426 bytes, 19 files,
SHA-256 `84789ff4d1cf7491eec2f1890d16734abb86a1761b77913dca8d0d8f3f20f66a`.
ZIP integrity, manifest version and the tag's commit were checked.

Remaining checks: installation through HACS in the user's own deployment and
live opt-in writes. The earlier manual installation/read operation was confirmed
by the user. No production systems were changed during publication. This release
is available as a HACS custom repository; no default-catalogue submission was made.

The following sections record earlier validation states, not current release
availability. Current delivery status is recorded in PROGRESS.md.

## Historical 0.1.0 baseline

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
Implementation and documentation are committed in the development history.
See PROGRESS.md and the GitHub development branch for subsequent delivery status.
The cloud environment draft now contains reproducible install/start instructions;
publishing that environment remains a separate user action.

## Historical public-release preparation

All eight commits through b8103af were scanned with checksum-verified Gitleaks
8.24.3: no leaks found. The 80 tests, Ruff and Bandit passed again; 39 internal
documentation links were checked. Public HACS validation is still pending because
GitHub denied changing visibility through the connected integration. PR #1 and
release draft 435813141 are prepared; publication is not claimed.
