# core/dfs_pruner.py

from typing import Dict, List
import json
import re

from specs.usage_manifest import record_decision
from llm.local_llama_client import call_llm


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
    """
    Uses local Ollama (via call_llm) to decide KEEP or PRUNE.
    """

    # Mandatory shortcut (still deterministic)
    if node.get("mandatory") is True:
        return {
            "decision": "KEEP",
            "reason": "Folder marked as mandatory"
        }

    # ---- Build LLM prompt ----
    decision_prompt = f"""
You are deciding whether a folder is REQUIRED in a software project.

PROJECT REQUIREMENT:
{final_prompt}

FOLDER PATH:
{path}

FOLDER DESCRIPTION:
{json.dumps(node.get("description", ""), indent=2)}

TASK:
Decide whether this folder should be KEPT or PRUNED.

RULES:
- Reply ONLY in valid JSON.
- Do NOT explain outside JSON.
- Decision must be either "KEEP" or "PRUNE".

RESPONSE FORMAT:
{{
  "decision": "KEEP | PRUNE",
  "reason": "short explanation"
}}
"""

    try:
        raw = call_llm(decision_prompt)

        # ---- Extract JSON safely ----
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in LLM response")

        data = json.loads(match.group(0))

        decision = data.get("decision", "").upper()
        reason = data.get("reason", "No reason provided")

        if decision not in ("KEEP", "PRUNE"):
            raise ValueError("Invalid decision value")

        return {
            "decision": decision,
            "reason": reason
        }

    except Exception as e:
        # ---- HARD FAIL SAFE ----
        return {
            "decision": "KEEP",
            "reason": f"Fallback KEEP due to LLM error: {str(e)}"
        }


# -----------------------------
# DFS traversal
# -----------------------------
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
    path_stack.append(node_name)

    current_path = "/".join(path_stack)

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
