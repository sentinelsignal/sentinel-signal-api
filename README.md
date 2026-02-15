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

Primary endpoint:
- `POST /v1/score`

Metadata endpoints:
- `GET /v1/workflows`
- `GET /v1/limits`
- `GET /v1/usage`

## OpenAPI Spec

- `openapi/openapi.json`

## Examples

- `examples/python_client.py`
- `examples/js_client.js`
- `examples/postman_collection.json`

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

Mock endpoints:
- `POST http://localhost:8010/v1/score`
- `GET http://localhost:8010/v1/workflows`
- `GET http://localhost:8010/v1/limits`
- `GET http://localhost:8010/v1/usage`

## Public Docs

- `docs/governance.md`
- `docs/billing.md`
- `docs/integration.md`

## Security and Secrets Policy

This public repository never contains live billing credentials or active Stripe identifiers.
Use placeholders only, for example:
- `STRIPE_PRODUCT_ID=prod_xxx`
- `STRIPE_PRICE_ID=price_live_xxx`
- `STRIPE_WEBHOOK_SECRET=whsec_xxx`
- `STRIPE_PUBLISHABLE_KEY=pk_live_xxx`

## Notes

This repo intentionally excludes private implementation details, internal model artifacts, internal DB schema names, and deployment internals.
