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

_(or simply: "Build me a SaaS product from scratch" — the system routes automatically)_

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
   - Backend Team  (API design)
   - Frontend Team (UI)
   - Mobile Team   (app structure)
3. Each team executes its workflow
4. Outputs are written to structured artifacts

### Output

```
.claude/workspace/
├── tasks/
│   └── task-001.json
└── artifacts/
    ├── product/prd.md
    ├── backend/api-design.md
    ├── frontend/ui-spec.md
    └── mobile/app-architecture.md
```

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
- `example_requests` break ties

Example:

```
"Why did revenue drop?"
→ Data     (+score: data, metrics, report)
→ Research (+score: investigate, compare)
→ Backend  (−score: database penalty)
Final: Data + Research

"Build a mobile app"
→ Mobile  (+score: iOS, Android, native)
→ Backend (+score: API, server)
→ Frontend (−score: mobile app penalty)
Final: Mobile + Backend
```

Routing is deterministic at the rule level, and adaptive at the system level.

You can customize routing in `.claude/routing.json`.

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

### Build a product

```
@orchestrator "Create a SaaS for AI agents marketplace"
```

Triggers:
- Product Team
- Backend Team
- Frontend Team

Output:
```
.claude/workspace/artifacts/product/prd.md
.claude/workspace/artifacts/backend/api-design.md
.claude/workspace/artifacts/frontend/ui-spec.md
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
.claude/workspace/artifacts/data/analysis.md
.claude/workspace/artifacts/research/synthesis.md
```

Copy and run this — you'll get real artifacts.

---

### Build an app

```
@orchestrator "Design a mobile app for habit tracking with iOS and Android support"
```

Triggers:
- Mobile Team
- Backend Team
- Product Team

Output:
```
.claude/workspace/artifacts/mobile/app-architecture.md
.claude/workspace/artifacts/backend/api-design.md
.claude/workspace/artifacts/product/prd.md
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
.claude/workspace/artifacts/research/competitive-analysis.md
.claude/workspace/artifacts/research/summary.md
```

Copy and run this — you'll get real artifacts.

---

## 🔧 Customization

### Customize behavior
Edit `.claude/workflows/<team>.md` to change how a team operates.

### Customize intelligence
Edit `.claude/routing.json` — v2 schema supports `positive_keywords` (+1), `negative_keywords` (−2), and `example_requests` per rule.

### Customize tools
Extend MCP integrations via `.claude/settings.json`.

---

## ⚠️ Safety

Use read-only credentials where possible. Review generated artifacts before acting on them.

### Details

- **Agents generate outputs — they do not execute external actions unless you do.**
  Agents write files to `.claude/workspace/artifacts/`. They do not call external APIs,
  run shell commands, or modify your database unless you explicitly wire that up.
- **Nothing runs without your approval.**
- Avoid running on production systems during initial setup.
- Review `.claude/settings.json` to see and control which tools each agent can access.

---

## 🗺 Roadmap

We're building the AI company OS.

**v1.x — Reliable execution**
- ✓ 10 specialized teams, 34 agents
- ✓ v2 routing with positive/negative scoring
- ✓ Lint + install test suites

**v2.0 — Intelligent systems**
- [ ] Confidence-based routing
- [ ] UI dashboard
- [ ] Visual workflow editor

**Long-term — AI-native companies**
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

Open a PR 🚀

---

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

---
