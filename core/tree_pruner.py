# core/tree_pruner.py

"""
Tree pruning logic (Step 2.5)

Takes:
- original folder-structure tree
- prune decisions (paths marked PRUNE)

Produces:
- pruned folder-structure tree
"""

from typing import Dict, Optional, Set


# -------------------------------------------------
# Utility: build pruned path set
# -------------------------------------------------
def extract_pruned_paths(prune_decisions: Dict) -> Set[str]:
    """
    Extract all paths explicitly marked as PRUNE.
    """
    pruned = set()

    for path, data in prune_decisions.get("decisions", {}).items():
        if data.get("decision") == "PRUNE":
            pruned.add(path)

    return pruned


# -------------------------------------------------
# Core recursive pruning algorithm (POST-ORDER DFS)
# -------------------------------------------------
def prune_tree(
    node: Dict,
    path_stack: list,
    pruned_paths: Set[str]
) -> Optional[Dict]:
    """
    Post-order DFS prune.

    Returns:
    - pruned node (dict) if kept
    - None if pruned
    """

    if not isinstance(node, dict):
        return None

    if node.get("type") != "folder":
        return None

    node_name = node.get("name", "<unnamed>")
    current_path = "/".join(path_stack + [node_name])

    # Root node is NEVER pruned
    is_root = len(path_stack) == 0

    # Explicit PRUNE (but not root)
    if not is_root and current_path in pruned_paths:
        return None


    children = node.get("children") or {}

    # ---------- LEAF ----------
    if not children:
        return dict(node)

    # ---------- POST-ORDER DFS ----------
    new_children = {}

    for child_name, child in children.items():
        if not isinstance(child, dict):
            continue

        if child.get("type") != "folder":
            continue

        child_copy = dict(child)
        child_copy["name"] = child_name

        pruned_child = prune_tree(
            node=child_copy,
            path_stack=path_stack + [node_name],
            pruned_paths=pruned_paths
        )

        if pruned_child is not None:
            new_children[child_name] = pruned_child

    # ---------- RULE 2: Parent survival ----------
    if not new_children:
        if is_root:
            node_copy = dict(node)
            node_copy["children"] = {}
            return node_copy

        if node.get("mandatory") is True:
            node_copy = dict(node)
            node_copy["children"] = {}
            return node_copy

        return None


    # ---------- KEEP NODE ----------
    node_copy = dict(node)
    node_copy["children"] = new_children
    return node_copy
