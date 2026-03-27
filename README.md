# AURORIE TEAMS

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ██████╗██╗  ██╗ █████╗ ██████╗ ██████╗ ██╗   ██╗██████╗  │
│  ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗ │
│  ╚█████╗ ███████║███████║██████╔╝██████╔╝ ╚████╔╝ ██████╔╝ │
│   ╚═══██╗██╔══██║██╔══██║██╔═══╝ ██╔═══╝   ╚██╔╝  ██╔══██╗ │
│  ██████╔╝██║  ██║██║  ██║██║     ██║        ██║   ██████╔╝ │
│  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝        ╚═╝   ╚═════╝  │
│                                                                 │
│   ███████╗██╗██╗  ██╗████████╗██████╗  ██████╗ ███╗   ███╗  │
│   ╚══███╔╝╚██╗██╔╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔═══██╗████╗ ████║│
│     ███╔╝  ╚███╔╝  ╚███╔╝    ██║   ██████╔╝██║   ██║██╔████╔██║│
│    ███╔╝   ██╔██╗  ██╔██╗    ██║   ██╔══██╗██║   ██║██║╚██╔╝██║│
│   ███████╗██╔╝ ██╗██╔╝ ██╗   ██║   ██║  ██║╚██████╔╝██║ ╚═╝ ██║│
│   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

> **An orchestration runtime for AI teams that doesn't forget.**

`One command` → `teams dispatched` → `artifacts written` → `execution tracked + resumable`

---

### Quick status

![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue?style=flat-square&logo=apple&logoColor=white)
![Version](https://img.shields.io/badge/version-v0.8.0-222?style=flat-square&logo=semantic-release&logoColor=white)
![Tests](https://img.shields.io/badge/tests-137%2F137%20green-222?style=flat-square&logo=github-actions&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## What it does

```
@orchestrator "Build a SaaS for AI agents marketplace"

  → routes:    backend ■■■■■■■■■■■■■■■■■■■■■■■ high
               product ■■■■■■ medium
               frontend ■■■■ medium

  → policy:    auto (high) · ignore (medium, high exists)

  → graph:     [product-1] → [backend-1]
                            ↘ [frontend-1]

  → output:    .claude/workspace/artifacts/{backend,frontend,product}/<task-id>/
```

**That's not a one-shot.** If `backend-1` fails:

```
@orchestrator --resume <task-id>

  partial_failed detected — retrying failed nodes only

  Wave 1: [product-1]     ■■■■■■■■■■■■■■■ done
  Wave 2: [backend-1]     RETRY ■■■■■■■■■■■ running   ← only this
  Wave 3: [frontend-1]   (waiting for backend) — skipped

  → only backend re-ran, frontend kept its done state
```

---

## Five things that make it different

| | | | | |
|---|---|---|---|---|
| **Decision-first** | **Graph-aware execution** | **Cross-task memory** | **Adaptive execution** | **Auto-retry** |
| Every routing decision is scored and explainable. You see exactly why each team was selected, secondary, or filtered — before anything runs. | Teams run in wave-based DAG order. Dependencies are explicit. Partial failures are contained. Nothing runs blindly. | Milestones track progress across tasks and time. Replay inspects any past execution. Resume continues from where it left off. | The system learns from past execution — success_rate and template outcomes bias future routing decisions. Not ML, not autonomous: rule-based, explainable, conservative. | Failed nodes retry automatically — exactly once, next wave. No config files, no policy layer changes. `--no-auto-retry` to disable. |
| `+API +endpoint +SaaS → score 4 → high → dispatched` | `product → backend → frontend` (linear) | `@orchestrator --replay <task-id>` | `--feedback-history` → see team stats | Wave 2: backend fails → retry → Wave 3: retried |
| `+requirements +SaaS → score 2 → medium → secondary` | `research → [backend, frontend]` (parallel fan-out) | `@orchestrator --resume <task-id>` | `--feedback` → see bias in debug output | `retryable: true`, `retry_count` per node |
| `+iOS → score −2 → filtered` | blocked nodes wait, done nodes stay done | `--milestone-status <id>` | runs < 5 → no bias applied | `@orchestrator --no-auto-retry` → partial_failed |

---

## Runtime reference

| Command | What it does |
|---------|--------------|
| `@orchestrator "prompt"` | Full routing + dispatch + artifact output |
| `@orchestrator --debug "prompt"` | See every score, evaluation, and decision before anything runs |
| `@orchestrator --dry-run "prompt"` | Preview routing + graph without dispatching |
| `@orchestrator --milestone "Goal" "prompt"` | Run with milestone tracking attached |
| `@orchestrator --milestone-status <id>` | Query aggregated milestone progress |
| `@orchestrator --resolve <task-id> all\|none\|selective` | Resolve a paused decision (idempotent) |
| `@orchestrator --replay <task-id>` | Read-only: inspect past routing + execution graph |
| `@orchestrator --resume <task-id>` | Resume: `in_progress` · `partial_failed` · `blocked` |
| `@orchestrator --feedback "prompt"` | Run with feedback bias debug output (shows adjusted scores) |
| `@orchestrator --feedback-history` | Print team/template stats from execution history and exit |
| `@orchestrator --no-auto-retry "prompt"` | Run with auto-retry disabled — failed nodes stay failed |

---

## Architecture

```
    ┌──────────────────────────────────────────────────────┐
    │                     Orchestrator                      │
    │  routing.json → score teams → build DAG → dispatch   │
    └────────────────────────┬─────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
     ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
     │ Backend  │      │ Frontend│      │ Product │
     │  Team    │      │  Team   │      │  Team   │
     └────┬────┘      └────┬────┘      └────┬────┘
          │                  │                  │
     ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
     │ developer│      │ developer│      │    PM   │
     │   QA    │      │  devops │      │    UX   │
     └─────────┘      └─────────┘      └─────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │    Artifacts     │
                    │ .claude/workspace│
                    └─────────────────┘
```

**Teams:** market · product · backend · frontend · infra · data · design · mobile · support · research

---

## Install

```bash
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
cd /path/to/your-project
/tmp/aurorie-teams/install.sh

@orchestrator "Build me a SaaS product from scratch"
```

Requirements: macOS or Linux · `jq` · `uuidgen` or `python3` · Node.js

---

## Three commands to try

```bash
# 1. Build a product (triggers Product + Backend + Frontend)
@orchestrator "Create a SaaS for AI agents marketplace"
```

```bash
# 2. Investigate a drop (triggers Data + Research)
@orchestrator "Investigate why our DAU dropped 30% last week"
```

```bash
# 3. Coordinate a milestone across multiple tasks
@orchestrator --milestone "Launch v1.0" "Build the crypto trading platform"
# ... then attach more tasks to the same milestone
@orchestrator --milestone-status ms_abc123
```

---

## Customize

| What | Where |
|------|-------|
| Team routing rules | `.claude/routing.json` |
| Dispatch policy (auto / ask / ignore) | `.claude/routing.json` → `dispatch_policy` |
| Team workflows | `.claude/workflows/<team>.md` |
| Agent tool access | `.claude/settings.json` |

---

## Safety

- **Agents write files — no external actions unless you wire them up.** Default: `.claude/workspace/artifacts/`
- **Nothing runs without your approval.** `ask` mode pauses for confirmation before dispatch
- **Use read-only credentials** where possible

---

## Test suite

**137/137 tests green** — every commit.

```bash
bash tests/install.test.sh && bash tests/lint.test.sh
python3 tests/routing/test_routing_cases.py
python3 tests/routing/test_dispatch_policy.py
python3 tests/routing/test_replay_resume.py
python3 tests/routing/test_feedback.py
python3 tests/routing/test_feedback_integration.py
python3 tests/routing/test_retry.py
python3 tests/routing/test_retry_integration.py
python3 tests/routing/test_step_c_simulation.py
```

---

## Roadmap

### v0.8 — Auto-Retry Policy _(current)_
- [x] Step C retry hook — integrated into wave dispatch loop, not a post-loop hook
- [x] `retryable: true` + `retry_count: 0` fields on every node (all graph templates)
- [x] `auto_retry_enabled` in `execution_graph.metadata` — readable in replay/debug
- [x] `--no-auto-retry` flag — disables auto-retry for this run, no config changes needed
- [x] `lib/retry.py` — pure functions: `check_retry_eligible`, `reset_for_retry`, `maybe_retry_nodes`
- [x] Final status semantics: retry-then-success → `completed`, unrecoverable → `partial_failed`
- [x] `test_step_c_simulation.py` — deterministic wave-level Step C simulation (R6/R8/R9)

### v0.7 — Adaptive Execution Runtime
- [x] Execution feedback loop — append-only JSONL event log
- [x] Team bias — success_rate-based score multiplier with MIN_SAMPLES guard
- [x] Graph template learning — template success_rate tracked and biased
- [x] `--feedback` and `--feedback-history` CLI flags
- [x] Terminal-state hook — automatic event write on task completion

### v0.6 — Persistent Execution Runtime
- [x] Replay — read-only execution inspection
- [x] Resume — continue DAG from partial state
- [x] State priority invariant — `pending_decision` always blocks resume
- [x] Partial failed recovery — only failed nodes reset
- [x] Blocked node recovery — re-checks `artifacts_in` before unblocking

### v0.5 — Goal-Oriented Coordination Runtime
- [x] Milestone system — cross-task tracking and aggregation
- [x] Selective routing — approve a subset of medium teams

### v0.4 — Interactive Routing Contract + DAG Execution
- [x] `pending_decision` schema + resolve interface
- [x] Wave-based DAG dispatch, parallel nodes, partial failure

### Long-term
- [ ] Observability dashboard
- [ ] Cross-task resume
- [ ] Agent marketplace

---

**Built with opinionated defaults. Customize everything.**
