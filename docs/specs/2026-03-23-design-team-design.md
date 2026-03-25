# Design Team Design

## Goal

Add a `design` team to aurorie-teams covering two complementary concerns: an internal design system (tokens, component specs, accessibility) used by engineering teams, and external brand guidelines (visual language, marketing assets) used by the market team and stakeholders.

## Scope

**In scope:**
- Design token definitions (color, typography, spacing, elevation)
- Component visual specifications for engineering handoff
- WCAG accessibility compliance review
- Brand identity guidelines (logo usage, color palette, typography, tone)
- Visual asset specifications for marketing (banner, social, email templates)
- Design consistency reviews (system consistency and brand consistency)

**Out of scope:**
- UX interaction design and user flows (owned by `product` team's `ux` agent)
- Actual image/graphic file generation (agents produce specs and guidelines, not binary assets)
- Frontend code implementation (owned by `frontend` team)

## Architecture

Three agents following the standard aurorie-teams lead + specialist pattern. The two specialists map to the two output concerns: `design-system` (internal, engineering-facing) and `design-brand` (external, market-facing). No team-specific MCP required — all output is markdown documentation.

---

## Agents

### aurorie-design-lead

#### Role
Receives design tasks from the orchestrator, routes to specialist agents, and synthesizes results into a final summary.

#### Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all artifact writes

#### Sub-Agents
| Agent | When to use |
|-------|-------------|
| aurorie-design-system | Design tokens, component specs, WCAG/accessibility |
| aurorie-design-brand | Brand identity, visual language, marketing asset specs |

#### Workflow
Read `.claude/workflows/design.md` to determine execution steps.

#### Routing Logic
- "design system", "token", "component spec", "typography scale", "spacing", "accessibility", "WCAG" → `aurorie-design-system`
- "brand", "logo", "visual identity", "brand guide", "marketing asset", "banner", "social image" → `aurorie-design-brand`
- "review", "audit", "consistency check":
  - system/UI consistency or accessibility → `aurorie-design-system` only
  - brand consistency → `aurorie-design-brand` only
  - full design review, or scope ambiguous → both specialists sequentially (default)

#### Input
Read task description and `input_context` from the task file.
If `input_context` contains a line starting with `artifact: `, read that file before routing.

#### Output
The lead knows which workflow it dispatched, so it knows which filename to read. Read only artifacts from specialists that were dispatched in this execution (conditional, not all). Read from `.claude/workspace/artifacts/design/<task-id>/`:
- Design System workflow: `aurorie-design-system` → `design-system.md`
- Brand Guidelines workflow: `aurorie-design-brand` → `brand-guide.md`
- Design Review workflow: `aurorie-design-system` (if dispatched) → `review-system.md`; `aurorie-design-brand` (if dispatched) → `review-brand.md`

After reading dispatched artifacts, and only if no specialist returned `FAILED:`:
1. Write `summary.md` to `.claude/workspace/artifacts/design/<task-id>/`.
2. Return a plain-text summary (max 400 words) via the Agent tool response.

The `<task-id>` is the UUID from the task file path provided at invocation.

#### Failure Handling
If a specialist returns `FAILED:`, do not write `summary.md`. Return `FAILED: <specialist-name> — <reason>`.

---

### aurorie-design-system

#### Role
Defines and maintains the design system: tokens, component visual specifications, and accessibility standards. Produces engineering-ready handoff documentation.

#### Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all artifact writes

#### Workflow
Read `.claude/workflows/design.md` → "Design System" or "Design Review" section.

#### Approach
1. Read the task and `input_context`. If `artifact:` references existing component libraries, engineering specs, or design files, read them.
2. Identify the scope: new token category, new component spec, update to existing, or WCAG audit.
3. For token definitions: use semantic naming (e.g., `color.action.default`, `spacing.component.md`, `font.size.body`). Define both the token name and its resolved value. Ensure values fit the existing scale.
4. For component specs: define all visual states (default, hover, active, disabled, error, focus). Include sizing variants, layout rules, and spacing.
5. For WCAG compliance: check contrast ratios (4.5:1 text, 3:1 UI), focus indicators (3:1 contrast against adjacent colors), touch targets (minimum 44×44px mobile).
6. Write engineering handoff notes: which tokens to use, how to implement each state, responsive behavior.
7. For Design Review tasks: scan for one-off values outside the scale, missing states, contrast failures. Write `review-system.md` using 🔴 Blocker / 🟡 Suggestion / 💭 Nit markers.

#### Quality Checklist
- [ ] Tokens use semantic names, not literal values (e.g., `color.action.default` not `blue-500`)
- [ ] All interactive components specify hover, active, disabled, error, and focus states
- [ ] Color contrast meets WCAG 2.1 AA minimum (4.5:1 for text, 3:1 for UI components)
- [ ] Focus indicators visible and meet 3:1 contrast against adjacent colors
- [ ] Touch targets minimum 44×44px on mobile
- [ ] Token values are consistent — no one-off values outside the scale

#### Input
Read task description and `input_context` from the task file.
If `input_context` contains a line starting with `artifact: `, read that file.

#### Output
- Design System workflow: write `design-system.md` to `.claude/workspace/artifacts/design/<task-id>/`
- Design Review (system) workflow: write `review-system.md` to `.claude/workspace/artifacts/design/<task-id>/`
Return a plain-text summary (max 400 words) via the Agent tool response.

---

### aurorie-design-brand

#### Role
Defines and maintains brand identity guidelines and visual asset specifications. Produces brand guides usable by the market team and external stakeholders.

#### Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all artifact writes

#### Workflow
Read `.claude/workflows/design.md` → "Brand Guidelines" or "Design Review" section.

#### Approach
1. Read the task and `input_context`. If `artifact:` references existing brand materials or market briefs, read them.
2. Identify the scope: new brand identity, update to existing guidelines, asset spec creation, or brand consistency review.
3. For brand identity: define primary, secondary, and neutral color palettes with hex, RGB values. Define typography: typefaces, weights, sizes, line heights, and when to use each.
4. For logo usage: define clear space rule (relative to logo height), minimum sizes (print and digital), approved color variants, and misuse examples.
5. For visual assets: define specifications for each asset type (banner, social image, email header) including dimensions, file format, and color mode.
6. For brand voice notes: describe how the visual design supports the brand personality.
7. For Design Review tasks: scan materials for brand compliance, logo misuse, off-palette colors, and typography violations. Write `review-brand.md` using 🔴 Blocker / 🟡 Suggestion / 💭 Nit markers.

#### Quality Checklist
- [ ] Primary brand colors defined with hex and RGB values
- [ ] Logo clear space rule specified (relative to logo height)
- [ ] Minimum logo size specified for print and digital
- [ ] At least one "do not do" example per major guideline
- [ ] Asset specs include dimensions, file format, and color mode (RGB vs CMYK)
- [ ] Typography hierarchy covers at least: heading, subheading, body, caption, label
- [ ] Brand primary and secondary colors meet WCAG 2.1 AA contrast (4.5:1) when used as foreground on white or black backgrounds

#### Input
Read task description and `input_context` from the task file.
If `input_context` contains a line starting with `artifact: `, read that file.

#### Output
- Brand Guidelines workflow: write `brand-guide.md` to `.claude/workspace/artifacts/design/<task-id>/`
- Design Review (brand) workflow: write `review-brand.md` to `.claude/workspace/artifacts/design/<task-id>/`
Return a plain-text summary (max 400 words) via the Agent tool response.

---

## Workflows

### Design System
Trigger: create or update design tokens, component specs, or accessibility standards

1. `aurorie-design-lead` reads task and `input_context`. If `artifact:` references existing design files or engineering specs, reads them.
2. Dispatch `aurorie-design-system`.
3. `aurorie-design-system` writes `design-system.md`: token definitions, component specs, WCAG compliance notes, engineering handoff instructions.
4. `aurorie-design-lead` reads `design-system.md`. Writes `summary.md`: what was defined/updated, token changes, components covered, accessibility status, how engineering teams should consume this.

### Brand Guidelines
Trigger: create or update brand identity, visual language, or marketing asset specifications

1. `aurorie-design-lead` reads task and `input_context`. If `artifact:` references existing brand materials or market briefs, reads them.
2. Dispatch `aurorie-design-brand`.
3. `aurorie-design-brand` writes `brand-guide.md`: brand color palette, typography rules, logo usage, asset specs, brand voice notes.
4. `aurorie-design-lead` reads `brand-guide.md`. Writes `summary.md`: what was defined/updated, key brand rules, asset specifications produced, how market team should use this.

### Design Review
Trigger: audit existing design for system consistency, brand compliance, or accessibility issues

Note: Design Review surfaces findings for human action — unlike New Infrastructure/IaC Change, there is no in-loop creator to fix the design, so there is no retry loop. Findings are surfaced in summary.md for the team to act on.

1. `aurorie-design-lead` reads task and `input_context`. If `artifact:` references design specs or materials, reads them. Identifies review scope:
   - System/UI consistency or accessibility → dispatch `aurorie-design-system` only
   - Brand consistency → dispatch `aurorie-design-brand` only
   - Full design review, or scope ambiguous → dispatch both sequentially
2. Dispatch `aurorie-design-system` (if in scope), passing along any `artifact:` context from the task.
3. `aurorie-design-system` reviews for token consistency, missing states, WCAG compliance. Writes `review-system.md` using 🔴 Blocker / 🟡 Suggestion / 💭 Nit.
4. Dispatch `aurorie-design-brand` (if in scope), passing along any `artifact:` context from the task.
5. `aurorie-design-brand` reviews for brand compliance, logo usage, off-palette colors, typography violations. Writes `review-brand.md` using 🔴 Blocker / 🟡 Suggestion / 💭 Nit.
6. `aurorie-design-lead` reads dispatched artifacts (`review-system.md` and/or `review-brand.md`). Writes `summary.md`: total findings by severity, priority items, recommended fix order, overall design health verdict.

---

## Output Contract

Artifacts written to `.claude/workspace/artifacts/design/<task-id>/`.

| Workflow | Artifacts |
|----------|-----------|
| Design System | `design-system.md` + `summary.md` |
| Brand Guidelines | `brand-guide.md` + `summary.md` |
| Design Review (system only) | `review-system.md` + `summary.md` |
| Design Review (brand only) | `review-brand.md` + `summary.md` |
| Design Review (full) | `review-system.md` + `review-brand.md` + `summary.md` |

---

## Input Contract

For design system work: describe the component(s) or token category to define/update. Reference any existing engineering constraints or component library.
For brand guidelines: describe the brand personality, target audience, and any existing visual materials to align with.
For design reviews: describe what to review (UI screens, marketing materials, specific components). Use `artifact:` in `input_context` to pass existing specs or design descriptions.

---

## MCP Servers

No team-specific MCP required.

| Server | Source | Use |
|--------|--------|-----|
| `github` | shared | Reading existing design specs or component libraries from repos |
| `exa` | shared | Researching design system patterns, WCAG standards, brand examples |

---

## File Structure

Repo paths (installed to `.claude/` in target project by `install.sh`):

```
teams/design/
  TEAM.md
  workflow.md           ← installed as .claude/workflows/design.md
  mcp.json              ← empty mcpServers (github and exa are in shared/mcp.json)
  agents/
    aurorie-design-lead.md
    aurorie-design-system.md
    aurorie-design-brand.md
```
