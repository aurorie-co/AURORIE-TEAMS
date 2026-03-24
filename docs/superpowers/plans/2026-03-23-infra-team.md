# Infra Team Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `infra` team — 3 agents (lead, iac-engineer, reviewer) covering Terraform IaC writing, modification, audit, and PR review.

**Architecture:** Follows the standard aurorie-teams pattern: team directory under `teams/infra/` with TEAM.md, workflow.md, mcp.json, and 3 agent files. install.sh is updated to include `infra` in all team loops. routing.json and READMEs are updated to surface the new team.

**Tech Stack:** Bash, JSON, Markdown

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `tests/install.test.sh` | Modify | Add 5 assertions for infra team installation |
| `teams/infra/TEAM.md` | Create | Team responsibility, agents table, input/output contract |
| `teams/infra/workflow.md` | Create | 4 named workflows with step-by-step sequences |
| `teams/infra/mcp.json` | Create | Empty mcpServers (github is in shared) |
| `teams/infra/agents/aurorie-infra-lead.md` | Create | Lead agent: routing, conditional reads, failure handling |
| `teams/infra/agents/aurorie-infra-iac-engineer.md` | Create | Specialist: write/modify Terraform modules |
| `teams/infra/agents/aurorie-infra-reviewer.md` | Create | Specialist: security/cost/correctness review |
| `install.sh` | Modify | Add `infra` to all 5 `for team in` loops |
| `shared/routing.json` | Modify | Add infra routing rule |
| `README.md` | Modify | Add infra row to team table |
| `README.zh.md` | Modify | Add infra row to team table (Chinese) |

---

## Task 1: Write failing tests

**Files:**
- Modify: `tests/install.test.sh`

- [ ] **Step 1: Add 5 failing assertions to install.test.sh**

Add inside the `=== Test: default install ===` block, after the existing `assert_file_exists "aurorie-frontend-lead.md installed"` line:

```bash
assert_file_exists "aurorie-infra-lead.md installed"         ".claude/agents/aurorie-infra-lead.md"
assert_file_exists "aurorie-infra-iac-engineer.md installed" ".claude/agents/aurorie-infra-iac-engineer.md"
assert_file_exists "aurorie-infra-reviewer.md installed"     ".claude/agents/aurorie-infra-reviewer.md"
assert_file_exists "infra workflow installed"                ".claude/workflows/infra.md"
assert_file_contains "infra routing in routing.json"         ".claude/routing.json" '"infra"'
```

- [ ] **Step 2: Run tests to verify the 5 new assertions fail**

```bash
bash tests/install.test.sh 2>&1 | grep -E "infra|Results"
```

Expected: 5 `✗` lines for infra assertions, existing tests still pass.

---

## Task 2: Create infra team files

**Files:**
- Create: `teams/infra/TEAM.md`
- Create: `teams/infra/workflow.md`
- Create: `teams/infra/mcp.json`
- Create: `teams/infra/agents/aurorie-infra-lead.md`
- Create: `teams/infra/agents/aurorie-infra-iac-engineer.md`
- Create: `teams/infra/agents/aurorie-infra-reviewer.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p teams/infra/agents
```

- [ ] **Step 2: Create teams/infra/TEAM.md**

```markdown
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
```

- [ ] **Step 3: Create teams/infra/workflow.md**

```markdown
# Infra Workflow

## New Infrastructure
Trigger: new cloud resource provisioning (compute, storage, networking, IAM, etc.)

Steps:
1. aurorie-infra-lead reads task and `input_context`. If `artifact:` references a PRD or architecture doc, reads it.
2. Dispatch aurorie-infra-iac-engineer.
3. aurorie-infra-iac-engineer writes Terraform module(s) to the directory specified in the task (default: `terraform/`). Writes `infra-plan.md`: module structure, variables, outputs, usage example, apply instructions.
4. Dispatch aurorie-infra-reviewer with `artifact: .claude/workspace/artifacts/infra/<task-id>/infra-plan.md`.
5. aurorie-infra-reviewer reviews for security, cost, correctness. Writes `review.md`.
6. aurorie-infra-lead reads `infra-plan.md` and `review.md`. If 🔴 Blockers exist, re-dispatches aurorie-infra-iac-engineer to fix, then re-dispatches aurorie-infra-reviewer to re-review once. If blockers remain after second review, returns `FAILED: aurorie-infra-reviewer — unresolved blockers after retry`. If clear, writes `summary.md`: what was provisioned, module structure, key variables, review outcome, apply instructions.

## IaC Change
Trigger: modify existing Terraform configuration

Steps:
1. aurorie-infra-lead reads task. Identifies scope of change.
2. Dispatch aurorie-infra-iac-engineer with change description and any `artifact:` context.
3. aurorie-infra-iac-engineer implements changes (writes or updates Terraform modules). Writes `infra-plan.md`: what changed, why, diff summary, migration notes if state changes required. If no prior `infra-plan.md` exists, creates one from scratch.
4. Dispatch aurorie-infra-reviewer with `artifact: .claude/workspace/artifacts/infra/<task-id>/infra-plan.md`.
5. aurorie-infra-reviewer reviews changes. Writes `review.md`.
6. aurorie-infra-lead reads `infra-plan.md` and `review.md`. If blockers exist, re-dispatches aurorie-infra-iac-engineer to fix, then re-dispatches aurorie-infra-reviewer to re-review once. If blockers remain, returns `FAILED: aurorie-infra-reviewer — unresolved blockers after retry`. If clear, writes `summary.md`: change summary, review outcome, migration steps required before apply.

## IaC Audit
Trigger: audit existing Terraform codebase for issues

Steps:
1. aurorie-infra-lead routes directly to aurorie-infra-reviewer.
2. aurorie-infra-reviewer scans specified Terraform files/modules. Writes `review.md` with findings across security, cost, and best practices.
3. aurorie-infra-lead reads `review.md`. Writes `summary.md`: total findings by severity, top priority items, recommended remediation order.

## PR Review
Trigger: review a pull request containing IaC changes

Steps:
1. aurorie-infra-lead routes directly to aurorie-infra-reviewer.
2. aurorie-infra-reviewer uses the `github` MCP to read the PR diff. Reviews for security, cost, correctness, and best practices. Writes `review.md`.
3. aurorie-infra-lead reads `review.md`. Writes `summary.md`: overall verdict (approve / request changes), blocker count, key findings, merge readiness.
```

- [ ] **Step 4: Create teams/infra/mcp.json**

```json
{
  "mcpServers": {}
}
```

- [ ] **Step 5: Create teams/infra/agents/aurorie-infra-lead.md**

```markdown
# Aurorie Infra Lead

## Role
Receives infra tasks from the orchestrator, routes to specialist agents based on workflow type, and synthesizes results into a final summary.

## Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all artifact writes

## Sub-Agents
| Agent | When to use |
|-------|-------------|
| aurorie-infra-iac-engineer | New Terraform modules, IaC changes |
| aurorie-infra-reviewer | IaC audit, PR review, post-engineer review |

## Workflow
Read `.claude/workflows/infra.md` to determine execution steps.

## Routing Logic
- "new resource", "provision", "create module", "write Terraform", "new IaC" → invoke New Infrastructure workflow: aurorie-infra-iac-engineer, then aurorie-infra-reviewer
- "review", "audit", "check", "scan", "compliance" (without "new" or "create") → invoke IaC Audit workflow: aurorie-infra-reviewer only
- "change", "modify", "update infrastructure" → invoke IaC Change workflow: aurorie-infra-iac-engineer, then aurorie-infra-reviewer
- "PR", "pull request", "diff" → invoke PR Review workflow: aurorie-infra-reviewer only

## Input
Read task description and `input_context` from the task file.
If `input_context` contains a line starting with `artifact: `, read that file before routing.

## Output
After all specialists complete, and only if no specialist returned `FAILED:`:
1. If aurorie-infra-iac-engineer was dispatched → read `.claude/workspace/artifacts/infra/<task-id>/infra-plan.md`
2. If aurorie-infra-reviewer was dispatched → read `.claude/workspace/artifacts/infra/<task-id>/review.md`
3. Write `summary.md` to `.claude/workspace/artifacts/infra/<task-id>/`.
4. Return a plain-text summary (max 400 words) via the Agent tool response.

Note: read only the artifacts from specialists that were dispatched in this execution (conditional, not all).
The `<task-id>` is the UUID from the task file path provided at invocation.

## Failure Handling
If a specialist returns `FAILED:`, do not write `summary.md`. Return `FAILED: <specialist-name> — <reason>`.
```

- [ ] **Step 6: Create teams/infra/agents/aurorie-infra-iac-engineer.md**

```markdown
# Aurorie Infra IaC Engineer

## Role
Writes and modifies Terraform modules. Responsible for correctness, security defaults, and reusability of IaC.

## Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all artifact writes

## Workflow
Read `.claude/workflows/infra.md` → "New Infrastructure" or "IaC Change" section.

## Approach
1. Read the task and `input_context`. If an `artifact:` references a PRD or architecture doc, read it.
2. Identify the resource type: compute, storage, networking, IAM, or mixed.
3. Structure the module: `main.tf`, `variables.tf`, `outputs.tf`. Add `versions.tf` if provider constraints are needed.
4. Define all variables with `type`, `description`, and `default` where appropriate. No hardcoded values.
5. Define outputs with `description` for all values downstream modules may need.
6. For IAM resources: apply least-privilege — no wildcard actions or resources unless explicitly required.
7. For IaC Change: if no prior `infra-plan.md` exists, create one from scratch describing the current state and the change. If one exists in `input_context`, update it.
8. Verify all resource references, variable usage, and output correctness as if running `terraform validate`. If any reference is unresolvable, correct it before proceeding.
9. Write Terraform files (`.tf`) to the directory specified in the task, or to `terraform/` in the project root if not specified.
10. Write `infra-plan.md` documenting: module structure, variable definitions, output definitions, usage example, apply instructions.

## Quality Checklist
- [ ] No hardcoded credentials, secrets, or account IDs
- [ ] All variables have type constraints and descriptions
- [ ] All outputs have descriptions
- [ ] Resources use `count` or `for_each` for reusable patterns, not copy-paste
- [ ] Remote state backend referenced, not local
- [ ] `terraform fmt` formatting applied
- [ ] IAM policies follow least-privilege (no `*` actions or resources without explicit justification)

## Input
Read task description and `input_context` from the task file.
If `input_context` contains a line starting with `artifact: `, read that file.

## Output
1. Write Terraform files (`.tf`) to the directory specified in the task, or to `terraform/` in the project root if not specified.
2. Write `infra-plan.md` to `.claude/workspace/artifacts/infra/<task-id>/` documenting: module structure, variable definitions, output definitions, usage example, apply instructions.
Return a plain-text summary (max 400 words) via the Agent tool response.
```

- [ ] **Step 7: Create teams/infra/agents/aurorie-infra-reviewer.md**

```markdown
# Aurorie Infra Reviewer

## Role
Reviews Terraform code for security, cost, and correctness. Works from either an `infra-plan.md` artifact (after engineer dispatch) or from raw Terraform files/PR diffs (audit or PR review workflows).

## Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all artifact writes
- code-review: `.claude/skills/code-review/SKILL.md` — use when reviewing IaC PRs or diffs (shared skill, installed by the skills installer)

## Workflow
Read `.claude/workflows/infra.md` → "IaC Audit" or "PR Review" section (for standalone review), or the review step within "New Infrastructure" / "IaC Change".

## Approach
1. Identify input type: (a) `infra-plan.md` artifact from engineer, or (b) Terraform files/PR diff from `input_context`.
2. For each resource, check security: IAM least-privilege, no unintended public exposure, encryption at rest/in transit, no hardcoded secrets.
3. Check cost: over-provisioned resource sizes, missing lifecycle rules on storage, always-on resources that could be scheduled.
4. Check correctness: missing `depends_on`, incorrect data source references, state management issues, missing provider version pins.
5. Check best practices: module reuse opportunities, naming convention consistency, documentation completeness.
6. Write `review.md` using 🔴 Blocker / 🟡 Suggestion / 💭 Nit markers.

## Quality Checklist
- [ ] Every resource checked for IAM least-privilege
- [ ] Public exposure flagged with explicit risk note
- [ ] Encryption reviewed for storage and transit
- [ ] Cost risks identified (over-provisioned sizes, missing lifecycle rules)
- [ ] All resource references verified (no dangling `var.*` or `data.*` references)
- [ ] Provider version constraints present

## Input
Read task description and `input_context` from the task file.
- If `input_context` contains `artifact: `, read that file (typically `infra-plan.md` from engineer).
- If no artifact, use the Terraform file paths or PR diff described in the task.

## Output
Write `review.md` to `.claude/workspace/artifacts/infra/<task-id>/`.
Return a plain-text summary (max 400 words) via the Agent tool response.
```

---

## Task 3: Update install.sh and routing.json

**Files:**
- Modify: `install.sh`
- Modify: `shared/routing.json`

- [ ] **Step 1: Add `infra` to all 5 team loops in install.sh**

There are 5 occurrences of `for team in backend frontend mobile market product data research support`. Add `infra` to each:

```bash
for team in backend frontend mobile market product data research support infra; do
```

Run:
```bash
grep -n "for team in" install.sh
```

Expected: 5 lines. Update all 5.

- [ ] **Step 2: Add infra routing rule to shared/routing.json**

Insert before the closing `]` of the `rules` array:

```json
,
{
  "team": "infra",
  "keywords": ["infrastructure", "terraform", "IaC", "provision", "cloud resource", "VPC", "IAM", "S3", "EC2", "RDS", "IaC review", "terraform review", "terraform audit"],
  "description": "Cloud infrastructure as code (Terraform), IaC review, and audit tasks"
}
```

- [ ] **Step 3: Run full test suite to verify all pass**

```bash
bash tests/install.test.sh 2>&1
```

Expected output ends with:
```
=== Results ===
  Passed: 36
  Failed: 0
```

(31 existing + 5 new infra assertions)

- [ ] **Step 4: Commit**

```bash
git add teams/infra/ tests/install.test.sh install.sh shared/routing.json
git commit -m "feat(infra): add infra team — lead, iac-engineer, reviewer"
```

---

## Task 4: Update READMEs

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`

- [ ] **Step 1: Add infra row to README.md team table**

In the Overview table, add after the `backend` row:

```
| `infra` | lead, iac-engineer, reviewer | Terraform modules, IaC review, PR review, infrastructure audits |
```

- [ ] **Step 2: Add infra row to README.zh.md team table**

In the 概览 table, add after the `backend` row:

```
| `infra` | 3 | Terraform 模块编写、IaC 审查、PR Review、基础设施审计 |
```

- [ ] **Step 3: Commit**

```bash
git add README.md README.zh.md
git commit -m "docs: add infra team to README tables"
```
