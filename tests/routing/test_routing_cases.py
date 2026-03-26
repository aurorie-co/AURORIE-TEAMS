#!/usr/bin/env python3
"""
Routing test suite for aurorie-teams.

Matching rules (must stay in sync with shared/agents/orchestrator.md Step 2):
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
