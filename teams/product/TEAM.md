# Product Team

## Responsibility
Owns product definition, feature requirements, UX design decisions, roadmap prioritization, and market/user research.
Does not own engineering implementation, marketing copy, or customer support.

## Agents
| Agent | Role |
|-------|------|
| aurorie-product-lead | Task intake, scope clarification, and routing |
| aurorie-product-pm | PRD writing, requirements, backlog, roadmap prioritization (RICE/MoSCoW); uses market-research skill for PRD problem-space validation only |
| aurorie-product-ux | User journey mapping, interaction design guidance, design constraints |
| aurorie-product-researcher | User research synthesis, feedback analysis, market/competitive intelligence |

## Input Contract
Provide: feature idea or problem statement, target user persona, business goal,
any existing research or user feedback. For UX tasks: existing flows or mockup references.
For research tasks: raw feedback data, research notes, or competitive context.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/product/<task-id>/`.
- Feature definition: `prd.md` + `ux-brief.md` + `summary.md`
- User stories / backlog: `user-stories.md` + `summary.md`
- Roadmap: `roadmap.md` + `summary.md`
- UX research / feedback: `ux-research.md` + `summary.md`
- Market / competitive research: `market-research.md` + `summary.md`
- All workflows: `summary.md` (written by lead — outcome, key findings, recommended next action)
