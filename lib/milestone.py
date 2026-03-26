"""
Milestone pure functions — orchestrator business logic layer.

These functions are deterministic and testable. The orchestrator handles
all I/O (file read/write); these functions only compute state transitions.

Append-only constraint (v0.5): tasks can be added to a milestone, never removed.
Milestone does NOT influence routing decisions.
"""

import uuid
from datetime import datetime, timezone


def make_milestone_id():
    """Generate a stable milestone ID: ms_<uuid[:8]>"""
    return "ms_" + uuid.uuid4().hex[:8]


def create_milestone(title, milestone_id=None):
    """
    Factory: create a new milestone dict.
    Does NOT write to disk — caller handles I/O.
    """
    now = datetime.now(timezone.utc).isoformat()
    return {
        "milestone_id": milestone_id or make_milestone_id(),
        "title": title,
        "status": "pending",
        "tasks": [],
        "created_at": now,
        "updated_at": now,
    }


def attach_task_to_milestone(milestone, task_id):
    """
    Append-only: add task_id to milestone.tasks[] if not already present.
    Returns a new milestone dict (pure — does not mutate input).
    """
    milestone = dict(milestone)
    milestone["tasks"] = list(milestone.get("tasks", []))
    if task_id not in milestone["tasks"]:
        milestone["tasks"].append(task_id)
    milestone["updated_at"] = datetime.now(timezone.utc).isoformat()
    return milestone


def aggregate_milestone_status(task_statuses):
    """
    Aggregate a list of task statuses into a milestone-level status.

    Priority chain (highest wins):
      partial_failed > in_progress > completed > pending
    """
    if not task_statuses:
        return "pending"
    if any(s == "partial_failed" for s in task_statuses):
        return "partial_failed"
    if any(s == "in_progress" for s in task_statuses):
        return "in_progress"
    if all(s == "completed" for s in task_statuses):
        return "completed"
    if all(s == "pending" for s in task_statuses):
        return "pending"
    return "in_progress"  # mixed states


def get_milestone_ref(milestone):
    """
    Lightweight ref for embedding in task JSON.
    Contains only milestone_id and title — no task list or status.
    """
    return {
        "milestone_id": milestone["milestone_id"],
        "title": milestone["title"],
    }
