import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yaml
import json
from dotenv import load_dotenv
from core.llm_structured import StructuredLLM
from core.schemas_project_blueprint import ProjectBlueprint

load_dotenv()


def build_project_blueprint(
    global_desc_path: str,
    stack_meta_path: str,
    output_path: str = "specs/project_blueprint.yaml"
):

    with open(global_desc_path, "r", encoding="utf-8") as f:
        global_desc = f.read()

    with open(stack_meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    user_requirement = meta["user_initial_prompt"]
    tech_stack = meta["tech_stack_summary"]

    llm = StructuredLLM()

    system_prompt = """
    You are generating a structured project blueprint.

    You MUST return ONLY valid JSON.
    Do NOT include markdown.
    Do NOT include explanation.
    Follow the EXACT structure shown below.
    """

    user_prompt = f"""
    USER REQUIREMENT:
    {user_requirement}

    TECH STACK:
    {tech_stack}

    GLOBAL ARCHITECTURE DOCUMENT:
    {global_desc}

    Return JSON in EXACTLY this structure:

    {{
      "project_meta": {{
        "name": "",
        "version": "",
        "language": "",
        "type": "",
        "description": ""
      }},
      "architecture": {{
        "pattern": "",
        "entry_points": [
          {{
            "name": "",
            "type": "",
            "description": ""
          }}
        ],
        "components": [
          {{
            "name": "",
            "responsibility": ""
          }}
        ],
        "data_flow_summary": ""
      }},
      "infrastructure": {{
        "external_services": [
          {{
            "name": "",
            "role": "",
            "purpose": ""
          }}
        ]
      }},
      "dependencies": {{
        "internal": [
          {{
            "name": "",
            "purpose": ""
          }}
        ],
        "external": [
          {{
            "name": "",
            "version": "",
            "purpose": ""
          }}
        ]
      }}
    }}

    All top-level keys are mandatory.
    Do NOT add extra keys.
    Do NOT rename keys.
    """

    blueprint: ProjectBlueprint = llm.call(
        prompt=system_prompt + "\n\n" + user_prompt,
        schema=ProjectBlueprint
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(blueprint.model_dump(), f, sort_keys=False)

    print("Project blueprint YAML generated successfully.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--global-desc", required=True)
    parser.add_argument("--meta", required=True)
    parser.add_argument("--output", default="specs/project_blueprint.yaml")
    args = parser.parse_args()

    build_project_blueprint(
        global_desc_path=args.global_desc,
        stack_meta_path=args.meta,
        output_path=args.output
    )