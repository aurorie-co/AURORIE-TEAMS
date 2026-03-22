# Engineer Team

## Responsibility
Owns all code development, infrastructure, testing, and technical operations for the project.
Does not own product requirements, business strategy, or customer communications.

## Agents
| Agent | Role |
|-------|------|
| aurorie-engineer-lead | Task intake, decomposition, and internal routing |
| aurorie-engineer-frontend | UI components, styling, client-side logic, accessibility |
| aurorie-engineer-backend | APIs, databases, business logic, authentication |
| aurorie-engineer-devops | CI/CD, Docker, deployment, infrastructure-as-code |
| aurorie-engineer-qa | Test strategy, automated testing, quality validation |

## Input Contract
Provide: task description, acceptance criteria, relevant file paths or codebase context.
For bug fixes: steps to reproduce, expected vs actual behavior.
For features: user story or PRD reference (use `artifact:` line in `input_context`).

## Output Contract
Primary artifacts written to `.claude/workspace/artifacts/engineer/<task-id>/`.
- Features: `implementation.md` (approach, files changed, how to test)
- Bug fixes: `fix.md` (root cause, solution, test added)
- Code reviews: `code-review.md` (findings by severity)
- Deployments: `deployment.md` (steps taken, verification results)
