# WebMCP Protocol Observations

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
