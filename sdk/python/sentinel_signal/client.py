from __future__ import annotations

from typing import Any

import requests


class SentinelSignalClient:
    def __init__(self, api_key: str, base_url: str = "https://api.sentinelsignal.io", timeout_seconds: float = 20.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def score(self, workflow: str, payload: dict[str, Any], options: dict[str, Any] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"workflow": workflow, "payload": payload}
        if options is not None:
            body["options"] = options
        response = requests.post(
            f"{self.base_url}/v1/score",
            headers=self._headers(),
            json=body,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def workflows(self) -> dict[str, Any]:
        response = requests.get(f"{self.base_url}/v1/workflows", headers=self._headers(), timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.json()

    def limits(self) -> dict[str, Any]:
        response = requests.get(f"{self.base_url}/v1/limits", headers=self._headers(), timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.json()

    def usage(self) -> dict[str, Any]:
        response = requests.get(f"{self.base_url}/v1/usage", headers=self._headers(), timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.json()
