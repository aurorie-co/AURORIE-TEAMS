#!/usr/bin/env python3
"""
Seeds .claude/workspace/execution_history.jsonl with demo history for v0.7 demo.

Creates 17 events:
- backend: 5 runs, 2 completed, 3 partial_failed → success_rate=0.4 → bias=0.75
- linear template: 6 runs, 4 completed, 2 partial_failed → success_rate=0.67 → bias=0.9
- data-first template: 6 runs, 5 completed, 1 partial_failed → success_rate=0.83 → bias=1.0

Run: python3 demo/v0.7/seed_history.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.feedback import build_feedback_event, append_event


def seed():
    history_path = Path(".claude/workspace/execution_history.jsonl")
    history_path.parent.mkdir(parents=True, exist_ok=True)

    # Overwrite to ensure clean demo state
    history_path.write_text("")

    events = []

    # backend: 5 initial runs (2 completed, 3 partial_failed) → rate=0.4
    # Use flat template so backend count doesn't pollute other template stats
    for i in range(5):
        status = "completed" if i < 2 else "partial_failed"
        events.append(build_feedback_event(
            task_id=f"backend_demo_{i}",
            run_n=1,
            run_kind="initial",
            teams=["backend"],
            graph_template="flat",
            final_status=status,
            failed_nodes=[] if status == "completed" else ["backend-1"],
            resumed=False,
        ))

    # linear template: 6 runs (4 completed, 2 partial_failed) → rate=0.67
    # Use frontend-only teams so template bias is independent of backend stat
    for i in range(6):
        status = "completed" if i < 4 else "partial_failed"
        events.append(build_feedback_event(
            task_id=f"linear_demo_{i}",
            run_n=1,
            run_kind="initial",
            teams=["frontend"],
            graph_template="linear",
            final_status=status,
            failed_nodes=[] if status == "completed" else ["frontend-1"],
            resumed=False,
        ))

    # data-first template: 6 runs (5 completed, 1 partial_failed) → rate=0.83
    for i in range(6):
        status = "completed" if i < 5 else "partial_failed"
        events.append(build_feedback_event(
            task_id=f"data_demo_{i}",
            run_n=1,
            run_kind="initial",
            teams=["data"],
            graph_template="data-first",
            final_status=status,
            failed_nodes=[] if status == "completed" else ["data-1"],
            resumed=False,
        ))

    # Write all events
    for event in events:
        append_event(history_path, event)

    print(f"✅ Seeded {len(events)} events to {history_path}")
    print()
    print("History summary:")
    print("  backend (5 runs):  success_rate=0.4  → bias=0.75")
    print("  linear  (6 runs):  success_rate=0.67  → bias=0.9")
    print("  data-first (6 runs): success_rate=0.83 → bias=1.0")
    print()
    print("Run '@orchestrator --feedback-history' to verify.")


if __name__ == "__main__":
    seed()
