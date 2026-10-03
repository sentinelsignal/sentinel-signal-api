"""Mock Sentinel Signal API generated from openapi/openapi.json.

Every operation in the spec is served: requests are checked for a Bearer key
and validated against the spec's request schema (422 on mismatch), and responses
are deterministic examples of the spec's success schema. Scores are derived
from a hash of the request, so the same payload always scores the same.
Nothing here is hand-maintained per endpoint, so the mock cannot drift from
the published contract.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jsonschema import Draft202012Validator

from spec import example, load_spec, operations, request_schema, success_schema

SPEC = load_spec()
app = FastAPI(title="Sentinel Signal Mock API", version=SPEC["info"]["version"], docs_url="/docs")
app.openapi = lambda: SPEC  # serve the published contract, not FastAPI's view of these generic routes


def _validator(schema: dict[str, Any]) -> Draft202012Validator:
    return Draft202012Validator({**schema, "components": SPEC["components"]})


def _validation_error(errors: list[Any]) -> JSONResponse:
    detail = [
        {"loc": ["body", *[str(part) for part in error.absolute_path]], "msg": error.message, "type": "value_error"}
        for error in errors
    ]
    return JSONResponse(status_code=422, content={"detail": detail})


def _score(seed: Any) -> float:
    blob = json.dumps(seed, sort_keys=True, separators=(",", ":"), default=str)
    return round(int(hashlib.sha256(blob.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF, 6)


def _risk(score: float) -> str:
    return "high" if score >= 0.67 else "moderate" if score >= 0.34 else "low"


def _personalize(value: Any, seed: Any) -> Any:
    """Make scored responses depend on the request instead of a fixed example."""
    if isinstance(value, list):
        return [_personalize(item, [seed, index]) for index, item in enumerate(value)]
    if not isinstance(value, dict):
        return value
    value = {key: _personalize(item, seed) for key, item in value.items()}
    if isinstance(value.get("score"), (int, float)):
        value["score"] = _score(seed)
        if value.get("risk_level") in {"low", "moderate", "high"}:
            value["risk_level"] = _risk(value["score"])
    if isinstance(seed, dict) and isinstance(seed.get("workflow"), str) and "workflow" in value:
        value["workflow"] = seed["workflow"]
    for key in ("scored_at", "generated_at", "received_at"):
        if key in value:
            value[key] = datetime.now(timezone.utc).isoformat()
    return value


def _handler(path: str, method: str, operation: dict[str, Any]):
    body_schema = request_schema(operation)
    body_validator = _validator(body_schema) if body_schema else None
    path_validators = {
        parameter["name"]: _validator(parameter.get("schema", {}))
        for parameter in operation.get("parameters", [])
        if parameter.get("in") == "path"
    }
    response_template = example(success_schema(operation))

    async def handle(request: Request) -> JSONResponse:
        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer ") or not authorization[7:].strip():
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid API key"})
        for name, validator in path_validators.items():
            errors = list(validator.iter_errors(request.path_params.get(name)))
            if errors:
                return JSONResponse(
                    status_code=422,
                    content={"detail": [{"loc": ["path", name], "msg": errors[0].message, "type": "value_error"}]},
                )
        body: Any = None
        if body_validator is not None:
            try:
                body = await request.json()
            except ValueError:
                return JSONResponse(
                    status_code=422, content={"detail": [{"loc": ["body"], "msg": "invalid JSON", "type": "value_error"}]}
                )
            errors = sorted(body_validator.iter_errors(body), key=lambda error: list(error.absolute_path))
            if errors:
                return _validation_error(errors)
        seed = body if body is not None else {"path": request.url.path, **request.path_params}
        return JSONResponse(content=_personalize(response_template, seed))

    handle.__name__ = operation.get("operationId", f"{method}_{path}")
    return handle


@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok"}


for _path, _method, _operation in operations(SPEC):
    app.add_api_route(_path, _handler(_path, _method, _operation), methods=[_method.upper()])
