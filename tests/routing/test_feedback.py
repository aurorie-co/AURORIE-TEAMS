#!/usr/bin/env python3
"""
Feedback Event test suite — v0.7 Adaptive Execution Runtime.
Tests build_feedback_event() pure function and JSONL store.
"""

from pathlib import Path
from lib.feedback import build_feedback_event, append_event, load_events


# ---------------------------------------------------------------------------
# Event Schema tests
# ---------------------------------------------------------------------------

def _test_build_feedback_event_initial():
    """
    F1: Build event for completed initial run.
    """
    event = build_feedback_event(
        task_id="task_abc",
        run_n=1,
        run_kind="initial",
        teams=["product", "backend"],
        graph_template="linear",
        final_status="completed",
        failed_nodes=[],
        resumed=False,
        milestone_id=None,
    )
    assert event["task_id"] == "task_abc"
    assert event["run_id"] == "task_abc_run_1"
    assert event["run_kind"] == "initial"
    assert event["teams"] == ["product", "backend"]
    assert event["graph_template"] == "linear"
    assert event["final_status"] == "completed"
    assert event["failed_nodes"] == []
    assert event["resumed"] is False
    assert event["milestone_id"] is None
    assert "timestamp" in event


def _test_build_feedback_event_resume():
    """
    F2: Build event for resumed run with resumed=true.
    """
    event = build_feedback_event(
        task_id="task_abc",
        run_n=2,
        run_kind="resume",
        teams=["product", "backend"],
        graph_template="linear",
        final_status="completed",
        failed_nodes=[],
        resumed=True,
        milestone_id="ms_xyz",
    )
    assert event["run_id"] == "task_abc_run_2"
    assert event["run_kind"] == "resume"
    assert event["resumed"] is True
    assert event["milestone_id"] == "ms_xyz"


def _test_build_feedback_event_partial_failed():
    """
    F3: Build event with failed_nodes populated.
    """
    event = build_feedback_event(
        task_id="task_def",
        run_n=1,
        run_kind="initial",
        teams=["backend", "frontend"],
        graph_template="flat",
        final_status="partial_failed",
        failed_nodes=["backend-1"],
        resumed=False,
        milestone_id=None,
    )
    assert event["final_status"] == "partial_failed"
    assert event["failed_nodes"] == ["backend-1"]
    assert event["graph_template"] == "flat"


# ---------------------------------------------------------------------------
# JSONL Store tests
# ---------------------------------------------------------------------------

def _test_append_and_load_jsonl():
    """
    F4: Append events to JSONL, load back, verify content and line count.
    """
    import json
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        history_path = tmp_path / "execution_history.jsonl"

        event1 = build_feedback_event(
            task_id="task_001", run_n=1, run_kind="initial",
            teams=["backend"], graph_template="linear",
            final_status="completed", failed_nodes=[], resumed=False,
        )
        event2 = build_feedback_event(
            task_id="task_002", run_n=1, run_kind="initial",
            teams=["frontend"], graph_template="flat",
            final_status="partial_failed", failed_nodes=["frontend-1"], resumed=False,
        )

        append_event(history_path, event1)
        append_event(history_path, event2)

        events = load_events(history_path)
        assert len(events) == 2
        assert events[0]["task_id"] == "task_001"
        assert events[1]["task_id"] == "task_002"
        assert events[1]["final_status"] == "partial_failed"

        # Verify raw lines are valid JSON
        with open(history_path) as f:
            lines = f.readlines()
        assert len(lines) == 2
        json.loads(lines[0])
        json.loads(lines[1])


def _test_load_events_empty():
    """
    F4b: Empty JSONL returns empty list.
    """
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        history_path = tmp_path / "empty.jsonl"
        history_path.write_text("")
        events = load_events(history_path)
        assert events == []


def _test_load_events_missing_file():
    """
    F4c: Missing JSONL file returns empty list (no exception).
    """
    events = load_events(Path("/nonexistent/path.jsonl"))
    assert events == []


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

TESTS = [
    ("build_feedback_event_initial", _test_build_feedback_event_initial),
    ("build_feedback_event_resume", _test_build_feedback_event_resume),
    ("build_feedback_event_partial_failed", _test_build_feedback_event_partial_failed),
    ("append_and_load_jsonl", _test_append_and_load_jsonl),
    ("load_events_empty", _test_load_events_empty),
    ("load_events_missing_file", _test_load_events_missing_file),
]


def main():
    failed = []
    for name, fn in TESTS:
        try:
            fn()
            print(f"  PASS {name}")
        except NotImplementedError as e:
            print(f"  FAIL {name}: NotImplementedError")
            failed.append(name)
        except Exception as e:
            print(f"  FAIL {name}: {e}")
            failed.append(name)
    print(f"\nResults: {len(TESTS) - len(failed)}/{len(TESTS)} passed, {len(failed)} failed")
    if failed:
        print(f"Failed: {failed}")
    return len(failed) == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
