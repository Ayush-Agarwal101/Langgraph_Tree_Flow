# core/node_description_builder.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from dotenv import load_dotenv
from llm.local_llama_client import call_llm

load_dotenv()


# ------------------------------------------------------------
# Helper: Extract all nodes (folders + files)
# ------------------------------------------------------------

def extract_all_nodes(tree, parents=None):
    if parents is None:
        parents = []

    results = []

    current_node = {
        "name": tree.get("name"),
        "type": tree.get("type"),
        "full_path": tree.get("full_path"),
        "description": tree.get("description", ""),
        "mandatory": tree.get("mandatory", "no"),
        "parents": parents.copy()
    }

    results.append(current_node)

    new_parents = parents + [{
        "name": tree.get("name"),
        "type": tree.get("type"),
        "full_path": tree.get("full_path")
    }]

    for child in tree.get("children", []):
        results.extend(extract_all_nodes(child, new_parents))

    return results


# ------------------------------------------------------------
# Main Builder
# ------------------------------------------------------------

def build_node_descriptions(
    pruned_structure_path: str,
    stack_meta_path: str,
    global_description_path: str,
    output_base_dir: str = "specs/node_descriptions"
):

    # Load inputs
    with open(pruned_structure_path, "r", encoding="utf-8") as f:
        pruned_structure = json.load(f)

    with open(stack_meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    with open(global_description_path, "r", encoding="utf-8") as f:
        global_description = f.read()

    user_requirement = meta["user_initial_prompt"]
    tech_stack_summary = meta["tech_stack_summary"]

    # Extract nodes
    all_nodes = extract_all_nodes(pruned_structure)

    os.makedirs(output_base_dir, exist_ok=True)

    for node in all_nodes:

        parent_text = ""
        for p in node["parents"]:
            parent_text += f"- {p['name']} ({p['type']})\n"

        system_prompt = """
        You are a senior software architect documenting a project.

        Strict Rules:
        - Remain fully consistent with the provided global architecture.
        - Do NOT introduce new architectural layers.
        - Do NOT change tech stack.
        - You MAY introduce internal helper functions and utilities
          if they align with the architecture.
        - Do NOT implement full code.
        - Do NOT output raw JSON.
        - Output must be clean, structured Markdown.

        You MUST follow this exact structure:

        # <Full Path>

        ## Purpose

        ## Responsibilities

        ## Key Functions (Conceptual)

        For each function:
        - Provide a clear function name.
        - Provide conceptual parameters (names only).
        - Provide conceptual return value.
        - Provide short description of responsibility.
        - Do NOT implement code.
        - Do NOT invent functions outside architectural scope.

        ## Interactions

        ## Future Extensibility
        """

        user_prompt = f"""
USER REQUIREMENT:
{user_requirement}

TECH STACK:
{tech_stack_summary}

GLOBAL ARCHITECTURE:
{global_description}

CURRENT NODE:
Name: {node['name']}
Type: {node['type']}
Full Path: {node['full_path']}
Description: {node['description']}
Mandatory: {node['mandatory']}

The top-level heading MUST be:
# {node['full_path']}

PARENT HIERARCHY:
{parent_text}

Generate the documentation strictly following the required structure.

Important:
- Every file must include a "Key Functions (Conceptual)" section.
- Function names must be explicitly defined.
- Include conceptual parameters and return values.
- Do NOT implement code.
- Do NOT redefine architecture.
"""

        full_prompt = system_prompt + "\n\n" + user_prompt

        print(f"Generating description for: {node['full_path']}")

        response = call_llm(full_prompt)

        # Build output file path
        safe_path = node["full_path"].replace("\\", "/")
        output_path = os.path.join(output_base_dir, safe_path + ".md")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response)

    print("\nAll node descriptions generated successfully.")


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--pruned", required=True)
    parser.add_argument("--meta", required=True)
    parser.add_argument("--global-desc", required=True)
    parser.add_argument("--output-dir", default="specs/node_descriptions")
    args = parser.parse_args()

    build_node_descriptions(
        pruned_structure_path=args.pruned,
        stack_meta_path=args.meta,
        global_description_path=args.global_desc,
        output_base_dir=args.output_dir
    )