# core/langgraph_from_structure.py

from typing import Dict
from core.langgraph_runner import LangGraphRecorder


def build_langgraph_from_pruned_tree(
    node: Dict,
    recorder: LangGraphRecorder,
    parent_name: str | None = None
):
    """
    Traverses a pruned folder structure and records it into LangGraphRecorder.
    """

    if not isinstance(node, dict):
        return

    if node.get("type") != "folder":
        return

    node_name = node.get("name")
    if not node_name:
        return

    # Add current node
    recorder.add_node(node_name)

    # Add edge from parent → current
    if parent_name:
        recorder.add_edge(parent_name, node_name)

    children = node.get("children") or {}

    # Detect leaf folder (no subfolders)
    has_subfolder = False
    for child in children.values():
        if isinstance(child, dict) and child.get("type") == "folder":
            has_subfolder = True
            break

    if not has_subfolder:
        recorder.mark_leaf(node_name)
        return

    # Recurse into children
    for child_name, child in children.items():
        if not isinstance(child, dict):
            continue

        if child.get("type") != "folder":
            continue

        child_copy = dict(child)
        child_copy["name"] = child_name

        build_langgraph_from_pruned_tree(
            node=child_copy,
            recorder=recorder,
            parent_name=node_name
        )
