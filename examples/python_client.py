#!/usr/bin/env python3
"""Minimal Python client example for Sentinel Signal unified scoring endpoint."""

from __future__ import annotations

import os

import requests

BASE_URL = os.getenv("SENTINEL_BASE_URL", "https://api.sentinelsignal.io")
API_KEY = os.getenv("SENTINEL_API_KEY", "YOUR_API_KEY")

payload = {
    "workflow": "healthcare.denial",
    "payload": {
        "external_claim_id": "DEMO-1001",
        "service_date": "2026-02-15",
        "provider_id": 1021,
        "payer_id": 44,
        "cpt_code": "99213",
        "icd10_code": "E119",
        "units": 1,
        "billed_amount": 250.0,
        "place_of_service": "11",
        "network_status": "in_network",
    },
    "options": {
        "operating_point": "high_recall",
        "allow_fallback": True,
    },
}

response = requests.post(
    f"{BASE_URL}/v1/score",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json=payload,
    timeout=20,
)

print("status:", response.status_code)
print(response.text)
