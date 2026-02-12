import json
from typing import Dict, List
from llm.local_llama_client import call_llm

def extract_files(node: Dict, path_stack=None):
    if path_stack is None:
        path_stack = []

    files = []

    name = node.get("name")
    node_type = node.get("type")

    if name:
        path_stack.append(name)

    if node_type == "file":
        files.append({
            "path": "/".join(path_stack),
            "description": node.get("description", "")
        })

    children = node.get("children", {})
    for child_name, child_data in children.items():
        child_copy = dict(child_data)
        child_copy["name"] = child_name
        files.extend(extract_files(child_copy, path_stack.copy()))

    return files


def generate_file_spec(
file_info: Dict,
final_prompt: str,
blueprint: Dict,
model="mistral"
) -> Dict:

    prompt = f"""


    You are an expert software engineer.

    PROJECT IDEA:
    {final_prompt}

    GLOBAL PROJECT BLUEPRINT:
    {json.dumps(blueprint, indent=2)}

    FILE PATH:
    {file_info["path"]}

    FILE DESCRIPTION:
    {file_info["description"]}

    Generate STRICT JSON with:

    file_path

    purpose

    exports

    imports

    functions (with parameters and purpose)

    state_used

    dependencies

    internal_logic_summary

    Return only JSON.
    """

    response = call_llm(prompt, model=model)

    try:
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except:
        pass

    return {"error": f"Failed for {file_info['path']}"}


def generate_all_file_specs(
pruned_tree: Dict,
final_prompt: str,
blueprint: Dict
) -> List[Dict]:

    files = extract_files(pruned_tree)

    specs = []

    for file_info in files:
        spec = generate_file_spec(file_info, final_prompt, blueprint)
        specs.append(spec)

    return specs


def save_file_specs(specs: List[Dict], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(specs, f, indent=2)