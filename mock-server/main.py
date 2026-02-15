from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field


class RequestOptions(BaseModel):
    operating_point: str | None = Field(default="balanced")
    model_version: str | None = None
    allow_fallback: bool = True


class ScoreRequest(BaseModel):
    workflow: str
    payload: dict[str, Any]
    options: RequestOptions | None = None


app = FastAPI(title="Sentinel Signal Mock API", version="1.0.0")


def _deterministic_score(workflow: str, payload: dict[str, Any]) -> float:
    blob = json.dumps({"workflow": workflow, "payload": payload}, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    raw = int(digest[:8], 16) / 0xFFFFFFFF
    return round(raw, 6)


def _risk(score: float) -> str:
    if score >= 0.67:
        return "high"
    if score >= 0.34:
        return "moderate"
    return "low"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/score")
def score(request: ScoreRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"error": {"type": "authentication_error", "message": "Missing or invalid API key"}})

    score_value = _deterministic_score(request.workflow, request.payload)
    confidence = round(min(0.99, 0.55 + abs(score_value - 0.5) * 0.9), 6)

    return {
        "score": score_value,
        "risk_level": _risk(score_value),
        "confidence": confidence,
        "model_version": request.options.model_version if request.options and request.options.model_version else "mock-1.0.0",
        "explanation": {
            "top_factors": [
                f"Workflow: {request.workflow}",
                "Deterministic mock score from payload hash",
                f"Payload fields: {len(request.payload.keys())}",
            ]
        },
        "details": {
            "workflow": request.workflow,
            "operating_point": (request.options.operating_point if request.options else "balanced"),
            "is_mock": True,
        },
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/v1/workflows")
def workflows() -> dict[str, Any]:
    return {
        "workflows": [
            {"id": "healthcare.denial", "name": "Healthcare Denial Risk", "version": "v1", "status": "public"},
            {"id": "healthcare.prior_auth", "name": "Healthcare Prior Auth Risk", "version": "v1", "status": "public"},
            {"id": "healthcare.reimbursement", "name": "Healthcare Reimbursement Forecast", "version": "v1", "status": "public"},
            {"id": "healthcare.appeal", "name": "Healthcare Appeal Generator", "version": "v1", "status": "beta-enterprise"},
        ]
    }


@app.get("/v1/limits")
def limits() -> dict[str, Any]:
    return {
        "plan": "free",
        "requests_per_second": 5,
        "monthly_calls_included": 1000,
        "usage_price_per_call_usd": 0.003,
    }


@app.get("/v1/usage")
def usage() -> dict[str, Any]:
    return {
        "current_period": datetime.now(timezone.utc).strftime("%Y-%m"),
        "total_calls": 123,
        "billable_calls": 0,
        "remaining_free_calls": 877,
    }
