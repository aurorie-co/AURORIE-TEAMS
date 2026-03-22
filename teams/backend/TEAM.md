# Backend Team

## Responsibility
Owns server-side APIs, databases, authentication, background jobs, and infrastructure.
Does not own UI components, mobile apps, or product requirements.

## Agents
| Agent | Role |
|-------|------|
| aurorie-backend-lead | Task intake, decomposition, and internal routing |
| aurorie-backend-developer | API endpoints, business logic, DB schemas, auth, background jobs |
| aurorie-backend-devops | CI/CD pipelines, Docker, cloud infrastructure, environment config |
| aurorie-backend-qa | Integration tests, API testing, coverage audits, regression validation |

## Input Contract
Provide: task description, acceptance criteria, relevant API contracts or DB schemas.
For bug fixes: steps to reproduce, expected vs actual behavior, relevant logs.
For features: PRD or user story reference (use `artifact:` line in `input_context`).

## Output Contract
Artifacts written to `.claude/workspace/artifacts/backend/<task-id>/`.
- Features: `backend-implementation.md` (approach, files changed, API contract, how to test)
- Bug fixes: `fix.md` (root cause, solution, test added)
- Code reviews: `code-review.md` (findings by severity)
- Deployments: `devops-implementation.md` (steps, verification, rollback)
