#!/usr/bin/env python3
"""
tests/routing/test_step_c_simulation.py

Deterministic Step C simulation — verifies runtime retry behavior end-to-end.

Covers:
- R6: retry picked up next wave (not same wave)
- R8: retry → success → graph.status = completed
- R9: --no-auto-retry → unrecoverable partial_failed

This is NOT a unit test of lib/retry.py (already covered by test_retry.py).
This simulates the ACTUAL Step C dispatch loop with real graph state transitions.
"""

import sys
sys.path.insert(0, "/Users/aurorie/workspace/aurorie/aurorie-teams")

from lib.retry import maybe_retry_nodes
from tests.routing.test_dispatch_policy import get_ready_nodes, advance_node


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _graph(*nodes, auto_retry_enabled=True):
    """Build a graph dict matching the orchestrator's execution_graph structure."""
    return {
        "metadata": {"auto_retry_enabled": auto_retry_enabled},
        "nodes": list(nodes),
        "edges": [],
        "status": "pending",
    }


def _node(node_id, status="pending", retryable=True, retry_count=0, depends_on=None):
    return {
        "node_id": node_id,
        "team": node_id.split("-")[0],
        "status": status,
        "retryable": retryable,
        "retry_count": retry_count,
        "depends_on": depends_on or [],
        "artifacts_in": [],
        "artifacts_out": [],
    }


def _dispatch_and_advance(graph, dispatch_results):
    """
    Simulate ONE wave dispatch:
    1. advance_node for each result
    2. call maybe_retry_nodes
    3. return (updated_graph, wave_log)
    """
    wave_log = []
    for node_id, result_status in dispatch_results:
        graph = advance_node(graph, node_id, result_status)
        wave_log.append(f"{node_id}→{result_status}")

    # Step C retry hook — runs after all nodes in this wave are advanced
    auto_retry = graph["metadata"].get("auto_retry_enabled", True)
    graph, retried_ids = maybe_retry_nodes(graph, auto_retry)

    # Override partial_failed → in_progress if retry fired (matches orchestrator Step C)
    if retried_ids:
        graph["status"] = "in_progress"

    return graph, wave_log, retried_ids


def _is_terminal(graph):
    return graph["status"] in ("completed", "partial_failed", "blocked")


def run_step_c(graph, dispatch_scenario_fn):
    """
    Run the Step C loop until terminal state.
    dispatch_scenario_fn(wave_count, graph) → list of (node_id, result_status)
    Returns (final_graph, wave_logs, retried_logs)
    """
    wave = 0
    wave_logs = []
    retried_logs = []

    while not _is_terminal(graph):
        wave += 1
        ready = get_ready_nodes(graph)

        if not ready:
            # All nodes are done/failed/blocked — check terminal
            if all(n["status"] in ("done", "failed", "blocked") for n in graph["nodes"]):
                # Set final status
                failed = [n for n in graph["nodes"] if n["status"] == "failed"]
                if failed:
                    graph["status"] = "partial_failed"
                else:
                    graph["status"] = "completed"
            break

        # Dispatch all ready nodes and get their simulated results
        results = dispatch_scenario_fn(wave, ready, graph)

        graph, wave_log, retried_ids = _dispatch_and_advance(graph, results)
        wave_logs.append(f"Wave {wave}: {', '.join(wave_log)}")
        if retried_ids:
            for nid in retried_ids:
                node = next(n for n in graph["nodes"] if n["node_id"] == nid)
                before = node["retry_count"] - 1
                retried_logs.append(f"  → Auto-retry: {nid} (retry_count: {before} → {node['retry_count']}) reset to pending for next wave")

        # After retry hook, if graph is still in_progress but no ready nodes, loop ends
        if graph["status"] == "in_progress":
            # Check if anything is still pending (retried nodes)
            still_pending = [n for n in graph["nodes"] if n["status"] == "pending"]
            if not still_pending and not ready:
                # All done after retry succeeded — no more waves needed
                all_done = all(n["status"] == "done" for n in graph["nodes"])
                if all_done:
                    graph["status"] = "completed"
                else:
                    # Some nodes still not done — keep going (another wave)
                    pass

    return graph, wave_logs, retried_logs


# ---------------------------------------------------------------------------
# Test 1: R6 — retry picked up next wave
# ---------------------------------------------------------------------------

def test_r6_retry_picked_up_next_wave():
    """
    R6: two nodes in parallel (flat graph). Wave 1: backend fails, product succeeds.
    Retry resets backend to pending → Wave 2: backend dispatched again → succeeds.

    Key R6 assertion: retry fires BETWEEN waves, not within the same wave.
    Backend is NOT dispatched twice simultaneously in wave 1.
    """
    dispatch_log = []

    def scenario(wave, ready, graph):
        dispatch_log.append((wave, list(ready)))
        # Wave 1: both product-1 and backend-1 are ready simultaneously (flat, no deps)
        #   → product succeeds, backend fails (retryable)
        # Wave 2: backend-1 was retried to pending → picked up and succeeds
        if wave == 1:
            return [("product-1", "done"), ("backend-1", "failed")]
        elif wave == 2:
            return [("backend-1", "done")]
        return []

    graph = _graph(
        _node("product-1", "pending", depends_on=[]),
        _node("backend-1", "pending", retryable=True, depends_on=[]),
        auto_retry_enabled=True,
    )

    final, waves, retries = run_step_c(graph, scenario)

    # Assertions
    assert final["status"] == "completed", f"Expected completed, got {final['status']}"
    backend_node = next(n for n in final["nodes"] if n["node_id"] == "backend-1")
    assert backend_node["retry_count"] == 1, f"Expected retry_count=1, got {backend_node['retry_count']}"
    assert backend_node["status"] == "done"

    # R6: exactly 2 waves. backend dispatched in wave 1 (failed), retried, dispatched in wave 2
    assert len(waves) == 2, f"Expected 2 waves, got {len(waves)}: {waves}"

    wave1_ready = [r for (w, r) in dispatch_log if w == 1][0]
    wave2_ready = [r for (w, r) in dispatch_log if w == 2][0]
    # Wave 1: both ready (flat graph), both dispatched
    assert wave1_ready == ["product-1", "backend-1"], f"Wave 1 ready: {wave1_ready}"
    # Wave 2: only backend-1 (retried to pending, product already done)
    assert wave2_ready == ["backend-1"], f"Wave 2 ready: {wave2_ready}"
    # Exactly 1 retry fired (backend-1)
    assert len(retries) == 1, f"Expected 1 retry, got {len(retries)}"

    print("  PASS test_r6_retry_picked_up_next_wave")
    for w in waves:
        print(f"    {w}")
    for r in retries:
        print(f"  {r}")


# ---------------------------------------------------------------------------
# Test 2: R8 — retry → success → graph.status = completed
# ---------------------------------------------------------------------------

def test_r8_retry_affects_graph_status():
    """
    R8: single node fails → retried → succeeds on retry → graph = completed.
    Previously this would leave graph in partial_failed.
    """
    dispatch_log = []

    def scenario(wave, ready, graph):
        dispatch_log.append((wave, list(ready)))
        if wave == 1:
            return [("backend-1", "failed")]
        elif wave == 2:
            return [("backend-1", "done")]
        return []

    graph = _graph(
        _node("backend-1", "pending", retryable=True, depends_on=[]),
        auto_retry_enabled=True,
    )

    final, waves, retries = run_step_c(graph, scenario)

    assert final["status"] == "completed", f"Expected completed, got {final['status']}"
    backend_node = next(n for n in final["nodes"] if n["node_id"] == "backend-1")
    assert backend_node["retry_count"] == 1, f"Expected retry_count=1, got {backend_node['retry_count']}"

    print("  PASS test_r8_retry_affects_graph_status")
    print(f"  Waves: {len(waves)}")
    for w in waves:
        print(f"    {w}")
    for r in retries:
        print(r)


# ---------------------------------------------------------------------------
# Test 3: R9 — no-auto-retry → partial_failed
# ---------------------------------------------------------------------------

def test_r9_no_auto_retry_flag_graph_status():
    """
    R9: auto_retry_enabled=False → fail → unrecoverable → graph.status = partial_failed.
    Metadata flag disables retry regardless of node-level retryable.
    """
    dispatch_log = []

    def scenario(wave, ready, graph):
        dispatch_log.append((wave, list(ready)))
        if wave == 1:
            return [("backend-1", "failed")]
        return []

    # auto_retry_enabled = False in metadata
    graph = _graph(
        _node("backend-1", "pending", retryable=True, depends_on=[]),
        auto_retry_enabled=False,
    )

    final, waves, retries = run_step_c(graph, scenario)

    assert final["status"] == "partial_failed", f"Expected partial_failed, got {final['status']}"
    backend_node = next(n for n in final["nodes"] if n["node_id"] == "backend-1")
    assert backend_node["retry_count"] == 0, f"Expected retry_count=0 (not retried), got {backend_node['retry_count']}"
    assert backend_node["status"] == "failed"
    assert len(retries) == 0, f"No retries should fire when auto_retry_enabled=False: {retries}"

    print("  PASS test_r9_no_auto_retry_flag_graph_status")
    print(f"  Waves: {len(waves)}")
    for w in waves:
        print(f"    {w}")
    assert len(retries) == 0


# ---------------------------------------------------------------------------
# Test 4: R3 — retry exhausted → no second retry
# ---------------------------------------------------------------------------

def test_r3_retry_exhausted_no_second_retry():
    """
    R3: node fails → retried (count=1) → fails again → no second retry.
    retry_count hard limit: exactly one retry per node.
    """
    dispatch_log = []

    def scenario(wave, ready, graph):
        dispatch_log.append((wave, list(ready)))
        if wave == 1:
            return [("backend-1", "failed")]
        elif wave == 2:
            return [("backend-1", "failed")]  # retry fails
        return []

    graph = _graph(
        _node("backend-1", "pending", retryable=True, depends_on=[]),
        auto_retry_enabled=True,
    )

    final, waves, retries = run_step_c(graph, scenario)

    # After wave 2: node failed again, retry_count=1 (exhausted), no more retries
    # Loop should detect no ready nodes and set terminal partial_failed
    assert final["status"] == "partial_failed", f"Expected partial_failed, got {final['status']}"
    backend_node = next(n for n in final["nodes"] if n["node_id"] == "backend-1")
    assert backend_node["retry_count"] == 1, f"Expected retry_count=1 (not incremented again), got {backend_node['retry_count']}"
    assert backend_node["status"] == "failed"
    # Only ONE retry should have fired
    assert len(retries) == 1, f"Expected exactly 1 retry, got {len(retries)}"

    print("  PASS test_r3_retry_exhausted_no_second_retry")
    for w in waves:
        print(f"    {w}")
    for r in retries:
        print(r)


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

TESTS = [
    ("test_r6_retry_picked_up_next_wave", test_r6_retry_picked_up_next_wave),
    ("test_r8_retry_affects_graph_status", test_r8_retry_affects_graph_status),
    ("test_r9_no_auto_retry_flag_graph_status", test_r9_no_auto_retry_flag_graph_status),
    ("test_r3_retry_exhausted_no_second_retry", test_r3_retry_exhausted_no_second_retry),
]


def main():
    failed = []
    for name, fn in TESTS:
        try:
            fn()
        except AssertionError as e:
            print(f"  FAIL {name}: {e}")
            failed.append(name)
        except Exception as e:
            print(f"  ERROR {name}: {e}")
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
