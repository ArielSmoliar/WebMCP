# WebMCP Protocol Observations

Maintainer-facing capability requests and their evidence status are tracked in
[`protocol-maintainer-feedback.md`](protocol-maintainer-feedback.md).

Captain's Table uses the imperative API because the workflow needs structured
results, conditional capabilities, and multiple state transitions on one page.

## What works well

- Page-scoped tools let ChatGPT operate the exact surface the human is viewing.
- An `AbortSignal` provides a workable lifecycle for state-dependent registration.
- JSON Schema gives the agent bounded choices without scraping presentation markup.
- Tool callbacks can reuse the same action controller as direct human controls.

## What the Protocol Lab measures

Every measurement is persisted with the session without advancing the workflow
revision. The evidence rail reports:

- registration acceptance and duration for each page tool;
- aggregate tool-set registration and abort-based removal at each revision;
- a deterministic capability epoch for the exact revision, plan hash, workflow
  state, and registered tool names;
- mutation-to-visible-render latency;
- rejection of a simulated callback retained from an obsolete capability epoch;
- execution attempts without authorization;
- idempotent replay against the original receipt key;
- receipt recovery after a page reload;
- the difference between the expected page tool set and the set explicitly
  reported by the agent through `report_observed_capabilities`.

The page does not label a successful `registerTool()` call as agent discovery.
Registration is page-measured. Discovery remains agent-reported because the
current API provides no discovery acknowledgement back to the page.

## Capability epochs

Dynamic registration creates a subtle race: aborting an old tool set asks the host
to remove it, but the page cannot observe when that removal becomes effective. A
naive callback can also read the newest page state when invoked, accidentally
giving an obsolete capability authority over a newer revision.

Captain's Table binds every callback to the revision that issued it. Mutation
callbacks submit that captured revision to the authoritative server; read-only UI
callbacks compare it before revealing or focusing state. Each registration set is
labeled `R{revision} · {fingerprint}`. The fingerprint is a deterministic diagnostic
identifier, not a cryptographic security claim.

The safety probe simulates invocation from the preceding epoch and records whether
the server accepted it. This tests the failure mode that abort-only lifecycle
management cannot itself prove safe.

Protocol events are diagnostic evidence, not cryptographic attestation of agent
identity. Timestamps are server-recorded, durations are page-measured, and the
agent-observation record is explicitly self-reported through a page tool.

## What a future version could improve

### Native structured output

The current callback resolves to a string. Native output schemas would make
results more reliable and remove one serialization layer.

### Standard authorization elicitation

WebMCP can expose or withhold a consequential tool, but applications need a
standard way to request scoped human approval without claiming that arbitrary
same-origin JavaScript proves physical human presence.

### Mutable capability annotations

Stateful products would benefit from updating availability and annotations without
aborting and re-registering definitions. Stable identity would also reduce races
around rapid tool changes.

### Invocation lifecycle events

Standard progress, cancellation, source, and completion events would let pages
render trustworthy evidence without wrapping every callback independently.

### Discovery acknowledgement

A page can measure that registration resolved, but not when an agent observes the
new capability or stops observing a removed one. A future lifecycle event or
registration-state API would let applications measure propagation latency and
capability-set accuracy without asking the agent to report its own view.

### Removal acknowledgement and invocation provenance

The page can send an abort signal but cannot confirm that a host has stopped
offering the old tool set. A future API should expose propagation acknowledgement
and attach an unforgeable registration identifier to each invocation. The current
demo compensates with revision-bound callbacks and reports the gap explicitly.

### Background lifecycle

Long-running work needs a defined relationship between tools, navigation,
service workers, and resumable execution.

These are observations from the implemented workflow, not requirements invented
outside the demo.

## 2026-08-31 target-browser observation

At `2026-08-31T21:02:59Z`, Codex selected its in-app ChatGPT browser for the
production URL and loaded Cloud Run revision 6. The restored production session
showed revision `R6`, plan hash fingerprint `04C2F029`, receipt `CT-2A9204`, and
the earlier persisted safety measurements: 0 stale mutations accepted, 0
authorization bypasses, 0 duplicate executions, 121 ms median visible-update
latency, and verified receipt recovery.

This browser did not expose `document.modelContext`; the interface correctly
entered Manual mode and displayed "This browser does not expose page tools."
The connected-browser inventory contained only the Codex in-app browser, and no
Captain's Table page tools appeared in the host tool catalog after navigation.
Consequently this run does **not** establish host discovery, invocation,
tool-set replacement, or removal acknowledgement. It also could not call
`report_observed_capabilities` or perform a new state-changing WebMCP invocation.
Those claims remain pending a ChatGPT browser build that enables WebMCP for this
session.

Official OpenAI site-tools documentation consulted after the stopped Chrome run
identifies the ChatGPT desktop app's built-in browser, not the Chrome extension,
as the supported host surface. It requires GPT-5.6 Sol or Terra, states that
Luna currently has WebMCP disabled, excludes Enterprise and Edu workspaces, and
notes that availability remains rollout-dependent. The next bounded gate is
therefore a fresh production tab in the built-in browser; Chrome extension
results remain valid negative evidence for that extension surface only.

A follow-up at `2026-08-31T21:06:03Z` narrowed the limitation. The installed
ChatGPT app is version `26.818.61809` (build `7019`) and its bundled browser
plugin documents the native `webmcp` capability with `fetchTools()` and tool
invocation support. The live production tab nevertheless advertised only the
`pageAssets` capability, and a direct capability lookup returned `Capability is
not available: webmcp`. This indicates that support is present in the installed
client bundle but is not enabled or exposed by the connected in-app-browser
backend for this session. Official OpenAI documentation currently provides no
public enablement switch or supported-build matrix for this capability.

At `2026-08-31T21:20:49Z`, the production origin was enrolled in Chrome's
WebMCP Origin Trial and Cloud Run revision
`captains-table-webmcp-00007-hft` deployed the resulting token. A cache-busted
Chrome 151 load then changed the page from Manual mode to "WebMCP connected."
The page measured 3/3 registrations accepted for `inspect_decision`,
`diagnose_plan`, and `report_observed_capabilities`, with capability epoch
`R1 · 94CBFBDC`.

The connected ChatGPT Chrome extension still advertised only the `pageAssets`
tab capability. Direct lookup of the host's native `webmcp` capability returned
`Capability is not available: webmcp`, including after waiting for propagation.
This proves page API enablement and page-side registration, but still does not
prove host discovery or invocation. It also demonstrates that browser API
availability, page registration acceptance, and agent-host WebMCP integration
are three distinct readiness layers that need separate diagnostics.

At `2026-08-31T21:45:33Z`, an explicitly approved execution of the host
verification runbook repeated the capability gate with a fresh production
session. `/health` returned `{"status":"ok"}`, `/readyz` returned
`{"status":"ready"}`, and Cloud Run revision
`captains-table-webmcp-00007-hft` served 100% of traffic. Chrome
`151.0.7922.174` loaded the new draft as `R1 · DA4F4EFF`; the page displayed
"WebMCP connected," measured 3/3 accepted registrations, exposed the page-side
set `inspect_decision`, `diagnose_plan`, and
`report_observed_capabilities`, and reported capability epoch
`R1 · 94CBFBDC`.

The production tab's host capability inventory contained only `pageAssets`.
Because native `webmcp` was absent, the run stopped at Phase 2 without fetching
host tools, invoking WebMCP, clicking a workflow control, running safety probes,
or asking for exact-plan authorization. The observed layers are therefore:
browser API enabled; page registrations accepted; host WebMCP capability not
advertised; host discovery, invocation, replacement, receipt recovery, and
stale-capability behavior not tested. No page-side signal is used as a
substitute for host discovery or removal acknowledgement.

Post-stop regression verification passed `node --check static/app.js` and all
seven tests under Python `3.13.15`; the known Starlette/httpx deprecation warning
remained. At `2026-08-31T21:46:41Z`, production `/health` and `/readyz` still
returned their expected healthy bodies. No compatibility code change or
deployment was justified by this result.

At `2026-08-31T21:54:46Z`, Ariel approved switching to the ChatGPT desktop
app's built-in browser and repeating the capability gate on the host surface
documented at <https://learn.chatgpt.com/docs/webmcp>. The built-in browser
restored the existing completed production session at `R6 · 04C2F029` with
receipt `CT-2A9204`; no fresh Firestore session was created. The page displayed
"WebMCP connected," accepted both completed-state registrations
(`inspect_decision` and `report_observed_capabilities`), and reported epoch
`R6 · 19C3FFBF`. The page's previously measured safety evidence remained
visible and unchanged.

The built-in production tab nevertheless advertised only `pageAssets`; native
host `webmcp` was absent. The run stopped before tool fetch or invocation and
did not click the page, rerun safety probes, alter the completed workflow, or
create another receipt. Because this is the officially documented surface, the
remaining explanations are host rollout, model eligibility, or workspace
eligibility. The browser-control surface does not expose which of those applies.

Read-only local task metadata subsequently identified the active model as
`gpt-5.6-sol`, which is eligible according to OpenAI's site-tools documentation.
The app identifies the task as local Codex rather than an Enterprise/Edu
ChatGPT task. This removes the two locally testable eligibility explanations and
leaves site-tools rollout or session enablement as the remaining supported
cause. No hidden feature flag, account mutation, or undocumented capability
override was attempted.

At `2026-08-31T22:18:55Z`, after updating and fully restarting ChatGPT, desktop
version `26.825.51511` (build `7377`) advertised native `webmcp` on the built-in
production tab. The host fetched exactly `inspect_decision` and
`report_observed_capabilities` for the restored completed state, including the
declared empty-object inspection schema and the diagnostic tool's tool-name,
revision, and optional epoch schema. The host origin and page URL matched the
production target.

The host called `report_observed_capabilities` with the exact two names,
revision 6, and epoch `R6 · 19C3FFBF`. The result contained no missing or
unexpected tools, returned `epoch_matches: true`, and left workflow revision 6
unchanged; the page visibly changed from **Not reported** to **2/2 reported**.
The host then called `inspect_decision`, which returned completed state,
revision 6, plan hash `04C2F029`, receipt `CT-2A9204`, and a non-stale matching
registration. This proves real host discovery and invocation. It does not yet
prove state-changing invocation, dynamic tool-set replacement, or removal
acknowledgement.

At `2026-08-31T22:21:24Z`, the updated Chrome-control host reclaimed the exact
existing production draft tab at `/?build=origin-trial-1`. The tab's advertised
capability inventory contained only `pageAssets`; native `webmcp` was absent.
The mandatory gate stopped the run before any page click, host tool fetch,
workflow mutation, authorization, safety probe, or new Firestore session. Taken
together with the built-in-browser result above, this is layered readiness:
page-level registration works in Chrome, native host discovery and read-only
invocation work in the updated built-in browser, but the Chrome extension does
not expose the native host capability for the reusable draft tab.

## Full built-in host lifecycle, 2026-08-31

The missing fresh-session control was a verified operability defect. A scoped
`Start new session` control created a new Firestore session and switched the
page without deleting or resetting its prior session. Cloud Run revision
`captains-table-webmcp-00008-jsq` first deployed the control. Testing an older
cached page then exposed an asset compatibility defect: old HTML had no control
while the unchanged script URL served code that assumed it existed, preventing
boot. An optional listener plus versioned script and polish URLs rolled forward
as revision `captains-table-webmcp-00009-z6j`, serving 100% of traffic.

The ChatGPT built-in host completed production session
`UHxbrN-7PCXUU7kwmY2nCiNt`. The host fetched and reported these exact sets:

- R1 `94CBFBDC`: `inspect_decision`, `diagnose_plan`,
  `report_observed_capabilities`.
- R2 `3E4C671A`: the R1 set plus `compare_repairs`.
- R3 `81C06189`: the R2 set plus `select_repair`.
- R4 `2E089520`: `inspect_decision`, `diagnose_plan`, `compare_repairs`,
  `select_repair`, `prepare_authorization`, `report_observed_capabilities`.
- R5 `BB341B1D`: `inspect_decision`, `diagnose_plan`, `select_repair`,
  `execute_authorized_plan`, `report_observed_capabilities`.
- R6 `19C3FFBF`: `inspect_decision`, `report_observed_capabilities`.

Each diagnostic report matched the page's expected revision and epoch with no
missing or unexpected names. WebMCP invocations visibly advanced diagnose,
comparison, selection, and execution. Ariel alone authorized R4 plan
`04C2F029`, moving the roadmap session to 12:15 at a total cost of $7,380 for
8 of 8 attendees and one simulated reservation. The page exposed no
`authorize_plan` WebMCP tool.

The R5 execution used idempotency key
`host-run-20260831-3419e643-6a7c-4455-821e-6eb68cea83da` and produced receipt
`CT-79ECA1` at R6. Reload recovered that exact receipt in 58 ms. Calling
`diagnose_plan` through the retained R5 host handle after completion returned
`WebMCP tool registration is stale. Call fetchTools() again.` The page's bounded
safety probes independently recorded stale acceptance `false` with
`stale_state`, authorization bypass `false` with `authorization_required`, and
receipt replay duplicate `false` with confirmation `CT-79ECA1`. These results
prove host-observed replacement and stale rejection. They do not treat
`registerTool()` resolution or the page's abort signal as host removal
acknowledgement.
