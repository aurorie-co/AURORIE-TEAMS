# Frontend Team

## Responsibility
Owns web UI components, layouts, styles, client-side logic, and browser performance.
Does not own mobile apps, backend APIs, or product requirements.

## Agents
| Agent | Role |
|-------|------|
| aurorie-frontend-lead | Task intake, decomposition, and internal routing |
| aurorie-frontend-developer | UI components, CSS, client-side logic, accessibility, browser APIs |
| aurorie-frontend-devops | Web deployment pipelines, CDN config, preview environments, build optimization |
| aurorie-frontend-qa | Component testing, visual regression, accessibility audits, PR review |

## Input Contract
Provide: task description, acceptance criteria, design reference or mockup (use `artifact:` for UX brief).
For bug fixes: steps to reproduce, browser/OS, expected vs actual behavior.
For features: UX brief or PRD reference.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/frontend/<task-id>/`.
- Features: `frontend-implementation.md` (files changed, component API, test coverage)
- Bug fixes: `fix.md` (root cause, solution, test added)
- Code reviews: `code-review.md` (findings by severity)
- Deployments: `devops-implementation.md` (steps, verification, rollback)
