# main_runner.py
# Run:
# python main_runner.py --json-file data/Web_Dev_Only.json --start-node "Core Application & Web Stacks" --initial-prompt "build a backend for online bakery shop that sells cakes"

import os
import json
import argparse
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from core.langgraph_runner import LangGraphRecorder
from core.llm_structured import StructuredLLM
from core.schemas import NodeDecision
from dotenv import load_dotenv
load_dotenv()
from langsmith import traceable

# ============================================================
# LLM CLIENT
# ============================================================

class LLMClient:
    def __init__(self, model: str = None):
        self.structured = StructuredLLM(model=model)

    @traceable(name="Choose Option")
    def choose_option(self, prompt: str, options: List[str]) -> NodeDecision:
        if not options:
            raise ValueError("No options available for selection.")

        options_text = "\n".join(f"- {opt}" for opt in options)

        formatted_prompt = f"""
        You are navigating a predefined decision tree.

        Your task is NOT to generate a project structure.
        Your task is ONLY to select ONE option from the provided list.

        USER REQUIREMENT:
        {prompt}

        AVAILABLE OPTIONS (choose exactly one):

        {options_text}

        Return ONLY valid JSON in this exact format:

        {{
          "choice": "exact_option_from_list",
          "rationale": "short explanation",
          "purpose": "what this option enables"
        }}

        The value of "choice" MUST be a string exactly matching one of the options above.
        Do NOT return a list.
        """

        response: NodeDecision = self.structured.call(
            prompt=formatted_prompt,
            schema=NodeDecision
        )

        # Robust semantic validation (case-insensitive match)

        choice_value = response.choice

        # If model returned list instead of string
        if isinstance(choice_value, list):
            if len(choice_value) == 1:
                choice_value = choice_value[0]
            else:
                raise ValueError(
                    f"Model returned multiple choices {choice_value}. Only one allowed."
                )

        choice_value = str(choice_value).strip()

        # Create lowercase lookup map
        option_lookup = {opt.lower(): opt for opt in options}

        if choice_value.lower() not in option_lookup:
            raise ValueError(
                f"Invalid choice '{choice_value}'. Must be one of {options}"
            )

        # Replace with canonical tree value
        response.choice = option_lookup[choice_value.lower()]

        return response


# ============================================================
# TREE UTILITIES
# ============================================================

def load_tree_from_file(filename: str) -> Any:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def find_key_recursive(obj: Any, target_key: str) -> Optional[Tuple[str, Any]]:
    if isinstance(obj, dict):
        if target_key in obj:
            return target_key, obj[target_key]
        for k, v in obj.items():
            res = find_key_recursive(v, target_key)
            if res:
                return res
    elif isinstance(obj, list):
        for item in obj:
            res = find_key_recursive(item, target_key)
            if res:
                return res
    return None


def extract_children_from_value(value: Any) -> List[Tuple[str, Any]]:
    children = []

    if isinstance(value, dict):
        for k, v in value.items():
            children.append((k, v))

    elif isinstance(value, list):
        for i, item in enumerate(value):
            if isinstance(item, dict) and len(item) == 1:
                key = list(item.keys())[0]
                children.append((key, item[key]))
            else:
                children.append((str(item), item))

    return children


# ============================================================
# TRAVERSAL
# ============================================================

@dataclass
class BranchState:
    path: List[str]
    node_name: str
    node_value: Any
    prompt: str

@traceable(name="Decision Traversal")
def traverse(tree: Any, start_node_name: str, llm: LLMClient, base_prompt: str):

    found = find_key_recursive(tree, start_node_name)
    if not found:
        raise ValueError(f"Start node '{start_node_name}' not found.")

    start_name, start_value = found

    recorder = LangGraphRecorder()

    branch = BranchState(
        path=[],
        node_name=start_name,
        node_value=start_value,
        prompt=base_prompt.strip()
    )

    completed_path = []

    while True:
        recorder.add_node(branch.node_name)
        children = extract_children_from_value(branch.node_value)

        if not children:
            recorder.mark_leaf(branch.node_name)
            completed_path = branch.path
            break

        child_names = [c[0] for c in children]

        # Build contextual prompt for this decision

        selected_stack_text = (
            "None yet"
            if not branch.path
            else " → ".join(branch.path)
        )

        decision_prompt = f"""
        User Requirement:
        {base_prompt}

        Selected Stack So Far:
        {selected_stack_text}

        Current Decision Node:
        {branch.node_name}

        Available Options:
        {", ".join(child_names)}

        Choose the single best option for the project.
        """

        decision = llm.choose_option(decision_prompt, child_names)

        chosen_name = decision.choice

        recorder.add_choice_rationale(
            parent_node=branch.node_name,
            choice=chosen_name,
            rationale=decision.rationale,
            purpose=decision.purpose
        )

        recorder.add_prompt_to_node(branch.node_name, decision_prompt)
        recorder.add_choice(branch.node_name, [chosen_name])

        matched = next((c for c in children if c[0] == chosen_name), None)

        if not matched:
            raise RuntimeError("Internal traversal mismatch.")

        child_name, child_value = matched

        recorder.add_edge(branch.node_name, child_name)

        recorder.add_prompt_to_edge(
            branch.node_name,
            child_name,
            decision_prompt
        )

        branch = BranchState(
            path=branch.path + [child_name],
            node_name=child_name,
            node_value=child_value,
            prompt=base_prompt
        )

    return completed_path, recorder


# ============================================================
# FINAL PROMPT BUILDER
# ============================================================

def build_clean_final_prompt(initial_prompt, tech_stack, recorder):

    prompt = f"""# Project Specification

## User Requirement
{initial_prompt.strip()}

## Selected Technology Stack

"""

    for i, tech in enumerate(tech_stack):
        prompt += f"### {i+1}. {tech}\n"

        parent = tech_stack[i-1] if i > 0 else None
        data = recorder.choice_rationales.get((parent, tech))

        if data:
            prompt += f"**Why chosen:** {data.get('rationale')}\n"
            prompt += f"**Purpose:** {data.get('purpose')}\n"

        prompt += "\n"

    prompt += "## Technology Stack Summary\n"
    prompt += " → ".join(tech_stack)

    return prompt


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--json-file", required=True)
    parser.add_argument("--start-node", required=True)
    parser.add_argument("--initial-prompt", required=True)
    parser.add_argument("--output-image", default="langgraph_output")
    parser.add_argument("--output-meta", default="langgraph_meta.json")
    args = parser.parse_args()

    tree = load_tree_from_file(args.json_file)
    llm = LLMClient()

    tech_stack, recorder = traverse(
        tree,
        args.start_node,
        llm,
        args.initial_prompt
    )

    outpath = recorder.render(args.output_image)

    # Save final prompt
    os.makedirs("specs", exist_ok=True)

    final_prompt = build_clean_final_prompt(
        args.initial_prompt,
        tech_stack,
        recorder
    )

    with open("specs/final_prompt.txt", "w", encoding="utf-8") as f:
        f.write(final_prompt)

    # Convert tuple keys to string keys for JSON safety
    formatted_choices = {}

    for (parent, choice), data in recorder.choice_rationales.items():
        key = f"{parent} -> {choice}"
        formatted_choices[key] = data

    # Save meta JSON
    meta = {
        "user_initial_prompt": args.initial_prompt,
        "tech_stack": tech_stack,
        "tech_stack_summary": " → ".join(tech_stack),
        "technology_choices": formatted_choices,
        "nodes": {
            n: {
                "is_leaf": recorder.nodes[n].is_leaf,
                "choices": recorder.node_choices.get(n, [])
            }
            for n in recorder.nodes
        },
        "edges": recorder.edges
    }

    with open("data/stack_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print("\nFINAL PROMPT SAVED TO specs/final_prompt.txt")
    print(f"Graph saved to: {outpath}")
    print(f"Meta saved to: {args.output_meta}")
