# Infra Team

## Responsibility
Owns cloud infrastructure as code (IaC). Manages Terraform modules for cloud resources (compute, storage, networking, IAM) in a cloud-agnostic way.
Does not own service-specific CI/CD pipelines, Docker/container configuration, or application-level monitoring (owned by per-team devops agents).

## Agents
| Agent | Role |
|-------|------|
| aurorie-infra-lead | Task intake, workflow routing, and final summary |
| aurorie-infra-iac-engineer | Write and modify Terraform modules |
| aurorie-infra-reviewer | Review IaC for security, cost, and correctness |

## Input Contract
Provide: description of infrastructure needed or the change to make.
For new resources: purpose, constraints (compliance, regions, naming conventions).
For changes: current state, desired end state, reason for change.
For audits: Terraform file paths, specific concerns if any.
For PR reviews: GitHub PR URL or PR number and repo.
Use `artifact:` in `input_context` to pass PRDs, architecture docs, or existing IaC files.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/infra/<task-id>/`.
- New Infrastructure: `infra-plan.md` + `review.md` + `summary.md`
- IaC Change: `infra-plan.md` + `review.md` + `summary.md`
- IaC Audit: `review.md` + `summary.md`
- PR Review: `review.md` + `summary.md`
- All workflows: `summary.md` (written by lead — outcome, key decisions, recommended next action)
