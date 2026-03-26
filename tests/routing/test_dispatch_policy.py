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

def apply_dispatch_policy(high_candidates, medium_candidates, policy, dry_run=False):
    """
    Applies dispatch_policy to candidates. Returns:
      (selected_teams, secondary_teams, ignored_teams, pending_decision_or_None)

    v0.4 semantics:
    - When ask is triggered: parks task with pending_decision, does NOT prompt.
      The CLI layer (or resolve interface) handles prompting separately.
    - dry_run only skips Steps A/B; it does NOT defer the ask prompt.
    - secondary_teams are never dispatched — informational only.
    """
    normalized = normalize_dispatch_policy(policy)
    selected = []
    secondary = []
    ignored = []
    pending_decision = None

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
        # v0.4: always park, never prompt here (CLI/resolve interface handles that)
        pending_decision = {
            "type": "dispatch_confirmation",
            "band": "medium",
            "context": f"medium_{medium_context}",
            "teams": medium_candidates,
            "options": ["all", "none"],
            "default": "none",
        }
    else:
        for team in medium_candidates:
            if medium_action == "auto":
                if medium_context == "when_no_high_exists":
                    selected.append(team)
                else:
                    secondary.append(team)
            elif medium_action == "ignore":
                ignored.append(team)

    return selected, secondary, ignored, pending_decision


def _render_cli_ask(pending_decision):
    """CLI renderer: formats pending_decision as a y/n prompt string."""
    lines = ["Medium-confidence teams identified:"]
    for t in pending_decision["teams"]:
        lines.append(f"  - {t['team']} (score {t['score']})")
    lines.append("Dispatch these teams? [Y/n]")
    return "\n".join(lines)


def _parse_cli_response(response, pending_decision):
    """
    Parses CLI response against pending_decision.options.
    Returns resolved decision dict: {selected: "all"|"none"|"selective", teams: [...]}.
    """
    response = response.strip().lower()
    if response in ("y", "yes", ""):
        return {"selected": "all"}
    elif response in ("n", "no"):
        return {"selected": "none"}
    else:
        # Invalid: re-prompt once, then default to "none"
        return {"selected": "none", "invalid": True}


def resolve_task(task, decision):
    """
    Applies a user decision to a parked task.

    Args:
        task: dict with keys routing_decision (containing pending_decision),
              selected_teams, ignored_teams
        decision: {"selected": "all"|"none"|"selective", "teams": [...]} from _parse_cli_response

    Returns:
        Updated task dict with:
        - pending_decision cleared
        - selected_teams / ignored_teams updated per decision
        - status set to "pending" (ready to dispatch) or "needs_clarification" (empty after decline)
    """
    pending = task.get("routing_decision", {}).get("pending_decision")
    if not pending:
        return task  # Idempotent: no-op if not parked

    selected = list(task.get("selected_teams", []))
    secondary = list(task.get("secondary_teams", []))
    ignored = list(task.get("ignored_teams", []))

    # Determine where confirmed teams go based on context
    when_high_exists = pending.get("context") == "medium_when_high_exists"

    if decision["selected"] == "all":
        for team in pending["teams"]:
            if when_high_exists:
                # When high teams exist, medium confirm → secondary (informational, not dispatched)
                if team not in secondary:
                    secondary.append(team)
            else:
                # No high teams → medium confirm → selected (dispatched)
                if team not in selected:
                    selected.append(team)
    elif decision["selected"] == "none":
        for team in pending["teams"]:
            if team not in ignored:
                ignored.append(team)
    elif decision["selected"] == "selective":
        confirmed = set(decision.get("teams", []))
        for team in pending["teams"]:
            if team["team"] in confirmed:
                if when_high_exists:
                    if team not in secondary:
                        secondary.append(team)
                else:
                    if team not in selected:
                        selected.append(team)
            else:
                if team not in ignored:
                    ignored.append(team)

    # Update routing_decision
    routing_decision = dict(task.get("routing_decision", {}))
    routing_decision.pop("pending_decision", None)
    routing_decision["selected_teams"] = selected
    routing_decision["secondary_teams"] = secondary
    routing_decision["ignored_teams"] = ignored

    # Mark declined_after_ask so Step 6 can distinguish user-declined from needs_clarification
    if decision["selected"] == "none":
        routing_decision["declined_after_ask"] = True

    # Status is determined by orchestrator Step 6 after resolve, not here.
    # Mark task as "pending" (ready for Step 6 to re-evaluate).
    result = dict(task)
    result["routing_decision"] = routing_decision
    result["status"] = "pending"
    return result


def _task_from_routing_decision(routing_decision):
    """Build a minimal task dict from a routing_decision (for testing resolve)."""
    return {
        "task_id": "test-task-001",
        "status": "awaiting_dispatch_decision",
        "routing_decision": dict(routing_decision),
        "selected_teams": list(routing_decision.get("selected_teams", [])),
        "secondary_teams": list(routing_decision.get("secondary_teams", [])),
        "ignored_teams": list(routing_decision.get("ignored_teams", [])),
    }


# ---------------------------------------------------------------------------
# Auto / ignore tests
# ---------------------------------------------------------------------------

def _team(name, score=2, confidence="medium"):
    return {"team": name, "score": score, "confidence": confidence, "matched_positive": [], "matched_negative": []}


def _test_high_auto_medium_ignored():
    """high: auto + medium.when_high_exists: ignore → selected: high only, ignored: medium"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "auto"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [_team("backend", 4)], [_team("product", 2)], policy
    )
    assert [t["team"] for t in selected] == ["backend"]
    assert secondary == []
    assert [t["team"] for t in ignored] == ["product"]
    assert pending is None


def _test_high_auto_medium_auto():
    """high: auto + medium.when_high_exists: auto → selected: high, secondary: medium"""
    policy = {"high": "auto", "medium": {"when_high_exists": "auto", "when_no_high_exists": "auto"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [_team("backend", 4)], [_team("product", 2)], policy
    )
    assert [t["team"] for t in selected] == ["backend"]
    assert [t["team"] for t in secondary] == ["product"]
    assert ignored == []
    assert pending is None


def _test_high_ignored():
    """high: ignore → selected: none (fallback)"""
    policy = {"high": "ignore", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "auto"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [_team("backend", 4)], [], policy
    )
    assert selected == []
    assert secondary == []
    assert [t["team"] for t in ignored] == ["backend"]
    assert pending is None


def _test_medium_only_auto():
    """medium.when_no_high_exists: auto → selected: medium"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "auto"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2)], policy
    )
    assert [t["team"] for t in selected] == ["product"]
    assert secondary == []
    assert ignored == []
    assert pending is None


# ---------------------------------------------------------------------------
# Ask mode tests (v0.4 — CLI layer: park + resolve)
# In v0.4, apply_dispatch_policy parks on ask; CLI handles prompt + resolve.
# ---------------------------------------------------------------------------

def _test_medium_only_ask_yes():
    """CLI resolve "y" → all medium teams selected"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2), _team("frontend", 2)], policy
    )
    # Step 1: parked with pending_decision
    assert pending is not None
    assert pending["type"] == "dispatch_confirmation"
    assert pending["context"] == "medium_when_no_high_exists"
    assert [t["team"] for t in pending["teams"]] == ["product", "frontend"]
    assert pending["options"] == ["all", "none"]
    assert selected == []  # parked, not yet dispatched

    # Step 2: CLI resolves → all selected
    task = _task_from_routing_decision({"selected_teams": selected, "secondary_teams": secondary, "ignored_teams": ignored, "pending_decision": pending})
    response = _parse_cli_response("y", pending)
    resolved = resolve_task(task, response)
    assert [t["team"] for t in resolved["routing_decision"]["selected_teams"]] == ["product", "frontend"]
    assert resolved["status"] == "pending"
    assert "pending_decision" not in resolved["routing_decision"]


def _test_medium_only_ask_no():
    """CLI resolve "n" → all medium teams ignored, pending cleared, declined_after_ask set"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2)], policy
    )
    task = _task_from_routing_decision({"selected_teams": selected, "secondary_teams": secondary, "ignored_teams": ignored, "pending_decision": pending})
    response = _parse_cli_response("n", pending)
    resolved = resolve_task(task, response)
    assert resolved["routing_decision"]["selected_teams"] == []
    assert [t["team"] for t in resolved["routing_decision"]["ignored_teams"]] == ["product"]
    assert "pending_decision" not in resolved["routing_decision"]
    assert resolved["routing_decision"].get("declined_after_ask") is True
    # resolve returns pending; Step 6 will re-evaluate and may set user_declined_dispatch


def _test_medium_only_ask_invalid_default_no():
    """CLI two invalid responses → treated as "none" (default_no)"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2)], policy
    )
    r1 = _parse_cli_response("maybe", pending)
    assert r1["selected"] == "none"
    assert r1.get("invalid") is True
    # After invalid, CLI re-prompts → second invalid defaults to "none"


def _test_high_with_medium_ask_yes():
    """high: auto + medium ask → confirm → selected: high + secondary: medium (when_high_exists)"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ask", "when_no_high_exists": "auto"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [_team("backend", 4)], [_team("product", 2)], policy
    )
    assert [t["team"] for t in selected] == ["backend"]  # high auto dispatched
    assert pending is not None
    assert pending["context"] == "medium_when_high_exists"

    task = _task_from_routing_decision({"selected_teams": selected, "secondary_teams": secondary, "ignored_teams": ignored, "pending_decision": pending})
    response = _parse_cli_response("y", pending)
    resolved = resolve_task(task, response)
    # When high exists, medium confirm → secondary
    assert [t["team"] for t in resolved["routing_decision"]["selected_teams"]] == ["backend"]
    assert [t["team"] for t in resolved["routing_decision"]["secondary_teams"]] == ["product"]
    assert resolved["status"] == "pending"


def _test_high_with_medium_ask_no():
    """high: auto + medium ask → decline → selected: high; ignored: medium; status = pending (can still dispatch)"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ask", "when_no_high_exists": "auto"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [_team("backend", 4)], [_team("product", 2)], policy
    )
    assert [t["team"] for t in selected] == ["backend"]
    assert pending is not None

    task = _task_from_routing_decision({"selected_teams": selected, "secondary_teams": secondary, "ignored_teams": ignored, "pending_decision": pending})
    response = _parse_cli_response("n", pending)
    resolved = resolve_task(task, response)
    assert [t["team"] for t in resolved["routing_decision"]["selected_teams"]] == ["backend"]
    assert [t["team"] for t in resolved["routing_decision"]["ignored_teams"]] == ["product"]
    # High is still selected → dispatchable → status = pending (NOT needs_clarification)
    assert resolved["status"] == "pending"


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
# Dry-run tests
# ---------------------------------------------------------------------------

def _test_dry_run_normal_high_auto():
    """dry_run=True + normal auto/ignore → selected_teams generated, pending is None"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "auto"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [_team("backend", 4)], [_team("product", 2)], policy, dry_run=True
    )
    assert [t["team"] for t in selected] == ["backend"]
    assert [t["team"] for t in ignored] == ["product"]
    assert pending is None


def _test_dry_run_ask_returns_pending_decision():
    """dry_run=True + ask policy → returns pending_decision (parked, same as normal mode)"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2)], policy, dry_run=True
    )
    assert selected == []
    assert secondary == []
    assert ignored == []
    assert pending is not None
    assert pending["type"] == "dispatch_confirmation"
    assert pending["context"] == "medium_when_no_high_exists"
    assert [t["team"] for t in pending["teams"]] == ["product"]
    assert "options" in pending
    assert "default" in pending


def _test_dry_run_no_prompt():
    """apply_dispatch_policy never prompts in v0.4 (CLI handles prompting separately)"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    # In v0.4, apply_dispatch_policy never calls prompt_fn — it parks immediately
    # This is tested by verifying pending_decision is returned (not ask_resolution)
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2)], policy, dry_run=True
    )
    assert pending is not None
    assert "type" in pending
    assert pending["type"] == "dispatch_confirmation"


def _test_dry_run_and_normal_mode_same_pending_decision():
    """dry_run=True and dry_run=False both return the same pending_decision"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    _, _, _, pending_dry = apply_dispatch_policy([], [_team("product", 2)], policy, dry_run=True)
    _, _, _, pending_norm = apply_dispatch_policy([], [_team("product", 2)], policy, dry_run=False)
    assert pending_dry == pending_norm, "dry_run does not change ask behavior in v0.4"


def _test_normal_ask_has_pending_decision_not_ask_required():
    """Normal mode (dry_run=False): pending_decision returned, no prompt called"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2)], policy, dry_run=False
    )
    assert pending is not None
    assert pending["type"] == "dispatch_confirmation"
    assert pending["context"] == "medium_when_no_high_exists"


DRYRUN_TESTS = [
    ("dry_run_normal_high_auto", _test_dry_run_normal_high_auto),
    ("dry_run_ask_returns_pending_decision", _test_dry_run_ask_returns_pending_decision),
    ("dry_run_no_prompt", _test_dry_run_no_prompt),
    ("dry_run_and_normal_mode_same_pending_decision", _test_dry_run_and_normal_mode_same_pending_decision),
    ("normal_ask_has_pending_decision_not_ask_required", _test_normal_ask_has_pending_decision_not_ask_required),
]


# ---------------------------------------------------------------------------
# Phase 1 — Interactive Routing Contract (pending_decision + resolve)
# ---------------------------------------------------------------------------

def _test_ask_parks_with_pending_decision():
    """ask triggers → pending_decision set, task parked, selected_teams unchanged"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2), _team("frontend", 2)], policy
    )
    # v0.4: parks, does not dispatch
    assert selected == []
    assert secondary == []
    assert ignored == []
    # pending_decision is set
    assert pending is not None
    assert pending["type"] == "dispatch_confirmation"
    assert pending["band"] == "medium"
    assert pending["context"] == "medium_when_no_high_exists"
    assert [t["team"] for t in pending["teams"]] == ["product", "frontend"]
    assert pending["options"] == ["all", "none"]
    assert pending["default"] == "none"


def _test_ask_no_fallback_triggered():
    """ask parks → fallback (Step 6) is NOT triggered"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2)], policy
    )
    # selected_teams is empty BUT no fallback — task is parked, not failed
    assert selected == []
    assert pending is not None
    # No ask_resolution field exists in v0.4


def _test_resolve_confirm_all():
    """resolve confirm → all pending teams added to selected_teams, pending cleared"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2), _team("frontend", 2)], policy
    )
    task = _task_from_routing_decision({
        "selected_teams": selected,
        "secondary_teams": secondary,
        "ignored_teams": ignored,
        "pending_decision": pending,
    })
    resolved = resolve_task(task, {"selected": "all"})
    assert [t["team"] for t in resolved["routing_decision"]["selected_teams"]] == ["product", "frontend"]
    assert "pending_decision" not in resolved["routing_decision"]
    assert resolved["status"] == "pending"


def _test_resolve_decline():
    """resolve decline → pending cleared, declined_after_ask flag set, status = pending (Step 6 decides final)"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2)], policy
    )
    task = _task_from_routing_decision({
        "selected_teams": selected,
        "secondary_teams": secondary,
        "ignored_teams": ignored,
        "pending_decision": pending,
    })
    resolved = resolve_task(task, {"selected": "none"})
    assert resolved["routing_decision"]["selected_teams"] == []
    assert [t["team"] for t in resolved["routing_decision"]["ignored_teams"]] == ["product"]
    assert "pending_decision" not in resolved["routing_decision"]
    assert resolved["routing_decision"].get("declined_after_ask") is True
    # resolve returns pending; Step 6 re-evaluates and may set needs_clarification if selected is empty


def _test_resolve_idempotent_twice():
    """resolving twice with same payload is idempotent — no duplicate teams"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2)], policy
    )
    task = _task_from_routing_decision({
        "selected_teams": selected,
        "secondary_teams": secondary,
        "ignored_teams": ignored,
        "pending_decision": pending,
    })
    r1 = resolve_task(task, {"selected": "all"})
    r2 = resolve_task(r1, {"selected": "all"})
    assert r2["routing_decision"]["selected_teams"] == r1["routing_decision"]["selected_teams"]
    assert len(r2["routing_decision"]["selected_teams"]) == 1  # no duplicates


def _test_resolve_noop_on_non_awaiting():
    """resolve on task without pending_decision → no-op (idempotent)"""
    task = {
        "task_id": "test-002",
        "status": "pending",
        "routing_decision": {
            "selected_teams": [_team("backend", 4)],
            "secondary_teams": [],
            "ignored_teams": [],
        },
        "selected_teams": [_team("backend", 4)],
        "secondary_teams": [],
        "ignored_teams": [],
    }
    result = resolve_task(task, {"selected": "all"})
    # unchanged
    assert result["status"] == "pending"
    assert [t["team"] for t in result["routing_decision"]["selected_teams"]] == ["backend"]


def _test_resolve_with_high_exists_confirm():
    """when high exists + medium ask confirm → medium goes to secondary (not selected)"""
    policy = {"high": "auto", "medium": {"when_high_exists": "ask", "when_no_high_exists": "auto"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [_team("backend", 4)], [_team("product", 2)], policy
    )
    assert [t["team"] for t in selected] == ["backend"]  # high already selected
    assert pending is not None

    task = _task_from_routing_decision({
        "selected_teams": selected,
        "secondary_teams": secondary,
        "ignored_teams": ignored,
        "pending_decision": pending,
    })
    resolved = resolve_task(task, {"selected": "all"})
    # When high exists, medium confirm → secondary
    assert [t["team"] for t in resolved["routing_decision"]["selected_teams"]] == ["backend"]
    assert [t["team"] for t in resolved["routing_decision"]["secondary_teams"]] == ["product"]
    assert resolved["status"] == "pending"


def _test_backward_compat_v03_ask_required():
    """v0.3 task with ask_required: true reads as equivalent pending_decision"""
    # Simulate v0.3 routing_decision with ask_required
    v03_routing_decision = {
        "routing_schema_version": "v0.3",
        "selected_teams": [],
        "secondary_teams": [],
        "ignored_teams": [],
        "ask_required": True,
    }
    # The equivalent pending_decision (for read-compatibility)
    equivalent_pending = {
        "type": "dispatch_confirmation",
        "band": "medium",
        "context": "medium_when_no_high_exists",
        "teams": [_team("product", 2)],
        "options": ["all", "none"],
        "default": "none",
    }
    task = _task_from_routing_decision({
        "selected_teams": [],
        "secondary_teams": [],
        "ignored_teams": [],
        "pending_decision": equivalent_pending,
    })
    resolved = resolve_task(task, {"selected": "all"})
    assert [t["team"] for t in resolved["routing_decision"]["selected_teams"]] == ["product"]
    assert resolved["status"] == "pending"


def _test_step6_re_evaluation_declined_empty_selected():
    """Step 6 behavior: declined_after_ask + empty selected_teams → needs_clarification"""
    # Simulate Step 6 re-evaluation after resolve declined (no high teams)
    task = {
        "task_id": "test-003",
        "status": "pending",  # returned by resolve_task
        "routing_decision": {
            "selected_teams": [],
            "secondary_teams": [],
            "ignored_teams": [_team("product", 2)],
            "declined_after_ask": True,
        },
    }
    # Step 6: selected_teams is empty AND declined_after_ask is True
    # → user_declined_dispatch (not needs_clarification)
    if not task["routing_decision"]["selected_teams"] and task["routing_decision"].get("declined_after_ask"):
        task["status"] = "user_declined_dispatch"
    else:
        task["status"] = "needs_clarification"
    assert task["status"] == "user_declined_dispatch"


def _test_step6_re_evaluation_declined_with_high_selected():
    """Step 6 behavior: declined_after_ask + non-empty selected_teams → pending (can dispatch)"""
    # Even with declined_after_ask, if selected_teams is not empty, dispatch can continue
    task = {
        "task_id": "test-004",
        "status": "pending",
        "routing_decision": {
            "selected_teams": [_team("backend", 4)],
            "secondary_teams": [],
            "ignored_teams": [_team("product", 2)],
            "declined_after_ask": True,
        },
    }
    if not task["routing_decision"]["selected_teams"] and task["routing_decision"].get("declined_after_ask"):
        task["status"] = "user_declined_dispatch"
    else:
        task["status"] = "pending"
    assert task["status"] == "pending"


# ---------------------------------------------------------------------------
# Phase 2: DAG Execution — graph functions
# ---------------------------------------------------------------------------

# Artifact path templates (per team, relative to workspace root)
ARTIFACT_OUT = {
    "product":  "artifacts/product/{task_id}/prd.md",
    "backend":  "artifacts/backend/{task_id}/backend-implementation.md",
    "frontend": "artifacts/frontend/{task_id}/frontend-implementation.md",
    "mobile":   "artifacts/mobile/{task_id}/mobile-implementation.md",
    "data":     "artifacts/data/{task_id}/analysis.md",
    "research": "artifacts/research/{task_id}/research-report.md",
    "infra":    "artifacts/infra/{task_id}/infra-spec.md",
    "design":   "artifacts/design/{task_id}/design-spec.md",
    "market":   "artifacts/market/{task_id}/market-analysis.md",
    "support":  "artifacts/support/{task_id}/support-playbook.md",
}


def select_graph_template(selected_teams):
    """
    Selects execution graph template using strict priority.
    Pure function.

    Priority (first match wins):
    1. 'data' in selected_teams                  → data-first
    2. 'research' in selected and 'product' not  → research-branch
    3. 'backend' in selected or 'frontend' in    → linear-pipeline
    4. fallback                                   → flat-parallel

    Args:
        selected_teams: list of team dicts with 'team' key

    Returns:
        str: one of 'data-first', 'research-branch', 'linear-pipeline', 'flat-parallel'
    """
    team_ids = {t["team"] for t in selected_teams}

    if "data" in team_ids:
        return "data-first"
    if "research" in team_ids and "product" not in team_ids:
        return "research-branch"
    if "backend" in team_ids or "frontend" in team_ids:
        return "linear-pipeline"
    return "flat-parallel"


def build_execution_graph(task_id, selected_teams):
    """
    Builds execution_graph for selected_teams using the selected template.
    Pure function — no side effects.

    Args:
        task_id: str UUID for this task
        selected_teams: list of team dicts with 'team', 'score', 'confidence'

    Returns:
        dict with keys: nodes[], edges[], status

    Templates:
    - data-first:   data → research → product → backend → frontend
    - research-branch: research → [backend, frontend] (parallel)
    - linear-pipeline: product → backend → frontend
    - flat-parallel: all selected teams in parallel (no edges)
    """
    template = select_graph_template(selected_teams)
    team_ids = [t["team"] for t in selected_teams]
    nodes = []
    edges = []

    def make_node(team):
        return {
            "node_id": f"{team}-1",
            "team": team,
            "depends_on": [],
            "status": "pending",
            "artifacts_in": [],
            "artifacts_out": [ARTIFACT_OUT.get(team, "").format(task_id=task_id)],
        }

    if template == "data-first":
        # data → research → product → backend → frontend
        chain = ["data", "research", "product", "backend", "frontend"]
        present = [t for t in chain if t in team_ids]
        nodes = [{"node_id": f"{t}-1", "team": t, "depends_on": [], "status": "pending",
                  "artifacts_in": [], "artifacts_out": [ARTIFACT_OUT[t].format(task_id=task_id)]} for t in present]
        for i, node in enumerate(nodes):
            if i > 0:
                prev = nodes[i - 1]
                node["depends_on"] = [prev["node_id"]]
                edges.append([prev["node_id"], node["node_id"]])

    elif template == "research-branch":
        # research → [backend, frontend] (parallel after research)
        order = ["research", "backend", "frontend"]
        present = [t for t in order if t in team_ids]
        research_node = None
        nodes = []
        for t in present:
            node = {
                "node_id": f"{t}-1",
                "team": t,
                "depends_on": [],
                "status": "pending",
                "artifacts_in": [],
                "artifacts_out": [ARTIFACT_OUT[t].format(task_id=task_id)],
            }
            if t == "research":
                research_node = node
            elif t in ("backend", "frontend"):
                if research_node:
                    node["depends_on"] = [research_node["node_id"]]
                    edges.append([research_node["node_id"], node["node_id"]])
            nodes.append(node)

    elif template == "linear-pipeline":
        # product → backend → frontend
        chain = ["product", "backend", "frontend"]
        present = [t for t in chain if t in team_ids]
        nodes = [{"node_id": f"{t}-1", "team": t, "depends_on": [], "status": "pending",
                  "artifacts_in": [], "artifacts_out": [ARTIFACT_OUT[t].format(task_id=task_id)]} for t in present]
        for i, node in enumerate(nodes):
            if i > 0:
                prev = nodes[i - 1]
                node["depends_on"] = [prev["node_id"]]
                edges.append([prev["node_id"], node["node_id"]])

    else:  # flat-parallel
        # All selected teams as independent parallel nodes
        for t in team_ids:
            nodes.append({
                "node_id": f"{t}-1",
                "team": t,
                "depends_on": [],
                "status": "pending",
                "artifacts_in": [],
                "artifacts_out": [ARTIFACT_OUT.get(t, "").format(task_id=task_id)],
            })

    # Populate artifacts_in for each node based on depends_on
    node_map = {n["node_id"]: n for n in nodes}
    for node in nodes:
        for dep_id in node.get("depends_on", []):
            dep_node = node_map.get(dep_id)
            if dep_node:
                node["artifacts_in"].extend(dep_node["artifacts_out"])

    return {"nodes": nodes, "edges": edges, "status": "pending"}


def get_ready_nodes(graph):
    """
    Returns list of node_ids that are ready to dispatch.
    A node is ready when:
    - status == 'pending'
    - all depends_on nodes have status == 'done'
    """
    node_map = {n["node_id"]: n for n in graph["nodes"]}
    ready = []
    for node in graph["nodes"]:
        if node["status"] != "pending":
            continue
        if all(node_map[dep_id]["status"] == "done" for dep_id in node.get("depends_on", [])):
            ready.append(node["node_id"])
    return ready


def advance_node(graph, node_id, new_status):
    """
    Updates a node's status. Returns updated graph (pure — copies).
    Does NOT check ready condition; caller is responsible.
    """
    graph = {"nodes": list(graph["nodes"]), "edges": list(graph["edges"]),
             "status": graph["status"]}
    node_map = {n["node_id"]: n for n in graph["nodes"]}
    if node_id in node_map:
        idx = graph["nodes"].index(node_map[node_id])
        updated = dict(node_map[node_id])
        updated["status"] = new_status
        graph["nodes"][idx] = updated
    # Update graph status
    if new_status == "running" and graph["status"] == "pending":
        graph["status"] = "in_progress"
    elif new_status == "done":
        if all(n["status"] == "done" for n in graph["nodes"]):
            graph["status"] = "completed"
    elif new_status == "failed":
        graph["status"] = "partial_failed"
    return graph


# ---------------------------------------------------------------------------
# Phase 2: DAG Execution — tests
# ---------------------------------------------------------------------------

def _test_template_data_first():
    """data in selected_teams → data-first template"""
    teams = [_team("data"), _team("backend")]
    assert select_graph_template(teams) == "data-first"


def _test_template_research_branch():
    """research selected, no product → research-branch template"""
    teams = [_team("research"), _team("backend")]
    assert select_graph_template(teams) == "research-branch"


def _test_template_linear_pipeline():
    """backend selected → linear-pipeline template"""
    teams = [_team("backend"), _team("frontend")]
    assert select_graph_template(teams) == "linear-pipeline"


def _test_template_flat_parallel():
    """no backend/frontend/data → flat-parallel fallback"""
    teams = [_team("product"), _team("market")]
    assert select_graph_template(teams) == "flat-parallel"


def _test_graph_linear_pipeline():
    """product → backend → frontend"""
    teams = [_team("product", 2), _team("backend", 4), _team("frontend", 3)]
    graph = build_execution_graph("task-001", teams)
    assert graph["status"] == "pending"
    node_ids = [n["node_id"] for n in graph["nodes"]]
    assert "product-1" in node_ids
    assert "backend-1" in node_ids
    assert "frontend-1" in node_ids
    # Check edges
    edges = graph["edges"]
    assert ["product-1", "backend-1"] in edges
    assert ["backend-1", "frontend-1"] in edges
    # backend depends on product
    backend = next(n for n in graph["nodes"] if n["node_id"] == "backend-1")
    assert backend["depends_on"] == ["product-1"]
    # frontend depends on backend
    frontend = next(n for n in graph["nodes"] if n["node_id"] == "frontend-1")
    assert frontend["depends_on"] == ["backend-1"]


def _test_graph_research_branch():
    """research → [backend, frontend] parallel"""
    teams = [_team("research"), _team("backend"), _team("frontend")]
    graph = build_execution_graph("task-002", teams)
    research = next(n for n in graph["nodes"] if n["node_id"] == "research-1")
    backend = next(n for n in graph["nodes"] if n["node_id"] == "backend-1")
    frontend = next(n for n in graph["nodes"] if n["node_id"] == "frontend-1")
    # Both depend on research
    assert backend["depends_on"] == ["research-1"]
    assert frontend["depends_on"] == ["research-1"]
    # No edge between backend and frontend
    edges = graph["edges"]
    assert ["research-1", "backend-1"] in edges
    assert ["research-1", "frontend-1"] in edges
    edge_ids = {tuple(e) for e in edges}
    assert ("backend-1", "frontend-1") not in edge_ids
    assert ("frontend-1", "backend-1") not in edge_ids


def _test_graph_data_first():
    """data → research → product → backend → frontend (all present)"""
    teams = [_team("data"), _team("research"), _team("product"), _team("backend"), _team("frontend")]
    graph = build_execution_graph("task-003", teams)
    node_ids = [n["node_id"] for n in graph["nodes"]]
    assert node_ids == ["data-1", "research-1", "product-1", "backend-1", "frontend-1"]
    edges = graph["edges"]
    assert ["data-1", "research-1"] in edges
    assert ["research-1", "product-1"] in edges
    assert ["product-1", "backend-1"] in edges
    assert ["backend-1", "frontend-1"] in edges


def _test_graph_flat_parallel():
    """product + market → no edges"""
    teams = [_team("product"), _team("market")]
    graph = build_execution_graph("task-004", teams)
    assert graph["edges"] == []
    for node in graph["nodes"]:
        assert node["depends_on"] == []


def _test_ready_nodes_no_deps():
    """flat parallel: all nodes ready initially"""
    teams = [_team("product"), _team("market")]
    graph = build_execution_graph("task-005", teams)
    ready = get_ready_nodes(graph)
    assert set(ready) == {"product-1", "market-1"}


def _test_ready_nodes_linear():
    """linear: first node ready, second not until first done"""
    teams = [_team("product"), _team("backend")]
    graph = build_execution_graph("task-006", teams)
    ready = get_ready_nodes(graph)
    assert ready == ["product-1"]  # only first
    # Advance product to done
    graph = advance_node(graph, "product-1", "done")
    ready = get_ready_nodes(graph)
    assert ready == ["backend-1"]


def _test_ready_nodes_research_parallel():
    """research done → backend and frontend both ready"""
    teams = [_team("research"), _team("backend"), _team("frontend")]
    graph = build_execution_graph("task-007", teams)
    graph = advance_node(graph, "research-1", "done")
    ready = get_ready_nodes(graph)
    assert set(ready) == {"backend-1", "frontend-1"}


def _test_graph_status_done():
    """all nodes done → graph status = completed"""
    teams = [_team("product"), _team("backend")]
    graph = build_execution_graph("task-008", teams)
    graph = advance_node(graph, "product-1", "done")
    graph = advance_node(graph, "backend-1", "done")
    assert graph["status"] == "completed"


def _test_graph_status_partial_failed():
    """node failed → graph status = partial_failed"""
    teams = [_team("product"), _team("backend"), _team("frontend")]
    graph = build_execution_graph("task-009", teams)
    graph = advance_node(graph, "product-1", "done")
    graph = advance_node(graph, "backend-1", "failed")
    assert graph["status"] == "partial_failed"


def _orchestrator_resolve_flow(task_id, action):
    # Load task from workspace (simulated)
    task = {
        "task_id": task_id,
        "status": "awaiting_dispatch_decision",
        "routing_decision": {
            "selected_teams": [],
            "secondary_teams": [],
            "ignored_teams": [],
            "pending_decision": {
                "type": "dispatch_confirmation",
                "band": "medium",
                "context": "medium_when_no_high_exists",
                "teams": [_team("product", 2), _team("frontend", 2)],
                "options": ["all", "none"],
                "default": "none",
            },
        },
    }
    # Simulate read + resolve
    resolved = resolve_task(task, {"selected": action})
    # Step 6 re-evaluation
    rd = resolved["routing_decision"]
    if not rd["selected_teams"] and rd.get("declined_after_ask"):
        resolved["status"] = "user_declined_dispatch"
    elif not rd["selected_teams"]:
        resolved["status"] = "needs_clarification"
    else:
        resolved["status"] = "pending"
    return resolved


def _test_resolve_all_continues_to_dispatch():
    """--resolve all → pending, no user_declined_dispatch, selected_teams populated"""
    result = _orchestrator_resolve_flow("test-task", "all")
    assert [t["team"] for t in result["routing_decision"]["selected_teams"]] == ["product", "frontend"]
    assert result["status"] == "pending"
    assert "pending_decision" not in result["routing_decision"]
    assert result["routing_decision"].get("declined_after_ask") is not True


def _test_resolve_none_sets_declined():
    """--resolve none → declined_after_ask set, status = user_declined_dispatch"""
    result = _orchestrator_resolve_flow("test-task", "none")
    assert result["routing_decision"]["selected_teams"] == []
    assert result["routing_decision"].get("declined_after_ask") is True
    assert result["status"] == "user_declined_dispatch"


def _test_resolve_noop_when_not_awaiting():
    """resolve on task without pending_decision → no-op"""
    task = {
        "task_id": "test-005",
        "status": "pending",
        "routing_decision": {
            "selected_teams": [_team("backend", 4)],
            "secondary_teams": [],
            "ignored_teams": [],
        },
    }
    result = resolve_task(task, {"selected": "all"})
    # No-op: status unchanged
    assert result["status"] == "pending"
    assert [t["team"] for t in result["routing_decision"]["selected_teams"]] == ["backend"]


def _test_resolve_idempotent():
    """resolving same task twice → second call is no-op"""
    task = {
        "task_id": "test-006",
        "status": "awaiting_dispatch_decision",
        "routing_decision": {
            "selected_teams": [],
            "secondary_teams": [],
            "ignored_teams": [],
            "pending_decision": {
                "type": "dispatch_confirmation",
                "band": "medium",
                "context": "medium_when_no_high_exists",
                "teams": [_team("product", 2)],
                "options": ["all", "none"],
                "default": "none",
            },
        },
    }
    r1 = resolve_task(task, {"selected": "all"})
    r2 = resolve_task(r1, {"selected": "all"})
    assert r1["routing_decision"]["selected_teams"] == r2["routing_decision"]["selected_teams"]
    assert len(r2["routing_decision"]["selected_teams"]) == 1


PHASE1_TESTS = [
    ("ask_parks_with_pending_decision", _test_ask_parks_with_pending_decision),
    ("ask_no_fallback_triggered", _test_ask_no_fallback_triggered),
    ("resolve_confirm_all", _test_resolve_confirm_all),
    ("resolve_decline", _test_resolve_decline),
    ("resolve_idempotent_twice", _test_resolve_idempotent_twice),
    ("resolve_noop_on_non_awaiting", _test_resolve_noop_on_non_awaiting),
    ("resolve_with_high_exists_confirm", _test_resolve_with_high_exists_confirm),
    ("backward_compat_v03_ask_required", _test_backward_compat_v03_ask_required),
    ("step6_declined_empty_selected", _test_step6_re_evaluation_declined_empty_selected),
    ("step6_declined_with_high_selected", _test_step6_re_evaluation_declined_with_high_selected),
    # Orchestrator smoke tests
    ("resolve_all_continues_to_dispatch", _test_resolve_all_continues_to_dispatch),
    ("resolve_none_sets_declined", _test_resolve_none_sets_declined),
    ("resolve_noop_when_not_awaiting", _test_resolve_noop_when_not_awaiting),
    ("resolve_idempotent", _test_resolve_idempotent),
]

GRAPH_TESTS = [
    # Template selector
    ("template_data_first", _test_template_data_first),
    ("template_research_branch", _test_template_research_branch),
    ("template_linear_pipeline", _test_template_linear_pipeline),
    ("template_flat_parallel", _test_template_flat_parallel),
    # Graph builder
    ("graph_linear_pipeline", _test_graph_linear_pipeline),
    ("graph_research_branch", _test_graph_research_branch),
    ("graph_data_first", _test_graph_data_first),
    ("graph_flat_parallel", _test_graph_flat_parallel),
    # Ready nodes
    ("ready_nodes_no_deps", _test_ready_nodes_no_deps),
    ("ready_nodes_linear", _test_ready_nodes_linear),
    ("ready_nodes_research_parallel", _test_ready_nodes_research_parallel),
    # Graph status
    ("graph_status_done", _test_graph_status_done),
    ("graph_status_partial_failed", _test_graph_status_partial_failed),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    all_tests = [
        ("normalize", NORMALIZE_TESTS),
        ("auto_ignore", AUTO_IGNORE_TESTS),
        ("ask", ASK_TESTS),
        ("dry_run", DRYRUN_TESTS),
        ("phase1", PHASE1_TESTS),
        ("graph", GRAPH_TESTS),
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
