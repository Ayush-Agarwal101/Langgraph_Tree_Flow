"""
Universal LLM-driven Decision-Tree Workflow Engine
Files produced in this textdoc:
 - main_runner.py  (entrypoint)
 - langgraph_runner.py (recorder + renderer)

Features:
 - Works with nested-dict JSON trees (keys = node names; values = dict/list/primitive)
 - No special "name" or "children" fields required
 - Supports branching when the model returns multiple choices
 - Records prompts and edges and renders a Graphviz image
 - Supports three modes of LLM backend:
     1) Remote Gemini-like HTTP API (GEMINI_API_URL + GEMINI_API_KEY)
     2) Local Llama-compatible model via llama-cpp-python (LOCAL_LLM_MODEL_PATH)
     3) Deterministic dry-run fallback when neither is configured
 - Saves full metadata (edge -> full prompt) into a JSON file alongside the image

How to use (short):
  - Save this file as two files: main_runner.py and langgraph_runner.py (split by the marker)
  - pip install -r requirements (see instructions below)
  - python main_runner.py --json-file Web_Dev_Only.json --start-node "Core Application & Web Stacks"

"""

# ---------- main_runner.py ----------
import os
import json
import argparse
import time
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import requests

# Visualization helper (separate module below)
from langgraph_runner import LangGraphRecorder
from local_llama_client import call_llm

# ---------------- LLM Client ----------------
@dataclass
class LLMClient:
    def choose_options(self, prompt: str, options: List[str], max_choices: int = 1, timeout: int = 15) -> List[str]:
        """
        Uses ONLY local Ollama (llama2 or any installed model).
        """
        if not options:
            return []

        full_prompt = (
            "Reply ONLY with a JSON array of chosen option names.\n"
            f"Options: {options}\n"
            f"Prompt: {prompt}\n"
        )

        try:
            output = call_llm(full_prompt, model="llama2")
            choices = self._extract_json_array(output)
            if choices:
                return choices[:max_choices]

            fallback = self._extract_by_token_matching(output, options, max_choices)
            if fallback:
                return fallback

        except Exception as e:
            print(f"[LLM] Ollama call failed: {e}")

        return self._deterministic_choice(prompt, options, max_choices)

    @staticmethod
    def _extract_json_array(text: str) -> List[str]:
        import json, re
        m = re.search(r"\[.*?\]", text, flags=re.DOTALL)
        if not m:
            return []
        try:
            arr = json.loads(m.group(0))
            if isinstance(arr, list):
                return [str(x) for x in arr]
        except:
            return []
        return []

    @staticmethod
    def _extract_by_token_matching(text: str, options: List[str], max_choices: int) -> List[str]:
        import re
        found = []
        for opt in options:
            if re.search(rf"\b{re.escape(opt)}\b", text, flags=re.IGNORECASE):
                found.append(opt)
                if len(found) >= max_choices:
                    break
        return found

    @staticmethod
    def _deterministic_choice(prompt: str, options: List[str], max_choices: int) -> List[str]:
        prompt_lower = prompt.lower()
        matches = [o for o in options if o.lower() in prompt_lower]
        if matches:
            return matches[:max_choices]
        ordered = sorted(options, key=lambda s: (len(s), s))
        return ordered[:max_choices]


# ---------------- Tree utilities ----------------

def load_tree_from_file(filename: str) -> Any:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def find_key_recursive(obj: Any, target_key: str) -> Optional[Tuple[str, Any]]:
    """Search nested dicts for a key name equal to target_key. Returns (key, value) pair if found."""
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
    """Given a node value (dict|list|primitive) return list of (child_name, child_value).
    - If value is dict -> children are its keys; child_value is the corresponding value
    - If value is list -> children are list items; child_name is the stringified item (or index)
    - If primitive -> no children
    """
    children: List[Tuple[str, Any]] = []
    if isinstance(value, dict):
        for k, v in value.items():
            children.append((k, v))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            # If item is a dict with single key, use that key as name; else stringify
            if isinstance(item, dict) and len(item) == 1:
                key = list(item.keys())[0]
                children.append((key, item[key]))
            else:
                # treat list item as leaf option
                children.append((str(item), item))
    return children


# ---------------- Traversal ----------------

@dataclass
class BranchState:
    path: List[str]
    node_name: str
    node_value: Any
    prompt: str
    history: List[Tuple[str, List[str]]] = field(default_factory=list)


def build_step_prompt(base_prompt: str, selections: List[str], current_step: str, options: List[str]) -> str:
    sel_text = " using " + " + ".join(selections) if selections else ""
    composed = f"{base_prompt}{sel_text}.\nCurrent step: {current_step}.\nOptions: {', '.join(options)}."
    return composed


def traverse(tree: Any, start_node_name: str, llm: LLMClient, base_prompt: str, max_branch_choices: int = 2) -> Tuple[List[BranchState], LangGraphRecorder]:
    # locate start node anywhere in the tree
    found = find_key_recursive(tree, start_node_name)
    if not found:
        raise ValueError(f"Start node '{start_node_name}' not found in tree.")
    start_name, start_value = found

    recorder = LangGraphRecorder()

    initial_prompt = base_prompt.strip()
    root_branch = BranchState(path=[], node_name=start_name, node_value=start_value, prompt=initial_prompt)
    active = [root_branch]
    completed: List[BranchState] = []

    while active:
        branch = active.pop(0)
        node_name = branch.node_name
        node_value = branch.node_value

        # record node and prompt
        recorder.add_node(node_name)
        recorder.add_prompt_to_node(node_name, branch.prompt)

        children = extract_children_from_value(node_value)
        child_names = [c[0] for c in children]

        if not children:
            recorder.mark_leaf(node_name)
            completed.append(branch)
            continue

        # Ask LLM to pick among child_names
        updated_prompt_for_choice = branch.prompt + f"\nStep: choose {node_name}. Options: {', '.join(child_names)}"
        chosen = llm.choose_options(updated_prompt_for_choice, child_names, max_choices=max_branch_choices)
        if not chosen:
            chosen = [child_names[0]]

        recorder.add_choice(node_name, chosen)

        for choice in chosen:
            # find chosen child tuple
            matched = next(((n, v) for (n, v) in children if n == choice), None)
            if not matched:
                # fallback: try case-insensitive match
                matched = next(((n, v) for (n, v) in children if n.lower() == choice.lower()), None)
            if not matched:
                # if still not found, skip
                continue
            child_name, child_value = matched

            new_selections = branch.path + [child_name]
            current_step_label = f"Choose {child_name}"
            options_for_next = [c[0] for c in extract_children_from_value(child_value)]
            new_prompt = build_step_prompt(base_prompt, new_selections, current_step_label, options_for_next)

            new_branch = BranchState(path=new_selections, node_name=child_name, node_value=child_value, prompt=new_prompt, history=branch.history + [(node_name, chosen)])

            recorder.add_edge(node_name, child_name)
            recorder.add_prompt_to_edge(node_name, child_name, new_prompt)

            active.append(new_branch)

    return completed, recorder


# ---------------- CLI ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal LLM-driven decision tree runner")
    parser.add_argument("--json-file", required=True, help="Path to JSON file")
    parser.add_argument("--start-node", required=True, help="Name of start node (dict key somewhere in JSON)")
    parser.add_argument("--initial-prompt", default="Build a clothing e-commerce website backend.", help="Initial seed prompt")
    parser.add_argument("--output-image", default="langgraph_output.png", help="Output image filename")
    parser.add_argument("--output-meta", default="langgraph_meta.json", help="Output metadata JSON file")
    parser.add_argument("--max-choices", type=int, default=2, help="Max number of choices LLM may return")
    args = parser.parse_args()

    tree = load_tree_from_file(args.json_file)
    llm = LLMClient()

    completed_branches, recorder = traverse(tree, args.start_node, llm, args.initial_prompt, max_branch_choices=args.max_choices)

    # render graph and save metadata
    outpath = recorder.render(args.output_image)
    meta = {
        "completed_branches": [b.path for b in completed_branches],
        "nodes": {n: {"prompts": recorder.nodes[n].prompts, "is_leaf": recorder.nodes[n].is_leaf} for n in recorder.nodes},
        "edges": [{"from": a, "to": b, "prompt": recorder.edge_prompts.get((a, b), "")} for (a, b) in recorder.edges]
    }
    with open(args.output_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"Traversal finished. Graph saved to: {outpath}")
    print(f"Metadata saved to: {args.output_meta}")

