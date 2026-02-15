# Mock Server

Lightweight mock API for integration testing without production credentials.

## Run

```bash
cd mock-server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8010
```

Then call:

- `POST http://localhost:8010/v1/score`
- `GET http://localhost:8010/v1/workflows`
- `GET http://localhost:8010/v1/limits`
- `GET http://localhost:8010/v1/usage`
