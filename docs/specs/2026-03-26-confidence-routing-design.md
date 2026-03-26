# Spec: Confidence-Based Routing (v0.2.0)

**Date:** 2026-03-26
**Scope:** Add confidence bands, conditional dispatch policy, and structured routing explanation to the orchestrator routing pipeline.
**Version target:** v0.2.0

---

## Goals

- Surface a confidence level (high / medium / low) for each routing decision
- Apply conditional dispatch: high-confidence teams execute, medium-confidence teams surface as secondary when high exists
- Write a complete `routing_decision` record into every task JSON for observability and future dashboard use
- Show a short, rules-derived routing summary to the user in the terminal
- Keep all routing policy values in `routing.json` as the single source of truth

## Out of Scope (v0.2.0)

- `dispatch_policy` configuration in `routing.json` (v0.3)
- Interactive user confirmation for medium teams (v0.3+)
- UI dashboard
- ML/semantic routing
- README or release notes update (separate PR)

---

## Schema Changes

### 1. `routing.json` — new top-level field

Add alongside the existing `"rules"` and `"fallback"` keys:

```json
"routing_policy": {
  "candidate_threshold": 1,
  "confidence_thresholds": {
    "high": 3,
    "medium": 1
  }
}
```

**Threshold semantics (inclusive lower bounds):**

```
net_score >= high    → confidence = "high"
net_score >= medium AND net_score < high → confidence = "medium"
net_score < medium   → confidence = "low" / filtered
```

**Default fallback (orchestrator must implement):**
If `routing_policy` is missing or incomplete, apply defaults:
- `candidate_threshold = 1`
- `confidence_thresholds.high = 3`
- `confidence_thresholds.medium = 1`

### 2. Task JSON — new `routing_decision` field

`routing_decision` is **optional** in the task JSON schema for backward compatibility with existing task files. Adding it must not break any existing consumer.

```json
"routing_decision": {
  "routing_schema_version": "v0.2",
  "policy_snapshot": {
    "candidate_threshold": 1,
    "confidence_thresholds": {
      "high": 3,
      "medium": 1
    },
    "dispatch_policy": {
      "high": "selected",
      "medium_when_high_exists": "secondary",
      "medium_when_no_high_exists": "selected",
      "low": "filtered"
    }
  },
  "dispatch_strategy": "conditional",
  "top_signals": ["API", "authentication"],
  "selected_teams": [
    {
      "team": "backend",
      "score": 4,
      "confidence": "high",
      "matched_positive": ["API", "endpoint", "authentication"],
      "matched_negative": []
    }
  ],
  "secondary_teams": [
    {
      "team": "product",
      "score": 2,
      "confidence": "medium",
      "matched_positive": ["requirements"],
      "matched_negative": []
    }
  ],
  "filtered_teams": [
    {
      "team": "research",
      "score": 0,
      "confidence": "low",
      "matched_positive": [],
      "matched_negative": []
    }
  ]
}
```

**Notes:**
- `policy_snapshot` captures the thresholds at time of execution, so historical records remain interpretable after `routing.json` is updated.
- All three team arrays use identical structure (including `matched_positive` / `matched_negative`) for consistent processing.
- `top_signals` is the union of `matched_positive` from `selected_teams`, deduplicated, top 3–5 terms. Drives the user-visible Reason line without re-computation.
- `dispatch_policy` inside `policy_snapshot` documents the current behavior description (not yet configurable; v0.3 will make it configurable).

---

## Orchestrator Decision Flow

Replaces the existing Routing section of `orchestrator.md`.

### Step 1 — Read policy

Read `routing.json`. Extract `routing_policy`. If missing or incomplete, apply defaults (see Schema section).

### Step 2 — Score each team

For each rule in `rules[]`:

```
net_score = count(positive_keywords matched) - 2 × count(negative_keywords matched)
```

Record `matched_positive[]` and `matched_negative[]` per team. Matching is case-insensitive, partial word match counts (existing behavior preserved).

### Step 3 — Candidate filter

```
if net_score < candidate_threshold:
    → filtered_teams (no further processing)
else:
    → candidate pool
```

### Step 3.5 — Sort candidate pool

Sort all candidates by:
1. `net_score` descending
2. `matched_positive` count descending
3. `matched_negative` count ascending

Stable sort ensures deterministic ordering for equal scores.

### Step 4 — Assign confidence bands

For each candidate:

```
if net_score >= thresholds.high   → confidence = "high"
elif net_score >= thresholds.medium → confidence = "medium"
```

(Low / filtered teams were eliminated in Step 3 and never reach this step under default thresholds where `medium = 1 = candidate_threshold`.)

### Step 5 — Conditional dispatch

```
if any high candidates exist:
    selected_teams = all high candidates (in sorted order)
    secondary_teams = all medium candidates
    dispatch_strategy = "conditional"

elif any medium candidates exist:
    selected_teams = all medium candidates (in sorted order)
    secondary_teams = []
    dispatch_strategy = "conditional"

else:
    → FALLBACK (see below)
```

**Parallel dispatch:** When `selected_teams` contains multiple teams, dispatch them in parallel (existing Step B behavior).

### Step 6 — Fallback behavior

Triggered when no candidates survive Step 3, or all survivors are filtered:

- Do **not** dispatch any team
- Do **not** generate any artifact
- Write task JSON with `status = "needs_clarification"` and `routing_decision.selected_teams = []`
- Output a single clarifying question to the user, then re-evaluate on their reply

### Step 7 — Write `routing_decision` to task JSON

Write the complete `routing_decision` block (per schema above) alongside the existing task fields. Compute `top_signals` as the top 3–5 deduplicated terms from `matched_positive` across `selected_teams`.

### Step 8 — Output user summary (terminal)

Template — when high teams exist:

```
Routed to:
- <team> (<confidence>, score <N>)

Also relevant (not dispatched):
- <team> (<confidence>, score <N>)

Reason: matched "<signal1>", "<signal2>".
```

Template — when only medium teams exist:

```
Routed to:
- <team> (medium, score <N>)

No high-confidence teams found.

Reason: matched "<signal1>", "<signal2>".
```

**Rules:**
- "Reason" is constructed from `top_signals` only — never free-form generated text
- Rejected/filtered teams are NOT listed in the summary (to avoid noise)
- "Also relevant" section is omitted entirely when `secondary_teams` is empty
- Secondary teams are listed under "Also relevant" with a note that they were not dispatched

---

## Files Changed

| File | Change type | Scope |
|---|---|---|
| `.claude/routing.json` | New field | Top-level `routing_policy` block |
| `.claude/agents/orchestrator.md` | Replace section | Full Routing section (Steps 1–8) |

**Not changed:** all team lead agents, workflow files, install scripts, README, CHANGELOG.

---

## Validation Checklist

Before merging, run these five prompts and verify:

1. **High only:** `"Add a REST endpoint for user authentication"` → backend high, no secondary
2. **High + secondary:** `"Build a crypto trading SaaS with user requirements"` → backend high, product secondary
3. **Medium-only fallback:** Low-specificity prompt with no strong keywords → medium teams dispatch, summary says "No high-confidence teams found"
4. **Filtered fallback:** Fully ambiguous prompt → fallback, `needs_clarification`, clarifying question output
5. **Negative keyword suppression:** `"Write a blog post about our iOS app"` → market routes, mobile does NOT despite iOS mention (negative keyword in market rule fires correctly)

For each: confirm `routing_decision` JSON in task file matches terminal summary.
