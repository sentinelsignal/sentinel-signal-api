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

  async score({ workflow, payload, options }) {
    const res = await fetch(`${this.baseUrl}/v1/score`, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({ workflow, payload, options })
    });
    if (!res.ok) throw new Error(`Score request failed: ${res.status}`);
    return res.json();
  }

  async workflows() {
    const res = await fetch(`${this.baseUrl}/v1/workflows`, { headers: this._headers() });
    if (!res.ok) throw new Error(`Workflows request failed: ${res.status}`);
    return res.json();
  }

  async limits() {
    const res = await fetch(`${this.baseUrl}/v1/limits`, { headers: this._headers() });
    if (!res.ok) throw new Error(`Limits request failed: ${res.status}`);
    return res.json();
  }

  async usage() {
    const res = await fetch(`${this.baseUrl}/v1/usage`, { headers: this._headers() });
    if (!res.ok) throw new Error(`Usage request failed: ${res.status}`);
    return res.json();
  }
}
