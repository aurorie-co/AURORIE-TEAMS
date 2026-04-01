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
    Simulate ONE wave dispatch (v0.8 baseline + v0.9 verification):

    dispatch_results entries (node_id, exec_status, verify_exit_code_or_None):
      - exec_status: "done" or "failed" from agent execution
      - verify_exit_code_or_None:
          None          → no verification_command on this node → done immediately
          0             → verification passed → done
          non-zero int  → verification failed → node becomes failed

    After advancing all nodes, call maybe_retry_nodes (same as v0.8).
    """
    wave_log = []
    for entry in dispatch_results:
        if len(entry) == 2:
            node_id, exec_status = entry
            verify_exit = None
        else:
            node_id, exec_status, verify_exit = entry

        # v0.9 verification gate: only run if execution reported success
        if exec_status == "done":
            if verify_exit is None:
                # No verification_command → done (v0.8 behavior)
                final_status = "done"
            elif verify_exit == 0:
                # Verification passed → done
                final_status = "done"
            else:
                # Verification failed → node becomes failed
                final_status = "failed"
        else:
            # Execution failure → no verification runs, normal failure path
            final_status = "failed"

        graph = advance_node(graph, node_id, final_status)
        wave_log.append(f"{node_id}:exec={exec_status}→{final_status}")

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
# v0.9 — Verification tests
# ---------------------------------------------------------------------------

def test_v9_no_verification_command_v0_8_behavior():
    """
    V9-1: node has no verification_command → execution success → done immediately.
    v0.8 behavior is unchanged when no verification is declared.
    """
    dispatch_log = []

    def scenario(wave, ready, graph):
        if wave == 1:
            return [("backend-1", "done")]   # 2-tuple: no verification_command
        return []

    graph = _graph(
        _node("backend-1", "pending", depends_on=[]),
        auto_retry_enabled=True,
    )
    # Node has no verification_command

    final, waves, retries = run_step_c(graph, scenario)
    backend_node = next(n for n in final["nodes"] if n["node_id"] == "backend-1")

    assert final["status"] == "completed"
    assert backend_node["status"] == "done"
    assert len(retries) == 0
    assert len(waves) == 1

    print("  PASS test_v9_no_verification_command_v0_8_behavior")
    for w in waves:
        print(f"    {w}")


def test_v9_verification_success_exit_0():
    """
    V9-2: execution reports success + verification exit 0 → node = done.
    """
    def scenario(wave, ready, graph):
        if wave == 1:
            # 3-tuple: exec_status="done", verify_exit=0 (success)
            return [("backend-1", "done", 0)]
        return []

    graph = _graph(
        _node("backend-1", "pending", depends_on=[]),
        auto_retry_enabled=True,
    )
    graph["nodes"][0]["verification_command"] = "python3 tests/routing/test_routing_cases.py"

    final, waves, retries = run_step_c(graph, scenario)
    backend_node = next(n for n in final["nodes"] if n["node_id"] == "backend-1")

    assert final["status"] == "completed"
    assert backend_node["status"] == "done"

    print("  PASS test_v9_verification_success_exit_0")
    for w in waves:
        print(f"    {w}")


def test_v9_verification_failure_exit_nonzero():
    """
    V9-3: execution reports success + verification exits non-zero → node = failed.
    No retry → graph = partial_failed.
    """
    def scenario(wave, ready, graph):
        if wave == 1:
            # 3-tuple: exec_status="done", verify_exit=1 (failure)
            return [("backend-1", "done", 1)]
        return []

    graph = _graph(
        _node("backend-1", "pending", retryable=False, depends_on=[]),
        auto_retry_enabled=True,
    )
    graph["nodes"][0]["verification_command"] = "python3 tests/routing/test_routing_cases.py"

    final, waves, retries = run_step_c(graph, scenario)
    backend_node = next(n for n in final["nodes"] if n["node_id"] == "backend-1")

    assert final["status"] == "partial_failed"
    assert backend_node["status"] == "failed"
    assert len(retries) == 0  # not retryable

    print("  PASS test_v9_verification_failure_exit_nonzero")
    for w in waves:
        print(f"    {w}")


def test_v9_verification_fail_retryable_retry_once():
    """
    V9-4: verification fails → node=failed (retryable, count<1) → auto-retry fires once.
    Retry succeeds → graph = completed.
    """
    def scenario(wave, ready, graph):
        if wave == 1:
            return [("backend-1", "done", 1)]   # first attempt: verification fails
        elif wave == 2:
            return [("backend-1", "done", 0)]   # retry: verification passes
        return []

    graph = _graph(
        _node("backend-1", "pending", retryable=True, depends_on=[]),
        auto_retry_enabled=True,
    )
    graph["nodes"][0]["verification_command"] = "python3 tests/routing/test_routing_cases.py"

    final, waves, retries = run_step_c(graph, scenario)
    backend_node = next(n for n in final["nodes"] if n["node_id"] == "backend-1")

    assert final["status"] == "completed"
    assert backend_node["status"] == "done"
    assert backend_node["retry_count"] == 1
    assert len(waves) == 2
    assert len(retries) == 1

    print("  PASS test_v9_verification_fail_retryable_retry_once")
    for w in waves:
        print(f"    {w}")
    for r in retries:
        print(f"  {r}")


def test_v9_execution_failure_no_verification_runs():
    """
    V9-5: execution reports failure → verification does NOT run → normal failure path.
    Key: execution failure takes priority; verification never executes.

    Wave 1: exec=failed → verification skipped → node=failed → auto-retry fires (pending)
    Wave 2: retried node dispatched → this time exec=done with verify_exit=0 → done
    """
    def scenario(wave, ready, graph):
        if wave == 1:
            # exec_status="failed" → verification does NOT run regardless of verify_exit
            return [("backend-1", "failed", 0)]
        elif wave == 2:
            # Retry: now execution succeeds with passing verification
            return [("backend-1", "done", 0)]
        return []

    graph = _graph(
        _node("backend-1", "pending", retryable=True, depends_on=[]),
        auto_retry_enabled=True,
    )
    graph["nodes"][0]["verification_command"] = "python3 tests/routing/test_routing_cases.py"

    final, waves, retries = run_step_c(graph, scenario)
    backend_node = next(n for n in final["nodes"] if n["node_id"] == "backend-1")

    assert final["status"] == "completed"
    assert backend_node["status"] == "done"
    assert backend_node["retry_count"] == 1
    # In wave 1: exec=failed, verify_exit was ignored (never executed)
    # auto_retry fired, reset to pending
    # In wave 2: execution succeeded, verification ran (exit 0) → done

    print("  PASS test_v9_execution_failure_no_verification_runs")
    for w in waves:
        print(f"    {w}")
    for r in retries:
        print(f"  {r}")


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

TESTS = [
    # v0.8 baseline
    ("test_r6_retry_picked_up_next_wave",             test_r6_retry_picked_up_next_wave),
    ("test_r8_retry_affects_graph_status",           test_r8_retry_affects_graph_status),
    ("test_r9_no_auto_retry_flag_graph_status",       test_r9_no_auto_retry_flag_graph_status),
    ("test_r3_retry_exhausted_no_second_retry",       test_r3_retry_exhausted_no_second_retry),
    # v0.9 verification
    ("test_v9_no_verification_command_v0_8_behavior",  test_v9_no_verification_command_v0_8_behavior),
    ("test_v9_verification_success_exit_0",           test_v9_verification_success_exit_0),
    ("test_v9_verification_failure_exit_nonzero",     test_v9_verification_failure_exit_nonzero),
    ("test_v9_verification_fail_retryable_retry_once",test_v9_verification_fail_retryable_retry_once),
    ("test_v9_execution_failure_no_verification_runs",test_v9_execution_failure_no_verification_runs),
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
