#!/usr/bin/env python3
"""
Replay/Resume test suite — v0.6 Persistent Execution Runtime.
Tests format_replay_output() and reconstruct_waves() pure functions.
"""

# ---------------------------------------------------------------------------
# Pure functions (implement these first — RED, then GREEN)
# ---------------------------------------------------------------------------

def reconstruct_waves(nodes):
    """
    Reconstructs wave order from node depends_on.
    Nodes are assigned to waves by depth (nodes with no depends_on = wave 1,
    nodes whose all depends_on are in wave N = wave N+1).

    Args:
        nodes: list of node dicts with node_id and depends_on

    Returns:
        list of lists: [[node-id, ...], [node-id, ...], ...]
    """
    node_map = {n["node_id"]: n for n in nodes}
    assigned = {}  # node_id → wave index (0-based)

    def wave_of(node_id):
        if node_id in assigned:
            return assigned[node_id]
        node = node_map[node_id]
        if not node.get("depends_on"):
            w = 0
        else:
            w = max(wave_of(dep) for dep in node["depends_on"]) + 1
        assigned[node_id] = w
        return w

    for n in nodes:
        wave_of(n["node_id"])

    waves = {}
    for nid, w in assigned.items():
        waves.setdefault(w, []).append(nid)

    return [waves[i] for i in sorted(waves.keys())]


def format_replay_output(task):
    """
    Formats a task JSON into the replay output string.
    Pure function — no side effects.

    Missing fields handling:
        - missing started_at/completed_at → "—"
        - missing waves/wave_order → reconstruct from depends_on depth
        - missing milestone → omit milestone section
        - missing execution_graph → print routing only
    """
    lines = []
    lines.append(f"=== REPLAY: {task['task_id']} ===\n")
    lines.append(f"Prompt: {task.get('prompt', '')}")
    lines.append(f"Status: {task.get('status', '')}\n")

    rd = task.get("routing_decision", {})
    selected = [t["team"] for t in rd.get("selected_teams", [])]
    secondary = [t["team"] for t in rd.get("secondary_teams", [])]
    ignored = [t.get("team", "") for t in rd.get("ignored_teams", [])]

    lines.append("Routing:")
    lines.append(f"  Selected:  {', '.join(selected) or '(none)'}")
    lines.append(f"  Secondary: {', '.join(secondary) or '(none)'}")
    lines.append(f"  Ignored:   {', '.join(ignored) or '(none)'}")

    graph = task.get("execution_graph")
    if graph:
        nodes = graph.get("nodes", [])
        wave_list = graph.get("waves")
        if not wave_list:
            wave_list = reconstruct_waves(nodes)
        lines.append("\nExecution Graph:")
        for wave_idx, wave_nodes in enumerate(wave_list):
            wave_num = wave_idx + 1
            node_strs = []
            for nid in wave_nodes:
                node = next((n for n in nodes if n["node_id"] == nid), {})
                status = node.get("status", "?")
                ts = node.get("completed_at") or node.get("started_at") or "—"
                node_strs.append(f"{nid} → {status} {ts}")
            lines.append(f"  Wave {wave_num}: [{', '.join(wave_nodes)}]")
            for ns in node_strs:
                lines.append(f"    {ns}")

        lines.append(f"\nFinal status: {graph.get('status', '?')}")

    milestone = task.get("milestone")
    if milestone:
        lines.append(f"Milestone: {milestone.get('title', '')} ({milestone.get('milestone_id', '')})")

    lines.append("\n=== END REPLAY ===")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Replay tests
# ---------------------------------------------------------------------------

def _test_replay_completed_task():
    """
    R1: Completed task → shows routing + graph + milestone info.
    """
    task = {
        "task_id": "t-001",
        "prompt": "Build a SaaS API",
        "status": "completed",
        "routing_decision": {
            "selected_teams": [{"team": "product"}, {"team": "backend"}],
            "secondary_teams": [{"team": "market"}],
            "ignored_teams": [],
        },
        "execution_graph": {
            "status": "completed",
            "nodes": [
                {"node_id": "product-1", "team": "product", "depends_on": [],
                 "status": "done", "started_at": "2026-03-26T10:01:00Z",
                 "completed_at": "2026-03-26T10:01:30Z"},
                {"node_id": "backend-1", "team": "backend", "depends_on": ["product-1"],
                 "status": "done", "started_at": "2026-03-26T10:01:30Z",
                 "completed_at": "2026-03-26T10:03:00Z"},
            ],
            "edges": [["product-1", "backend-1"]],
            "waves": [["product-1"], ["backend-1"]],
            "started_at": "2026-03-26T10:01:00Z",
            "completed_at": "2026-03-26T10:03:00Z",
        },
        "milestone": {"milestone_id": "ms_abc", "title": "Launch SaaS"},
    }
    output = format_replay_output(task)
    assert "t-001" in output
    assert "Build a SaaS API" in output
    assert "completed" in output
    assert "product" in output
    assert "backend" in output
    assert "market" in output  # secondary
    assert "Wave 1" in output
    assert "Wave 2" in output
    assert "ms_abc" in output
    assert "Launch SaaS" in output


def _test_replay_missing_timestamps():
    """
    R2: Missing started_at/completed_at → displays "—".
    """
    task = {
        "task_id": "t-002",
        "prompt": "Test task",
        "status": "in_progress",
        "routing_decision": {
            "selected_teams": [{"team": "backend"}],
            "secondary_teams": [],
            "ignored_teams": [],
        },
        "execution_graph": {
            "status": "in_progress",
            "nodes": [
                {"node_id": "backend-1", "team": "backend", "depends_on": [],
                 "status": "running"},  # no timestamps
            ],
            "edges": [],
            "waves": [["backend-1"]],
        },
    }
    output = format_replay_output(task)
    assert "—" in output  # missing timestamp
    assert "backend" in output


def _test_replay_missing_waves():
    """
    R3: Missing waves field → reconstructs from depends_on depth.
    """
    nodes = [
        {"node_id": "product-1", "depends_on": []},
        {"node_id": "backend-1", "depends_on": ["product-1"]},
        {"node_id": "frontend-1", "depends_on": ["backend-1"]},
    ]
    waves = reconstruct_waves(nodes)
    assert waves == [["product-1"], ["backend-1"], ["frontend-1"]]


def _test_replay_with_milestone():
    """
    R4: Task with milestone → milestone ref printed.
    """
    task = {
        "task_id": "t-003",
        "prompt": "Design a mobile app",
        "status": "completed",
        "routing_decision": {
            "selected_teams": [{"team": "mobile"}],
            "secondary_teams": [],
            "ignored_teams": [],
        },
        "execution_graph": {
            "status": "completed",
            "nodes": [
                {"node_id": "mobile-1", "team": "mobile", "depends_on": [],
                 "status": "done",
                 "started_at": "2026-03-26T11:00:00Z",
                 "completed_at": "2026-03-26T11:30:00Z"},
            ],
            "edges": [],
            "waves": [["mobile-1"]],
            "started_at": "2026-03-26T11:00:00Z",
            "completed_at": "2026-03-26T11:30:00Z",
        },
        "milestone": {"milestone_id": "ms_xyz", "title": "Mobile Launch"},
    }
    output = format_replay_output(task)
    assert "ms_xyz" in output
    assert "Mobile Launch" in output


def _test_replay_no_graph():
    """
    R5: Task with no execution_graph → prints routing only.
    """
    task = {
        "task_id": "t-004",
        "prompt": "Quick question",
        "status": "pending",
        "routing_decision": {
            "selected_teams": [],
            "secondary_teams": [],
            "ignored_teams": [],
        },
    }
    output = format_replay_output(task)
    assert "t-004" in output
    assert "Quick question" in output
    assert "Execution Graph" not in output  # no graph section


def _test_reconstruct_waves_parallel():
    """
    R3b: Two nodes with same depends_on → same wave.
    """
    nodes = [
        {"node_id": "research-1", "depends_on": []},
        {"node_id": "backend-1", "depends_on": ["research-1"]},
        {"node_id": "frontend-1", "depends_on": ["research-1"]},
    ]
    waves = reconstruct_waves(nodes)
    assert waves[0] == ["research-1"]
    assert set(waves[1]) == {"backend-1", "frontend-1"}  # parallel wave


def _test_reconstruct_waves_complex():
    """
    R3c: Complex DAG: product → backend → frontend; research → infra
    """
    nodes = [
        {"node_id": "product-1", "depends_on": []},
        {"node_id": "backend-1", "depends_on": ["product-1"]},
        {"node_id": "frontend-1", "depends_on": ["backend-1"]},
        {"node_id": "research-1", "depends_on": []},
        {"node_id": "infra-1", "depends_on": ["research-1"]},
    ]
    waves = reconstruct_waves(nodes)
    assert waves[0] == ["product-1", "research-1"]  # both roots
    assert waves[1] == ["backend-1", "infra-1"]    # second wave
    assert waves[2] == ["frontend-1"]               # third wave


# ---------------------------------------------------------------------------
# Resume validation tests
# ---------------------------------------------------------------------------

def validate_resume(task):
    """
    Validates whether a task is resumable.
    Returns (resumable: bool, reason: str)

    Priority:
    1. pending_decision exists → not resumable (must use --resolve)
    2. no execution_graph → not resumable
    3. graph.status = completed → not resumable
    4. graph.status = pending (empty graph) → not resumable
    5. task.status = user_declined_dispatch → not resumable
    6. Otherwise → resumable
    """
    rd = task.get("routing_decision", {})
    if rd.get("pending_decision"):
        return False, "task awaits human decision — use --resolve"

    graph = task.get("execution_graph")
    if not graph:
        return False, "no execution graph found"

    status = graph.get("status", task.get("status"))
    if status == "completed":
        return False, "task already completed"
    if status == "pending" and not graph.get("nodes"):
        return False, "no execution graph to resume"
    if task.get("status") == "user_declined_dispatch":
        return False, "task was declined by user"

    return True, ""


def _test_resume_awaiting_decision_noop():
    """
    RV1: pending_decision exists → not resumable.
    """
    task = {
        "task_id": "t-010",
        "status": "awaiting_dispatch_decision",
        "routing_decision": {
            "pending_decision": {
                "type": "dispatch_confirmation",
                "teams": [{"team": "backend"}],
            }
        },
        "execution_graph": {
            "status": "in_progress",
            "nodes": [],
        },
    }
    resumable, reason = validate_resume(task)
    assert not resumable
    assert "--resolve" in reason


def _test_resume_no_graph_noop():
    """
    RV2: no execution_graph → not resumable.
    """
    task = {
        "task_id": "t-011",
        "status": "pending",
        "routing_decision": {
            "selected_teams": [{"team": "backend"}],
        },
    }
    resumable, reason = validate_resume(task)
    assert not resumable
    assert "no execution graph" in reason.lower()


def _test_resume_completed_noop():
    """
    RV3: graph.status = completed → no-op.
    """
    task = {
        "task_id": "t-012",
        "status": "completed",
        "routing_decision": {},
        "execution_graph": {
            "status": "completed",
            "nodes": [{"node_id": "backend-1", "depends_on": [], "status": "done"}],
        },
    }
    resumable, reason = validate_resume(task)
    assert not resumable
    assert "completed" in reason.lower()


def _test_resume_declined_noop():
    """
    RV4: status = user_declined_dispatch → not resumable.
    """
    task = {
        "task_id": "t-013",
        "status": "user_declined_dispatch",
        "routing_decision": {},
        "execution_graph": {
            "status": "pending",
            "nodes": [],
        },
    }
    resumable, reason = validate_resume(task)
    assert not resumable


def _test_resume_in_progress_resumable():
    """
    RV5: graph.status = in_progress → resumable.
    """
    task = {
        "task_id": "t-014",
        "status": "in_progress",
        "routing_decision": {},
        "execution_graph": {
            "status": "in_progress",
            "nodes": [
                {"node_id": "product-1", "depends_on": [], "status": "done"},
                {"node_id": "backend-1", "depends_on": ["product-1"], "status": "pending"},
            ],
        },
    }
    resumable, reason = validate_resume(task)
    assert resumable


def _test_resume_partial_failed_resumable():
    """
    RV6: graph.status = partial_failed → resumable (after confirm).
    """
    task = {
        "task_id": "t-015",
        "status": "in_progress",
        "routing_decision": {},
        "execution_graph": {
            "status": "partial_failed",
            "nodes": [
                {"node_id": "product-1", "depends_on": [], "status": "done"},
                {"node_id": "backend-1", "depends_on": ["product-1"], "status": "failed"},
            ],
        },
    }
    resumable, reason = validate_resume(task)
    assert resumable


def _test_resume_blocked_resumable():
    """
    RV7: graph.status = blocked → resumable (after confirm + recheck).
    """
    task = {
        "task_id": "t-016",
        "status": "in_progress",
        "routing_decision": {},
        "execution_graph": {
            "status": "blocked",
            "nodes": [
                {"node_id": "product-1", "depends_on": [], "status": "done"},
                {"node_id": "backend-1", "depends_on": ["product-1"], "status": "blocked"},
            ],
        },
    }
    resumable, reason = validate_resume(task)
    assert resumable


# ---------------------------------------------------------------------------
# Resume: partial_failed retry — only failed nodes reset
# ---------------------------------------------------------------------------

def reset_partial_failed_graph(graph):
    """
    Resets only 'failed' nodes to 'pending' in a partial_failed graph.
    Does NOT touch done, blocked, running, or pending nodes.

    Returns new graph dict (pure — copies).
    """
    new_graph = {
        "status": graph.get("status", "pending"),
        "nodes": [],
    }
    for n in graph.get("nodes", []):
        node = dict(n)
        if node["status"] == "failed":
            node["status"] = "pending"
        new_graph["nodes"].append(node)
    return new_graph


def _test_partial_failed_only_failed_reset():
    """
    RV8: partial_failed → only failed nodes reset to pending.
    """
    graph = {
        "status": "partial_failed",
        "nodes": [
            {"node_id": "product-1", "status": "done"},
            {"node_id": "backend-1", "status": "failed"},    # only this resets
            {"node_id": "frontend-1", "status": "pending"},  # untouched
            {"node_id": "mobile-1", "status": "blocked"},    # untouched
            {"node_id": "data-1", "status": "running"},     # untouched
        ],
    }
    reset = reset_partial_failed_graph(graph)
    statuses = {n["node_id"]: n["status"] for n in reset["nodes"]}
    assert statuses["product-1"] == "done"
    assert statuses["backend-1"] == "pending"    # reset
    assert statuses["frontend-1"] == "pending"  # unchanged
    assert statuses["mobile-1"] == "blocked"   # unchanged
    assert statuses["data-1"] == "running"     # unchanged


# ---------------------------------------------------------------------------
# Resume: blocked recovery — re-check artifacts_in
# ---------------------------------------------------------------------------

ARTIFACT_CHECK = {}  # path → bool (set by test harness)


def check_artifacts_in(node, artifact_map):
    """
    Check if all artifacts_in files for a node exist on disk.
    Uses artifact_map (path → bool) for test harness.
    """
    return all(artifact_map.get(path, False) for path in node.get("artifacts_in", []))


def unblock_graph(graph, artifact_map):
    """
    Re-evaluate blocked nodes: if all artifacts_in are now present,
    set status to 'pending'; otherwise keep 'blocked'.

    Returns new graph dict (pure).
    """
    new_graph = {
        "status": graph.get("status", "pending"),
        "nodes": [],
    }
    for n in graph.get("nodes", []):
        node = dict(n)
        if node["status"] == "blocked":
            if check_artifacts_in(node, artifact_map):
                node["status"] = "pending"
        new_graph["nodes"].append(node)
    return new_graph


def _test_blocked_node_unblocks_when_artifacts_present():
    """
    RV9: blocked node whose artifacts_in now exist → becomes pending.
    """
    graph = {
        "status": "blocked",
        "nodes": [
            {"node_id": "backend-1", "depends_on": [], "status": "blocked",
             "artifacts_in": ["artifacts/product/test/prd.md"]},
        ],
    }
    artifact_map = {"artifacts/product/test/prd.md": True}
    result = unblock_graph(graph, artifact_map)
    assert result["nodes"][0]["status"] == "pending"


def _test_blocked_node_stays_blocked_when_artifact_missing():
    """
    RV10: blocked node with still-missing artifact → stays blocked.
    """
    graph = {
        "status": "blocked",
        "nodes": [
            {"node_id": "backend-1", "depends_on": [], "status": "blocked",
             "artifacts_in": ["artifacts/product/test/prd.md"]},
        ],
    }
    artifact_map = {"artifacts/product/test/prd.md": False}  # still missing
    result = unblock_graph(graph, artifact_map)
    assert result["nodes"][0]["status"] == "blocked"


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

TESTS = [
    # Replay
    ("replay_completed_task", _test_replay_completed_task),
    ("replay_missing_timestamps", _test_replay_missing_timestamps),
    ("replay_missing_waves", _test_replay_missing_waves),
    ("replay_with_milestone", _test_replay_with_milestone),
    ("replay_no_graph", _test_replay_no_graph),
    ("reconstruct_waves_parallel", _test_reconstruct_waves_parallel),
    ("reconstruct_waves_complex", _test_reconstruct_waves_complex),
    # Resume validation
    ("resume_awaiting_decision_noop", _test_resume_awaiting_decision_noop),
    ("resume_no_graph_noop", _test_resume_no_graph_noop),
    ("resume_completed_noop", _test_resume_completed_noop),
    ("resume_declined_noop", _test_resume_declined_noop),
    ("resume_in_progress_resumable", _test_resume_in_progress_resumable),
    ("resume_partial_failed_resumable", _test_resume_partial_failed_resumable),
    ("resume_blocked_resumable", _test_resume_blocked_resumable),
    # Partial failed reset
    ("partial_failed_only_failed_reset", _test_partial_failed_only_failed_reset),
    # Blocked unblock
    ("blocked_node_unblocks_when_artifacts_present", _test_blocked_node_unblocks_when_artifacts_present),
    ("blocked_node_stays_blocked_when_artifact_missing", _test_blocked_node_stays_blocked_when_artifact_missing),
]


def main():
    failed = []
    for name, fn in TESTS:
        try:
            fn()
            print(f"  ✓ {name}")
        except NotImplementedError as e:
            print(f"  ✗ {name}: NotImplementedError")
            failed.append(name)
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            failed.append(name)
    print(f"\nResults: {len(TESTS) - len(failed)}/{len(TESTS)} passed, {len(failed)} failed")
    if failed:
        print(f"Failed: {failed}")
    return len(failed) == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
