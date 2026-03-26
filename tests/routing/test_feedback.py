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
# Aggregation tests
# ---------------------------------------------------------------------------

def _make_event(task_id, run_kind, final_status, teams):
    return build_feedback_event(
        task_id=task_id,
        run_n=1 if run_kind == "initial" else 2,
        run_kind=run_kind,
        teams=teams,
        graph_template="linear",
        final_status=final_status,
        failed_nodes=[],
        resumed=(run_kind == "resume"),
    )


def _test_aggregate_team_stats_empty():
    """
    F6: Empty event list -> empty stats.
    """
    from lib.feedback import aggregate_team_stats
    stats = aggregate_team_stats([])
    assert stats == {}


def _test_aggregate_team_stats_single_team():
    """
    F7: 3 completed + 2 partial_failed -> success_rate=0.6.
    Only run_kind='initial' counts.
    """
    from lib.feedback import aggregate_team_stats
    events = [
        _make_event("t1", "initial", "completed", ["backend"]),
        _make_event("t2", "initial", "completed", ["backend"]),
        _make_event("t3", "initial", "completed", ["backend"]),
        _make_event("t4", "initial", "partial_failed", ["backend"]),
        _make_event("t5", "initial", "partial_failed", ["backend"]),
        _make_event("t6", "resume", "completed", ["backend"]),   # excluded
    ]
    stats = aggregate_team_stats(events)
    assert "backend" in stats
    assert stats["backend"]["runs"] == 5        # only initial counted
    assert stats["backend"]["successes"] == 3
    assert stats["backend"]["success_rate"] == 0.6


def _test_aggregate_team_stats_multiple_teams():
    """
    F8: 2 teams -> correct per-team stats.
    """
    from lib.feedback import aggregate_team_stats
    events = [
        _make_event("t1", "initial", "completed", ["backend", "frontend"]),
        _make_event("t2", "initial", "partial_failed", ["backend"]),
        _make_event("t3", "initial", "completed", ["frontend"]),
        _make_event("t4", "initial", "blocked", ["frontend"]),
    ]
    stats = aggregate_team_stats(events)
    assert stats["backend"]["runs"] == 2
    assert stats["backend"]["success_rate"] == 0.5
    assert stats["frontend"]["runs"] == 3
    assert stats["frontend"]["success_rate"] == 2/3  # 2 completed, 1 blocked


def _test_aggregate_team_stats_resume_excluded():
    """
    F5: resume runs are excluded from stats entirely.
    """
    from lib.feedback import aggregate_team_stats
    events = [
        _make_event("t1", "initial", "partial_failed", ["backend"]),
        _make_event("t2", "resume", "completed", ["backend"]),   # must NOT count
    ]
    stats = aggregate_team_stats(events)
    assert stats["backend"]["runs"] == 1
    assert stats["backend"]["successes"] == 0


def _make_event_tpl(task_id, run_kind, final_status, graph_template):
    return build_feedback_event(
        task_id=task_id,
        run_n=1 if run_kind == "initial" else 2,
        run_kind=run_kind,
        teams=["backend"],
        graph_template=graph_template,
        final_status=final_status,
        failed_nodes=[],
        resumed=(run_kind == "resume"),
    )


def _test_aggregate_template_stats():
    """
    G1: 5 linear + 2 flat runs -> correct per-template stats.
    Only run_kind='initial' counted.
    """
    from lib.feedback import aggregate_template_stats
    events = [
        _make_event_tpl("t1", "initial", "completed", "linear"),
        _make_event_tpl("t2", "initial", "completed", "linear"),
        _make_event_tpl("t3", "initial", "completed", "linear"),
        _make_event_tpl("t4", "initial", "partial_failed", "linear"),
        _make_event_tpl("t5", "initial", "partial_failed", "linear"),
        _make_event_tpl("t6", "initial", "completed", "flat"),
        _make_event_tpl("t7", "initial", "partial_failed", "flat"),
        _make_event_tpl("t8", "resume", "completed", "linear"),   # excluded
    ]
    stats = aggregate_template_stats(events)
    assert stats["linear"]["runs"] == 5   # t8 excluded (resume)
    assert stats["linear"]["success_rate"] == 3/5
    assert stats["flat"]["runs"] == 2
    assert stats["flat"]["success_rate"] == 0.5


# ---------------------------------------------------------------------------
# Bias Computation tests
# ---------------------------------------------------------------------------

def _test_feedback_multiplier_insufficient_runs():
    """
    F9: runs < 5 -> returns 1.0 (no bias applied).
    """
    from lib.feedback import feedback_multiplier
    assert feedback_multiplier(0.3, 3) == 1.0
    assert feedback_multiplier(0.9, 4) == 1.0


def _test_feedback_multiplier_high_rate():
    """
    F10: success_rate >= 0.8 -> returns 1.0.
    """
    from lib.feedback import feedback_multiplier
    assert feedback_multiplier(0.8, 10) == 1.0
    assert feedback_multiplier(0.95, 20) == 1.0


def _test_feedback_multiplier_medium_rate():
    """
    F11: 0.6 <= rate < 0.8 -> returns 0.9.
    """
    from lib.feedback import feedback_multiplier
    assert feedback_multiplier(0.6, 10) == 0.9
    assert feedback_multiplier(0.7, 15) == 0.9
    assert feedback_multiplier(0.79, 8) == 0.9


def _test_feedback_multiplier_low_rate():
    """
    F12: 0.4 <= rate < 0.6 -> returns 0.75.
    """
    from lib.feedback import feedback_multiplier
    assert feedback_multiplier(0.4, 10) == 0.75
    assert feedback_multiplier(0.5, 7) == 0.75


def _test_feedback_multiplier_very_low_rate():
    """
    F13: rate < 0.4 -> returns 0.6.
    """
    from lib.feedback import feedback_multiplier
    assert feedback_multiplier(0.3, 10) == 0.6
    assert feedback_multiplier(0.0, 8) == 0.6


def _test_compute_team_bias():
    """
    F9-F13: compute_team_bias applies multiplier per team.
    """
    from lib.feedback import compute_team_bias
    stats = {
        "backend":  {"runs": 12, "success_rate": 0.65},  # 0.6 <= 0.65 < 0.8 -> 0.9
        "frontend": {"runs": 20, "success_rate": 0.85},  # >= 0.8 -> 1.0
        "product":  {"runs": 3,  "success_rate": 0.33},  # runs < 5 -> 1.0
    }
    bias = compute_team_bias(stats)
    assert bias["backend"] == 0.9
    assert bias["frontend"] == 1.0
    assert bias["product"] == 1.0


def _test_compute_template_bias():
    """
    G2: compute_template_bias applies multiplier per template.
    """
    from lib.feedback import compute_template_bias
    stats = {
        "linear":     {"runs": 8,  "success_rate": 0.75},
        "data-first": {"runs": 15, "success_rate": 0.53},
        "flat":       {"runs": 3,  "success_rate": 0.33},  # insufficient
    }
    bias = compute_template_bias(stats)
    assert bias["linear"] == 0.9          # 0.6 <= 0.75 < 0.8
    assert bias["data-first"] == 0.75     # 0.4 <= 0.53 < 0.6
    assert bias["flat"] == 1.0            # runs < 5


# ---------------------------------------------------------------------------
# Apply to Routing tests
# ---------------------------------------------------------------------------

def _test_apply_team_bias_reduces_score():
    """
    F14: Team with low success_rate -> adjusted_score < raw_score.
    """
    from lib.feedback import apply_team_bias
    bias = {"backend": 0.9}
    candidates = [
        {"team": "backend", "raw_score": 3, "confidence": "high"},
    ]
    adjusted = apply_team_bias(candidates, bias)
    assert adjusted[0]["adjusted_score"] == 2.7
    assert adjusted[0]["feedback_bias"] == 0.9


def _test_apply_team_bias_no_bias_when_insufficient():
    """
    F15: runs < 5 -> feedback_bias=1.0, adjusted_score = raw_score.
    """
    from lib.feedback import apply_team_bias
    bias = {"backend": 1.0}
    candidates = [
        {"team": "backend", "raw_score": 3, "confidence": "high"},
    ]
    adjusted = apply_team_bias(candidates, bias)
    assert adjusted[0]["adjusted_score"] == 3.0
    assert adjusted[0]["feedback_bias"] == 1.0


def _test_apply_team_bias_high_rate_no_change():
    """
    F16: success_rate >= 0.8 -> adjusted_score = raw_score.
    """
    from lib.feedback import apply_team_bias
    bias = {"frontend": 1.0}
    candidates = [
        {"team": "frontend", "raw_score": 4, "confidence": "high"},
    ]
    adjusted = apply_team_bias(candidates, bias)
    assert adjusted[0]["adjusted_score"] == 4.0


def _test_apply_team_bias_includes_stats():
    """
    F17b: adjusted team includes runs + success_rate for debug output.
    """
    from lib.feedback import apply_team_bias
    team_stats = {"backend": {"runs": 12, "success_rate": 0.58, "successes": 7}}
    bias = {"backend": 0.9}
    candidates = [{"team": "backend", "raw_score": 3, "confidence": "high"}]
    adjusted = apply_team_bias(candidates, bias, team_stats)
    assert adjusted[0]["runs"] == 12
    assert adjusted[0]["success_rate"] == 0.58
    assert adjusted[0]["feedback_bias"] == 0.9
    assert adjusted[0]["adjusted_score"] == 2.7


def _test_apply_template_bias_multiple_candidates():
    """
    G3: Multiple templates available -> bias applied to each.
    """
    from lib.feedback import apply_template_bias
    bias = {"linear": 0.9, "flat": 1.0}
    candidates = ["linear", "flat"]
    adjusted = apply_template_bias(candidates, bias)
    assert adjusted["linear"]["feedback_bias"] == 0.9
    assert adjusted["flat"]["feedback_bias"] == 1.0


def _test_apply_template_bias_insufficient_data():
    """
    G3b: runs < 5 -> no bias applied.
    """
    from lib.feedback import apply_template_bias
    bias = {"experimental": 1.0}
    candidates = ["experimental"]
    adjusted = apply_template_bias(candidates, bias)
    assert adjusted["experimental"]["feedback_bias"] == 1.0


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
    ("aggregate_team_stats_empty", _test_aggregate_team_stats_empty),
    ("aggregate_team_stats_single_team", _test_aggregate_team_stats_single_team),
    ("aggregate_team_stats_multiple_teams", _test_aggregate_team_stats_multiple_teams),
    ("aggregate_team_stats_resume_excluded", _test_aggregate_team_stats_resume_excluded),
    ("aggregate_template_stats", _test_aggregate_template_stats),
    ("feedback_multiplier_insufficient_runs", _test_feedback_multiplier_insufficient_runs),
    ("feedback_multiplier_high_rate", _test_feedback_multiplier_high_rate),
    ("feedback_multiplier_medium_rate", _test_feedback_multiplier_medium_rate),
    ("feedback_multiplier_low_rate", _test_feedback_multiplier_low_rate),
    ("feedback_multiplier_very_low_rate", _test_feedback_multiplier_very_low_rate),
    ("compute_team_bias", _test_compute_team_bias),
    ("compute_template_bias", _test_compute_template_bias),
    ("apply_team_bias_reduces_score", _test_apply_team_bias_reduces_score),
    ("apply_team_bias_no_bias_when_insufficient", _test_apply_team_bias_no_bias_when_insufficient),
    ("apply_team_bias_high_rate_no_change", _test_apply_team_bias_high_rate_no_change),
    ("apply_team_bias_includes_stats", _test_apply_team_bias_includes_stats),
    ("apply_template_bias_multiple_candidates", _test_apply_template_bias_multiple_candidates),
    ("apply_template_bias_insufficient_data", _test_apply_template_bias_insufficient_data),
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
