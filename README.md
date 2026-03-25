# aurorie-teams

![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue?style=flat-square)
![Agents](https://img.shields.io/badge/agents-34-informational?style=flat-square)
![Teams](https://img.shields.io/badge/teams-10-informational?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

Company-wide Claude Code multi-agent configuration library.
34 agents across 10 teams, ready to install into any project.

**Languages:** English | [中文](README.zh.md)

---

## Quick Start

```bash
# 1. Clone the library
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams

# 2. Install into your project
cd /path/to/your-project && /tmp/aurorie-teams/install.sh

# 3. Invoke the orchestrator
# In Claude Code: @orchestrator Write a blog post about our new API release.
```

---

## Overview

aurorie-teams gives your Claude Code environment a full company org chart — each team has a lead agent that routes tasks to specialists, coordinates outputs, and writes a final `summary.md`. Teams operate independently or chain together for cross-functional workflows.

### Architecture

```mermaid
graph TD
    U([User Request]) --> O[orchestrator<br/>reads routing.json]
    O --> ML[market-lead]
    O --> PL[product-lead]
    O --> RL[research-lead]
    O --> SL[support-lead]
    O --> FL[frontend-lead]
    O --> BL[backend-lead]
    O --> IL[infra-lead]
    O --> DL[design-lead]
    O --> DAL[data-lead]
    O --> MOL[mobile-lead]

    ML --> MS1[seo]
    ML --> MS2[content]
    ML --> MS3[analytics]

    PL --> PS1[pm]
    PL --> PS2[ux]
    PL --> PS3[researcher]

    FL --> FS1[developer]
    FL --> FS2[qa]
    FL --> FS3[devops]

    MS2 --> A1[(artifact)]
    PS1 --> A2[(artifact)]
    FS1 --> A3[(artifact)]

    style O fill:#1a1a2e,color:#fff,stroke:#4a4a8a
    style U fill:#16213e,color:#fff,stroke:#4a4a8a
```

### Teams

| Team | Agents | What it does |
|------|--------|--------------|
| `market` | lead, seo, content, analytics | Blog posts, SEO audits, campaign analytics, content rewrites |
| `product` | lead, pm, ux, researcher | PRDs, UX briefs, market research, roadmap planning |
| `research` | lead, web, synthesizer | Deep research, competitor analysis, synthesized reports |
| `support` | lead, triage, responder, escalation | Ticket triage, response drafts, escalation coordination |
| `frontend` | lead, developer, qa, devops | UI implementation, component review, frontend CI/CD |
| `mobile` | lead, ios, android, qa, devops | Mobile feature dev, cross-platform review, release pipeline |
| `backend` | lead, developer, qa, devops | API development, database, backend infrastructure |
| `infra` | lead, iac-engineer, reviewer | Terraform modules, IaC review, PR review, infrastructure audits |
| `design` | lead, system, brand | Design tokens, component specs, WCAG accessibility, brand identity guidelines |
| `data` | lead, analyst, pipeline, reporting | Data analysis, ETL pipelines, dashboards |

---

## Requirements

| Dependency | Install |
|------------|---------|
| macOS or Linux (bash 3.2+) | — |
| `jq` | `brew install jq` / `apt install jq` |
| `uuidgen` or `python3` | pre-installed on most systems |
| Node.js | for `npx`-based MCP servers |

---

## Install

From your project root:

```bash
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
cd /path/to/your-project
/tmp/aurorie-teams/install.sh
```

This installs 34 agents, 27 skills, and 10 workflow files into `.claude/` inside your project.

### Install Flags

| Flag | Effect |
|------|--------|
| (none) | Default install |
| `--force-workflows` | Overwrite local workflow + routing.json overrides (prompts for confirmation) |
| `--yes` | Skip confirmation prompts (for CI) |
| `--detect-orphans` | Report stale agent/skill files not in repo |

### Upgrade

```bash
cd /tmp/aurorie-teams && git pull
cd /path/to/your-project && /tmp/aurorie-teams/install.sh
```

---

## Environment Variables

Set in your shell profile before starting Claude Code:

```bash
export GITHUB_TOKEN=...        # GitHub API — all teams via shared MCP
export EXA_API_KEY=...         # Exa neural search — market, product, research teams
export FIRECRAWL_API_KEY=...   # Web crawling — market, research teams
export POSTGRES_URL=...        # PostgreSQL connection string — backend, data teams
                               # Format: postgresql://user:password@host:5432/dbname
```

---

## MCP Servers

MCP servers are pre-configured per team and merged into `.claude/settings.json` at install time. Only the servers a team genuinely needs are included.

| Server | Package | Teams |
|--------|---------|-------|
| `github` | `@modelcontextprotocol/server-github` | All teams (shared) |
| `exa` | `exa-mcp-server` | market, product, research (shared) |
| `firecrawl` | `firecrawl-mcp` | market, research |
| `puppeteer` | `@modelcontextprotocol/server-puppeteer` | market |
| `playwright` | `@playwright/mcp` | frontend |
| `postgres` | `@modelcontextprotocol/server-postgres` | backend, data |
| `sqlite` | `@modelcontextprotocol/server-sqlite` | data |

`filesystem` is intentionally excluded — agents use Claude Code's built-in Read/Write/Edit/Glob/Grep tools instead.

---

## Tutorial

### 1. Invoking a team via the orchestrator

The `orchestrator` agent is the recommended entry point. It reads `.claude/routing.json`, scores your request against each team's `positive_keywords` (+1) and `negative_keywords` (−2), picks the best-matching team, and dispatches the team lead. When signals are mixed it identifies the *primary intent* to avoid ambiguous multi-team dispatches.

In Claude Code, tell the `orchestrator` agent what you need:

```
@orchestrator Write a blog post about our new API release.
Target audience: developers. Goal: drive signups.
```

The orchestrator routes this to `aurorie-market-lead`, which dispatches SEO and content specialists, then writes a `summary.md` with the final deliverable path.

---

### 2. Invoking a team lead directly

Skip the orchestrator if you already know which team you need:

```
@aurorie-market-lead Write a blog post about our new API release.
Target audience: developers. Goal: drive signups.
```

---

### 3. Example: Content Creation (market team)

**Request:**
```
@aurorie-market-lead
Write a landing page for our new mobile SDK.
Audience: mobile developers (iOS/Android).
Goal: trial signups.
Include SEO optimization.
```

**What happens:**
1. `aurorie-market-lead` reads the brief, detects "landing page" — always dispatches SEO first
2. `aurorie-market-seo` audits keywords, writes `seo-report.md`
3. `aurorie-market-content` drafts the landing page using the SEO report, writes `content.md`
4. Lead reviews and writes `summary.md`

**Artifacts produced:**
```
.claude/workspace/artifacts/market/<task-id>/
  seo-report.md       <- keyword research, on-page recommendations
  content.md          <- landing page copy
  summary.md          <- lead's final synthesis
```

---

### 4. Example: Support Ticket (support team)

**Request:**
```
@aurorie-support-lead
Customer ticket: "I exported my data and the file is empty. I've tried 3 times."
Account: Pro plan, 2 years tenure. No prior tickets about exports.
```

**What happens:**
1. `aurorie-support-triage` classifies: Bug / P1 — major feature broken, no workaround
2. `aurorie-support-responder` drafts a P1-tone response with next steps
3. Lead reviews and writes `summary.md`

**If triage returns P0:** lead additionally dispatches `aurorie-support-escalation` to produce an `escalation-plan.md` before the customer response goes out.

**Artifacts produced:**
```
.claude/workspace/artifacts/support/<task-id>/
  triage-report.md    <- category, priority, root cause hypothesis
  response-draft.md   <- customer-facing response, tone notes, send channel
  summary.md          <- lead's synthesis
```

---

### 5. Example: Cross-team workflow (product → frontend)

Teams can chain by passing artifacts between them. Use `input_context` with an `artifact:` line.

**Step 1 — Product team writes a PRD:**
```
@aurorie-product-lead
Write a PRD for a dark mode feature.
Users want dark mode on mobile. Engineering estimate: 1 sprint.
```

This produces `.claude/workspace/artifacts/product/<task-id>/prd.md`.

**Step 2 — Frontend team implements from the PRD:**
```
@aurorie-frontend-lead
Implement the dark mode feature described in the PRD.
input_context:
artifact: .claude/workspace/artifacts/product/<actual-task-id>/prd.md
```

The frontend lead reads the PRD artifact and routes to developer and QA specialists accordingly.

---

### 6. Example: Content Performance Rewrite (market team)

When existing content is underperforming, the market team can run a full diagnosis and rewrite in one request:

```
@aurorie-market-lead
Our blog post "Getting Started with the API" is getting 200 visits/month,
down from 800 six months ago. Organic traffic dropped after a competitor published
a similar guide with better SEO.

Performance data:
- Current: 200 visits/month, position 18 for "api getting started guide"
- Prior: 800 visits/month, position 6
- CTR: 1.2% (was 4.8%)

Please rewrite the post to recover rankings.
```

**What happens:**
1. Analytics diagnoses the traffic drop (keyword ranking loss, CTR decline)
2. SEO identifies keyword gaps vs. competitors
3. Content rewrites the post incorporating both reports
4. Lead writes `summary.md` with original issue, changes made, and expected recovery

---

### 7. Example: Deep Research (research team)

**Request:**
```
@aurorie-research-lead
Research the AI code generation tools market: key competitors (GitHub Copilot, Cursor, Tabnine),
their pricing, differentiation, and user sentiment.
Goal: inform our product roadmap decisions.
```

**What happens:**
1. `aurorie-research-web` searches the web via Exa/Firecrawl, collecting raw data
2. `aurorie-research-synthesizer` synthesizes raw data into a structured report
3. Lead reviews and writes `summary.md` with key insights and recommended actions

**Artifacts produced:**
```
.claude/workspace/artifacts/research/<task-id>/
  research-notes.md   <- raw sources, data points, quotes
  research-report.md  <- synthesized findings, competitive landscape
  summary.md          <- lead's key insights and recommended actions
```

---

## Customizing

- **Workflows:** Edit `.claude/workflows/<team>.md` to change how a team operates
- **Routing:** Edit `.claude/routing.json` to control which keywords route to which team. The schema (v2) supports `positive_keywords` (+1 per match), `negative_keywords` (−2 per match, strong disqualifier), and `example_requests` (used to break ties) per team rule
- **CLAUDE.md:** Edit `CLAUDE.md` in your project root to add project context all agents read

Changes to `.claude/workflows/` and `.claude/routing.json` are preserved on upgrade (unless you run with `--force-workflows`).

---

## How It Works

Every team follows the same pattern:

```
User request
    └── orchestrator (reads routing.json)
            └── team lead (reads workflow, dispatches specialists)
                    ├── specialist A --> artifact A
                    ├── specialist B --> artifact B
                    └── lead writes summary.md
```

**Task files** at `.claude/workspace/tasks/<task-id>.json` carry the task description and `input_context` between agents.

**Artifacts** at `.claude/workspace/artifacts/<team>/<task-id>/` are the team's deliverables. Pass them between teams using `artifact: <path>` in `input_context`.

**`summary.md`** is always the final output — written by the lead after reviewing all specialist outputs. It is the canonical deliverable to share with stakeholders.

---

## Workspace Layout

All runtime files live under `.claude/workspace/` (gitignored). The canonical paths are:

| Path | Description |
|------|-------------|
| `.claude/workspace/tasks/{task_id}.json` | Task descriptor written by orchestrator before dispatch |
| `.claude/workspace/artifacts/{team}/{task_id}/` | Team output directory |
| `.claude/workspace/artifacts/{team}/{task_id}/summary.md` | Final deliverable — always present after a completed task |

Example after running a product task and a market task:

```
.claude/workspace/
├── tasks/
│   ├── 3f8a1c2d-0001-4b5e-9d6f-abc123def456.json   ← product task
│   └── 7e2b9a4f-0002-4c8d-be12-def456abc789.json   ← market task
└── artifacts/
    ├── product/
    │   └── 3f8a1c2d-0001-4b5e-9d6f-abc123def456/
    │       ├── prd.md
    │       └── summary.md
    └── market/
        └── 7e2b9a4f-0002-4c8d-be12-def456abc789/
            ├── seo-report.md
            ├── content.md
            └── summary.md
```

Pass artifacts between teams using `artifact: <path>` in `input_context` — see the cross-team workflow tutorial above.


## Tests

Two test suites live in `tests/`:

| Script | What it tests |
|--------|--------------|
| `tests/install.test.sh` | Full install lifecycle: file placement, routing preservation, MCP merge, orphan detection |
| `tests/lint.test.sh` | Source tree consistency: agent/workflow/skill/routing contract validation |

Run both with:

```bash
bash tests/install.test.sh && bash tests/lint.test.sh
```
