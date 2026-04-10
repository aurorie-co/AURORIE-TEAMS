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
![Version](https://img.shields.io/badge/version-v0.9.0-222?style=flat-square&logo=semantic-release&logoColor=white)
![Tests](https://img.shields.io/badge/tests-225%2F225%20green-222?style=flat-square&logo=github-actions&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## What it does

```
@aurorie-orchestrator "Build a SaaS for AI agents marketplace"

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
@aurorie-orchestrator --resume <task-id>

  partial_failed detected — retrying failed nodes only

  Wave 1: [product-1]     ■■■■■■■■■■■■■■■ done
  Wave 2: [backend-1]     RETRY ■■■■■■■■■■■ running   ← only this
  Wave 3: [frontend-1]   (waiting for backend) — skipped

  → only backend re-ran, frontend kept its done state
```

---

## Six things that make it different

| | | | | | |
|---|---|---|---|---|---|
| **Decision-first** | **Graph-aware execution** | **Cross-task memory** | **Adaptive execution** | **Auto-retry** | **Verified execution** |
| Every routing decision is scored and explainable. You see exactly why each team was selected, secondary, or filtered — before anything runs. | Teams run in wave-based DAG order. Dependencies are explicit. Partial failures are contained. Nothing runs blindly. | Milestones track progress across tasks and time. Replay inspects any past execution. Resume continues from where it left off. | The system learns from past execution — success_rate and template outcomes bias future routing decisions. Not ML, not autonomous: rule-based, explainable, conservative. | Failed nodes retry automatically — exactly once, next wave. `--no-auto-retry` to disable. | `node = done` is not what the model says — it is what `verification_command` exit code confirms. |
| `+API +endpoint → score 4 → high → dispatched` | `product → backend → frontend` (linear) | `@aurorie-orchestrator --replay <task-id>` | `--feedback-history` → see team stats | Wave 2: fails → retry → Wave 3: retried | backend node: `pytest tests/` exit 0 → done |
| `+requirements → score 2 → medium → secondary` | `research → [backend, frontend]` (parallel) | `@aurorie-orchestrator --resume <task-id>` | `--feedback` → see bias in debug output | `retryable: true`, `retry_count` per node | verify failure → node failed → retry hook fires |
| `+iOS → score −2 → filtered` | blocked nodes wait, done nodes stay done | `--milestone-status <id>` | runs < 5 → no bias applied | `@aurorie-orchestrator --no-auto-retry` → partial_failed | whitelist: `python3`, `pytest`, `bash`, `sh` only |

---

## Runtime reference

| Command | What it does |
|---------|--------------|
| `@aurorie-orchestrator "prompt"` | Full routing + dispatch + artifact output |
| `@aurorie-orchestrator --debug "prompt"` | See every score, evaluation, and decision before anything runs |
| `@aurorie-orchestrator --dry-run "prompt"` | Preview routing + graph without dispatching |
| `@aurorie-orchestrator --milestone "Goal" "prompt"` | Run with milestone tracking attached |
| `@aurorie-orchestrator --milestone-status <id>` | Query aggregated milestone progress |
| `@aurorie-orchestrator --resolve <task-id> all\|none\|selective` | Resolve a paused decision (idempotent) |
| `@aurorie-orchestrator --replay <task-id>` | Read-only: inspect past routing + execution graph |
| `@aurorie-orchestrator --resume <task-id>` | Resume: `in_progress` · `partial_failed` · `blocked` |
| `@aurorie-orchestrator --feedback "prompt"` | Run with feedback bias debug output (shows adjusted scores) |
| `@aurorie-orchestrator --feedback-history` | Print team/template stats from execution history and exit |
| `@aurorie-orchestrator --no-auto-retry "prompt"` | Run with auto-retry disabled — failed nodes stay failed |

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

@aurorie-orchestrator "Build me a SaaS product from scratch"
```

Requirements: macOS or Linux · `jq` · `uuidgen` or `python3` · Node.js

---

## Three commands to try

```bash
# 1. Build a product (triggers Product + Backend + Frontend)
@aurorie-orchestrator "Create a SaaS for AI agents marketplace"
```

```bash
# 2. Investigate a drop (triggers Data + Research)
@aurorie-orchestrator "Investigate why our DAU dropped 30% last week"
```

```bash
# 3. Coordinate a milestone across multiple tasks
@aurorie-orchestrator --milestone "Launch v1.0" "Build the crypto trading platform"
# ... then attach more tasks to the same milestone
@aurorie-orchestrator --milestone-status ms_abc123
```

---

## Demos

### v0.9 — Verified Node Completion

Terminal demo showing the v0.9 verification loop in action.

```bash
python3 demo/v0.9/demo_script.py
```

Covers:
- Node with `verification_command`: exit 0 → done, non-zero → failed
- Execution failure skips verification (priority: execution > verification)
- Verification failure + retryable → retry fires once → retried node succeeds → `completed`
- Verification failure + non-retryable → `partial_failed`

Duration: ~30 seconds (terminal output, no recording needed)

### v0.8 — Auto-Retry Policy

Deterministic Step C wave simulation showing retry behavior at the runtime level.

```bash
python3 demo/v0.8/demo_script.py
```

Covers:
- Wave 1 fails → retry fires → Wave 2 retried node succeeds → `completed`
- `--no-auto-retry` → unrecoverable `partial_failed`
- Retry exhausted → `partial_failed`

Duration: ~30 seconds (terminal output, no recording needed)

### v0.7 — Adaptive Execution Runtime

Timed terminal demo showing how execution history changes future routing decisions.

```bash
# Seed history first
python3 demo/v0.7/seed_history.py

# Run the demo (record with QuickTime)
python3 demo/v0.7/demo_script.py
```

Covers:
- Same prompt run twice — first run no history (baseline), second run with history (bias applied)
- `backend` success_rate=0.4 → bias=0.75 → adjusted_score drops from 3.0 → 2.25
- Template selection biased by historical performance

Duration: ~2:30 (timed narration)

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

### v0.9 — Verified Execution Runtime _(current)_
- [x] `lib/verify.py` — `validate_verification_command()` + `run_verification()` (token-based allowlist)
- [x] `verification_command` field on nodes (optional, additive)
- [x] Execution failure vs verification failure — two distinct failure sources
- [x] Step C: verification runs after node reports success; exit 0 → done, non-zero → failed
- [x] Verification failure reuses existing `auto_retry` / `partial_failed` semantics
- [x] 5 new Step C simulation tests (V9-1 through V9-5) — 225/225 total tests

### v0.8 — Auto-Retry Policy
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
