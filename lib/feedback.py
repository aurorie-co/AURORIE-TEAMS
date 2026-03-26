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
