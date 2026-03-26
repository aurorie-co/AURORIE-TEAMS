# Debug Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `--debug` flag support to the orchestrator so users can see a full per-team routing trace in the terminal without changing routing decisions or dispatch behavior.

**Architecture:** Two insertions into `shared/agents/orchestrator.md` only — a new Step 0 (flag detection and stripping) and a new Step 7.5 (debug trace rendered from the already-computed `routing_decision`). Steps 1–7 and Step 8 are untouched. Debug output is a pure projection of `routing_decision`; no re-evaluation occurs.

**Tech Stack:** Markdown (orchestrator instruction file). No new code files. No new dependencies.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `shared/agents/orchestrator.md` | Modify | Insert Step 0 + Step 7.5 |

---

## Task 1: Insert Step 0 — Flag parsing

**Files:**
- Modify: `shared/agents/orchestrator.md` (insert after `## Routing\n\n`, before `### Step 1`)

- [ ] **Step 1: Read the current file and locate the insertion point**

  Read `shared/agents/orchestrator.md`. Find the exact text:

  ```
  ## Routing

  ### Step 1 — Read policy
  ```

  Step 0 must be inserted between `## Routing` and `### Step 1 — Read policy`.

- [ ] **Step 2: Insert Step 0**

  Using the Edit tool, replace:

  ```
  ## Routing

  ### Step 1 — Read policy
  ```

  With:

  ```
  ## Routing

  ### Step 0 — Parse debug flag

  Inspect the raw user input before any routing begins.

  **If `--debug` appears as a standalone token** (space-delimited; do not match `--debug` embedded in natural language like `"build --debug mode feature"`):
  - Set `debug_mode = true`
  - Strip `--debug` from the input. Also strip `--dry-run` if present (reserved — no-op in v0.2.x).
  - Use the remaining text as `clean_prompt` for all subsequent steps.

  **If `--debug` is absent:**
  - `debug_mode = false`
  - Continue normally. Steps 1–7 and Step 8 are completely unaffected.

  **Step 0 does nothing else.** Do not read routing.json, score teams, or produce output here.

  ### Step 1 — Read policy
  ```

- [ ] **Step 3: Verify the file looks correct**

  Run:
  ```bash
  grep -n "Step 0\|Step 1\|Step 7\|Step 8" shared/agents/orchestrator.md
  ```

  Expected output should show Step 0 appearing before Step 1, and steps numbered in correct order.

- [ ] **Step 4: Run tests — confirm nothing broke**

  ```bash
  python3 tests/routing/test_routing_cases.py
  ```

  Expected:
  ```
  Running 5 routing test cases...

    ✓ backend_high_only
    ✓ high_with_secondary
    ✓ medium_only
    ✓ fallback_needs_clarification
    ✓ negative_keyword_suppression

  Results: 5 passed, 0 failed
  ```

  Then:
  ```bash
  bash tests/lint.test.sh 2>&1 | tail -5
  ```

  Expected: `Passed: 50` (or more), `Failed: 0`.

- [ ] **Step 5: Commit**

  ```bash
  git add shared/agents/orchestrator.md
  git commit -m "feat(orchestrator): add Step 0 — debug flag parsing"
  ```

---

## Task 2: Insert Step 7.5 — Debug render

**Files:**
- Modify: `shared/agents/orchestrator.md` (insert between Step 7 closing paragraph and `### Step 8`)

- [ ] **Step 1: Locate the insertion point**

  Find the exact text near the end of Step 7:

  ```
  Always use the actual `routing_policy` values from the current `routing.json` when writing `policy_snapshot` — not hardcoded values.

  ### Step 8 — Output user summary
  ```

  Step 7.5 must be inserted between that closing paragraph and `### Step 8`.

- [ ] **Step 2: Insert Step 7.5**

  Using the Edit tool, replace:

  ```
  Always use the actual `routing_policy` values from the current `routing.json` when writing `policy_snapshot` — not hardcoded values.

  ### Step 8 — Output user summary
  ```

  With:

  ```
  Always use the actual `routing_policy` values from the current `routing.json` when writing `policy_snapshot` — not hardcoded values.

  ### Step 7.5 — Render debug trace (debug mode only)

  **Skip entirely if `debug_mode = false`.**

  Read the following fields from `routing_decision` (written in Step 7). Do not re-evaluate or re-score anything.

  Fields needed:
  - `dispatch_strategy` — top-level field on `routing_decision`
  - `policy_snapshot.candidate_threshold`
  - `policy_snapshot.confidence_thresholds.high`
  - `policy_snapshot.confidence_thresholds.medium`
  - `selected_teams[]` — each entry: `team`, `score`, `confidence`, `matched_positive[]`, `matched_negative[]`
  - `secondary_teams[]` — same fields
  - `filtered_teams[]` — same fields

  Print exactly this block:

  ```
  === ROUTING DEBUG ===

  Policy:
  - candidate_threshold: <policy_snapshot.candidate_threshold>
  - confidence.high: <policy_snapshot.confidence_thresholds.high>
  - confidence.medium: <policy_snapshot.confidence_thresholds.medium>
  - dispatch_strategy: <routing_decision.dispatch_strategy>

  Evaluations:
  <for each team: first selected_teams, then secondary_teams, then filtered_teams>
  <team>: score <score>, <confidence> → <state>
    + <matched_positive joined by ", ", or "(none)" if empty>
    - <matched_negative joined by ", ", or "(none)" if empty>

  Dispatch:
    Selected:  <selected_teams[*].team joined by ", ", or "(none)" if empty>
    Secondary: <secondary_teams[*].team joined by ", ", or "(none)" if empty>
    Filtered:  <filtered_teams[*].team joined by ", ", or "(none)" if empty>

  === END ROUTING DEBUG ===
  ```

  Rendering rules:
  - `score`: read from `routing_decision` — never recomputed. If the field is absent, display `N/A`.
  - `confidence = low`: assigned when score < `confidence_thresholds.medium` (implicit — not a configurable key).
  - `state`: `selected` for entries in `selected_teams`, `secondary` for `secondary_teams`, `filtered` for `filtered_teams`.
  - Within each group, maintain the order from `routing_decision` (score desc, positive_count desc, negative_count asc — matching Step 3.5).
  - All three sections (Selected / Secondary / Filtered) are always printed, even when empty.
  - Fallback case: `Selected: (none)`, `Secondary: (none)`, all teams appear under `Filtered`.

  Proceed immediately to Step 8 after printing.

  ### Step 8 — Output user summary
  ```

- [ ] **Step 3: Verify step ordering**

  ```bash
  grep -n "### Step" shared/agents/orchestrator.md
  ```

  Expected order: Step 0, Step 1, Step 2, Step 3, Step 3.5, Step 4, Step 5, Step 6, Step 7, **Step 7.5**, Step 8, Step A, Step B.

- [ ] **Step 4: Run tests — confirm nothing broke**

  ```bash
  python3 tests/routing/test_routing_cases.py
  ```

  Expected: 5 passed, 0 failed.

  ```bash
  bash tests/lint.test.sh 2>&1 | tail -5
  ```

  Expected: Passed: 50 (or more), Failed: 0.

- [ ] **Step 5: Commit**

  ```bash
  git add shared/agents/orchestrator.md
  git commit -m "feat(orchestrator): add Step 7.5 — debug trace render from routing_decision"
  ```

---

## Task 3: Sync to .claude/ and manual smoke test

**Files:**
- Read: `install.sh` (to find the copy command for shared/ → .claude/)

- [ ] **Step 1: Find how shared/ syncs to .claude/**

  ```bash
  grep -n "orchestrator" install.sh | head -10
  ```

  This shows the copy command. Run it to sync the updated orchestrator.md to your local `.claude/agents/`.

- [ ] **Step 2: Smoke test — normal prompt (no --debug)**

  Invoke the orchestrator with a normal prompt (no `--debug`). Verify:
  - No debug block appears in the output
  - Routing and dispatch work as before

  Example prompt: `@orchestrator "Add a REST endpoint for user authentication with JWT"`

  Expected: normal `Routed to: backend (high)` summary, no `=== ROUTING DEBUG ===` block.

- [ ] **Step 3: Smoke test — debug prompt, high confidence**

  Invoke: `@orchestrator --debug "Build a SaaS platform with user requirements and API endpoints"`

  Expected output (order: debug block → normal summary → dispatch):

  ```
  === ROUTING DEBUG ===

  Policy:
  - candidate_threshold: 1
  - confidence.high: 3
  - confidence.medium: 1
  - dispatch_strategy: conditional

  Evaluations:
  backend: score 4, high → selected
    + ...
    - (none)
  product: score 2, medium → secondary
    + ...
    - (none)
  frontend: score 1, medium → secondary
    + ...
    - (none)
  [remaining teams as filtered]

  Dispatch:
    Selected:  backend
    Secondary: product, frontend
    Filtered:  market, mobile, data, ...

  === END ROUTING DEBUG ===

  Routed to:
  - backend (high, score ...)
  ...
  ```

- [ ] **Step 4: Smoke test — debug prompt, fallback**

  Invoke: `@orchestrator --debug "Help me with this thing"`

  Expected: debug block shows `Selected: (none)`, `Secondary: (none)`, all teams under `Filtered`. Normal fallback clarifying question follows.

- [ ] **Step 5: Commit install script sync (only if install.sh was modified)**

  If `install.sh` required any changes (unlikely), commit them:
  ```bash
  git add install.sh
  git commit -m "chore: update install.sh for debug mode orchestrator"
  ```

  If no changes needed, skip this step.

---

## Self-Review

**Spec coverage:**
- ✅ Step 0: flag parsing, standalone token rule, clean_prompt stripping, --dry-run strip no-op
- ✅ Step 7.5: pure render from routing_decision, three-section format, ordering rules
- ✅ Fallback case: (none) for selected/secondary, all teams in filtered
- ✅ score from routing_decision only, N/A if absent
- ✅ confidence = low definition
- ✅ ROUTING DEBUG / END ROUTING DEBUG boundary
- ✅ policy_snapshot fields specified
- ✅ Steps 1–7 and Step 8 unchanged
- ✅ Existing 5 routing tests still pass (verified in each task)

**Not covered (out of scope per spec):**
- --dry-run execution logic (v0.3)
- Automated snapshot test for debug output
