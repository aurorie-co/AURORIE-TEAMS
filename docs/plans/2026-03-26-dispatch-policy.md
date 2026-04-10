# dispatch_policy Config Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `dispatch_policy` to `routing.json` and `aurorie-orchestrator.md` so users can control per-confidence-band dispatch behavior (auto/ask/ignore), with ask mode triggering a Y/n prompt before dispatching medium-confidence teams.

**Architecture:** Insert Step 5.5 (policy enforcement) between Step 5 (classification) and Step 6 (fallback). Step 5 is updated to output `high_candidates[]` and `medium_candidates[]` rather than `selected_teams` directly. Step 5.5 reads `dispatch_policy`, handles ask mode interaction, and produces `selected_teams`, `secondary_teams`, `ignored_teams`. A Python mirror of the algorithm in `tests/routing/test_dispatch_policy.py` verifies the logic deterministically. Existing tests must continue to pass.

**Tech Stack:** Markdown (orchestrator instructions), JSON (routing.json), Python 3 stdlib (test evaluator — no dependencies).

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `shared/routing.json` | Modify | Add `dispatch_policy` block inside `routing_policy` |
| `shared/agents/aurorie-orchestrator.md` | Modify | Step 1 normalization; Step 5 classification rename; insert Step 5.5; Step 6 fallback status; Step 7 routing_decision schema; Steps A/B secondary constraint |
| `tests/routing/test_dispatch_policy.py` | Create | Python evaluator + 10 test cases for Step 5.5 state machine |
| `tests/lint.test.sh` | Modify | Run dispatch policy test suite after existing routing tests |

---

### Task 1: Add dispatch_policy to routing.json

**Files:**
- Modify: `shared/routing.json`

- [ ] **Step 1: Read routing.json to find the insertion point**

  Read `shared/routing.json`. Locate `"routing_policy"`. It currently looks like:
  ```json
  "routing_policy": {
    "candidate_threshold": 1,
    "confidence_thresholds": {
      "high": 3,
      "medium": 1
    }
  }
  ```

- [ ] **Step 2: Add dispatch_policy inside routing_policy**

  Using the Edit tool, replace:
  ```json
  "routing_policy": {
    "candidate_threshold": 1,
    "confidence_thresholds": {
      "high": 3,
      "medium": 1
    }
  }
  ```

  With:
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

  These defaults reproduce v0.2 behavior exactly.

- [ ] **Step 3: Verify JSON is valid**

  Run:
  ```bash
  jq . shared/routing.json
  ```

  Expected: JSON pretty-prints without errors.

- [ ] **Step 4: Run existing routing tests to confirm nothing broke**

  Run:
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

- [ ] **Step 5: Commit**

  ```bash
  git add shared/routing.json
  git commit -m "feat(routing): add dispatch_policy defaults to routing_policy"
  ```

---

### Task 2: Create test file + normalize_dispatch_policy

**Files:**
- Create: `tests/routing/test_dispatch_policy.py`

- [ ] **Step 1: Write the failing test for normalize_dispatch_policy**

  Create `tests/routing/test_dispatch_policy.py` with:

  ```python
  #!/usr/bin/env python3
  """
  Dispatch policy test suite — mirrors Step 5.5 of aurorie-orchestrator.md.
  Tests normalize_dispatch_policy and apply_dispatch_policy.
  """

  DEFAULTS = {
      "high": "auto",
      "medium": {
          "when_high_exists": "ignore",
          "when_no_high_exists": "auto",
      },
  }


  def normalize_dispatch_policy(policy: dict) -> dict:
      raise NotImplementedError


  # ---------------------------------------------------------------------------
  # Normalization tests
  # ---------------------------------------------------------------------------

  def _test_normalize_missing():
      result = normalize_dispatch_policy({})
      assert result == DEFAULTS, f"Expected defaults, got {result}"


  def _test_normalize_partial_missing_medium():
      result = normalize_dispatch_policy({"high": "ignore"})
      assert result["high"] == "ignore"
      assert result["medium"] == DEFAULTS["medium"]


  def _test_normalize_full_override():
      policy = {
          "high": "ignore",
          "medium": {"when_high_exists": "ask", "when_no_high_exists": "ask"},
      }
      result = normalize_dispatch_policy(policy)
      assert result["high"] == "ignore"
      assert result["medium"]["when_high_exists"] == "ask"
      assert result["medium"]["when_no_high_exists"] == "ask"


  def _test_normalize_pure_function():
      p = {"high": "ignore"}
      r1 = normalize_dispatch_policy(p)
      r2 = normalize_dispatch_policy(p)
      assert r1 == r2


  NORMALIZE_TESTS = [
      ("normalize_missing_returns_defaults", _test_normalize_missing),
      ("normalize_partial_fills_medium_defaults", _test_normalize_partial_missing_medium),
      ("normalize_full_override_preserved", _test_normalize_full_override),
      ("normalize_is_pure_function", _test_normalize_pure_function),
  ]


  if __name__ == "__main__":
      pass  # runner added in later tasks
  ```

- [ ] **Step 2: Run test to verify it fails**

  Run:
  ```bash
  python3 -c "
  import sys; sys.path.insert(0, 'tests/routing')
  from test_dispatch_policy import NORMALIZE_TESTS
  for name, fn in NORMALIZE_TESTS:
      try: fn(); print(f'PASS {name}')
      except Exception as e: print(f'FAIL {name}: {e}')
  "
  ```

  Expected: all four print `FAIL ... NotImplementedError`.

- [ ] **Step 3: Implement normalize_dispatch_policy**

  In `tests/routing/test_dispatch_policy.py`, replace:
  ```python
  def normalize_dispatch_policy(policy: dict) -> dict:
      raise NotImplementedError
  ```

  With:
  ```python
  def normalize_dispatch_policy(policy: dict) -> dict:
      """Pure function: fills missing dispatch_policy keys with v0.2-equivalent defaults."""
      medium = dict(DEFAULTS["medium"])
      medium.update(policy.get("medium", {}))
      return {
          "high": policy.get("high", DEFAULTS["high"]),
          "medium": medium,
      }
  ```

- [ ] **Step 4: Run tests to verify they pass**

  Run the same command as Step 2. Expected: all four print `PASS`.

- [ ] **Step 5: Commit**

  ```bash
  git add tests/routing/test_dispatch_policy.py
  git commit -m "test(dispatch): add normalize_dispatch_policy with 4 tests"
  ```

---

### Task 3: Implement apply_dispatch_policy (auto/ignore cases)

**Files:**
- Modify: `tests/routing/test_dispatch_policy.py`

Each candidate is a dict with keys: `team`, `score`, `confidence`, `matched_positive`, `matched_negative`.

- [ ] **Step 1: Write failing tests for auto/ignore cases**

  Append to `tests/routing/test_dispatch_policy.py` (before the `if __name__` block):

  ```python
  # ---------------------------------------------------------------------------
  # Evaluator stub
  # ---------------------------------------------------------------------------

  def apply_dispatch_policy(high_candidates, medium_candidates, policy, prompt_fn=None):
      raise NotImplementedError


  # ---------------------------------------------------------------------------
  # Auto / ignore tests
  # ---------------------------------------------------------------------------

  def _team(name, score=2):
      return {"team": name, "score": score, "confidence": "high", "matched_positive": [], "matched_negative": []}


  def _test_high_auto_medium_ignored():
      """high: auto + medium.when_high_exists: ignore → selected: high only, ignored: medium"""
      policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "auto"}}
      selected, secondary, ignored, ask_res = apply_dispatch_policy(
          [_team("backend", 4)], [_team("product", 2)], policy
      )
      assert [t["team"] for t in selected] == ["backend"]
      assert secondary == []
      assert [t["team"] for t in ignored] == ["product"]
      assert ask_res is None


  def _test_high_auto_medium_auto():
      """high: auto + medium.when_high_exists: auto → selected: high, secondary: medium"""
      policy = {"high": "auto", "medium": {"when_high_exists": "auto", "when_no_high_exists": "auto"}}
      selected, secondary, ignored, ask_res = apply_dispatch_policy(
          [_team("backend", 4)], [_team("product", 2)], policy
      )
      assert [t["team"] for t in selected] == ["backend"]
      assert [t["team"] for t in secondary] == ["product"]
      assert ignored == []
      assert ask_res is None


  def _test_high_ignored():
      """high: ignore → selected: none (fallback)"""
      policy = {"high": "ignore", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "auto"}}
      selected, secondary, ignored, ask_res = apply_dispatch_policy(
          [_team("backend", 4)], [], policy
      )
      assert selected == []
      assert secondary == []
      assert [t["team"] for t in ignored] == ["backend"]
      assert ask_res is None


  def _test_medium_only_auto():
      """medium.when_no_high_exists: auto → selected: medium"""
      policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "auto"}}
      selected, secondary, ignored, ask_res = apply_dispatch_policy(
          [], [_team("product", 2)], policy
      )
      assert [t["team"] for t in selected] == ["product"]
      assert secondary == []
      assert ignored == []
      assert ask_res is None


  AUTO_IGNORE_TESTS = [
      ("high_auto_medium_ignored", _test_high_auto_medium_ignored),
      ("high_auto_medium_auto", _test_high_auto_medium_auto),
      ("high_ignored", _test_high_ignored),
      ("medium_only_auto", _test_medium_only_auto),
  ]
  ```

- [ ] **Step 2: Run to verify they fail**

  Run:
  ```bash
  python3 -c "
  import sys; sys.path.insert(0, 'tests/routing')
  from test_dispatch_policy import AUTO_IGNORE_TESTS
  for name, fn in AUTO_IGNORE_TESTS:
      try: fn(); print(f'PASS {name}')
      except Exception as e: print(f'FAIL {name}: {e}')
  "
  ```

  Expected: all four print `FAIL ... NotImplementedError`.

- [ ] **Step 3: Implement apply_dispatch_policy (no ask mode yet)**

  Replace:
  ```python
  def apply_dispatch_policy(high_candidates, medium_candidates, policy, prompt_fn=None):
      raise NotImplementedError
  ```

  With:
  ```python
  def apply_dispatch_policy(high_candidates, medium_candidates, policy, prompt_fn=None):
      """
      Applies dispatch_policy to candidates. Returns:
        (selected_teams, secondary_teams, ignored_teams, ask_resolution)
      ask_resolution is None when ask mode was not triggered.
      secondary_teams are never dispatched — informational only.
      """
      normalized = normalize_dispatch_policy(policy)
      selected = []
      secondary = []
      ignored = []
      ask_resolution = None

      # Apply high policy
      high_action = normalized["high"]
      for team in high_candidates:
          if high_action == "auto":
              selected.append(team)
          elif high_action == "ignore":
              ignored.append(team)

      # Determine medium context
      medium_context = "when_high_exists" if high_candidates else "when_no_high_exists"
      medium_action = normalized["medium"][medium_context]

      if medium_action == "ask":
          ask_resolution = _handle_ask(medium_candidates, medium_context, selected, secondary, ignored, prompt_fn)
      else:
          for team in medium_candidates:
              if medium_action == "auto":
                  if medium_context == "when_no_high_exists":
                      selected.append(team)
                  else:
                      secondary.append(team)
              elif medium_action == "ignore":
                  ignored.append(team)

      return selected, secondary, ignored, ask_resolution


  def _handle_ask(medium_candidates, medium_context, selected, secondary, ignored, prompt_fn):
      """Handles ask mode. Triggered at most once. Returns ask_resolution dict."""
      team_names = [t["team"] for t in medium_candidates]
      lines = ["Medium-confidence teams identified:"]
      for t in medium_candidates:
          lines.append(f"  - {t['team']} (score {t['score']})")
      lines.append("Dispatch these teams? [Y/n]")
      question = "\n".join(lines)

      prompt_count = 0
      fn = prompt_fn if prompt_fn else input

      response = fn(question).strip().lower()
      prompt_count += 1

      if response not in ("y", "yes", "n", "no", ""):
          response = fn("Please reply y or n.").strip().lower()
          prompt_count += 1
          if response not in ("y", "yes", "n", "no", ""):
              response = "default_no"

      if response in ("y", "yes", ""):
          user_response = "yes"
          for team in medium_candidates:
              if medium_context == "when_no_high_exists":
                  selected.append(team)
              else:
                  secondary.append(team)
      elif response == "default_no":
          user_response = "default_no"
          for team in medium_candidates:
              ignored.append(team)
      else:
          user_response = "no"
          for team in medium_candidates:
              ignored.append(team)

      return {
          "triggered": True,
          "context": f"medium_{medium_context}",
          "teams": team_names,
          "user_response": user_response,
          "prompt_count": prompt_count,
      }
  ```

- [ ] **Step 4: Run tests to verify they pass**

  Run the same command as Step 2. Expected: all four print `PASS`.

- [ ] **Step 5: Commit**

  ```bash
  git add tests/routing/test_dispatch_policy.py
  git commit -m "test(dispatch): add apply_dispatch_policy with auto/ignore cases"
  ```

---

### Task 4: Add ask mode tests

**Files:**
- Modify: `tests/routing/test_dispatch_policy.py`

- [ ] **Step 1: Append ask mode tests**

  Append to `tests/routing/test_dispatch_policy.py` (before the `if __name__` block):

  ```python
  # ---------------------------------------------------------------------------
  # Ask mode tests
  # ---------------------------------------------------------------------------

  def _mock_prompt(responses):
      """Returns a function that yields pre-set responses in order."""
      it = iter(responses)
      return lambda _question: next(it)


  def _test_medium_only_ask_yes():
      """ask + user 'y' → selected: all medium, ask triggered once"""
      policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
      candidates = [_team("product", 2), _team("frontend", 1)]
      selected, secondary, ignored, ask_res = apply_dispatch_policy(
          [], candidates, policy, prompt_fn=_mock_prompt(["y"])
      )
      assert [t["team"] for t in selected] == ["product", "frontend"]
      assert secondary == []
      assert ignored == []
      assert ask_res is not None
      assert ask_res["triggered"] is True
      assert ask_res["user_response"] == "yes"
      assert ask_res["teams"] == ["product", "frontend"]
      assert ask_res["prompt_count"] == 1  # triggered at most once


  def _test_medium_only_ask_no():
      """ask + user 'n' → ignored: all medium, fallback → user_declined_dispatch"""
      policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
      selected, secondary, ignored, ask_res = apply_dispatch_policy(
          [], [_team("product", 2)], policy, prompt_fn=_mock_prompt(["n"])
      )
      assert selected == []
      assert ignored[0]["team"] == "product"
      assert ask_res["user_response"] == "no"
      assert ask_res["prompt_count"] == 1


  def _test_medium_only_ask_invalid_then_default_no():
      """ask + invalid + invalid → default_no"""
      policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
      selected, secondary, ignored, ask_res = apply_dispatch_policy(
          [], [_team("product", 2)], policy, prompt_fn=_mock_prompt(["maybe", "idk"])
      )
      assert selected == []
      assert ignored[0]["team"] == "product"
      assert ask_res["user_response"] == "default_no"
      assert ask_res["prompt_count"] == 2  # re-prompted once


  def _test_high_with_medium_ask_yes():
      """high: auto + medium.when_high_exists: ask + user 'y' → selected: high, secondary: medium"""
      policy = {"high": "auto", "medium": {"when_high_exists": "ask", "when_no_high_exists": "auto"}}
      selected, secondary, ignored, ask_res = apply_dispatch_policy(
          [_team("backend", 4)], [_team("product", 2)], policy, prompt_fn=_mock_prompt(["y"])
      )
      # ask applies to medium only — high unaffected
      assert [t["team"] for t in selected] == ["backend"]
      assert [t["team"] for t in secondary] == ["product"]
      assert ignored == []
      assert ask_res["triggered"] is True
      assert ask_res["user_response"] == "yes"
      assert ask_res["prompt_count"] == 1  # ask triggered at most once


  ASK_TESTS = [
      ("medium_only_ask_yes", _test_medium_only_ask_yes),
      ("medium_only_ask_no", _test_medium_only_ask_no),
      ("medium_only_ask_invalid_then_default_no", _test_medium_only_ask_invalid_then_default_no),
      ("high_with_medium_ask_yes", _test_high_with_medium_ask_yes),
  ]
  ```

- [ ] **Step 2: Add main runner to test file**

  Replace:
  ```python
  if __name__ == "__main__":
      pass  # runner added in later tasks
  ```

  With:
  ```python
  if __name__ == "__main__":
      all_tests = NORMALIZE_TESTS + AUTO_IGNORE_TESTS + ASK_TESTS

      print(f"Running {len(all_tests)} dispatch policy test cases...\n")
      passed = 0
      failed = 0
      for name, fn in all_tests:
          try:
              fn()
              print(f"  ✓ {name}")
              passed += 1
          except Exception as e:
              print(f"  ✗ {name}: {e}")
              failed += 1

      print(f"\nResults: {passed} passed, {failed} failed")
      raise SystemExit(0 if failed == 0 else 1)
  ```

- [ ] **Step 3: Run all dispatch policy tests**

  Run:
  ```bash
  python3 tests/routing/test_dispatch_policy.py
  ```

  Expected:
  ```
  Running 12 dispatch policy test cases...

    ✓ normalize_missing_returns_defaults
    ✓ normalize_partial_fills_medium_defaults
    ✓ normalize_full_override_preserved
    ✓ normalize_is_pure_function
    ✓ high_auto_medium_ignored
    ✓ high_auto_medium_auto
    ✓ high_ignored
    ✓ medium_only_auto
    ✓ medium_only_ask_yes
    ✓ medium_only_ask_no
    ✓ medium_only_ask_invalid_then_default_no
    ✓ high_with_medium_ask_yes

  Results: 12 passed, 0 failed
  ```

- [ ] **Step 4: Commit**

  ```bash
  git add tests/routing/test_dispatch_policy.py
  git commit -m "test(dispatch): add ask mode tests and main runner (12 cases total)"
  ```

---

### Task 5: Update aurorie-orchestrator.md — Step 1 + Step 5

**Files:**
- Modify: `shared/agents/aurorie-orchestrator.md`

- [ ] **Step 1: Read aurorie-orchestrator.md and locate Step 1**

  Read `shared/agents/aurorie-orchestrator.md`. Find Step 1:

  ```
  ### Step 1 — Read policy

  Read `.claude/routing.json`. Extract `routing_policy`. If the field is missing or incomplete, apply these defaults:
  - `candidate_threshold = 1`
  - `confidence_thresholds.high = 3`
  - `confidence_thresholds.medium = 1`
  ```

- [ ] **Step 2: Update Step 1 to include dispatch_policy normalization**

  Replace:
  ```
  ### Step 1 — Read policy

  Read `.claude/routing.json`. Extract `routing_policy`. If the field is missing or incomplete, apply these defaults:
  - `candidate_threshold = 1`
  - `confidence_thresholds.high = 3`
  - `confidence_thresholds.medium = 1`
  ```

  With:
  ```
  ### Step 1 — Read policy

  Read `.claude/routing.json`. Extract `routing_policy`. If the field is missing or incomplete, apply these defaults:
  - `candidate_threshold = 1`
  - `confidence_thresholds.high = 3`
  - `confidence_thresholds.medium = 1`

  Normalize `dispatch_policy` (pure function — same input always produces same output):
  - If `dispatch_policy` is absent or incomplete, fill missing keys with:
    - `high = "auto"`
    - `medium.when_high_exists = "ignore"`
    - `medium.when_no_high_exists = "auto"`
  - These defaults reproduce v0.2 dispatch behavior exactly.
  ```

- [ ] **Step 3: Locate Step 5**

  In the same file, find:
  ```
  ### Step 5 — Conditional dispatch

  ```
  if any high candidates exist:
      selected_teams = all high candidates (sorted order)
      secondary_teams = all medium candidates
      dispatch_strategy = "conditional"

  elif any medium candidates exist:
      selected_teams = all medium candidates (sorted order)
      secondary_teams = []
      dispatch_strategy = "conditional"

  else:
      → FALLBACK (Step 6)
  ```

  When `selected_teams` contains multiple teams, dispatch them in parallel (Step B).
  When `selected_teams` contains one team, use single dispatch (Step A).
  ```

- [ ] **Step 4: Update Step 5 to output high_candidates and medium_candidates**

  Replace the full Step 5 block found in Step 3 with:

  ```
  ### Step 5 — Classify candidates

  ```
  if any high candidates exist:
      high_candidates = all high candidates (sorted order)
      medium_candidates = all medium candidates
      dispatch_strategy = "conditional"

  elif any medium candidates exist:
      high_candidates = []
      medium_candidates = all medium candidates (sorted order)
      dispatch_strategy = "conditional"

  else:
      → FALLBACK (Step 6): status = "needs_clarification"
  ```

  Step 5 produces classification only — it does not produce `selected_teams` or `secondary_teams`.
  Step 5.5 applies `dispatch_policy` and produces the final dispatch set.
  ```

- [ ] **Step 5: Verify step ordering**

  Run:
  ```bash
  grep -n "### Step" shared/agents/aurorie-orchestrator.md
  ```

  Expected output shows: Step 0, Step 1, Step 2, Step 3, Step 3.5, Step 4, Step 5, Step 6, Step 7, Step 7.5, Step 8, Step A, Step B. (Step 5.5 comes in Task 6.)

- [ ] **Step 6: Run tests to confirm nothing broke**

  Run:
  ```bash
  python3 tests/routing/test_routing_cases.py && python3 tests/routing/test_dispatch_policy.py
  ```

  Expected: both pass.

- [ ] **Step 7: Commit**

  ```bash
  git add shared/agents/aurorie-orchestrator.md
  git commit -m "feat(orchestrator): update Step 1 (dispatch_policy normalization) and Step 5 (classification rename)"
  ```

---

### Task 6: Insert Step 5.5 into aurorie-orchestrator.md

**Files:**
- Modify: `shared/agents/aurorie-orchestrator.md`

- [ ] **Step 1: Locate the insertion point**

  Find the exact closing text of (the updated) Step 5:
  ```
  Step 5 produces classification only — it does not produce `selected_teams` or `secondary_teams`.
  Step 5.5 applies `dispatch_policy` and produces the final dispatch set.

  ### Step 6 — Fallback
  ```

- [ ] **Step 2: Insert Step 5.5**

  Replace:
  ```
  Step 5 produces classification only — it does not produce `selected_teams` or `secondary_teams`.
  Step 5.5 applies `dispatch_policy` and produces the final dispatch set.

  ### Step 6 — Fallback
  ```

  With:
  ```
  Step 5 produces classification only — it does not produce `selected_teams` or `secondary_teams`.
  Step 5.5 applies `dispatch_policy` and produces the final dispatch set.

  ### Step 5.5 — Apply dispatch_policy

  **Precondition:** `dispatch_policy` has been normalized in Step 1. `high_candidates[]` and `medium_candidates[]` are available from Step 5.

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
      if medium_context = "when_no_high_exists" → add to selected_teams
      if medium_context = "when_high_exists"    → add to secondary_teams
    "ignore" → add to ignored_teams
    "ask"    → trigger ask mode (see below)
  ```

  **Ask mode** (triggered when action = "ask"):
  - Ask mode is triggered at most once per routing invocation. If multiple medium candidates require "ask", they are grouped into a single prompt.
  - Ask mode applies only to the medium band. High teams and ignored teams are not affected.

  Output:
  ```
  Medium-confidence teams identified:
  - <team> (score N)
  - <team> (score N)
  Dispatch these teams? [Y/n]
  ```

  Input contract:
  - `y` / `yes` / `<empty>` → dispatch all prompted teams (same as `auto` for this context); `user_response = "yes"`
  - `n` / `no` → add all to `ignored_teams`; `user_response = "no"`
  - invalid → re-prompt once: `"Please reply y or n."`
  - invalid (second time) → treat as `no`; `user_response = "default_no"`

  **Outputs of Step 5.5:**
  - `selected_teams[]` — teams that will be dispatched
  - `secondary_teams[]` — medium teams surfaced for context but not dispatched (when_high_exists + auto action only). Never dispatched in Steps A/B — informational only.
  - `ignored_teams[]` — teams suppressed by policy (ignore action) or user decision (ask → no/default_no)
  - `ask_resolution` — present only when ask was triggered; omit otherwise

  **ask_resolution schema:**
  ```json
  {
    "triggered": true,
    "context": "medium_when_no_high_exists",
    "teams": ["product", "frontend"],
    "user_response": "yes"
  }
  ```

  **Semantic boundary:**
  - `secondary_teams` and `ignored_teams` are mutually exclusive.
  - `secondary_teams` = surfaced for context, not dispatched.
  - `ignored_teams` = explicitly suppressed by policy or user decision.

  **Trigger Step 6 (Fallback) if `selected_teams` is empty after this step.**

  When `selected_teams` contains multiple teams, dispatch them in parallel (Step B).
  When `selected_teams` contains one team, use single dispatch (Step A).

  ### Step 6 — Fallback
  ```

- [ ] **Step 3: Verify step ordering**

  Run:
  ```bash
  grep -n "### Step" shared/agents/aurorie-orchestrator.md
  ```

  Expected: Step 0, Step 1, Step 2, Step 3, Step 3.5, Step 4, Step 5, **Step 5.5**, Step 6, Step 7, Step 7.5, Step 8, Step A, Step B.

- [ ] **Step 4: Run tests**

  Run:
  ```bash
  python3 tests/routing/test_routing_cases.py && python3 tests/routing/test_dispatch_policy.py
  ```

  Expected: both pass.

- [ ] **Step 5: Commit**

  ```bash
  git add shared/agents/aurorie-orchestrator.md
  git commit -m "feat(orchestrator): insert Step 5.5 — dispatch_policy enforcement"
  ```

---

### Task 7: Update Step 6, Step 7, Steps A/B

**Files:**
- Modify: `shared/agents/aurorie-orchestrator.md`

- [ ] **Step 1: Update Step 6 fallback status**

  Find:
  ```
  ### Step 6 — Fallback

  Triggered when Step 5 dispatch logic finds no selected teams (no high or medium candidates):
  - Do NOT dispatch any team
  - Do NOT generate any artifact
  - Generate one task-id, write task JSON with `status = "needs_clarification"` and the following `routing_decision`:
    ```json
    "routing_decision": {
      "routing_schema_version": "v0.2",
  ```

  Replace the Step 6 opening paragraph and JSON block:
  ```
  ### Step 6 — Fallback

  Triggered when Step 5 dispatch logic finds no selected teams (no high or medium candidates):
  - Do NOT dispatch any team
  - Do NOT generate any artifact
  - Generate one task-id, write task JSON with `status = "needs_clarification"` and the following `routing_decision`:
    ```json
    "routing_decision": {
      "routing_schema_version": "v0.2",
      "dispatch_strategy": "fallback",
      "selected_teams": [],
      "secondary_teams": [],
      "filtered_teams": [{ "team": "<team-id>", "score": 0, "confidence": "low", "matched_positive": [], "matched_negative": [] }]
    }
    ```
  - Output exactly one clarifying question — no preamble, no explanation, just the question (e.g. "Is this a backend API task or a UI feature?")
  - Re-evaluate routing when the user replies
  ```

  With:
  ```
  ### Step 6 — Fallback

  Triggered when no teams remain selected after Step 5.5 policy enforcement. Two cases:

  - **`user_declined_dispatch`**: ask mode was triggered AND `user_response` is `"no"` or `"default_no"`.
  - **`needs_clarification`**: `selected_teams` is empty AND no ask was triggered (e.g., all candidates filtered or ignored by policy).

  In both cases:
  - Do NOT dispatch any team
  - Do NOT generate any artifact
  - Generate one task-id, write task JSON with the appropriate `status` and the following `routing_decision`:
    ```json
    "routing_decision": {
      "routing_schema_version": "v0.3",
      "dispatch_strategy": "fallback",
      "selected_teams": [],
      "secondary_teams": [],
      "ignored_teams": [],
      "filtered_teams": [{ "team": "<team-id>", "score": 0, "confidence": "low", "matched_positive": [], "matched_negative": [] }]
    }
    ```
  - Output exactly one clarifying question — no preamble, no explanation, just the question (e.g. "Is this a backend API task or a UI feature?")
  - Re-evaluate routing when the user replies
  ```

- [ ] **Step 2: Update Step 7 routing_decision schema**

  Find the routing_decision JSON block in Step 7 (starts with `"routing_schema_version": "v0.2"`). Replace the entire JSON block and the line above it:

  ```
  ```json
  "routing_decision": {
    "routing_schema_version": "v0.2",
    "policy_snapshot": {
      "candidate_threshold": "<routing_policy.candidate_threshold>",
      "confidence_thresholds": {
        "high": "<routing_policy.confidence_thresholds.high>",
        "medium": "<routing_policy.confidence_thresholds.medium>"
      },
      "dispatch_policy": {
        "high": "selected",
        "medium_when_high_exists": "secondary",
        "medium_when_no_high_exists": "selected",
        "low": "filtered"
      }
    },
    "dispatch_strategy": "<dispatch_strategy>",
    "top_signals": ["<top matched keywords from selected_teams, max 5>"],
    "selected_teams": [
      {
        "team": "<team-id>",
        "score": 0,
        "confidence": "high",
        "matched_positive": [],
        "matched_negative": []
      }
    ],
    "secondary_teams": [
      {
        "team": "<team-id>",
        "score": 0,
        "confidence": "medium",
        "matched_positive": [],
        "matched_negative": []
      }
    ],
    "filtered_teams": [
      {
        "team": "<team-id>",
        "score": 0,
        "confidence": "low",
        "matched_positive": [],
        "matched_negative": []
      }
    ]
  }
  ```
  ```

  With:
  ```
  ```json
  "routing_decision": {
    "routing_schema_version": "v0.3",
    "policy_snapshot": {
      "candidate_threshold": "<routing_policy.candidate_threshold>",
      "confidence_thresholds": {
        "high": "<routing_policy.confidence_thresholds.high>",
        "medium": "<routing_policy.confidence_thresholds.medium>"
      },
      "dispatch_policy": {
        "high": "<routing_policy.dispatch_policy.high>",
        "medium": {
          "when_high_exists": "<routing_policy.dispatch_policy.medium.when_high_exists>",
          "when_no_high_exists": "<routing_policy.dispatch_policy.medium.when_no_high_exists>"
        }
      }
    },
    "dispatch_strategy": "<dispatch_strategy>",
    "top_signals": ["<top matched keywords from selected_teams, max 5>"],
    "selected_teams": [
      {
        "team": "<team-id>",
        "score": 0,
        "confidence": "high",
        "matched_positive": [],
        "matched_negative": []
      }
    ],
    "secondary_teams": [
      {
        "team": "<team-id>",
        "score": 0,
        "confidence": "medium",
        "matched_positive": [],
        "matched_negative": []
      }
    ],
    "ignored_teams": [
      {
        "team": "<team-id>",
        "score": 0,
        "confidence": "medium",
        "matched_positive": [],
        "matched_negative": []
      }
    ],
    "filtered_teams": [
      {
        "team": "<team-id>",
        "score": 0,
        "confidence": "low",
        "matched_positive": [],
        "matched_negative": []
      }
    ],
    "ask_resolution": {
      "triggered": true,
      "context": "<medium_when_high_exists|medium_when_no_high_exists>",
      "teams": ["<team-id>"],
      "user_response": "<yes|no|default_no>"
    }
  }
  ```

  Note: `ask_resolution` is omitted from the task JSON when ask was not triggered.
  ```

- [ ] **Step 3: Update Steps A/B — add secondary_teams constraint**

  Find the Step A section opening:
  ```
  ### Step A — Single Dispatch

  1. Generate task-id: `uuidgen | tr '[:upper:]' '[:lower:]'`
  ```

  Add a constraint note before the numbered list:
  ```
  ### Step A — Single Dispatch

  **Constraint:** Dispatch `selected_teams` only. `secondary_teams` are informational and must never be dispatched here.

  1. Generate task-id: `uuidgen | tr '[:upper:]' '[:lower:]'`
  ```

  Similarly, find:
  ```
  ### Step B — Parallel Dispatch

  1. Generate one task-id per selected team.
  ```

  Add:
  ```
  ### Step B — Parallel Dispatch

  **Constraint:** Dispatch `selected_teams` only. `secondary_teams` are informational and must never be dispatched here.

  1. Generate one task-id per selected team.
  ```

- [ ] **Step 4: Verify step ordering and grep for v0.2 schema version**

  Run:
  ```bash
  grep -n "routing_schema_version" shared/agents/aurorie-orchestrator.md
  ```

  Expected: all occurrences show `"v0.3"`, none show `"v0.2"`.

- [ ] **Step 5: Run tests**

  Run:
  ```bash
  python3 tests/routing/test_routing_cases.py && python3 tests/routing/test_dispatch_policy.py
  ```

  Expected: both pass.

- [ ] **Step 6: Commit**

  ```bash
  git add shared/agents/aurorie-orchestrator.md
  git commit -m "feat(orchestrator): update Step 6 fallback status, Step 7 schema v0.3, Steps A/B constraint"
  ```

---

### Task 8: CI integration

**Files:**
- Modify: `tests/lint.test.sh`

- [ ] **Step 1: Read the end of lint.test.sh**

  Read `tests/lint.test.sh`. Find the last 10 lines — the routing test invocation currently looks like:

  ```bash
  echo "=== Routing: run deterministic routing test suite ==="
  python3 "$(dirname "$0")/routing/test_routing_cases.py"
  ROUTING_EXIT=$?

  [[ $FAIL -eq 0 && $ROUTING_EXIT -eq 0 ]] && exit 0 || exit 1
  ```

- [ ] **Step 2: Add dispatch policy test runner**

  Replace:
  ```bash
  echo "=== Routing: run deterministic routing test suite ==="
  python3 "$(dirname "$0")/routing/test_routing_cases.py"
  ROUTING_EXIT=$?

  [[ $FAIL -eq 0 && $ROUTING_EXIT -eq 0 ]] && exit 0 || exit 1
  ```

  With:
  ```bash
  echo "=== Routing: run deterministic routing test suite ==="
  python3 "$(dirname "$0")/routing/test_routing_cases.py"
  ROUTING_EXIT=$?

  echo ""
  echo "=== Dispatch: run dispatch policy test suite ==="
  python3 "$(dirname "$0")/routing/test_dispatch_policy.py"
  DISPATCH_EXIT=$?

  [[ $FAIL -eq 0 && $ROUTING_EXIT -eq 0 && $DISPATCH_EXIT -eq 0 ]] && exit 0 || exit 1
  ```

- [ ] **Step 3: Run full lint suite**

  Run:
  ```bash
  bash tests/lint.test.sh 2>&1 | tail -15
  ```

  Expected output ends with something like:
  ```
  === Routing: run deterministic routing test suite ===
  Running 5 routing test cases...
  ...
  Results: 5 passed, 0 failed

  === Dispatch: run dispatch policy test suite ===
  Running 12 dispatch policy test cases...
  ...
  Results: 12 passed, 0 failed
  ```

  And exits 0.

- [ ] **Step 4: Run install test suite too**

  Run:
  ```bash
  bash tests/install.test.sh 2>&1 | tail -5
  ```

  Expected: exits 0.

- [ ] **Step 5: Commit**

  ```bash
  git add tests/lint.test.sh
  git commit -m "ci: add dispatch policy test suite to lint runner"
  ```

---

## Self-Review

**Spec coverage:**
- ✅ Schema: `dispatch_policy` inside `routing_policy`, valid actions per band — Task 1
- ✅ Normalization pure function — Task 2 + Task 5 (Step 1)
- ✅ Step 5 renames to high/medium candidates — Task 5 (Step 4)
- ✅ Step 5.5 full algorithm (auto/ignore/ask) — Task 6
- ✅ Ask mode: single prompt, all-or-none, invalid→re-prompt→default_no — Tasks 3+4+6
- ✅ ask_resolution: triggered, context, teams, user_response — Tasks 4+6
- ✅ secondary_teams never dispatched — Tasks 6+7 (Step 3)
- ✅ Fallback: user_declined_dispatch vs needs_clarification — Task 7 (Step 1)
- ✅ routing_decision: v0.3 schema, ignored_teams, ask_resolution, actual dispatch_policy in policy_snapshot — Task 7 (Step 2)
- ✅ CI integration — Task 8
- ✅ v0.2 regression: 5 existing routing cases must still pass — verified in Tasks 1, 5, 6, 7, 8

**Placeholder scan:** None found. All code is complete.

**Type consistency:**
- `high_candidates` / `medium_candidates` introduced in Task 5 (Step 5), consumed in Task 6 (Step 5.5) ✅
- `selected_teams` / `secondary_teams` / `ignored_teams` produced in Step 5.5, consumed by Step 6, Step 7, Steps A/B ✅
- `ask_resolution` dict keys consistent across Tasks 4, 6, 7: `triggered`, `context`, `teams`, `user_response` ✅
- `_team()` helper used in Tasks 3 and 4, defined once in Task 3 ✅
- `normalize_dispatch_policy()` defined in Task 2, called in Task 3's `apply_dispatch_policy()` ✅
