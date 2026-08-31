---
target: docs/interaction-design.md
total_score: 31
p0_count: 0
p1_count: 3
timestamp: 2026-08-31T17-23-19Z
slug: docs-interaction-design-md
---
# Impeccable Design Critique: Shared Decision Surface

## Design Health Score

This is a pre-implementation score. It evaluates the interaction specification and design system, not a rendered interface.

| # | Heuristic | Score | Key issue |
|---|---|---:|---|
| 1 | Visibility of System Status | 4 | State coverage and localized causal feedback are excellent on paper; timing and announcements remain unverified. |
| 2 | Match System / Real World | 3 | The offsite decision is natural, but protocol terms can leak into the judge's task. |
| 3 | User Control and Freedom | 2 | Human editing and restart exist; undo, revert, and pending-action cancellation are not designed. |
| 4 | Consistency and Standards | 4 | Shared controller, stable vocabulary, tokens, and inline authorization establish a coherent system. |
| 5 | Error Prevention | 4 | Revisions, exact-plan authorization, bounded inputs, tool removal, and idempotency prevent consequential mistakes. |
| 6 | Recognition Rather Than Recall | 3 | Work and evidence are co-located, but tool names and collapsed history may demand protocol knowledge. |
| 7 | Flexibility and Efficiency | 2 | Agent and manual routes exist, but accelerators, focus order, and a fast repeat path are unspecified. |
| 8 | Aesthetic and Minimalist Design | 3 | The hierarchy is disciplined; the 680px composition could still become a dense status cockpit. |
| 9 | Error Recovery | 4 | Failures, authoritative refresh, preserved state, and recovery actions are unusually complete in the plan. |
| 10 | Help and Documentation | 2 | Browser guidance exists, but the first action and contextual explanations are missing. |
| **Total** |  | **31/40** | **Good foundation; implementation is not yet visually verified.** |

## Anti-Patterns Verdict

**LLM assessment:** The interaction concept passes the AI-slop test. A shared mutable surface, conditional capabilities, stale-plan invalidation, and receipt recovery are specific and behavior-led. The visual direction remains at risk: warm off-white, restrained blue-green, Inter, thin rules, and Linear/Stripe references can land in the familiar tasteful-AI-tool lane. The implementation needs one protocol-native visual grammar, not more decoration.

**Deterministic scan:** A mandatory scan was attempted against the repository. It exited 1 with `Error: bundled detector not found.` The expected detector implementation is absent from both locations checked by the wrapper, so no JSON counts, rules, locations, or false positives were available. An exhaustive inventory found no HTML, JSX, TSX, Vue, Svelte, Astro, MDX, runtime configuration, or other viewable UI implementation.

**Visual overlays:** No reliable user-visible overlay exists. The stable target is a Markdown interaction plan and there is no page runtime to inspect or inject.

## Overall Impression

This is a strong, unusually rigorous interaction thesis. Its best idea is visible authority: the agent can prepare and execute only when state permits, while the human remains the sole authorization path. The largest opportunity is to make that thesis self-evident in the first five seconds without asking judges to interpret a protocol log.

## What's Working

- Authority is embodied in behavior: authorization is absent from the tool surface, execution appears only when valid, and a human edit invalidates the prepared state.
- Cause and effect are designed as product behavior: human and WebMCP routes converge on one controller, mutations identify changed regions, and execution can recover the same receipt.
- The split-pane constraint shapes the design honestly: the active decision stays primary and evidence earns a side rail only at wider widths.

## Cognitive Load and Emotional Journey

Seven of eight cognitive-load checks pass in the plan: single focus, grouping, hierarchy, one decision at a time, minimal choices, recognition support, and progressive disclosure. Chunking is the exception. The authorization boundary presents changed fields, cost, hash, scope, and expiry together, while the full evidence record contains eight metadata fields. No decision exposes more than four options, but these non-decision clusters can overload the narrow pane.

The intended journey is compelling: skepticism at open, orientation at diagnosis, analytical confidence during comparison, healthy caution at authorization, increased trust when an edit invalidates stale preparation, and relief at a concrete receipt. The emotional valley is the invalidation moment. Preserved work and one precise explanation must make it feel protective rather than punitive.

## Priority Issues

### P1: The first five seconds lack an obvious on-page action

**Why it matters:** The golden journey begins in ChatGPT, so the page can initially look like a static plan. A judge should not need narration to discover the first proof point.

**Fix:** Add a compact first-run cue beside the active decision: “Ask ChatGPT to find what blocks this plan,” with one copyable example and a manual equivalent. Retire it after diagnosis.

**Suggested command:** `impeccable onboard`, then `impeccable clarify`.

### P1: Undo and cancellation are underspecified

**Why it matters:** Repair selection and arrival editing mutate the exact plan. Without a local escape path, visible authority feels one-sided.

**Fix:** Add a localized “Revert last change” before authorization; cancel safe in-flight comparisons or selections; explain that Start over creates a fresh session.

**Suggested command:** `impeccable harden`.

### P1: Protocol vocabulary can displace decision vocabulary

**Why it matters:** Tool names, hashes, revisions, and idempotency prove technical depth but force first-time judges to translate diagnostics while making a decision.

**Fix:** Lead with task language such as “Plan changed; review required.” Put exact tool names, hashes, and revisions under “Technical evidence,” and explain capability changes in one sentence.

**Suggested command:** `impeccable clarify`, then `impeccable distill`.

### P2: The narrow comparison pattern is asserted, not resolved

**Why it matters:** Two alternatives across cost, attendance, timing, and tradeoffs can become unreadable at 680px or compete with status and evidence.

**Fix:** Specify a row-aligned matrix with sticky attribute labels, alternatives as columns, controlled labeled horizontal overflow, and evidence below the decision.

**Suggested command:** `impeccable adapt`, followed by implementation-time `impeccable audit`.

### P2: The visual identity lacks a singular protocol-native signature

**Why it matters:** The interaction is distinctive, but the token system can still render as a polished generic AI product.

**Fix:** Prototype a restrained “instrument calibration” revision seal whose geometry changes only on verified mutation and whose previous state remains in the trail. Reject badge, terminal, and decorative variants.

**Suggested command:** `impeccable bolder`, then `impeccable quieter`.

## Persona Red Flags

**Jordan, first-time user:** There is no explicit first action. “Capability,” “hash,” “stale,” and snake-case tool names can resemble developer diagnostics. Capability disappearance may look like a defect, and contextual help plus undo are not specified.

**Sam, accessibility-dependent user:** Keyboard use, focus, announcements, reduced motion, and color independence are promised, but live-region priority, focus destination after remote mutations, disclosure focus restoration, comparison semantics, 200% zoom, and expiry accommodation remain undefined. A transient tint cannot carry causal meaning.

**Riley, stress tester:** Backend behavior is thorough, but the visible treatment of two tabs, refresh during authorization, long comparison content, dynamic-to-compatibility fallback, and uncertain execution is not compositionally specified.

**Morgan, hackathon judge:** Morgan has under three minutes, shifts attention between ChatGPT and the page, and is skeptical of staged demos. Requiring the evidence log to prove authenticity, hiding stale recovery behind narration, or presenting compatibility mode as dynamic registration would weaken trust.

## Minor Observations

- Dynamic registration and compatibility mode need visibly different, honest labels.
- “Prepared” and “valid” authorization require distinct language and controls, not nearly identical status pills.
- Expiry needs a timezone, an accessible time treatment, and behavior for expiration while reading.
- Keep protocol-frontier observations collapsed and after the receipt.
- Uppercase, letter-spaced labels may slow scanning in a dense pane.
- Font weights 430, 620, and 650 require the variable Inter asset or disciplined fallback weights.
- Contrast, 44px targets, stable comparison layout, and component states remain implementation-dependent.

## Questions to Consider

1. If the evidence history vanished, would the changed decision surface still prove that WebMCP operated it?
2. Should capability registration read primarily as user guidance or protocol demonstration?
3. Can “you are approving exactly this version” carry the trust story, with the hash available only as evidence?
4. What single sentence turns stale authorization after a human edit from frustration into increased trust?
5. Is the memorable screenshot a distinctive interaction state, or merely a tasteful interface?
