// Minimal JavaScript client example for Sentinel Signal unified scoring endpoint.

const BASE_URL = process.env.SENTINEL_BASE_URL || "https://api.sentinelsignal.io";
const API_KEY = process.env.SENTINEL_API_KEY || "YOUR_API_KEY";

const body = {
  workflow: "healthcare.denial",
  payload: {
    external_claim_id: "DEMO-1001",
    service_date: "2026-02-15",
    provider_id: 1021,
    payer_id: 44,
    cpt_code: "99213",
    icd10_code: "E119",
    units: 1,
    billed_amount: 250.0,
    place_of_service: "11",
    network_status: "in_network"
  },
  options: {
    operating_point: "high_recall",
    allow_fallback: true
  }
};

fetch(`${BASE_URL}/v1/score`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${API_KEY}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify(body)
})
  .then(async (res) => {
    const text = await res.text();
    console.log("status:", res.status);
    console.log(text);
  })
  .catch((err) => {
    console.error("request failed:", err);
  });
