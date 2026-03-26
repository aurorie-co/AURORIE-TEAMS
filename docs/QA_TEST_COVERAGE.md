# QA Test Coverage Report — v0.3 / v0.4 / v0.5

> **Reviewer:** Senior QA Engineer
> **Scope:** dispatch_policy (v0.3), pending_decision + DAG execution (v0.4), milestone coordination (v0.5)
> **Date:** 2026-03-26
> **Status:** 83/83 tests green (78 dispatch/routing + 5 routing cases)
> **Last updated:** After G-20/G-22 blocked node tests

---

## Executive Summary

| Layer | Feature | Coverage | Notes |
|-------|---------|----------|-------|
| v0.3 | Dispatch policy (normalize, auto, ask) | ✅ Strong | 18 cases, pure functions well-tested |
| v0.4 | Interactive routing (pending_decision + resolve) | ✅ Good | 14 Phase1 + 3 E2E runtime tests |
| v0.4 | DAG execution (Step C) | ✅ Good | Template selection + 6 P0 runtime + 3 blocked node tests |
| v0.5 | Milestone coordination | ✅ Good | 14 unit + 2 E2E wiring |
| v0.5 | Selective routing | ✅ Good | 6 selective resolve tests |

**Overall verdict:** P0 runtime gaps now closed. Core logic well-tested. Remaining gaps are lower-risk integration and CLI contract tests.

---

## v0.3 — Controllable Execution

### NORMALIZE (4/4 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `normalize_missing_returns_defaults` | `dispatch_policy` absent → fills all defaults | ✅ |
| 2 | `normalize_partial_fills_medium_defaults` | `high: "auto"`, medium absent → fills medium defaults | ✅ |
| 3 | `normalize_full_override_preserved` | All keys present → no changes | ✅ |
| 4 | `normalize_is_pure_function` | Same input → same output (idempotent) | ✅ |

**Assessment:** Covers all normalization paths. No gap.

**Missing edge cases:**
- `dispatch_policy` with unknown keys (should ignore unknown, not error)
- `normalize_dispatch_policy` called with `None` input

---

### AUTO_IGNORE (4/4 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `high_auto_medium_ignored` | high exists + medium policy=ignore → medium suppressed | ✅ |
| 2 | `high_auto_medium_auto` | high exists + medium policy=auto → medium goes to secondary | ✅ |
| 3 | `high_ignored` | high policy=ignore → no selected, fallback triggered | ✅ |
| 4 | `medium_only_auto` | no high + medium policy=auto → medium auto-dispatched | ✅ |

**Assessment:** Covers primary auto/ignore paths.

**Missing test cases:**
| Gap | Scenario | Risk |
|-----|---------|------|
| G-01 | `high: "ignore"` + multiple high teams → all ignored? | Low |
| G-02 | `medium.when_high_exists: "auto"` (counterintuitive but valid) | Low |
| G-03 | Empty `high_candidates` + `medium.when_no_high_exists: "ignore"` → fallback | Medium |

---

### ASK MODE (5/5 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `medium_only_ask_yes` | y/yes → all medium teams dispatched | ✅ |
| 2 | `medium_only_ask_no` | n/no → all medium teams suppressed | ✅ |
| 3 | `medium_only_ask_invalid_default_no` | invalid input → defaults to "none" | ✅ |
| 4 | `high_with_medium_ask_yes` | high auto + medium ask → yes: both dispatched | ✅ |
| 5 | `high_with_medium_ask_no` | high auto + medium ask → no: high still dispatched, medium suppressed | ✅ |

**Assessment:** All confirmation flows covered.

**Missing test cases:**
| Gap | Scenario | Risk |
|-----|---------|------|
| G-04 | Ask triggered + empty `medium_candidates` (should not happen — already guarded) | Low — known guard exists |
| G-05 | Ask prompt accepts uppercase `Y`/`N` | Low |
| G-06 | Ask fires twice in same routing (should be prevented by "at most once" rule) | Medium |

---

### DRY_RUN (5/5 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `dry_run_normal_high_auto` | dry-run with auto high → pending_decision written, no dispatch | ✅ |
| 2 | `dry_run_ask_returns_pending_decision` | dry-run with ask mode → pending_decision present | ✅ |
| 3 | `dry_run_no_prompt` | dry-run skips user prompt entirely | ✅ |
| 4 | `dry_run_and_normal_mode_same_pending_decision` | dry-run and normal produce identical pending_decision | ✅ |
| 5 | `normal_ask_has_pending_decision_not_ask_required` | Normal mode uses pending_decision (not legacy ask_required) | ✅ |

**Assessment:** Good coverage for dry-run behavior.

**Missing test cases:**
| Gap | Scenario | Risk |
|-----|---------|------|
| G-07 | `--debug --dry-run` combined flag produces both traces | Low |
| G-08 | dry-run + fallback (no teams) → pending_decision not set | Medium |
| G-09 | dry-run preserves existing task JSON (idempotent re-dry-run) | Low |

---

## v0.4 — Interactive Routing Contract + DAG Execution

### PHASE 1 — pending_decision + Resolve (14/14 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `ask_parks_with_pending_decision` | Ask mode → task parked with pending_decision | ✅ |
| 2 | `ask_no_fallback_triggered` | Ask triggered → fallback NOT called | ✅ |
| 3 | `resolve_confirm_all` | Resolve all → pending_decision.cleared, selected_teams populated | ✅ |
| 4 | `resolve_decline` | Resolve none → teams suppressed, declined flag set | ✅ |
| 5 | `resolve_idempotent_twice` | Resolve same task twice → second call is no-op | ✅ |
| 6 | `resolve_noop_on_non_awaiting` | Resolve on non-awaiting task → no-op | ✅ |
| 7 | `resolve_with_high_exists_confirm` | Resolve all with high still present → high + selected both dispatched | ✅ |
| 8 | `backward_compat_v03_ask_required` | Legacy `ask_required: true` → treated as equivalent pending_decision | ✅ |
| 9 | `step6_declined_empty_selected` | All medium declined + no high → user_declined_dispatch | ✅ |
| 10 | `step6_declined_with_high_selected` | All medium declined + high exists → high dispatched | ✅ |
| 11 | `resolve_all_continues_to_dispatch` | Resolve all → proceeds to Step C (not A/B) | ✅ |
| 12 | `resolve_none_sets_declined` | Resolve none → declined_after_ask = true | ✅ |
| 13 | `resolve_noop_when_not_awaiting` | Non-awaiting task → resolve returns no-op message | ✅ |
| 14 | `resolve_idempotent` | Idempotent resolve behavior | ✅ |

**Assessment:** Strong Phase 1 coverage. All state transitions tested.

**Missing test cases:**
| Gap | Scenario | Risk |
|-----|---------|------|
| G-10 | `awaiting_dispatch_decision` → task removed from disk before resolve | High — data loss scenario |
| G-11 | Resolve with `all` on already-resolved task (no pending_decision) → idempotent | Medium |
| G-12 | `declined_after_ask` transient flag cleared after Step 6 re-evaluation | Medium |

---

### GRAPH — Template Selection (4/4 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `template_data_first` | data team selected → data-first chain selected | ✅ |
| 2 | `template_research_branch` | research + no product → research branch selected | ✅ |
| 3 | `template_linear_pipeline` | backend or frontend → linear pipeline selected | ✅ |
| 4 | `template_flat_parallel` | no match → flat parallel fallback | ✅ |

**Missing test cases:**
| Gap | Scenario | Risk |
|-----|---------|------|
| G-13 | `data` + `backend` + `frontend` → data-first still wins (priority) | Medium |
| G-14 | `research` + `product` → research branch NOT selected (product present) | Medium |
| G-15 | `mobile` + `frontend` → linear pipeline | Low |

---

### GRAPH — Execution + Status (15/15 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `graph_linear_pipeline` | product→backend→frontend wave order | ✅ |
| 2 | `graph_research_branch` | research→[backend,frontend] fan-out | ✅ |
| 3 | `graph_data_first` | data→backend→frontend chain | ✅ |
| 4 | `graph_flat_parallel` | all teams parallel | ✅ |
| 5 | `ready_nodes_no_deps` | no depends_on → all nodes ready | ✅ |
| 6 | `ready_nodes_linear` | Wave N+1 ready only after N completes | ✅ |
| 7 | `ready_nodes_research_parallel` | research→[backend,frontend] parallel ready | ✅ |
| 8 | `graph_status_done` | all nodes completed → graph status = completed | ✅ |
| 9 | `graph_status_partial_failed` | any node partial_failed → graph status = partial_failed | ✅ |
| 10 | `e2e_linear_pipeline` | Full Step C: build graph → advance → completion | ✅ |
| 11 | `e2e_research_branch_parallel` | Full Step C: fan-out + parallel dispatch | ✅ |
| 12 | `blocked_node_excluded_from_ready` | artifacts_in missing → node blocked, excluded from ready | ✅ G-22 |
| 13 | `blocked_graph_becomes_blocked_status` | all non-terminal nodes blocked → graph status = blocked | ✅ G-20 |
| 14 | `unblock_and_redispatch` | node unblocked when artifacts appear → becomes ready | ✅ |
| 15 | `get_ready_nodes_on_partial_failed_graph` | partial_failed graph → get_ready_nodes returns [] | ✅ G-16 |

**Previously missing (now covered):**
- G-16: `get_ready_nodes` on terminal graph → empty ✅ (test #15)
- G-17: `advance_node` on done node → idempotent ✅ (P0-RT-02)
- G-18: Wave 2 fails → partial_failed ✅ (P0-E2E-02)

**Still missing:**
| Gap | Scenario | Risk |
|-----|---------|------|
| G-21 | Two nodes depend on same upstream → both unblocked when upstream completes | Low |

---

## v0.5 — Milestone Coordination

### MILESTONE UNIT (14/14 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `milestone_create` | Create with id → correct schema | ✅ |
| 2 | `milestone_create_auto_id` | Create without id → `ms_<8-char-uuid>` format | ✅ |
| 3 | `milestone_attach_task` | Attach task → added to tasks[] | ✅ |
| 4 | `milestone_attach_multiple_tasks` | Attach 3 tasks → all present | ✅ |
| 5 | `milestone_append_only_idempotent` | Attach same task twice → no duplicate | ✅ |
| 6 | `aggregate_all_completed` | All completed → milestone = completed | ✅ |
| 7 | `aggregate_any_in_progress` | Any in_progress → milestone = in_progress | ✅ |
| 8 | `aggregate_partial_failed` | Any partial_failed → milestone = partial_failed | ✅ |
| 9 | `aggregate_all_pending` | All pending → milestone = pending | ✅ |
| 10 | `aggregate_mixed_no_in_progress` | completed + pending (no in_progress) → in_progress | ✅ |
| 11 | `aggregate_empty` | No tasks → pending | ✅ |
| 12 | `get_milestone_ref` | Returns {milestone_id, title} only | ✅ |
| 13 | `aggregate_mixed_with_partial_failed` | partial_failed > in_progress > completed priority | ✅ |
| 14 | `attach_same_task_idempotent` | Attaching same task twice → idempotent | ✅ |

**Missing test cases:**
| Gap | Scenario | Risk |
|-----|---------|------|
| G-23 | `create_milestone(title=None)` → should error or have default | Medium |
| G-24 | `create_milestone("")` (empty title) → edge case | Low |
| G-25 | `attach_task_to_milestone(None, task_id)` → error handling | Medium |
| G-26 | Status aggregation with unknown status string (e.g. "unknown") | Low |

---

### MILESTONE E2E WIRING (2/2 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `e2e_milestone_create_and_attach` | milestone → task → attach → ref correct | ✅ |
| 2 | `e2e_milestone_second_task_append_only` | 2 tasks → append-only + aggregation | ✅ |

**Missing test cases:**
| Gap | Scenario | Risk |
|-----|---------|------|
| G-27 | `--milestone-status ms_xxx` where ms_xxx does not exist → graceful error | High |
| G-28 | `--milestone-status` on milestone with all tasks missing (fresh milestone) → all pending | Medium |
| G-29 | Routing fallback (no teams dispatched) → milestone stays with empty tasks[] | Medium |
| G-30 | Task created with milestone → task JSON has correct `milestone` ref field | Medium |
| G-31 | Milestone re-aggregation via `--milestone-status` → status updated + written | Medium |
| G-32 | Multiple `--milestone-status` calls → idempotent (no state drift) | Low |
| G-33 | Milestone task list overflow (100+ tasks) → performance | Low |

---

## v0.5 — Selective Routing (6/6 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `selective_single_team` | Pending: [product, frontend]; resolve selective [product] → product selected, frontend ignored | ✅ |
| 2 | `selective_multiple_teams` | Pending: [product, frontend]; resolve selective [both] → both selected | ✅ |
| 3 | `selective_empty_subset_declined` | Empty selective → same as 'none' → declined_after_ask=True | ✅ |
| 4 | `selective_invalid_team_ignored` | Team not in pending → silently ignored | ✅ |
| 5 | `selective_idempotent_twice` | Same selective payload twice → same result, no duplicates | ✅ |
| 6 | `selective_with_high_exists_goes_to_secondary` | High exists + selective medium → medium goes to secondary | ✅ |

**Assessment:** All core selective dispatch paths covered.

**Missing test cases:**
| Gap | Scenario | Risk |
|-----|---------|------|
| G-S1 | CLI parsing: `--resolve <id> selective backend, product` (extra spaces) | Low |
| G-S2 | Case sensitivity: `Backend` vs `backend` in team-id | Low |
| G-S3 | Selective + all teams NOT in pending (e.g., resolve selective data,research when pending is product,frontend) | Medium |

---

## Orchestrator CLI Contract (Not Tested ⚠️)

These are the orchestrator-level behaviors that the spec defines but no test suite exercises end-to-end:

| # | Gap | Scenario | Risk |
|---|-----|---------|------|
| G-34 | `--debug` trace format correctness | Output matches exact format spec | High |
| G-35 | `--debug --dry-run` combined | Both traces appear | Medium |
| G-36 | Step 8 output format for each scenario | high+secondary, medium-only, pending_decision, dry-run | High |
| G-37 | Step 7 routing_decision schema completeness | All required fields present | High |
| G-38 | FALLBACK step: clarifying question output | Exactly one question, no preamble | Medium |
| G-39 | Step A: single team dispatch flow | task JSON written + Agent invoked | High |
| G-40 | Step B: parallel dispatch | Multiple task JSONs + parallel Agent calls | High |
| G-41 | Step C: DAG dispatch loop termination | Graph completed → STOP, no re-dispatch | High |
| G-42 | FAILED: prefix handling | Team lead returns `FAILED:` → surfaced to user | High |
| G-43 | Version/schema consistency | `routing_schema_version: "v0.4"` in routing_decision | Low |

---

## Routing Cases (5/5 ✅)

| # | Test Case | Scenario | Status |
|---|----------|----------|--------|
| 1 | `backend_high_only` | Single high team → direct dispatch | ✅ |
| 2 | `high_with_secondary` | High + medium secondary | ✅ |
| 3 | `medium_only` | Medium team only (no high) | ✅ |
| 4 | `fallback_needs_clarification` | No candidates → needs_clarification | ✅ |
| 5 | `negative_keyword_suppression` | Negative keywords → filtered | ✅ |

**Missing test cases:**
| Gap | Scenario | Risk |
|-----|---------|------|
| G-44 | Tie-breaking: two teams same score → deterministic order | Medium |
| G-45 | `candidate_threshold = 0` → all candidates pass filter | Low |
| G-46 | Score exactly at threshold boundary (score=3, high=3) | Low |
| G-47 | All teams filtered (score < 1 for all) → fallback | Low |

---

## Gap Summary by Priority

### P0 — Must Have (No Coverage)

| ID | Gap | Feature |
|----|-----|---------|
| G-10 | Task JSON missing before resolve | Phase1 resolve |
| G-27 | Milestone not found → error message | Milestone CLI |
| G-34 | `--debug` trace format correctness | CLI contract |
| G-36 | Step 8 output per scenario | CLI contract |
| G-37 | Step 7 routing_decision schema | CLI contract |
| G-39 | Step A dispatch flow | Orchestrator |
| G-40 | Step B parallel dispatch | Orchestrator |
| G-41 | Step C termination | Orchestrator |
| G-42 | FAILED: prefix handling | Orchestrator |

### P1 — Should Have (Partial Coverage)

| ID | Gap | Feature |
|----|-----|---------|
| G-03 | Empty high + medium.ignore → fallback | Auto/ignore |
| G-06 | Ask fires twice prevention | Ask mode |
| G-08 | Dry-run + fallback | Dry-run |
| G-12 | declined_after_ask cleared after Step 6 | Phase1 |
| G-13 | data + backend + frontend → data-first wins | Graph template |
| G-14 | research + product → branch NOT selected | Graph template |
| G-16 | get_ready_nodes on terminal graph → empty | Graph execution |
| G-19 | advance_node on partial_failed → idempotent | Graph execution |
| G-20 | Ready nodes empty + non-terminal graph → blocked | Graph execution |
| G-22 | Missing artifact_in → node blocked | Graph execution |
| G-30 | Task JSON has correct milestone ref field | Milestone wiring |
| G-31 | --milestone-status re-aggregation + write | Milestone wiring |
| G-44 | Tie-breaking deterministic | Routing |

### P2 — Nice to Have (Low Risk)

| ID | Gap |
|----|-----|
| G-01 | high: ignore + multiple high teams |
| G-02 | medium.when_high_exists: auto |
| G-05 | Ask accepts uppercase Y/N |
| G-07 | --debug --dry-run combined |
| G-09 | Dry-run idempotent re-run |
| G-11 | Resolve all on already-resolved task |
| G-17 | advance_node on already-completed node |
| G-21 | Two nodes depend on same upstream |
| G-24 | Empty title milestone creation |
| G-25 | attach_task_to_milestone with None |
| G-26 | Unknown status string in aggregation |
| G-32 | Multiple --milestone-status calls idempotent |
| G-35 | Step 8 clarifying question format |
| G-38 | Selective resolve idempotent |
| G-45 | candidate_threshold = 0 |
| G-46 | Score at exact threshold boundary |
| G-47 | All teams filtered |

---

## Test Execution Commands

```bash
# All routing tests
python3 tests/routing/test_routing_cases.py
python3 tests/routing/test_dispatch_policy.py

# Quick smoke (last 3 groups only)
python3 -c "
import sys; sys.path.insert(0, 'tests/routing')
from test_dispatch_policy import main
main()
" 2>&1 | tail -5

# Count test cases by group
python3 tests/routing/test_dispatch_policy.py 2>&1 | grep "  ✓" | wc -l
# Expected: 78
```

---

## Recommendation

**Immediate (P0 gaps → before any release):**
1. ~~Add orchestrator E2E tests for Step A/B/C dispatch~~ ✅ (P0-E2E-01)
2. ~~Add graph partial failure test: wave N fails → partial_failed, loop stops~~ ✅ (P0-E2E-02, P0-E2E-03)
3. ~~Add graph blocked node handling~~ ✅ (P1-RT: blocked_node_excluded, blocked_graph_becomes_blocked, unblock_and_redispatch)
4. G-10: Resolve with missing task JSON → graceful error
5. G-27: milestone-status on nonexistent ID → graceful error
6. G-34: `--debug` trace format validation
7. G-36/G-37: Step 7/8 CLI contract (schema + output)
8. G-39/G-40/G-41/G-42: Step A/B/C orchestrator dispatch contract

**Next sprint (P1 gaps):**
- G-30: Task JSON has correct milestone ref field
- G-31: --milestone-status re-aggregation + write
- G-13/G-14: Graph template priority cases

**Backlog (P2 gaps):**
- All low-risk items
- Selective routing tests (after implementation)

**Do NOT ship without P0 coverage.** The P0 gaps represent real failure paths in production use.
