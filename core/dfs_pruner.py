# core/dfs_pruner.py

import json
from typing import Dict, Any, List

from core.council import council_decide_leaf
from specs.usage_manifest import record_decision


def normalize_path(path_stack: List[str]) -> str:
    return "/".join(path_stack)


def is_leaf_folder(node: Dict[str, Any]) -> bool:
    """
    Leaf = folder with no subfolders.
    Files may exist in description.
    """
    children = node.get("children", {})
    return not any(
        child.get("type") == "folder"
        for child in children.values()
    )


def dfs_traverse(
    node: Dict[str, Any],
    path_stack: List[str],
    final_prompt: str,
    prune_decisions: dict,
    usage_manifest: dict
):
    name = node["name"]
    path_stack.append(name)

    node_type = node.get("type", "folder")
    children = node.get("children", {})

    # ---- LEAF FOLDER ----
    if node_type == "folder" and is_leaf_folder(node):
        full_path = normalize_path(path_stack)

        description = node.get("description", {})
        mandatory = node.get("mandatory", False)

        decision_data = council_decide_leaf(
            final_prompt=final_prompt,
            path=full_path,
            leaf_description=description,
            mandatory=mandatory
        )

        decision = decision_data["decision"]

        prune_decisions["decisions"][full_path] = {
            "decision": decision,
            "description": decision_data.get("description", ""),
            "reason": decision_data.get("reason", "")
        }

        record_decision(
            manifest=usage_manifest,
            path=full_path,
            decision=decision,
            reason=decision_data.get("reason", "")
        )

    # ---- CONTINUE DFS ----
    for child_name, child in children.items():
        child_copy = dict(child)
        child_copy["name"] = child_name
        dfs_traverse(
            child_copy,
            path_stack,
            final_prompt,
            prune_decisions,
            usage_manifest
        )

    path_stack.pop()
