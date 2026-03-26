# AURORIE TEAMS

> Turn Claude Code into a fully-operational AI startup team in 60 seconds — with real artifacts.

⚡ 34 Agents · 10 Teams · 1 Orchestrator
⚡ Plug-and-play AI workflows for real-world execution
⚡ Built for builders, founders, and power users

![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue?style=flat-square)
![Agents](https://img.shields.io/badge/agents-34-informational?style=flat-square)
![Teams](https://img.shields.io/badge/teams-10-informational?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

**Languages:** English | [中文](README.zh.md)

---

- [Install in 60 seconds](#install-in-60-seconds)
- [What it actually does](#-what-it-actually-does)
- [How it works](#-how-it-works)
- [Why not just use ChatGPT?](#-why-not-just-use-chatgpt)
- [Intelligent Routing](#-intelligent-routing)
- [Decision Policy](#-decision-policy)
- [Debug Mode](#-debug-mode)
- [Dry Run Mode](#-dry-run-mode)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Try these prompts](#-try-these-prompts)
- [Customization](#-customization)
- [Safety](#️-safety)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Tests](#tests)

---

## Install in 60 seconds

```bash
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
cd /path/to/your-project
/tmp/aurorie-teams/install.sh
```

Then just ask:

```
@orchestrator "Build me a SaaS product from scratch"
```

_(the orchestrator reads `.claude/routing.json` to dispatch teams automatically)_

Just type a task — the system routes teams automatically.

---

## 🎬 What it actually does

### Input

```
@orchestrator "Build a crypto trading dashboard with real-time data and mobile support"
```

### What happens internally

1. Orchestrator analyzes intent
2. Selects relevant teams:
   - Product Team  (requirements)
   - Backend Team  (services & data layer)
   - Frontend Team (UI)
   - Mobile Team   (app structure)
3. Each team executes its workflow
4. Outputs are written to structured artifacts (each in its own task folder)

### Output

```
.claude/workspace/
├── tasks/
│   └── <task-id>.json
└── artifacts/
    ├── product/<task-id>/
    │   ├── prd.md
    │   └── summary.md
    ├── backend/<task-id>/
    │   ├── backend-implementation.md
    │   └── summary.md
    ├── frontend/<task-id>/
    │   ├── frontend-implementation.md
    │   └── summary.md
    └── mobile/<task-id>/
        ├── ios-implementation.md
        └── summary.md
```

Each task gets its own folder (UUID) so outputs never collide.

💡 You just went from idea → structured execution plan in seconds.

Each file is a reusable artifact — not just a response.

---

## 🧩 How it works

You don't interact with agents directly — the system does it for you:

```mermaid
graph TD
    U([User Request]) --> O[Orchestrator]
    O --> T1[Product Team]
    O --> T2[Backend Team]
    O --> T3[Frontend Team]
    O --> T4[Mobile Team]
    O --> T5[Data Team]
    O --> T6[... 5 more teams]

    style O fill:#1a1a2e,color:#fff,stroke:#4a4a8a
    style U fill:#16213e,color:#fff,stroke:#4a4a8a
```

Three layers:

1. **Orchestrator** — routes your request to the right teams
2. **Teams (10 domains)** — each specializes in a function
3. **Agents (34 total)** — each executes specific tasks with defined workflows

> ChatGPT → one smart person
> AURORIE TEAMS → a full company working together

_Want to see the full system? → See [Architecture](#-architecture) below._

---

## ⚡ Why not just use ChatGPT?

Because real work is not single-step.

| ChatGPT | AURORIE TEAMS |
|---------|---------------|
| One response | Multi-step execution |
| Generalist | Specialized teams |
| Ephemeral output | Structured artifacts |
| Manual thinking | Automated orchestration |

You don't need one answer.
You need a team that executes.

Ready to try it? ↓

---

## 🧠 Intelligent Routing

Each routing decision is explainable — not a black box.

Each request is scored against every team rule:
- **+1** for each `positive_keywords` match
- **−2** for each `negative_keywords` match (strong disqualifier)

Scores map to confidence bands:
- **high** (score ≥ 3) → dispatched immediately as primary team
- **medium** (score ≥ 1) → dispatched as secondary when no high team, or surfaced as "also relevant"
- **low / filtered** (score < 1) → suppressed

Example:

```
"Add a REST endpoint for user authentication with JWT"
→ backend: score 4, high → selected
→ product: score 1, medium → secondary (not dispatched)
→ market:  score -1, low  → filtered

"Build a SaaS platform with user requirements and API endpoints"
→ backend:   score 4, high   → selected
→ product:   score 2, medium → secondary
→ frontend:  score 1, medium → secondary
→ remaining: low             → filtered
```

Routing is deterministic at the rule level, and adaptive at the system level.

You can customize routing in `.claude/routing.json`. The `routing_policy` block controls thresholds.

### Debug routing decisions

Add `--debug` to any orchestrator call to see the full trace:

```
@orchestrator --debug "Build a SaaS platform with user requirements and API endpoints"
```

Output:

```
=== ROUTING DEBUG ===

Policy:
- candidate_threshold: 1
- confidence.high: 3
- confidence.medium: 1
- dispatch_policy.high: auto
- dispatch_policy.medium.when_high_exists: ignore
- dispatch_policy.medium.when_no_high_exists: auto
- dispatch_strategy: conditional

Evaluations:
backend: score 4, high → selected
  + API, endpoint, SaaS, platform
  - (none)
product: score 2, medium → secondary
  + requirements, SaaS
  - (none)
market: score -1, low → filtered
  + (none)
  - iOS

Dispatch:
  Selected:  backend
  Secondary: product, frontend
  Ignored:   (none)
  Filtered:  market, mobile, data, ...

=== END ROUTING DEBUG ===
```

When `ask` mode is triggered, an additional `Ask` block appears showing the prompted teams and user response.

Debug output is a pure projection of `routing_decision` — it does not change dispatch behavior.

---

## 🧠 Decision Policy

Control what happens per confidence band after classification — not a black box, a programmable policy.

```json
"dispatch_policy": {
  "high": "auto",
  "medium": {
    "when_high_exists": "ignore",
    "when_no_high_exists": "ask"
  }
}
```

Three actions:
- **`auto`** — dispatch immediately
- **`ask`** — prompt for confirmation before dispatching (medium band only in v0.3)
- **`ignore`** — suppress the team entirely

**Ask mode example** — when a medium-only prompt triggers `ask`:

```
Medium-confidence teams identified:
- product (score 2)
- frontend (score 1)
Dispatch these teams? [Y/n]
```

- `y` / `yes` / `<empty>` → dispatch all prompted teams
- `n` / `no` → suppress all
- Two invalid replies → treated as `no` (records `user_response: "default_no"`)

Ask fires at most once per routing invocation. High-confidence teams are never affected.

Customize in `.claude/routing.json`. The default policy reproduces v0.2 behavior exactly — no change required unless you want custom control.

---

## 🕸 Execution Graph

Selected teams are not always dispatched flat — v0.4 builds an execution graph so teams execute in dependency order, and independent nodes run in parallel.

**Graph templates (strict priority — first match wins):**

| Priority | Condition | Template |
|----------|-----------|----------|
| 1 | `data` in selected teams | data-first chain |
| 2 | `research` selected, no `product` | research branch fan-out |
| 3 | `backend` or `frontend` selected | linear pipeline |
| 4 | fallback | flat parallel |

**Linear pipeline example** — `product → backend → frontend`:

```
Wave 1: product (ready immediately)
Wave 2: backend (unlocked after product done)
Wave 3: frontend (unlocked after backend done)
```

**Research branch** — `research → [backend, frontend]` in parallel after research completes.

**Graph runtime states:** `pending` → `in_progress` → `completed` | `partial_failed`

The graph is stored in the task JSON (`routing_decision.execution_graph`) — not just a plan, but a live runtime object tracked throughout execution.

---

## 🎯 Milestone — Cross-Task Coordination

v0.5 introduces milestone as a persistent coordination layer that tracks progress *across tasks, graphs, and time*.

**CLI:**

```
@orchestrator --milestone "Launch SaaS" "Build a crypto trading platform"
@orchestrator --milestone-status ms_abc123
```

**What it does:**

- `--milestone "Title" "prompt"` — groups the task under a named goal. The task runs normally (routing + dispatch unchanged), but is tagged with a milestone ref. Milestone file created at `.claude/workspace/milestones/<id>.json`.
- `--milestone-status <id>` — queries milestone, aggregates all attached task statuses, and prints a summary:

```
Milestone: Launch SaaS (ms_abc123)
Status: in_progress
Tasks: 3 total
  - completed: 1
  - in_progress: 1
  - pending: 1
```

**Status aggregation** (highest wins):
`partial_failed` > `in_progress` > `completed` > `pending`

**Key properties:**

| Property | Value |
|----------|-------|
| Schema | `.claude/workspace/milestones/<id>.json` |
| Task ref | `{milestone_id, title}` embedded in task JSON |
| Append-only | Tasks can be added, never removed |
| Routing influence | None — milestone is a coordination label, not a routing signal |
| Status triggers | Task creation, `--milestone-status` query |

**Use cases:**
- Track a product launch across multiple feature tasks
- Monitor a platform build across `product → backend → frontend` waves
- Coordinate a research sprint across parallel branches

---

## 🔍 Debug Mode

`--debug` exposes the full routing trace — every score, every decision, every field:

```
@orchestrator --debug "Build a SaaS platform with user requirements and API endpoints"
```

```
=== ROUTING DEBUG ===

Policy:
- candidate_threshold: 1
- confidence.high: 3
- confidence.medium: 1
- dispatch_policy.high: auto
- dispatch_policy.medium.when_high_exists: ignore
- dispatch_policy.medium.when_no_high_exists: auto
- dispatch_strategy: conditional

Evaluations:
backend: score 4, high → selected
  + API, endpoint, SaaS, platform
  - (none)
product: score 2, medium → secondary
  + requirements, SaaS
  - (none)
market: score -1, low → filtered
  + (none)
  - iOS

Dispatch:
  Selected:  backend
  Secondary: product, frontend
  Ignored:   (none)
  Filtered:  market, mobile, data, ...

=== END ROUTING DEBUG ===
```

When `ask` mode fires, an `Ask:` block is appended showing context, user response, and prompted teams.

---

## ⏸ Dry Run Mode

`--dry-run` shows what would happen without dispatching any teams:

```
@orchestrator --dry-run "Build a crypto SaaS with real-time price feeds"
```

```
Routed to:
- backend (high, score 4)
- product (medium, score 2)

Dry run — no teams were dispatched.
```

**What it does:**
- Full routing decision is computed and displayed
- Steps A/B (actual team dispatch) are skipped
- `--ask` prompts are deferred — `ask_required: true` is recorded instead

**Combine with `--debug` for the full trace without side effects:**

```
@orchestrator --debug --dry-run "Build a crypto SaaS"
```

Both flags work together — `--debug` shows the trace, `--dry-run` prevents dispatch.

---

## 🏗 Architecture

Here's the full system:

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

Each team includes:
- Agents (specialists with defined roles)
- Workflows (step-by-step execution guides)
- Skills (reusable task modules)
- MCP integrations (tool access per team)

---

## 🛠 Installation

Requirements: macOS or Linux (bash 3.2+) · `jq` · `uuidgen` or `python3` · Node.js

```bash
# 1. Clone the library
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams

# 2. Install into your project
cd /path/to/your-project
/tmp/aurorie-teams/install.sh

# 3. Add API keys (optional but recommended)
export GITHUB_TOKEN=...
export EXA_API_KEY=...
export FIRECRAWL_API_KEY=...
export POSTGRES_URL=...

# 4. Verify
# In Claude Code: @orchestrator "Test the system"
# You should see routing + task output.
```

Done ✅ Your Claude Code is now an AI startup team.

### Install flags

```
--force-workflows   Overwrite existing workflow + routing overrides
--yes               Skip all confirmation prompts
--detect-orphans    Report stale agent/skill files no longer in repo
```

### Upgrade

```bash
git -C /tmp/aurorie-teams pull
cd /path/to/your-project && /tmp/aurorie-teams/install.sh
```

---

## 🧪 Try these prompts

Each prompt triggers a different team workflow — try one to see the system in action.

### Build a product ⭐ Start here

```
@orchestrator "Create a SaaS for AI agents marketplace"
```

Triggers:
- Product Team
- Backend Team
- Frontend Team

Output:
```
.claude/workspace/artifacts/product/<task-id>/prd.md
.claude/workspace/artifacts/product/<task-id>/summary.md
.claude/workspace/artifacts/backend/<task-id>/backend-implementation.md
.claude/workspace/artifacts/backend/<task-id>/summary.md
.claude/workspace/artifacts/frontend/<task-id>/frontend-implementation.md
.claude/workspace/artifacts/frontend/<task-id>/summary.md
```

Copy and run this — you'll get real artifacts.

---

### Analyze data

```
@orchestrator "Investigate why our DAU dropped 30% last week"
```

Triggers:
- Data Team
- Research Team

Output:
```
.claude/workspace/artifacts/data/<task-id>/analysis.md
.claude/workspace/artifacts/data/<task-id>/summary.md
.claude/workspace/artifacts/research/<task-id>/research-report.md
.claude/workspace/artifacts/research/<task-id>/summary.md
```

Copy and run this — you'll get real artifacts.

---

### Build an app

```
@orchestrator "Design a mobile app for habit tracking with iOS and Android support"
```

Triggers:
- Mobile Team
- Product Team

Output:
```
.claude/workspace/artifacts/mobile/<task-id>/ios-implementation.md
.claude/workspace/artifacts/mobile/<task-id>/android-implementation.md
.claude/workspace/artifacts/mobile/<task-id>/summary.md
.claude/workspace/artifacts/product/<task-id>/prd.md
.claude/workspace/artifacts/product/<task-id>/summary.md
```

Copy and run this — you'll get real artifacts.

---

### Research a market

```
@orchestrator "Compare the top 5 AI code generation tools — pricing, features, positioning"
```

Triggers:
- Research Team

Output:
```
.claude/workspace/artifacts/research/<task-id>/comparison-matrix.md
.claude/workspace/artifacts/research/<task-id>/summary.md
```

Copy and run this — you'll get real artifacts.

---

### Build a trading system

```
@orchestrator "Build a crypto SaaS with real-time price feeds, portfolio analytics, and a React dashboard"
```

Triggers:
- Product Team
- Backend Team
- Frontend Team
- Data Team

Output:
```
.claude/workspace/artifacts/product/<task-id>/prd.md
.claude/workspace/artifacts/product/<task-id>/summary.md
.claude/workspace/artifacts/backend/<task-id>/backend-implementation.md
.claude/workspace/artifacts/backend/<task-id>/summary.md
.claude/workspace/artifacts/frontend/<task-id>/frontend-implementation.md
.claude/workspace/artifacts/frontend/<task-id>/summary.md
.claude/workspace/artifacts/data/<task-id>/report-spec.md
.claude/workspace/artifacts/data/<task-id>/summary.md
```

Copy and run this — you'll get real artifacts.

---

## 🔧 Customization

### Customize behavior
Edit `.claude/workflows/<team>.md` to change how a team operates.

### Customize intelligence
Edit `.claude/routing.json` — configure scoring rules (`positive_keywords` / `negative_keywords`) and confidence thresholds, plus `dispatch_policy` to control what happens per band (auto / ask / ignore).

### Customize tools
Extend MCP integrations via `.claude/settings.json`.

---

## ⚠️ Safety

Use read-only credentials where possible. Review generated artifacts before acting on them.

### Details

- **Agents generate outputs — they do not execute external actions unless you do.**
  Agents write files to `.claude/workspace/artifacts/`. They do not call external APIs,
  run shell commands, or modify your database unless you explicitly wire that up.
  **Default behavior is local file generation under `.claude/workspace/artifacts/`.**
- **Nothing runs without your approval.**
- Avoid running on production systems during initial setup.
- Review `.claude/settings.json` to see and control which tools each agent can access.

---

## 🗺 Roadmap

We're building the AI company OS.

**v0.1 — Foundation**
- ✓ 10 specialized teams, 34 agents
- ✓ v2 routing with positive/negative scoring
- ✓ Lint + install test suites

**v0.2 — Observable routing**
- ✓ Confidence-based routing (high / medium / filtered)
- ✓ Routing test suite — 5 regression cases, CI-integrated
- ✓ `--debug` flag — full per-team routing trace in terminal

**v0.3 — Controllable execution**
- [x] `dispatch_policy` config — per-confidence-band behavior in routing.json
- [x] `normalize_dispatch_policy` — pure function, fills missing keys with v0.2-equivalent defaults
- [x] `apply_dispatch_policy` — Step 5.5 enforcement: auto / ignore / ask modes
- [x] Ask mode MVP — interactive confirmation for medium-confidence teams (at most once per routing)
- [x] Dispatch policy test suite — 47 cases: normalize (4), auto/ignore (4), ask (5), dry-run (5), phase1 (14), graph (15)
- [x] `--dry-run` flag — compute routing without dispatching
- [x] `--debug --dry-run` combined mode

**v0.4 — Interactive Routing Contract + DAG Execution (complete)**
- [x] `pending_decision` schema — replaces `ask_required: true` with full structured payload
- [x] `awaiting_dispatch_decision` task status
**v0.5 — Goal-Oriented Coordination Runtime**

v0.5 introduces a persistent coordination layer across tasks.

- [x] **Milestone system** (complete)
  - Persistent coordination layer across tasks and graphs
  - Aggregate status: partial_failed > in_progress > completed > pending
  - Append-only: tasks can be added, never removed
  - CLI: `--milestone "title" "prompt"` and `--milestone-status <id>`
  - Pure functions: `lib/milestone.py` — 63/63 tests passing

- [ ] **Selective routing**
  - Extend decision resolution from all|none → all|none|selective
  - Allow users to choose a subset of medium-confidence teams

- [ ] **DAG dry-run**
  - Preview execution_graph and wave order before dispatch
  - Make dependencies explicit prior to execution

**v0.5 moves from task orchestration to goal-oriented coordination.**

**Long-term — AI-native companies**
- [ ] Observability dashboard
- [ ] Agent marketplace
- [ ] Memory system
- [ ] Cross-project orchestration

---

## 🤝 Contributing

We're building the AI company OS — and we're opinionated about it.

Want to help?
- Add new teams
- Improve routing logic
- Build workflows
- Share use cases

We value coherence over volume.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR 🚀

---

## Tests

Four test suites in `tests/`, all green on every commit:

| Script | What it tests |
|--------|--------------|
| `tests/install.test.sh` | Install lifecycle: file placement, routing preservation, MCP merge, orphan detection |
| `tests/lint.test.sh` | Source tree contract: agent/workflow/skill/routing validation |
| `tests/routing/test_routing_cases.py` | 5 routing regression cases: confidence bands, dispatch, fallback, negative keyword suppression |
| `tests/routing/test_dispatch_policy.py` | 63 cases: dispatch (47) + milestone (14 unit + 2 E2E) |

Run all tests before opening a PR:

```bash
bash tests/install.test.sh && bash tests/lint.test.sh
```

Or run routing tests standalone:

```bash
python3 tests/routing/test_routing_cases.py
python3 tests/routing/test_dispatch_policy.py
```

---
