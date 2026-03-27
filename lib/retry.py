"""
Auto-retry logic for v0.8 — pure functions.
"""

def check_retry_eligible(node, auto_retry_enabled):
    """
    Returns (eligible: bool, reason: str).
    Guards (all must be true for eligible=True):
    - auto_retry_enabled must be True
    - node.get("retryable") must be True
    - node.get("retry_count", 0) must be < 1
    - node.get("status") must == "failed"
    """
    if not auto_retry_enabled:
        return False, "auto-retry disabled"
    if not node.get("retryable", False):
        return False, "node not retryable"
    if node.get("retry_count", 0) >= 1:
        return False, "retry count exhausted"
    if node.get("status") != "failed":
        return False, "node not in failed status"
    return True, "eligible"


def reset_for_retry(node):
    """
    Resets node to pending and increments retry_count.
    Pure function — returns new node dict, does not mutate.
    """
    return {
        **node,
        "status": "pending",
        "retry_count": node.get("retry_count", 0) + 1,
    }


def maybe_retry_nodes(graph, auto_retry_enabled):
    """
    Scans all failed nodes, resets eligible ones per check_retry_eligible.
    Returns (updated_graph, retried_node_ids[]).
    """
    retried = []
    updated_nodes = []
    for node in graph.get("nodes", []):
        eligible, _ = check_retry_eligible(node, auto_retry_enabled)
        if eligible:
            updated_nodes.append(reset_for_retry(node))
            retried.append(node["node_id"])
        else:
            updated_nodes.append(node)
    return (
        {**graph, "nodes": updated_nodes},
        retried,
    )