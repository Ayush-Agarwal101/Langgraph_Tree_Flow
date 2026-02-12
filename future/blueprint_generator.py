import json
from typing import Dict, Any
from llm.local_llama_client import call_llm

def summarize_pruned_tree(node: Dict, indent: int = 0) -> str:
    """
    Convert pruned tree into readable text summary for LLM.
    """
    if not isinstance(node, dict):
        return

name = node.get("name", "")
result = "  " * indent + f"- {name}\n"

children = node.get("children", {})
for child_name, child_data in children.items():
    child_copy = dict(child_data)
    child_copy["name"] = child_name
    result += summarize_pruned_tree(child_copy, indent + 1)

return result


def generate_project_blueprint(
final_prompt: str,
pruned_tree: Dict[str, Any],
model: str = "mistral"
) -> Dict[str, Any]:

    tree_summary = summarize_pruned_tree(pruned_tree)

    prompt = f"""
    You are an expert software architect.
    Given:
    PROJECT IDEA:
    {final_prompt}

    PRUNED PROJECT STRUCTURE:
    {tree_summary}

    Your task:
    Generate a COMPLETE PROJECT BLUEPRINT in STRICT JSON format.

    The JSON must contain:

    project_overview

    tech_stack

    architecture_pattern

    modules (list with purpose)

    routing_strategy

    state_management_strategy

    data_flow_description

    api_contracts (if applicable)

    naming_conventions

    folder_responsibility_map

    Return ONLY valid JSON.
    Do not explain.
    """

    response = call_llm(prompt, model=model)

    try:
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except:
        pass

    return {"error": "Failed to parse blueprint"}


def save_blueprint(blueprint: Dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(blueprint, f, indent=2)