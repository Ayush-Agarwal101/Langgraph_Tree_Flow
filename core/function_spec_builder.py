# core/function_spec_builder.py

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import yaml
import json
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel
from core.llm_structured import StructuredLLM

load_dotenv()


# -----------------------------
# Schema Models
# -----------------------------

class ParameterSpec(BaseModel):
    name: str
    type: str


class FunctionSpec(BaseModel):
    name: str
    parameters: List[ParameterSpec]
    return_type: str
    description: str


class FileFunctionSpec(BaseModel):
    file: str
    functions: List[FunctionSpec]


# -----------------------------
# Extract Markdown
# -----------------------------

def extract_key_functions_section(markdown_text: str) -> str:
    if "## Key Functions" not in markdown_text:
        return ""

    section = markdown_text.split("## Key Functions")[1]

    # stop at next section if exists
    split_tokens = ["## Interactions", "## Future Extensibility"]
    for token in split_tokens:
        if token in section:
            section = section.split(token)[0]

    return section.strip()


# -----------------------------
# Builder
# -----------------------------

def build_function_specs(
    node_docs_dir: str,
    output_dir: str = "specs/function_specs"
):

    llm = StructuredLLM()
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(node_docs_dir):
        for file in files:
            if not file.endswith(".md"):
                continue

            file_path = os.path.join(root, file)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            key_section = extract_key_functions_section(content)

            if not key_section.strip():
                continue  # Skip folders without functions

            relative_path = os.path.relpath(file_path, node_docs_dir)
            yaml_output_path = os.path.join(
                output_dir,
                relative_path.replace(".md", ".yaml")
            )

            os.makedirs(os.path.dirname(yaml_output_path), exist_ok=True)

            system_prompt = """
You are converting conceptual function descriptions
into strict machine-readable function specifications.

Rules:
- Only use functions listed.
- Do NOT invent new functions.
- Infer reasonable data types based on tech stack.
- Output strict JSON only.
"""

            user_prompt = f"""
File Path:
{relative_path.replace('.md','')}

Conceptual Function Section:
{key_section}

Return JSON strictly matching this schema:

{{
  "file": "string",
  "functions": [
    {{
      "name": "string",
      "parameters": [
        {{
          "name": "string",
          "type": "string"
        }}
      ],
      "return_type": "string",
      "description": "string"
    }}
  ]
}}
"""

            spec: FileFunctionSpec = llm.call(
                prompt=system_prompt + "\n\n" + user_prompt,
                schema=FileFunctionSpec
            )

            with open(yaml_output_path, "w", encoding="utf-8") as f:
                yaml.dump(spec.model_dump(), f, sort_keys=False)

            print(f"Generated YAML for {relative_path}")

    print("\nAll function specs generated successfully.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--node-docs", required=True)
    parser.add_argument("--output", default="specs/function_specs")
    args = parser.parse_args()

    build_function_specs(
        node_docs_dir=args.node_docs,
        output_dir=args.output
    )