# dispatch_policy Config — Design Spec (v0.3)

## Goal

Give users prescriptive control over what happens per confidence band after routing classification. The dispatch outcome is no longer fully automatic — it is the result of `classification × policy × (optionally) user input`.

## Architecture

```
Step 5    Classify candidates → high_candidates[], medium_candidates[]
          (pure classification — no policy read here)
Step 5.5  Apply dispatch_policy
          → reads dispatch_policy from routing_policy
          → resolves each band's action (auto / ask / ignore)
          → handles ask mode interaction if triggered
          → produces: selected_teams[], secondary_teams[], ignored_teams[], ask_resolution?
Step 6    Fallback (if selected_teams is empty after Step 5.5)
Step 7    Write routing_decision (reflects post-policy final state)
```

**Key boundary:**
- Step 5 outputs classification (pre-policy state).
- Step 5.5 outputs enforcement result (post-policy state).
- Steps A/B (execution) consume only the post-5.5 output. They have no knowledge of why a team was skipped, what policy was applied, or whether ask was triggered.
- `secondary_teams` are never dispatched in Steps A/B. They are informational only.

`selected_teams` in `routing_decision` reflects the post-policy final dispatch set — not the raw confidence output.

## Schema

`dispatch_policy` lives inside `routing_policy` in `.claude/routing.json`:

```json
"routing_policy": {
  "candidate_threshold": 1,
  "confidence_thresholds": {
    "high": 3,
    "medium": 1
  },
  "dispatch_policy": {
    "high": "auto",
    "medium": {
      "when_high_exists": "ignore",
      "when_no_high_exists": "auto"
    }
  }
}
```

### Valid actions per band

| Band | Valid actions (v0.3) |
|------|---------------------|
| `high` | `auto` \| `ignore` |
| `medium.when_high_exists` | `auto` \| `ask` \| `ignore` |
| `medium.when_no_high_exists` | `auto` \| `ask` \| `ignore` |

`ask` is not a valid action for `high` in v0.3. Reserve for a future version.

`low` is not part of `dispatch_policy`. Teams below `candidate_threshold` are filtered in Step 3 and never reach Step 5.5.

### Defaults

If `dispatch_policy` is missing or incomplete, it must be normalized before Step 5.5 runs:

```json
{
  "high": "auto",
  "medium": {
    "when_high_exists": "ignore",
    "when_no_high_exists": "auto"
  }
}
```

These defaults reproduce exactly the v0.2 dispatch behavior. No behavior change occurs until the user explicitly sets a different action.

**Policy fallback contract:** Missing or incomplete `dispatch_policy` must be normalized to the v0.2-equivalent policy before Step 5.5 runs. The orchestrator applies this normalization in Step 1, after reading `routing_policy`.

**Normalization is a pure function:** same input config always produces the same normalized output. No side effects, no state.

## Step 5.5 — Policy Enforcement

### Preconditions

- Step 5 has produced `high_candidates[]` and `medium_candidates[]`.
- `dispatch_policy` has been normalized (Step 1).

### Algorithm

**Determine medium context:**
```
if high_candidates is non-empty → medium_context = "when_high_exists"
else                            → medium_context = "when_no_high_exists"
```

**Apply policy per band:**

```
HIGH candidates:
  action = dispatch_policy.high
  "auto"   → add to selected_teams
  "ignore" → add to ignored_teams

MEDIUM candidates:
  action = dispatch_policy.medium[medium_context]
  "auto":
    if medium_context = "when_high_exists" → add to secondary_teams
    if medium_context = "when_no_high_exists" → add to selected_teams
  "ignore" → add to ignored_teams
  "ask"    → trigger ask mode (see below)
```

### Ask Mode

Ask mode is triggered **at most once per routing invocation**. If multiple bands or candidates require `ask`, they are grouped into a single prompt.

Ask mode applies only to the band that triggered it (medium in v0.3). High teams and ignored teams are not affected by the ask decision.

**Output:**
```
Medium-confidence teams identified:
- <team> (score N)
- <team> (score N)
Dispatch these teams? [Y/n]
```

**Input contract:**
| Input | Action |
|-------|--------|
| `y` / `yes` / `<empty>` | Dispatch all prompted teams (same as `auto` for this context) |
| `n` / `no` | Add all to `ignored_teams`; record `user_response: "no"` |
| invalid | Re-prompt once: `"Please reply y or n."` |
| invalid (second time) | Treat as `no`; record `user_response: "default_no"` |

### Output fields

| Field | Description |
|-------|-------------|
| `selected_teams[]` | Teams that will be dispatched |
| `secondary_teams[]` | Medium teams surfaced for context but not dispatched (when_high_exists + auto) |
| `ignored_teams[]` | Teams suppressed by policy or user decision |
| `ask_resolution` | Present only when ask was triggered; absence means no user interaction occurred |

**Semantic boundary:**
- `secondary_teams` = medium teams surfaced for context (when_high_exists + auto action).
- `ignored_teams` = teams explicitly suppressed by policy (`ignore` action) or user decision (ask → no).
- These two sets are mutually exclusive.

### ask_resolution schema

```json
"ask_resolution": {
  "triggered": true,
  "context": "medium_when_no_high_exists",
  "teams": ["product", "frontend"],
  "user_response": "yes" | "no" | "default_no"
}
```

`teams` records exactly which teams were presented in the ask prompt — required for replay and audit.

`ask_resolution` is present only when ask is triggered. Absence of the field implies no user interaction occurred.

### Fallback handoff (Step 6)

Triggered when `selected_teams` is empty after Step 5.5. Task status:

| Condition | Status |
|-----------|--------|
| ask triggered AND `user_response` = `"no"` or `"default_no"` | `user_declined_dispatch` |
| No candidates selected AND no ask was triggered | `needs_clarification` |

### routing_decision update (Step 7)

`dispatch_policy` is included in `policy_snapshot`. New top-level fields alongside `filtered_teams`:

```json
"routing_decision": {
  "routing_schema_version": "v0.3",
  "policy_snapshot": {
    "candidate_threshold": 1,
    "confidence_thresholds": { "high": 3, "medium": 1 },
    "dispatch_policy": {
      "high": "auto",
      "medium": {
        "when_high_exists": "ignore",
        "when_no_high_exists": "auto"
      }
    }
  },
  "dispatch_strategy": "conditional",
  "top_signals": [],
  "selected_teams": [],
  "secondary_teams": [],
  "ignored_teams": [],
  "filtered_teams": [],
  "ask_resolution": { "triggered": true, "context": "...", "teams": ["..."], "user_response": "..." }
}
```

`ask_resolution` is omitted when ask was not triggered.

`selected_teams` reflects the post-policy final dispatch set.

## Testing

### Test file structure

```
tests/routing/
  test_routing_cases.py        # v0.2: scoring + classification regression (5 cases)
  test_dispatch_policy.py      # v0.3: Step 5.5 state machine (new file)
```

Separate files because routing tests are deterministic and dispatch tests are stateful (ask mode requires input simulation).

### Ask mode simulation

Implement `prompt_user(question) -> str` as an injectable function:

```python
def prompt_user(question: str) -> str:
    return input(question)
```

Tests inject a mock:

```python
def mock_prompt(responses):
    responses = iter(responses)
    return lambda q: next(responses)
```

### Test cases

| Case | Policy | Input | Expected |
|------|--------|-------|----------|
| `high_auto_medium_ignored` | `high: auto, medium.when_high_exists: ignore` | backend (high), product (medium) | selected: backend; ignored: product |
| `high_auto_medium_auto` | `high: auto, medium.when_high_exists: auto` | backend (high), product (medium) | selected: backend; secondary: product |
| `high_ignored` | `high: ignore` | backend (high) | selected: none; fallback: needs_clarification |
| `medium_only_auto` | `medium.when_no_high_exists: auto` | product (medium) | selected: product |
| `medium_only_ask_yes` | `medium.when_no_high_exists: ask` | product, frontend (medium) | ask triggered once; user: "y"; selected: product, frontend |
| `medium_only_ask_no` | `medium.when_no_high_exists: ask` | product (medium) | ask triggered; user: "n"; ignored: product; fallback: user_declined_dispatch |
| `medium_only_ask_invalid_default_no` | `medium.when_no_high_exists: ask` | product (medium) | two invalid inputs; default_no; fallback: user_declined_dispatch |
| `high_with_medium_ask_yes` | `high: auto, medium.when_high_exists: ask` | backend (high), product (medium) | ask triggered once (medium only); user: "y"; selected: backend; secondary: product |

**Additional assertions for all ask cases:**
- `ask_prompt_count == 1` (ask triggered at most once)
- `ask_resolution` present in routing_decision
- `ignored_teams` / `selected_teams` match post-policy expectations

**v0.2 regression cases** (must still pass with default dispatch_policy):
- `backend_high_only` → selected: backend
- `fallback_needs_clarification` → status: needs_clarification

## What does NOT change

- Steps 1–5 and Steps 6–8 are structurally unchanged. Step 5.5 is a pure insertion.
- `filtered_teams` semantics unchanged (pre-candidate-threshold exclusion).
- `--debug` output: `routing_decision` already contains all fields. Debug trace reads from it as before — no new rendering logic needed for dispatch_policy fields.
- `routing_schema_version` bumps to `"v0.3"`.

## Out of scope (v0.3)

- `high: ask` — reserved for future version.
- Selective team inclusion in ask mode (Option B interaction) — v0.3.x or v0.4.
- `--dry-run` execution logic — separate v0.3 item (P1 after dispatch_policy).
- Automated snapshot test for ask mode output format.
