"""Helpers that read openapi/openapi.json and build deterministic examples from it.

Shared by the mock server and tools/generate_postman.py so neither carries its
own copy of the API surface.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

SPEC_PATH = Path(__file__).resolve().parents[1] / "openapi" / "openapi.json"
HTTP_METHODS = ("get", "post", "put", "patch", "delete")
MAX_DEPTH = 8


@lru_cache(maxsize=1)
def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def operations(spec: dict[str, Any] | None = None) -> list[tuple[str, str, dict[str, Any]]]:
    spec = spec or load_spec()
    return [
        (path, method, operation)
        for path, methods in sorted(spec["paths"].items())
        for method, operation in methods.items()
        if method in HTTP_METHODS
    ]


def resolve(schema: dict[str, Any], spec: dict[str, Any] | None = None) -> dict[str, Any]:
    spec = spec or load_spec()
    while "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        schema = spec["components"]["schemas"][name]
    return schema


def request_schema(operation: dict[str, Any]) -> dict[str, Any] | None:
    return operation.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")


def success_schema(operation: dict[str, Any]) -> dict[str, Any] | None:
    for status in ("200", "201"):
        response = operation.get("responses", {}).get(status)
        if response:
            return response.get("content", {}).get("application/json", {}).get("schema")
    return None


def example(schema: dict[str, Any] | None, spec: dict[str, Any] | None = None, depth: int = 0) -> Any:
    """A deterministic value that validates against `schema`, preferring authored examples."""
    if schema is None:
        return None
    spec = spec or load_spec()
    schema = resolve(schema, spec)
    for key in ("example", "const"):
        if key in schema:
            return schema[key]
    if schema.get("examples"):
        return schema["examples"][0]
    if schema.get("default") is not None:
        return schema["default"]
    if schema.get("enum"):
        return schema["enum"][0]
    for key in ("anyOf", "oneOf"):
        if key in schema:
            options = [option for option in schema[key] if resolve(option, spec).get("type") != "null"]
            return example((options or schema[key])[0], spec, depth)
    if "allOf" in schema:
        merged: dict[str, Any] = {}
        for part in schema["allOf"]:
            value = example(part, spec, depth)
            if isinstance(value, dict):
                merged.update(value)
        return merged
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = next((item for item in kind if item != "null"), "null")
    if kind == "object" or "properties" in schema:
        if depth >= MAX_DEPTH:
            return {}
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        return {
            name: example(sub, spec, depth + 1)
            for name, sub in properties.items()
            if name in required or depth < 2
        }
    if kind == "array":
        if depth >= MAX_DEPTH:
            return []
        count = max(1, schema.get("minItems", 1))
        return [example(schema.get("items", {}), spec, depth + 1) for _ in range(count)]
    if kind == "string":
        formats = {
            "date-time": "2026-01-01T00:00:00Z",
            "date": "2026-01-01",
            "uri": "https://api.sentinelsignal.io",
            "email": "dev@example.com",
            "uuid": "00000000-0000-4000-8000-000000000000",
        }
        value = formats.get(schema.get("format", ""), "string")
        return value.ljust(schema.get("minLength", 0), "x")[: schema.get("maxLength", len(value)) or None]
    if kind == "integer":
        return int(schema.get("minimum", 0))
    if kind == "number":
        return float(schema.get("minimum", 0.0))
    if kind == "boolean":
        return True
    return None
