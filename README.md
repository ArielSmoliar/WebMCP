# Captain's Table

Captain's Table is a WebMCP reference application where a human and ChatGPT's
browser agent operate one live decision surface together. The agent can inspect,
diagnose, compare, select, and execute structured actions. Only the human can
authorize the exact plan.

The product demonstrates six state-aware imperative WebMCP tools, dynamic tool
registration, exact-plan human authorization, stale-state invalidation, durable
persistence, and idempotent receipt recovery. The page remains fully usable when
WebMCP is unavailable.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. In a WebMCP-enabled ChatGPT browser, ask:

> Find the most important conflict in this offsite plan, compare repairs, and
> select the arrival-safe option.

Authorization is intentionally a page-only human action. After authorizing, ask
ChatGPT to create the reservation.

## Test

```bash
.venv/bin/python -m pytest -q
```

See [the engineering plan](docs/engineering-plan.md), [interaction design](docs/interaction-design.md),
[Google Cloud deployment guide](docs/deploy-google-cloud.md), and
[protocol observations](docs/protocol-observations.md).

## Technology

- OpenAI ChatGPT as the external browser agent
- WebMCP imperative API through `document.modelContext`
- FastAPI, Pydantic, Firestore in production, SQLite locally, and plain semantic HTML/CSS/JavaScript
- Google Cloud Run with a least-privilege service identity

No embedded agent or second model is used. The OpenAI Agents SDK is deliberately
absent because ChatGPT already owns agent planning and WebMCP invocation.
