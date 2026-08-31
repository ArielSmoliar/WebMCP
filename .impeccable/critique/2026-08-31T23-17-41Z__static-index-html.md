---
target: static/index.html and local Captain's Table interface
total_score: 40
p0_count: 0
p1_count: 0
timestamp: 2026-08-31T23-17-41Z
slug: static-index-html
---
#### Design Health Score

| Category | Score | Result |
|---|---:|---|
| Workflow hierarchy | 5 | The active workflow owns the primary track; evidence cannot size its rows. |
| Stage progression | 5 | Inspect, Repair, Review, and Reserve expose current and completed state. |
| Cognitive load | 5 | Three proof signals remain visible; full protocol evidence is disclosed. |
| Status and feedback | 5 | Operations have specific labels, explicit race-sensitive locking, and accurate failure outcomes. |
| Plain-language clarity | 5 | Outcome labels bridge exact protocol terminology. |
| Completion hierarchy | 5 | The receipt precedes and visually outweighs historical evidence. |
| Responsive accessibility | 5 | Workflow framing precedes proof at narrow widths; independent evidence placement preserves semantics at wide widths. |
| Visual-system discipline | 5 | The instrument-table system remains restrained, product-specific, and free of named anti-patterns. |
| **Total** | **40/40** | **No remaining actionable static-design issues.** |

#### Five Priority Fixes

1. **Workflow-first hierarchy:** Pass. The workflow and evidence are structurally decoupled at wide widths.
2. **Three default proof signals:** Pass. Page connection, tool version, and strict agent-tool match are visible; raw evidence stays collapsed.
3. **All-stage journey:** Pass. A persistent four-step indicator maps every application state and exposes `aria-current` plus accessible completion labels.
4. **Scoped, specific feedback:** Pass. Initiating controls and the live region name the operation; failure paths no longer announce success.
5. **Plain-language protocol bridge and outcome-first completion:** Pass. Visible labels describe outcomes, while exact protocol terms remain available in technical evidence. The receipt is the completed-state focal point.

#### Anti-Patterns Verdict

Manual review passes. The receipt side stripe and fluid heading size found in the first rerun were removed. No gradient, glass, card-grid, hero-metric, side-stripe, or other named Impeccable absolute-ban pattern remains in the changed surface.

The deterministic detector remains unavailable: `detect.mjs --json static/index.html` exits 1 with `Error: bundled detector not found.` Automated counts are unknown, not zero.

#### Final Responsive Structure

The proof and technical evidence remain unique DOM nodes. Below 1100px, the decision heading and stage progression lead, the three proof signals follow before the action body, and full technical evidence follows the decision. At wide widths, the nodes move into an independently flowing sticky rail. Source-slot evidence is excluded from the wide first-paint layout until relocation, preventing a transient workflow shift without cloning IDs or content.

#### Verification Limits

The local server passed syntax and test validation, but the in-app browser could not reach the localhost listener because of browser isolation. Responsive conclusions are based on independent DOM/CSS review rather than a claimed screenshot or overlay.
