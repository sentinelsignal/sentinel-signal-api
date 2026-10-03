"""Every published operation is covered by the mock server, both SDKs and Postman."""

from __future__ import annotations

import json
import re
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "mock-server"), str(REPO / "sdk" / "python"), str(REPO / "tools")]

import generate_postman  # noqa: E402
from main import app  # noqa: E402
from sentinel_signal import SentinelSignalClient  # noqa: E402
from spec import example, load_spec, operations, request_schema, success_schema  # noqa: E402

SPEC = load_spec()
OPERATIONS = operations(SPEC)
AUTH = {"Authorization": "Bearer test-key"}


def _camel(name: str) -> str:
    head, *rest = name.split("_")
    return head + "".join(part.title() for part in rest)


def _concrete(path: str) -> str:
    return path.replace("{workflow}", "healthcare.denial")


def _validates(schema: dict, value: object) -> list[str]:
    validator = Draft202012Validator({**schema, "components": SPEC["components"]})
    return [error.message for error in validator.iter_errors(value)]


def test_spec_operation_ids_are_unique_and_present() -> None:
    ids = [operation.get("operationId") for _, _, operation in OPERATIONS]
    assert all(ids) and len(ids) == len(set(ids))


@pytest.mark.parametrize("path,method,operation", OPERATIONS, ids=[op["operationId"] for _, _, op in OPERATIONS])
def test_mock_serves_operation_with_schema_valid_response(path: str, method: str, operation: dict) -> None:
    client = TestClient(app)
    schema = request_schema(operation)
    body = example(schema) if schema else None
    response = client.request(method.upper(), _concrete(path), json=body, headers=AUTH)
    assert response.status_code == 200, response.text
    assert _validates(success_schema(operation), response.json()) == []
    assert client.request(method.upper(), _concrete(path), json=body).status_code == 401


def test_mock_rejects_invalid_bodies_and_unknown_workflows() -> None:
    client = TestClient(app)
    assert client.post("/v1/score", json={"payload": {}}, headers=AUTH).status_code == 422
    assert client.get("/v1/workflows/not.a.workflow/schema", headers=AUTH).status_code == 422


def test_mock_scores_deterministically_per_payload() -> None:
    client = TestClient(app)
    body = example(request_schema(SPEC["paths"]["/v1/score"]["post"]))
    first = client.post("/v1/score", json=body, headers=AUTH).json()
    again = client.post("/v1/score", json=body, headers=AUTH).json()
    other = client.post("/v1/score", json={**body, "payload": {**body["payload"], "units": 7}}, headers=AUTH).json()
    assert first["score"] == again["score"] != other["score"]


@pytest.mark.parametrize("operation_id", [op["operationId"] for _, _, op in OPERATIONS])
def test_python_and_js_sdks_expose_every_operation(operation_id: str) -> None:
    assert callable(getattr(SentinelSignalClient, operation_id, None)), f"Python SDK missing {operation_id}"
    js = (REPO / "sdk" / "js" / "client.js").read_text(encoding="utf-8")
    assert re.search(rf"^\s*async {_camel(operation_id)}\(", js, re.MULTILINE), f"JS SDK missing {_camel(operation_id)}"


@pytest.fixture(scope="module")
def mock_url():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


def test_python_sdk_round_trips_every_operation_against_the_mock(mock_url: str) -> None:
    client = SentinelSignalClient(api_key="test-key", base_url=mock_url)
    score_body = example(request_schema(SPEC["paths"]["/v1/score"]["post"]))
    feedback = example(request_schema(SPEC["paths"]["/v1/feedback"]["post"]))
    assert client.score(score_body["workflow"], score_body["payload"], score_body.get("options"))["score"] >= 0
    assert client.score_batch([score_body], continue_on_error=True)
    assert client.list_workflows() == client.workflows()
    assert client.get_workflow_schema("healthcare.denial")
    assert client.validate_workflow_payload("healthcare.denial", score_body["payload"])
    assert client.get_limits() == client.limits()
    assert client.get_usage(month="2026-01") and client.usage()
    assert client.submit_feedback(feedback)


def test_js_sdk_round_trips_against_the_mock(mock_url: str) -> None:
    node = subprocess.run(["node", "--version"], capture_output=True, text=True)
    if node.returncode != 0:
        pytest.skip("node not installed")
    script = f"""
      import {{ SentinelSignalClient }} from "{(REPO / 'sdk' / 'js' / 'client.js').as_uri()}";
      const c = new SentinelSignalClient({{ apiKey: "test-key", baseUrl: "{mock_url}" }});
      const wf = await c.listWorkflows();
      const schema = await c.getWorkflowSchema({{ workflow: "healthcare.denial" }});
      const usage = await c.getUsage({{ month: "2026-01" }});
      const limits = await c.getLimits();
      if (!wf || !schema || !usage || !limits) throw new Error("empty response");
      console.log("ok");
    """
    result = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0 and result.stdout.strip() == "ok", result.stderr


def test_postman_collection_is_generated_from_the_spec() -> None:
    committed = json.loads((REPO / "examples" / "postman_collection.json").read_text(encoding="utf-8"))
    assert committed == generate_postman.build()
    assert len(committed["item"]) == len(OPERATIONS)
