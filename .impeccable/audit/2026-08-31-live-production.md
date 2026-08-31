# Impeccable Audit: Live Production Interface

Target: `https://captains-table-webmcp-pgg2be7x2a-ue.a.run.app`

Quality bar: flagship hackathon demo and reusable reference product.

## Audit Health Score

| # | Dimension | Score | Key finding |
|---|---|---:|---|
| 1 | Accessibility | 3 | Strong semantics and focus treatment; async errors are not announced visibly. |
| 2 | Performance | 4 | Dependency-free client, no media payload, bounded state rendering. |
| 3 | Responsive Design | 3 | Narrow judge pane is strong; wide desktop underuses available space. |
| 4 | Theming | 3 | OKLCH tokens are consistent; semantic error tokens are missing from CSS. |
| 5 | Anti-Patterns | 4 | No gradients, glass, generic card grid, or chatbot shell. |
| **Total** | | **17/20** | **Good** |

## Anti-Patterns Verdict

Pass. The interface is restrained and intentionally product-like. The revision
calibration motif, shared decision surface, and page-only authorization boundary
make it specific. It does not read as a generic AI dashboard.

## Executive Summary

- Issues: 0 P0, 2 P1, 2 P2.
- Preserve the quiet instrument-table hierarchy and direct manipulation model.
- Fix async action feedback and recovery before submission recording.
- Use the designed evidence rail on wide screens so technical depth is visible to
  judges without weakening the focused split-pane layout.

## Detailed Findings

### [P1] Async actions have no durable loading or error state

- Location: `static/app.js`, `action`, event listeners, and `boot`.
- Category: Accessibility / interaction.
- Impact: A network, Firestore, stale-revision, or authorization error becomes an
  unhandled promise. The user receives no recovery instruction and can click the
  same action repeatedly while it is pending.
- Standard: WCAG 3.3.1 Error Identification and 4.1.3 Status Messages.
- Recommendation: Add one inline `role=alert` status, disable controls while a
  mutation is pending, and translate known server errors into actionable copy.
- Suggested command: `impeccable harden`.

### [P1] Initial load failure is reduced to a header label

- Location: `static/app.js`, `boot().catch`.
- Category: Accessibility / edge-case recovery.
- Impact: A failed boot leaves controls visible but unusable, with no retry path.
- Recommendation: Reuse the inline error surface and expose a reload action or
  explicit refresh instruction.
- Suggested command: `impeccable harden`.

### [P2] Wide screens hide technical depth below unused space

- Location: `static/styles.css`, `main`; live desktop screenshot.
- Category: Responsive design / information architecture.
- Impact: On a full browser, the primary column remains narrow while the protocol
  evidence sits below it. Judges can miss the non-trivial tool and revision trail.
- Recommendation: At 1100 px and wider, place Technical evidence in a restrained
  sticky rail, as already permitted by `DESIGN.md`.
- Suggested command: `impeccable layout`.

### [P2] Secondary and disclosure controls have incomplete states

- Location: `static/styles.css`, `static/workflow.css`.
- Category: Accessibility / polish.
- Impact: Primary, secondary, summary, and text controls do not share a complete
  hover, active, and disabled vocabulary.
- Recommendation: Add token-aligned states without decorative motion.
- Suggested command: `impeccable polish`.

## Systemic Pattern

The visual system is mature, but async behavior is not yet represented as a
first-class design-system state. The fix should be shared across every mutation,
not patched button by button.

## Positive Findings

- Semantic landmarks, headings, labels, table scopes, live announcer, skip link,
  and visible focus outlines are already present.
- All primary interactive targets meet the 44 px touch-height target.
- The interface respects reduced motion and avoids expensive decorative effects.
- OKLCH tokens, tinted neutrals, and restrained accent use match the documented
  design system.
- Manual mode is honest and the authorization boundary is visible in the UI.

## Recommended Actions

1. **[P1] `impeccable harden`**: Add shared pending, error, and recovery behavior.
2. **[P2] `impeccable layout`**: Activate the wide-screen evidence rail.
3. **[P2] `impeccable polish`**: Complete interaction states and reverify the journey.
