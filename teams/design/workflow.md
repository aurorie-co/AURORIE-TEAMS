# Design Workflow

## Design System
Trigger: create or update design tokens, component visual specs, or accessibility standards

Steps:
1. aurorie-design-lead reads task and `input_context`. If `artifact:` references existing design files or engineering specs, reads them.
2. Dispatch aurorie-design-system.
3. aurorie-design-system writes `design-system.md`: token definitions across all categories (color, typography, spacing, shadow, transition, border/radius), dark-mode token overrides, component specs for all states (default through empty), WCAG compliance notes, and engineering handoff instructions.
4. aurorie-design-lead reads `design-system.md`. Writes `summary.md`: what was defined/updated, which token categories changed, components covered and their states, dark mode coverage, accessibility status, how engineering teams should consume this.

## Brand Guidelines
Trigger: create or update brand identity, visual language, or marketing asset specifications

Steps:
1. aurorie-design-lead reads task and `input_context`. If `artifact:` references existing brand materials or market briefs, reads them.
2. Dispatch aurorie-design-brand.
3. aurorie-design-brand writes `brand-guide.md`: Brand Foundation (purpose, vision, mission, values, personality, promise), color palette, typography hierarchy, logo usage rules, brand voice across contexts, visual asset specs by platform, and inclusive representation notes.
4. aurorie-design-lead reads `brand-guide.md`. Writes `summary.md`: Brand Foundation summary, key visual rules established, asset specifications produced per platform, brand voice highlights, how market team should use this.

## Design Review
Trigger: audit existing design for system consistency, brand compliance, or accessibility issues

Note: Design Review surfaces findings for human action — there is no in-loop creator agent to fix the design, so there is no retry loop. Findings are surfaced in summary.md for the team to act on.

Steps:
1. aurorie-design-lead reads task and `input_context`. If `artifact:` references design specs or materials, reads them. Identifies review scope:
   - System/UI consistency or accessibility → dispatch aurorie-design-system only (skip steps 4–5)
   - Brand consistency → dispatch aurorie-design-brand only (skip steps 2–3)
   - Full design review, or scope ambiguous → dispatch both specialists sequentially (all steps)
2. (If system in scope) Dispatch aurorie-design-system with any `artifact:` context from the task.
3. (If system in scope) aurorie-design-system reviews for token consistency, missing states, dark-mode gaps, WCAG compliance, and missing reduced-motion fallbacks. Writes `review-system.md` using 🔴 Blocker / 🟡 Suggestion / 💭 Nit.
4. (If brand in scope) Dispatch aurorie-design-brand with any `artifact:` context from the task.
5. (If brand in scope) aurorie-design-brand reviews for Brand Foundation alignment, brand compliance, logo misuse, off-palette colors, typography violations, and representation issues. Writes `review-brand.md` using 🔴 Blocker / 🟡 Suggestion / 💭 Nit.
6. aurorie-design-lead reads dispatched artifacts (`review-system.md` and/or `review-brand.md`). Writes `summary.md`: total findings by severity, priority items, recommended fix order, overall design health verdict.
