# command to run: python main_runner.py --json-file Web_Dev_Only.json --start-node "Core Application & Web Stacks" --initial-prompt "I run an offline bakery shop and want to take it online so more people can discover and order from me."

import os
import json
import argparse
import time
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import requests
from langgraph_runner import LangGraphRecorder
from local_llama_client import call_llm, call_nvidia_llm

@dataclass
class LLMClient:
    def choose_options(self, prompt: str, options: List[str], max_choices: int = 1, timeout: int = 15) -> List[str]:
        """
        Uses ONLY local Ollama (llama2 or any installed model).
        """
        if not options:
            return []

        full_prompt = (
            "Reply ONLY with a JSON Object containing a list of choices.\n"
            f"Options: {options}\n"
            f"Prompt: {prompt}\n"
        )

        try:
            output = call_llm(full_prompt, model="llama2")
            # output = call_nvidia_llm(full_prompt, model="meta/llama3-70b")
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
    merge_mode: bool = False
    merged_choices: List[str] = field(default_factory=list)
    selected_children: List[str] = field(default_factory=list) # store multiple web servers


def build_step_prompt(base_prompt: str, selections: List[str], current_step: str, options: List[str]) -> str:
    sel_text = " using " + " + ".join(selections) if selections else ""
    composed = f"{base_prompt}{sel_text}.\nCurrent step: {current_step}.\nFrom the following options,you *must* recommend only one if there is a clearly best choice for the current task. If there isn’t a single best option, *then only* give me more options.\nOptions: {', '.join(options)}."
    return composed


def traverse(tree: Any, start_node_name: str, llm: LLMClient, base_prompt: str, max_branch_choices: int = 2) -> Tuple[List[BranchState], LangGraphRecorder]:

    FRAMEWORK_NODES = {
        # Frontend Frameworks
        "React",
        "Vue",
        "Angular",
        "Svelte",
        
        # Meta Frameworks (SSR/SSG)
        "Next.js",
        "Next.js (React)",
        "Next.js (SSG)",
        "Nuxt.js",
        "Nuxt.js (Vue)",
        "Nuxt.js (SSG)",
        "SvelteKit",
        "SvelteKit (Svelte)",
        "Gatsby",
        "Astro",
        "ISR / On-Demand Revalidation (Nuxt 3)",
        
        # PWA variants
        "React + Workbox",
        "Vue PWA",
        "Angular PWA",
        "AngularDart",
        "Flutter Web",
        
        # Build Tools
        "Vite",
        "vite",
        "Webpack",
        "Webpack / Create React App",
        "Parcel",
        "none",
        
        # Backend Frameworks - Python
        "Django",
        "Django Channels",
        "Flask",
        "FastAPI",
        "FastAPI (WebSockets)",
        "FastAPI SSE",
        
        # Backend Frameworks - Node.js
        "Express.js",
        "Express.js SSE",
        "NestJS",
        "NestJS (GraphQL)",
        "NestJS (WebSockets)",
        "Koa.js",
        "Hapi.js",
        
        # Backend Frameworks - Go
        "Gin",
        "Gin SSE",
        "Echo",
        "Fiber",
        "Fiber (WS)",
        "Chi",
        
        # Backend Frameworks - Java/Kotlin
        "Spring Boot",
        "Spring Boot (GraphQL)",
        "Spring Boot (Kotlin)",
        "Spring WebFlux",
        
        # Backend Frameworks - PHP
        "Laravel",
        "Symfony",
        
        # Backend Frameworks - Ruby
        "Ruby on Rails",
        "Sinatra",
    }

    FORCED_CHOICES = {
        "Core Application & Web Stacks": ["Web Development"],
        "Web Development": ["Frontend", "Backend"]
    }

    FIXED_CHOICES = {
        "Backend": ["REST", "GraphQL"],
    }
    
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

        # Ask LLM to pick
        updated_prompt_for_choice = branch.prompt + f"\nStep: choose {node_name}. Options: {', '.join(child_names)}"

        # Priority 1: FORCED_CHOICES (only these, no LLM)
        if node_name in FORCED_CHOICES:
            forced = FORCED_CHOICES[node_name]
            chosen = [c for c in forced if c in child_names]
            print(f"FORCED (exclusive) at '{node_name}': {chosen}")
            print(f"   ↳ Ignored options: {[c for c in child_names if c not in chosen]}")

        # Priority 2: FIXED_CHOICES (always include + LLM adds more)
        elif node_name in FIXED_CHOICES:
            fixed = FIXED_CHOICES[node_name]
            chosen = [c for c in fixed if c in child_names]
            print(f"FIXED (always included) at '{node_name}': {chosen}")
            
            remaining = [c for c in child_names if c not in chosen]
            
            if remaining and len(chosen) < max_branch_choices:
                additional_slots = max_branch_choices - len(chosen)
                
                # Update prompt to tell LLM what's already chosen
                additive_prompt = (
                    updated_prompt_for_choice 
                    + f"\n\nNote: {', '.join(chosen)} are already selected (required). "
                    + f"You may choose up to {additional_slots} additional option(s) from the remaining: {', '.join(remaining)}."
                    + f"\nIf none of the remaining options are needed, you can choose none."
                )
                
                llm_choices = llm.choose_options(additive_prompt, remaining, max_choices=additional_slots)
                
                if llm_choices:
                    chosen.extend(llm_choices)
                    print(f"LLM added: {llm_choices}")
                else:
                    print(f"LLM chose not to add more")
            
            elif remaining:
                print(f"Max choices ({max_branch_choices}) reached. Remaining ignored: {remaining}")
            else:
                print(f"No remaining options to choose from")

        # Priority 3: Normal LLM choice (no fixed or forced)
        else:
            chosen = llm.choose_options(updated_prompt_for_choice, child_names, max_choices=max_branch_choices)
            print(f"LLM chose at '{node_name}': {chosen}")

        # Fallback if nothing was chosen
        if not chosen:
            chosen = [child_names[0]]
            print(f"Fallback (nothing chosen) at '{node_name}': {chosen}")

        recorder.add_choice(node_name, chosen)

        # ---- MERGE MODE: We're inside a framework, collecting all subsequent choices ----
        if getattr(branch, "merge_mode", False):
            # Collect all chosen options into this framework's list
            branch.selected_children.extend(chosen)
            
            # Check if we can go deeper (are there grandchildren?)
            has_grandchildren = False
            for choice in chosen:
                matched = next(((n, v) for (n, v) in children if n == choice), None)
                if not matched:
                    matched = next(((n, v) for (n, v) in children if n.lower() == choice.lower()), None)
                if matched:
                    _, child_value = matched
                    grandchildren = extract_children_from_value(child_value)
                    if grandchildren:
                        has_grandchildren = True
                        break
            
            # If there are more levels, continue collecting
            if has_grandchildren:
                for choice in chosen:
                    matched = next(((n, v) for (n, v) in children if n == choice), None)
                    if not matched:
                        matched = next(((n, v) for (n, v) in children if n.lower() == choice.lower()), None)
                    if not matched:
                        continue
                    
                    child_name, child_value = matched
                    new_selections = branch.path + [child_name]
                    current_step_label = f"Choose {child_name}"
                    options_for_next = [c[0] for c in extract_children_from_value(child_value)]
                    new_prompt = branch.prompt  # Keep the same prompt, we're just collecting

                    new_branch = BranchState(
                        path=new_selections,
                        node_name=child_name,
                        node_value=child_value,
                        prompt=new_prompt,
                        history=branch.history + [(node_name, chosen)],
                        merge_mode=True,
                        merged_choices=branch.merged_choices,
                        selected_children=branch.selected_children.copy()
                    )

                    recorder.add_edge(node_name, child_name)
                    recorder.add_prompt_to_edge(node_name, child_name, f"Collecting options for {branch.merged_choices[0]}")
                    active.append(new_branch)
            else:
                # No more children - FINALIZE this framework branch with ONE prompt
                framework_name = branch.merged_choices[0]
                all_selections = " → ".join(branch.selected_children)
                
                # Create a special FINAL leaf node to show the complete prompt
                final_node_name = f"{framework_name}_FINAL"
                
                final_prompt = (
                    f"{'='*5}\n"
                    + f"FRAMEWORK: {framework_name}\n"
                    + f"SELECTED COMPONENTS: {all_selections}\n"
                    + f"{'='*5}\n"
                )

                # Add edge from current node to FINAL node with the complete prompt
                recorder.add_edge(node_name, final_node_name)
                recorder.add_prompt_to_edge(node_name, final_node_name, final_prompt)
                
                # Mark the FINAL node
                recorder.add_node(final_node_name)
                recorder.mark_framework(final_node_name)
                recorder.mark_leaf(final_node_name)
                
                completed.append(
                    BranchState(
                        path=branch.path + [final_node_name],
                        node_name=final_node_name,
                        node_value={},
                        prompt=final_prompt,
                        history=branch.history + [(node_name, chosen)],
                        merge_mode=True,
                        merged_choices=branch.merged_choices,
                        selected_children=branch.selected_children
                    )
                )
            
            continue

        # ---- CHECK IF CHOSEN CHILDREN ARE FRAMEWORKS (if yes, enable merge mode) ----
        framework_children = [c for c in chosen if c in FRAMEWORK_NODES]
        
        if framework_children:
            # One or more frameworks selected - create separate branch for EACH
            for framework_choice in framework_children:
                matched = next(((n, v) for (n, v) in children if n == framework_choice), None)
                if not matched:
                    matched = next(((n, v) for (n, v) in children if n.lower() == framework_choice.lower()), None)
                if not matched:
                    continue
                
                child_name, child_value = matched
                new_selections = branch.path + [child_name]
                
                framework_prompt = (
                    base_prompt 
                    + f"\n\n--- Starting framework branch: {child_name} ---"
                )

                # ENABLE MERGE MODE for this framework
                new_branch = BranchState(
                    path=new_selections,
                    node_name=child_name,
                    node_value=child_value,
                    prompt=framework_prompt,
                    history=branch.history + [(node_name, [child_name])],
                    merge_mode=True,
                    merged_choices=[child_name],  # Store the framework name
                    selected_children=[]  # Will collect all subsequent choices
                )

                recorder.add_edge(node_name, child_name)
                recorder.add_prompt_to_edge(node_name, child_name, f"Selected framework: {child_name}")
                active.append(new_branch)
            
            continue

        # ---- NORMAL BRANCHING (before reaching frameworks) ----
        for choice in chosen:
            matched = next(((n, v) for (n, v) in children if n == choice), None)
            if not matched:
                matched = next(((n, v) for (n, v) in children if n.lower() == choice.lower()), None)
            if not matched:
                continue
            
            child_name, child_value = matched
            new_selections = branch.path + [child_name]
            current_step_label = f"Choose {child_name}"
            options_for_next = [c[0] for c in extract_children_from_value(child_value)]
            new_prompt = build_step_prompt(base_prompt, new_selections, current_step_label, options_for_next)

            new_branch = BranchState(
                path=new_selections,
                node_name=child_name,
                node_value=child_value,
                prompt=new_prompt,
                history=branch.history + [(node_name, chosen)]
            )

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
        "nodes": {n: {"is_leaf": recorder.nodes[n].is_leaf, "is_framework": recorder.nodes[n].is_framework} for n in recorder.nodes},
        "edges": [{"from": a, "to": b, "prompt": recorder.edge_prompts.get((a, b), "")} for (a, b) in recorder.edges]
    }
    with open(args.output_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"Traversal finished. Graph saved to: {outpath}")
    print(f"Metadata saved to: {args.output_meta}")

