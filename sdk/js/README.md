# JavaScript SDK (Minimal)

```javascript
import { SentinelSignalClient } from "./client.js";

const client = new SentinelSignalClient({ apiKey: "YOUR_API_KEY" });

const response = await client.score({
  workflow: "healthcare.denial",
  payload: {
    payer: "PAYER_X",
    cpt: "99213",
    icd10: ["E11.9"],
    billed_amount: 250.0,
    place_of_service: "11",
    in_network: true
  },
  options: { operating_point: "high_recall" }
});

console.log(response);
```
