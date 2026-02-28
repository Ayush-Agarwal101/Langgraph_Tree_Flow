# core/global_description_builder.py

import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from llm.local_llama_client import call_llm
from dotenv import load_dotenv

load_dotenv()


def build_global_description(
    pruned_structure_path: str,
    stack_meta_path: str,
    output_path: str = "specs/global_description.md"
):

    # Load pruned structure
    with open(pruned_structure_path, "r", encoding="utf-8") as f:
        pruned_structure = json.load(f)

    # Load stack metadata
    with open(stack_meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    user_requirement = meta["user_initial_prompt"]
    tech_stack_summary = meta["tech_stack_summary"]

    pruned_structure_str = json.dumps(pruned_structure, indent=2)

    system_prompt = f"""
You are a senior software architect.

Your task is to generate a complete and professional project-level description. 

You must:
- Describe the overall system.
- Explain the architecture.
- Explain how frontend, backend, database, and devops (if present) interact.
- Explain responsibilities of major folders.
- Describe scalability, maintainability, and extensibility.
- Do NOT repeat raw JSON.
- Do NOT list file structure mechanically.
- Write as if preparing documentation for senior developers.
"""

    user_prompt = f"""
USER REQUIREMENT:
{user_requirement}

SELECTED TECH STACK:
{tech_stack_summary}

FINAL PRUNED PROJECT STRUCTURE:
{pruned_structure_str}

Generate a complete global project description. Format the output in professional Markdown with clear headings and sections.
"""

    full_prompt = system_prompt + "\n\n" + user_prompt

    response = call_llm(full_prompt)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response)

    print(f"\nGlobal project description saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--pruned", required=True)
    parser.add_argument("--meta", required=True)
    parser.add_argument("--output", default="specs/global_description.txt")
    args = parser.parse_args()

    build_global_description(
        pruned_structure_path=args.pruned,
        stack_meta_path=args.meta,
        output_path=args.output
    )