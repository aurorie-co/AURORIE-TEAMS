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

TESTS = [
    ("build_execution_graph_has_retryable_field", _test_build_execution_graph_has_retryable_field),
    ("build_execution_graph_retryable_all_templates", _test_build_execution_graph_retryable_all_templates),
    ("check_retry_eligible_all_true", _test_check_retry_eligible_all_true),
    ("check_retry_eligible_not_retryable", _test_check_retry_eligible_not_retryable),
    ("check_retry_eligible_count_exhausted", _test_check_retry_eligible_count_exhausted),
    ("check_retry_eligible_not_failed", _test_check_retry_eligible_not_failed),
    ("check_retry_eligible_auto_retry_disabled", _test_check_retry_eligible_auto_retry_disabled),
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