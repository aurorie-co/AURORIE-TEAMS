# Design Team

## Responsibility
Owns the design system (tokens, component specs, accessibility) and brand identity guidelines (visual language, marketing asset specs).
Does not own UX interaction design or user flows (owned by `product` team's `ux` agent), frontend code implementation (owned by `frontend` team), or actual binary asset generation.

## Agents
| Agent | Role |
|-------|------|
| aurorie-design-lead | Task intake, routing to specialists, and final summary synthesis |
| aurorie-design-system | Design tokens, component visual specs, WCAG/accessibility standards |
| aurorie-design-brand | Brand identity guidelines, visual language, marketing asset specs |

## Input Contract
For design system work: describe the component(s) or token category to define/update. Reference any existing engineering constraints or component library.
For brand guidelines: describe the brand personality, target audience, and any existing visual materials to align with.
For design reviews: describe what to review (UI screens, marketing materials, specific components). Use `artifact:` in `input_context` to pass existing specs or design descriptions.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/design/<task-id>/`.

| Workflow | Artifacts |
|----------|-----------|
| Design System | `design-system.md` + `summary.md` |
| Brand Guidelines | `brand-guide.md` + `summary.md` |
| Design Review (system only) | `review-system.md` + `summary.md` |
| Design Review (brand only) | `review-brand.md` + `summary.md` |
| Design Review (full) | `review-system.md` + `review-brand.md` + `summary.md` |
