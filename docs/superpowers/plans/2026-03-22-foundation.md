# aurorie-teams Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the repo foundation: directory scaffold, `install.sh` with all flags, shared orchestrator agent, file-handoff skill, routing config, and project templates.

**Architecture:** A shell-script-based installer copies versioned configuration files into a local project's `.claude/` directory. All routing is machine-readable JSON. All inter-agent context flows through a well-defined file protocol.

**Tech Stack:** bash, jq (JSON merge), standard POSIX utilities (`uuidgen`/`python3`, `cp`, `mkdir`). All agent/skill files are Markdown. No runtime dependencies beyond Claude Code.

**Spec:** `docs/superpowers/specs/2026-03-22-aurorie-teams-design.md`

---

## File Map

| File | Responsibility |
|------|---------------|
| `VERSION` | Single semver string for the repo |
| `CHANGELOG.md` | Human-readable version history |
| `README.md` | Install instructions and quickstart |
| `tests/install.test.sh` | Bash tests for install.sh (written first — TDD) |
| `install.sh` | Installer: copies agents/skills/workflows, merges MCP configs, manages versions |
| `shared/agents/orchestrator.md` | Top-level dispatcher agent definition |
| `shared/skills/file-handoff/SKILL.md` | Inter-agent artifact protocol (required by all agents) |
| `shared/routing.json` | Machine-readable team routing rules |
| `shared/mcp.json` | Global MCP server definitions |
| `templates/CLAUDE.md.template` | Local project CLAUDE.md starter |
| `templates/.gitignore.template` | Workspace gitignore block |

---

## Task 1: Repo Scaffold and VERSION

**Files:** `VERSION`, `CHANGELOG.md`, `README.md`

- [ ] **Step 1: Initialize git repo and write VERSION**

```bash
cd /Users/aurorie/workspace/aurorie/aurorie-teams
git init
echo "1.0.0" > VERSION
```

- [ ] **Step 2: Create CHANGELOG.md**

```markdown
# Changelog

## 1.0.0 — 2026-03-22

### Added
- Initial release
- Six teams: engineer, market, product, data, research, support
- install.sh with --force-workflows, --detect-orphans, --yes flags
- Shared orchestrator agent and file-handoff skill
- Machine-readable routing.json
- MCP secrets via shell env var references
```

- [ ] **Step 3: Create README.md**

```markdown
# aurorie-teams

Company-wide Claude Code agent configuration library.

## Requirements

- macOS or Linux (bash 3.2+)
- `jq` — `brew install jq` / `apt install jq`
- `uuidgen` or `python3`
- Node.js (for `npx`-based MCP servers)

## Install

```bash
# From your local project root:
git clone https://github.com/aurorie/aurorie-teams.git /tmp/aurorie-teams
cd /path/to/your-project
/tmp/aurorie-teams/install.sh
```

## Flags

| Flag | Effect |
|------|--------|
| (none) | Default install |
| `--force-workflows` | Overwrite local workflow + routing.json overrides (prompts for confirmation) |
| `--yes` | Skip confirmation prompts (for CI, use with --force-workflows) |
| `--detect-orphans` | Report stale agent/skill files not in repo |

## Upgrade

```bash
cd /tmp/aurorie-teams && git pull
cd /path/to/your-project && /tmp/aurorie-teams/install.sh
```

## Environment Variables for MCP

Set these in your shell profile before starting Claude Code:

```bash
export GITHUB_TOKEN=...
export EXA_API_KEY=...
export FIRECRAWL_API_KEY=...
```

## Customizing

- **Workflows:** Edit `.claude/workflows/<team>.md`
- **Routing:** Edit `.claude/routing.json`
- **CLAUDE.md:** Edit `CLAUDE.md` in your project root
```

- [ ] **Step 4: Commit**

```bash
git add VERSION CHANGELOG.md README.md
git commit -m "chore: initial repo scaffold with VERSION and README"
```

---

## Task 2: Team Directory Stubs

**Files:** `teams/*/` directories, agent stubs, skill stubs, workflow stubs, mcp.json stubs

These stubs give `install.sh` real files to work with during tests. Full content is written in Plan 2.

- [ ] **Step 1: Create all directory structure**

```bash
for team in engineer market product data research support; do
  mkdir -p teams/$team/agents teams/$team/skills
done
mkdir -p shared/agents shared/skills/file-handoff templates tests
```

- [ ] **Step 2: Write stub TEAM.md for each team**

`teams/engineer/TEAM.md`:
```markdown
# Engineer Team

## Responsibility
Owns all code development, infrastructure, testing, and technical operations.
Does not own product requirements or business strategy.

## Agents
| Agent | Role |
|-------|------|
| aurorie-engineer-lead | Task intake and internal routing |
| aurorie-engineer-frontend | UI components, styles, client-side logic |
| aurorie-engineer-backend | APIs, databases, business logic |
| aurorie-engineer-devops | CI/CD, deployment, infrastructure |
| aurorie-engineer-qa | Testing, quality assurance |

## Input Contract
Provide: task description, acceptance criteria, any relevant codebase context.

## Output Contract
Writes artifacts to `.claude/workspace/artifacts/engineer/<task-id>/`.
Returns implementation summary via Agent tool response.
```

Repeat for each team with appropriate content (1 paragraph each):
- `teams/market/TEAM.md` — owns marketing, SEO, content, analytics
- `teams/product/TEAM.md` — owns PRDs, roadmap, UX
- `teams/data/TEAM.md` — owns analysis, pipelines, reporting
- `teams/research/TEAM.md` — owns research, synthesis, information gathering
- `teams/support/TEAM.md` — owns customer support, ticket triage

- [ ] **Step 3: Write stub workflow.md for each team**

`teams/engineer/workflow.md`:
```markdown
# Engineer Workflow

## Feature Development
Trigger: new feature request or code change task

Steps:
1. aurorie-engineer-lead reviews requirements and creates task breakdown
2. Assign to aurorie-engineer-backend and/or aurorie-engineer-frontend based on scope
3. aurorie-engineer-qa validates acceptance criteria
4. Write output to `.claude/workspace/artifacts/engineer/<task-id>/`

## Bug Fix
Trigger: bug report or failing test

Steps:
1. aurorie-engineer-lead identifies affected component
2. Assign to relevant specialist
3. aurorie-engineer-qa verifies fix
4. Write output to `.claude/workspace/artifacts/engineer/<task-id>/`
```

Repeat minimal workflow.md for: market, product, data, research, support.

- [ ] **Step 4: Write stub agent files**

`teams/engineer/agents/aurorie-engineer-lead.md`:
```markdown
# Engineer Lead

## Role
Receives engineering tasks, decomposes them, and routes to specialist agents.

## Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required

## Sub-Agents
| Agent | When to use |
|-------|-------------|
| aurorie-engineer-frontend | UI, components, styles |
| aurorie-engineer-backend | APIs, databases, business logic |
| aurorie-engineer-devops | CI/CD, deployment, infra |
| aurorie-engineer-qa | Testing and validation |

## Workflow
Read `.claude/workflows/engineer.md` to determine execution steps.

## Input
Read task description and `input_context` from the task file.
If `input_context` contains a line starting with `artifact: `, read that file before starting work.

## Output
Write artifacts to `.claude/workspace/artifacts/engineer/<task-id>/`.
Return a plain-text summary (max 400 words) via the Agent tool response.
```

Create minimal specialist stubs (role + skills + input/output sections, no sub-agents):
- `engineer`: `aurorie-engineer-frontend.md`, `aurorie-engineer-backend.md`, `aurorie-engineer-devops.md`, `aurorie-engineer-qa.md`
- `market`: `aurorie-market-lead.md`, `aurorie-market-seo.md`, `aurorie-market-content.md`, `aurorie-market-analytics.md`
- `product`: `aurorie-product-lead.md`, `aurorie-product-pm.md`, `aurorie-product-ux.md`
- `data`: `aurorie-data-lead.md`, `aurorie-data-analyst.md`, `aurorie-data-pipeline.md`, `aurorie-data-reporting.md`
- `research`: `aurorie-research-lead.md`, `aurorie-research-web.md`, `aurorie-research-synthesizer.md`
- `support`: `aurorie-support-lead.md`, `aurorie-support-triage.md`, `aurorie-support-responder.md`, `aurorie-support-escalation.md`

- [ ] **Step 5: Write stub skill directories**

`teams/engineer/skills/tdd/SKILL.md`:
```markdown
# TDD Skill

Use when writing new code or fixing bugs.

## Process
1. Write a failing test first
2. Run it to confirm it fails
3. Write minimal implementation
4. Run tests to confirm pass
5. Refactor if needed
```

Create one stub skill per team:
- `teams/engineer/skills/code-review/SKILL.md` — stub
- `teams/engineer/skills/deployment/SKILL.md` — stub
- `teams/market/skills/content-engine/SKILL.md` — stub
- `teams/market/skills/seo-audit/SKILL.md` — stub
- `teams/product/skills/prd-writing/SKILL.md` — stub
- `teams/product/skills/user-story/SKILL.md` — stub
- `teams/data/skills/sql-patterns/SKILL.md` — stub
- `teams/data/skills/visualization/SKILL.md` — stub
- `teams/research/skills/deep-research/SKILL.md` — stub
- `teams/research/skills/exa-search/SKILL.md` — stub
- `teams/support/skills/customer-comms/SKILL.md` — stub

- [ ] **Step 6: Write mcp.json for each team**

`teams/engineer/mcp.json`:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    }
  }
}
```

`teams/research/mcp.json`:
```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": { "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}" }
    },
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": { "EXA_API_KEY": "${EXA_API_KEY}" }
    }
  }
}
```

Remaining teams (market, product, data, support) with no MCP yet:
```json
{
  "mcpServers": {}
}
```

- [ ] **Step 7: Commit**

```bash
git add teams/
git commit -m "chore: add team directory stubs for install.sh testing"
```

---

## Task 3: Shared Layer Files

**Files:** `shared/routing.json`, `shared/mcp.json`, `shared/agents/orchestrator.md`, `shared/skills/file-handoff/SKILL.md`, `templates/CLAUDE.md.template`, `templates/.gitignore.template`

- [ ] **Step 1: Write shared/routing.json**

```json
{
  "version": "1",
  "rules": [
    {
      "team": "engineer",
      "keywords": ["code", "build", "deploy", "bug", "test", "api", "database", "infrastructure", "refactor", "CI", "PR", "fix", "implement", "feature"],
      "description": "Code, infrastructure, and technical implementation tasks"
    },
    {
      "team": "market",
      "keywords": ["marketing", "SEO", "content", "social", "campaign", "blog", "copywriting", "analytics", "growth", "acquisition"],
      "description": "Marketing, content, and growth tasks"
    },
    {
      "team": "product",
      "keywords": ["product", "feature", "PRD", "requirements", "roadmap", "UX", "user story", "wireframe", "design", "specification"],
      "description": "Product definition, requirements, and UX tasks"
    },
    {
      "team": "data",
      "keywords": ["data", "report", "dashboard", "SQL", "metrics", "pipeline", "analysis", "chart", "query", "insight"],
      "description": "Data analysis, reporting, and pipeline tasks"
    },
    {
      "team": "research",
      "keywords": ["research", "investigate", "find", "compare", "summarize", "market research", "competitor", "survey", "synthesis"],
      "description": "Research, synthesis, and information gathering tasks"
    },
    {
      "team": "support",
      "keywords": ["support", "customer", "ticket", "issue", "complaint", "help", "response", "escalate", "refund"],
      "description": "Customer support and issue response tasks"
    }
  ],
  "fallback": "orchestrator-clarify"
}
```

- [ ] **Step 2: Write shared/mcp.json**

```json
{
  "mcpServers": {}
}
```

- [ ] **Step 3: Write shared/agents/orchestrator.md**

```markdown
# Orchestrator

## Role
Top-level dispatcher. Receives user requests, reads routing rules, invokes team leads,
and synthesizes results for the user.

## Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all task file writes

## Routing

1. Read `.claude/routing.json`.
2. Match user request intent against rules (keywords are hints, not exact matches).
3. If one team matches: single dispatch (Step A).
4. If multiple teams match: parallel dispatch (Step B).
5. If no team matches (`fallback: "orchestrator-clarify"`): ask the user one clarifying
   question, then re-evaluate.

### Step A — Single Dispatch
1. Generate task-id via Bash tool: `uuidgen | tr '[:upper:]' '[:lower:]'`
   Fallback: `python3 -c "import uuid; print(uuid.uuid4())"`
2. Write task file to `.claude/workspace/tasks/<task-id>.json`:
   ```json
   {
     "task_id": "<generated-uuid>",
     "created_at": "<ISO8601>",
     "description": "<user request>",
     "assigned_team": "<team>",
     "status": "pending",
     "input_context": "",
     "artifact_path": ".claude/workspace/artifacts/<team>/<task-id>/"
   }
   ```
3. Invoke team lead via Agent tool with prompt:
   ```
   Task file: .claude/workspace/tasks/<task-id>.json
   Read the task file and execute your assigned workflow.
   Return a plain-text summary (max 400 words) of what was produced.
   ```
4. Return Agent tool result to user.

### Step B — Parallel Dispatch
1. Generate one task-id per team via Bash tool.
2. Write one task file per team.
3. Invoke all relevant team leads simultaneously via parallel Agent tool calls.
4. Await all responses.
5. Synthesize summaries (each max 400 words). Return combined summary to user.

## Sequential Cross-Team Workflows
Defined as multi-step sequences in the project's CLAUDE.md — not as a single
orchestrator invocation. Each step invokes the orchestrator or a team lead with
`input_context` referencing the prior artifact via `artifact: <path>` syntax.

## Failure Handling
If a team lead returns a response prefixed with `FAILED: `:
surface the failure message to the user immediately. Do not retry automatically.
```

- [ ] **Step 4: Write shared/skills/file-handoff/SKILL.md**

```markdown
# File Handoff Protocol

Required skill for all agents. Use for every artifact write and context read.

## Writing Output
1. Create artifact directory via Bash tool:
   `mkdir -p .claude/workspace/artifacts/<team>/<task-id>/`
2. Write primary output files using lowercase kebab-case names
   (e.g., `prd.md`, `code-review.md`, `seo-report.md`).
3. Write `summary.md` last — one paragraph: what was produced, where it lives, key findings.
4. Update `status` in the task file to `"completed"` or `"failed"` using the Write tool.
5. Return the contents of `summary.md` as your Agent tool response (max 400 words).

## Reading Input
1. Read the task file at the path provided in your invocation prompt.
2. Read `description` for the task goal.
3. Scan `input_context` line by line. For any line starting with `artifact: `,
   read that file path before starting work.

## Artifact Naming
- Lowercase kebab-case only (e.g., `frontend-implementation.md`, `market-analysis.md`).
- No spaces or special characters.
- One primary output file per specialist agent execution.
```

- [ ] **Step 5: Write templates/CLAUDE.md.template**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project Context

[Describe your project here. Agents read this for background context.]

## Agent Teams

This project uses aurorie-teams. Agents are in `.claude/agents/`.

Routing rules are in `.claude/routing.json` — edit to customize which keywords
route to which team.

To invoke: use the `orchestrator` agent for most tasks, or invoke a team lead
directly (e.g., `aurorie-engineer-lead`) for single-team work.

## Sequential Workflows

Define multi-step cross-team workflows here. Example:

### Feature Development (Product → Engineer)
1. Invoke `aurorie-product-lead` to write a PRD.
   When complete, find the actual task-id in `.claude/workspace/tasks/` and note the artifact path.
2. Invoke `aurorie-engineer-lead` with:
   `input_context: "artifact: .claude/workspace/artifacts/product/<actual-task-id>/prd.md\nImplement the features described in the PRD."`
   Replace `<actual-task-id>` with the UUID written by step 1.

## Workspace

Runtime files in `.claude/workspace/` (gitignored):
- `tasks/` — one JSON file per active task
- `artifacts/` — team outputs as `<team>/<task-id>/`

## Customizing

- Workflow behavior: edit `.claude/workflows/<team>.md`
- Routing rules: edit `.claude/routing.json`
```

- [ ] **Step 6: Write templates/.gitignore.template**

```
# aurorie-teams runtime workspace — local only, do not commit
.claude/workspace/
```

- [ ] **Step 7: Commit**

```bash
git add shared/ templates/
git commit -m "feat: add shared orchestrator, file-handoff skill, routing config, and templates"
```

---

## Task 4: Write Failing Tests (TDD — before install.sh)

**Files:** `tests/install.test.sh`

Write the full test suite now. Every test will fail until Task 5 implements `install.sh`.

- [ ] **Step 1: Write tests/install.test.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

PASS=0; FAIL=0
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "  ✓ $desc"; ((PASS++))
  else
    echo "  ✗ $desc" >&2
    echo "    expected: '$expected'" >&2
    echo "    got:      '$actual'" >&2
    ((FAIL++))
  fi
}

assert_file_exists() {
  local desc="$1" path="$2"
  if [[ -e "$path" ]]; then
    echo "  ✓ $desc"; ((PASS++))
  else
    echo "  ✗ $desc (missing: $path)" >&2; ((FAIL++))
  fi
}

assert_file_absent() {
  local desc="$1" path="$2"
  if [[ ! -e "$path" ]]; then
    echo "  ✓ $desc"; ((PASS++))
  else
    echo "  ✗ $desc (should not exist: $path)" >&2; ((FAIL++))
  fi
}

assert_file_contains() {
  local desc="$1" path="$2" pattern="$3"
  if grep -qF "$pattern" "$path" 2>/dev/null; then
    echo "  ✓ $desc"; ((PASS++))
  else
    echo "  ✗ $desc (pattern '$pattern' not found in $path)" >&2; ((FAIL++))
  fi
}

# ── setup temp project ────────────────────────────────────────────────────────
TMPDIR_PROJECT="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_PROJECT"' EXIT
cd "$TMPDIR_PROJECT"
touch .gitignore

echo ""
echo "=== Test: default install ==="
"$REPO_ROOT/install.sh" > /dev/null

assert_file_exists "orchestrator.md installed"      ".claude/agents/orchestrator.md"
assert_file_exists "aurorie-engineer-lead.md installed"     ".claude/agents/aurorie-engineer-lead.md"
assert_file_exists "tdd skill installed"            ".claude/skills/tdd/SKILL.md"
assert_file_exists "file-handoff skill installed"   ".claude/skills/file-handoff/SKILL.md"
assert_file_exists "engineer workflow installed"    ".claude/workflows/engineer.md"
assert_file_exists "routing.json installed"         ".claude/routing.json"
assert_file_exists "settings.json generated"        ".claude/settings.json"
assert_file_exists "CLAUDE.md generated"            "CLAUDE.md"
assert_file_exists ".aurorie-teams-version written" ".claude/.aurorie-teams-version"
assert_file_contains ".gitignore has workspace entry" ".gitignore" ".claude/workspace/"

echo ""
echo "=== Test: routing.json skipped on second install ==="
echo '{"version":"custom"}' > .claude/routing.json
"$REPO_ROOT/install.sh" > /dev/null
routing_version="$(cat .claude/routing.json)"
assert_eq "custom routing.json preserved" '{"version":"custom"}' "$routing_version"

echo ""
echo "=== Test: --force-workflows --yes overwrites routing.json ==="
"$REPO_ROOT/install.sh" --force-workflows --yes > /dev/null 2>&1
routing_v="$(jq -r '.version' .claude/routing.json)"
assert_eq "routing.json reset to repo version" "1" "$routing_v"

echo ""
echo "=== Test: workflow skipped if exists ==="
echo "custom workflow" > .claude/workflows/engineer.md
"$REPO_ROOT/install.sh" > /dev/null
assert_file_contains "custom workflow preserved" ".claude/workflows/engineer.md" "custom workflow"

echo ""
echo "=== Test: CLAUDE.md skipped if exists ==="
echo "custom content" > CLAUDE.md
"$REPO_ROOT/install.sh" > /dev/null
assert_file_contains "existing CLAUDE.md preserved" "CLAUDE.md" "custom content"

echo ""
echo "=== Test: settings.json has mcpServers ==="
mcp_count="$(jq -r '.mcpServers | keys | length' .claude/settings.json)"
assert_eq "settings.json has MCP entries" "true" "$([[ "$mcp_count" -ge 1 ]] && echo true || echo false)"

echo ""
echo "=== Test: settings.json preserves locally-added MCP server ==="
jq '.mcpServers["local-custom"] = {"command":"custom","args":[]}' .claude/settings.json > .claude/settings.json.tmp
mv .claude/settings.json.tmp .claude/settings.json
"$REPO_ROOT/install.sh" > /dev/null
has_local="$(jq -r '.mcpServers | has("local-custom")' .claude/settings.json)"
assert_eq "locally-added MCP server preserved after reinstall" "true" "$has_local"

echo ""
echo "=== Test: version file matches repo VERSION ==="
installed_version="$(cat .claude/.aurorie-teams-version)"
repo_version="$(cat "$REPO_ROOT/VERSION")"
assert_eq ".aurorie-teams-version matches repo VERSION" "$repo_version" "$installed_version"

echo ""
echo "=== Test: .gitignore not duplicated on second install ==="
"$REPO_ROOT/install.sh" > /dev/null
count="$(grep -c ".claude/workspace/" .gitignore)"
assert_eq ".gitignore entry not duplicated" "1" "$count"

echo ""
echo "=== Test: --force-workflows without --yes aborts in non-TTY ==="
# Simulate non-TTY by redirecting stdin from /dev/null
echo "custom-again" > .claude/routing.json
"$REPO_ROOT/install.sh" --force-workflows < /dev/null > /dev/null 2>&1 || true
still_custom="$(cat .claude/routing.json)"
assert_eq "--force-workflows without --yes aborts (non-TTY)" "custom-again" "$still_custom"

echo ""
echo "=== Test: --detect-orphans reports stale agent ==="
echo "stub" > .claude/agents/old-legacy-agent.md
output="$("$REPO_ROOT/install.sh" --detect-orphans 2>&1)"
assert_eq "--detect-orphans reports orphaned agent" "true" \
  "$([[ "$output" == *"old-legacy-agent.md"* ]] && echo true || echo false)"

echo ""
echo "=== Results ==="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
```

- [ ] **Step 2: Make executable**

```bash
chmod +x tests/install.test.sh
```

- [ ] **Step 3: Run tests — verify they fail (install.sh doesn't exist yet)**

```bash
bash tests/install.test.sh 2>&1 | head -5
```

Expected: error like `install.sh: No such file or directory` — confirming tests run before implementation.

- [ ] **Step 4: Commit failing tests**

```bash
git add tests/
git commit -m "test: add install.sh integration tests (failing — TDD)"
```

---

## Task 5: Implement install.sh

**Files:** `install.sh`

Implement to make all tests in Task 4 pass.

- [ ] **Step 1: Write install.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

# ── resolve paths ────────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="$PWD/.claude"
REPO_VERSION="$(cat "$REPO_ROOT/VERSION")"
INSTALLED_VERSION_FILE="$TARGET/.aurorie-teams-version"
FORCE_WORKFLOWS=false
DETECT_ORPHANS=false
YES=false

# ── parse flags ───────────────────────────────────────────────────────────────
for arg in "$@"; do
  case $arg in
    --force-workflows) FORCE_WORKFLOWS=true ;;
    --detect-orphans)  DETECT_ORPHANS=true ;;
    --yes)             YES=true ;;
  esac
done

# ── check dependencies ────────────────────────────────────────────────────────
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq is required. Install with: brew install jq  or  apt install jq" >&2
  exit 1
fi

# ── print version transition ─────────────────────────────────────────────────
if [[ -f "$INSTALLED_VERSION_FILE" ]]; then
  PREV_VERSION="$(cat "$INSTALLED_VERSION_FILE")"
  if [[ "$PREV_VERSION" != "$REPO_VERSION" ]]; then
    echo "Updating aurorie-teams: $PREV_VERSION → $REPO_VERSION"
    echo "See $REPO_ROOT/CHANGELOG.md for what changed."
  else
    echo "Installing aurorie-teams $REPO_VERSION"
  fi
else
  echo "Installing aurorie-teams $REPO_VERSION"
fi

# ── create target directories ────────────────────────────────────────────────
mkdir -p "$TARGET/agents" "$TARGET/skills" "$TARGET/workflows" \
         "$TARGET/workspace/tasks" "$TARGET/workspace/artifacts"

# ── install agents (always overwrite) ────────────────────────────────────────
cp "$REPO_ROOT/shared/agents/orchestrator.md" "$TARGET/agents/"
for team in engineer market product data research support; do
  for agent_file in "$REPO_ROOT/teams/$team/agents/"*.md; do
    cp "$agent_file" "$TARGET/agents/"
  done
done
echo "  ✓ agents installed"

# ── install skills (always overwrite) ────────────────────────────────────────
cp -r "$REPO_ROOT/shared/skills/"* "$TARGET/skills/"
for team in engineer market product data research support; do
  cp -r "$REPO_ROOT/teams/$team/skills/"* "$TARGET/skills/"
done
echo "  ✓ skills installed"

# ── collect workflow + routing files that exist locally ───────────────────────
OVERWRITE_CANDIDATES=()
if [[ "$FORCE_WORKFLOWS" == true ]]; then
  for team in engineer market product data research support; do
    dest="$TARGET/workflows/$team.md"
    [[ -f "$dest" ]] && OVERWRITE_CANDIDATES+=("$dest")
  done
  dest="$TARGET/routing.json"
  [[ -f "$dest" ]] && OVERWRITE_CANDIDATES+=("$dest")
fi

# ── confirm overwrite if needed ───────────────────────────────────────────────
if [[ ${#OVERWRITE_CANDIDATES[@]} -gt 0 ]]; then
  if [[ "$YES" == false ]]; then
    # Abort silently if stdin is not a TTY (non-interactive / CI without --yes)
    if [[ ! -t 0 ]]; then
      echo "ERROR: --force-workflows requires --yes in non-interactive mode." >&2
      exit 1
    fi
    echo ""
    echo "The following files exist locally and will be overwritten:"
    for f in "${OVERWRITE_CANDIDATES[@]}"; do echo "  $f"; done
    echo ""
    read -r -p "Overwrite these files? [y/N] " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
      echo "Aborted."
      exit 0
    fi
  fi
fi

# ── install workflows ─────────────────────────────────────────────────────────
for team in engineer market product data research support; do
  src="$REPO_ROOT/teams/$team/workflow.md"
  dest="$TARGET/workflows/$team.md"
  if [[ "$FORCE_WORKFLOWS" == true ]]; then
    cp "$src" "$dest"
    echo "  WARNING: overwriting $dest" >&2
  else
    # portable skip-if-exists (avoids cp -n portability issues)
    [[ -f "$dest" ]] || cp "$src" "$dest"
  fi
done
echo "  ✓ workflows installed (existing local overrides preserved)"

# ── install routing.json ──────────────────────────────────────────────────────
routing_dest="$TARGET/routing.json"
if [[ "$FORCE_WORKFLOWS" == true ]]; then
  cp "$REPO_ROOT/shared/routing.json" "$routing_dest"
  echo "  WARNING: overwriting $routing_dest" >&2
else
  [[ -f "$routing_dest" ]] || cp "$REPO_ROOT/shared/routing.json" "$routing_dest"
fi
echo "  ✓ routing.json installed"

# ── merge mcp configs into settings.json ─────────────────────────────────────
settings_dest="$TARGET/settings.json"
merged_mcp="{}"

# collect all mcp.json paths: shared first, then teams alphabetically (hardcoded for safety)
mcp_files=("$REPO_ROOT/shared/mcp.json")
for team in engineer market product data research support; do
  mcp_file="$REPO_ROOT/teams/$team/mcp.json"
  [[ -f "$mcp_file" ]] && mcp_files+=("$mcp_file")
done

for mcp_file in "${mcp_files[@]}"; do
  incoming="$(jq '.mcpServers // {}' "$mcp_file")"
  # check for key collisions
  collisions="$(jq -rn \
    --argjson a "$merged_mcp" \
    --argjson b "$incoming" \
    '($a | keys) as $ak | ($b | keys) as $bk | $ak - ($ak - $bk) | .[]' 2>/dev/null || true)"
  if [[ -n "$collisions" ]]; then
    echo "WARNING: MCP server key collision in $mcp_file: $collisions (last definition wins)" >&2
  fi
  merged_mcp="$(jq -s '.[0] * .[1]' <(echo "$merged_mcp") <(echo "$incoming"))"
done

if [[ -f "$settings_dest" ]]; then
  # validate existing settings.json
  if ! jq . "$settings_dest" &>/dev/null; then
    echo "WARNING: existing settings.json is malformed — backing up to settings.json.bak" >&2
    cp "$settings_dest" "${settings_dest}.bak"
    echo "{}" > "$settings_dest"
  fi
  # merge: preserve all non-mcpServers keys; locally-added entries kept, repo entries overwrite matching keys
  existing_mcp="$(jq '.mcpServers // {}' "$settings_dest")"
  # existing_mcp first, then merged_mcp overwrites matching keys
  final_mcp="$(jq -s '.[0] * .[1]' <(echo "$existing_mcp") <(echo "$merged_mcp"))"
  jq --argjson mcp "$final_mcp" '. + {mcpServers: $mcp}' "$settings_dest" > "${settings_dest}.tmp"
  mv "${settings_dest}.tmp" "$settings_dest"
else
  jq -n --argjson mcp "$merged_mcp" '{mcpServers: $mcp}' > "$settings_dest"
fi
echo "  ✓ settings.json merged"

# ── generate CLAUDE.md if absent ─────────────────────────────────────────────
if [[ ! -f "CLAUDE.md" ]]; then
  cp "$REPO_ROOT/templates/CLAUDE.md.template" "CLAUDE.md"
  echo "  ✓ CLAUDE.md generated from template"
else
  echo "  - CLAUDE.md already exists, skipping"
fi

# ── append .gitignore block if not present ────────────────────────────────────
gitignore_marker=".claude/workspace/"
if [[ ! -f ".gitignore" ]] || ! grep -qF "$gitignore_marker" ".gitignore"; then
  { echo ""; cat "$REPO_ROOT/templates/.gitignore.template"; } >> ".gitignore"
  echo "  ✓ .gitignore updated"
else
  echo "  - .gitignore already contains workspace entry, skipping"
fi

# ── write installed version ───────────────────────────────────────────────────
echo "$REPO_VERSION" > "$INSTALLED_VERSION_FILE"
echo "  ✓ version recorded: $REPO_VERSION"

# ── detect orphans ────────────────────────────────────────────────────────────
if [[ "$DETECT_ORPHANS" == true ]]; then
  echo ""
  echo "Checking for orphaned files..."

  # build list of expected agent basenames
  repo_agents=("orchestrator.md")
  for team in engineer market product data research support; do
    for f in "$REPO_ROOT/teams/$team/agents/"*.md; do
      [[ -f "$f" ]] && repo_agents+=("$(basename "$f")")
    done
  done

  orphaned_agents=()
  for f in "$TARGET/agents/"*.md; do
    [[ -f "$f" ]] || continue
    name="$(basename "$f")"
    found=false
    for r in "${repo_agents[@]}"; do [[ "$r" == "$name" ]] && found=true && break; done
    [[ "$found" == false ]] && orphaned_agents+=("$f")
  done

  if [[ ${#orphaned_agents[@]} -gt 0 ]]; then
    echo "Orphaned agents (not in repo):"
    for f in "${orphaned_agents[@]}"; do echo "  $f"; done
  else
    echo "  No orphaned agents found."
  fi

  # build list of expected skill directory names
  repo_skills=()
  for s in "$REPO_ROOT/shared/skills/"*/; do
    [[ -d "$s" ]] && repo_skills+=("$(basename "$s")")
  done
  for team in engineer market product data research support; do
    for s in "$REPO_ROOT/teams/$team/skills/"*/; do
      [[ -d "$s" ]] && repo_skills+=("$(basename "$s")")
    done
  done

  orphaned_skills=()
  for d in "$TARGET/skills/"*/; do
    [[ -d "$d" ]] || continue
    name="$(basename "$d")"
    found=false
    for r in "${repo_skills[@]}"; do [[ "$r" == "$name" ]] && found=true && break; done
    [[ "$found" == false ]] && orphaned_skills+=("$d")
  done

  if [[ ${#orphaned_skills[@]} -gt 0 ]]; then
    echo "Orphaned skills (not in repo):"
    for d in "${orphaned_skills[@]}"; do echo "  $d"; done
  else
    echo "  No orphaned skills found."
  fi
fi

echo ""
echo "aurorie-teams $REPO_VERSION installed to $TARGET/"
```

- [ ] **Step 2: Make executable**

```bash
chmod +x install.sh
```

- [ ] **Step 3: Run tests — verify all pass**

```bash
bash tests/install.test.sh
```

Expected: `Failed: 0`

- [ ] **Step 4: Fix any failures, rerun until green**

If a test fails, fix the corresponding logic in `install.sh` and rerun:
```bash
bash tests/install.test.sh
```

- [ ] **Step 5: Commit**

```bash
git add install.sh
git commit -m "feat: implement install.sh — all tests passing"
```

---

## Task 6: Validation Pass

- [ ] **Step 1: Run install into a fresh temp project**

```bash
TMPDIR="$(mktemp -d)"
cd "$TMPDIR"
touch .gitignore
bash /Users/aurorie/workspace/aurorie/aurorie-teams/install.sh
```

Expected output ends with:
```
aurorie-teams 1.0.0 installed to <path>/.claude/
```

- [ ] **Step 2: Verify file structure**

```bash
find .claude -not -path "*/workspace/*" | sort
```

Expected: orchestrator.md, all team agents, all skills, all workflows, routing.json, settings.json, .aurorie-teams-version all present.

- [ ] **Step 3: Verify settings.json is valid JSON with mcpServers**

```bash
jq '.mcpServers | keys' .claude/settings.json
```

Expected: array of MCP server names (at least `github`, `firecrawl`, `exa`).

- [ ] **Step 4: Verify routing.json is valid**

```bash
jq '.rules | length' .claude/routing.json
```

Expected: `6`

- [ ] **Step 5: Clean up and commit**

```bash
rm -rf "$TMPDIR"
cd /Users/aurorie/workspace/aurorie/aurorie-teams
git add -A
git commit -m "chore: foundation complete — install.sh, shared layer, all tests passing"
```

---

## Done

Foundation is complete when:
- `bash tests/install.test.sh` exits with `Failed: 0`
- `install.sh` runs cleanly into a fresh directory
- `settings.json` is valid JSON with `mcpServers`
- `routing.json` has 6 rules
- `.aurorie-teams-version` matches `VERSION`

**Next:** Plan 2 — Teams fills in full agent, skill, and workflow content for all six teams.
