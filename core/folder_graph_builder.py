# folder_graph_builder.py

import json
from typing import Dict, Any
from core.langgraph_runner import LangGraphRecorder


def load_folder_structure(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_langgraph_from_folder_structure(
    data: Dict[str, Any],
    recorder: LangGraphRecorder,
    parent_id: str = ""
):
    """
    Recursively converts folder_structure.json into LangGraph nodes and edges.
    """

    name = data["name"]
    node_type = data.get("type", "folder")
    description = data.get("description", "")
    required_when = data.get("required_when")

    # Construct a unique node id using path
    node_id = f"{parent_id}/{name}" if parent_id else name

    # Register node
    recorder.add_node(node_id)

    # Mark files as leaf nodes
    if node_type == "file":
        recorder.mark_leaf(node_id)

    # Attach metadata via a pseudo-prompt (used later by LLM)
    meta_prompt = f"""
TYPE: {node_type}
DESCRIPTION: {description}
"""
    if required_when:
        meta_prompt += f"REQUIRED_WHEN: {required_when}\n"

    recorder.add_prompt_to_node(node_id, meta_prompt.strip())

    # Add edge from parent → current
    if parent_id:
        recorder.add_edge(parent_id, node_id)

    # Recurse for children
    if node_type == "folder":
        children = data.get("children", {})
        for child_name, child_data in children.items():
            child_data = dict(child_data)  # defensive copy
            child_data["name"] = child_name
            build_langgraph_from_folder_structure(
                child_data,
                recorder,
                parent_id=node_id
            )