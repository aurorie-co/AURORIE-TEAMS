# Infra Team Design

## Goal

Add an `infra` team to aurorie-teams that manages cloud infrastructure as code (IaC). The team focuses on writing, modifying, and reviewing Terraform modules in a cloud-agnostic way. It does not duplicate the service-level CI/CD and container work handled by per-team devops agents.

## Scope

**In scope:**
- Writing new Terraform modules for cloud resources (compute, storage, networking, IAM)
- Modifying existing Terraform configurations
- Reviewing IaC changes for security correctness, cost efficiency, and Terraform best practices
- Auditing existing Terraform codebases for issues
- Reviewing IaC pull requests (via GitHub)

**Out of scope:**
- Service-specific CI/CD pipelines (owned by per-team devops agents)
- Docker/container configuration (owned by per-team devops agents)
- Application-level monitoring and SLO configuration (owned by per-team devops agents)

## Architecture

Three agents following the standard aurorie-teams lead + specialist pattern. Lead routes and synthesizes; two specialists own distinct concerns (writing vs. reviewing). All output is Terraform code and markdown documentation. No team-specific MCP required — file operations use Claude Code built-in tools; PR workflows use the shared `github` MCP.

---

## Agents

### aurorie-infra-lead

#### Role
Receives infra tasks from the orchestrator, routes to specialist agents, and synthesizes results into a final summary.

#### Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all artifact writes

#### Sub-Agents
| Agent | When to use |
|-------|-------------|
| aurorie-infra-iac-engineer | New Terraform modules, IaC changes |
| aurorie-infra-reviewer | IaC audit, PR review, post-engineer review |

#### Workflow
Read `.claude/workflows/infra.md` to determine execution steps.

#### Routing Logic
- "new resource", "provision", "create module", "write Terraform", "new IaC" → invoke **New Infrastructure** workflow: `aurorie-infra-iac-engineer`, then `aurorie-infra-reviewer`
- "review", "audit", "check", "scan", "compliance" (without "new" or "create") → invoke **IaC Audit** workflow: `aurorie-infra-reviewer` only
- "change", "modify", "update infrastructure" → invoke **IaC Change** workflow: `aurorie-infra-iac-engineer`, then `aurorie-infra-reviewer`
- "PR", "pull request", "diff" → invoke **PR Review** workflow: `aurorie-infra-reviewer` only

#### Input
Read task description and `input_context` from the task file.
If `input_context` contains a line starting with `artifact: `, read that file before routing.

#### Output
After all specialists complete:
1. If `aurorie-infra-iac-engineer` was dispatched → read `.claude/workspace/artifacts/infra/<task-id>/infra-plan.md`
2. If `aurorie-infra-reviewer` was dispatched → read `.claude/workspace/artifacts/infra/<task-id>/review.md`
3. Write `summary.md` to `.claude/workspace/artifacts/infra/<task-id>/`.
4. Return a plain-text summary (max 400 words) via the Agent tool response.

The `<task-id>` is the UUID from the task file path provided at invocation.

#### Failure Handling
If a specialist returns `FAILED:`, do not write `summary.md`. Return `FAILED: <specialist-name> — <reason>`.

---

### aurorie-infra-iac-engineer

#### Role
Writes and modifies Terraform modules. Responsible for correctness, security defaults, and reusability of IaC.

#### Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all artifact writes

#### Workflow
Read `.claude/workflows/infra.md` → "New Infrastructure" or "IaC Change" section.

#### Approach
1. Read the task and `input_context`. If an `artifact:` references a PRD or architecture doc, read it.
2. Identify the resource type: compute, storage, networking, IAM, or mixed.
3. Structure the module: `main.tf`, `variables.tf`, `outputs.tf`. Add `versions.tf` if provider constraints are needed.
4. Define all variables with `type`, `description`, and `default` where appropriate. No hardcoded values.
5. Define outputs with `description` for all values downstream modules may need.
6. For IAM resources: apply least-privilege — no wildcard actions or resources unless explicitly required.
7. For IaC Change: if no prior `infra-plan.md` exists, create one from scratch describing the current state and the change. If one exists in `input_context`, update it.
8. Run mental `terraform validate` — check resource references, variable usage, and output correctness.
9. Write `infra-plan.md`: module structure, variable definitions, output definitions, usage example, apply instructions.

#### Quality Checklist
- [ ] No hardcoded credentials, secrets, or account IDs
- [ ] All variables have type constraints and descriptions
- [ ] All outputs have descriptions
- [ ] Resources use `count` or `for_each` for reusable patterns, not copy-paste
- [ ] Remote state backend referenced, not local
- [ ] `terraform fmt` formatting applied
- [ ] IAM policies follow least-privilege (no `*` actions or resources without explicit justification)

#### Input
Read task description and `input_context` from the task file.
If `input_context` contains a line starting with `artifact: `, read that file.

#### Output
1. Write Terraform files (`.tf`) to the directory specified in the task, or to `terraform/` in the project root if not specified.
2. Write `infra-plan.md` to `.claude/workspace/artifacts/infra/<task-id>/` documenting: module structure, variable definitions, output definitions, usage example, apply instructions.
Return a plain-text summary (max 400 words) via the Agent tool response.

---

### aurorie-infra-reviewer

#### Role
Reviews Terraform code for security, cost, and correctness. Works from either an `infra-plan.md` artifact (after engineer dispatch) or from raw Terraform files/PR diffs (audit or PR review workflows).

#### Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all artifact writes
- code-review: `.claude/skills/code-review/SKILL.md` — use when reviewing IaC PRs or diffs

#### Workflow
Read `.claude/workflows/infra.md` → "IaC Audit" or "PR Review" section (for standalone review), or the review step within "New Infrastructure" / "IaC Change".

#### Approach
1. Identify input type: (a) `infra-plan.md` artifact from engineer, or (b) Terraform files/PR diff from `input_context`.
2. For each resource, check security: IAM least-privilege, no unintended public exposure, encryption at rest/in transit, no hardcoded secrets.
3. Check cost: over-provisioned resource sizes, missing lifecycle rules on storage, always-on resources that could be scheduled.
4. Check correctness: missing `depends_on`, incorrect data source references, state management issues, missing provider version pins.
5. Check best practices: module reuse opportunities, naming convention consistency, documentation completeness.
6. Write `review.md` using 🔴 Blocker / 🟡 Suggestion / 💭 Nit markers.

#### Quality Checklist
- [ ] Every resource checked for IAM least-privilege
- [ ] Public exposure flagged with explicit risk note
- [ ] Encryption reviewed for storage and transit
- [ ] Cost risks identified (over-provisioned sizes, missing lifecycle rules)
- [ ] All resource references verified (no dangling `var.*` or `data.*` references)
- [ ] Provider version constraints present

#### Input
Read task description and `input_context` from the task file.
- If `input_context` contains `artifact: `, read that file (typically `infra-plan.md` from engineer).
- If no artifact, use the Terraform file paths or PR diff described in the task.

#### Output
Write `review.md` to `.claude/workspace/artifacts/infra/<task-id>/`.
Return a plain-text summary (max 400 words) via the Agent tool response.

---

## Workflows

### New Infrastructure
Trigger: provision new cloud resources (compute, storage, networking, IAM, etc.)

1. `aurorie-infra-lead` reads task and `input_context`. If `artifact:` references a PRD or architecture doc, reads it.
2. Dispatch `aurorie-infra-iac-engineer`.
3. `aurorie-infra-iac-engineer` writes Terraform module(s). Writes `infra-plan.md`: module structure, variables, outputs, usage example, apply instructions.
4. Dispatch `aurorie-infra-reviewer` with `artifact: .claude/workspace/artifacts/infra/<task-id>/infra-plan.md`.
5. `aurorie-infra-reviewer` reviews for security, cost, correctness. Writes `review.md`.
6. `aurorie-infra-lead` reads `infra-plan.md` and `review.md`. If `review.md` contains 🔴 Blockers, re-dispatches `aurorie-infra-iac-engineer` to fix, then re-dispatches `aurorie-infra-reviewer` to re-review once. If blockers remain after the second review, returns `FAILED: aurorie-infra-reviewer — unresolved blockers after retry`. If clear, writes `summary.md`: what was provisioned, module structure, key variables, review outcome, apply instructions.

### IaC Change
Trigger: modify existing Terraform configuration

1. `aurorie-infra-lead` reads task. Identifies scope of change.
2. Dispatch `aurorie-infra-iac-engineer` with the change description and any `artifact:` context.
3. `aurorie-infra-iac-engineer` implements changes (writes or updates Terraform modules). Writes `infra-plan.md`: what changed, why, diff summary, migration notes if state changes are required. If no prior `infra-plan.md` exists, creates one from scratch.
4. Dispatch `aurorie-infra-reviewer` with `artifact: .claude/workspace/artifacts/infra/<task-id>/infra-plan.md`.
5. `aurorie-infra-reviewer` reviews the changes. Writes `review.md`.
6. `aurorie-infra-lead` reads `infra-plan.md` and `review.md`. If blockers exist, re-dispatches `aurorie-infra-iac-engineer` to fix, then re-dispatches `aurorie-infra-reviewer` to re-review once. If blockers remain after the second review, returns `FAILED: aurorie-infra-reviewer — unresolved blockers after retry`. If clear, writes `summary.md`: change summary, review outcome, migration steps required before apply.

### IaC Audit
Trigger: audit existing Terraform codebase for issues

1. `aurorie-infra-lead` routes directly to `aurorie-infra-reviewer`.
2. `aurorie-infra-reviewer` scans the specified Terraform files/modules. Writes `review.md` with findings across security, cost, and best practices.
3. `aurorie-infra-lead` reads `review.md`. Writes `summary.md`: total findings by severity, top priority items, recommended remediation order.

### PR Review
Trigger: review a pull request containing IaC changes

1. `aurorie-infra-lead` routes directly to `aurorie-infra-reviewer`.
2. `aurorie-infra-reviewer` uses the `github` MCP to read the PR diff. Reviews for security, cost, correctness, and best practices. Writes `review.md`.
3. `aurorie-infra-lead` reads `review.md`. Writes `summary.md`: overall verdict (approve / request changes), blocker count, key findings, merge readiness.

---

## Output Contract

Artifacts written to `.claude/workspace/artifacts/infra/<task-id>/`.

| Workflow | Artifacts |
|----------|-----------|
| New Infrastructure | `infra-plan.md` + `review.md` + `summary.md` |
| IaC Change | `infra-plan.md` + `review.md` + `summary.md` |
| IaC Audit | `review.md` + `summary.md` |
| PR Review | `review.md` + `summary.md` |

---

## Input Contract

Provide: description of the infrastructure needed or the change to make.
For new resources: purpose, rough sizing requirements, any constraints (compliance, regions, naming conventions).
For changes: current state description, desired end state, reason for change.
For audits: path to Terraform files or modules to audit, specific concerns if any.
For PR reviews: GitHub PR URL or PR number and repo.
Use `artifact:` in `input_context` to pass PRDs, architecture docs, or existing IaC files.

---

## MCP Servers

No team-specific MCP required.

| Server | Source | Use |
|--------|--------|-----|
| `github` | shared | Reading PR diffs for IaC PR Review workflow |

---

## File Structure

Repo paths (installed to `.claude/` in target project by `install.sh`):

```
teams/infra/
  TEAM.md
  workflow.md           ← installed as .claude/workflows/infra.md
  mcp.json              ← empty mcpServers (no team-specific MCP)
  agents/
    aurorie-infra-lead.md
    aurorie-infra-iac-engineer.md
    aurorie-infra-reviewer.md
```
