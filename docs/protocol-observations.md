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
- mutation-to-visible-render latency;
- intentionally stale revision rejection;
- execution attempts without authorization;
- idempotent replay against the original receipt key;
- receipt recovery after a page reload;
- the difference between the expected page tool set and the set explicitly
  reported by the agent through `report_observed_capabilities`.

The page does not label a successful `registerTool()` call as agent discovery.
Registration is page-measured. Discovery remains agent-reported because the
current API provides no discovery acknowledgement back to the page.

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

### Background lifecycle

Long-running work needs a defined relationship between tools, navigation,
service workers, and resumable execution.

These are observations from the implemented workflow, not requirements invented
outside the demo.
