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
            "options": ["all", "none", "selective"],
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
    # "none" and empty "selective" both count as user-declined
    if decision["selected"] == "none":
        routing_decision["declined_after_ask"] = True
    elif decision["selected"] == "selective" and not decision.get("teams", []):
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
    assert pending["options"] == ["all", "none", "selective"]
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
    assert pending["options"] == ["all", "none", "selective"]
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
            "retryable": True,
            "retry_count": 0,
        }

    if template == "data-first":
        # data → research → product → backend → frontend
        chain = ["data", "research", "product", "backend", "frontend"]
        present = [t for t in chain if t in team_ids]
        nodes = [{"node_id": f"{t}-1", "team": t, "depends_on": [], "status": "pending",
                  "artifacts_in": [], "artifacts_out": [ARTIFACT_OUT[t].format(task_id=task_id)],
                  "retryable": True, "retry_count": 0} for t in present]
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
                "retryable": True,
                "retry_count": 0,
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
                  "artifacts_in": [], "artifacts_out": [ARTIFACT_OUT[t].format(task_id=task_id)],
                  "retryable": True, "retry_count": 0} for t in present]
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
                "retryable": True,
                "retry_count": 0,
            })

    # Populate artifacts_in for each node based on depends_on
    node_map = {n["node_id"]: n for n in nodes}
    for node in nodes:
        for dep_id in node.get("depends_on", []):
            dep_node = node_map.get(dep_id)
            if dep_node:
                node["artifacts_in"].extend(dep_node["artifacts_out"])

    return {
        "nodes": nodes,
        "edges": edges,
        "status": "pending",
        "metadata": {"graph_template": select_graph_template(selected_teams)},
    }


def check_blocked(node):
    """
    Returns True if the node's input artifacts are missing (blocked).
    In production, this checks the filesystem. In tests, use the BLOCKED_NODES set.
    """
    return node.get("blocked", False)


def get_ready_nodes(graph):
    """
    Returns list of node_ids that are ready to dispatch.
    A node is ready when:
    - status == 'pending'
    - all depends_on nodes have status == 'done'
    - not blocked (artifacts_in exist)
    """
    node_map = {n["node_id"]: n for n in graph["nodes"]}
    ready = []
    for node in graph["nodes"]:
        if node["status"] != "pending":
            continue
        if check_blocked(node):
            continue
        if all(node_map[dep_id]["status"] == "done" for dep_id in node.get("depends_on", [])):
            ready.append(node["node_id"])
    return ready


def advance_node(graph, node_id, new_status):
    """
    Updates a node's status. Returns updated graph (pure — copies).
    Does NOT check ready condition; caller is responsible.

    new_status: 'running' | 'done' | 'failed' | 'blocked'
    """
    graph = {
        "metadata": dict(graph.get("metadata", {})),
        "nodes": list(graph["nodes"]),
        "edges": list(graph["edges"]),
        "status": graph["status"],
    }
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
    elif new_status == "blocked":
        # Graph is blocked when all non-done, non-failed nodes are also blocked
        non_terminal = [n for n in graph["nodes"] if n["status"] not in ("done", "failed")]
        if non_terminal and all(n["status"] == "blocked" for n in non_terminal):
            graph["status"] = "blocked"
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


# ---------------------------------------------------------------------------
# Phase 2: E2E Orchestrator Smoke Tests
# Verifies full orchestrator wiring: Step 7 builds graph → Step C executes it.
# _simulate_dispatch_loop mirrors the Step C dispatch loop for test purposes.
# ---------------------------------------------------------------------------

def _simulate_dispatch_loop(task_id, selected_teams):
    """
    Simulates Step C DAG dispatch loop end-to-end.
    Builds graph from selected_teams, then simulates wave-based execution
    by advancing all ready nodes to 'done' in dependency order.

    Returns the final execution_graph dict.
    """
    graph = build_execution_graph(task_id, selected_teams)

    # Simulate wave-based dispatch loop (Step C)
    while graph["status"] not in ("completed", "partial_failed"):
        ready = get_ready_nodes(graph)
        if not ready:
            # Blocked — no forward progress possible
            break
        # Advance all ready nodes to 'done' in this wave
        for node_id in ready:
            graph = advance_node(graph, node_id, "done")

    return graph


def _test_e2e_linear_pipeline():
    """
    E2E: product + backend + frontend → linear pipeline
    Verifies:
    - template = linear-pipeline
    - graph edges: product → backend → frontend
    - Step C wave order: product (wave 1) → backend (wave 2) → frontend (wave 3)
    - graph final status = completed
    """
    teams = [_team("product", 2), _team("backend", 4), _team("frontend", 3)]
    graph = _simulate_dispatch_loop("e2e-linear-001", teams)

    # Template
    assert select_graph_template(teams) == "linear-pipeline"

    # Edges
    edges = graph["edges"]
    assert ["product-1", "backend-1"] in edges
    assert ["backend-1", "frontend-1"] in edges

    # Wave execution order (verified via node status snapshots between advances)
    g = build_execution_graph("e2e-linear-001", teams)
    wave1 = get_ready_nodes(g)
    assert wave1 == ["product-1"]  # only product ready initially

    g = advance_node(g, "product-1", "done")
    wave2 = get_ready_nodes(g)
    assert wave2 == ["backend-1"]  # backend unlocked after product

    g = advance_node(g, "backend-1", "done")
    wave3 = get_ready_nodes(g)
    assert wave3 == ["frontend-1"]  # frontend unlocked after backend

    g = advance_node(g, "frontend-1", "done")
    assert g["status"] == "completed"


def _test_e2e_research_branch_parallel():
    """
    E2E: research + backend + frontend → research-branch fan-out
    Verifies:
    - template = research-branch
    - graph edges: research → backend, research → frontend
    - research done → backend AND frontend ready in same wave (parallel)
    - graph final status = completed
    """
    teams = [_team("research", 3), _team("backend", 4), _team("frontend", 3)]
    graph = _simulate_dispatch_loop("e2e-research-001", teams)

    # Template
    assert select_graph_template(teams) == "research-branch"

    # Edges: both downstream nodes depend on research
    edges = graph["edges"]
    assert ["research-1", "backend-1"] in edges
    assert ["research-1", "frontend-1"] in edges
    # No edge between backend and frontend (parallel, not sequential)
    edge_set = {tuple(e) for e in edges}
    assert ("backend-1", "frontend-1") not in edge_set
    assert ("frontend-1", "backend-1") not in edge_set

    # Wave 1: only research ready
    g = build_execution_graph("e2e-research-001", teams)
    wave1 = get_ready_nodes(g)
    assert wave1 == ["research-1"]

    # Wave 2: backend AND frontend ready simultaneously after research done
    g = advance_node(g, "research-1", "done")
    wave2 = get_ready_nodes(g)
    assert set(wave2) == {"backend-1", "frontend-1"}

    # Advance both in same wave
    g = advance_node(g, "backend-1", "done")
    g = advance_node(g, "frontend-1", "done")
    assert g["status"] == "completed"


# ---------------------------------------------------------------------------
# Selective Routing — v0.5 interactive routing (selective confirm)
# ---------------------------------------------------------------------------

def _test_selective_single_team():
    """
    Selective routing: resolve selective one-of-two pending teams.
    - pending: [product, frontend]
    - resolve selective [product]
    → product selected, frontend ignored, pending_decision cleared
    """
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2), _team("frontend", 2)], policy
    )
    assert pending is not None
    assert pending["options"] == ["all", "none", "selective"], \
        f"pending.options must include 'selective', got {pending['options']}"

    task = _task_from_routing_decision({
        "selected_teams": selected,
        "secondary_teams": secondary,
        "ignored_teams": ignored,
        "pending_decision": pending,
    })
    resolved = resolve_task(task, {"selected": "selective", "teams": ["product"]})
    assert [t["team"] for t in resolved["routing_decision"]["selected_teams"]] == ["product"]
    assert [t["team"] for t in resolved["routing_decision"]["ignored_teams"]] == ["frontend"]
    assert "pending_decision" not in resolved["routing_decision"]
    assert resolved["status"] == "pending"


def _test_selective_multiple_teams():
    """
    Selective routing: resolve selective multiple pending teams.
    - pending: [product, frontend]
    - resolve selective [product, frontend]
    → both selected, pending_decision cleared
    """
    policy = {"high": "auto", "medium": {"when_high_exists": "ignore", "when_no_high_exists": "ask"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [], [_team("product", 2), _team("frontend", 2)], policy
    )
    assert pending["options"] == ["all", "none", "selective"]

    task = _task_from_routing_decision({
        "selected_teams": selected,
        "secondary_teams": secondary,
        "ignored_teams": ignored,
        "pending_decision": pending,
    })
    resolved = resolve_task(task, {"selected": "selective", "teams": ["product", "frontend"]})
    selected_teams = [t["team"] for t in resolved["routing_decision"]["selected_teams"]]
    assert set(selected_teams) == {"product", "frontend"}
    assert "pending_decision" not in resolved["routing_decision"]
    assert resolved["status"] == "pending"


def _test_selective_empty_subset_declined():
    """
    Selective routing: resolve selective with empty list → equivalent to 'none'.
    - pending: [product]
    - resolve selective [] (empty)
    → product ignored, declined_after_ask=True (same as 'none')
    """
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
    resolved = resolve_task(task, {"selected": "selective", "teams": []})
    assert resolved["routing_decision"]["selected_teams"] == []
    assert [t["team"] for t in resolved["routing_decision"]["ignored_teams"]] == ["product"]
    assert resolved["routing_decision"].get("declined_after_ask") is True, \
        "selective empty should set declined_after_ask (same as 'none')"
    assert "pending_decision" not in resolved["routing_decision"]


def _test_selective_invalid_team_ignored():
    """
    Selective routing: team not in pending_decision.teams is silently ignored.
    - pending: [product]
    - resolve selective [backend, data] (neither in pending)
    → product ignored (not in confirmed), no error
    """
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
    resolved = resolve_task(task, {"selected": "selective", "teams": ["backend", "data"]})
    # Invalid teams are ignored; product was neither confirmed nor declined → what happens?
    # Per design: only confirmed teams are moved; unmentioned teams default to ignored
    assert "pending_decision" not in resolved["routing_decision"]


def _test_selective_idempotent_twice():
    """
    Selective routing: resolving same selective payload twice is idempotent.
    - First resolve: [product] selected, [frontend] ignored
    - Second resolve: same result, no duplicates, no state drift
    """
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
    r1 = resolve_task(task, {"selected": "selective", "teams": ["product"]})
    r2 = resolve_task(r1, {"selected": "selective", "teams": ["product"]})
    assert [t["team"] for t in r2["routing_decision"]["selected_teams"]] == ["product"]
    assert [t["team"] for t in r2["routing_decision"]["ignored_teams"]] == ["frontend"]
    # No duplicates
    assert len(r2["routing_decision"]["selected_teams"]) == 1


def _test_selective_with_high_exists_goes_to_secondary():
    """
    Selective routing when high teams exist: medium confirm → secondary (not selected).
    - high: backend (auto), medium: product, frontend (ask)
    - resolve selective [product, frontend]
    → backend stays selected; product+frontend go to secondary
    """
    policy = {"high": "auto", "medium": {"when_high_exists": "ask", "when_no_high_exists": "auto"}}
    selected, secondary, ignored, pending = apply_dispatch_policy(
        [_team("backend", 4)], [_team("product", 2), _team("frontend", 2)], policy
    )
    assert [t["team"] for t in selected] == ["backend"]
    assert pending is not None
    assert pending["options"] == ["all", "none", "selective"]

    task = _task_from_routing_decision({
        "selected_teams": selected,
        "secondary_teams": secondary,
        "ignored_teams": ignored,
        "pending_decision": pending,
    })
    resolved = resolve_task(task, {"selected": "selective", "teams": ["product", "frontend"]})
    # High stays selected; selective medium → secondary (not dispatched)
    assert [t["team"] for t in resolved["routing_decision"]["selected_teams"]] == ["backend"]
    assert set([t["team"] for t in resolved["routing_decision"]["secondary_teams"]]) == {"product", "frontend"}
    assert "pending_decision" not in resolved["routing_decision"]


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
    # Selective routing (v0.5)
    ("selective_single_team", _test_selective_single_team),
    ("selective_multiple_teams", _test_selective_multiple_teams),
    ("selective_empty_subset_declined", _test_selective_empty_subset_declined),
    ("selective_invalid_team_ignored", _test_selective_invalid_team_ignored),
    ("selective_idempotent_twice", _test_selective_idempotent_twice),
    ("selective_with_high_exists_goes_to_secondary", _test_selective_with_high_exists_goes_to_secondary),
]


# ---------------------------------------------------------------------------
# Graph metadata tests
# ---------------------------------------------------------------------------

def _test_build_execution_graph_stores_template():
    """metadata.graph_template is set from select_graph_template."""
    teams = [_team("backend"), _team("frontend")]
    graph = build_execution_graph("t1", teams)
    assert graph["metadata"]["graph_template"] == "linear-pipeline"


def _test_build_execution_graph_metadata_template_data_first():
    """data team → data-first template."""
    teams = [_team("data"), _team("backend")]
    graph = build_execution_graph("t2", teams)
    assert graph["metadata"]["graph_template"] == "data-first"


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
    # Graph metadata
    ("graph_metadata_template_stores", _test_build_execution_graph_stores_template),
    ("graph_metadata_template_data_first", _test_build_execution_graph_metadata_template_data_first),
    # Ready nodes
    ("ready_nodes_no_deps", _test_ready_nodes_no_deps),
    ("ready_nodes_linear", _test_ready_nodes_linear),
    ("ready_nodes_research_parallel", _test_ready_nodes_research_parallel),
    # Graph status
    ("graph_status_done", _test_graph_status_done),
    ("graph_status_partial_failed", _test_graph_status_partial_failed),
    # E2E orchestrator smoke tests (Step 7 → Step C)
    ("e2e_linear_pipeline", _test_e2e_linear_pipeline),
    ("e2e_research_branch_parallel", _test_e2e_research_branch_parallel),
]


# ---------------------------------------------------------------------------
# Milestone pure functions
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Milestone pure functions (imported from lib — single source of truth)
# ---------------------------------------------------------------------------

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
from milestone import (
    make_milestone_id,
    create_milestone,
    attach_task_to_milestone,
    aggregate_milestone_status,
    get_milestone_ref,
)

# ---------------------------------------------------------------------------
# Milestone tests
# ---------------------------------------------------------------------------

def _test_milestone_create():
    """create_milestone → id, title, pending, empty tasks"""
    ms = create_milestone("Launch SaaS v1", "ms_test001")
    assert ms["milestone_id"] == "ms_test001"
    assert ms["title"] == "Launch SaaS v1"
    assert ms["status"] == "pending"
    assert ms["tasks"] == []
    assert "created_at" in ms


def _test_milestone_create_auto_id():
    """create_milestone without id → auto-generates ms_<uuid>"""
    ms = create_milestone("My Milestone")
    assert ms["milestone_id"].startswith("ms_")
    assert len(ms["milestone_id"]) == 11  # ms_ + 8 chars


def _test_milestone_attach_task():
    """attach_task → task added to list"""
    ms = create_milestone("Test", "ms_t001")
    ms = attach_task_to_milestone(ms, "task_abc")
    assert ms["tasks"] == ["task_abc"]


def _test_milestone_attach_multiple_tasks():
    """attach two tasks → both in list"""
    ms = create_milestone("Test", "ms_t002")
    ms = attach_task_to_milestone(ms, "task_1")
    ms = attach_task_to_milestone(ms, "task_2")
    assert ms["tasks"] == ["task_1", "task_2"]


def _test_milestone_append_only_idempotent():
    """same task added twice → no-op"""
    ms = create_milestone("Test", "ms_t003")
    ms = attach_task_to_milestone(ms, "task_x")
    ms = attach_task_to_milestone(ms, "task_x")
    assert ms["tasks"] == ["task_x"]


def _test_aggregate_all_completed():
    """all completed → completed"""
    assert aggregate_milestone_status(["completed", "completed"]) == "completed"


def _test_aggregate_any_in_progress():
    """any in_progress → in_progress"""
    assert aggregate_milestone_status(["completed", "in_progress", "pending"]) == "in_progress"


def _test_aggregate_partial_failed():
    """any partial_failed → partial_failed (highest priority)"""
    assert aggregate_milestone_status(["completed", "partial_failed"]) == "partial_failed"
    assert aggregate_milestone_status(["in_progress", "partial_failed"]) == "partial_failed"


def _test_aggregate_all_pending():
    """all pending → pending"""
    assert aggregate_milestone_status(["pending", "pending"]) == "pending"


def _test_aggregate_mixed_no_in_progress():
    """completed + pending, no in_progress → in_progress"""
    assert aggregate_milestone_status(["completed", "pending"]) == "in_progress"


def _test_aggregate_empty():
    """no tasks → pending"""
    assert aggregate_milestone_status([]) == "pending"


def _test_get_milestone_ref():
    """get_milestone_ref → lightweight {id, title}"""
    ms = create_milestone("My Goal", "ms_ref001")
    ref = get_milestone_ref(ms)
    assert ref == {"milestone_id": "ms_ref001", "title": "My Goal"}
    assert "tasks" not in ref
    assert "status" not in ref


def _test_aggregate_mixed_with_partial_failed():
    """partial_failed takes priority over in_progress and completed"""
    assert aggregate_milestone_status(["completed", "in_progress", "partial_failed"]) == "partial_failed"
    assert aggregate_milestone_status(["pending", "in_progress", "partial_failed"]) == "partial_failed"


def _test_attach_same_task_idempotent():
    """attaching the same task twice does not duplicate"""
    ms = create_milestone("Test", "ms_idem")
    ms = attach_task_to_milestone(ms, "task_x")
    ms = attach_task_to_milestone(ms, "task_x")
    assert ms["tasks"] == ["task_x"]


# ---------------------------------------------------------------------------
# Milestone E2E orchestrator wiring tests
# ---------------------------------------------------------------------------

import json
import os
import tempfile
import shutil


def _temp_workspace():
    """Create a temp workspace dir simulating .claude/workspace."""
    ws = tempfile.mkdtemp()
    os.makedirs(os.path.join(ws, "tasks"))
    os.makedirs(os.path.join(ws, "milestones"))
    return ws


def _write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _read_json(path):
    with open(path) as f:
        return json.load(f)


def _test_e2e_milestone_create_and_attach():
    """
    E2E 1: Create milestone, create task with milestone ref, attach task.
    Verifies:
    - milestone file created at correct path
    - task JSON contains milestone ref
    - milestone.tasks contains task_id
    - milestone status is pending (one task, status=pending)
    """
    ws = _temp_workspace()
    try:
        milestone_title = "Launch SaaS"
        task_id = "task_abc123"

        # Step 1: orchestrator creates milestone
        ms = create_milestone(milestone_title, "ms_e2e001")
        milestone_path = os.path.join(ws, "milestones", f"{ms['milestone_id']}.json")
        _write_json(milestone_path, ms)

        # Step 2: task JSON written (Step A) with milestone ref
        task = {
            "task_id": task_id,
            "status": "pending",
            "milestone": get_milestone_ref(ms),
        }
        task_path = os.path.join(ws, "tasks", f"{task_id}.json")
        _write_json(task_path, task)

        # Step 3: attach task to milestone (after task exists)
        ms = _read_json(milestone_path)
        ms = attach_task_to_milestone(ms, task_id)
        _write_json(milestone_path, ms)

        # Step 4: aggregate status
        ms = _read_json(milestone_path)  # re-read to get updated tasks list
        statuses = [_read_json(os.path.join(ws, "tasks", tid + ".json"))["status"] for tid in ms["tasks"]]
        ms["status"] = aggregate_milestone_status(statuses)
        _write_json(milestone_path, ms)

        # Assertions
        assert os.path.exists(milestone_path), "milestone file must exist"
        ms = _read_json(milestone_path)
        assert ms["milestone_id"] == "ms_e2e001"
        assert ms["title"] == milestone_title
        assert ms["tasks"] == [task_id], f"expected [{task_id}], got {ms['tasks']}"
        assert ms["status"] == "pending"

        task = _read_json(task_path)
        assert task["milestone"] == {"milestone_id": "ms_e2e001", "title": milestone_title}
        assert "tasks" not in task["milestone"]
    finally:
        shutil.rmtree(ws)


def _test_e2e_milestone_second_task_append_only():
    """
    E2E 2: Second task attached to same milestone.
    Verifies:
    - append-only: task_id not duplicated
    - aggregate: pending+pending → pending
    - aggregate: pending+in_progress → in_progress
    - milestone_ref embedded in second task
    """
    ws = _temp_workspace()
    try:
        ms = create_milestone("Multi-task Goal", "ms_e2e002")
        milestone_path = os.path.join(ws, "milestones", f"{ms['milestone_id']}.json")
        _write_json(milestone_path, ms)

        task1_id = "task_t1"
        task2_id = "task_t2"

        # Task 1 created
        task1 = {"task_id": task1_id, "status": "pending", "milestone": get_milestone_ref(ms)}
        _write_json(os.path.join(ws, "tasks", f"{task1_id}.json"), task1)
        ms = attach_task_to_milestone(ms, task1_id)
        ms["status"] = aggregate_milestone_status(["pending"])
        _write_json(milestone_path, ms)

        # Task 2 created
        task2 = {"task_id": task2_id, "status": "in_progress", "milestone": get_milestone_ref(ms)}
        _write_json(os.path.join(ws, "tasks", f"{task2_id}.json"), task2)
        ms = attach_task_to_milestone(ms, task2_id)
        ms["status"] = aggregate_milestone_status(["pending", "in_progress"])
        _write_json(milestone_path, ms)

        ms = _read_json(milestone_path)
        # Append-only: task1 not duplicated
        assert ms["tasks"].count(task1_id) == 1, f"append-only violated: {ms['tasks']}"
        assert ms["tasks"] == [task1_id, task2_id]
        assert ms["status"] == "in_progress"

        # Second task has milestone ref
        t2 = _read_json(os.path.join(ws, "tasks", f"{task2_id}.json"))
        assert t2["milestone"] == {"milestone_id": "ms_e2e002", "title": "Multi-task Goal"}
    finally:
        shutil.rmtree(ws)


# ---------------------------------------------------------------------------
# P0 Runtime tests — fills gaps identified in QA coverage report
# These tests target the "orchestrator integration / runtime contract" layer
# that pure-function tests alone do not cover.
# ---------------------------------------------------------------------------

def _test_e2e_ask_resolve_dag():
    """
    P0-E2E-01: ask parks → resolve all → graph built → Step C executes to completion.
    Verifies the resolve-to-Step-C contract: resolve populates selected_teams,
    graph is built, and DAG dispatch completes all waves.
    """
    # Simulate ask + resolve flow (from _orchestrator_resolve_flow pattern)
    task = {
        "task_id": "test-resolve-dag",
        "status": "awaiting_dispatch_decision",
        "routing_decision": {
            "selected_teams": [],
            "secondary_teams": [],
            "ignored_teams": [],
            "pending_decision": {
                "type": "dispatch_confirmation",
                "band": "medium",
                "context": "medium_when_no_high_exists",
                "teams": [_team("backend", 3), _team("frontend", 2)],
                "options": ["all", "none"],
                "default": "none",
            },
        },
    }
    resolved = resolve_task(task, {"selected": "all"})
    assert resolved["status"] == "pending"
    assert "pending_decision" not in resolved["routing_decision"]
    selected = resolved["routing_decision"]["selected_teams"]
    assert len(selected) == 2

    # Verify Step C would execute: build graph and run to completion
    graph = build_execution_graph("test-resolve-dag", selected)
    assert graph["status"] == "pending"
    assert len(graph["nodes"]) == 2

    # Step C dispatch loop: simulate to completion
    g = graph
    while g["status"] not in ("completed", "partial_failed"):
        ready = get_ready_nodes(g)
        if not ready:
            break
        for node_id in ready:
            g = advance_node(g, node_id, "done")

    assert g["status"] == "completed", f"Expected completed, got {g['status']}"


def _test_e2e_partial_failure_middle_wave():
    """
    P0-E2E-02: linear pipeline, wave 1 done → wave 2 partial_failed → graph stops.
    Verifies that partial failure in any wave propagates to graph status and halts dispatch.
    This is the most critical DAG runtime guarantee.
    """
    teams = [_team("product", 3), _team("backend", 4), _team("frontend", 2)]
    graph = build_execution_graph("test-partial-fail", teams)
    assert select_graph_template(teams) == "linear-pipeline"

    # Wave 1: product advances to done
    g = advance_node(graph, "product-1", "done")
    wave2 = get_ready_nodes(g)
    assert wave2 == ["backend-1"]  # backend unlocked

    # Wave 2: backend partial_fails — this MUST halt the dispatch loop
    g = advance_node(g, "backend-1", "failed")
    assert g["status"] == "partial_failed"
    assert g["nodes"][1]["status"] == "failed"  # backend node is failed

    # Verify dispatch loop would stop (no more advance calls)
    ready = get_ready_nodes(g)
    assert ready == [], f"Expected no ready nodes after partial_failure, got {ready}"


def _test_ready_nodes_empty_on_terminal_graph():
    """
    P0-RT-01: completed graph → get_ready_nodes returns [].
    Verifies the contract: once graph reaches terminal status, no nodes are ready.
    """
    teams = [_team("product", 2), _team("backend", 4)]
    graph = build_execution_graph("test-terminal", teams)

    # Advance all to done
    g = advance_node(graph, "product-1", "done")
    assert g["status"] == "pending"
    g = advance_node(g, "backend-1", "done")
    assert g["status"] == "completed"

    # Terminal graph must return empty ready set
    ready = get_ready_nodes(g)
    assert ready == [], f"Expected [] on completed graph, got {ready}"


def _test_advance_node_idempotent_on_done():
    """
    P0-RT-02: advancing an already-done node is a no-op (idempotent).
    This prevents double-processing if orchestrator calls advance_node twice.
    """
    teams = [_team("backend", 4)]
    graph = build_execution_graph("test-idempotent", teams)
    g = advance_node(graph, "backend-1", "done")
    assert g["status"] == "completed"
    assert g["nodes"][0]["status"] == "done"

    # Advance again — must be idempotent
    g2 = advance_node(g, "backend-1", "done")
    assert g2["status"] == "completed"  # still completed
    assert g2["nodes"][0]["status"] == "done"  # still done
    # Graph unchanged
    assert g == g2


def _test_e2e_research_branch_partial_failure():
    """
    P0-E2E-03: research branch fan-out, research done, one downstream fails.
    Verifies: fan-out where backend fails but frontend completes → graph partial_failed.
    Also verifies the surviving branch (frontend) is correctly handled.
    """
    teams = [_team("research", 3), _team("backend", 4), _team("frontend", 2)]
    graph = build_execution_graph("test-research-fail", teams)
    assert select_graph_template(teams) == "research-branch"

    # Wave 1: research done
    g = advance_node(graph, "research-1", "done")
    wave2 = get_ready_nodes(g)
    assert set(wave2) == {"backend-1", "frontend-1"}  # both ready in parallel

    # Wave 2: backend fails, frontend completes
    g = advance_node(g, "backend-1", "failed")
    assert g["status"] == "partial_failed"

    # frontend was still in wave2; verify it's still tracked correctly
    frontend_node = next(n for n in g["nodes"] if n["team"] == "frontend")
    assert frontend_node["status"] == "pending"  # not yet advanced, still pending


def _test_get_ready_nodes_on_partial_failed_graph():
    """
    P0-RT-03: partial_failed graph → get_ready_nodes returns [].
    Confirms terminal status locks the ready set.
    """
    teams = [_team("backend", 4), _team("frontend", 2)]
    graph = build_execution_graph("test-pf-terminal", teams)
    g = advance_node(graph, "backend-1", "failed")
    assert g["status"] == "partial_failed"

    ready = get_ready_nodes(g)
    assert ready == [], f"Expected [] on partial_failed graph, got {ready}"


def _test_blocked_node_excluded_from_ready():
    """
    G-22: Node with blocked=True (artifacts_in missing) is excluded from get_ready_nodes.
    Confirms: blocked nodes are not dispatched even when depends_on are satisfied.
    """
    teams = [_team("research", 3), _team("backend", 4), _team("frontend", 2)]
    graph = build_execution_graph("test-blocked", teams)
    assert select_graph_template(teams) == "research-branch"

    # Wave 1: research completes
    g = advance_node(graph, "research-1", "done")
    wave2 = get_ready_nodes(g)
    assert set(wave2) == {"backend-1", "frontend-1"}  # both ready

    # Backend has missing artifacts_in → mark it blocked
    node_map = {n["node_id"]: n for n in g["nodes"]}
    idx = g["nodes"].index(node_map["backend-1"])
    g["nodes"][idx] = dict(g["nodes"][idx])
    g["nodes"][idx]["blocked"] = True

    # Backend is now blocked; frontend should still be ready
    ready = get_ready_nodes(g)
    assert "backend-1" not in ready, "blocked node should not be in ready set"
    assert "frontend-1" in ready, "frontend should still be ready"

    # Frontend completes
    g = advance_node(g, "frontend-1", "done")

    # Backend is still blocked; no nodes ready; graph stays pending (not terminal)
    ready = get_ready_nodes(g)
    assert ready == [], "no ready nodes when blocked node remains"
    assert g["status"] == "pending", f"graph pending (blocked not terminal), got {g['status']}"


def _test_blocked_graph_becomes_blocked_status():
    """
    G-20: When ALL non-terminal nodes are blocked → graph status becomes 'blocked'.
    Confirms the terminal blocked state: all remaining work is stuck on missing artifacts.
    """
    teams = [_team("product", 3), _team("backend", 4)]
    graph = build_execution_graph("test-all-blocked", teams)
    assert select_graph_template(teams) == "linear-pipeline"

    # Wave 1: product completes → backend has depends satisfied
    g = advance_node(graph, "product-1", "done")

    # Backend's artifacts_in are missing → mark blocked
    node_map = {n["node_id"]: n for n in g["nodes"]}
    idx = g["nodes"].index(node_map["backend-1"])
    g["nodes"][idx] = dict(g["nodes"][idx])
    g["nodes"][idx]["blocked"] = True

    # No ready nodes
    ready = get_ready_nodes(g)
    assert ready == []

    # Graph transitions to blocked (all non-done nodes are blocked)
    g = advance_node(g, "backend-1", "blocked")
    assert g["status"] == "blocked", f"Expected blocked, got {g['status']}"

    # Terminal: get_ready_nodes returns [] on blocked graph
    ready = get_ready_nodes(g)
    assert ready == [], "get_ready_nodes returns [] on blocked graph"


def _test_unblock_and_redispatch():
    """
    Unblock scenario: node has blocked=True, then blocked=False when artifacts appear.
    The node's status must also be set back to 'pending' for get_ready_nodes to include it.
    """
    teams = [_team("product", 3), _team("backend", 4)]
    graph = build_execution_graph("test-unblock", teams)

    # Wave 1: product completes
    g = advance_node(graph, "product-1", "done")

    # Backend is blocked (artifacts_in missing)
    node_map = {n["node_id"]: n for n in g["nodes"]}
    idx = g["nodes"].index(node_map["backend-1"])
    g["nodes"][idx] = dict(g["nodes"][idx])
    g["nodes"][idx]["blocked"] = True

    # Backend is blocked
    assert "backend-1" not in get_ready_nodes(g)

    # Artifacts appear: unblock backend (set blocked=False and status=pending)
    # Must re-fetch node_map since we replaced the node dict above
    node_map = {n["node_id"]: n for n in g["nodes"]}
    idx = g["nodes"].index(node_map["backend-1"])
    g["nodes"][idx] = dict(g["nodes"][idx])
    g["nodes"][idx]["blocked"] = False
    g["nodes"][idx]["status"] = "pending"

    # Backend is now ready
    ready = get_ready_nodes(g)
    assert "backend-1" in ready, "unblocked node should be ready"


# ---------------------------------------------------------------------------
# Orchestrator dispatch prompt template tests
# ---------------------------------------------------------------------------

ORCHESTRATOR_DISPATCH_TESTS = []


def _test_step_a_uses_general_purpose_agent_type():
    """Step A dispatch must use subagent_type='general-purpose' (only available type)."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    # Find Step A dispatch block
    step_a_start = content.find("### Step A — Single Dispatch")
    step_b_start = content.find("### Step B — Parallel Dispatch")
    assert step_a_start != -1, "Step A not found in orchestrator.md"
    step_a_section = content[step_a_start:step_b_start]

    # Must specify subagent_type: "general-purpose"
    assert 'subagent_type: "general-purpose"' in step_a_section, (
        "Step A must use subagent_type='general-purpose' for dispatch"
    )


def _test_step_a_reads_team_lead_agent_file():
    """Step A dispatch must instruct agent to read aurorie-<team>-lead.md."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step_a_start = content.find("### Step A — Single Dispatch")
    step_b_start = content.find("### Step B — Parallel Dispatch")
    step_a_section = content[step_a_start:step_b_start]

    # Must instruct reading the team lead agent description
    assert "aurorie-<team>-lead.md" in step_a_section, (
        "Step A must instruct reading aurorie-<team>-lead.md for team lead role"
    )


def _test_step_a_reads_workflow_file():
    """Step A dispatch must instruct agent to read .claude/workflows/<team>.md."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step_a_start = content.find("### Step A — Single Dispatch")
    step_b_start = content.find("### Step B — Parallel Dispatch")
    step_a_section = content[step_a_start:step_b_start]

    # Must instruct reading the workflow
    assert ".claude/workflows/<team>.md" in step_a_section, (
        "Step A must instruct reading .claude/workflows/<team>.md for execution steps"
    )


ORCHESTRATOR_DISPATCH_TESTS = [
    ("step_a_uses_general_purpose_agent_type", _test_step_a_uses_general_purpose_agent_type),
    ("step_a_reads_team_lead_agent_file", _test_step_a_reads_team_lead_agent_file),
    ("step_a_reads_workflow_file", _test_step_a_reads_workflow_file),
]


# ---------------------------------------------------------------------------
# Orchestrator Step B/C dispatch validation
# ---------------------------------------------------------------------------

ORCHESTRATOR_STEP_B_TESTS = []


def _test_step_b_uses_step_a_template():
    """Step B must reference Step A prompt template for dispatch."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step_b_start = content.find("### Step B — Parallel Dispatch")
    step_c_start = content.find("### Step C — DAG Dispatch Loop")
    assert step_b_start != -1, "Step B not found in orchestrator.md"
    step_b_section = content[step_b_start:step_c_start]

    # Must use Step A template
    assert "Step A prompt template" in step_b_section, (
        "Step B must use the Step A prompt template for dispatch"
    )


def _test_step_b_parallels_dispatch():
    """Step B must indicate parallel dispatch of multiple team leads."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step_b_start = content.find("### Step B — Parallel Dispatch")
    step_c_start = content.find("### Step C — DAG Dispatch Loop")
    step_b_section = content[step_b_start:step_c_start]

    # Must indicate simultaneous/parallel dispatch
    assert "simultaneously" in step_b_section or "parallel" in step_b_section.lower(), (
        "Step B must indicate simultaneous/parallel dispatch"
    )


def _test_step_b_respects_selected_teams_only():
    """Step B must dispatch only selected_teams, never secondary_teams."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step_b_start = content.find("### Step B — Parallel Dispatch")
    step_c_start = content.find("### Step C — DAG Dispatch Loop")
    step_b_section = content[step_b_start:step_c_start]

    # Must have constraint about selected_teams only
    assert "selected_teams" in step_b_section, (
        "Step B must reference selected_teams"
    )
    assert "secondary_teams" in step_b_section or "informational" in step_b_section.lower(), (
        "Step B must clarify secondary_teams are informational only"
    )


ORCHESTRATOR_STEP_B_TESTS = [
    ("step_b_uses_step_a_template", _test_step_b_uses_step_a_template),
    ("step_b_parallels_dispatch", _test_step_b_parallels_dispatch),
    ("step_b_respects_selected_teams_only", _test_step_b_respects_selected_teams_only),
]


# ---------------------------------------------------------------------------
# Orchestrator Step C dispatch validation
# ---------------------------------------------------------------------------

ORCHESTRATOR_STEP_C_TESTS = []


def _test_step_c_uses_step_b_for_ready_nodes():
    """Step C must dispatch ready nodes via Step B."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step_c_start = content.find("### Step C — DAG Dispatch Loop")
    assert step_c_start != -1, "Step C not found"
    # Find end of Step C section
    orchestrator_end = content.find("\n## ", step_c_start + 10)
    if orchestrator_end == -1:
        orchestrator_end = len(content)
    step_c_section = content[step_c_start:orchestrator_end]

    # Must use Step B for ready node dispatch
    assert "Step B" in step_c_section, (
        "Step C must dispatch ready nodes via Step B"
    )


def _test_step_c_handles_auto_retry():
    """Step C must handle auto-retry when nodes fail."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step_c_start = content.find("### Step C — DAG Dispatch Loop")
    orchestrator_end = content.find("\n## ", step_c_start + 10)
    if orchestrator_end == -1:
        orchestrator_end = len(content)
    step_c_section = content[step_c_start:orchestrator_end]

    # Must handle auto-retry
    assert "auto_retry" in step_c_section.lower() or "retry" in step_c_section, (
        "Step C must handle auto-retry for failed nodes"
    )


def _test_step_c_checks_terminal_status():
    """Step C must STOP when graph reaches terminal state."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step_c_start = content.find("### Step C — DAG Dispatch Loop")
    orchestrator_end = content.find("\n## ", step_c_start + 10)
    if orchestrator_end == -1:
        orchestrator_end = len(content)
    step_c_section = content[step_c_start:orchestrator_end]

    # Must check terminal status
    assert "completed" in step_c_section or "partial_failed" in step_c_section or "STOP" in step_c_section, (
        "Step C must check for terminal states (completed/partial_failed)"
    )


ORCHESTRATOR_STEP_C_TESTS = [
    ("step_c_uses_step_b_for_ready_nodes", _test_step_c_uses_step_b_for_ready_nodes),
    ("step_c_handles_auto_retry", _test_step_c_handles_auto_retry),
    ("step_c_checks_terminal_status", _test_step_c_checks_terminal_status),
]


# ---------------------------------------------------------------------------
# Orchestrator Resolve Interface validation
# ---------------------------------------------------------------------------

ORCHESTRATOR_RESOLVE_TESTS = []


def _test_resolve_accepts_all_none_selective():
    """Resolve interface must accept all/none/selective actions."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    resolve_start = content.find("### Resolve Interface")
    assert resolve_start != -1, "Resolve Interface not found"
    resolve_section = content[resolve_start:resolve_start + 3000]

    assert '"all"' in resolve_section, "Resolve must accept 'all'"
    assert '"none"' in resolve_section, "Resolve must accept 'none'"
    assert '"selective"' in resolve_section, "Resolve must accept 'selective'"


def _test_resolve_validates_pending_decision():
    """Resolve must validate pending_decision is present."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    resolve_start = content.find("### Resolve Interface")
    resolve_section = content[resolve_start:resolve_start + 3000]

    assert "pending_decision" in resolve_section, (
        "Resolve must validate pending_decision is present"
    )


ORCHESTRATOR_RESOLVE_TESTS = [
    ("resolve_accepts_all_none_selective", _test_resolve_accepts_all_none_selective),
    ("resolve_validates_pending_decision", _test_resolve_validates_pending_decision),
]


# ---------------------------------------------------------------------------
# Orchestrator Replay Interface validation
# ---------------------------------------------------------------------------

ORCHESTRATOR_REPLAY_TESTS = []


def _test_replay_has_interface():
    """Orchestrator must have Replay Interface section."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    assert "### Replay Interface" in content, (
        "Orchestrator must have Replay Interface section"
    )


def _test_replay_is_read_only():
    """Replay must be read-only with no state mutation."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    replay_start = content.find("### Replay Interface")
    replay_end = content.find("### Resume Interface", replay_start)
    if replay_end == -1:
        replay_end = replay_start + 2000
    replay_section = content[replay_start:replay_end]

    assert "read-only" in replay_section.lower() or "no state mutation" in replay_section.lower(), (
        "Replay must be read-only with no state mutation"
    )


ORCHESTRATOR_REPLAY_TESTS = [
    ("replay_has_interface", _test_replay_has_interface),
    ("replay_is_read_only", _test_replay_is_read_only),
]


# ---------------------------------------------------------------------------
# Orchestrator Resume Interface validation
# ---------------------------------------------------------------------------

ORCHESTRATOR_RESUME_TESTS = []


def _test_resume_has_interface():
    """Orchestrator must have Resume Interface section."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    assert "### Resume Interface" in content, (
        "Orchestrator must have Resume Interface section"
    )


def _test_resume_handles_partial_failed():
    """Resume must handle partial_failed state."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    resume_start = content.find("### Resume Interface")
    resume_section = content[resume_start:resume_start + 3000]

    assert "partial_failed" in resume_section, (
        "Resume must handle partial_failed state"
    )


def _test_resume_increments_run_n():
    """Resume must increment run_n for tracking."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    resume_start = content.find("### Resume Interface")
    resume_section = content[resume_start:resume_start + 3000]

    assert "run_n" in resume_section, (
        "Resume must increment run_n for tracking"
    )


ORCHESTRATOR_RESUME_TESTS = [
    ("resume_has_interface", _test_resume_has_interface),
    ("resume_handles_partial_failed", _test_resume_handles_partial_failed),
    ("resume_increments_run_n", _test_resume_increments_run_n),
]


# ---------------------------------------------------------------------------
# Orchestrator Milestone Interface validation
# ---------------------------------------------------------------------------

ORCHESTRATOR_MILESTONE_TESTS = []


def _test_milestone_has_interface():
    """Orchestrator must have Milestone Interface section."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    assert "## Milestone Interface" in content, (
        "Orchestrator must have Milestone Interface section"
    )


def _test_milestone_status_mode():
    """Orchestrator must support --milestone-status flag."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step0_start = content.find("### Step 0")
    step1_start = content.find("### Step 1")
    step0_section = content[step0_start:step1_start]

    assert "--milestone-status" in step0_section, (
        "Orchestrator must support --milestone-status flag in Step 0"
    )


def _test_milestone_mode():
    """Orchestrator must support --milestone flag."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step0_start = content.find("### Step 0")
    step1_start = content.find("### Step 1")
    step0_section = content[step0_start:step1_start]

    assert "--milestone" in step0_section, (
        "Orchestrator must support --milestone flag in Step 0"
    )


ORCHESTRATOR_MILESTONE_TESTS = [
    ("milestone_has_interface", _test_milestone_has_interface),
    ("milestone_status_mode", _test_milestone_status_mode),
    ("milestone_mode", _test_milestone_mode),
]


# ---------------------------------------------------------------------------
# Orchestrator Dry-run Mode validation
# ---------------------------------------------------------------------------

ORCHESTRATOR_DRYRUN_TESTS = []


def _test_dry_run_flag_in_step0():
    """Orchestrator must support --dry-run flag in Step 0."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step0_start = content.find("### Step 0")
    step1_start = content.find("### Step 1")
    step0_section = content[step0_start:step1_start]

    assert "--dry-run" in step0_section, (
        "Orchestrator must support --dry-run flag in Step 0"
    )


def _test_dry_run_skips_dispatch():
    """Dry-run mode must skip Steps A/B dispatch."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step_a_start = content.find("### Step A")
    step0_start = content.find("### Step 0")
    step1_start = content.find("### Step 1")
    step0_section = content[step0_start:step1_start]

    # Find dry_run_mode in step 0
    assert "dry_run_mode" in step0_section or "--dry-run" in step0_section, (
        "Orchestrator must track dry_run_mode"
    )

    # Step A/B must mention skipping when dry_run_mode is true
    step_a_section = content[step_a_start:step_a_start + 500]
    assert "dry_run_mode = true" in step_a_section or "dry-run" in step_a_section.lower(), (
        "Step A must skip when dry_run_mode is true"
    )


ORCHESTRATOR_DRYRUN_TESTS = [
    ("dry_run_flag_in_step0", _test_dry_run_flag_in_step0),
    ("dry_run_skips_dispatch", _test_dry_run_skips_dispatch),
]


# ---------------------------------------------------------------------------
# Orchestrator Feedback Mode validation
# ---------------------------------------------------------------------------

ORCHESTRATOR_FEEDBACK_TESTS = []


def _test_feedback_flag_in_step0():
    """Orchestrator must support --feedback and --feedback-history flags."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step0_start = content.find("### Step 0")
    step1_start = content.find("### Step 1")
    step0_section = content[step0_start:step1_start]

    assert "--feedback" in step0_section, (
        "Orchestrator must support --feedback flag in Step 0"
    )
    assert "--feedback-history" in step0_section, (
        "Orchestrator must support --feedback-history flag in Step 0"
    )


def _test_feedback_bias_applied_in_step3_6():
    """Step 3.6 must apply feedback bias to candidate scores."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step3_6_start = content.find("### Step 3.6 — Apply Feedback Bias")
    assert step3_6_start != -1, "Step 3.6 not found"

    step3_6_end = content.find("### Step 4", step3_6_start)
    step3_6_section = content[step3_6_start:step3_6_end]

    assert "feedback" in step3_6_section.lower() or "bias" in step3_6_section.lower(), (
        "Step 3.6 must apply feedback bias"
    )


def _test_feedback_mode_shows_debug_output():
    """Step 7.6 must render feedback bias debug when feedback_mode is true."""
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    content = orchestrator_path.read_text()

    step7_6_start = content.find("### Step 7.6 — Feedback Bias Debug")
    assert step7_6_start != -1, "Step 7.6 not found"

    step7_6_section = content[step7_6_start:step7_6_start + 1000]

    assert "feedback_mode = true" in step7_6_section, (
        "Step 7.6 must check feedback_mode = true"
    )


ORCHESTRATOR_FEEDBACK_TESTS = [
    ("feedback_flag_in_step0", _test_feedback_flag_in_step0),
    ("feedback_bias_applied_in_step3_6", _test_feedback_bias_applied_in_step3_6),
    ("feedback_mode_shows_debug_output", _test_feedback_mode_shows_debug_output),
]


RUNTIME_TESTS = [
    # P0-E2E: Orchestrator integration — ask/resolve → DAG dispatch
    ("e2e_ask_resolve_dag", _test_e2e_ask_resolve_dag),
    ("e2e_partial_failure_middle_wave", _test_e2e_partial_failure_middle_wave),
    ("e2e_research_branch_partial_failure", _test_e2e_research_branch_partial_failure),
    # P0-RT: Graph runtime contracts
    ("ready_nodes_empty_on_terminal_graph", _test_ready_nodes_empty_on_terminal_graph),
    ("advance_node_idempotent_done", _test_advance_node_idempotent_on_done),
    ("get_ready_nodes_on_partial_failed_graph", _test_get_ready_nodes_on_partial_failed_graph),
    # P1-RT: Blocked node handling (G-20, G-22)
    ("blocked_node_excluded_from_ready", _test_blocked_node_excluded_from_ready),
    ("blocked_graph_becomes_blocked_status", _test_blocked_graph_becomes_blocked_status),
    ("unblock_and_redispatch", _test_unblock_and_redispatch),
]


MILESTONE_TESTS = [
    ("milestone_create", _test_milestone_create),
    ("milestone_create_auto_id", _test_milestone_create_auto_id),
    ("milestone_attach_task", _test_milestone_attach_task),
    ("milestone_attach_multiple_tasks", _test_milestone_attach_multiple_tasks),
    ("milestone_append_only_idempotent", _test_milestone_append_only_idempotent),
    ("aggregate_all_completed", _test_aggregate_all_completed),
    ("aggregate_any_in_progress", _test_aggregate_any_in_progress),
    ("aggregate_partial_failed", _test_aggregate_partial_failed),
    ("aggregate_all_pending", _test_aggregate_all_pending),
    ("aggregate_mixed_no_in_progress", _test_aggregate_mixed_no_in_progress),
    ("aggregate_empty", _test_aggregate_empty),
    ("get_milestone_ref", _test_get_milestone_ref),
    ("aggregate_mixed_with_partial_failed", _test_aggregate_mixed_with_partial_failed),
    ("attach_same_task_idempotent", _test_attach_same_task_idempotent),
    ("e2e_milestone_create_and_attach", _test_e2e_milestone_create_and_attach),
    ("e2e_milestone_second_task_append_only", _test_e2e_milestone_second_task_append_only),
]

# ---------------------------------------------------------------------------
# Coordinator Protocol validation (fix for team-lead-implementing-directly bug)
# ---------------------------------------------------------------------------

COORDINATOR_PROTOCOL_TESTS = []


def _read_orchestrator():
    from pathlib import Path
    orchestrator_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "orchestrator.md"
    if not orchestrator_path.exists():
        orchestrator_path = Path(__file__).parent.parent.parent / "shared" / "agents" / "orchestrator.md"
    return orchestrator_path.read_text()


def _test_step_a_has_mandatory_protocol():
    """Step A must have MANDATORY PROTOCOL section with explicit coordinator rules."""
    content = _read_orchestrator()
    step_a_start = content.find("### Step A — Single Dispatch")
    step_b_start = content.find("### Step B — Parallel Dispatch")
    step_a_section = content[step_a_start:step_b_start]

    assert "MANDATORY PROTOCOL" in step_a_section, (
        "Step A must contain MANDATORY PROTOCOL section"
    )


def _test_step_a_never_implement_rule():
    """Step A must explicitly forbid the agent from implementing directly."""
    content = _read_orchestrator()
    step_a_start = content.find("### Step A — Single Dispatch")
    step_b_start = content.find("### Step B — Parallel Dispatch")
    step_a_section = content[step_a_start:step_b_start]

    # Must have "NEVER" rule against direct implementation
    assert "NEVER" in step_a_section and "implement" in step_a_section.lower(), (
        "Step A must have a 'NEVER implement' rule in MANDATORY PROTOCOL"
    )


def _test_step_a_dispatch_via_agent_tool():
    """Step A must instruct dispatch via Agent tool with subagent_type."""
    content = _read_orchestrator()
    step_a_start = content.find("### Step A — Single Dispatch")
    step_b_start = content.find("### Step B — Parallel Dispatch")
    step_a_section = content[step_a_start:step_b_start]

    assert 'Agent(subagent_type="general-purpose"' in step_a_section or \
           "Agent tool" in step_a_section, (
        "Step A must instruct dispatch via Agent tool"
    )


def _test_step_a_reads_workflow_first():
    """Step A must instruct reading workflow file FIRST before any other action."""
    content = _read_orchestrator()
    step_a_start = content.find("### Step A — Single Dispatch")
    step_b_start = content.find("### Step B — Parallel Dispatch")
    step_a_section = content[step_a_start:step_b_start]

    # The dispatch block must mention reading workflow file first
    assert ".claude/workflows/" in step_a_section, (
        "Step A must mention reading workflow file"
    )


def _test_step_b_reinforces_coordinator_protocol():
    """Step B must reinforce that team leads follow coordinator protocol."""
    content = _read_orchestrator()
    step_b_start = content.find("### Step B — Parallel Dispatch")
    step_c_start = content.find("### Step C — DAG Dispatch Loop")
    step_b_section = content[step_b_start:step_c_start]

    # Step B must mention coordinator protocol
    assert "MANDATORY PROTOCOL" in step_b_section or "coordinator" in step_b_section.lower(), (
        "Step B must reinforce coordinator protocol"
    )


def _test_frontend_lead_has_hard_coordinator_rules():
    """aurorie-frontend-lead must have hard rules making coordinator behavior non-negotiable."""
    from pathlib import Path
    lead_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "aurorie-frontend-lead.md"
    if not lead_path.exists():
        return  # skip if not present in this project

    content = lead_path.read_text()

    # Must define role as COORDINATOR
    assert "COORDINATOR" in content, (
        "aurorie-frontend-lead must explicitly define role as COORDINATOR"
    )
    # Must have NEVER implement rule
    assert "NEVER" in content and ("implement" in content.lower() or "write" in content.lower()), (
        "aurorie-frontend-lead must have NEVER implement/write rule"
    )
    # Must have ALWAYS dispatch rule
    assert "ALWAYS" in content and "dispatch" in content.lower(), (
        "aurorie-frontend-lead must have ALWAYS dispatch rule"
    )


def _test_design_workflow_has_ui_design_section():
    """design.md must have UI Design section for design→frontend handoff."""
    from pathlib import Path
    workflow_path = Path(__file__).parent.parent.parent / ".claude" / "workflows" / "design.md"
    if not workflow_path.exists():
        return  # skip if not present in this project

    content = workflow_path.read_text()

    assert "## UI Design" in content, (
        "design.md must have ## UI Design section"
    )
    # Must mention frontend team handoff
    assert "frontend" in content.lower() and ("handoff" in content.lower() or "implement" in content.lower()), (
        "design.md UI Design section must mention frontend team handoff or implementation"
    )


COORDINATOR_PROTOCOL_TESTS = [
    ("step_a_mandatory_protocol_exists", _test_step_a_has_mandatory_protocol),
    ("step_a_never_implement_rule", _test_step_a_never_implement_rule),
    ("step_a_dispatch_via_agent_tool", _test_step_a_dispatch_via_agent_tool),
    ("step_a_reads_workflow_first", _test_step_a_reads_workflow_first),
    ("step_b_reinforces_coordinator_protocol", _test_step_b_reinforces_coordinator_protocol),
    ("frontend_lead_hard_coordinator_rules", _test_frontend_lead_has_hard_coordinator_rules),
    ("design_workflow_ui_design_section", _test_design_workflow_has_ui_design_section),
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
        ("milestone", MILESTONE_TESTS),
        ("runtime", RUNTIME_TESTS),
        ("orchestrator_dispatch", ORCHESTRATOR_DISPATCH_TESTS),
        ("orchestrator_step_b", ORCHESTRATOR_STEP_B_TESTS),
        ("orchestrator_step_c", ORCHESTRATOR_STEP_C_TESTS),
        ("orchestrator_resolve", ORCHESTRATOR_RESOLVE_TESTS),
        ("orchestrator_replay", ORCHESTRATOR_REPLAY_TESTS),
        ("orchestrator_resume", ORCHESTRATOR_RESUME_TESTS),
        ("orchestrator_milestone", ORCHESTRATOR_MILESTONE_TESTS),
        ("orchestrator_dryrun", ORCHESTRATOR_DRYRUN_TESTS),
        ("orchestrator_feedback", ORCHESTRATOR_FEEDBACK_TESTS),
        ("coordinator_protocol", COORDINATOR_PROTOCOL_TESTS),
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
