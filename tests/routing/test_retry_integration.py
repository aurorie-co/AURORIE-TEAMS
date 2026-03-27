#!/usr/bin/env python3
"""
Retry integration tests — simulates Step C retry flow (v0.8 Auto-Retry Policy).

Covers:
- maybe_retry_nodes resets eligible failed nodes (pending, retry_count incremented)
- maybe_retry_nodes ignores non-retryable and completed nodes
- Exhausted retry (count >= 1) is not retried
- Auto-retry disabled via flag prevents any retries
"""

import sys
sys.path.insert(0, "/Users/aurorie/workspace/aurorie/aurorie-teams")

from lib.retry import maybe_retry_nodes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _graph(*nodes):
    return {"nodes": list(nodes)}


def _node(node_id, status, retryable=True, retry_count=0):
    return {"node_id": node_id, "status": status, "retryable": retryable, "retry_count": retry_count}


# ---------------------------------------------------------------------------
# Test 1: maybe_retry_nodes_resets_eligible_failed_nodes
# ---------------------------------------------------------------------------

def test_maybe_retry_nodes_resets_eligible_failed_nodes():
    """
    3-node graph:
    - backend-1: failed, retryable=True, retry_count=0  -> retried (pending, count=1)
    - backend-2: failed, retryable=False, retry_count=0 -> unchanged (failed, count=0)
    - backend-3: completed, retryable=True, retry_count=0 -> unchanged (completed)
    """
    graph = _graph(
        _node("backend-1", "failed", retryable=True, retry_count=0),
        _node("backend-2", "failed", retryable=False, retry_count=0),
        _node("backend-3", "completed", retryable=True, retry_count=0),
    )

    updated, retried_node_ids = maybe_retry_nodes(graph, auto_retry_enabled=True)

    # backend-1: retried and reset
    assert updated["nodes"][0]["node_id"] == "backend-1"
    assert updated["nodes"][0]["status"] == "pending"
    assert updated["nodes"][0]["retry_count"] == 1

    # backend-2: not retryable, unchanged
    assert updated["nodes"][1]["node_id"] == "backend-2"
    assert updated["nodes"][1]["status"] == "failed"
    assert updated["nodes"][1]["retry_count"] == 0

    # backend-3: not failed, unchanged
    assert updated["nodes"][2]["node_id"] == "backend-3"
    assert updated["nodes"][2]["status"] == "completed"
    assert updated["nodes"][2]["retry_count"] == 0

    assert retried_node_ids == ["backend-1"]


# ---------------------------------------------------------------------------
# Test 2: maybe_retry_nodes_exhausted_retry_not_retried
# ---------------------------------------------------------------------------

def test_maybe_retry_nodes_exhausted_retry_not_retried():
    """
    Node has already been retried (retry_count=1) -> not retried again.
    """
    graph = _graph(
        _node("backend-1", "failed", retryable=True, retry_count=1),
    )

    updated, retried_node_ids = maybe_retry_nodes(graph, auto_retry_enabled=True)

    assert updated["nodes"][0]["status"] == "failed"
    assert updated["nodes"][0]["retry_count"] == 1  # unchanged
    assert retried_node_ids == []


# ---------------------------------------------------------------------------
# Test 3: auto_retry_disabled_no_retries
# ---------------------------------------------------------------------------

def test_auto_retry_disabled_no_retries():
    """
    auto_retry_enabled=False -> no nodes retried regardless of flags.
    """
    graph = _graph(
        _node("backend-1", "failed", retryable=True, retry_count=0),
    )

    updated, retried_node_ids = maybe_retry_nodes(graph, auto_retry_enabled=False)

    assert updated["nodes"][0]["status"] == "failed"
    assert updated["nodes"][0]["retry_count"] == 0
    assert retried_node_ids == []


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

TESTS = [
    ("test_maybe_retry_nodes_resets_eligible_failed_nodes", test_maybe_retry_nodes_resets_eligible_failed_nodes),
    ("test_maybe_retry_nodes_exhausted_retry_not_retried", test_maybe_retry_nodes_exhausted_retry_not_retried),
    ("test_auto_retry_disabled_no_retries", test_auto_retry_disabled_no_retries),
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
    total = len(TESTS)
    passed = total - len(failed)
    print(f"\nResults: {passed}/{total} passed")
    if failed:
        print(f"Failed: {failed}")
    return len(failed) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
