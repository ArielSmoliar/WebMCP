# WebMCP Demo Handoff

Updated: 2026-08-31

## Current State

The dedicated local Git repository is `/Users/arielsmoliar/Documents/ChatGPT/WebMCP`.
It is separate from Offsite Captain, Resurface, Flare AI, Stagehand, and loco-agent.

- Branch: `main`
- Current checkpoint: `a7eabab feat: enable Chrome WebMCP origin trial`
- Working tree before this final handoff update: clean
- Git remote: `https://github.com/ArielSmoliar/WebMCP.git`
- Public repository: `https://github.com/ArielSmoliar/WebMCP`
- Deployment: `https://captains-table-webmcp-1017459622661.us-east1.run.app`
- Cloud Run service: `captains-table-webmcp`, revision
  `captains-table-webmcp-00007-hft`, project `offsite-captain-2026`, region
  `us-east1`
- Firestore: deletion-protected named database `captains-table`; runtime IAM is
  conditionally restricted to that database
- A dedicated project, `captains-table-webmcp-2026`, was created but could not be
  linked to billing because the billing account reached its project quota. It is
  unused and unbilled; do not delete it without explicit user approval.
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

The page exposes six imperative workflow tools:

1. `inspect_decision`
2. `diagnose_plan`
3. `compare_repairs`
4. `select_repair`
5. `prepare_authorization`
6. `execute_authorized_plan`

It also exposes one diagnostic tool, `report_observed_capabilities`, which lets
ChatGPT report the tool set it currently sees. The Protocol Lab compares that
agent-reported set with the page's expected registration set. Do not describe a
resolved `registerTool()` promise as proof that the agent observed the tool.

Only the direct page UI can authorize the exact plan. There is deliberately no
`authorize_plan` WebMCP tool.

## Architecture

- FastAPI and Pydantic API in `app/main.py`
- Deterministic workflow with SQLite and Firestore adapters in `app/core.py`
- Semantic product interface in `static/index.html`
- Shared human/WebMCP action controller in `static/app.js`
- Persisted Protocol Lab telemetry in both storage adapters and the Technical
  Evidence rail
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
- Revision-bound capability epochs with deterministic tool-set fingerprints. An
  obsolete callback cannot acquire authority over newer page state, even before
  host-side removal propagation is observable.
- Manual fallback when WebMCP is unavailable.
- Exact-plan authorization and authorization invalidation after mutation.
- Docker, Render, provenance, and protocol-observation documentation.

## Verification Evidence

- Python 3.13: `7 passed` after the Firestore migration.
- JavaScript syntax: `node --check static/app.js` passed.
- Python compilation passed.
- `git diff --check` passed.
- In-app browser QA completed at 760px and 680px widths.
- Browser journey reached receipt `CT-830C56`, revision 7, and persisted it after reload.
- Production Cloud Run journey reached receipt `CT-F10E26`, revision 6, and
  restored it unchanged after a fresh reload from Firestore.
- Public `/health` returned `{"status":"ok"}` and `/readyz` returned
  `{"status":"ready"}` on Cloud Run revision 5.
- Post-deployment Impeccable audit scored 17/20. The resulting polish pass added
  shared pending/error recovery, complete control states, and the documented
  wide-screen protocol evidence rail. The polished local journey completed with
  receipt `CT-FAB03F`; production revision 3 serves the new error surface and
  polish stylesheet.
- Production Protocol Lab run completed at revision 6 with receipt `CT-2A9204`:
  0 stale mutations accepted, 0 authorization bypasses, 0 duplicate executions,
  121 ms median mutation-to-visible-update latency, and verified receipt recovery
  after reload. WebMCP discovery remains correctly labeled `Not reported` in the
  Manual-mode verification browser.
- The first revision 4 production check exposed mixed cached assets. Static asset
  versioning was added and verified in revision 5.
- Capability-epoch implementation passes all seven tests and JavaScript syntax
  verification locally. Cloud Run revision `captains-table-webmcp-00006-m2n`
  serves 100% of traffic, `/health` returns `{"status":"ok"}`, and the production
  HTML references the `capability-epochs-1` asset set. A real WebMCP-enabled agent
  observation and invocation run remains to be recorded.
- A target-browser attempt at `2026-08-31T21:02:59Z` loaded production revision
  `R6 · 04C2F029` in the Codex in-app ChatGPT browser and recovered receipt
  `CT-2A9204`. The page correctly entered Manual mode because that browser did not
  expose `document.modelContext`. It was the only connected browser surface, and
  no Captain's Table tools appeared in the host tool catalog. This is exact
  negative evidence only: it does not prove host discovery, invocation,
  replacement, or removal acknowledgement. `report_observed_capabilities` and a
  state-changing WebMCP invocation remain pending a WebMCP-enabled ChatGPT browser
  build.
- A follow-up at `2026-08-31T21:06:03Z` confirmed that ChatGPT app version
  `26.818.61809` (build `7019`) bundles native WebMCP browser support. The live
  production tab still advertised only `pageAssets`; direct lookup of the
  `webmcp` tab capability returned `Capability is not available: webmcp`.
  Therefore the limitation is session/backend enablement, not absence of client
  implementation. No public OpenAI enablement switch or supported-build matrix
  was found. The next real proof run needs a connected browser whose production
  tab advertises `webmcp`.
- After that attempt, `node --check static/app.js` passed and the Python 3.13
  suite passed all seven tests (with one upstream Starlette/httpx deprecation
  warning).
- Chrome Origin Trial registration `2570904476344909825` now enables WebMCP for
  the exact production origin through November 16, 2026. Cloud Run revision
  `captains-table-webmcp-00007-hft` serves the token and 100% of traffic.
- A cache-busted Chrome 151 load at `2026-08-31T21:20:49Z` reached "WebMCP
  connected," accepted 3/3 R1 page registrations, and reported epoch
  `R1 · 94CBFBDC`. The connected ChatGPT Chrome extension still advertised only
  `pageAssets`; native host lookup returned `Capability is not available:
  webmcp`. This is page-enablement evidence, not host discovery or invocation.
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

- Actual host discovery and invocation by ChatGPT. Chrome 151 now exposes
  `document.modelContext` through the Origin Trial and the page accepts its
  registrations, but the connected ChatGPT extension session did not advertise
  the host `webmcp` capability.
- Dynamic tool removal/appearance in the real judging environment.
- Real WebMCP discovery acknowledgement and dynamic removal in the target browser.
- Docker build. The local Docker client was installed, but its daemon socket did not respond.
- The full browser error matrix, concurrent browser tabs, and authorization expiry UI.

## Remaining Work, In Priority Order

1. Fully restart ChatGPT, reconnect Chrome, and reopen the cache-busted production
   URL `/?build=origin-trial-1`. Confirm that the tab advertises the native host
   `webmcp` capability before making any discovery claim.
2. If the host capability appears, verify all six workflow tools plus the
   diagnostic reporting tool, schemas, dynamic lifecycle, visible mutations,
   authorization boundary, and receipt.
3. Have the agent call `report_observed_capabilities` with the current revision and
   capability epoch, then capture one state-changing WebMCP invocation. This is the
   remaining proof needed to move the demonstrated score from 9.0 to 9.5.
4. Fix any compatibility differences found in the real browser. Use stable compatibility
   mode only if dynamic propagation is unreliable, and label it honestly.
5. Add browser automation coverage for the complete journey and failure matrix.
6. Run post-capability-epoch Impeccable critique and browser audit.
7. Prepare Devpost text, screenshots, video script, provenance statement, and submission.

## Important Boundaries

- OpenAI technology only. ChatGPT is the external agent.
- Do not add Gemini or Google ADK runtime code.
- Do not add the OpenAI Agents SDK unless real browser testing proves an embedded
  runtime is necessary. It is currently deliberately absent.
- Do not add a standalone MCP server. This demo is about page-scoped WebMCP.
- Do not claim that same-origin JavaScript proves physical human presence.
- Do not claim real WebMCP verification until it is exercised in the target browser.
- Deployment and public repository are already approved and live. Do not submit to
  Devpost without explicit user confirmation.

## New Session Prompt

```text
Continue the WebMCP hackathon demo in the dedicated repository at
/Users/arielsmoliar/Documents/ChatGPT/WebMCP. Read HANDOFF.md completely before
acting, then inspect git status and the latest commits. The public repository is
https://github.com/ArielSmoliar/WebMCP and the live Cloud Run demo is
https://captains-table-webmcp-1017459622661.us-east1.run.app. Production revision
captains-table-webmcp-00007-hft serves the capability-epoch build plus the Chrome
WebMCP Origin Trial token, which expires November 16, 2026.

The immediate goal is to turn the implemented WebMCP relevance score into a
demonstrated 9.5/10. Use a real WebMCP-enabled ChatGPT browser to verify dynamic
tool discovery, report_observed_capabilities with the current capability epoch,
one state-changing tool invocation, tool-set replacement after the revision
changes, the page-only authorization boundary, execution, receipt recovery, and
the stale-capability safety probe. Do not claim host discovery or removal
acknowledgement from registerTool resolution alone. Record exact evidence in
HANDOFF.md and docs/protocol-observations.md, fix compatibility issues if found,
run node --check static/app.js and the seven-test Python suite, then deploy and
push only if code changes are required.

Chrome 151 already proves page-level enablement: the cache-busted production URL
reported WebMCP connected, accepted 3/3 R1 registrations, and emitted epoch
R1 · 94CBFBDC. The prior ChatGPT extension session still exposed only pageAssets,
so restart ChatGPT and first verify that the tab advertises the native webmcp
capability. Do not confuse page registration with host discovery.

Preserve the settled architecture: OpenAI ChatGPT is the external agent, no
embedded Agents SDK, no Gemini/ADK runtime, no standalone MCP server, human-only
exact-plan authorization, Firestore production persistence, and revision-bound
capability epochs. Use the Impeccable skill for any interface changes. Keep the
tone precise, quietly ambitious, and trustworthy.
```

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
- `docs/protocol-maintainer-feedback.md`
- `docs/webmcp-host-verification-runbook.md`
- `.impeccable/critique/2026-08-31T17-23-19Z__docs-interaction-design-md.md`
- `CHALLENGE_WORK.md`
