# AURORIE TEAMS

> An interactive, graph-aware orchestration runtime for AI teams — built for builders, founders, and power users.

**One command. Real artifacts. Recoverable execution.**

```bash
@orchestrator "Build a SaaS for AI agents marketplace"
```

---

### [34 Agents](#system-model) · [10 Teams](#system-model) · [1 Orchestrator](#orchestrator) · [100 tests green](#tests)

![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue?style=flat-square)
![Version](https://img.shields.io/badge/version-v0.6.0-blue?style=flat-square)
![Agents](https://img.shields.io/badge/agents-34-informational?style=flat-square)
![Teams](https://img.shields.io/badge/teams-10-informational?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

**Languages:** English | [中文](README.zh.md)

---

## What makes it different

Most agent systems just run and forget. AURORIE TEAMS treats every execution as a first-class, recoverable event.

### Decision-first

Before anything runs, the system decides *what* to do and *why*. Every routing decision is scored, explainable, and programmable — not a black-box LLM call. You can see exactly which teams were selected, which were secondary, and why.

### Graph-aware execution

Teams don't run flat in parallel. A wave-based DAG determines execution order — dependencies are respected, independent nodes run in parallel, and partial failures are contained. Nothing runs blindly.

### Cross-task coordination

One task is a milestone. Track progress across tasks, graphs, and time. Resume interrupted work. Replay past executions. The system has memory.

---

## One complete flow

```bash
@orchestrator "Build a SaaS for AI agents marketplace"
```

**Step 1 — Routing decision**

```
→ backend (high, score 4) → selected
→ product (medium, score 2) → secondary
→ frontend (medium, score 1) → secondary
```

**Step 2 — Decision policy**

```
→ dispatch_policy.medium.when_high_exists: ignore
   secondary teams suppressed
```

**Step 3 — Wave execution**

```
Wave 1: [product-1]     → done          10:01:01
Wave 2: [backend-1]     → done          10:02:33
Wave 3: [frontend-1]   → completed      10:04:12
```

**Output:**

```
.claude/workspace/
├── tasks/<task-id>.json       # routing + execution graph + milestone ref
└── artifacts/
    ├── product/<task-id>/     # prd.md + summary.md
    ├── backend/<task-id>/     # implementation + summary.md
    └── frontend/<task-id>/    # implementation + summary.md
```

> **Not one-shot.** When something fails, you resume — not restart.

---

## Runtime modes

AURORIE TEAMS is an interactive runtime. Every mode is a different way to operate on the same execution state.

### `@orchestrator "prompt"` — Normal execution

Full routing + dispatch. Teams write artifacts. Graph is built and tracked.

### `@orchestrator --debug "prompt"` — See the full trace

Every score, every evaluation, every confidence band. See exactly what the system decided and why before anything runs.

### `@orchestrator --dry-run "prompt"` — Preview without side effects

Compute the routing decision and see the execution graph — without dispatching any teams. Combine with `--debug` for the full trace preview.

### `@orchestrator --milestone "Launch SaaS" "prompt"` — Track across tasks

Group tasks under a shared goal. Query with `--milestone-status <id>` to see aggregated progress. Status rolls up: `partial_failed > in_progress > completed > pending`.

### `@orchestrator --resolve <task-id> all|none|selective` — Resolve a paused decision

When a task is parked awaiting confirmation, resolve it — approve all, decline all, or selectively choose teams. Idempotent.

### `@orchestrator --replay <task-id>` — Inspect past execution (read-only)

See the routing decision, wave timeline, node statuses, and milestone ref for any past task. No state mutation.

### `@orchestrator --resume <task-id>` — Continue from where it left off

Resume an interrupted DAG. Three paths:

- **`in_progress`** — continues from current wave
- **`partial_failed`** — retries only failed nodes (done/blocked untouched)
- **`blocked`** — re-checks `artifacts_in`, only unblocks nodes whose artifacts now exist

Every resume path prompts for confirmation before mutating state.

---

## System model

```
User Request → Orchestrator → Teams → Agents → Artifacts
                    ↓
              routing_decision (who + why)
                    ↓
              execution_graph (DAG + waves)
                    ↓
              milestone (cross-task coordination)
```

### Orchestrator

Reads `.claude/routing.json`. Scores every team rule. Builds the execution graph. Drives dispatch.

### Teams (10 domains)

Each team is a self-contained unit: agents, workflows, skills, and MCP tool access.

| Team      | Focus                     |
|-----------|---------------------------|
| market    | SEO, content, analytics   |
| product   | PM, UX, research          |
| backend   | services, data layer     |
| frontend  | UI, React                 |
| infra     | deployment, DevOps        |
| data      | analysis, pipelines       |
| design    | visual, UX                |
| mobile    | iOS, Android              |
| support   | help, docs                |
| research  | market, competitive       |

### Execution graph

Wave-based DAG. Dependencies are explicit. Nodes run in parallel within a wave. Partial failures are contained and resumable.

### Artifacts

Every team writes structured output to `.claude/workspace/artifacts/<team>/<task-id>/`. Each task gets its own UUID folder — outputs never collide.

### Milestones

Persistent coordination layer. Tasks attach to a milestone at creation. Milestone status is aggregated from all attached tasks — never a control signal.

---

## Install

```bash
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
cd /path/to/your-project
/tmp/aurorie-teams/install.sh
```

Then run:

```bash
@orchestrator "Build me a SaaS product from scratch"
```

**Requirements:** macOS or Linux · `jq` · `uuidgen` or `python3` · Node.js

**Upgrade:**

```bash
git -C /tmp/aurorie-teams pull && /tmp/aurorie-teams/install.sh
```

---

## Try it

### Build a product

```bash
@orchestrator "Create a SaaS for AI agents marketplace"
```

Product + Backend + Frontend → prd, implementation, UI

### Analyze and investigate

```bash
@orchestrator "Investigate why our DAU dropped 30% last week"
```

Data + Research → analysis, report

### Coordinate a multi-task goal

```bash
@orchestrator --milestone "Launch v1.0" "Build a crypto trading platform"
```

First task attached to milestone → `--milestone-status <id>` tracks progress across all subsequent tasks

---

## Customize

| What                              | Where                              |
|-----------------------------------|------------------------------------|
| Team routing rules                | `.claude/routing.json`             |
| Dispatch policy (auto/ask/ignore) | `.claude/routing.json` → `dispatch_policy` |
| Team workflows                    | `.claude/workflows/<team>.md`      |
| Agent tools                       | `.claude/settings.json`            |

---

## Safety

- **Agents generate outputs — no external actions unless you wire them up.**
  Default behavior is local file generation under `.claude/workspace/artifacts/`.
- **Nothing runs without your approval.** `ask` mode pauses for confirmation.
- **Use read-only credentials** where possible.
- Review `.claude/settings.json` to control per-agent tool access.

---

## Tests

**113/113 tests green** — every commit.

```bash
bash tests/install.test.sh && bash tests/lint.test.sh
python3 tests/routing/test_routing_cases.py
python3 tests/routing/test_dispatch_policy.py
python3 tests/routing/test_replay_resume.py
```

---

## Roadmap

### v0.6 — Persistent Execution Runtime *(current)*

- [x] Replay — read-only execution inspection
- [x] Resume — continue DAG from partial state
- [x] State priority invariant — `pending_decision` always blocks resume
- [x] Partial failed recovery — only failed nodes reset
- [x] Blocked node recovery — re-checks `artifacts_in`

### v0.5 — Goal-Oriented Coordination Runtime

- [x] Milestone system — cross-task tracking and aggregation
- [x] Selective routing — approve a subset of medium teams

### v0.4 — Interactive Routing Contract + DAG Execution

- [x] `pending_decision` schema + resolve interface
- [x] Wave-based DAG dispatch, parallel nodes, partial failure

### Long-term — AI-native companies

- [ ] Observability dashboard
- [ ] Automatic retry
- [ ] Cross-task resume
- [ ] Agent marketplace

---

## Contributing

We're building the AI company OS — opinionated and in public.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.
