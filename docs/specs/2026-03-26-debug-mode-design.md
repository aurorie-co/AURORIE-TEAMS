# Spec: Debug Mode (v0.2.x)

**Date:** 2026-03-26
**Scope:** `--debug` flag support in the orchestrator. Adds a per-team routing trace to terminal output without altering routing decisions or dispatch behavior.
**Goal:** Make the routing engine observable — turn the "black box" into a system where users can see exactly why each team was selected, secondary, or filtered.

---

## Core Principle

> Debug output is a pure projection of `routing_decision`.
> It must not introduce any new computation or inference.

Debug mode is an **observability layer**, not an execution control layer. It changes what is printed; it does not change what is decided or dispatched.

---

## Goals

- Show routing policy, per-team scores, and final dispatch in the terminal
- Source all data from the already-computed `routing_decision` (no re-evaluation)
- Leave Steps 1–7 of the orchestrator completely untouched
- Keep the existing 5 routing test cases passing without modification
- Lay groundwork for `--dry-run` extension (v0.3+) without implementing it now

## Out of Scope

- `--dry-run` (design-compatible, not implemented in v0.2.x)
- Colored terminal output
- Interactive / expandable output
- Artifact-level debug pages or dashboard

---

## Required Invariant

All evaluated teams must appear in exactly one of the three lists in `routing_decision`:

```
selected_teams ∪ secondary_teams ∪ filtered_teams = all evaluated teams
```

This is a structural invariant of `routing_decision`. Step 7.5 relies on it to render a complete trace without consulting `rules[]` again. If a future threshold change could violate this invariant, the routing pipeline (not debug mode) must be fixed.

---

## Architecture

```
Step 0   ← NEW: parse --debug flag
Step 1–7 ← UNCHANGED
Step 7.5 ← NEW: render debug trace from routing_decision
Step 8   ← UNCHANGED: normal summary + dispatch
```

### Step 0 — Flag Parsing

Inspect the raw user input before any routing begins:

1. If `--debug` is present **as a standalone token** (not embedded in natural language, e.g. `"build --debug mode"` does not trigger it):
   - Set `debug_mode = true`
   - Strip `--debug` (and `--dry-run` if present — reserved, no-op for now) from the input
   - The remaining text is `clean_prompt` — pass this to Steps 1–7

2. If `--debug` is absent:
   - `debug_mode = false`
   - Proceed normally; Steps 1–7 and 8 are unaffected

**Step 0 does nothing else.** It does not read routing.json, score teams, or produce output.

### Steps 1–7 — Unchanged

The routing pipeline runs on `clean_prompt` exactly as before. Scoring, candidate threshold, confidence bands, dispatch strategy, task JSON writes — all unchanged.

The only input change is that `clean_prompt` has had `--debug` stripped. The routing results must be identical to a non-debug invocation with the same semantic prompt.

### Step 7.5 — Debug Render

**Precondition:** `debug_mode = true` AND Step 7 has written `routing_decision`.

**Source:** `routing_decision` only — specifically:
- `policy_snapshot` — must include all routing_policy fields required to interpret the routing result: `candidate_threshold`, `confidence_thresholds` (high + medium), and `dispatch_strategy`
- `selected_teams[]` — each entry has `team`, `score`, `confidence`, `matched_positive`, `matched_negative`
- `secondary_teams[]` — same fields
- `filtered_teams[]` — same fields

**Output format:**

```
=== ROUTING DEBUG ===

Policy:
- candidate_threshold: <value>
- confidence.high: <value>
- confidence.medium: <value>
- dispatch_strategy: <value>

Evaluations:
<team>: score <N>, <confidence> → <state>
  + <matched_positive keywords, comma-separated, or "(none)">
  - <matched_negative keywords, comma-separated, or "(none)">
[repeat for all teams, ordered: selected → secondary → filtered]

Dispatch:
  Selected:  <team list, or "(none)">
  Secondary: <team list, or "(none)">
  Filtered:  <team list, or "(none)">

=== END ROUTING DEBUG ===
```

**Rendering rules:**

- `score` is read directly from `routing_decision` — never recomputed
- `confidence` values: `high` and `medium` are assigned by `confidence_thresholds`; `low` is assigned when `score < confidence_thresholds.medium` (implicit, not configurable)
- `state` label: `selected`, `secondary`, or `filtered`
- Empty lists render as `(none)` — the three-section structure is always present
- Teams are listed ordered: selected group → secondary group → filtered group. Within each group, order is `(score desc, positive_count desc, negative_count asc)` — matching routing Step 3.5
- All teams from all three lists are printed — no team is omitted
- `matched_positive` and `matched_negative` are printed verbatim from `routing_decision`
- **Fallback case:** when no teams are selected or secondary, the Dispatch block must show `Selected: (none)` and `Secondary: (none)`, with all teams appearing under `Filtered`

**Example output:**

```
=== ROUTING DEBUG ===

Policy:
- candidate_threshold: 1
- confidence.high: 3
- confidence.medium: 1
- dispatch_strategy: conditional

Evaluations:
backend: score 4, high → selected
  + API, endpoint, authentication
  - (none)
product: score 2, medium → secondary
  + requirements, SaaS
  - (none)
market: score -1, low → filtered
  + blog
  - iOS
mobile: score -3, low → filtered
  + (none)
  - blog post, write a
frontend: score 1, medium → secondary
  + SaaS
  - (none)
[...remaining teams...]

Dispatch:
  Selected:  backend
  Secondary: product, frontend
  Filtered:  market, mobile, data, ...

=== END ROUTING DEBUG ===
```

### Step 8 — Normal Summary + Dispatch

Unchanged. Runs after Step 7.5 (if debug) or after Step 7 (if not debug).

**Output order in debug mode:**

```
[debug block]
[normal summary]
[dispatch / execution]
```

---

## Score Field Contract

`routing_decision` already stores `score` on every team entry (selected, secondary, filtered). Step 7.5 reads this field directly. This is the **only permitted source** for scores in debug output.

If `score` is absent from a team entry (schema regression), Step 7.5 must display `score: N/A` rather than recompute.

---

## `--dry-run` Extension (Future)

Syntax: `--debug --dry-run`

When both flags are present (future implementation):
- Print debug block as normal
- Skip dispatch
- Print: `Dry run — no teams were dispatched.`

Step 0 already strips both flags. No other changes are needed now; this is a placeholder for v0.3.

---

## Testing

The existing 5 routing cases in `tests/routing/test_routing_cases.py` remain unchanged. Debug mode does not affect `selected`, `secondary`, `fallback`, or `filtered` results — the routing evaluator is not modified.

No automated snapshot test for debug output is required in v0.2.x. Manual verification:
- Run `@orchestrator --debug "Build a SaaS platform..."` and confirm all three sections appear
- Confirm routing result matches non-debug invocation of the same prompt
- Confirm `--debug "Help me with this thing"` shows fallback with Filtered listing all teams

---

## File Changes

| File | Action | Change |
|---|---|---|
| `shared/agents/orchestrator.md` | Modify | Add Step 0 (flag parse) + Step 7.5 (debug render) |

No changes to `shared/routing.json`, team workflows, or existing tests.
