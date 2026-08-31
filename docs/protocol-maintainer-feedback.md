# WebMCP Maintainer Feedback Log

Updated: 2026-08-31

This document captures protocol and host-platform learnings from building and
testing Captain's Table. It is a working evidence log for a later review with
WebMCP maintainers, not a claim that every item belongs in the protocol itself.

## Reporting standard

Each entry should distinguish:

- the observed behavior and environment;
- the user or developer impact;
- the demo's current workaround;
- the smallest useful platform or protocol improvement;
- the evidence still needed before presenting the finding as confirmed.

Do not treat `registerTool()` resolution as host discovery or removal
acknowledgement. Do not generalize behavior from a browser that does not expose
WebMCP.

## Confirmed implementation learnings

### 1. Discovery acknowledgement

**Observed:** The page can observe that `registerTool()` resolved, but cannot
observe when the host or agent begins offering the tool.

**Impact:** Products cannot measure propagation latency or truthfully show that
an agent discovered a capability. Registration success and agent discovery are
different facts.

**Current workaround:** Captain's Table exposes
`report_observed_capabilities`, allowing the agent to self-report the names and
capability epoch it currently sees. The UI labels missing evidence as "Not
reported."

**Requested capability:** A host-originated registration/discovery lifecycle
event containing a stable registration identifier, observed tool names, and a
timestamp.

### 2. Removal acknowledgement

**Observed:** Aborting a registration set requests removal but does not tell the
page when the host has stopped offering those tools.

**Impact:** Dynamic applications cannot distinguish a removal request from
completed host propagation. Rapid state transitions can leave obsolete tools
visible temporarily.

**Current workaround:** Every callback is bound to the revision and capability
epoch that issued it. The server rejects stale mutations even if a host retains
an obsolete callback.

**Requested capability:** Explicit removal acknowledgement, ideally tied to the
same stable registration identifier and observable by both page and host.

### 3. Invocation provenance

**Observed:** A page callback does not receive an unforgeable host-issued
registration identity or invocation provenance.

**Impact:** Applications can log that a callback ran, but cannot strongly attest
which registered instance the host invoked or prove agent identity.

**Current workaround:** Captured revision, capability epoch, expected revision,
server timestamps, and source labels provide diagnostic evidence only.

**Requested capability:** Invocation metadata containing a host-issued
registration ID, invocation ID, selected tool version, and originating host
context, with clear trust semantics.

### 4. Stateful capability replacement

**Observed:** State-dependent tools are replaced by aborting and re-registering
the full set after each revision.

**Impact:** Full replacement increases propagation races and makes stable tool
identity difficult for agents and telemetry.

**Current workaround:** Deterministic capability epochs fingerprint the exact
revision, state, plan hash, and tool names.

**Requested capability:** Atomic tool-set replacement or mutable capability
definitions that preserve stable identity while updating availability, schema,
annotations, and descriptions.

### 5. Structured outputs

**Observed:** Tool callbacks return a serialized JSON string rather than a
protocol-native structured result validated against an output schema.

**Impact:** Agents must parse another serialization layer, and hosts cannot
validate or present fields consistently.

**Current workaround:** All results use one predictable JSON envelope containing
status, state, revision, summary, data, registration, and changed UI regions.

**Requested capability:** Native output schemas and structured result values,
including a standard way to identify affected page regions.

### 6. Human authorization semantics

**Observed:** Tool availability can signal that execution is possible, but the
protocol does not provide a standard exact-plan human authorization primitive.
Same-origin JavaScript is not proof of physical human presence.

**Impact:** Consequential workflows risk vague consent, overclaiming user
presence, or inventing incompatible authorization conventions.

**Current workaround:** Captain's Table deliberately exposes no authorization
tool. Only the page UI can authorize the exact server-computed plan hash;
subsequent mutation invalidates authorization.

**Requested capability:** A standard host-mediated approval flow that binds the
human decision to an exact action payload or digest, scope, expiry, and
single-use or replay semantics.

### 7. Invocation lifecycle and cancellation

**Observed:** The current callback surface lacks standard progress,
cancellation, completion, and retry lifecycle events.

**Impact:** Long-running tools cannot provide consistent progress or distinguish
host cancellation from application failure. Telemetry and recovery are
application-specific.

**Current workaround:** The page wraps actions with pending, success, and error
states and relies on idempotency keys for execution recovery.

**Requested capability:** Standard invocation IDs, cancellation signals,
progress events, completion status, retry intent, and idempotency guidance.

### 8. Capability availability diagnostics

**Observed:** ChatGPT app version `26.818.61809` build `7019` bundles WebMCP
support, while the connected in-app-browser production tab advertises only
`pageAssets`; direct lookup reports `Capability is not available: webmcp`.
Official documentation currently exposes no enablement switch or supported-host
matrix.

**Impact:** Builders cannot readily determine whether a failure is caused by
page compatibility, browser version, account rollout, host backend, or an
unsupported surface.

**Current workaround:** The demo feature-detects `document.modelContext`, enters
an honest Manual mode, and records `webmcp_unavailable` without claiming a
registration failure.

**Requested capability:** A documented support matrix and a safe diagnostic API
that reports availability plus a coarse reason such as unsupported browser,
disabled rollout, insecure context, policy restriction, or page error.

**Evidence status:** Confirmed for this client and session; broader rollout
behavior still needs comparison in a WebMCP-enabled ChatGPT browser.

### 9. Layered readiness diagnostics

**Observed:** After Origin Trial enrollment, Chrome 151 exposed the page API and
Captain's Table successfully registered its R1 tool set. The connected ChatGPT
Chrome extension still did not expose a native `webmcp` tab capability to the
agent controller.

**Impact:** A page may truthfully report successful WebMCP registration while
the agent host remains unable to discover or invoke its tools. A single
"supported" status obscures where readiness failed.

**Current workaround:** The demo reports page acceptance separately from agent
observation, and this evidence log records the browser and host layers
independently.

**Requested capability:** Standard diagnostics that distinguish at least:
browser API enabled, page registration accepted, host attached, tool set
observed, tool callable, and removal propagated. Each layer should provide a
coarse failure reason without leaking sensitive host state.

**Evidence status:** Confirmed on Chrome 151 with the WebMCP Origin Trial token,
ChatGPT browser extension connected, and Captain's Table revision 7.

## Further questions to test

- How quickly does a real host observe initial registration and replacement?
- Does the host ever invoke an obsolete callback after an abort signal?
- How are same-name replacements represented to the agent?
- What happens to tools across reload, navigation, backgrounding, and tab
  restoration?
- How are concurrent invocations ordered when each advances page revision?
- How do schema validation errors and callback exceptions appear to the agent?
- Does the host preserve tool handles across a capability-set change, and how is
  staleness surfaced?
- Which annotations are needed for read-only, mutating, consequential,
  idempotent, and human-approval-required tools?
- What accessibility and user-control requirements should hosts apply when an
  invocation changes visible page state?

## End-of-work maintainer package

Before sharing externally, review this log together and produce:

1. a concise executive summary ranked by user impact;
2. a reproducible environment and exact observation timeline;
3. minimal examples for each confirmed lifecycle gap;
4. a separation between protocol requests, host-product requests, and
   documentation requests;
5. explicit confidence and evidence status for every claim.
