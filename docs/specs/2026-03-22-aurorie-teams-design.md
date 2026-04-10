# aurorie-teams Design Spec

**Date:** 2026-03-22
**Status:** Draft v2

---

## Overview

`aurorie-teams` is a company-wide Claude Code configuration library hosted on GitHub. Developers pull the repo and run `install.sh` from their **local project root** to copy agents, skills, workflow templates, and routing config into `.claude/`. Each local project's `CLAUDE.md` describes the project; routing logic lives in a structured `routing.json` file, not in `CLAUDE.md`.

---

## Design Principles

- **Configuration vs. runtime separation** — the repo contains only definitions; runtime files (task state, artifacts) are local-only and gitignored.
- **Flat routing (two hops max)** — Orchestrator → Team Lead → Specialist Agent.
- **Base + override** — team workflow templates are skipped on reinstall unless `--force-workflows` is passed with explicit confirmation.
- **Machine-readable routing** — routing rules live in `.claude/routing.json`, not embedded in human-readable markdown.
- **Explicit secrets contract** — MCP environment variables reference shell env vars; no secrets stored in the repo.
- **Versioned releases** — the repo carries a `VERSION` file; `install.sh` records installed version in `.claude/.aurorie-teams-version`.

---

## Repo Structure

```
aurorie-teams/
├── README.md
├── VERSION                             # semver string, e.g. "1.0.0"
├── install.sh
│
├── teams/
│   ├── engineer/
│   │   ├── TEAM.md                     # human documentation only (not read by agents at runtime)
│   │   ├── workflow.md
│   │   ├── agents/
│   │   │   ├── aurorie-engineer-lead.md
│   │   │   ├── aurorie-engineer-frontend.md
│   │   │   ├── aurorie-engineer-backend.md
│   │   │   ├── aurorie-engineer-devops.md
│   │   │   └── aurorie-engineer-qa.md
│   │   ├── skills/
│   │   │   ├── tdd/SKILL.md
│   │   │   ├── code-review/SKILL.md
│   │   │   └── deployment/SKILL.md
│   │   └── mcp.json
│   │
│   ├── market/
│   │   ├── TEAM.md
│   │   ├── workflow.md
│   │   ├── agents/
│   │   │   ├── aurorie-market-lead.md
│   │   │   ├── aurorie-market-seo.md
│   │   │   ├── aurorie-market-content.md
│   │   │   └── aurorie-market-analytics.md
│   │   ├── skills/
│   │   │   ├── content-engine/SKILL.md
│   │   │   └── seo-audit/SKILL.md
│   │   └── mcp.json
│   │
│   ├── product/
│   │   ├── TEAM.md
│   │   ├── workflow.md
│   │   ├── agents/
│   │   │   ├── aurorie-product-lead.md
│   │   │   ├── aurorie-product-pm.md
│   │   │   └── aurorie-product-ux.md
│   │   ├── skills/
│   │   │   ├── prd-writing/SKILL.md
│   │   │   └── user-story/SKILL.md
│   │   └── mcp.json
│   │
│   ├── data/
│   │   ├── TEAM.md
│   │   ├── workflow.md
│   │   ├── agents/
│   │   │   ├── aurorie-data-lead.md
│   │   │   ├── aurorie-data-analyst.md
│   │   │   ├── aurorie-data-pipeline.md
│   │   │   └── aurorie-data-reporting.md
│   │   ├── skills/
│   │   │   ├── sql-patterns/SKILL.md
│   │   │   └── visualization/SKILL.md
│   │   └── mcp.json
│   │
│   ├── research/
│   │   ├── TEAM.md
│   │   ├── workflow.md
│   │   ├── agents/
│   │   │   ├── aurorie-research-lead.md
│   │   │   ├── aurorie-research-web.md
│   │   │   └── aurorie-research-synthesizer.md
│   │   ├── skills/
│   │   │   ├── deep-research/SKILL.md
│   │   │   └── exa-search/SKILL.md
│   │   └── mcp.json
│   │
│   └── support/
│       ├── TEAM.md
│       ├── workflow.md
│       ├── agents/
│       │   ├── aurorie-support-lead.md
│       │   ├── aurorie-support-triage.md
│       │   ├── aurorie-support-responder.md
│       │   └── aurorie-support-escalation.md
│       ├── skills/
│       │   └── customer-comms/SKILL.md
│       └── mcp.json
│
├── shared/
│   ├── agents/
│   │   └── aurorie-orchestrator.md
│   ├── skills/
│   │   └── file-handoff/SKILL.md
│   ├── routing.json                    # default routing rules (machine-readable)
│   └── mcp.json
│
└── templates/
    ├── CLAUDE.md.template
    └── .gitignore.template
```

---

## Local Project Structure (Post-Install)

`install.sh` must be run from the **local project root**. All paths are relative to that root.

```
my-project/
├── CLAUDE.md                           # project description; does NOT contain routing rules
└── .claude/
    ├── .aurorie-teams-version          # installed version string, e.g. "1.0.0"
    ├── agents/
    │   ├── aurorie-orchestrator.md
    │   ├── aurorie-engineer-lead.md
    │   └── ... (all team agents)
    ├── skills/
    │   ├── tdd/SKILL.md
    │   └── ...
    ├── workflows/
    │   ├── engineer.md
    │   ├── market.md
    │   ├── product.md
    │   ├── data.md
    │   ├── research.md
    │   └── support.md
    ├── routing.json                    # installed from shared/routing.json; locally overridable
    ├── settings.json                   # merged MCP config
    └── workspace/                      # gitignored — runtime only
        ├── tasks/                      # one JSON file per task
        └── artifacts/                  # team outputs: <team>/<task-id>/
```

---

## install.sh Behavior

**Invocation:** `./path/to/aurorie-teams/install.sh [flags]` run from the local project root.
- `REPO_ROOT` is resolved using `$(cd "$(dirname "$0")" && pwd)` (handles symlinks and relative paths).
- Install target: `$PWD/.claude/`.
- Required tools: `bash 3.2+`, `jq` (for JSON merge), `uuidgen` or `python3`.
- Supported OS: macOS and Linux. Windows is not supported.

### Install table

| Target | default | `--force-workflows` | `--detect-orphans` |
|--------|---------|--------------------|--------------------|
| `.claude/agents/` | overwrite | overwrite | report orphans, no delete |
| `.claude/skills/` | overwrite | overwrite | report orphans, no delete |
| `.claude/workflows/<team>.md` | skip if exists | prompt then overwrite | — |
| `.claude/routing.json` | skip if exists | overwrite (with same prompt as workflows) | — |
| `.claude/settings.json` | regenerate (merge) | regenerate (merge) | — |
| `CLAUDE.md` | generate if absent | generate if absent | — |
| `.gitignore` | append block if absent | append block if absent | — |
| `.claude/.aurorie-teams-version` | write/overwrite | write/overwrite | — |

### `--force-workflows` confirmation

Before overwriting any workflow file, the script prints the list of files to be overwritten and prompts:

```
The following workflow files have local content and will be overwritten:
  .claude/workflows/engineer.md
  .claude/workflows/market.md

Overwrite these files? [y/N]
```

Pass `--yes` to bypass the prompt (for CI environments). No backup is created; developers must commit or stash changes before running.

### `--detect-orphans`

Compares files in `.claude/agents/` and `.claude/skills/` against the repo. Prints files present locally but absent from the repo. No files are deleted. Output goes to stdout.

```
Orphaned agents (not in repo):
  .claude/agents/engineer-legacy.md

Orphaned skills (not in repo):
  .claude/skills/old-seo-audit/
```

### Version tracking

After install, writes the repo's `VERSION` string to `.claude/.aurorie-teams-version`. On subsequent installs, the script prints the version transition:

```
Updating aurorie-teams: 1.0.0 → 1.2.0
```

### Workflow file naming

`teams/<team>/workflow.md` is installed as `.claude/workflows/<team>.md`, where `<team>` is the directory name (e.g., `teams/engineer/workflow.md` → `.claude/workflows/engineer.md`).

### Orphaned files (non-detection mode)

Without `--detect-orphans`, `install.sh` does not remove stale files. Run `--detect-orphans` to find them.

---

## settings.json Merge Logic

`install.sh` merges MCP configs from:
1. `shared/mcp.json` (base)
2. Each `teams/<team>/mcp.json` (additive, alphabetical team order)

Each `mcp.json` uses this schema:

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "<executable>",
      "args": ["<arg1>", "<arg2>"],
      "env": { "<KEY>": "${ENV_VAR_NAME}" }
    }
  }
}
```

**`env` values must reference shell environment variables using `${VAR_NAME}` syntax. Never store actual secret values in `mcp.json`.** The shell environment must have the required variables set before Claude Code starts (e.g., via `.env` loaded by a shell profile, or CI secrets injection).

Merge strategy:
- All `"mcpServers"` objects are merged into a single `"mcpServers"` key.
- **Key collision:** if two files define the same server name, the last one wins (alphabetical team order). Warning printed to **stderr**.
- If `settings.json` already exists: non-`mcpServers` top-level keys are preserved. The `mcpServers` key is **merged** — locally-added server entries not present in any repo `mcp.json` are kept; repo entries overwrite matching keys by name.
- If `settings.json` is malformed JSON: warn to stderr, back up to `settings.json.bak`, write fresh from merge result.

Example merged output:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": { "EXA_API_KEY": "${EXA_API_KEY}" }
    }
  }
}
```

---

## Routing

### routing.json schema

The orchestrator reads `.claude/routing.json` — **not** `CLAUDE.md` — to determine which team to invoke. This file is machine-readable and locally overridable.

Default `shared/routing.json` installed as `.claude/routing.json`:

```json
{
  "version": "1",
  "rules": [
    {
      "team": "engineer",
      "keywords": ["code", "build", "deploy", "bug", "test", "api", "database", "infrastructure", "refactor", "CI", "PR"],
      "description": "Code, infrastructure, and technical implementation tasks"
    },
    {
      "team": "market",
      "keywords": ["marketing", "SEO", "content", "social", "campaign", "blog", "copywriting", "analytics"],
      "description": "Marketing, content, and growth tasks"
    },
    {
      "team": "product",
      "keywords": ["product", "feature", "PRD", "requirements", "roadmap", "UX", "user story", "wireframe"],
      "description": "Product definition, requirements, and UX tasks"
    },
    {
      "team": "data",
      "keywords": ["data", "report", "dashboard", "SQL", "metrics", "pipeline", "analysis", "chart"],
      "description": "Data analysis, reporting, and pipeline tasks"
    },
    {
      "team": "research",
      "keywords": ["research", "investigate", "find", "compare", "summarize", "market research", "competitor"],
      "description": "Research, synthesis, and information gathering tasks"
    },
    {
      "team": "support",
      "keywords": ["support", "customer", "ticket", "issue", "complaint", "help", "response"],
      "description": "Customer support and issue response tasks"
    }
  ],
  "fallback": "aurorie-orchestrator-clarify"
}
```

Routing behavior:
1. The orchestrator matches the user request against `keywords` in each rule using LLM judgment (keywords are hints, not exact matches).
2. If one team clearly matches: dispatch to that team's lead.
3. If multiple teams match: dispatch in parallel.
4. If no rule matches (`fallback: "aurorie-orchestrator-clarify"`): ask the user a clarifying question before routing.
5. `routing.json` is skipped on reinstall (`cp -n`). Developers edit `.claude/routing.json` to customize routing without losing changes.

---

## Skill Invocation Contract

Skills are `SKILL.md` files in `.claude/skills/<skill-name>/`. Agents invoke skills by reading the skill file at the start of execution and following its instructions. The invocation mechanism is prompt-based, not programmatic.

**How an agent invokes a skill:**

In the agent's `.md` file, list the skills it uses in a `## Skills` section:

```markdown
## Skills
- tdd: `.claude/skills/tdd/SKILL.md` — use when writing new code or fixing bugs
- code-review: `.claude/skills/code-review/SKILL.md` — use when reviewing a PR
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — use for all artifact writes
```

At runtime, the agent reads the listed skill files before executing the relevant step. The skill file's instructions take precedence over the agent's default behavior for that step.

**All agents must list `file-handoff` as a required skill.** It governs artifact writing and is always active.

---

## Orchestrator Agent Content

The `shared/agents/aurorie-orchestrator.md` file (installed as `.claude/agents/aurorie-orchestrator.md`):

```markdown
# Orchestrator

## Role
Top-level dispatcher. Receives user requests, determines which team(s) to invoke,
manages parallel and sequential dispatch, and synthesizes results for the user.

## Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all task file writes

## Routing
1. Read `.claude/routing.json` to load routing rules.
2. Match the user request against rules using intent judgment (keywords are hints).
3. If one team matches: single dispatch (step A).
4. If multiple teams match: parallel dispatch (step B).
5. If no team matches: ask one clarifying question, then re-evaluate.

### Step A — Single dispatch
1. Generate task-id: `uuidgen | tr '[:upper:]' '[:lower:]'` (fallback: `python3 -c "import uuid; print(uuid.uuid4())"`)
2. Write `.claude/workspace/tasks/<task-id>.json`
3. Invoke team lead via Agent tool with prompt:
   ```
   Task file: .claude/workspace/tasks/<task-id>.json
   Read the task file and execute your assigned workflow.
   Return a plain-text summary (max 400 words) of what was produced.
   ```
4. Return the Agent tool result to the user.

### Step B — Parallel dispatch
1. Generate one task-id per team.
2. Write one task file per team.
3. Invoke all team leads simultaneously via parallel Agent tool calls.
4. Await all responses.
5. Synthesize summaries and return to user.

## Sequential Cross-Team Workflows
For tasks where one team's output feeds another (e.g., product writes PRD → engineer implements):
- These are expressed as multi-step CLAUDE.md workflows, not single orchestrator invocations.
- Each step invokes the orchestrator (or a team lead directly) with an `input_context` referencing the previous team's artifact.
- Example: "Step 1: invoke aurorie-product-lead. Step 2: invoke aurorie-engineer-lead with artifact: path from step 1."

## Failure Handling
If a team lead returns a failure summary: surface it to the user immediately. Do not retry automatically.

## Summary Length
Return synthesized summaries to the user. If any team's summary exceeds 400 words, truncate to key points and reference the artifact path for full details.
```

---

## File Formats

### TEAM.md

`TEAM.md` is **human documentation only**. It is not read by agents at runtime. Its purpose is to help developers understand the team when browsing the repo.

```markdown
# <Team Name> Team

## Responsibility
One paragraph: what this team owns and what it explicitly does not own.

## Agents
| Agent | Role |
|-------|------|
| <team>-lead | Task intake and internal routing |
| <team>-<specialist> | Description |

## Input Contract
What information to include when invoking this team.

## Output Contract
What artifacts this team produces and where they are written.
```

### Agent file (`.claude/agents/<name>.md`)

```markdown
# <Agent Name>

## Role
One-line description.

## Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required
- <skill-name>: `.claude/skills/<skill-name>/SKILL.md` — when to use

## Routing (orchestrator only)
Keywords and intent signals that route to this team (for reference; authoritative source is routing.json).

## Sub-Agents (Lead agents only)
| Agent | When to use |
|-------|-------------|
| <name> | condition |

## Workflow
Read `.claude/workflows/<team>.md` to determine execution steps.

## Input
Read task description and `input_context` from the task file.
If `input_context` contains a line starting with `artifact: `, read that file path before starting work.

## Output
Write artifacts to `.claude/workspace/artifacts/<team>/<task-id>/`.
Return a plain-text summary (max 400 words) via the Agent tool response.
```

### Workflow template (`teams/<team>/workflow.md`)

```markdown
# <Team> Workflow

## <Workflow Name>
Trigger: <condition that activates this workflow>

Steps:
1. Step one
2. Step two
3. Write output to `.claude/workspace/artifacts/<team>/<task-id>/`
```

### CLAUDE.md template (`templates/CLAUDE.md.template`)

```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project Context
[Describe the project here. This is read by agents for background understanding.]

## Agent Teams

This project uses aurorie-teams. Invoke teams via the `orchestrator` agent or team leads directly.

Routing rules are defined in `.claude/routing.json` (edit to customize).

## Sequential Workflows

Define multi-step cross-team workflows here. Example:

### Feature Development
1. Invoke `aurorie-product-lead` to produce a PRD for the feature.
   After step 1 completes, read the actual `task-id` from `.claude/workspace/tasks/` to get the real artifact path.
2. Invoke `aurorie-engineer-lead` with:
   `input_context: "artifact: .claude/workspace/artifacts/product/<actual-task-id-from-step-1>/prd.md"`
   Replace `<actual-task-id-from-step-1>` with the UUID written by step 1.

## Workspace

Runtime files are in `.claude/workspace/` (gitignored):
- `tasks/` — one JSON file per active task
- `artifacts/` — team outputs structured as `<team>/<task-id>/`

## Customizing Workflows

Edit `.claude/workflows/<team>.md` to override default team behavior.
Edit `.claude/routing.json` to change which keywords route to which team.
```

---

## Inter-Agent Context Protocol (file-handoff)

### Agent invocation mechanism

Orchestrator and team leads use the Claude Code **`Agent` tool** to spawn sub-agents. The `Agent` tool response is the **authoritative completion signal**. Callers do not poll task files.

**Standard invocation prompt:**
```
Task file: .claude/workspace/tasks/<task-id>.json
Read the task file and execute your assigned workflow.
Return a plain-text summary (max 400 words) of what was produced.
```

### Task file schema

**One task file per team per invocation.** Both the orchestrator (on behalf of teams) and team leads (when invoked directly) create task files.

`task-id` generation: the creating agent runs `uuidgen | tr '[:upper:]' '[:lower:]'` via its **Bash tool**. Fallback (if `uuidgen` is absent): `python3 -c "import uuid; print(uuid.uuid4())"` also via Bash tool.

```json
{
  "task_id": "<lowercase uuid>",
  "created_at": "<ISO8601 timestamp>",
  "description": "<natural language task description>",
  "assigned_team": "<single team name>",
  "status": "pending | in_progress | completed | failed",
  "input_context": "<plain text — additional context. Use 'artifact: <path>' on its own line to reference a prior artifact file.>",
  "artifact_path": ".claude/workspace/artifacts/<team>/<task-id>/"
}
```

### input_context artifact reference convention

To pass a prior team's output as input, include a line in `input_context` starting with `artifact: `:

```
artifact: .claude/workspace/artifacts/product/abc-123/prd.md
Please implement the features described in the PRD above.
```

Agents that read `input_context` must check for lines starting with `artifact: ` and read those files before starting work.

### Completion signal

The `Agent` tool return value is the authoritative completion signal. Team leads also write `summary.md` and update `status` in the task file for human inspection only. Sequential workflows chain via the `artifact_path` field in the task file — callers read artifact files directly, not `summary.md`.

### Failure handling

If a team lead cannot complete its task: return a failure description as the `Agent` tool result (prefixed with `FAILED: `). Set `status` to `"failed"` in the task file. The orchestrator surfaces this to the user immediately. No automatic retry.

---

## file-handoff Skill Content

The `shared/skills/file-handoff/SKILL.md` file:

```markdown
# File Handoff Protocol

Required skill for all agents. Use for every artifact write and context read.

## Writing Output
1. Create the artifact directory: `.claude/workspace/artifacts/<team>/<task-id>/`
2. Write primary output files using lowercase kebab-case names (e.g., `prd.md`, `code-review.md`).
3. Write `summary.md` last — one paragraph: what was produced, where it lives, key findings.
4. Update `status` in the task file to `"completed"` or `"failed"`.
5. Return the contents of `summary.md` as your Agent tool response (max 400 words).

## Reading Input
1. Read the task file provided in your invocation prompt.
2. Read `description` for the task goal.
3. Scan `input_context` for lines starting with `artifact: ` — read those files before starting work.

## Artifact Naming
- Lowercase kebab-case only.
- No spaces or special characters.
- One primary output file per specialist agent (e.g., `frontend-implementation.md`, `seo-report.md`).
```

---

## Versioning and Upgrade Story

### VERSION file

The repo root contains a `VERSION` file with a semver string (e.g., `1.0.0`). This is the single source of truth for the repo version.

### .aurorie-teams-version

`install.sh` writes the installed version to `.claude/.aurorie-teams-version`. This file is committed to the local project's git repo (not gitignored) so the team knows which version of aurorie-teams is installed.

### Upgrade workflow

```bash
cd aurorie-teams && git pull
cd ../my-project && ../aurorie-teams/install.sh
```

On install, the script compares the new version to `.claude/.aurorie-teams-version` and prints:

```
Updating aurorie-teams: 1.0.0 → 1.2.0
See aurorie-teams/CHANGELOG.md for what changed.
```

Agents and skills are always overwritten on reinstall (they are not user-customizable). Workflow files and `routing.json` are not overwritten unless `--force-workflows` is passed.

### CHANGELOG.md

The repo maintains a `CHANGELOG.md` at the root. Each version entry notes changed agents, skills, and breaking workflow changes.

---

## Explicit Scope Decisions

- **`CLAUDE.md` is file-existence-based only.** If it exists, `install.sh` skips it regardless of content.
- **`routing.json` is skipped on reinstall** (`cp -n`). Use `--force-workflows` to reset it (it is treated the same as workflow files for override purposes).
- **`--force-workflows` applies to workflows and `routing.json` together.** No per-file scoping. Manual copy for individual file updates.
- **`TEAM.md` is documentation only.** Not read by agents at runtime.
- **Secrets are never stored in the repo.** All `env` values in `mcp.json` use `${VAR_NAME}` shell variable references.
- **Context window protection:** All agent summaries are capped at 400 words. Extended content goes in artifact files.

---

## Environment Requirements

| Requirement | Notes |
|-------------|-------|
| macOS or Linux | Windows not supported |
| bash 3.2+ | Standard on macOS |
| `jq` | Required for settings.json merge (`brew install jq` / `apt install jq`) |
| `uuidgen` or `python3` | For task-id generation |
| `npx` / Node.js | Required for MCP servers that use `npx` |
| Shell env vars for MCP secrets | Set before starting Claude Code (e.g., `GITHUB_TOKEN`, `EXA_API_KEY`) |

---

## .gitignore Addition

```gitignore
# aurorie-teams runtime workspace — local only, do not commit
.claude/workspace/
```

`.claude/.aurorie-teams-version` is **not** gitignored — commit it to track which version is installed.

---

## Teams Summary

| Team | Lead | Specialist Agents | Core Skills | MCP |
|------|------|-------------------|-------------|-----|
| engineer | aurorie-engineer-lead | frontend, backend, devops, qa | tdd, code-review, deployment | github, filesystem |
| market | aurorie-market-lead | seo, content, analytics | content-engine, seo-audit | browser |
| product | aurorie-product-lead | pm, ux | prd-writing, user-story | — |
| data | aurorie-data-lead | analyst, pipeline, reporting | sql-patterns, visualization | database |
| research | aurorie-research-lead | web, synthesizer | deep-research, exa-search | firecrawl, exa |
| support | aurorie-support-lead | triage, responder, escalation | customer-comms | email, slack |
