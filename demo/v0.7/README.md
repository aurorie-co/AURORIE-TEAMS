# v0.7 Demo — "History Changes Decisions"

**Duration:** 2–3 minutes
**Goal:** Show that the same prompt produces different routing after history accumulates.

---

## Pre-Demo Setup

Run this once before recording to seed the history:

```bash
cd /path/to/aurorie-teams
python3 demo/v0.7/seed_history.py
```

This writes 17 events to `.claude/workspace/execution_history.jsonl`:
- **backend**: 5 initial runs, 2 completed, 3 partial_failed → success_rate = 0.4 → bias = 0.75
- **linear** template: 6 runs, 4 completed, 2 partial_failed → success_rate = 0.67 → bias = 0.9
- **data-first** template: 6 runs, 5 completed, 1 partial_failed → success_rate = 0.83 → bias = 1.0

---

## Demo Script

### 🎬 Opening (0:00–0:15)

> "AURORIE TEAMS v0.7. The system doesn't just execute — it learns from execution history."

> "Watch what happens when the same prompt runs twice, with history in between."

---

### 🟢 Part 1 — First Run: No History (0:15–0:45)

**Action:**
```bash
# First, clear history to start fresh
@orchestrator --feedback "Build a SaaS landing page"
```

> "No history yet. Every team starts with bias = 1.0."
>
> "Backend gets raw_score: 3, adjusted_score: 3."
>
> "Nothing penalizes it — we have no data."

**What to show in terminal:**
```
backend:
  raw_score: 3
  runs: 0
  success_rate: N/A
  feedback_bias: 1.0
  adjusted_score: 3.0
  confidence: high
```

> "All teams at bias 1.0. This is the baseline."

---

### 🔴 Part 2 — Check History (0:45–1:15)

**Action:**
```bash
@orchestrator --feedback-history
```

> "Here's what's accumulated since then:"
>
> "Backend: 5 runs, 40% success rate → bias 0.75."
>
> "The linear template: 67% success rate → bias 0.9."
>
> "data-first template: 83% success rate — top performer."

**What to show:**
```
backend:
  runs: 5
  success_rate: 0.4
  success_rate_display: "0.4" (5 runs)

Templates:
  data-first:  runs=6, success_rate=0.83, bias=1.0
  linear:       runs=6, success_rate=0.67, bias=0.9
  flat:         runs=0, insufficient data
```

> "The system has been paying attention."

---

### 🔵 Part 3 — Second Run: Same Prompt, Different Decision (1:15–2:30)

**Action:**
```bash
@orchestrator --feedback "Build a SaaS landing page"
```

> "Same prompt. Same teams. But now history exists."
>
> "Watch backend: raw_score is still 3 — nothing changed in the routing rules."
>
> "But adjusted_score is now 2.25 — because 0.75 × 3 = 2.25."
>
> "Its confidence dropped from high to medium — purely from history."

**What to show:**
```
backend:
  raw_score: 3
  runs: 5
  success_rate: 0.4
  feedback_bias: 0.75
  adjusted_score: 2.25    ← this changed
  confidence: medium       ← this changed
```

> "**Nothing changed in the prompt.**
> **Only the history changed — and the decision changed.**"

> "If the dispatch policy says 'medium confidence teams require confirmation,'
> this task now pauses and asks."
>
> "Without history, it would've auto-dispatched."

**Show template selection:**
```
Template candidates:
  data-first:  bias=1.0  ✓ (best historical performance)
  linear:       bias=0.9
  flat:         bias=1.0  (insufficient data)

Selected template: data-first
```

> "The execution graph structure is also informed by history."

---

### 🎯 Closing (2:30–3:00)

> "That's the feedback loop:"
>
> "Task completes → event written."
> "Next routing → history read."
> "Score adjusted."
>
> "Not ML. Not autonomous. Rule-based, explainable, conservative."
>
> "runs < 5 → no bias. High performers → no penalty."
>
> "The system doesn't just execute anymore."
> "It improves how it executes."

---

## Three Sentences to Memorize

1. **"First run — no history."**
2. **"History accumulates."**
3. **"Next run — different decision."**

---

## What the Demo Proves

| | Without History | With History |
|---|---|---|
| backend adjusted_score | 3.0 | 2.25 |
| backend confidence | high | medium |
| Template bias applied | no | yes |
| Dispatch outcome | auto | may-pause |

---

## Files in This Demo

```
demo/v0.7/
  README.md          ← this file
  seed_history.py    ← seeds .claude/workspace/execution_history.jsonl
  history/
    seed.jsonl        ← the 17-event history file
```
