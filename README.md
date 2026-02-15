# sentinel-signal-api

Public API package for Sentinel Signal Systems.

This repository exposes only public integration assets:
- API surface overview
- OpenAPI specification
- Python and JavaScript client examples
- Governance summary
- High-level billing flow

## API Surface

Primary endpoint:
- `POST /v1/score`

Supporting endpoints:
- `GET /v1/workflows`
- `GET /v1/limits`
- `GET /v1/usage`

Legacy workflow-specific endpoints remain available for backward compatibility and are documented in the OpenAPI spec.

## OpenAPI Spec

- `openapi/openapi.json`

## Examples

- `examples/python_client.py`
- `examples/js_client.js`

## Public Docs

- `docs/governance.md`
- `docs/billing.md`
- `docs/integration.md`

## Notes

This repo intentionally excludes private implementation details, internal model artifacts, deployment internals, and non-public operational code.
