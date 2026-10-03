# Changelog

## 1.2.0 - 2026-10-03

Brings the public package back in line with production:
- `openapi/openapi.json` is now generated from the production contract (8 public operations, up from 4): adds `POST /v1/score/batch`, `GET /v1/workflows/{workflow}/schema`, `POST /v1/workflows/{workflow}/validate` and `POST /v1/feedback`, with the production request/response schemas
- Python and JS SDKs cover every operation (`score_batch`, `get_workflow_schema`, `validate_workflow_payload`, `submit_feedback`, ...); the old `workflows()`, `limits()` and `usage()` names still work
- Mock server is generated from the spec: validates requests and returns schema-valid responses for every operation
- Postman collection is generated from the spec
- CI: contract tests, OpenAPI validation and secret scanning
- Added MIT `LICENSE` and `SECURITY.md`

## 1.1.0 - 2026-02-15

Public-distribution hardening release:
- Replaced OpenAPI spec with public-only endpoint surface and generic schemas
- Removed internal readiness/artifact metadata exposure from public spec
- Added mock server for integration without production credentials
- Added Postman collection for import-based API testing
- Added minimal Python and JavaScript SDK wrappers
- Added explicit Stripe placeholder policy (no live identifiers in public assets)

## 1.0.0 - 2026-02-15

Initial public package release with:
- OpenAPI spec export
- Unified endpoint integration examples (Python + JavaScript)
- Governance summary
- High-level billing flow documentation
- Integration guide
