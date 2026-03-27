#!/usr/bin/env python3
"""tests/routing/test_retry.py — Auto-retry test suite"""

def _test_build_execution_graph_has_retryable_field():
    from tests.routing.test_dispatch_policy import build_execution_graph
    teams = [{"team": "backend"}, {"team": "frontend"}]
    graph = build_execution_graph("task_retry_test", teams)
    for node in graph["nodes"]:
        assert "retryable" in node, f"node {node['node_id']} missing retryable"
        assert "retry_count" in node, f"node {node['node_id']} missing retry_count"
        assert node["retryable"] is True
        assert node["retry_count"] == 0

def _test_build_execution_graph_retryable_all_templates():
    from tests.routing.test_dispatch_policy import build_execution_graph
    templates = [
        [{"team": "data"}],
        [{"team": "research"}, {"team": "backend"}],
        [{"team": "product"}, {"team": "backend"}],
        [{"team": "backend"}, {"team": "frontend"}],
    ]
    for teams in templates:
        graph = build_execution_graph(f"task_{id(teams)}", teams)
        for node in graph["nodes"]:
            assert node["retryable"] is True
            assert node["retry_count"] == 0

def _test_check_retry_eligible_all_true():
    from lib.retry import check_retry_eligible
    node = {"status": "failed", "retryable": True, "retry_count": 0}
    eligible, reason = check_retry_eligible(node, auto_retry_enabled=True)
    assert eligible is True

def _test_check_retry_eligible_not_retryable():
    from lib.retry import check_retry_eligible
    node = {"status": "failed", "retryable": False, "retry_count": 0}
    eligible, reason = check_retry_eligible(node, auto_retry_enabled=True)
    assert eligible is False
    assert "not retryable" in reason

def _test_check_retry_eligible_count_exhausted():
    from lib.retry import check_retry_eligible
    node = {"status": "failed", "retryable": True, "retry_count": 1}
    eligible, reason = check_retry_eligible(node, auto_retry_enabled=True)
    assert eligible is False
    assert "exhausted" in reason.lower()

def _test_check_retry_eligible_not_failed():
    from lib.retry import check_retry_eligible
    node = {"status": "blocked", "retryable": True, "retry_count": 0}
    eligible, reason = check_retry_eligible(node, auto_retry_enabled=True)
    assert eligible is False
    assert "not in failed" in reason.lower()

def _test_check_retry_eligible_auto_retry_disabled():
    from lib.retry import check_retry_eligible
    node = {"status": "failed", "retryable": True, "retry_count": 0}
    eligible, reason = check_retry_eligible(node, auto_retry_enabled=False)
    assert eligible is False
    assert "disabled" in reason.lower()

def _test_maybe_retry_nodes_resets_eligible():
    """R6: failed + retryable + count=0 → node reset to pending, count=1"""
    from lib.retry import maybe_retry_nodes
    graph = {
        "nodes": [
            {"node_id": "backend-1", "team": "backend", "status": "failed",
             "retryable": True, "retry_count": 0},
        ],
        "edges": [],
        "status": "partial_failed",
    }
    updated, retried = maybe_retry_nodes(graph, auto_retry_enabled=True)
    assert retried == ["backend-1"]
    assert updated["nodes"][0]["status"] == "pending"
    assert updated["nodes"][0]["retry_count"] == 1

def _test_maybe_retry_nodes_ignores_non_retryable():
    """R2/R7: failed + retryable=False → not retried"""
    from lib.retry import maybe_retry_nodes
    graph = {
        "nodes": [
            {"node_id": "backend-1", "team": "backend", "status": "failed",
             "retryable": False, "retry_count": 0},
        ],
        "edges": [],
        "status": "partial_failed",
    }
    updated, retried = maybe_retry_nodes(graph, auto_retry_enabled=True)
    assert retried == []
    assert updated["nodes"][0]["status"] == "failed"

def _test_maybe_retry_nodes_no_second_retry():
    """R3: failed + count=1 → not retried again"""
    from lib.retry import maybe_retry_nodes
    graph = {
        "nodes": [
            {"node_id": "backend-1", "team": "backend", "status": "failed",
             "retryable": True, "retry_count": 1},
        ],
        "edges": [],
        "status": "partial_failed",
    }
    updated, retried = maybe_retry_nodes(graph, auto_retry_enabled=True)
    assert retried == []
    assert updated["nodes"][0]["status"] == "failed"

def _test_maybe_retry_nodes_mixed():
    """R7: 3 nodes, only the retryable one gets reset"""
    from lib.retry import maybe_retry_nodes
    graph = {
        "nodes": [
            {"node_id": "backend-1", "team": "backend", "status": "failed",
             "retryable": True, "retry_count": 0},
            {"node_id": "frontend-1", "team": "frontend", "status": "failed",
             "retryable": False, "retry_count": 0},
            {"node_id": "product-1", "team": "product", "status": "done",
             "retryable": True, "retry_count": 0},
        ],
        "edges": [],
        "status": "partial_failed",
    }
    updated, retried = maybe_retry_nodes(graph, auto_retry_enabled=True)
    assert retried == ["backend-1"]
    assert updated["nodes"][0]["status"] == "pending"
    assert updated["nodes"][0]["retry_count"] == 1
    assert updated["nodes"][1]["status"] == "failed"
    assert updated["nodes"][2]["status"] == "done"

def _test_maybe_retry_nodes_disabled():
    """R5: auto_retry_enabled=False → nothing retried"""
    from lib.retry import maybe_retry_nodes
    graph = {
        "nodes": [
            {"node_id": "backend-1", "team": "backend", "status": "failed",
             "retryable": True, "retry_count": 0},
        ],
        "edges": [],
        "status": "partial_failed",
    }
    updated, retried = maybe_retry_nodes(graph, auto_retry_enabled=False)
    assert retried == []
    assert updated["nodes"][0]["status"] == "failed"

def _test_all_done_after_retry_completed():
    """R11: after retry resets node to pending, re-dispatch succeeds → graph = completed"""
    from lib.retry import maybe_retry_nodes
    graph = {
        "nodes": [
            {"node_id": "backend-1", "team": "backend", "status": "failed",
             "retryable": True, "retry_count": 0},
            {"node_id": "frontend-1", "team": "frontend", "status": "done",
             "retryable": True, "retry_count": 0},
        ],
        "status": "partial_failed",
    }
    updated, retried = maybe_retry_nodes(graph, auto_retry_enabled=True)
    assert retried == ["backend-1"]
    assert updated["nodes"][0]["status"] == "pending"
    assert updated["nodes"][0]["retry_count"] == 1
    # Simulate re-dispatch succeeding
    updated["nodes"][0]["status"] = "done"
    all_done = all(n["status"] == "done" for n in updated["nodes"])
    assert all_done is True
    # Orchestrator sets graph.status = "completed"


def _test_unrecoverable_failed_partial():
    """R12: node failed + not retryable → stays failed → partial_failed"""
    from lib.retry import maybe_retry_nodes
    graph = {
        "nodes": [
            {"node_id": "backend-1", "team": "backend", "status": "failed",
             "retryable": False, "retry_count": 0},
        ],
        "status": "partial_failed",
    }
    updated, retried = maybe_retry_nodes(graph, auto_retry_enabled=True)
    assert retried == []
    assert updated["nodes"][0]["status"] == "failed"
    # Orchestrator sets graph.status = "partial_failed"

TESTS = [
    ("build_execution_graph_has_retryable_field", _test_build_execution_graph_has_retryable_field),
    ("build_execution_graph_retryable_all_templates", _test_build_execution_graph_retryable_all_templates),
    ("check_retry_eligible_all_true", _test_check_retry_eligible_all_true),
    ("check_retry_eligible_not_retryable", _test_check_retry_eligible_not_retryable),
    ("check_retry_eligible_count_exhausted", _test_check_retry_eligible_count_exhausted),
    ("check_retry_eligible_not_failed", _test_check_retry_eligible_not_failed),
    ("check_retry_eligible_auto_retry_disabled", _test_check_retry_eligible_auto_retry_disabled),
    ("maybe_retry_nodes_resets_eligible", _test_maybe_retry_nodes_resets_eligible),
    ("maybe_retry_nodes_ignores_non_retryable", _test_maybe_retry_nodes_ignores_non_retryable),
    ("maybe_retry_nodes_no_second_retry", _test_maybe_retry_nodes_no_second_retry),
    ("maybe_retry_nodes_mixed", _test_maybe_retry_nodes_mixed),
    ("maybe_retry_nodes_disabled", _test_maybe_retry_nodes_disabled),
    ("all_done_after_retry_completed", _test_all_done_after_retry_completed),
    ("unrecoverable_failed_partial", _test_unrecoverable_failed_partial),
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
    print(f"\nResults: {len(TESTS) - len(failed)}/{len(TESTS)} passed")
    return len(failed) == 0

if __name__ == "__main__":
    main()