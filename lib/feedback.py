# ─────────────────────────────
# Section 1 — Event Schema
# ─────────────────────────────

def build_feedback_event(task_id, run_n, run_kind, teams, graph_template,
                         final_status, failed_nodes, resumed, milestone_id=None):
    """
    Builds a feedback event dict per the v0.7 schema.

    run_id is deterministic: f"{task_id}_run_{n}"
    """
    from datetime import datetime, timezone
    return {
        "task_id": task_id,
        "run_id": f"{task_id}_run_{run_n}",
        "run_kind": run_kind,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "teams": teams,
        "graph_template": graph_template,
        "final_status": final_status,
        "failed_nodes": failed_nodes,
        "resumed": resumed,
        "milestone_id": milestone_id,
    }


# ─────────────────────────────
# Section 2 — Store (append-only)
# ─────────────────────────────

from pathlib import Path
import json


def append_event(path: Path, event: dict) -> None:
    """
    Appends one JSON event to a JSONL file.
    Creates the file if it does not exist.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(event) + "\n")


def load_events(path: Path) -> list[dict]:
    """
    Loads all events from a JSONL file.
    Returns empty list if file does not exist or is empty.
    """
    path = Path(path)
    if not path.exists():
        return []
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


# ─────────────────────────────
# Section 3 — Aggregation
# ─────────────────────────────

def aggregate_team_stats(events):
    """
    Aggregates team-level success_rate and runs from initial-run events only.

    Success = final_status == "completed"
    Failure = final_status in {"partial_failed", "blocked"}

    Resume runs (run_kind != "initial") are excluded from statistics.

    Returns:
        {
            "backend": {"runs": int, "successes": int, "success_rate": float},
            ...
        }
    """
    totals = {}  # team -> {"runs": int, "successes": int}

    for event in events:
        if event.get("run_kind") != "initial":
            continue
        for team in event.get("teams", []):
            if team not in totals:
                totals[team] = {"runs": 0, "successes": 0}
            totals[team]["runs"] += 1
            if event.get("final_status") == "completed":
                totals[team]["successes"] += 1

    result = {}
    for team, data in totals.items():
        result[team] = {
            "runs": data["runs"],
            "successes": data["successes"],
            "success_rate": data["successes"] / data["runs"] if data["runs"] > 0 else 0.0,
        }
    return result


def aggregate_template_stats(events):
    """
    Aggregates template-level success_rate and runs from initial-run events only.

    Success = final_status == "completed"
    Failure = final_status in {"partial_failed", "blocked"}

    Resume runs (run_kind != "initial") are excluded.

    Returns:
        {
            "linear":    {"runs": int, "successes": int, "success_rate": float},
            "flat":      {"runs": int, "successes": int, "success_rate": float},
            ...
        }
    """
    totals = {}  # template -> {"runs": int, "successes": int}

    for event in events:
        if event.get("run_kind") != "initial":
            continue
        tpl = event.get("graph_template")
        if tpl not in totals:
            totals[tpl] = {"runs": 0, "successes": 0}
        totals[tpl]["runs"] += 1
        if event.get("final_status") == "completed":
            totals[tpl]["successes"] += 1

    result = {}
    for tpl, data in totals.items():
        result[tpl] = {
            "runs": data["runs"],
            "successes": data["successes"],
            "success_rate": data["successes"] / data["runs"] if data["runs"] > 0 else 0.0,
        }
    return result


# ─────────────────────────────
# Section 4 — Bias Computation
# ─────────────────────────────

MIN_SAMPLES = 5


def feedback_multiplier(success_rate: float, runs: int) -> float:
    """
    Returns a bias multiplier in [0.6, 1.0].

    Rules:
    - runs < MIN_SAMPLES (5): insufficient data -> 1.0 (no bias)
    - success_rate >= 0.8:   -> 1.0
    - 0.6 <= rate < 0.8:    -> 0.9
    - 0.4 <= rate < 0.6:    -> 0.75
    - rate < 0.4:           -> 0.6
    """
    if runs < MIN_SAMPLES:
        return 1.0
    if success_rate >= 0.8:
        return 1.0
    if success_rate >= 0.6:
        return 0.9
    if success_rate >= 0.4:
        return 0.75
    return 0.6


def compute_team_bias(team_stats: dict) -> dict:
    """
    Computes bias multiplier per team from aggregated stats.
    """
    return {
        team: feedback_multiplier(data["success_rate"], data["runs"])
        for team, data in team_stats.items()
    }


def compute_template_bias(template_stats: dict) -> dict:
    """
    Computes bias multiplier per template from aggregated stats.
    """
    return {
        tpl: feedback_multiplier(data["success_rate"], data["runs"])
        for tpl, data in template_stats.items()
    }


# ─────────────────────────────
# Section 5 — Orchestrator Hook
# ─────────────────────────────

TERMINAL_STATES = {"completed", "partial_failed", "blocked"}


def is_terminal_state(task: dict) -> bool:
    """Returns True if task is in a terminal state."""
    graph = task.get("execution_graph", {})
    status = graph.get("status") or task.get("status", "")
    return status in TERMINAL_STATES


def get_teams_from_task(task: dict) -> list[str]:
    """Extracts teams from task's execution graph."""
    graph = task.get("execution_graph", {})
    teams = []
    for node in graph.get("nodes", []):
        if node.get("team") and node["team"] not in teams:
            teams.append(node["team"])
    return teams


def get_graph_template(task: dict) -> str:
    """Returns graph_template if set, else 'unknown'."""
    graph = task.get("execution_graph", {})
    return graph.get("metadata", {}).get("graph_template", "unknown")


def get_failed_nodes(task: dict) -> list[str]:
    """Returns list of failed node IDs from execution graph."""
    graph = task.get("execution_graph", {})
    return [
        node["node_id"] for node in graph.get("nodes", [])
        if node.get("status") == "failed"
    ]


def maybe_append_feedback_event(path: Path, task: dict,
                                run_id: str, run_written: dict,
                                run_kind: str) -> None:
    """
    Hook for orchestrator: appends feedback event only on terminal state,
    and only once per run (deduplicated by run_written dict).

    Args:
        path: path to execution_history.jsonl
        task: full task dict
        run_id: the run_id for this event
        run_written: in-memory dict used as guard {run_id: True}
        run_kind: "initial" or "resume" — must be set by the orchestrator
    """
    if run_id in run_written:
        return  # already written for this run
    if not is_terminal_state(task):
        return

    run_written[run_id] = True

    graph = task.get("execution_graph", {})
    final_status = graph.get("status") or task.get("status", "unknown")
    teams = get_teams_from_task(task)
    graph_template = get_graph_template(task)
    failed_nodes = get_failed_nodes(task)
    resumed = bool(task.get("resumed", False))
    milestone_id = task.get("milestone", {}).get("milestone_id") if task.get("milestone") else None

    run_n = int(run_id.rsplit("_", 1)[-1])

    event = build_feedback_event(
        task_id=task["task_id"],
        run_n=run_n,
        run_kind=run_kind,
        teams=teams,
        graph_template=graph_template,
        final_status=final_status,
        failed_nodes=failed_nodes,
        resumed=resumed,
        milestone_id=milestone_id,
    )

    append_event(path, event)


# ─────────────────────────────
# Section 6 — Apply to Routing
# ─────────────────────────────

def apply_team_bias(candidates: list[dict], team_bias: dict,
                    team_stats: dict = None) -> list[dict]:
    """
    Applies feedback bias to team candidates at the score level.

    Each candidate dict is extended with:
      - adjusted_score: raw_score * bias_multiplier
      - feedback_bias: the multiplier used
      - runs (if team_stats provided)
      - success_rate (if team_stats provided)

    Candidates not in team_bias receive bias=1.0.
    """
    result = []
    for c in candidates:
        team = c["team"]
        multiplier = team_bias.get(team, 1.0)
        new_c = dict(c)
        new_c["feedback_bias"] = multiplier
        new_c["adjusted_score"] = c["raw_score"] * multiplier
        if team_stats and team in team_stats:
            new_c["runs"] = team_stats[team]["runs"]
            new_c["success_rate"] = team_stats[team]["success_rate"]
        result.append(new_c)
    return result


def apply_template_bias(candidates: list[str], template_bias: dict) -> dict:
    """
    Applies feedback bias to template candidates.

    Returns dict of {template: {"feedback_bias": float}}.

    Templates not in template_bias receive bias=1.0.
    """
    result = {}
    for tpl in candidates:
        result[tpl] = {
            "feedback_bias": template_bias.get(tpl, 1.0),
        }
    return result
