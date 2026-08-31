# Engineering Plan: Captain's Table WebMCP Demo

> Deployment amendment (2026-08-31): production persistence now targets
> Firestore transactions on Google Cloud Run. SQLite remains the local adapter.
> The original Render/SQLite deployment discussion below is retained as design
> history; `docs/deploy-google-cloud.md` is the authoritative deployment guide.

## Outcome

Ship a dedicated, public, OpenAI-first WebMCP application in which a judge uses
ChatGPT's in-app browser to inspect, repair, authorize, and execute one live
offsite decision. The page and ChatGPT operate the same state. Human authorization
remains impossible through WebMCP.

## Scope

### In

- One deterministic offsite scenario with an intentionally stale constraint.
- One judge-operated decision surface.
- One bounded human arrival-time edit that proves stale-state invalidation.
- One bounded revert of the latest pre-authorization mutation.
- Six state-aware WebMCP tools.
- Dynamic registration and removal of consequential tools.
- Shared UI actions for clicks and WebMCP invocations.
- Exact-plan hashing and human-only authorization.
- Idempotent simulated execution and a confirmation receipt.
- A stale-plan rejection path demonstrated in the product.
- A compact protocol evidence rail and future-WebMCP observations.
- Unit, API, browser-state, and tool-contract tests.
- A deployable container and public-repository documentation.

### Out

- Gemini or Google ADK runtime code.
- An embedded chat interface or second agent.
- OpenAI Agents SDK unless browser-agent testing proves deterministic repair tools
  insufficient.
- Real bookings, real inventory, calendars, email, or authentication.
- Multi-user collaboration, multiple scenarios, or a generalized workflow engine.
- A standalone MCP server.

## Existing Work Reused

The new repository may adapt code we own from Offsite Captain. The challenge
submission will identify all reused files and distinguish pre-August 25 work from
the WebMCP extension through commit history and `CHALLENGE_WORK.md`.

| Problem | Reuse | New work |
|---|---|---|
| Domain models | Adapt strict plan and ledger models | Smaller public contracts for WebMCP |
| Validation | Adapt deterministic feasibility rules | Conflict and repair result schema |
| Plan identity | Adapt canonical SHA-256 hashing | Expose short identity in shared UI |
| Authorization | Adapt exact-plan, expiring approval | Human-only browser interaction |
| Execution | Adapt idempotent simulated booking | Structured WebMCP receipt result |
| Persistence | Adapt repository boundary and SQLite adapter | Persistent single-instance demo storage |
| Agent runtime | Do not reuse Gemini/ADK | ChatGPT is the external agent |
| Frontend | Do not port old layout | New shared decision surface |

## Architecture

```text
ChatGPT in-app browser
        |
        | discover / invoke document.modelContext tools
        v
+--------------------------------------------------+
| Browser                                           |
|                                                   |
|  WebMCP registry                                  |
|       |                                           |
|       v                                           |
|  Shared action controller <---- human controls    |
|       |                         and page edits      |
|       | render state + evidence                   |
+-------|-------------------------------------------+
        |
        | typed JSON API
        v
+--------------------------------------------------+
| FastAPI                                           |
|                                                   |
| scenario -> validator -> repairs -> plan hash     |
|                            |                      |
| human authorization store -> execution engine    |
|                            |                      |
|                       confirmation receipt       |
+--------------------------------------------------+
```

The browser action controller is the only mutation entry point on the client.
Buttons and WebMCP callbacks call the same functions. WebMCP callbacks never
manipulate the DOM directly and never recreate business rules.

Product copy names the decision state first. Tool names, revisions, hashes, and
invocation metadata appear only inside Technical evidence, except for the compact
revision seal. Remote tool calls never steal keyboard focus.

## Workflow State

```text
DRAFT
  | diagnose
  v
CONFLICT_FOUND
  | compare repairs
  v
OPTIONS_READY
  | human or agent selects repair
  v
REVIEWED
  | human authorizes exact hash
  v
AUTHORIZED
  | execute tool or human control
  v
COMPLETED

Any plan mutation after REVIEWED or AUTHORIZED
  -> invalidates approval
  -> returns to REVIEWED with a new hash

Revert latest mutation before authorization
  -> creates a new revision and hash
  -> records the reversed mutation
  -> never restores prior authorization
```

The server owns the authoritative workflow state. The browser holds a renderable
snapshot plus the current server revision. Every mutation sends the expected
revision. A mismatch returns `stale_state`, never silent last-write-wins behavior.

Workflow snapshots are stored in SQLite on an attached persistent volume. The
deployment runs one application instance so compare-and-save revision checks and
idempotent execution retain the same serialized semantics as the local process.
The service must fail readiness if the configured persistent path is not writable.

Every mutation uses one SQLite `BEGIN IMMEDIATE` transaction: load the session,
verify the expected revision, apply exactly one state transition, persist revision
+ 1, and commit. A competing request blocks and then returns `stale_state` after it
observes the committed revision. Confirmation receipts have a unique constraint on
session plus idempotency key, so repeated execution returns the original receipt.

Execution replay is ordered deliberately. The server first looks up the receipt by
session and idempotency key. It returns that receipt only when the stored plan hash
and action match the request; mismatched key reuse fails. When no receipt exists,
the server then verifies revision, authorization, and inventory before executing.

## WebMCP Tool Surface

| Tool | State | Side effect | Visible result |
|---|---|---|---|
| `inspect_decision` | All | None | Focuses current state; returns the receipt when completed |
| `diagnose_plan` | Draft+ | Analysis state only | Highlights the blocking conflict |
| `compare_repairs` | Conflict found+ | Creates bounded alternatives | Opens an inline comparison |
| `select_repair` | Options ready+ | Changes exact plan and hash | Updates schedule, cost, and decision trail |
| `prepare_authorization` | Reviewed | None | Focuses the human review control |
| `execute_authorized_plan` | Authorized only | Simulated reservation | Replaces decision view with receipt |

### Tool Transition and Retry Matrix

| Tool | Allowed states | First call | Repeat call | Revision | Authorization |
|---|---|---|---|---|---|
| `inspect_decision` | All | Read current snapshot or receipt | Return current snapshot or receipt | Never changes | Never changes |
| `diagnose_plan` | Draft, conflict, options, reviewed, authorized | Draft → conflict with deterministic finding | Return existing finding | First transition only | Never changes |
| `compare_repairs` | Conflict, options, reviewed | Conflict → options with deterministic alternatives | Return existing alternatives | First transition only | Never changes |
| `select_repair` | Options, reviewed, authorized | Select repair → reviewed with new hash | Same repair is a no-op; different repair selects and rehashes | Only when selection changes | Different selection invalidates |
| `prepare_authorization` | Reviewed | Focus exact review boundary | Return same review data | Never changes | Never creates authorization |
| `execute_authorized_plan` | Authorized, completed | Authorized → completed with receipt | Matching idempotency key returns receipt | First execution only | Consumed/preserved with receipt |

Calls outside the named states return `invalid_state` without mutation. Expired
authorization returns the session to reviewed before producing
`authorization_expired`. The bounded human arrival edit is allowed in reviewed or
authorized state, always creates a new revision and hash when the value changes,
and invalidates authorization. Submitting the current arrival time is a no-op.

`authorize_plan` is deliberately absent. Only a direct human interaction can
create authorization. `execute_authorized_plan` is registered only while a valid
authorization exists and is removed immediately when the plan changes or execution
completes.

Dynamic registration is the primary mode. A compatibility mode keeps the same
stateful tools registered throughout the session but enforces state in each callback
and returns `invalid_state` or `authorization_required` without mutation. The
deployed app is tested in ChatGPT before submission; dynamic mode ships only if
tool-change propagation is reliable across the full judging flow. Both modes share
the same tool definitions and callback implementations.

One callback wrapper is the sole source of WebMCP evidence events. It records an
invocation ID, `source: webmcp`, tool name, start time, duration, revision before
and after, result code, and changed UI regions. Direct controls emit distinct
`source: human` events through the shared action controller. UI rendering code
cannot create WebMCP-labeled evidence independently.

Every tool returns:

```json
{
  "ok": true,
  "state": "reviewed",
  "revision": 4,
  "summary": "Selected the arrival-safe repair.",
  "data": {},
  "ui": { "focus": "authorization", "changed": ["agenda", "cost", "hash"] }
}
```

`app/core.py` defines one public error-code enum. API responses and WebMCP tool
results pass those codes through unchanged; the frontend maps each code to visible
recovery guidance without inventing aliases. The catalog includes
`unsupported_browser`, `tool_registration_rejected`, `invalid_input`,
`invalid_state`, `stale_state`, `authorization_required`,
`authorization_expired`, `plan_changed`, `inventory_changed`, `storage_error`,
and `execution_uncertain`.

## WebMCP Lifecycle

```text
load page
  -> feature-detect document.modelContext
  -> register tools allowed for snapshot state
  -> render WebMCP availability

state/revision changes
  -> abort prior registrations
  -> register the exact new tool set
  -> append protocol evidence event

navigate away
  -> abort all registrations
```

The app remains usable without WebMCP, but shows an explicit unsupported-browser
state and test instructions. It never installs a fake production polyfill.

## API Contracts

- `POST /api/session`: create a fresh deterministic judge session with an opaque,
  cryptographically random identifier. It never resets an existing session.
- `GET /api/session/{id}`: return the authoritative snapshot.
- `POST /api/session/{id}/diagnose`: return findings at an expected revision.
- `POST /api/session/{id}/repairs`: create bounded repair alternatives.
- `POST /api/session/{id}/selection`: select one repair and update the plan hash.
- `POST /api/session/{id}/constraint`: update one attendee arrival time, increment
  revision, recalculate findings, change the exact plan hash, and invalidate approval.
- `POST /api/session/{id}/revert`: reverse the latest eligible pre-authorization
  mutation at an expected revision, create a new revision and hash, and preserve a
  trail link to the reversed mutation. It never restores authorization.
- `POST /api/session/{id}/authorize`: direct-UI request carrying the exact plan
  hash, revision, scope, and an explicit consent value.
- `POST /api/session/{id}/execute`: require authorization and an idempotency key.

Responses are strict JSON. Unknown fields and invalid enum values fail closed.

The browser stores its opaque session identifier in local storage. “Start over”
creates a new session and switches the browser to it; no public endpoint resets an
existing session. Sessions expire 30 days after their last activity and are lazily
deleted during session creation, keeping judges isolated through the full judging
period without adding authentication.

## Human-Only Authorization

No WebMCP tool authorizes a plan. The direct page control is the only product path
that calls the authorization endpoint, which requires explicit consent plus the
exact session, revision, plan hash, and action scope. The server still rejects
expired, stale, mismatched, or superseded authorization records.

This is a WebMCP capability boundary, not an identity or trusted-human-presence
claim. JavaScript executing in the same origin cannot securely prove to the server
that a request originated from a physical click. The product and submission will
state that a standardized WebMCP elicitation and authorization primitive would
improve future versions.

## Failure and Recovery Map

| Failure | Trigger | User/agent result |
|---|---|---|
| Unsupported WebMCP | API absent | Product works manually; setup guidance is visible |
| Tool registration rejected | permission/policy | Evidence rail names the rejection; manual flow remains |
| Invalid tool input | schema mismatch | Stable failure; no state change |
| Slow request | network delay | The affected action shows pending state; duplicate input disabled |
| Navigate during request | page unload | Client aborts; server operation remains revision/idempotency safe |
| Double invocation | repeated action | Same revision or idempotency key returns same outcome |
| Stale revision | page or agent used old state | Reject and refresh authoritative snapshot |
| Missing authorization | execute before approval | Reject and focus authorization boundary |
| Plan changed | mutation after approval | Invalidate approval and require new review |
| Inventory changed | execution-time version mismatch | Reject without partial receipt |
| Response lost after execution | network failure | Recovery call returns existing receipt |
| Process restart | host restart or deploy | Session, authorization, and receipt reload from SQLite |
| Persistence unavailable | missing/unwritable volume | Readiness fails; mutations return a named storage error |
| Concurrent judges | separate browsers use the app | Opaque session IDs isolate all state and receipts |

## Test Plan

```text
Domain tests
  models -> validator -> repairs -> hash -> authorization -> execution

API tests
  strict contracts -> revision conflicts -> auth boundary -> idempotency

Browser controller tests
  human action ----+
                   +-> same controller -> same state/render
  WebMCP callback -+

Playwright browser tests
  mocked modelContext -> schemas -> lifecycle -> dynamic tool set -> failures

End-to-end smoke
  open -> diagnose -> compare -> select -> authorize -> execute -> recover
```

Required edge cases include empty input, unknown repair ID, repeated selection,
double authorization, expired authorization, mutation after authorization, double
execution, lost execution response, back navigation, narrow viewport, reduced
motion, and absence of `document.modelContext`.

Contract coverage must enumerate every public error code and assert both its API
shape and its visible browser recovery treatment.

### Required Test Matrix

`tests/test_core.py`:

- Scenario validates the intended conflict and no unrelated findings.
- Repair generation is deterministic, bounded, budget-aware, and rejects invalid input.
- Selection accepts the current revision and rejects stale or unknown selections.
- Arrival adjustment accepts a bounded valid time, rejects invalid input, increments
  revision, recalculates findings, changes the hash, and invalidates authorization.
- Plan hashing is canonical; meaningful mutations change the hash.
- Authorization accepts exact state and rejects stale, changed, expired, or superseded plans.
- Execution succeeds once, returns the same receipt for a duplicate idempotency key,
  rejects a changed plan, and preserves atomicity on inventory failure.
- SQLite restores draft, authorization, and completed receipt state after restart.
- Storage failures produce `storage_error` without partial state.

`tests/test_api.py`:

- Every route accepts its strict contract and rejects missing, extra, mistyped, and
  overlong input.
- Revision conflicts, domain failures, and unexpected storage failures map to the
  documented status and error envelope.
- Authorization requires explicit consent, exact scope, revision, and plan hash.
- The bounded constraint endpoint rejects stale revisions and cannot edit other fields.
- Revert accepts only the latest eligible pre-authorization mutation, creates a new
  revision, rejects stale or repeated requests, and never restores authorization.
- Health succeeds independently; readiness fails for an unwritable database path
  and succeeds after a database read/write transaction.
- Concurrent mutation requests produce one winner and one `stale_state` result.

`tests/test_browser.py` with Playwright:

- Human controls and WebMCP callbacks call the same action-controller methods and
  produce equivalent snapshots and localized visual changes.
- Dynamic mode registers the state-appropriate tool set, aborts old registrations,
  and surfaces the newly authorized execution tool.
- Compatibility mode keeps tools stable and returns named state failures without
  mutation.
- Authorization is never registered as a WebMCP tool in either mode.
- Missing `document.modelContext` and rejected registration remain manually usable
  and show explicit guidance.
- Every public error code produces structured tool output, visible recovery copy,
  and a recoverable next action.
- Slow requests disable duplicate controls; double invocation is idempotent;
  navigation aborts client work without corrupting server state.
- A stale open page refreshes to the authoritative revision after rejection.
- Remote mutations preserve keyboard focus, announce consequential changes, and
  expose a persistent jump link to the affected region.
- The comparison retains table semantics, labeled overflow, and usable navigation
  at 680px and 200% zoom.
- First-run guidance is dismissible, uses the real workflow, and retires after diagnosis.
- Lost execution response recovers the persisted receipt.
- The full judge journey passes at desktop and narrow viewport widths.
- Keyboard operation, visible focus, color-independent status, and reduced-motion
  behavior remain functional despite no formal conformance target.

## File Plan

```text
app/
  main.py              FastAPI routes and static hosting
  core.py              models, scenario, validation, state, auth, execution
static/
  index.html           semantic judge-operated surface
  app.js               action controller, renderer, WebMCP registry
  styles.css           tokenized product design
tests/
  test_core.py
  test_api.py
  test_browser.py       Playwright with a mocked document.modelContext
docs/
  engineering-plan.md
  interaction-design.md
  protocol-observations.md
PRODUCT.md
DESIGN.md
CHALLENGE_WORK.md
README.md
LICENSE
pyproject.toml
Dockerfile
render.yaml
```

The eight implementation and test files are an explicit scope limit. Documentation,
packaging, and challenge-provenance files remain separate because they are release
requirements, not runtime abstractions. No second JavaScript test toolchain is
introduced.

## Delivery Sequence

### Gate 1: Prove the browser lifecycle

1. Deploy a minimal page that registers a read tool, changes the tool set after one
   state transition, and emits real callback evidence.
   Provision the paid Render instance and persistent disk before this deployment;
   confirm region, mount path, restart persistence, and service availability.
2. Verify discovery, invocation, `toolchange` propagation, and re-invocation in
   ChatGPT's in-app browser.
3. Lock dynamic mode or compatibility mode before building the full integration.

### Gate 2: Ship the complete golden journey

4. Port the reduced deterministic core and lock strict API contracts.
5. Build the shared action controller and semantic decision surface.
6. Implement diagnose, compare, select, bounded human edit, authorization, execute,
   and receipt recovery through the selected registration mode.
7. Deploy and run the complete sub-three-minute flow in ChatGPT.

### Gate 3: Earn the technical-completeness claim

8. Add SQLite restart recovery, transaction contention, and every named error path.
9. Complete the full pytest and Playwright matrix.
10. Resolve visual tokens, rerun Impeccable documentation, critique, and audit.
11. Write protocol observations from demonstrated evidence, freeze the deployment,
    record the video, and finalize submission materials.

If Gate 1 or Gate 2 fails, reduce scope explicitly against the accepted plan before
continuing. Do not spend the remaining schedule on Gate 3 while the real ChatGPT
journey is unverified.

## Parallelization

| Lane | Work | Depends on |
|---|---|---|
| A | Core state, SQLite transactions, API contracts, backend tests | Scope and contracts |
| B | Semantic page structure, visual tokens, responsive states | Snapshot and error-envelope shapes |
| C | Challenge provenance, protocol observations, deployment documentation | Scope |
| D | WebMCP registry, browser controller, Playwright journey | A and B |

Lanes A, B, and C may begin in parallel after the JSON contracts are written. Lane
D follows the stable backend and markup contracts. Because this repository is small
and `static/app.js` is the shared integration point, WebMCP and browser-controller
implementation stay in one sequential lane.

## What Already Exists

- Offsite Captain's strict models, deterministic validator, canonical hashing,
  exact-plan authorization, SQLite repository, idempotent booking engine, and
  recovery semantics partially solve the backend problem and will be adapted.
- Its Gemini/ADK runtime and existing frontend are intentionally not reused because
  ChatGPT is the external agent and the WebMCP interaction needs a new composition.
- ChatGPT's in-app browser provides the agent and WebMCP client; the product does not
  build or embed a second agent loop.

## NOT in Scope

- OpenAI Agents SDK: unnecessary while ChatGPT owns the browser-agent loop.
- A separate MCP server: duplicates the page-scoped WebMCP surface.
- Real reservations and third-party integrations: add risk without improving the
  protocol demonstration.
- Multiple scenarios, users, or organizations: distract from one complete judging
  journey.
- A generalized workflow framework: the submission demonstrates the pattern before
  attempting to productize it.
- Managed Postgres and multi-instance scale: SQLite with one Render instance meets
  the judging reliability requirement with less infrastructure.

## Implementation Tasks

- [ ] **T1 (P1, human: ~1 day / Codex: ~2h)**: Core: Port the deterministic
  domain and implement transactional revisioned SQLite state.
  - Surfaced by: Architecture and performance review, persistence and concurrency.
  - Files: `app/core.py`, `tests/test_core.py`
  - Verify: `pytest tests/test_core.py -q`
- [ ] **T2 (P1, human: ~1 day / Codex: ~2h)**: API: Implement strict action,
  authorization, execution, health, and readiness contracts.
  - Surfaced by: Architecture and code-quality review, explicit capability and error boundaries.
  - Files: `app/main.py`, `tests/test_api.py`
  - Verify: `pytest tests/test_api.py -q`
- [ ] **T3 (P1, human: ~1 day / Codex: ~2h)**: WebMCP: Build one shared action
  controller with dynamic registration and compatibility mode.
  - Surfaced by: Architecture review, ChatGPT lifecycle compatibility.
  - Files: `static/app.js`, `tests/test_browser.py`
  - Verify: `pytest tests/test_browser.py -q`
- [ ] **T4 (P1, human: ~1 day / Codex: ~2h)**: Interface: Implement the shared
  decision surface and every required visible state.
  - Surfaced by: Interaction design and test review.
  - Files: `static/index.html`, `static/styles.css`, `tests/test_browser.py`
  - Verify: desktop and narrow Playwright journeys plus Impeccable critique/audit
- [ ] **T5 (P1, human: ~4h / Codex: ~45m)**: Distribution: Package and deploy one
  Render instance with a persistent disk and verified readiness.
  - Surfaced by: Architecture review, public judging availability.
  - Files: `Dockerfile`, `render.yaml`, `README.md`
  - Verify: deployed `/healthz`, `/readyz`, restart recovery, and no-deploy freeze
- [ ] **T6 (P2, human: ~4h / Codex: ~45m)**: Submission: Document provenance,
  protocol observations, test evidence, and the final demo path.
  - Surfaced by: Devpost existing-project rules and product positioning.
  - Files: `CHALLENGE_WORK.md`, `docs/protocol-observations.md`, `README.md`
  - Verify: public repository requirements and sub-three-minute script checklist

## Distribution

The production target is one paid Render web-service instance built from the
repository. `render.yaml` defines the FastAPI start command, health check, one
instance, and a persistent disk mounted at `/var/data`. The application reads the
SQLite path from `CAPTAINS_TABLE_DB`, which production sets to
`/var/data/captains-table.sqlite3`.

Render's disk makes the service temporarily unavailable during a deploy, so the
release procedure includes a deployed smoke test followed by a deployment freeze
for the judging period. `/healthz` reports process health; `/readyz` verifies the
database path is writable and a read/write transaction succeeds.

## Release Gates

- No Gemini or Google ADK dependency remains.
- No authorization WebMCP tool exists.
- Human and WebMCP paths share the same client controller.
- All state mutations require expected revision.
- Execution is idempotent and recoverable.
- SQLite state survives application restarts on an attached persistent volume.
- Deployment is limited to one application instance until transactional compare-and-save exists.
- Render configuration mounts `/var/data`, runs one paid instance, and passes both health probes.
- No deploy occurs after the final judging smoke test unless recovery requires it.
- The live URL works without credentials through the judging period.
- Dynamic tool changes work through the full ChatGPT flow, or the tested
  stable-registration compatibility mode is selected before recording.
- Public repository includes an OSI-compatible license and provenance document.
- The demo video contains a real ChatGPT WebMCP invocation, stale-state rejection,
  human authorization, successful execution, and receipt recovery.

## Engineering Review Summary

- Step 0 scope challenge: reduced to eight implementation and test files.
- Architecture review: four issues found and resolved.
- Code-quality review: one issue found and resolved through a single error contract.
- Test review: branch and interaction diagram produced; full matrix accepted.
- Performance review: one concurrency issue resolved with transactional mutations.
- Outside voice: twelve findings reviewed; each was accepted, already covered, or
  resolved through an explicit decision.
- Critical silent gaps: zero remain in the plan.
- TODO proposals: zero. Deferred productization work is intentionally listed under
  NOT in Scope instead of creating speculative backlog.
- Parallelization: three early lanes may run in parallel; WebMCP integration follows
  stable backend and markup contracts.
- Completeness choices: 17 of 17 recommendations accepted at the complete or
  recommended gated option.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | Not run | Prior conversational strategy review only |
| Codex Review | `/codex review` | Independent second opinion | 1 | Clear | Isolated outside voice, 12 findings resolved |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | Clear | 8 primary issues, 0 critical gaps |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | Pending | Impeccable plan evaluation follows |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | Not run | Not required for the plan gate |

**CROSS-MODEL:** The outside voice challenged schedule risk, session lifecycle,
dynamic-tool sequencing, replay ordering, stale-state feasibility, visual readiness,
and split-pane density. All disagreements were resolved through explicit decisions.

**VERDICT:** ENG CLEARED. The gated plan is ready for Impeccable design evaluation.

NO UNRESOLVED DECISIONS
