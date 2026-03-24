# Infra Workflow

## New Infrastructure
Trigger: new cloud resource provisioning (compute, storage, networking, IAM, etc.)

Steps:
1. aurorie-infra-lead reads task and `input_context`. If `artifact:` references a PRD or architecture doc, reads it.
2. Dispatch aurorie-infra-iac-engineer.
3. aurorie-infra-iac-engineer writes Terraform module(s) to the directory specified in the task (default: `terraform/`). Writes `infra-plan.md`: module structure, variables, outputs, usage example, apply instructions.
4. Dispatch aurorie-infra-reviewer with `artifact: .claude/workspace/artifacts/infra/<task-id>/infra-plan.md`.
5. aurorie-infra-reviewer reviews for security, reliability, cost, and correctness. Writes `review.md`.
6. aurorie-infra-lead reads `infra-plan.md` and `review.md`. If 🔴 Blockers exist, re-dispatches aurorie-infra-iac-engineer with `artifact: .claude/workspace/artifacts/infra/<task-id>/review.md` to fix blockers, then re-dispatches aurorie-infra-reviewer to re-review once. If blockers remain after second review, returns `FAILED: aurorie-infra-reviewer — unresolved blockers after retry`. If clear, writes `summary.md`: what was provisioned, module structure, key variables, review outcome, apply instructions.

## IaC Change
Trigger: modify existing Terraform configuration

Steps:
1. aurorie-infra-lead reads task. Identifies scope of change.
2. Dispatch aurorie-infra-iac-engineer with change description and any `artifact:` context.
3. aurorie-infra-iac-engineer implements changes (writes or updates Terraform modules). Writes `infra-plan.md`: what changed, why, diff summary, migration notes if state changes required. If no prior `infra-plan.md` exists, creates one from scratch.
4. Dispatch aurorie-infra-reviewer with `artifact: .claude/workspace/artifacts/infra/<task-id>/infra-plan.md`.
5. aurorie-infra-reviewer reviews changes for security, reliability, cost, and correctness. Writes `review.md`.
6. aurorie-infra-lead reads `infra-plan.md` and `review.md`. If blockers exist, re-dispatches aurorie-infra-iac-engineer with `artifact: .claude/workspace/artifacts/infra/<task-id>/review.md` to fix blockers, then re-dispatches aurorie-infra-reviewer to re-review once. If blockers remain, returns `FAILED: aurorie-infra-reviewer — unresolved blockers after retry`. If clear, writes `summary.md`: change summary, review outcome, migration steps required before apply.

## IaC Audit
Trigger: audit existing Terraform codebase for issues

Steps:
1. aurorie-infra-lead routes directly to aurorie-infra-reviewer.
2. aurorie-infra-reviewer scans specified Terraform files/modules. Writes `review.md` with findings across security, reliability, cost, and best practices.
3. aurorie-infra-lead reads `review.md`. Writes `summary.md`: total findings by severity, top priority items, recommended remediation order.

## PR Review
Trigger: review a pull request containing IaC changes

Steps:
1. aurorie-infra-lead routes directly to aurorie-infra-reviewer.
2. aurorie-infra-reviewer uses the `github` MCP to read the PR diff. Reviews for security, reliability, cost, correctness, and best practices. Writes `review.md`.
3. aurorie-infra-lead reads `review.md`. Writes `summary.md`: overall verdict (approve / request changes), blocker count, key findings, merge readiness.
