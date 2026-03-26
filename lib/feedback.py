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
