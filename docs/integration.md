# Integration Guide

## 1. Read the Spec

Use `openapi/openapi.json` to generate or validate clients.

## 2. Authenticate

Send bearer token credentials with each API request:

```http
Authorization: Bearer YOUR_API_KEY
```

## 3. Score via Unified Endpoint

Use the primary endpoint:

- `POST /v1/score`

Request shape:
- `workflow`: workflow identifier, e.g. `healthcare.denial`
- `payload`: workflow-specific payload object
- `options` (optional): operating point, version pinning, fallback behavior

## 4. Handle Response

Use normalized fields for orchestration:
- `score`
- `risk_level`
- `confidence`
- `model_version`
- `explanation.top_factors`

Use `details` for workflow-specific output.

## 5. Discover Workflows and Validate Payloads

- `GET /v1/workflows`: supported workflows
- `GET /v1/workflows/{workflow}/schema`: the payload schema for one workflow
- `POST /v1/workflows/{workflow}/validate`: check a payload without scoring it
- `GET /v1/limits` and `GET /v1/usage`: plan limits and usage for your key

## 6. Score in Batches

`POST /v1/score/batch` takes `items` (each a `workflow` and `payload`, with optional `options` and `item_id`). Set `continue_on_error` to get per-item errors instead of failing the whole batch.

## 7. Report Outcomes

`POST /v1/feedback` records the observed outcome for an earlier score. Pass the `request_id` from the scoring response. Do not include PHI or direct identifiers in `notes`.

## 8. Error Handling

Handle standard status classes:
- `4xx` for request/auth/rate issues
- `5xx` for transient server failures

Recommended client behavior:
- validate payloads before send
- retry transient failures with backoff
- treat non-retriable `4xx` as hard failures

## 9. Local Integration Without Production Credentials

Use the included mock server (`mock-server/`) for schema-compatible development:
- deterministic fake scoring outputs
- same endpoint surface as public v1
- no internal model logic exposure

## 8. Optional Accelerators

- Postman collection: `examples/postman_collection.json`
- Minimal SDK wrappers:
  - Python: `sdk/python/`
  - JavaScript: `sdk/js/`
