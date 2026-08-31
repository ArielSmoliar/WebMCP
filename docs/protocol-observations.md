# WebMCP Protocol Observations

Captain's Table uses the imperative API because the workflow needs structured
results, conditional capabilities, and multiple state transitions on one page.

## What works well

- Page-scoped tools let ChatGPT operate the exact surface the human is viewing.
- An `AbortSignal` provides a workable lifecycle for state-dependent registration.
- JSON Schema gives the agent bounded choices without scraping presentation markup.
- Tool callbacks can reuse the same action controller as direct human controls.

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

### Background lifecycle

Long-running work needs a defined relationship between tools, navigation,
service workers, and resumable execution.

These are observations from the implemented workflow, not requirements invented
outside the demo.
