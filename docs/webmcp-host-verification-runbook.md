# WebMCP Host Verification Runbook

## Metadata

- **Status:** Approved
- **Owner:** Ariel Smoliar
- **Operator:** Ariel Smoliar for the page-only authorization step; Codex for
  browser inspection, WebMCP invocation, verification, and evidence capture
- **Last verified:** 2026-08-31 (completed end to end in the ChatGPT built-in
  browser; receipt `CT-79ECA1`)
- **Environment:** Production Cloud Run service `captains-table-webmcp`, project
  `offsite-captain-2026`, region `us-east1`; the ChatGPT desktop app's built-in
  browser, which official OpenAI documentation identifies as the supported site
  tools surface; verified with ChatGPT desktop `26.825.51511` build `7377`
- **Expected duration:** 30–45 minutes after the host `webmcp` capability is
  available
- **Change/incident ID:** WebMCP host verification / demonstrated relevance 9.5

## Objective

Demonstrate, with exact and bounded evidence, that a real ChatGPT browser host
discovers and invokes Captain's Table's state-dependent WebMCP tools through a
complete production workflow. Preserve the page-only human authorization
boundary, prove receipt recovery and stale-capability containment, and avoid
claiming host discovery or removal acknowledgement from page registration alone.

## Scope

**Included**

- Live demo:
  `https://captains-table-webmcp-1017459622661.us-east1.run.app/`
- One newly created production workflow session in Firestore
- Chrome Origin Trial page enablement and ChatGPT host capability discovery
- Host-observed tool sets and capability epochs across workflow revisions
- One state-changing WebMCP invocation at minimum; complete WebMCP journey when
  the host behaves correctly
- Direct page authorization by the human operator
- Execution, idempotent receipt recovery, and the built-in stale-capability,
  authorization, and duplicate-execution probes
- Sanitized evidence updates in `HANDOFF.md`,
  `docs/protocol-observations.md`, and
  `docs/protocol-maintainer-feedback.md`

**Excluded**

- Devpost submission
- Renaming the product or repository
- Adding an embedded agent, OpenAI Agents SDK runtime, Gemini/ADK runtime, or
  standalone MCP server
- Destructive Firestore cleanup, IAM changes, billing changes, credential
  creation, or Origin Trial registration changes
- Compatibility fixes, deployment, or Git push during the evidence run; those
  require a separate reviewed change after the run stops

**Must remain unchanged**

- OpenAI ChatGPT remains the external agent.
- Only the direct page UI may authorize the exact plan. There must be no
  `authorize_plan` WebMCP tool.
- Server-side expected-revision checks, plan-hash authorization, Firestore
  persistence, idempotency, and revision-bound capability epochs remain intact.
- Page registration acceptance must remain labeled separately from host
  discovery and removal propagation.
- Existing production sessions and receipts must not be deleted or overwritten.

## Preconditions

- [ ] Repository `/Users/arielsmoliar/Documents/ChatGPT/WebMCP` is on `main`,
  clean, and synchronized with `origin/main`.
- [ ] Latest expected repository commit and production revision are recorded
  before the run; do not assume the identifiers in this draft remain current.
- [ ] `https://captains-table-webmcp-1017459622661.us-east1.run.app/health`
  returns `{"status":"ok"}` and `/readyz` returns `{"status":"ready"}`.
- [ ] Production HTML contains the WebMCP Origin Trial token, and the trial has
  not passed its November 16, 2026 expiry date.
- [ ] ChatGPT is using GPT-5.6 Sol or GPT-5.6 Terra, is updated to the latest
  available desktop build, and is not operating in an Enterprise or Edu
  workspace. Official documentation states that GPT-5.6 Luna has site tools
  disabled and that availability also depends on rollout.
- [ ] The ChatGPT desktop app's built-in browser is the selected browser surface.
  Do not substitute the Chrome extension or another automation browser for the
  documented host surface.
- [ ] The operator opens a fresh cache-busted URL such as
  `/?build=origin-trial-1`. If local storage restores a completed session, use a
  fresh browser profile or clear only this demo's session through an approved,
  reversible method; never delete Firestore data.
- [ ] The page starts in `draft` state at revision 1 with no receipt and displays
  **WebMCP connected**.
- [ ] The production tab advertises a native host `webmcp` capability. Page-side
  `registerTool()` success alone does not satisfy this precondition.
- [ ] Ariel is present to perform the exact page-only authorization when the
  run reaches that gate.
- [ ] Evidence files contain no Origin Trial token, cookies, account details,
  session credentials, private browser data, or unrelated tab content.

## Risk and stop conditions

- **Risk:** Production workflow mutations persist in Firestore.
  **Containment:** Use exactly one fresh demo session and record its sanitized
  session identifier only if needed for reproducibility. Do not reuse or delete
  another session.
- **Risk:** The browser exposes the page API but the ChatGPT host cannot fetch or
  call the tools.
  **Containment:** Stop after recording the layered readiness result. Do not
  modify application code, reinstall software, or claim host discovery.
- **Risk:** A stale tool remains visible after a revision change.
  **Containment:** Do not invoke it as a normal workflow action. Record its
  presence, run only the built-in stale-capability probe, and stop before any
  improvised mutation.
- **Risk:** Authorization is performed by the agent or exposed as a tool.
  **Containment:** Stop immediately, preserve sanitized evidence, and classify
  the run as failed.
- **Risk:** Tool schemas, names, revision, epoch, visible state, or receipt
  disagree.
  **Containment:** Stop at the first contradiction. Do not retry with guessed
  inputs or repair production during the run.
- **Risk:** A mutation is accepted with the wrong expected revision, execution
  occurs without authorization, or a replay creates a second receipt.
  **Containment:** Stop immediately and do not perform further mutations.
- **Stop immediately if:** Another user's data appears; any secret or credential
  is exposed; `/health` or `/readyz` becomes unhealthy; the target origin,
  service, project, or revision differs from the recorded scope; browser control
  switches away from the approved Chrome profile; verification evidence is
  unavailable or contradictory; recovery would require an unapproved external
  or destructive action.

## Evidence plan

- Record sanitized UTC timestamps, Chrome and ChatGPT versions, production
  revision, page revision and plan fingerprint, page-expected tool names,
  host-observed tool names, capability epoch, tool-call result summaries,
  visible state transitions, receipt confirmation, protocol-probe results, and
  health/test outcomes.
- Store durable observations in `docs/protocol-observations.md`, session status
  and next steps in `HANDOFF.md`, and protocol or host capability requests in
  `docs/protocol-maintainer-feedback.md`.
- Prefer copied text and structured results over screenshots. If screenshots are
  needed for submission material, capture only the demo tab and review them for
  unrelated browser or account content before retention.
- Never record the Origin Trial token, cookies, authorization headers, account
  email, browser history, unrelated tabs, Firestore credentials, service-account
  material, or full private session payloads.
- Retain only evidence necessary to support the stated claims. A run failure is
  evidence; label it accurately rather than repeating mutations to obtain a
  preferred result.

## Procedure

Execution approval must be recorded before Phase 2. That approval covers creation
of one fresh Firestore session, bounded workflow mutations, persisted diagnostic
telemetry, and the Phase 7 safety probes. It does not replace Ariel's personal
exact-plan authorization in Phase 5 and does not authorize a public Git push,
deployment, or Devpost submission.

### Phase 1 — Read-only repository and production preflight

1. **Action:** In `/Users/arielsmoliar/Documents/ChatGPT/WebMCP`, inspect the
   current branch, working tree, latest commits, and configured remote.
   - **Classification:** `read-only`
   - **Expected result:** `main` is clean and synchronized with
     `origin/main`; the remote is `https://github.com/ArielSmoliar/WebMCP.git`.
   - **Verify:** Record `git status --short --branch` and the latest three
     one-line commits without changing files.
   - **If verification fails:** Stop. Resolve repository drift in a separate
     reviewed workflow.
   - **Approval required:** None.

2. **Action:** Query `/health`, `/readyz`, and the deployed HTML.
   - **Classification:** `read-only`
   - **Expected result:** Health and readiness are successful; the HTML includes
     an Origin Trial meta element without printing or storing its full token.
   - **Verify:** Record endpoint status bodies, response timestamps, and only the
     presence of the meta element.
   - **If verification fails:** Stop. Do not start a production session.
   - **Approval required:** None.

3. **Action:** Resolve the current Cloud Run revision serving 100% of traffic.
   - **Classification:** `read-only`
   - **Expected result:** One named revision serves all traffic for
     `captains-table-webmcp` in `us-east1`.
   - **Verify:** Compare it with `HANDOFF.md`; record any factual drift before
     execution.
   - **If verification fails:** Stop if the service, project, region, or traffic
     target differs from scope.
   - **Approval required:** None.

### Phase 2 — Browser and host capability gate

1. **Action:** Connect Codex to the ChatGPT desktop app's built-in browser, name
   the browser session, and open a fresh cache-busted production tab.
   - **Classification:** `production change`; loading a fresh session creates a
     durable Firestore record that this procedure does not delete
   - **Expected result:** The tab loads Captain's Table in `draft` state,
     revision 1, and displays **WebMCP connected**.
   - **Verify:** Read the visible title, URL, workflow state, revision, and
     connection label. Confirm no existing receipt was restored.
   - **If verification fails:** Stop. Do not clear broad browser data or delete
     server state. Prepare a separately approved session-isolation method.
   - **Approval required:** Gate 2. The user must approve the production
     verification run before this phase begins.

2. **Action:** Inspect the production tab's advertised capabilities.
   - **Classification:** `read-only`
   - **Expected result:** The tab advertises `webmcp` in addition to any ordinary
     browser capabilities.
   - **Verify:** Capture the sanitized capability names. Then obtain the native
     WebMCP handle and read its documentation before calling it.
   - **If verification fails:** Stop the run and record: browser API enabled,
     page registration accepted if visible, host capability unavailable. Do not
     proceed to page clicks as a substitute for host invocation.
   - **Approval required:** None.

### Phase 3 — Initial host discovery and observation

1. **Action:** Fetch the current page-defined tools through the native host
   WebMCP capability.
   - **Classification:** `read-only`
   - **Expected result:** At draft revision 1, the host observes exactly
     `inspect_decision`, `diagnose_plan`, and
     `report_observed_capabilities`, with their declared schemas.
   - **Verify:** Compare the host-observed set with the page's **Live
     capabilities** text. Record both sets and the current capability epoch.
   - **If verification fails:** Stop. Do not infer discovery from page telemetry.
   - **Approval required:** None.

2. **Action:** Call `report_observed_capabilities` with the exact host-observed
   names, current revision, and current epoch.
   - **Classification:** `production change` (diagnostic telemetry persists in
     Firestore; workflow revision must not advance)
   - **Expected result:** The result reports no missing or unexpected tools and
     `epoch_matches: true`; the page's Agent observation changes from **Not
     reported** without advancing the workflow revision.
   - **Verify:** Compare the returned registration metadata, visible page metric,
     and unchanged revision.
   - **If verification fails:** Stop and record the mismatch. Do not edit the
     reported list to force a match.
   - **Approval required:** Covered by the execution approval recorded before
     Phase 2.

3. **Action:** Call `inspect_decision`.
   - **Classification:** `read-only`
   - **Expected result:** The structured result matches the visible draft plan,
     revision, plan fingerprint, and registration epoch.
   - **Verify:** Compare result fields with the page; workflow revision remains
     unchanged.
   - **If verification fails:** Stop before mutation.
   - **Approval required:** None.

### Phase 4 — State-changing invocation and tool-set replacement

1. **Action:** Call `diagnose_plan` once through the native WebMCP handle.
   - **Classification:** `reversible` production mutation within the isolated
     demo session
   - **Expected result:** The shared page advances from `draft` to `conflict`,
     the visible revision increments by one, and the late-arrival conflict is
     shown.
   - **Verify:** Compare the call result, visible status, decision trail source
     `webmcp`, new revision, and new page capability epoch.
   - **If verification fails:** Stop. Do not retry the mutation blindly.
   - **Approval required:** The user's approval of this runbook execution is
     required before starting Phase 4.

2. **Action:** Fetch the tool set again using the host-supported refresh path.
   - **Classification:** `read-only`
   - **Expected result:** The host now observes exactly `inspect_decision`,
     `diagnose_plan`, `compare_repairs`, and
     `report_observed_capabilities` for the new epoch. This transition is
     additive; it does not yet prove removal behavior.
   - **Verify:** Record the new set, revision, epoch, and the absence of tools
     that should no longer be offered. Describe this only as host-observed
     replacement, not protocol-level removal acknowledgement.
   - **If verification fails:** Stop. Retain the old tool-set evidence and do not
     invoke an obsolete callback as a normal action.
   - **Approval required:** None.

3. **Action:** Report the replacement set with
   `report_observed_capabilities`, then continue the same fetch-report-verify
   pattern after each subsequent mutation.
   - **Classification:** `reversible` diagnostic telemetry
   - **Expected result:** Each observation matches the current page set and
     epoch without advancing revision.
   - **Verify:** No missing or unexpected tools; `epoch_matches: true`.
   - **If verification fails:** Stop at the first mismatch.
   - **Approval required:** None.

### Phase 5 — Repair selection and authorization boundary

1. **Action:** Call `compare_repairs`, refresh the host set, and verify the
   `options` state.
   - **Classification:** `reversible` production mutation within the isolated
     session
   - **Expected result:** Two bounded repairs appear. The host observes exactly
     `inspect_decision`, `diagnose_plan`, `compare_repairs`, `select_repair`,
     and `report_observed_capabilities` for the new revision.
   - **Verify:** Compare names, cost, attendance, tradeoff, revision, epoch, and
     decision trail.
   - **If verification fails:** Stop.
   - **Approval required:** Covered by the Phase 4 mutation gate.

2. **Action:** Call `select_repair` with `repair_id: "shift"`, refresh the host
   set, and call `prepare_authorization`.
   - **Classification:** `reversible` production mutation followed by a
     read-only focus action
   - **Expected result:** The plan enters `reviewed`, the roadmap session moves
     to the arrival-safe time, and the page focuses the exact-plan review without
     authorizing it.
   - **Verify:** Confirm the result, visible schedule, budget, revision, plan
     fingerprint, decision trail, and that authorization is still absent.
   - **If verification fails:** Stop.
   - **Approval required:** Covered by the Phase 4 mutation gate.

3. **Action:** Inspect the host-observed reviewed-state tools.
   - **Classification:** `read-only`
   - **Expected result:** The host observes exactly `inspect_decision`,
     `diagnose_plan`, `compare_repairs`, `select_repair`,
     `prepare_authorization`, and `report_observed_capabilities`;
     `execute_authorized_plan` and `authorize_plan` are absent.
   - **Verify:** Record exact host-observed names and report them through
     `report_observed_capabilities`.
   - **If verification fails:** Stop. The authorization boundary is not proven.
   - **Approval required:** None.

4. **Action:** Hand control to Ariel to review the exact revision, plan
   fingerprint, change, cost, and scope, then click **Authorize this version** on
   the page.
   - **Classification:** `reversible` material production state change; expires
     and is invalidated by later plan mutation
   - **Expected result:** The plan enters `authorized`; the human action appears
     in the decision trail; the page hides the authorization control and makes
     execution available.
   - **Verify:** Ariel confirms the exact values before clicking. After the
     click, Codex verifies the new revision, authorization expiry, trail source
     `human`, and host-observed tool set.
   - **If verification fails:** Stop. Do not authorize through scripts, WebMCP,
     DOM automation, or API calls.
   - **Approval required:** Gate 2. Ariel must personally approve and perform the
     page action at this step. Earlier approval to run the procedure does not
     replace this exact-plan decision.

### Phase 6 — Authorized execution and receipt recovery

1. **Action:** Confirm the authorized-state host set includes
   `execute_authorized_plan` and does not include `authorize_plan`; report the
   set through `report_observed_capabilities`.
   - **Classification:** `read-only` plus reversible diagnostic telemetry
   - **Expected result:** The host observes exactly `inspect_decision`,
     `diagnose_plan`, `select_repair`, `execute_authorized_plan`, and
     `report_observed_capabilities`; the set and epoch match the authorized page
     state.
   - **Verify:** Record exact names, revision, epoch, and zero mismatches.
   - **If verification fails:** Stop before execution.
   - **Approval required:** None.

2. **Action:** Generate one unique non-sensitive idempotency key and call
   `execute_authorized_plan` exactly once.
   - **Classification:** `irreversible within this procedure`; simulated
     external action with a durable production receipt that is not deleted or
     rolled back
   - **Expected result:** The page enters `completed`, shows one confirmation
     receipt, and records one WebMCP execution in the decision trail.
   - **Verify:** Compare returned and visible confirmation, revision, and receipt
     metadata. Confirm there is one receipt and that the completed-state host
     observes exactly `inspect_decision` and
     `report_observed_capabilities`.
   - **If verification fails:** Do not generate a new key or repeat execution.
     Reload first and attempt receipt recovery with the original session.
   - **Approval required:** Covered by Ariel's exact-plan authorization and the
     approved runbook execution; pause if the page describes any action beyond
     the documented simulated reservation.

3. **Action:** Reload the same production tab and session.
   - **Classification:** `read-only`
   - **Expected result:** The same confirmation receipt is restored from
     Firestore and `receipt_recovered` appears in protocol evidence.
   - **Verify:** Match the confirmation exactly; confirm no new execution event
     or receipt was created.
   - **If verification fails:** Stop. Do not create another session or execute
     again to conceal the failure.
   - **Approval required:** None.

### Phase 7 — Safety probes

1. **Action:** Use the page's **Run safety checks** control once after receipt
   recovery.
   - **Classification:** `production change`; diagnostic calls against the
     isolated session persist telemetry and include rejected mutation probes
     plus idempotent receipt replay
   - **Expected result:** Zero stale-capability mutations accepted, zero
     authorization bypasses, zero duplicate executions, and the original receipt
     remains unchanged.
   - **Verify:** Read the visible metrics and raw sanitized protocol trace.
   - **If verification fails:** Stop and preserve evidence. Do not rerun probes
     until the cause is reviewed.
   - **Approval required:** The user must approve executing this phase when the
     runbook is started because it sends bounded diagnostic requests to
     production.

2. **Action:** Confirm that any old tool absence is described only as the
   host-observed current set.
   - **Classification:** `read-only`
   - **Expected result:** Evidence makes no claim of protocol removal
     acknowledgement unless the host exposes a direct acknowledgement signal.
   - **Verify:** Review draft evidence language before saving it.
   - **If verification fails:** Correct the language; do not alter measured data.
   - **Approval required:** None.

### Phase 8 — Regression and health verification

1. **Action:** Run `node --check static/app.js` and the seven-test Python 3.13
   suite from the repository root.
   - **Classification:** `read-only` verification; tests may create temporary
     local files only
   - **Expected result:** JavaScript syntax passes and exactly seven Python tests
     pass. The known Starlette/httpx deprecation warning may remain.
   - **Verify:** Record command exit status and concise test summary.
   - **If verification fails:** Stop. Do not deploy or push.
   - **Approval required:** None.

2. **Action:** Recheck production `/health` and `/readyz`.
   - **Classification:** `read-only`
   - **Expected result:** Both remain healthy after the evidence run.
   - **Verify:** Record sanitized response bodies and UTC timestamp.
   - **If verification fails:** Stop, preserve evidence, and begin a separately
     approved incident assessment.
   - **Approval required:** None.

### Phase 9 — Evidence update and conditional change gate

1. **Action:** Update the three approved evidence documents with exact facts,
   uncertainties, versions, timestamps, tool sets, epochs, results, and
   deviations.
   - **Classification:** `reversible` repository documentation change
   - **Expected result:** The demonstrated score and claims match the evidence;
     maintainer feedback separates protocol, host-product, and documentation
     requests.
   - **Verify:** Run `git diff --check` and review the full documentation diff.
   - **If verification fails:** Correct the documentation before commit.
   - **Approval required:** None for factual evidence updates within this scope.

2. **Action:** Decide whether compatibility code changes are required.
   - **Classification:** `read-only` decision gate
   - **Expected result:** If no verified defect exists, make no code change and
     do not deploy. If a defect exists, stop this run and prepare a separate
     scoped change with tests, rollback, approval, and deployment verification.
   - **Verify:** State the observed defect and evidence, or state that no code
     change is justified.
   - **If verification fails:** Default to no code change.
   - **Approval required:** Explicit user approval is required before any new
     production deployment or materially different external change.

3. **Action:** Commit and push approved documentation after review.
   - **Classification:** `reversible` external repository change
   - **Expected result:** A focused commit reaches `origin/main`; the worktree is
     clean and synchronized.
   - **Verify:** Record commit ID, push result, and final `git status`.
   - **If verification fails:** Keep local changes intact and stop. Do not force
     push or rewrite history.
   - **Approval required:** The runbook execution approval must explicitly
     include pushing evidence to the public repository.

## Rollback

- **Trigger:** Wrong target origin or project; unexpected private data; unhealthy
  production; accepted stale mutation; authorization bypass; duplicate receipt;
  agent-driven authorization; incompatible tool schema; or any contradiction
  between host result, page state, and server-backed revision.
- **Decision owner:** Ariel Smoliar.
- **Actions:** Stop all further mutations. Preserve sanitized evidence. Release
  browser control without closing or altering unrelated tabs. Do not delete the
  production session or receipt. Revoke no tokens and change no infrastructure
  inside this run. Revert an unpushed documentation edit with a normal reviewed
  patch; if a documentation commit was pushed, correct it with a new commit rather
  than rewriting history. Handle any code or production rollback in a separate
  approved runbook using the last known healthy Cloud Run revision.
- **Verification:** Production health remains successful; existing sessions are
  readable; repository history is intact; no additional workflow events or
  receipts appear after the stop timestamp.
- **Limitations:** The simulated reservation receipt is intentionally durable and
  has no deletion rollback in this procedure. Browser or host rollout failures
  cannot be repaired by application rollback. Rollback does not convert a failed
  verification run into a passing one.

## Completion criteria

- [ ] The production tab advertises native host `webmcp` support.
- [ ] The host-observed initial tools and schemas exactly match the page set.
- [ ] `report_observed_capabilities` records matching revision and epoch without
  advancing workflow state.
- [ ] At least one host-originated WebMCP mutation advances the visible revision.
- [ ] Host-observed tool sets match every tested post-mutation state.
- [ ] Evidence calls this tool-set replacement, not removal acknowledgement.
- [ ] `authorize_plan` is absent in every host-observed set.
- [ ] Ariel personally authorizes the exact plan through the page UI.
- [ ] Execution produces exactly one receipt and the decision trail identifies
  WebMCP execution.
- [ ] Reload restores the identical receipt without duplicate execution.
- [ ] Safety probes show zero stale mutations accepted, zero authorization
  bypasses, and zero duplicate executions.
- [ ] JavaScript syntax and all seven Python tests pass.
- [ ] Production health and readiness remain successful.
- [ ] Evidence documents contain exact, sanitized observations and unresolved
  limitations.
- [ ] No architecture boundary changed and no unapproved deployment occurred.

## Communications

- **Start:** Ariel confirms the approved runbook version, exact production
  target, permission for bounded workflow mutations and safety probes, and
  whether evidence may be pushed to the public repository.
- **Failure:** Codex stops immediately and reports the failed phase, last verified
  state, sanitized evidence, production health, and safest next decision. No
  improvised repair is attempted.
- **Completion:** Codex reports the demonstrated claims, missing claims, receipt
  recovery result, safety metrics, tests, production health, documentation
  commit, and any maintainer-facing follow-up.

## Record

- **Started:** 2026-08-31T21:44:32Z
- **Completed:** 2026-08-31T21:45:33Z (stopped at mandatory Phase 2 gate)
- **Operator:** Codex; Ariel's exact-plan action was not reached
- **Approvals:** Ariel approved one fresh Firestore session, bounded workflow
  mutations, persisted diagnostics and safety probes, and local evidence updates.
  Public push, deployment, and Devpost submission were not approved.
- **Outcome:** Production preflight passed. Chrome `151.0.7922.174` loaded a
  fresh draft at `R1 · DA4F4EFF`; the page accepted 3/3 registrations at epoch
  `R1 · 94CBFBDC`, but the host advertised only `pageAssets`. The run stopped
  before host discovery, invocation, page workflow mutations, authorization,
  receipt creation, and safety probes. Post-stop JavaScript syntax, all seven
  Python 3.13 tests, and production health/readiness checks passed.
- **Follow-up gate:** At `2026-08-31T21:54:46Z`, an approved retry used the
  officially documented ChatGPT built-in browser. It restored completed session
  `R6 · 04C2F029`, accepted 2/2 page registrations at epoch
  `R6 · 19C3FFBF`, and advertised only `pageAssets`. The retry stopped before
  host discovery, invocation, page interaction, or additional production
  mutation. Local task metadata confirmed eligible model `gpt-5.6-sol` and a
  local Codex task rather than an Enterprise/Edu ChatGPT task, leaving
  rollout/session enablement as the remaining supported blocker.
- **Post-update continuation:** ChatGPT `26.825.51511` build `7377` advertised
  native `webmcp` after a full restart. At `2026-08-31T22:18:55Z`, the host
  discovered exactly the two completed-state tools, reported a matching 2/2 set
  for revision 6 and epoch `R6 · 19C3FFBF`, and invoked
  `inspect_decision` without advancing revision. Host discovery and read-only
  invocation are proven; the fresh state-changing journey remains pending.
- **Draft-tab retry:** At `2026-08-31T22:21:24Z`, the updated Chrome-control
  host reclaimed the exact existing production draft tab
  `/?build=origin-trial-1`. Its capability inventory contained only
  `pageAssets`; native `webmcp` was absent. The mandatory Phase 2 gate stopped
  the retry before clicks, host tool fetch, workflow mutation, authorization,
  safety probes, or creation of another Firestore session. This records layered
  readiness and is not evidence of host discovery or removal acknowledgement.
- **Compatibility deployment:** The missing fresh-session control was confirmed
  as an operability defect. `Start new session` was deployed in revision
  `captains-table-webmcp-00008-jsq`. An older cached HTML page then exposed an
  unchanged-asset-URL startup defect; backward-compatible initialization and
  versioned asset URLs rolled forward in revision
  `captains-table-webmcp-00009-z6j`, which serves 100% of traffic.
- **Successful continuation:** The built-in host completed session
  `UHxbrN-7PCXUU7kwmY2nCiNt` from R1 through R6. Exact capability epochs were
  `R1 · 94CBFBDC`, `R2 · 3E4C671A`, `R3 · 81C06189`,
  `R4 · 2E089520`, `R5 · BB341B1D`, and `R6 · 19C3FFBF` with tool counts
  3, 4, 5, 6, 5, and 2. Every diagnostic comparison matched exactly.
- **Authorization and execution:** Ariel personally authorized R4 plan
  `04C2F029` for the 12:15 shift, $7,380 total, 8 of 8 attendance, and one
  simulated reservation. The host executed exactly once with idempotency key
  `host-run-20260831-3419e643-6a7c-4455-821e-6eb68cea83da`, producing receipt
  `CT-79ECA1`. Reload recovered the same receipt in 58 ms.
- **Replacement and safety:** The R6 host inventory contained only inspection
  and diagnostic reporting. Calling `diagnose_plan` through the retained R5
  handle returned `WebMCP tool registration is stale. Call fetchTools() again.`
  Persisted probes recorded stale accepted `false`, authorization bypassed
  `false`, and duplicate receipt `false`. This proves host-observed replacement
  and stale rejection, not removal acknowledgement from `registerTool()`.
- **Deviations:** The repository was intentionally dirty after the approved
  pre-execution runbook and handoff corrections. No unplanned production action
  occurred.
- **Follow-up:** Preserve this completed evidence. Repeat only for a specific
  compatibility question and never infer host discovery or removal
  acknowledgement from page registration alone.
- **Next verification:** When ChatGPT host enablement changes or a documented
  supported host surface becomes available
