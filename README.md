# SparkyFitness for Home Assistant

Read-only, asynchronous Home Assistant custom integration for a self-hosted
[SparkyFitness](https://github.com/CodeWithCJ/SparkyFitness) server.

**Version 0.1.0 — initial release candidate.** Developed against the v1.11.0 API;
synthetic tests use Home Assistant 2026.2.3 / Python 3.13. No production-instance
or real Garmin-data validation has been performed. Older SparkyFitness releases
may expose fewer endpoints. This repository is installable as a HACS custom
repository; it is not included in the default HACS catalogue.

## Features

- UI configuration with server URL and API key; verifies the authenticated user.
- Independent integration entries for independent server accounts.
- Default 15-minute polling, configurable from 5 to 1440 minutes.
- Nutrition, targets, body measurements, steps, workouts and sleep.
- Automatic discovery of custom categories, including imported Garmin metrics.
- German and English UI; configurable IANA calendar time zone.
- Expired-key reauthentication, timeout handling and HTTP 429 backoff.
- GET requests only. TLS verification enabled; local HTTP supported.

See [sensor/API documentation](docs/API.md),
[Unraid installation](docs/UNRAID.md), and [validation](docs/VALIDATION.md).

## Installation

In HACS, add `https://github.com/Lupusred/ha-sparkyfitness` as a custom repository
of category **Integration**, then download SparkyFitness and restart Home
Assistant. The repository must be accessible to your HACS GitHub account; private
repositories require access through HACS-supported authentication. Otherwise use
the manual installation below. No public listing or release is created by this
implementation.

Alternatively, copy `custom_components/sparkyfitness` into your existing Home
Assistant `/config/custom_components/` directory and restart Home Assistant.
Do not copy the entire repository into `custom_components`.

In **Settings → Devices & services → Add integration → SparkyFitness**, enter the
SparkyFitness web server URL (for example `http://192.168.1.20:8080`) and a dedicated
read-only API key. A reverse-proxy path prefix is supported. The optional trailing
`/api` is normalized away. Set the time zone in integration options to match the
SparkyFitness profile; initially the Home Assistant time zone is used.

## Development

Current status, open work and continuation instructions: [PROGRESS.md](PROGRESS.md).
Development takes place on `develop/sparkyfitness`; see [AGENTS.md](AGENTS.md)
for the commit, test and push workflow.

```sh
uv python install 3.13
uv venv --python 3.13 --managed-python .venv
uv pip install --python .venv/bin/python -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/ruff check custom_components tests
.venv/bin/ruff format --check custom_components tests
```

Tests never need real credentials. They use Home Assistant's custom-component
test plugin and synthetic HTTP responses. `api.py` owns HTTP/authentication,
`data.py` transforms responses, `coordinator.py` owns scheduling and calendar dates,
and `sensor.py` registers entities. Future write support should use a separate,
explicitly enabled service layer; this version exposes no write services.

## Privacy

The integration contacts only the configured server. It never calls Garmin,
analytics services or other external data providers. Redirects are rejected to
prevent forwarding API keys. Keys are entered using a password selector and
stored by Home Assistant in its config-entry storage (not encrypted by this
integration). Protect `/config`, its backups and Home Assistant access. Health
sensor states may be retained by Home Assistant Recorder; configure Recorder
exclusions if you do not want that history. No raw payloads, key values, names,
emails or server error bodies are logged by this integration.

## Maintenance

Re-run the tests before upgrading the pinned Home Assistant test package. Verify
endpoint/response changes against the server source and add synthetic regression
fixtures. Use semantic release tags and update `manifest.json` for HACS updates.
Do not publish real fitness-data fixtures or credentials.
