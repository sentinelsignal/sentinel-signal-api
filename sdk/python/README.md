# Python SDK (Minimal)

```python
from sentinel_signal import SentinelSignalClient

client = SentinelSignalClient(api_key="YOUR_API_KEY")
response = client.score(
    workflow="healthcare.denial",
    payload={
        "payer": "PAYER_X",
        "cpt": "99213",
        "icd10": ["E11.9"],
        "billed_amount": 250.0,
        "place_of_service": "11",
        "in_network": True,
    },
    options={"operating_point": "high_recall"},
)
print(response)
```
