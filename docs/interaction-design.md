# Interaction Design: The Shared Decision Surface

## Scene

A judge works at a desktop monitor in normal office light with ChatGPT's in-app
browser open beside the conversation. They have less than three minutes to
understand the product and need immediate proof that ChatGPT is operating the
page through structured WebMCP tools rather than simulated clicks.

This forces a light, warm-neutral working surface with high information density,
restrained color, and direct state transitions.

## Composition

```text
+---------------------------------------------------------------------+
| Captain's Table                  WebMCP connected       Plan 8F2C... |
+---------------------------------------------------------------------+
|                                                                     |
|  NEW YORK OFFSITE                    Decision trail / protocol       |
|  Oct 12–14 · 8 people                12:01 inspect_decision          |
|                                                                     |
|  [constraint strip: budget · arrival · required outcome]            |
|                                                                     |
|  AGENDA / ACTIVE DECISION            Current capability set          |
|  ┌──────────────────────────────┐    inspect_decision                |
|  │ Roadmap session             │    diagnose_plan                   |
|  │ conflict highlighted here   │    compare_repairs                 |
|  └──────────────────────────────┘                                    |
|                                                                     |
|  Inline comparison appears here after agent invocation               |
|                                                                     |
|  [human authorization boundary, inline and persistent when relevant] |
+---------------------------------------------------------------------+
```

The ChatGPT split pane at roughly 680–900px is the primary composition. The plan
and active decision occupy the full available width. A compact capability strip
near the header shows connection state and the current tool set; the complete
invocation history appears below the decision so it never competes with the work.

Only above roughly 1100px does the full evidence history become a subordinate side
rail. At narrower widths it remains a normal document section, never an overlay or
modal.

## Primary Demonstration

1. The page opens with one active plan, a compact “WebMCP connected” indicator,
   and a dismissible cue beside the active decision: “Ask ChatGPT to find what
   blocks this plan.” It includes one copyable prompt and a manual “Inspect
   conflict” action. Both use the real workflow. The cue retires after diagnosis
   and stays dismissed for the session.
2. The judge asks ChatGPT to identify the most important conflict.
3. `diagnose_plan` highlights the late-arrival conflict and adds one evidence event.
4. The judge asks for repairs under a $300 budget increase.
5. `compare_repairs` inserts two aligned alternatives beneath the affected agenda
   item. Cost, attendance, timing, and tradeoff differences use stable columns.
6. ChatGPT selects the arrival-safe option through `select_repair`. The exact plan
   hash changes and the decision trail records the mutation.
7. ChatGPT asks to proceed. `prepare_authorization` scrolls/focuses the inline
   authorization boundary but cannot approve it.
8. The human adjusts one attendee's arrival time through an inline control before
   authorizing. The plan hash changes, the previous preparation is marked stale,
   findings recalculate, and execution remains unavailable.
9. The human reviews the new diff and authorizes through the page.
10. `execute_authorized_plan` becomes available. ChatGPT invokes it and the surface
    resolves into a confirmation receipt with an idempotent replay indicator.

The first value moment is step 3: the exact conflict changes in place and the
decision trail identifies ChatGPT's structured action. A judge should reach it in
under 30 seconds without documentation.

## Signature Behaviors

### Causal focus

Every WebMCP invocation briefly marks the exact region it changed, using outline,
background tint, and a text announcement. The treatment lasts long enough to
connect cause and effect and then settles into the normal state.

### Capability mirror

The evidence rail shows only the currently registered tools. When authorization
becomes valid, `execute_authorized_plan` appears. When the plan changes, it
disappears immediately and the page names why.

The product surface describes capability changes in task language first:
“Execution is now available” or “Execution paused because the plan changed.” Exact
tool names appear only in the subordinate Technical evidence disclosure. Dynamic
registration is labeled “Live capabilities.” Compatibility mode is labeled
“Stable compatibility mode,” with copy explaining that tools remain discoverable
while the application enforces their allowed states.

### Exact-plan review

Authorization is inline, never a modal. It shows the changed fields, total cost,
plan hash, scope, and expiry. The human control is visually distinct from agent
actions without theatrical warning styling.

The visible review is chunked into three questions: “What changes?”, “What does it
cost?”, and “What are you authorizing?” Plan hash, exact scope, revision, and
absolute expiry sit under “Technical details.” The primary trust statement is:
“You are approving exactly this version.”

- **Ready for review:** ChatGPT prepared the exact change; no permission exists.
- **Authorized:** You approved this exact version until the displayed local time.
- **Review again:** The plan changed, so the previous authorization no longer applies.

If authorization expires while the judge is reading, the review remains visible,
focus does not move, and the action becomes “Review and authorize again.” Expiry is
shown as an absolute time in the browser's local timezone; no countdown is used.

### Revision calibration

A compact revision seal is the protocol-native signature. It combines a short plan
identity with a two-part calibration mark. A verified mutation advances one notch
and leaves the previous mark in the trail. A no-op or rejected action never
advances it. The newest notch uses Mineral Signal briefly, then returns to graphite.
Text always names the revision change, so geometry and color are supplementary.

The seal is not a pill, status badge, terminal treatment, or oversized metric. It
appears once in the header and as a smaller historical mark in the trail.

### Revert and cancellation

Before authorization, the latest successful plan mutation exposes one localized
“Revert last change” action in the decision trail. Revert creates a new revision
and hash, records which mutation it reversed, and never resurrects authorization.
After authorization or execution it is unavailable and the interface explains why.

Pending comparisons and selections expose “Cancel request” while the browser can
safely abort the client request. Cancellation never promises the server did not
finish. The client refreshes authoritative state and reports either “Request
canceled” or “The change completed before cancellation.”

“Start over” is secondary and lives in Technical evidence. Its confirmation says:
“Start a fresh scenario? This session will remain unchanged.”

### Protocol frontier

A collapsed section after completion lists observations grounded in the demonstrated
workflow: native output schemas, standardized approval elicitation, progress,
capability annotations, and background/service-worker lifecycle. It is evidence
from the product, not a speculative feature list in the main workflow.

## Content Hierarchy

1. Current decision and blocking state.
2. Exact effect of the latest agent or human action.
3. Feasible alternatives and tradeoffs.
4. Human authorization requirement.
5. Execution receipt and recovery state.
6. Protocol evidence and future observations.

Product language always precedes protocol evidence. The main surface uses
“conflict,” “comparison,” “plan changed,” “review,” and “reservation.” The evidence
layer may use `diagnose_plan`, revision, hash, invocation ID, and idempotency.

## Split-Pane Adaptation

The layout adapts by information priority, not by shrinking a desktop composition.

### 680–759px

- One column; active decision, latest effect, and next action precede evidence.
- The header contains product name, connection state, and revision seal only.
- Constraints wrap as a definition list, not a horizontal chip strip.
- Repair comparison uses a semantic table inside a labeled horizontal scroll
  region. Attributes are rows, alternatives are columns, and the first column is
  sticky. A text hint appears only when overflow exists.
- Authorization becomes the active region when required. The comparison moves
  under “Review alternatives.”
- Capabilities, history, and frontier observations appear below the work.

### 760–1099px

- One primary column with a compact two-row header.
- The comparison retains stable row alignment inside the content column.
- Latest evidence is summarized near the change; full history remains below.

### 1100px and wider

- The active decision remains the larger column.
- A subordinate evidence rail may remain visible but never equals the decision's
  visual weight.

At all widths, containers permit 200% zoom and 40% copy expansion. Interactive
targets are at least 44 by 44 CSS pixels when touch input is present. Logical CSS
properties support bidirectional layout even though demo copy is English.

## Focus and Announcements

- Remote agent mutations never steal keyboard focus. Routine progress uses a polite
  announcement; blocked, invalidated, and completed consequential states are assertive.
- After diagnosis, a persistent “Jump to conflict” link points to the affected region.
- Opening Technical evidence moves focus to its heading; closing it restores focus
  to the disclosure control.
- The comparison has a caption, column headers, row headers, keyboard-reachable
  overflow, and remains understandable without spatial position.
- Causal highlighting persists for at least three seconds. Reduced motion removes
  transforms, while the permanent trail entry carries the same information.
- Authorization expiry imposes no time limit. The preserved plan can be reviewed
  and authorized again.

## Recovery Copy

| State | Primary message | Next action |
|---|---|---|
| Stale page | “This plan changed elsewhere. We refreshed the latest version.” | “Review latest plan” |
| Authorization invalidated | “The arrival time changed. Review this version again before execution.” | “Review changes” |
| Execution uncertain | “We did not receive confirmation. Check the existing reservation before trying again.” | “Check reservation” |
| Receipt recovered | “Reservation found. No duplicate action was created.” | “View receipt” |
| WebMCP unavailable | “This browser cannot expose page tools to ChatGPT.” | “Continue manually” and setup help |
| Registration rejected | “ChatGPT could not access this page's tools. The plan is still usable here.” | “Continue manually” |
| Canceled locally | “Request canceled.” or “The change completed before cancellation.” | “Review current plan” |

## Visual Direction

- Restrained warm-neutral light theme with mineral blue-green active states.
- One technical-humanist sans; mono only for tools, hashes, revisions, and times.
- Tonal grouping and rules, not a grid of repeated cards.
- Thin structural dividers and large whitespace changes to mark workflow stages.
- Motion limited to 160–220ms opacity and transform transitions using ease-out-quint.
- No gradient text, glass surfaces, neon, colored side stripes, or nested cards.

## Required States

- WebMCP connecting, connected, unavailable, and registration rejected.
- No diagnosis, conflict focused, alternatives loading, and alternatives ready.
- Selection pending, selected, and rejected as stale.
- Authorization required, prepared, valid, expired, and invalidated.
- Execution pending, completed, uncertain, and recovered.
- Empty evidence history and populated evidence history.
- First-run cue visible, dismissed, and completed.
- Revert available, pending, completed, unavailable, and rejected as stale.
- Cancellation before and after server completion.
- Two-tab conflict, refresh during authorization, and compatibility fallback.
- Long comparison copy, 200% zoom, keyboard-only use, and live-region behavior.

## Design Evaluation Checklist

- Can a judge identify the active decision in under five seconds?
- Is the page useful without reading the full evidence history?
- Does every agent action produce an observable, localized change?
- Can the judge distinguish agent-permitted and human-only actions without copy?
- Does the dynamic tool set teach WebMCP rather than merely report it?
- Are comparison columns stable when content length changes?
- Is the authorization boundary understandable without a modal?
- Do stale, blocked, and successful outcomes remain distinct without color?
- Does the 680–900px ChatGPT split-pane composition feel primary rather than compressed?
- Does the interface still work with keyboard input and reduced motion?
- Does any region resemble a generic AI dashboard or chatbot transcript?
