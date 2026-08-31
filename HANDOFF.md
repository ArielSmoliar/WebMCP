# WebMCP Demo Handoff

Updated: 2026-08-31

## Current State

The dedicated local Git repository is `/Users/arielsmoliar/Documents/ChatGPT/WebMCP`.
It is separate from Offsite Captain, Resurface, Flare AI, Stagehand, and loco-agent.

- Branch: `main`
- Implementation checkpoint: `a247d9e feat: build WebMCP shared decision demo`
- Working tree at handoff creation: clean before adding these handoff artifacts
- Git remote: `https://github.com/ArielSmoliar/WebMCP.git`
- Public repository: `https://github.com/ArielSmoliar/WebMCP`
- Deployment target: Google Cloud Run with Firestore; not yet created
- Product name in the code and interface: `Captain's Table`
- Repository name: `WebMCP`

The user questioned why the interface was still called Captain's Table. We clarified
that `WebMCP` is the dedicated repository and Captain's Table is only the internal
demo/product name. Do not rename the product or repository without settling this
explicitly with the user.

## Product Thesis

The demo is a reusable reference for a trustworthy shared decision surface operated
by a human and ChatGPT's browser agent. The offsite plan is the demonstration
scenario, not the intended product boundary.

The page exposes six imperative WebMCP tools:

1. `inspect_decision`
2. `diagnose_plan`
3. `compare_repairs`
4. `select_repair`
5. `prepare_authorization`
6. `execute_authorized_plan`

Only the direct page UI can authorize the exact plan. There is deliberately no
`authorize_plan` WebMCP tool.

## Architecture

- FastAPI and Pydantic API in `app/main.py`
- Deterministic workflow with SQLite and Firestore adapters in `app/core.py`
- Semantic product interface in `static/index.html`
- Shared human/WebMCP action controller in `static/app.js`
- Base tokens and layout in `static/styles.css` and `static/workflow.css`
- Docker and Cloud Run deployment configuration in `Dockerfile` and
  `docs/deploy-google-cloud.md`

The server is authoritative. Every mutation carries an expected revision. SQLite
uses `BEGIN IMMEDIATE` locally and Firestore uses transactions in production.
Authorization binds the exact plan hash. Execution uses an idempotency key and
returns the existing receipt on replay.

## Completed Work

- Product, design, interaction, engineering, and test plans.
- Full engineering-plan review with all decisions resolved.
- Impeccable critique, score 31/40 before implementation.
- All five critique priorities resolved in the interaction specification.
- Complete manual workflow: diagnose, compare, select, human edit, authorize,
  execute, reload, and recover the same receipt.
- Dynamic state-aware WebMCP registration using `document.modelContext.registerTool()`
  and abort-based unregistration.
- Manual fallback when WebMCP is unavailable.
- Exact-plan authorization and authorization invalidation after mutation.
- Docker, Render, provenance, and protocol-observation documentation.

## Verification Evidence

- Python 3.13: `6 passed` in `8.03s`.
- JavaScript syntax: `node --check static/app.js` passed.
- Python compilation passed.
- `git diff --check` passed.
- In-app browser QA completed at 760px and 680px widths.
- Browser journey reached receipt `CT-830C56`, revision 7, and persisted it after reload.
- Browser QA found and fixed:
  - duplicate repair actions;
  - stale budget, arrival, and agenda values after plan mutation;
  - repaired conflict presented as current;
  - stretched status treatment at 680px;
  - missing favicon request.

The temporary Python 3.13 verification environment was
`/private/tmp/captains-table-py313`. The workspace `.venv` uses Python 3.14 and
intermittently stalled importing pytest/FastAPI. Prefer Python 3.13, matching the
Docker image.

## Not Yet Verified

- Actual discovery and invocation by ChatGPT in a WebMCP-enabled browser. The in-app
  browser used for QA did not expose `document.modelContext`, so it exercised Manual mode.
- Dynamic tool removal/appearance in the real judging environment.
- Public deployment and restart recovery on a Render persistent disk.
- Docker build. The local Docker client was installed, but its daemon socket did not respond.
- The full browser error matrix, concurrent browser tabs, and authorization expiry UI.
- A post-implementation Impeccable critique/audit.

## Remaining Work, In Priority Order

1. Decide whether the product remains `Captain's Table` or receives a protocol-native
   name. Do not conflate this with the dedicated repository name `WebMCP`.
2. Decide whether the GitHub repository should be public or private.
3. Create the GitHub repository, add the remote, and push `main` only after the user
   authorizes the visibility choice.
4. Deploy the Cloud Run service with Firestore Native mode.
5. Open the deployed URL in a WebMCP-enabled ChatGPT browser and verify all six tools,
   schemas, dynamic lifecycle, visible mutations, authorization boundary, and receipt.
6. Fix any compatibility differences found in the real browser. Use stable compatibility
   mode only if dynamic propagation is unreliable, and label it honestly.
7. Add browser automation coverage for the complete journey and failure matrix.
8. Run post-implementation Impeccable critique, audit, and polish.
9. Prepare Devpost text, screenshots, video script, provenance statement, and submission.

## Important Boundaries

- OpenAI technology only. ChatGPT is the external agent.
- Do not add Gemini or Google ADK runtime code.
- Do not add the OpenAI Agents SDK unless real browser testing proves an embedded
  runtime is necessary. It is currently deliberately absent.
- Do not add a standalone MCP server. This demo is about page-scoped WebMCP.
- Do not claim that same-origin JavaScript proves physical human presence.
- Do not claim real WebMCP verification until it is exercised in the target browser.
- Do not publish, deploy, or submit without the required user decision or confirmation.

## Useful Commands

```bash
cd "/Users/arielsmoliar/Documents/ChatGPT/WebMCP"
/opt/homebrew/bin/python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt pytest httpx
.venv/bin/python -m pytest -q
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8097
```

## Primary Files

- `PRODUCT.md`
- `DESIGN.md`
- `docs/engineering-plan.md`
- `docs/interaction-design.md`
- `docs/test-plan.md`
- `docs/protocol-observations.md`
- `.impeccable/critique/2026-08-31T17-23-19Z__docs-interaction-design-md.md`
- `CHALLENGE_WORK.md`
