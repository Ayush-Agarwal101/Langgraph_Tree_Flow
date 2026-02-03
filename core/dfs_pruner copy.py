# core/dfs_pruner.py

from typing import Dict, List
from specs.usage_manifest import record_decision


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
# Temporary LLM decision logic
# -----------------------------
def llm_decide_keep_or_prune(path: str, node: Dict, final_prompt: str) -> Dict:
    """
    Stub decision logic.
    Replace later with council of LLMs.
    """

    if node.get("mandatory") is True:
        return {
            "decision": "KEEP",
            "reason": "Folder marked as mandatory"
        }

    prompt_lower = final_prompt.lower()
    path_lower = path.lower()

    if "backend" in path_lower:
        return {
            "decision": "PRUNE",
            "reason": "Frontend-only project"
        }

    if "store" in path_lower and "context" in prompt_lower:
        return {
            "decision": "PRUNE",
            "reason": "State handled via React Context"
        }

    return {
        "decision": "KEEP",
        "reason": "Relevant to project scope"
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

        # ✅ Proper manifest recording
        record_decision(
            manifest=usage_manifest,
            path=current_path,
            decision=decision["decision"],
            reason=decision["reason"],
            model="mistral"
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
