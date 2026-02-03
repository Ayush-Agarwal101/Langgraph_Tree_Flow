# dfs_pruner.py

import json
from typing import Dict, Any, List
from llm.local_llama_client import call_llm
from specs.usage_manifest import record_decision


def llm_evaluate_path(
    final_prompt: str,
    path: List[Dict[str, str]]
) -> tuple[bool, str]:
    """
    Returns (keep, reason)
    """

    path_text = "\n".join(
        f"- {p['type'].upper()}: {p['name']} | {p['description']}"
        for p in path
    )

    prompt = f"""
You are a strict architectural decision engine.

PROJECT CONTEXT:
{final_prompt}

CANDIDATE PATH (root → leaf):
{path_text}

QUESTION:
Is this path REQUIRED for the project?

Rules:
- Reply ONLY in JSON
- Format:
  {{
    "keep": true | false,
    "reason": "<one short sentence>"
  }}
- If unsure, keep = false
"""

    response = call_llm(prompt, model="mistral")

    try:
        data = json.loads(response)
        return bool(data.get("keep", False)), data.get("reason", "")
    except Exception:
        return False, "Invalid or unclear response"

def dfs_prune(
    node: Dict[str, Any],
    final_prompt: str,
    path_stack: List[Dict[str, str]],
    accepted_paths: List[List[Dict[str, str]]],
    manifest: Dict
) -> bool:
    current = {
        "name": node["name"],
        "type": node.get("type", "folder"),
        "description": node.get("description", "")
    }

    path_stack.append(current)

    node_type = node.get("type", "folder")

    # ---- LEAF NODE ----
    if node_type == "file" or not node.get("children"):
        keep, reason = llm_evaluate_path(final_prompt, path_stack)

        decision = "KEEP" if keep else "PRUNE"

        record_decision(
            manifest=manifest,
            path_stack=path_stack,
            decision=decision,
            reason=reason,
            model="mistral"
        )

        if keep:
            accepted_paths.append(list(path_stack))

        path_stack.pop()
        return keep

    # ---- FOLDER NODE ----
    keep_any_child = False

    for child_name, child in node.get("children", {}).items():
        child_copy = dict(child)
        child_copy["name"] = child_name

        if dfs_prune(
            child_copy,
            final_prompt,
            path_stack,
            accepted_paths,
            manifest
        ):
            keep_any_child = True

    path_stack.pop()
    return keep_any_child


def generate_yaml_from_paths(paths: List[List[Dict[str, str]]]) -> str:
    """
    Each leaf path becomes a YAML entry.
    """

    lines = []

    for i, path in enumerate(paths, 1):
        lines.append(f"- path_{i}:")
        for p in path:
            lines.append(f"  - {p['name']}: {p['type']}")

    return "\n".join(lines)
