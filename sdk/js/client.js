// Thin wrapper over the public API. One method per operationId in openapi/openapi.json
// (camelCased: score_batch -> scoreBatch).
export class SentinelSignalClient {
  constructor({ apiKey, baseUrl = "https://api.sentinelsignal.io" }) {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  _headers() {
    return {
      Authorization: `Bearer ${this.apiKey}`,
      "Content-Type": "application/json"
    };
  }

  async _request(method, path, { body, query } = {}) {
    const url = new URL(`${this.baseUrl}${path}`);
    for (const [key, value] of Object.entries(query || {})) {
      if (value !== undefined && value !== null) url.searchParams.set(key, value);
    }
    const res = await fetch(url, {
      method,
      headers: this._headers(),
      body: body === undefined ? undefined : JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`${method} ${path} failed: ${res.status}`);
    return res.json();
  }

  // POST /v1/score
  async score({ workflow, payload, options }) {
    return this._request("POST", "/v1/score", { body: { workflow, payload, options } });
  }

  // POST /v1/score/batch
  async scoreBatch({ items, continueOnError }) {
    return this._request("POST", "/v1/score/batch", { body: { items, continue_on_error: continueOnError } });
  }

  // GET /v1/workflows
  async listWorkflows() {
    return this._request("GET", "/v1/workflows");
  }

  // GET /v1/workflows/{workflow}/schema
  async getWorkflowSchema({ workflow }) {
    return this._request("GET", `/v1/workflows/${encodeURIComponent(workflow)}/schema`);
  }

  // POST /v1/workflows/{workflow}/validate
  async validateWorkflowPayload({ workflow, payload }) {
    return this._request("POST", `/v1/workflows/${encodeURIComponent(workflow)}/validate`, { body: { payload } });
  }

  // GET /v1/limits
  async getLimits() {
    return this._request("GET", "/v1/limits");
  }

  // GET /v1/usage
  async getUsage({ month } = {}) {
    return this._request("GET", "/v1/usage", { query: { month } });
  }

  // POST /v1/feedback
  async submitFeedback(feedback) {
    return this._request("POST", "/v1/feedback", { body: feedback });
  }

  // Pre-1.2 names, kept so existing integrations keep working.
  async workflows() {
    return this.listWorkflows();
  }

  async limits() {
    return this.getLimits();
  }

  async usage() {
    return this.getUsage();
  }
}
