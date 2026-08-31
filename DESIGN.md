---
name: Captain's Table
description: A shared decision surface for humans and browser agents.
colors:
  signal: "oklch(52% 0.105 184)"
  signal-hover: "oklch(46% 0.100 184)"
  signal-soft: "oklch(93% 0.030 184)"
  ground: "oklch(97.5% 0.008 80)"
  ground-raised: "oklch(99% 0.005 80)"
  ground-secondary: "oklch(94% 0.010 80)"
  ink: "oklch(23% 0.018 205)"
  ink-muted: "oklch(48% 0.020 205)"
  alloy: "oklch(84% 0.014 205)"
  warning: "oklch(62% 0.125 72)"
  warning-soft: "oklch(94% 0.030 72)"
  danger: "oklch(52% 0.135 28)"
  danger-soft: "oklch(94% 0.030 28)"
typography:
  headline:
    fontFamily: "Inter Variable, Inter, system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 650
    lineHeight: 1.14
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Inter Variable, Inter, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 620
    lineHeight: 1.3
  body:
    fontFamily: "Inter Variable, Inter, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 430
    lineHeight: 1.55
  label:
    fontFamily: "Inter Variable, Inter, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 620
    lineHeight: 1.25
    letterSpacing: "0.045em"
  evidence:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "0.75rem"
    fontWeight: 450
    lineHeight: 1.5
rounded:
  control: "6px"
  surface: "10px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  2xl: "32px"
  3xl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.signal}"
    textColor: "{colors.ground-raised}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "10px 16px"
  button-primary-hover:
    backgroundColor: "{colors.signal-hover}"
    textColor: "{colors.ground-raised}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "10px 16px"
  button-secondary:
    backgroundColor: "{colors.ground-raised}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "10px 16px"
  input:
    backgroundColor: "{colors.ground-raised}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
  revision-seal:
    backgroundColor: "transparent"
    textColor: "{colors.ink-muted}"
    typography: "{typography.evidence}"
    rounded: "{rounded.control}"
    padding: "6px 8px"
---

# Design System: Captain's Table

## Overview

**Creative North Star: "The Instrument Table"**

The interface should feel like a finely made instrument laid out for a demanding
operator: precise enough to trust immediately, quiet enough to keep attention on
the decision, and distinctive through behavior rather than decoration. Linear's
operational clarity, Stripe's technical confidence, and Teenage Engineering's
controlled product character set the standard.

The product is a shared working surface, not a chatbot shell. Agent activity,
human edits, protocol state, authorization boundaries, and execution evidence
must appear in one coherent composition. Responsive motion should clarify state
changes without turning the judge's task into a presentation sequence.

The primary canvas is ChatGPT's 680–900px split pane. The active decision remains
single-column at that width, with compact capability evidence near the header and
full protocol history below. A side evidence rail is earned only above 1100px.

The signature visual behavior is revision calibration: one compact geometric seal
advances only after a verified state mutation and preserves the prior mark in the
decision trail. It gives the protocol a recognizable physical metaphor without
turning the interface into a console or adding decorative chrome.

**Key Characteristics:**

- Restrained, high-information product composition.
- Visible state and causality between agent actions and page changes.
- Familiar controls with a small number of memorable protocol-native patterns.
- Technical evidence integrated into the workflow instead of hidden in a demo log.

## Colors

The palette uses warm tinted neutrals with a mineral blue-green signal reserved
for active selection, primary actions, and verified protocol state. The OKLCH
frontmatter is normative.

### Primary

- **Mineral Signal:** Used sparingly for
  selected state, primary action, focus, and verified WebMCP availability.

### Neutral

- **Warm Instrument Ground:** The main
  working surface, tinted away from pure white.
- **Graphite Reading Ink:** Primary text,
  never pure black.
- **Quiet Alloy:** Dividers, inactive
  controls, and secondary structure.

**The Ten Percent Rule.** The accent occupies no more than ten percent of a screen.
Its rarity makes protocol state and consequential actions unmistakable.

**The Semantic Independence Rule.** Warning, stale, blocked, authorized, and
completed states must remain distinguishable without relying on hue alone.

## Typography

**Display Font:** Inter Variable with system-ui fallback
**Body Font:** Inter Variable with system-ui fallback
**Label/Mono Font:** Native UI monospace stack for evidence only

**Character:** One technical-humanist sans carries the product interface without
performative typographic contrast. A restrained mono role identifies tool names,
hashes, timestamps, and protocol evidence. Tabular numerals keep cost and schedule
comparisons stable.

### Hierarchy

- **Display:** Used once for the active decision, never as a marketing headline.
- **Headline:** Separates workflow stages and comparison regions.
- **Title:** Names actionable sections and selected alternatives.
- **Body:** Carries explanations and recovery guidance at a maximum of 70ch.
- **Label:** Identifies state, tools, ownership, and compact metadata.

**The One-Family Rule.** Hierarchy comes from size, weight, and spacing. Do not add
a decorative display face to make the product appear designed.

## Elevation

The system is flat by default. Depth comes from tonal layering, borders, and
spatial hierarchy. Shadows may appear only for temporary overlays or a control
that physically rises during direct manipulation.

**The State, Not Decoration Rule.** Elevation communicates interaction or temporary
layering. If a resting surface needs a shadow to feel important, the hierarchy is
wrong.

## Components

Interactive controls use gently squared 6px corners; grouped working surfaces use
10px corners. Borders use Quiet Alloy at 1px. Focus is a 2px Mineral Signal outline
with a 2px ground-colored offset. Every interactive component includes default,
hover, focus, active, disabled, loading, success, and relevant error states.

Buttons should feel immediate and controlled. Inputs should look native to a
serious product, with visible focus and inline validation. Containers should be
used only where grouping or interaction semantics require them. The signature
component is the decision surface: a synchronized plan, conflict, comparison, and
authorization view that visibly responds to WebMCP tool calls.

The revision seal is the only custom visual motif. It uses two short horizontal
calibration bars plus a text revision. Bars have square ends, never glow, never
animate continuously, and never become a pill or oversized metric. A verified
revision advances the second bar by one 4px step for 180ms; accompanying text
provides the durable meaning.

State transitions run for 180ms using `cubic-bezier(0.22, 1, 0.36, 1)` and animate
only opacity and transform. Reduced motion removes transforms and shortens feedback
to an immediate opacity change.

## Do's and Don'ts

### Do:

- **Do** keep the shared decision and its current state visually dominant.
- **Do** expose WebMCP tool activity as legible product behavior and compact evidence.
- **Do** reserve the mineral accent for active, selected, and verified states.
- **Do** use short responsive transitions to connect cause and effect.
- **Do** make stale state, blocked execution, authorization, and completion explicit.

### Don't:

- **Don't** build a generic AI dashboard from interchangeable cards and oversized metrics.
- **Don't** use a chatbot-first layout that reduces the product to a transcript.
- **Don't** use dark neon agent-console styling, terminal cosplay, or science-fiction decoration.
- **Don't** use excessive cards, nested containers, glass effects, or decorative gradients.
- **Don't** ship hackathon-demo roughness, placeholder copy, unexplained controls, or staged interactions that fail under direct use.
- **Don't** imitate generic dark AI control panels with neon gradients and glass cards.
- **Don't** use gradient text, colored side-stripe borders, or modal dialogs as the first solution.
