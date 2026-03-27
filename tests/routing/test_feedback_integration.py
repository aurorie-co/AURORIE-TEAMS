#!/usr/bin/env python3
"""
Feedback Integration test suite — v0.7 Adaptive Execution Runtime.
Verifies orchestrator integration points without running the full agent.

These tests cover:
- Team bias affects adjusted_score (not raw)
- High-confidence (>= 0.8) teams get bias=1.0
- build_execution_graph stores graph_template in metadata
- Terminal state triggers feedback event write
- Non-terminal state does NOT trigger event write
- Resume path increments run_n correctly
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.feedback import (
    build_feedback_event,
    append_event,
    load_events,
    aggregate_team_stats,
    compute_team_bias,
    apply_team_bias,
    maybe_append_feedback_event,
)
from tests.routing.test_dispatch_policy import build_execution_graph


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _team(name, score=3, confidence="high"):
    return {"team": name, "score": score, "confidence": confidence}


# ---------------------------------------------------------------------------
# Test 1: team_bias_affects_adjusted_score
# ---------------------------------------------------------------------------

def _test_team_bias_affects_adjusted_score():
    """
    5 backend runs: 3 completed, 2 partial_failed
    -> success_rate = 3/5 = 0.6
    -> 0.6 <= 0.6 < 0.8 -> bias = 0.9 (MIN_SAMPLES=5 threshold met)
    -> adjusted_score = raw_score * 0.9 < raw_score
    """
    events = [
        build_feedback_event(
            task_id=f"t{i}", run_n=1, run_kind="initial",
            teams=["backend"], graph_template="linear",
            final_status=status,
            failed_nodes=[] if status == "completed" else ["backend-1"],
            resumed=False,
        )
        for i, status in enumerate([
            "completed", "completed", "completed",
            "partial_failed", "partial_failed",
        ])
    ]

    team_stats = aggregate_team_stats(events)
    team_bias = compute_team_bias(team_stats)

    assert team_stats["backend"]["runs"] == 5
    assert team_stats["backend"]["success_rate"] == 0.6
    assert team_bias["backend"] == 0.9  # 0.6 <= 0.6 < 0.8

    candidates = [{"team": "backend", "raw_score": 3, "confidence": "high"}]
    adjusted = apply_team_bias(candidates, team_bias, team_stats)

    assert adjusted[0]["adjusted_score"] == 2.7  # 3 * 0.9
    assert adjusted[0]["feedback_bias"] == 0.9
    assert adjusted[0]["raw_score"] == 3
    assert adjusted[0]["adjusted_score"] < adjusted[0]["raw_score"]


# ---------------------------------------------------------------------------
# Test 2: team_bias_preserves_high_confidence
# ---------------------------------------------------------------------------

def _test_team_bias_preserves_high_confidence():
    """
    Backend with 5 runs, 4 completed, 1 partial_failed
    -> success_rate = 0.8 -> bias = 1.0
    -> adjusted_score == raw_score
    """
    events = [
        build_feedback_event(
            task_id=f"t{i}", run_n=1, run_kind="initial",
            teams=["backend"], graph_template="linear",
            final_status=status,
            failed_nodes=[] if status == "completed" else ["backend-1"],
            resumed=False,
        )
        for i, status in enumerate([
            "completed", "completed", "completed", "completed", "partial_failed"
        ])
    ]

    team_stats = aggregate_team_stats(events)
    team_bias = compute_team_bias(team_stats)

    assert team_bias["backend"] == 1.0  # rate >= 0.8

    candidates = [{"team": "backend", "raw_score": 4, "confidence": "high"}]
    adjusted = apply_team_bias(candidates, team_bias, team_stats)

    assert adjusted[0]["adjusted_score"] == 4.0
    assert adjusted[0]["feedback_bias"] == 1.0


# ---------------------------------------------------------------------------
# Test 3: template_stored_in_graph_metadata
# ---------------------------------------------------------------------------

def _test_template_stored_in_graph_metadata():
    """
    build_execution_graph() returns dict with metadata.graph_template set.
    """
    teams = [_team("backend"), _team("frontend")]
    graph = build_execution_graph("task_test", teams)

    assert "metadata" in graph
    assert "graph_template" in graph["metadata"]
    # backend+frontend -> linear-pipeline
    assert graph["metadata"]["graph_template"] == "linear-pipeline"


def _test_template_stored_data_first():
    """data team -> data-first template."""
    teams = [_team("data")]
    graph = build_execution_graph("task_test2", teams)
    assert graph["metadata"]["graph_template"] == "data-first"


def _test_template_stored_research_branch():
    """research without product -> research-branch template."""
    teams = [_team("research"), _team("backend")]
    graph = build_execution_graph("task_test3", teams)
    assert graph["metadata"]["graph_template"] == "research-branch"


# ---------------------------------------------------------------------------
# Test 4: feedback_event_hook_writes_on_terminal
# ---------------------------------------------------------------------------

def _test_feedback_event_hook_writes_on_terminal():
    """
    Task reaching terminal state (completed) -> event written once.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        history_path = Path(tmp_dir) / "history.jsonl"

        task = {
            "task_id": "task_terminal",
            "status": "in_progress",
            "execution_graph": {
                "status": "completed",
                "metadata": {"graph_template": "linear-pipeline"},
                "nodes": [
                    {
                        "node_id": "backend-1",
                        "team": "backend",
                        "status": "done",
                        "depends_on": [],
                    },
                ],
                "edges": [],
                "waves": [["backend-1"]],
            },
        }

        run_written = {}

        # Write on first call
        maybe_append_feedback_event(
            history_path, task, "task_terminal_run_1", run_written, "initial"
        )

        events = load_events(history_path)
        assert len(events) == 1
        assert events[0]["task_id"] == "task_terminal"
        assert events[0]["run_id"] == "task_terminal_run_1"
        assert events[0]["run_kind"] == "initial"
        assert events[0]["final_status"] == "completed"
        assert events[0]["teams"] == ["backend"]


# ---------------------------------------------------------------------------
# Test 5: feedback_event_not_written_on_in_progress
# ---------------------------------------------------------------------------

def _test_feedback_event_not_written_on_in_progress():
    """
    Task still in_progress -> no event written.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        history_path = Path(tmp_dir) / "history.jsonl"

        task = {
            "task_id": "task_inprogress",
            "status": "in_progress",
            "execution_graph": {
                "status": "in_progress",
                "metadata": {},
                "nodes": [],
                "edges": [],
            },
        }

        run_written = {}

        maybe_append_feedback_event(
            history_path, task, "task_inprogress_run_1", run_written, "initial"
        )

        events = load_events(history_path)
        assert len(events) == 0


# ---------------------------------------------------------------------------
# Test 6: resume_increments_run_n
# ---------------------------------------------------------------------------

def _test_resume_increments_run_n():
    """
    Initial run sets run_n=1, resume run_n=2, run_kind=resume.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        history_path = Path(tmp_dir) / "history.jsonl"

        # Initial run
        initial_task = {
            "task_id": "task_resume",
            "status": "partial_failed",
            "resumed": False,
            "run_n": 1,
            "run_kind": "initial",
            "execution_graph": {
                "status": "partial_failed",
                "metadata": {"graph_template": "linear-pipeline"},
                "nodes": [
                    {"node_id": "backend-1", "team": "backend", "status": "failed", "depends_on": []},
                ],
                "edges": [],
                "waves": [["backend-1"]],
            },
        }

        run_written = {}

        maybe_append_feedback_event(
            history_path, initial_task, "task_resume_run_1", run_written, "initial"
        )

        # Resume run
        resume_task = {
            "task_id": "task_resume",
            "status": "completed",
            "resumed": True,
            "run_n": 2,
            "run_kind": "resume",
            "execution_graph": {
                "status": "completed",
                "metadata": {"graph_template": "linear-pipeline"},
                "nodes": [
                    {"node_id": "backend-1", "team": "backend", "status": "done", "depends_on": []},
                ],
                "edges": [],
                "waves": [["backend-1"]],
            },
        }

        maybe_append_feedback_event(
            history_path, resume_task, "task_resume_run_2", run_written, "resume"
        )

        events = load_events(history_path)
        assert len(events) == 2

        assert events[0]["run_id"] == "task_resume_run_1"
        assert events[0]["run_kind"] == "initial"
        assert events[0]["final_status"] == "partial_failed"

        assert events[1]["run_id"] == "task_resume_run_2"
        assert events[1]["run_kind"] == "resume"
        assert events[1]["final_status"] == "completed"
        assert events[1]["resumed"] is True


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

TESTS = [
    ("team_bias_affects_adjusted_score", _test_team_bias_affects_adjusted_score),
    ("team_bias_preserves_high_confidence", _test_team_bias_preserves_high_confidence),
    ("template_stored_in_graph_metadata", _test_template_stored_in_graph_metadata),
    ("template_stored_data_first", _test_template_stored_data_first),
    ("template_stored_research_branch", _test_template_stored_research_branch),
    ("feedback_event_hook_writes_on_terminal", _test_feedback_event_hook_writes_on_terminal),
    ("feedback_event_not_written_on_in_progress", _test_feedback_event_not_written_on_in_progress),
    ("resume_increments_run_n", _test_resume_increments_run_n),
]


def main():
    failed = []
    for name, fn in TESTS:
        try:
            fn()
            print(f"  PASS {name}")
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
