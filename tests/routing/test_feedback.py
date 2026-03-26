#!/usr/bin/env python3
"""
Feedback Event test suite — v0.7 Adaptive Execution Runtime.
Tests build_feedback_event() pure function.
"""

from lib.feedback import build_feedback_event


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
# Test runner
# ---------------------------------------------------------------------------

TESTS = [
    ("build_feedback_event_initial", _test_build_feedback_event_initial),
    ("build_feedback_event_resume", _test_build_feedback_event_resume),
    ("build_feedback_event_partial_failed", _test_build_feedback_event_partial_failed),
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
