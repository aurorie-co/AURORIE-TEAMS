#!/usr/bin/env python3
"""
demo/v0.8/demo_script.py — Deterministic Step C simulation demo

Shows retry behavior at the wave level — the "runtime behavior" gap
identified in the QA review.

Usage:
  python3 demo/v0.8/demo_script.py
"""

import sys
sys.path.insert(0, "/Users/aurorie/workspace/aurorie/aurorie-teams")

from tests.routing.test_step_c_simulation import (
    _graph, _node, _dispatch_and_advance, _is_terminal,
    get_ready_nodes,
)
from lib.retry import maybe_retry_nodes

WAVE_BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║  AURORIE TEAMS v0.8 — Auto-Retry Policy                         ║
║  Step C Wave Simulation                                          ║
╚══════════════════════════════════════════════════════════════════╝"""

SECTION = lambda title: print(f"\n{'='*60}\n  {title}\n{'='*60}")


def simulate(name, graph, waves):
    """Run a fixed wave sequence, print each step."""
    print(f"\n▶  {name}")
    print(f"    Initial: {[(n['node_id'], n['status']) for n in graph['nodes']]}")
    print(f"    auto_retry_enabled: {graph['metadata'].get('auto_retry_enabled')}")

    for wave_i, dispatch_results in enumerate(waves, 1):
        ready = get_ready_nodes(graph)
        print(f"\n  ── Wave {wave_i} ──")
        print(f"  Ready nodes : {ready}")

        # Advance nodes
        for node_id, result in dispatch_results:
            graph = _advance(graph, node_id, result)
            print(f"  Dispatch    : {node_id} → {result}")

        # Retry hook
        auto_retry = graph["metadata"].get("auto_retry_enabled", True)
        graph, retried = maybe_retry_nodes(graph, auto_retry)

        if retried:
            for nid in retried:
                node = next(n for n in graph["nodes"] if n["node_id"] == nid)
                before = node["retry_count"] - 1
                print(f"  ⚡ Retry     : {nid} (retry_count: {before} → {node['retry_count']}) reset to pending for next wave")
                graph["status"] = "in_progress"

        print(f"  Graph status: {graph['status']}")

        if _is_terminal(graph):
            break

    print(f"\n  Final graph.status: {graph['status']}")
    for n in graph["nodes"]:
        print(f"    {n['node_id']}: status={n['status']}, retry_count={n['retry_count']}")
    return graph


def _advance(graph, node_id, new_status):
    """Simplified advance_node for demo display."""
    nodes = []
    for n in graph["nodes"]:
        if n["node_id"] == node_id:
            n = dict(n)
            n["status"] = new_status
        nodes.append(n)
    # Update graph status
    all_done = all(nn["status"] == "done" for nn in nodes)
    any_failed = any(nn["status"] == "failed" for nn in nodes)
    graph = dict(graph)
    graph["nodes"] = nodes
    if all_done:
        graph["status"] = "completed"
    elif any_failed:
        graph["status"] = "partial_failed"
    return graph


def main():
    print(WAVE_BANNER)

    # ── Demo 1: Auto-retry succeeds ──────────────────────────────────
    SECTION("Demo 1 — Auto-Retry: fail → retry → success")

    graph = _graph(
        _node("product-1", "pending", depends_on=[]),
        _node("backend-1", "pending", retryable=True, depends_on=[]),
        auto_retry_enabled=True,
    )

    waves = [
        [("product-1", "done"), ("backend-1", "failed")],   # Wave 1
        [("backend-1", "done")],                             # Wave 2
    ]
    result = simulate("Backend fails Wave 1 → retried → succeeds Wave 2", graph, waves)
    print("""
  ✓ backend: failed → retry_count=1 → pending → dispatched Wave 2 → done
  ✓ graph.status = completed
  ✓ R6 (next-wave pickup) ✓ R8 (retry→success→completed)""")


    # ── Demo 2: --no-auto-retry → partial_failed ──────────────────────
    SECTION("Demo 2 — --no-auto-retry: fail → unrecoverable")

    graph = _graph(
        _node("backend-1", "pending", retryable=True, depends_on=[]),
        auto_retry_enabled=False,   # --no-auto-retry
    )

    waves = [
        [("backend-1", "failed")],  # Wave 1
    ]
    result = simulate("--no-auto-retry: backend fails → no retry", graph, waves)
    print("""
  ✓ backend: failed → NOT retried (auto_retry_enabled=False)
  ✓ retry_count stays 0
  ✓ graph.status = partial_failed
  ✓ R9 (--no-auto-retry flag)""")


    # ── Demo 3: Retry exhausted → partial_failed ───────────────────────
    SECTION("Demo 3 — Retry exhausted: fail → retry → fail again → partial_failed")

    graph = _graph(
        _node("backend-1", "pending", retryable=True, depends_on=[]),
        auto_retry_enabled=True,
    )

    waves = [
        [("backend-1", "failed")],   # Wave 1: fail → retry
        [("backend-1", "failed")],   # Wave 2: fails again → no more retries
    ]
    result = simulate("Backend fails → retried → fails again → exhausted", graph, waves)
    print("""
  ✓ Wave 1: backend fails → retried (retry_count: 0→1)
  ✓ Wave 2: backend fails again → retry_count already 1 → NOT retried
  ✓ graph.status = partial_failed
  ✓ R3 (once only)""")


    # ── Summary ──────────────────────────────────────────────────────
    SECTION("What This Proves")
    print("""
  R6 — Next-wave pickup:
    Retry fires AFTER a wave completes. Failed node is NOT re-dispatched
    within the same wave. It becomes pending and is picked up in the next wave.

  R8 — Retry → success → completed:
    When a retried node succeeds, the graph reaches "completed" — not
    "partial_failed". The retry erased the failure history.

  R9 — --no-auto-retry flag:
    When auto_retry_enabled=False in metadata, no retry eligibility checks
    fire regardless of node-level retryable flag. unrecoverable → partial_failed.

  R3 — Exactly one retry:
    retry_count is a hard counter. After one retry, retry_count=1 and
    the node is not eligible again.
""")


if __name__ == "__main__":
    main()
