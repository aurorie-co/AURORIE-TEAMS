# aurorie-teams

Company-wide Claude Code multi-agent configuration library.
28 agents across 8 teams, ready to install into any project.

**Languages:** English | [中文](README.zh.md)

---

## Overview

aurorie-teams gives your Claude Code environment a full company org chart — each team has a lead agent that routes tasks to specialists, coordinates outputs, and writes a final `summary.md`. Teams operate independently or chain together for cross-functional workflows.

| Team | Agents | What it does |
|------|--------|-------------|
| `market` | lead, seo, content, analytics | Blog posts, SEO audits, campaign analytics, content rewrites |
| `product` | lead, pm, ux, researcher | PRDs, UX briefs, market research, roadmap planning |
| `research` | lead, web, synthesizer | Deep research, competitor analysis, synthesized reports |
| `support` | lead, triage, responder, escalation | Ticket triage, response drafts, escalation coordination |
| `frontend` | lead, developer, qa, devops | UI implementation, component review, frontend CI/CD |
| `mobile` | lead, ios, android, qa, devops | Mobile feature dev, cross-platform review, release pipeline |
| `backend` | lead, developer, qa, devops | API development, database, backend infrastructure |
| `data` | lead, analyst, pipeline, reporting | Data analysis, ETL pipelines, dashboards |

---

## Requirements

- macOS or Linux (bash 3.2+)
- `jq` — `brew install jq` / `apt install jq`
- `uuidgen` or `python3`
- Node.js (for `npx`-based MCP servers)

---

## Install

From your project root:

```bash
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
cd /path/to/your-project
/tmp/aurorie-teams/install.sh
```

This installs 28 agents, 27 skills, and 8 workflow files into `.claude/` inside your project.

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
export GITHUB_TOKEN=...        # GitHub API access (research, frontend, backend teams)
export EXA_API_KEY=...         # Exa neural search (research, market teams)
export FIRECRAWL_API_KEY=...   # Web crawling (research, market teams)
```

---

## Tutorial

### 1. Invoking a team via the orchestrator

The `orchestrator` agent is the recommended entry point. It reads `.claude/routing.json`, matches your request to the right team, and dispatches the team lead.

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
1. `aurorie-market-lead` reads the brief, detects "landing page" → always dispatches SEO first
2. `aurorie-market-seo` audits keywords, writes `seo-report.md`
3. `aurorie-market-content` drafts the landing page using the SEO report, writes `content.md`
4. Lead reviews and writes `summary.md`

**Artifacts produced:**
```
.claude/workspace/artifacts/market/<task-id>/
  seo-report.md       ← keyword research, on-page recommendations
  content.md          ← landing page copy
  summary.md          ← lead's final synthesis
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
  triage-report.md    ← category, priority, root cause hypothesis
  response-draft.md   ← customer-facing response, tone notes, send channel
  summary.md          ← lead's synthesis
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

## Customizing

- **Workflows:** Edit `.claude/workflows/<team>.md` to change how a team operates
- **Routing:** Edit `.claude/routing.json` to control which keywords route to which team
- **CLAUDE.md:** Edit `CLAUDE.md` in your project root to add project context all agents read

Changes to `.claude/workflows/` and `.claude/routing.json` are preserved on upgrade (unless you run with `--force-workflows`).

---

## How it works

Every team follows the same pattern:

```
User request
    └── orchestrator (reads routing.json)
            └── team lead (reads workflow, dispatches specialists)
                    ├── specialist A → artifact A
                    ├── specialist B → artifact B
                    └── lead writes summary.md
```

**Task files** at `.claude/workspace/tasks/<task-id>.json` carry the task description and `input_context` between agents.

**Artifacts** at `.claude/workspace/artifacts/<team>/<task-id>/` are the team's deliverables. Pass them between teams using `artifact: <path>` in `input_context`.

**`summary.md`** is always the final output — written by the lead after reviewing all specialist outputs. It is the canonical deliverable to share with stakeholders.
