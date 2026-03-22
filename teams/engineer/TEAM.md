# Engineer Team

## Responsibility
Owns all code development, infrastructure, testing, and technical operations.
Does not own product requirements or business strategy.

## Agents
| Agent | Role |
|-------|------|
| engineer-lead | Task intake and internal routing |
| engineer-frontend | UI components, styles, client-side logic |
| engineer-backend | APIs, databases, business logic |
| engineer-devops | CI/CD, deployment, infrastructure |
| engineer-qa | Testing, quality assurance |

## Input Contract
Provide: task description, acceptance criteria, any relevant codebase context.

## Output Contract
Writes artifacts to `.claude/workspace/artifacts/engineer/<task-id>/`.
Returns implementation summary via Agent tool response.
