from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests


class SentinelSignalClient:
    """Thin wrapper over the public API. One method per operationId in openapi/openapi.json."""

    def __init__(self, api_key: str, base_url: str = "https://api.sentinelsignal.io", timeout_seconds: float = 20.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, *, json: Any = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers=self._headers(),
            json=json,
            params={key: value for key, value in (params or {}).items() if value is not None} or None,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    # POST /v1/score
    def score(self, workflow: str, payload: dict[str, Any], options: dict[str, Any] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"workflow": workflow, "payload": payload}
        if options is not None:
            body["options"] = options
        return self._request("POST", "/v1/score", json=body)

    # POST /v1/score/batch
    def score_batch(self, items: list[dict[str, Any]], continue_on_error: bool | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"items": items}
        if continue_on_error is not None:
            body["continue_on_error"] = continue_on_error
        return self._request("POST", "/v1/score/batch", json=body)

    # GET /v1/workflows
    def list_workflows(self) -> dict[str, Any]:
        return self._request("GET", "/v1/workflows")

    # GET /v1/workflows/{workflow}/schema
    def get_workflow_schema(self, workflow: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/workflows/{quote(workflow, safe='')}/schema")

    # POST /v1/workflows/{workflow}/validate
    def validate_workflow_payload(self, workflow: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", f"/v1/workflows/{quote(workflow, safe='')}/validate", json={"payload": payload})

    # GET /v1/limits
    def get_limits(self) -> dict[str, Any]:
        return self._request("GET", "/v1/limits")

    # GET /v1/usage
    def get_usage(self, month: str | None = None) -> dict[str, Any]:
        return self._request("GET", "/v1/usage", params={"month": month})

    # POST /v1/feedback
    def submit_feedback(self, feedback: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/v1/feedback", json=feedback)

    # Pre-1.2 names, kept so existing integrations keep working.
    def workflows(self) -> dict[str, Any]:
        return self.list_workflows()

    def limits(self) -> dict[str, Any]:
        return self.get_limits()

    def usage(self) -> dict[str, Any]:
        return self.get_usage()
