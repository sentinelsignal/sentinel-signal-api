# sentinel-signal-api

Public API package for Sentinel Signal Systems.

This repository exposes only public integration assets:
- API surface overview
- OpenAPI specification
- Client examples and minimal SDK wrappers
- Governance summary
- High-level billing flow
- Mock server for integration testing

## API Surface

Scoring:
- `POST /v1/score`
- `POST /v1/score/batch`
- `POST /v1/workflows/{workflow}/validate` (validate a payload without scoring)

Discovery and account:
- `GET /v1/workflows`
- `GET /v1/workflows/{workflow}/schema`
- `GET /v1/limits`
- `GET /v1/usage`

Outcome feedback:
- `POST /v1/feedback`

## OpenAPI Spec

- `openapi/openapi.json`

The spec is generated from the production API contract and must not be edited by hand. The SDKs, mock server and Postman collection are tested against it in CI (`tests/test_contract.py`), so a change to the contract fails CI until they cover it.

## Examples

- `examples/python_client.py`
- `examples/js_client.js`
- `examples/postman_collection.json` (generated: `python tools/generate_postman.py`)

## Minimal SDKs

- `sdk/python/`
- `sdk/js/`

## Mock Server

Use the mock server to integrate without production credentials or model internals:

```bash
cd mock-server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8010
```

The mock serves every operation in `openapi/openapi.json` at `http://localhost:8010`. It requires a Bearer key (any value), validates request bodies against the spec (422 on mismatch) and returns schema-valid responses with deterministic scores derived from the payload.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q tests
```

## Public Docs

- `docs/governance.md`
- `docs/billing.md`
- `docs/integration.md`

## License and Security

MIT licensed (see `LICENSE`). Report vulnerabilities as described in `SECURITY.md`.

## Secrets Policy

This public repository never contains live billing credentials or active Stripe identifiers.
Use placeholders only, for example:
- `STRIPE_PRODUCT_ID=prod_xxx`
- `STRIPE_PRICE_ID=price_live_xxx`
- `STRIPE_WEBHOOK_SECRET=whsec_xxx`
- `STRIPE_PUBLISHABLE_KEY=pk_live_xxx`

## Notes

This repo intentionally excludes private implementation details, internal model artifacts, internal DB schema names, and deployment internals.
