---
target: static/index.html and deployed Captain’s Table interface
total_score: 29
p0_count: 0
p1_count: 2
timestamp: 2026-08-31T23-04-57Z
slug: static-index-html
---
#### Design Health Score

| # | Heuristic | Score | Key Issue |
|---|---|---:|---|
| 1 | Visibility of System Status | 3 | Strong connection, revision, state, receipt, latency, and trail; busy feedback is nonspecific. |
| 2 | Match System / Real World | 3 | The offsite plan is concrete, but protocol vocabulary needs a plain-language bridge. |
| 3 | User Control and Freedom | 2 | Revert and Start new session help, but finality and post-authorization recovery are underexplained. |
| 4 | Consistency and Standards | 4 | Typography, controls, borders, spacing, and state language are cohesive. |
| 5 | Error Prevention | 4 | Exact-plan authorization, revision binding, stale rejection, and idempotency are excellent. |
| 6 | Recognition Rather Than Recall | 3 | Context stays visible, but the relationship between ChatGPT and page actions must be inferred. |
| 7 | Flexibility and Efficiency | 3 | Manual and WebMCP paths coexist; explicit power-user accelerators are limited. |
| 8 | Aesthetic and Minimalist Design | 2 | Styling is restrained, but expanded technical evidence competes with the primary decision. |
| 9 | Error Recovery | 3 | Error copy is clear; placement and recovery controls are uneven across failure types. |
| 10 | Help and Documentation | 2 | First-run guidance exists, but stages and protocol terms lack concise contextual explanation. |
| **Total** | | **29/40** | **Good foundation; hierarchy and comprehension need one more pass.** |

#### Anti-Patterns Verdict

**LLM assessment:** Pass. The interface avoids generic AI-dashboard tells: no dark neon console, chatbot transcript, gradient decoration, glass cards, oversized metrics, or interchangeable card grid. Warm instrument neutrals, sparse mineral signal, the revision seal, and visible authority boundaries feel intentional. The serious regression is layout rather than aesthetic: the wide-screen evidence rail can make protocol telemetry appear more important than the decision.

**Deterministic scan:** Unavailable. `detect.mjs --json static/index.html` exited 1 with `Error: bundled detector not found.` Both expected detector-engine paths were absent, so issue counts and rule locations are unknown, not zero. No false positives could be assessed.

**Visual overlays:** No reliable user-visible overlay exists. Mutable injection failed because the browser evaluation surface is read-only. The live server and overlay injection were correctly skipped. A fresh-tab screenshot and DOM inspection were used as fallback evidence.

#### Overall Impression

Captain's Table looks precise, authored, and trustworthy. Its strongest product idea, a shared decision surface with human-only authority, is genuinely visible in the workflow. The biggest opportunity is to make the user's outcome dominate the first viewport and let protocol evidence support it, not compete with it.

#### What's Working

1. **Authority is structurally visible.** Inspection, repair, page-only authorization, execution, receipt, and recovery are separate states rather than explanatory claims.
2. **The visual system earns trust.** Warm neutrals, sparse signal color, flat borders, squared controls, and the revision motif are distinctive without decoration or terminal cosplay.
3. **The receipt and audit trail feel real.** Source attribution, revision, confirmation, stale-call rejection, and recovery evidence make this substantially more credible than a staged demo.

#### Priority Issues

##### [P1] The evidence rail pushes the active decision below the fold

**Why it matters:** At 1280×720, technical evidence stretches the opening grid while the active decision begins roughly 486 px down. The design says the decision is primary, but the layout makes telemetry primary.

**Fix:** Decouple decision positioning from evidence-rail height. Keep the brief compact, start the decision immediately beneath it, and initially expose only connection, revision, and two or three proof signals. Validate at 680–900 px and 1280×720.

**Suggested command:** `impeccable layout`

##### [P1] Completion foregrounds implementation proof instead of the outcome

**Why it matters:** The reservation receipt is the emotional and informational climax, yet it sits below the fold while protocol metrics and safety checks are immediately visible.

**Fix:** Give completed state its own hierarchy. Bring the receipt into the first viewport, add a compact verified-execution summary, and keep full metrics and raw traces behind disclosure.

**Suggested command:** `impeccable distill`

##### [P2] Workflow state is legible but the journey is not

**Why it matters:** Current labels are clear, but first-timers cannot see the overall progression or what remains. They must infer how ChatGPT, page controls, revisions, authorization, and execution connect.

**Fix:** Add a compact textual stage indicator such as `Inspect → Repair → Review → Reserve`, plus one sentence explaining that ChatGPT and the page operate the same live plan.

**Suggested command:** `impeccable clarify`

##### [P2] Busy feedback is global and nonspecific

**Why it matters:** Every button dims during any request, with no operation label. Users cannot tell whether the page is diagnosing, authorizing, registering tools, or reserving.

**Fix:** Disable only conflicting controls, change the initiating label to the active operation, and pair `aria-busy` with visible status text while preserving safe exits.

**Suggested command:** `impeccable harden`

##### [P2] Protocol vocabulary lacks outcome language

**Why it matters:** `Capability epoch`, `agent observation`, and `page-accepted` raise translation cost for judges and non-platform users.

**Fix:** Pair exact terms with outcome labels such as `Tool version`, `Agent saw current tools`, `Old calls blocked`, and `Duplicates prevented`. Keep protocol terms in technical details.

**Suggested command:** `impeccable clarify`

#### Persona Red Flags

**Jordan, first-timer:** The opening proposition explains the category rather than the first action. The ChatGPT-to-page causal link and the full workflow must be inferred. Automatically open evidence introduces jargon before Jordan reaches the decision.

**Alex, power user:** The agent path is a strong accelerator, but below-fold decisions, no explicit keyboard accelerators, and global busy disabling create avoidable presentation latency.

**Sam, accessibility-dependent:** Semantic headings, native controls, skip link, visible focus, live regions, tables, and reduced-motion support are strong. However, visual and DOM reading order diverge at wide widths, dynamic announcements omit the newly available primary action, and global disabling can temporarily remove every control from keyboard navigation without a specific progress message.

#### Minor Observations

- `Start new session` can read as secondary navigation rather than a consequential context switch.
- Original conflict and final receipt containers have similar visual weight.
- `No duplicate action was created if this receipt was recovered` is accurate but awkward; `Recovered receipts never create a duplicate reservation` is clearer.
- The protocol method paragraph is dense for the narrow rail.
- The browser evidence pass observed a large amount of unused space at a 2048 px capture, reinforcing the need to test wide composition deliberately.

#### Questions to Consider

- If the protocol works perfectly, should users see eight metrics before the decision?
- Which screenshot should judges remember: the protocol run, or a human-authorized plan completed by an agent?
- Could the revision seal carry enough proof that the evidence rail becomes quieter?
- After reservation, should the product feel final, branchable, or amendable through a new authorization cycle?
