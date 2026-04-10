# Routing Test Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, data-driven Python test suite that validates routing engine behavior against 5 regression cases and integrates into CI.

**Architecture:** Two new files — `tests/routing/cases.json` (fixture) and `tests/routing/test_routing_cases.py` (evaluator + runner). The evaluator reimplements the routing pipeline in ~80 lines of stdlib Python, reads `shared/routing.json`, and asserts selected/secondary/fallback/filtered per case. Existing bash tests are untouched.

**Tech Stack:** Python 3 stdlib only (json, re, sys, pathlib). No pytest, no third-party deps.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `tests/routing/cases.json` | Create | Test fixture: 5 cases with expected routing outcomes |
| `tests/routing/test_routing_cases.py` | Create | Routing evaluator + test runner |

---

## Task 1: Create test fixture

**Files:**
- Create: `tests/routing/cases.json`

- [ ] **Step 1: Create the directory**

  ```bash
  mkdir -p tests/routing
  ```

- [ ] **Step 2: Write cases.json**

  Create `tests/routing/cases.json` with exactly this content:

  ```json
  [
    {
      "name": "backend_high_only",
      "prompt": "Add a REST endpoint for user authentication with JWT",
      "expected": {
        "selected": [{ "team": "backend", "confidence": "high" }],
        "secondary": [],
        "fallback": false,
        "expected_filtered": []
      }
    },
    {
      "name": "high_with_secondary",
      "prompt": "Build a SaaS platform with user requirements and API endpoints",
      "expected": {
        "selected": [{ "team": "backend", "confidence": "high" }],
        "secondary": [{ "team": "product" }, { "team": "frontend" }],
        "fallback": false,
        "expected_filtered": []
      }
    },
    {
      "name": "medium_only",
      "prompt": "Help me think about a feature for my product",
      "expected": {
        "selected": [{ "team": "product", "confidence": "medium" }],
        "secondary": [],
        "fallback": false,
        "expected_filtered": []
      }
    },
    {
      "name": "fallback_needs_clarification",
      "prompt": "Help me with this thing",
      "expected": {
        "selected": [],
        "secondary": [],
        "fallback": true,
        "expected_status": "needs_clarification",
        "expected_filtered": []
      }
    },
    {
      "name": "negative_keyword_suppression",
      "prompt": "Write a blog post about our iOS app and its features",
      "expected": {
        "selected": [],
        "secondary": [],
        "fallback": true,
        "expected_filtered": ["market"]
      }
    }
  ]
  ```

- [ ] **Step 3: Validate JSON is well-formed**

  ```bash
  python3 -c "import json; json.load(open('tests/routing/cases.json')); print('valid')"
  ```
  Expected: `valid`

- [ ] **Step 4: Commit**

  ```bash
  git add tests/routing/cases.json
  git commit -m "test(routing): add 5-case routing fixture"
  ```

---

## Task 2: Create the evaluator and test runner

**Files:**
- Create: `tests/routing/test_routing_cases.py`

- [ ] **Step 1: Create the file**

  Create `tests/routing/test_routing_cases.py` with exactly this content:

  ```python
  #!/usr/bin/env python3
  """
  Routing test suite for aurorie-teams.

  Matching rules (must stay in sync with shared/agents/aurorie-orchestrator.md Step 2):
  - Case-insensitive
  - Token-based prefix match: keyword matches any word that starts with it
    e.g. "auth" matches "authentication"; "api" does NOT match "capability"
  - Multi-word keywords: phrase match (substring of full request string)
  """

  import json
  import re
  import sys
  from pathlib import Path

  ROOT = Path(__file__).parent.parent.parent


  # ── Evaluator ────────────────────────────────────────────────────────────────

  def _token_match(keyword: str, request: str) -> bool:
      kw = keyword.lower()
      if " " in kw:
          return kw in request.lower()
      tokens = re.findall(r"\w+", request.lower())
      return any(tok.startswith(kw) for tok in tokens)


  def evaluate_routing(prompt: str, config: dict) -> dict:
      """
      Run the routing pipeline against a prompt.

      Returns:
          {
              "selected":  [{"team": str, "confidence": "high"|"medium"}],
              "secondary": [{"team": str, "confidence": "medium"}],
              "filtered":  [{"team": str, "score": int, ...}],
              "fallback":  bool,
          }
      """
      policy = config.get("routing_policy", {})
      threshold = policy.get("candidate_threshold", 1)
      thresholds = policy.get("confidence_thresholds", {})
      high_t = thresholds.get("high", 3)
      med_t = thresholds.get("medium", 1)

      scored = []
      for rule in config["rules"]:
          pos = [kw for kw in rule["positive_keywords"] if _token_match(kw, prompt)]
          neg = [kw for kw in rule["negative_keywords"] if _token_match(kw, prompt)]
          net = len(pos) - 2 * len(neg)
          band = "high" if net >= high_t else ("medium" if net >= med_t else "low")
          scored.append({
              "team": rule["team"],
              "score": net,
              "confidence": band,
              "matched_positive": pos,
              "matched_negative": neg,
          })

      # Sort: score desc, positive count desc, negative count asc
      scored.sort(key=lambda r: (-r["score"], -len(r["matched_positive"]), len(r["matched_negative"])))

      filtered = [r for r in scored if r["score"] < threshold]
      candidates = [r for r in scored if r["score"] >= threshold]
      high = [r for r in candidates if r["confidence"] == "high"]
      medium = [r for r in candidates if r["confidence"] == "medium"]

      if high:
          return {"selected": high, "secondary": medium, "filtered": filtered, "fallback": False}
      if medium:
          return {"selected": medium, "secondary": [], "filtered": filtered, "fallback": False}
      return {"selected": [], "secondary": [], "filtered": filtered, "fallback": True}


  # ── Assertions ───────────────────────────────────────────────────────────────

  def _check_case(case: dict, config: dict) -> list[str]:
      result = evaluate_routing(case["prompt"], config)
      exp = case["expected"]
      failures = []

      # selected: exact ordered list of {team, confidence}
      exp_selected = exp.get("selected", [])
      act_selected = [{"team": r["team"], "confidence": r["confidence"]} for r in result["selected"]]
      if act_selected != exp_selected:
          failures.append(f"selected: expected {exp_selected} got {act_selected}")

      # secondary: unordered set of team names
      exp_secondary = {s["team"] for s in exp.get("secondary", [])}
      act_secondary = {r["team"] for r in result["secondary"]}
      if act_secondary != exp_secondary:
          failures.append(
              f"secondary: expected {sorted(exp_secondary)} got {sorted(act_secondary)}"
          )

      # fallback: exact bool
      exp_fallback = exp.get("fallback", False)
      if result["fallback"] != exp_fallback:
          failures.append(f"fallback: expected {exp_fallback} got {result['fallback']}")

      # expected_filtered: subset check — every listed team must be in filtered
      filtered_teams = {r["team"] for r in result["filtered"]}
      for team in exp.get("expected_filtered", []):
          if team not in filtered_teams:
              failures.append(
                  f"expected_filtered: '{team}' not in filtered set {sorted(filtered_teams)}"
              )

      return failures


  # ── Runner ───────────────────────────────────────────────────────────────────

  def main() -> None:
      config_path = ROOT / "shared" / "routing.json"
      cases_path = Path(__file__).parent / "cases.json"

      with open(config_path) as f:
          config = json.load(f)
      with open(cases_path) as f:
          cases = json.load(f)

      print(f"Running {len(cases)} routing test cases...\n")
      passed = failed = 0

      for case in cases:
          failures = _check_case(case, config)
          if failures:
              print(f"  \u2717 {case['name']}")
              for msg in failures:
                  print(f"    {msg}")
              failed += 1
          else:
              print(f"  \u2713 {case['name']}")
              passed += 1

      print(f"\nResults: {passed} passed, {failed} failed")
      sys.exit(0 if failed == 0 else 1)


  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 2: Run the tests — expect all 5 to pass**

  ```bash
  python3 tests/routing/test_routing_cases.py
  ```

  Expected output:
  ```
  Running 5 routing test cases...

    ✓ backend_high_only
    ✓ high_with_secondary
    ✓ medium_only
    ✓ fallback_needs_clarification
    ✓ negative_keyword_suppression

  Results: 5 passed, 0 failed
  ```

  If any case fails, the output will show the exact diff between expected and actual. Fix `cases.json` expected values if the evaluator behavior is correct but the fixture is wrong.

- [ ] **Step 3: Verify exit code**

  ```bash
  python3 tests/routing/test_routing_cases.py; echo "Exit: $?"
  ```

  Expected last line: `Exit: 0`

- [ ] **Step 4: Commit**

  ```bash
  git add tests/routing/test_routing_cases.py
  git commit -m "test(routing): add routing evaluator and 5-case test runner"
  ```

---

## Task 3: Integrate into CI test runner

**Files:**
- Read: `tests/lint.test.sh` (to understand existing test pattern)
- Modify: `tests/lint.test.sh` OR create a thin wrapper

The existing `tests/lint.test.sh` runs lint checks. The simplest CI integration is to call the routing tests from the same entrypoint that runs lint and install tests. Check how CI currently calls the tests, then add the routing test call.

- [ ] **Step 1: Check how tests are currently called**

  ```bash
  cat tests/lint.test.sh | head -5
  cat tests/install.test.sh | head -5
  ```

  Both are standalone scripts. CI likely calls them as:
  ```bash
  bash tests/lint.test.sh && bash tests/install.test.sh
  ```

- [ ] **Step 2: Verify routing tests run cleanly from repo root**

  ```bash
  cd /path/to/repo && python3 tests/routing/test_routing_cases.py
  ```

  The test uses `Path(__file__).parent.parent.parent` to find `shared/routing.json` regardless of working directory. Confirm this resolves correctly:

  ```bash
  python3 -c "
  from pathlib import Path
  root = Path('tests/routing/test_routing_cases.py').resolve().parent.parent.parent
  print(root)
  print((root / 'shared' / 'routing.json').exists())
  "
  ```

  Expected: prints repo root path and `True`.

- [ ] **Step 3: Add routing tests to existing CI call**

  Open `tests/lint.test.sh`. At the **end** of the file, after the final `=== Results ===` block, add:

  ```bash
  echo ""
  echo "=== Routing: run deterministic routing test suite ==="
  python3 "$(dirname "$0")/routing/test_routing_cases.py"
  ```

  This piggybacks on the existing lint test entry point so CI picks it up automatically.

- [ ] **Step 4: Run the full lint test to confirm routing tests are included**

  ```bash
  bash tests/lint.test.sh
  ```

  Expected: all existing lint checks pass, then at the end:
  ```
  === Routing: run deterministic routing test suite ===
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
  git add tests/lint.test.sh
  git commit -m "ci: add routing test suite to lint test runner"
  ```
