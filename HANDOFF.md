# WebMCP Demo Handoff

Updated: 2026-08-31

## Current State

The dedicated local Git repository is `/Users/arielsmoliar/Documents/ChatGPT/WebMCP`.
It is separate from Offsite Captain, Resurface, Flare AI, Stagehand, and loco-agent.

- Branch: `main`
- Deployed code checkpoint: `b54c031 test: cover browser journey and failure matrix`
- Working tree before this final handoff update: clean
- Git remote: `https://github.com/ArielSmoliar/WebMCP.git`
- Public repository: `https://github.com/ArielSmoliar/WebMCP`
- Deployment: `https://captains-table-webmcp-1017459622661.us-east1.run.app`
- Cloud Run service: `captains-table-webmcp`, revision
  `captains-table-webmcp-00011-cf4`, project `offsite-captain-2026`, region
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
- Full ChatGPT built-in-host lifecycle verification across six capability epochs,
  including visible state-changing invocation, exact page-only authorization,
  execution, receipt recovery, host-observed replacement, and stale-handle
  rejection.
- Workflow-first interface redesign: persistent Inspect → Repair → Review →
  Reserve progression; exactly three default proof signals; full evidence behind
  disclosure; scoped busy feedback; and outcome-first receipt hierarchy.
- Final independent Impeccable static review: 40/40 with no remaining actionable
  static-design issues. The initial 29/40 and final 40/40 evidence snapshots are
  committed under `.impeccable/critique/`.
- Regression coverage in the existing seven-test suite locks the workflow/proof
  order, three-signal contract, collapsed evidence, responsive node relocation,
  scoped busy controls, cache-versioned assets, and absence of an
  `authorize_plan` tool.

## Verification Evidence

- Python 3.13: `20 passed` after expanding the isolated Playwright browser suite.
- `tests/test_browser.py` now covers the complete local R1 through R6 journey
  through a mocked `document.modelContext` registration surface and the real
  HTTP/SQLite controller path. It verifies dynamic tool replacement, absence of
  `authorize_plan`, page-only authorization, receipt recovery, stale-handle
  rejection, unavailable and rejected registration fallback, scoped busy state,
  visible public-error recovery, two-tab revision races, navigation during
  mutation without server corruption, and narrow reduced-motion layout. It does
  not replace native ChatGPT host proof.
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
- The approved host-verification run stopped at its mandatory capability gate at
  `2026-08-31T21:45:33Z`. Production health and readiness passed, revision
  `captains-table-webmcp-00007-hft` served 100% of traffic, and a fresh Chrome
  `151.0.7922.174` tab loaded draft state `R1 · DA4F4EFF`. The page again
  displayed **WebMCP connected**, accepted 3/3 registrations, and emitted epoch
  `R1 · 94CBFBDC`, while the ChatGPT Chrome host advertised only `pageAssets`.
  Per the runbook, no host tool fetch, WebMCP invocation, page click, workflow
  mutation, authorization, receipt, or safety probe followed. Host discovery,
  invocation, replacement, receipt recovery, and stale-capability behavior
  therefore remain unproven in the real host. Post-stop verification passed
  `node --check static/app.js`, the Python 3.13 suite (`7 passed`, one known
  Starlette/httpx deprecation warning), `/health`, and `/readyz`.
- A second approved gate at `2026-08-31T21:54:46Z` used the ChatGPT desktop
  app's built-in browser, the host surface now identified by official OpenAI
  site-tools documentation. The browser restored the existing completed session
  `R6 · 04C2F029` and receipt `CT-2A9204`; the page accepted 2/2 completed-state
  registrations at epoch `R6 · 19C3FFBF`. The built-in host still advertised
  only `pageAssets`, so the run again stopped before host discovery or
  invocation. This narrows the blocker to model, workspace, or rollout
  availability on the documented host surface, not the Chrome extension alone.
- Read-only local task metadata then confirmed that this task runs
  `gpt-5.6-sol`, an eligible model under OpenAI's site-tools documentation, and
  the app identifies it as a local Codex task rather than an Enterprise/Edu
  ChatGPT task. Rollout/session enablement is therefore the remaining supported
  explanation. No hidden flag or unsupported override was attempted.
- After updating and fully restarting ChatGPT, app version `26.825.51511`
  (build `7377`) exposed native `webmcp` on the built-in production tab at
  `2026-08-31T22:18:55Z`. The host fetched exactly the completed-state tools
  `inspect_decision` and `report_observed_capabilities`, including their schemas.
  The diagnostic report matched 2/2 tools at revision 6 and epoch
  `R6 · 19C3FFBF` with no missing or unexpected names and
  `epoch_matches: true`. A host invocation of `inspect_decision` returned plan
  hash `04C2F029` and receipt `CT-2A9204` without advancing revision. This is the
  first real proof of ChatGPT host discovery and invocation; dynamic replacement
  and a host-originated state mutation still require a fresh workflow session.
- At `2026-08-31T22:21:24Z`, the updated Chrome-control host reclaimed the
  already-open production draft tab `/?build=origin-trial-1`. Its exact native
  capability inventory still contained only `pageAssets`; `webmcp` was absent.
  The run therefore stopped at the mandatory capability gate without clicks,
  workflow mutations, safety probes, authorization, or a new Firestore session.
  This is a layered-readiness result: the updated built-in browser proves host
  discovery and read-only invocation on a completed session, while the Chrome
  extension does not advertise the native host capability on the draft tab.
- A verified operability defect prevented the documented fresh-session path:
  the page had no supported control for switching away from a completed local
  session. The scoped `Start new session` control was implemented, tested, and
  deployed. Revision `captains-table-webmcp-00008-jsq` exposed a second cache
  compatibility defect because cached older HTML could load the changed script
  under the unchanged asset URL. The backward-compatible listener and versioned
  asset URLs were deployed as revision `captains-table-webmcp-00009-z6j`, which
  serves 100% of traffic with passing `/health` and `/readyz`.
- The built-in host then completed the full production journey in Firestore
  session `UHxbrN-7PCXUU7kwmY2nCiNt`. Host-observed capability epochs were:
  `R1 · 94CBFBDC` (3 tools), `R2 · 3E4C671A` (4),
  `R3 · 81C06189` (5), `R4 · 2E089520` (6),
  `R5 · BB341B1D` (5), and `R6 · 19C3FFBF` (2). Every reported set matched
  with no missing or unexpected names and `epoch_matches: true`.
- Ariel personally authorized R4 plan `04C2F029`: shift the roadmap session to
  12:15, preserve attendance at 8 of 8, total cost $7,380, and scope one
  simulated offsite reservation. There is still no `authorize_plan` WebMCP
  tool. The host executed exactly once at R5 with idempotency key
  `host-run-20260831-3419e643-6a7c-4455-821e-6eb68cea83da`, producing receipt
  `CT-79ECA1` at R6. Reload recovered the same receipt.
- Host-observed replacement is proven by fetching each current set after state
  change. A retained R5 handle was rejected with `WebMCP tool registration is
  stale. Call fetchTools() again.` This is stale-handle evidence, not a claim
  that `registerTool()` resolution acknowledged removal. The persisted safety
  probes reported stale callback accepted `false` (`stale_state`), authorization
  bypassed `false` (`authorization_required`), and duplicate receipt `false`.
- Browser QA found and fixed:
  - duplicate repair actions;
  - stale budget, arrival, and agenda values after plan mutation;
  - repaired conflict presented as current;
  - stretched status treatment at 680px;
  - missing favicon request.
- Commit `f0e428f65ae71637249b13e585aa7e9c83cc243c` is pushed to GitHub
  `main`. The working tree was clean and synchronized after the push.
- Post-push production verification confirmed that no automatic deployment
  occurred: Cloud Run revision `captains-table-webmcp-00009-z6j` still serves
  100% of traffic and the live HTML still references the pre-redesign asset
  versions. `/`, `/health`, and `/readyz` passed. Google Frontend returns 404
  specifically for `/healthz`; use `/health` and `/readyz` for live readiness.
- Ariel then explicitly approved the push and workflow-first production release.
  Commits `5aa90dd` and `b54c031` were pushed to GitHub `main`. The expanded
  Python 3.13 suite passed 20 tests, including 13 Playwright browser cases.
- Cloud Run revision `captains-table-webmcp-00011-cf4` now serves 100% of traffic
  with the `impeccable-workflow-1` asset set. `/health` and `/readyz` passed.
  An isolated production visual smoke loaded the real HTML/CSS/JavaScript while
  intercepting all session API calls locally: HTTP 200, 166 ms navigation time,
  zero console errors, exactly three default proof signals, collapsed technical
  evidence, and no Firestore workflow mutation.

The temporary Python 3.13 verification environment was
`/private/tmp/captains-table-py313`. The workspace `.venv` uses Python 3.14 and
intermittently stalled importing pytest/FastAPI. Prefer Python 3.13, matching the
Docker image.

## Not Yet Verified

- Native host discovery in the connected Chrome extension. The updated built-in
  browser now proves discovery, state-changing invocation, dynamic replacement,
  stale-handle rejection, authorization separation, and receipt recovery.
- Protocol-native discovery acknowledgement and explicit dynamic-removal
  acknowledgement. The host lifecycle and stale-handle behavior are verified,
  but the current API still does not expose these acknowledgements.
- Local Docker-daemon execution. Cloud Build successfully built the Dockerfile
  for production revisions 8 and 9.
- The full browser error matrix, concurrent browser tabs, and authorization expiry UI.

## Remaining Work, In Priority Order

1. Preserve the completed production evidence and avoid creating another
   Firestore session unless a specific new verification requires it.
2. Extend browser automation further if time permits with server-backed expiry,
   inventory/storage fault injection, and explicit 200% zoom assertions. The
   current suite already covers their visible error treatment plus two-tab,
   navigation, reduced-motion, and narrow-layout behavior.
3. Capture submission screenshots/video and prepare Devpost text and provenance.
   Do not submit without Ariel's explicit confirmation.

## Important Boundaries

- OpenAI technology only. ChatGPT is the external agent.
- Do not add Gemini or Google ADK runtime code.
- Do not add the OpenAI Agents SDK unless real browser testing proves an embedded
  runtime is necessary. It is currently deliberately absent.
- Do not add a standalone MCP server. This demo is about page-scoped WebMCP.
- Do not claim that same-origin JavaScript proves physical human presence.
- Real WebMCP host discovery and invocation are verified in the ChatGPT built-in
  browser. Do not generalize that result to the Chrome extension, and do not
  claim protocol-native discovery or removal acknowledgement.
- The public repository and workflow-first production revision are live. Do not
  submit to Devpost without explicit confirmation.

## New Session Prompt

```text
Continue the WebMCP hackathon demo in the dedicated repository at
/Users/arielsmoliar/Documents/ChatGPT/WebMCP. Read HANDOFF.md completely before
acting, then inspect git status and the latest commits. The public repository is
https://github.com/ArielSmoliar/WebMCP and the live Cloud Run demo is
https://captains-table-webmcp-1017459622661.us-east1.run.app. GitHub `main`
includes deployed code commit b54c0316b80ace37847d0157db85fe9ef75f9e21 plus
the subsequent deployment-record documentation. Production revision
captains-table-webmcp-00011-cf4 serves 100% of traffic with the workflow-first
interface and the Chrome WebMCP Origin Trial token, which expires November 16,
2026.

The full built-in-host journey is verified through receipt CT-79ECA1. Preserve
that evidence while preparing submission materials, screenshots, and video.
The verified run captured dynamic tool discovery,
report_observed_capabilities at every capability epoch, state-changing tool
invocations, tool-set replacement, the page-only authorization boundary,
execution, receipt recovery, and
the stale-capability safety probe. Do not claim host discovery or removal
acknowledgement from registerTool resolution alone. Record exact evidence in
HANDOFF.md and docs/protocol-observations.md, fix compatibility issues if found,
run node --check static/app.js and the 20-test Python suite. The final local
Impeccable review is 40/40. Do not submit to Devpost without explicit
confirmation.

Chrome 151 proves page-level enablement but its connected extension exposed only
pageAssets. The ChatGPT built-in browser separately proved native webmcp host
discovery and invocation. Preserve that layered distinction and do not confuse
page registration with host discovery.

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
- `.impeccable/critique/2026-08-31T23-04-57Z__static-index-html.md`
- `.impeccable/critique/2026-08-31T23-17-41Z__static-index-html.md`
- `CHALLENGE_WORK.md`
