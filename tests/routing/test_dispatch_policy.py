#!/usr/bin/env python3
"""
Dispatch policy test suite — mirrors Step 5.5 of orchestrator.md.
Tests normalize_dispatch_policy (this file) and apply_dispatch_policy (added in later tasks).
"""

DEFAULTS = {
    "high": "auto",
    "medium": {
        "when_high_exists": "ignore",
        "when_no_high_exists": "auto",
    },
}


def normalize_dispatch_policy(policy: dict) -> dict:
    """Pure function: fills missing dispatch_policy keys with v0.2-equivalent defaults."""
    medium = dict(DEFAULTS["medium"])
    medium.update(policy.get("medium", {}))
    return {
        "high": policy.get("high", DEFAULTS["high"]),
        "medium": medium,
    }


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


# ---------------------------------------------------------------------------
# Evaluator stub
# ---------------------------------------------------------------------------

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

    if medium_action == "ask" and medium_candidates:
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

    YES_RESPONSES = ("y", "yes", "")
    NO_RESPONSES = ("n", "no", "")

    if response in YES_RESPONSES:
        user_response = "yes"
        for team in medium_candidates:
            if medium_context == "when_no_high_exists":
                selected.append(team)
            else:
                secondary.append(team)
    elif response == "default_no":
        user_response = response
    else:
        user_response = "no"

    if user_response in ("no", "default_no"):
        for team in medium_candidates:
            ignored.append(team)

    return {
        "triggered": True,
        "context": f"medium_{medium_context}",
        "teams": team_names,
        "user_response": user_response,
        "prompt_count": prompt_count,
    }


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


# ---------------------------------------------------------------------------
# Ask mode tests
# ---------------------------------------------------------------------------

def _test_medium_only_ask_yes():
    """medium.when_no_high_exists: ask → user says "y" → selected: all medium"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    mock_responses = iter(["y"])
    selected, secondary, ignored, ask_res = apply_dispatch_policy(
        [], [_team("product", 2), _team("frontend", 2)], policy, prompt_fn=lambda q: next(mock_responses)
    )
    assert [t["team"] for t in selected] == ["product", "frontend"]
    assert secondary == []
    assert ignored == []
    assert ask_res is not None
    assert ask_res["triggered"] is True
    assert ask_res["context"] == "medium_when_no_high_exists"
    assert ask_res["teams"] == ["product", "frontend"]
    assert ask_res["user_response"] == "yes"
    assert ask_res["prompt_count"] == 1


def _test_medium_only_ask_no():
    """medium.when_no_high_exists: ask → user says "n" → ignored: all medium"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    mock_responses = iter(["n"])
    selected, secondary, ignored, ask_res = apply_dispatch_policy(
        [], [_team("product", 2)], policy, prompt_fn=lambda q: next(mock_responses)
    )
    assert selected == []
    assert secondary == []
    assert [t["team"] for t in ignored] == ["product"]
    assert ask_res is not None
    assert ask_res["triggered"] is True
    assert ask_res["context"] == "medium_when_no_high_exists"
    assert ask_res["user_response"] == "no"


def _test_medium_only_ask_invalid_default_no():
    """medium.when_no_high_exists: ask → two invalid inputs → default_no"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    mock_responses = iter(["maybe", "what?"])
    selected, secondary, ignored, ask_res = apply_dispatch_policy(
        [], [_team("product", 2)], policy, prompt_fn=lambda q: next(mock_responses)
    )
    assert selected == []
    assert secondary == []
    assert [t["team"] for t in ignored] == ["product"]
    assert ask_res is not None
    assert ask_res["triggered"] is True
    assert ask_res["context"] == "medium_when_no_high_exists"
    assert ask_res["user_response"] == "default_no"
    assert ask_res["prompt_count"] == 2


def _test_high_with_medium_ask_yes():
    """high: auto + medium.when_high_exists: ask → user says "y" → selected: high; secondary: medium"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ask", "when_no_high_exists": "auto"}}
    mock_responses = iter(["y"])
    selected, secondary, ignored, ask_res = apply_dispatch_policy(
        [_team("backend", 4)], [_team("product", 2)], policy, prompt_fn=lambda q: next(mock_responses)
    )
    assert [t["team"] for t in selected] == ["backend"]
    assert [t["team"] for t in secondary] == ["product"]
    assert ignored == []
    assert ask_res is not None
    assert ask_res["triggered"] is True
    assert ask_res["context"] == "medium_when_high_exists"
    assert ask_res["teams"] == ["product"]
    assert ask_res["user_response"] == "yes"
    assert ask_res["prompt_count"] == 1


def _test_high_with_medium_ask_no():
    """high: auto + medium.when_high_exists: ask → user says "n" → selected: high; ignored: medium"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ask", "when_no_high_exists": "auto"}}
    mock_responses = iter(["n"])
    selected, secondary, ignored, ask_res = apply_dispatch_policy(
        [_team("backend", 4)], [_team("product", 2)], policy, prompt_fn=lambda q: next(mock_responses)
    )
    assert [t["team"] for t in selected] == ["backend"]
    assert secondary == []
    assert [t["team"] for t in ignored] == ["product"]
    assert ask_res is not None
    assert ask_res["triggered"] is True
    assert ask_res["context"] == "medium_when_high_exists"
    assert ask_res["user_response"] == "no"
    assert ask_res["prompt_count"] == 1


ASK_TESTS = [
    ("medium_only_ask_yes", _test_medium_only_ask_yes),
    ("medium_only_ask_no", _test_medium_only_ask_no),
    ("medium_only_ask_invalid_default_no", _test_medium_only_ask_invalid_default_no),
    ("high_with_medium_ask_yes", _test_high_with_medium_ask_yes),
    ("high_with_medium_ask_no", _test_high_with_medium_ask_no),
]


AUTO_IGNORE_TESTS = [
    ("high_auto_medium_ignored", _test_high_auto_medium_ignored),
    ("high_auto_medium_auto", _test_high_auto_medium_auto),
    ("high_ignored", _test_high_ignored),
    ("medium_only_auto", _test_medium_only_auto),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    all_tests = [
        ("normalize", NORMALIZE_TESTS),
        ("auto_ignore", AUTO_IGNORE_TESTS),
        ("ask", ASK_TESTS),
    ]

    total_passed = total_failed = 0

    for group_name, tests in all_tests:
        print(f"\n{group_name.upper()} tests:")
        for name, fn in tests:
            try:
                fn()
                print(f"  \u2713 {name}")
                total_passed += 1
            except AssertionError as e:
                print(f"  \u2717 {name}: {e}")
                total_failed += 1

    print(f"\nResults: {total_passed} passed, {total_failed} failed")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
