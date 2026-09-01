# Captain's Table

![Captain's Table WebMCP hero: a human-authorized planning instrument with revision-bound agent signals](docs/assets/captains-table-webmcp-hero-v2.png)

Captain's Table is a WebMCP reference application where a human and ChatGPT's
browser agent operate one live decision surface together. The agent can inspect,
diagnose, compare, select, and execute structured actions. Only the human can
authorize the exact plan.

**[Open the live Cloud Run demo](https://captains-table-webmcp-1017459622661.us-east1.run.app/)**

## Current progress

The complete workflow, safety model, telemetry, Firestore persistence, and
revision-bound capability lifecycle are implemented and deployed. Production
revision `captains-table-webmcp-00009-z6j` serves 100% of traffic.

Chrome 151 has also been verified at the page layer through the WebMCP Origin
Trial. A cache-busted production load reached **WebMCP connected**, accepted all
three initial tool registrations, and issued capability epoch
`R1 · 94CBFBDC` for:

- `inspect_decision`
- `diagnose_plan`
- `report_observed_capabilities`

The updated ChatGPT built-in browser completed the full R1 through R6 production
journey. It discovered every state-dependent tool set, invoked the mutating
workflow tools, preserved page-only human authorization, rejected a retained
stale handle, executed exactly once, and recovered receipt `CT-79ECA1` after
reload. The connected Chrome extension remains page-enablement-only in this
environment and is not presented as host-discovery evidence.

Implemented and demonstrated relevance are both assessed at 9.5/10.

## What it demonstrates

The product demonstrates six state-aware workflow tools, one diagnostic
capability reporting tool, dynamic registration, exact-plan human authorization,
stale-state invalidation, durable persistence, and idempotent receipt recovery.
The page remains fully usable when WebMCP is unavailable.

Every dynamic tool set is issued as a capability epoch bound to one workflow
revision and a deterministic fingerprint. A callback retained after the page
requests removal still carries its issuing revision, so the server rejects it
instead of silently applying it to newer state.

Its Protocol Lab records page-side registration acceptance, tool-set removal,
invocation latency, stale-state rejection, authorization probes, idempotent
replay, receipt recovery, and obsolete-callback containment. Agent discovery is
labeled separately because current WebMCP does not acknowledge to the page which
tools the agent can see. ChatGPT can call `report_observed_capabilities` to supply
that missing observation explicitly.

The six workflow tools appear as the plan advances:

1. `inspect_decision`
2. `diagnose_plan`
3. `compare_repairs`
4. `select_repair`
5. `prepare_authorization`
6. `execute_authorized_plan`

There is deliberately no `authorize_plan` tool. Authorization is a page-only
human action bound to the exact server-computed plan hash. Any later plan
mutation invalidates it.

## Verified evidence

- Seven Python tests pass on Python 3.13.
- `node --check static/app.js` passes.
- Production state survives Cloud Run revision replacement in Firestore.
- Receipt recovery returns the original receipt without duplicate execution.
- The stale-capability probe accepts zero obsolete mutations.
- The authorization probe accepts zero bypasses.
- The idempotency probe creates zero duplicate executions.
- The measured production protocol run recorded 121 ms median
  mutation-to-visible-update latency.
- Chrome Origin Trial registration enables `document.modelContext` for the exact
  production origin through November 16, 2026.

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

Local browsers without WebMCP support enter an explicit Manual mode; the full
human workflow remains usable.

## Verify in Chrome

The production origin is enrolled in Chrome's WebMCP Origin Trial for Chrome
149–156. With the ChatGPT browser extension connected, open this cache-busted
URL to avoid a stale pre-token document:

```text
https://captains-table-webmcp-1017459622661.us-east1.run.app/?build=origin-trial-1
```

Treat these as separate checkpoints:

1. The page reports **WebMCP connected**.
2. Page registration resolves for the expected capability epoch.
3. The ChatGPT host reports the tools it actually observes.
4. A host-originated invocation advances the visible revision.
5. The host observes the replacement tool set.

The first two checkpoints do not prove the remaining three.

## Test

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/playwright install chromium
.venv/bin/python -m pytest -q
```

The browser suite runs the complete WebMCP lifecycle against a local SQLite
server, including dynamic tool replacement, page-only authorization, receipt
recovery, stale-handle rejection, fallback modes, and visible stale-state recovery.

See [the engineering plan](docs/engineering-plan.md),
[interaction design](docs/interaction-design.md),
[Google Cloud deployment guide](docs/deploy-google-cloud.md),
[protocol observations](docs/protocol-observations.md), and the
[maintainer feedback log](docs/protocol-maintainer-feedback.md). The
[host-verification runbook](docs/webmcp-host-verification-runbook.md) defines the
gated procedure for completing the remaining end-to-end proof.

## Technology

- OpenAI ChatGPT as the external browser agent
- WebMCP imperative API through `document.modelContext`
- FastAPI, Pydantic, Firestore in production, SQLite locally, and plain semantic
  HTML/CSS/JavaScript
- Google Cloud Run with a least-privilege service identity

No embedded agent or second model is used. The OpenAI Agents SDK is deliberately
absent because ChatGPT already owns agent planning and WebMCP invocation.
