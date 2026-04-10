# Spec: Routing Test Suite (v0.2.x)

**Date:** 2026-03-26
**Scope:** Deterministic, data-driven test suite for the routing evaluator. Validates confidence bands, dispatch logic, fallback, and negative keyword suppression against `shared/routing.json`.
**Goal:** Replace manual validation with a repeatable CI gate.

---

## Goals

- Lock in the 5 validated routing cases as regression tests
- Assert selected teams (ordered), secondary teams (unordered set), fallback status
- Run with zero third-party dependencies: `python3 tests/routing/test_routing_cases.py`
- Integrate into existing CI alongside lint and install tests
- Stay non-brittle: only assert team names + confidence bands, not scores or signal lists

## Out of Scope

- End-to-end orchestrator invocation (no LLM calls)
- Full task JSON structure validation
- Pytest or any testing framework beyond stdlib

---

## File Structure

```
tests/
  routing/
    cases.json          # Fixture: all test cases
    test_routing_cases.py  # Evaluator + test runner
```

Existing `tests/lint.test.sh` and `tests/install.test.sh` are unchanged.

---

## cases.json Schema

Each case asserts only the fields that matter. Structures are uniform throughout.

```json
[
  {
    "name": "backend_high_only",
    "prompt": "...",
    "expected": {
      "selected": [
        { "team": "backend", "confidence": "high" }
      ],
      "secondary": [
        { "team": "product" }
      ],
      "fallback": false,
      "expected_filtered": []
    }
  }
]
```

**Field semantics:**

| Field | Type | Assertion mode | Notes |
|---|---|---|---|
| `selected` | `[{team, confidence}]` | **Ordered** — position matters | Sorted by score desc per routing spec |
| `secondary` | `[{team}]` | **Unordered** — set comparison | Confidence not asserted on secondary |
| `fallback` | bool | exact | `true` means no teams dispatched |
| `expected_status` | string (optional) | exact, if present | e.g. `"needs_clarification"` |
| `expected_filtered` | `[team]` (optional) | subset — every listed team must appear in filtered list | Validates negative suppression |

---

## The 5 Cases

### Case 1 — Backend high only
```json
{
  "name": "backend_high_only",
  "prompt": "Add a REST endpoint for user authentication with JWT",
  "expected": {
    "selected": [{ "team": "backend", "confidence": "high" }],
    "secondary": [],
    "fallback": false,
    "expected_filtered": []
  }
}
```

### Case 2 — High with secondary
```json
{
  "name": "high_with_secondary",
  "prompt": "Build a SaaS platform with user requirements and API endpoints",
  "expected": {
    "selected": [{ "team": "backend", "confidence": "high" }],
    "secondary": [{ "team": "product" }, { "team": "frontend" }],
    "fallback": false,
    "expected_filtered": []
  }
}
```

### Case 3 — Medium only
```json
{
  "name": "medium_only",
  "prompt": "Help me think about a feature for my product",
  "expected": {
    "selected": [{ "team": "product", "confidence": "medium" }],
    "secondary": [],
    "fallback": false,
    "expected_filtered": []
  }
}
```

### Case 4 — Fallback / needs clarification
```json
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
}
```

### Case 5 — Negative keyword suppression
```json
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
```

---

## Evaluator Logic

Implemented in `test_routing_cases.py`. Pure Python, no external deps.

### Matching rules (source of truth for test evaluator)

```
# Matching rules (must stay in sync with aurorie-orchestrator.md Step 2):
# - Case-insensitive
# - Token-based prefix match: keyword matches any word that starts with it
#   e.g. "auth" matches "authentication"; "api" does NOT match "capability"
# - Multi-word keywords: phrase match (substring of full request)
```

### Scoring

```python
net_score = len(pos_matches) - 2 * len(neg_matches)
```

### Pipeline (mirrors orchestrator Steps 1–5)

1. Read `shared/routing.json` — extract `routing_policy`
2. Score each team
3. Filter: `net_score < candidate_threshold` → `filtered`
4. Sort candidates: `net_score desc`, `pos_count desc`, `neg_count asc`
5. Band: `>= high_t` → high; `>= med_t` → medium
6. Dispatch: if high exists → `selected=high, secondary=medium`; elif medium → `selected=medium`; else fallback

### Assertions per case

- `selected` teams and confidence bands: exact ordered list
- `secondary` team names: unordered set (order ignored)
- `fallback`: bool exact
- `expected_status`: asserted as `"needs_clarification"` only when `fallback=true` and field is present
- `expected_filtered`: every listed team must appear in `filtered` result (subset check)

### Output format

```
Running 5 routing test cases...

  ✓ backend_high_only
  ✓ high_with_secondary
  ✓ medium_only
  ✓ fallback_needs_clarification
  ✓ negative_keyword_suppression

Results: 5 passed, 0 failed
```

On failure:
```
  ✗ medium_only
    selected: expected [product(medium)] got [product(medium), support(medium)]
```

Exit code 0 on all pass, 1 on any failure.

---

## CI Integration

Add to existing test runner (alongside lint and install tests):

```bash
python3 tests/routing/test_routing_cases.py
```

No new CI infrastructure required.
