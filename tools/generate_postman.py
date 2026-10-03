#!/usr/bin/env python3
"""Generate examples/postman_collection.json from openapi/openapi.json.

    python tools/generate_postman.py          # write
    python tools/generate_postman.py --check  # fail if the committed collection is stale
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "mock-server"))

from spec import example, load_spec, operations, request_schema  # noqa: E402

OUTPUT = REPO / "examples" / "postman_collection.json"
EXAMPLE_PATH_VALUES = {"workflow": "healthcare.denial"}


def _url(path: str) -> str:
    return "{{baseUrl}}" + re.sub(r"\{(\w+)\}", lambda m: EXAMPLE_PATH_VALUES.get(m.group(1), m.group(1)), path)


def build() -> dict:
    spec = load_spec()
    items = []
    for path, method, operation in operations(spec):
        request: dict = {
            "method": method.upper(),
            "header": [{"key": "Authorization", "value": "Bearer {{apiKey}}"}],
            "url": _url(path),
        }
        schema = request_schema(operation)
        if schema is not None:
            request["header"].append({"key": "Content-Type", "value": "application/json"})
            request["body"] = {"mode": "raw", "raw": json.dumps(example(schema, spec), indent=2)}
        items.append({"name": operation.get("summary") or operation["operationId"], "request": request})
    return {
        "info": {
            "name": "Sentinel Signal Public API",
            "description": f"Generated from openapi/openapi.json (API {spec['info']['version']}).",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [
            {"key": "baseUrl", "value": "https://api.sentinelsignal.io"},
            {"key": "apiKey", "value": "YOUR_API_KEY"},
        ],
        "item": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2) + "\n"
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            sys.stderr.write("examples/postman_collection.json is stale; run python tools/generate_postman.py\n")
            return 1
        print("postman collection is fresh")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
