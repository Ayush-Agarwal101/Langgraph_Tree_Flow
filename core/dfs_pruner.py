# core/dfs_pruner.py

from typing import Dict, List
import json
from specs.usage_manifest import record_decision
from llm.local_llama_client import call_llm
from core.llm_structured import StructuredLLM
from core.schemas import PruneDecision

# -----------------------------
# Helper: detect leaf folder
# -----------------------------
def is_leaf_folder(node: Dict) -> bool:
    """
    Leaf = folder with no subfolders.
    Files inside do NOT matter.
    """
    children = node.get("children") or {}

    for child in children.values():
        if isinstance(child, dict) and child.get("type") == "folder":
            return False

    return True


# -----------------------------
# LLM decision logic (Ollama)
# -----------------------------
def llm_decide_keep_or_prune(path: str, node: Dict, final_prompt: str) -> Dict:

    if node.get("mandatory") is True:
        return {
            "decision": "KEEP",
            "reason": "Folder marked as mandatory"
        }

    decision_prompt = f"""
PROJECT REQUIREMENT:
{final_prompt}

FOLDER PATH:
{path}

FOLDER DESCRIPTION:
{json.dumps(node.get("description", ""), indent=2)}

Respond with:
{{
  "decision": "KEEP or PRUNE",
  "reason": "short explanation"
}}
"""

    llm = StructuredLLM(model="mistral")

    result = llm.call(
        prompt=decision_prompt,
        schema=PruneDecision
    )

    return {
        "decision": result.decision,
        "reason": result.reason
    }


# DFS traversal
def dfs_traverse(
    node: Dict,
    path_stack: List[str],
    final_prompt: str,
    prune_decisions: Dict,
    usage_manifest: Dict
):
    # Safety guards
    if not isinstance(node, dict):
        return

    if node.get("type") != "folder":
        return

    node_name = node.get("name", "<unnamed>")

    current_path = "/".join(path_stack + [node_name])
    path_stack.append(node_name)

    # Debug trace
    print(f">>> DFS at: {current_path}")

    children = node.get("children") or {}

    # -------- LEAF FOLDER --------
    if is_leaf_folder(node):
        decision = llm_decide_keep_or_prune(
            path=current_path,
            node=node,
            final_prompt=final_prompt
        )

        prune_decisions["decisions"][current_path] = {
            "decision": decision["decision"],
            "description": node.get("description", ""),
            "reason": decision["reason"]
        }

        # Record in usage manifest
        record_decision(
            manifest=usage_manifest,
            path=current_path,
            decision=decision["decision"],
            reason=decision["reason"],
            model="ollama"
        )

        path_stack.pop()
        return

    # -------- DFS INTO CHILD FOLDERS --------
    for child_name, child in children.items():
        if not isinstance(child, dict):
            continue

        if child.get("type") != "folder":
            continue

        child_copy = dict(child)
        child_copy["name"] = child_name

        dfs_traverse(
            node=child_copy,
            path_stack=path_stack,
            final_prompt=final_prompt,
            prune_decisions=prune_decisions,
            usage_manifest=usage_manifest
        )

    path_stack.pop()
