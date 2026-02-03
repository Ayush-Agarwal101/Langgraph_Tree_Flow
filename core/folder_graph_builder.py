# core/folder_graph_builder.py

import json
from typing import Dict, Any
from core.langgraph_runner import LangGraphRecorder


def load_folder_structure(path: str) -> Dict[str, Any]:
    """Load folder structure JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_langgraph_from_folder_structure(
    data: Dict[str, Any],
    recorder: LangGraphRecorder,
    parent_id: str = ""
):
    """
    Recursively converts folder_structure.json into LangGraph nodes and edges.

    Leaf definition:
    - A folder with NO subfolders
    - Files do NOT matter
    """

    name = data.get("name")
    if not name:
        return

    node_type = data.get("type", "folder")
    description = data.get("description", "")

    # Construct unique node ID using full path
    node_id = f"{parent_id}/{name}" if parent_id else name

    # Register node
    recorder.add_node(node_id)

    # Attach metadata (used later for LLM prompts)
    meta_prompt = f"""
TYPE: {node_type}
DESCRIPTION: {description}
""".strip()

    recorder.add_prompt_to_node(node_id, meta_prompt)

    # Add edge from parent → current
    if parent_id:
        recorder.add_edge(parent_id, node_id)

    # Detect leaf folder (no subfolders)
    if node_type == "folder":
        children = data.get("children") or {}
        has_subfolder = any(
            isinstance(child, dict) and child.get("type") == "folder"
            for child in children.values()
        )

        if not has_subfolder:
            recorder.mark_leaf(node_id)

    # Recurse into children
    if node_type == "folder":
        for child_name, child_data in (data.get("children") or {}).items():
            if not isinstance(child_data, dict):
                continue

            child_copy = dict(child_data)
            child_copy["name"] = child_name

            build_langgraph_from_folder_structure(
                data=child_copy,
                recorder=recorder,
                parent_id=node_id
            )
