# core/langgraph_runner.py
from dataclasses import dataclass
from typing import Dict, List, Tuple
import graphviz

@dataclass
class TraversalNode:
    name: str
    is_leaf: bool = False
    prompt: str = ""


class LangGraphRecorder:
    def __init__(self):
        self.nodes: Dict[str, TraversalNode] = {}
        self.edges: List[Tuple[str, str]] = []
        self.edge_prompts: Dict[Tuple[str, str], List[str]] = {}
        self.choice_rationales: Dict[Tuple[str, str], Dict[str, str]] = {}
        self.node_choices = {}
        # {(parent_node, choice): {"rationale": "...", "purpose": "..."}}

    def add_choice_rationale(self, parent_node: str, choice: str,
                             rationale: str, purpose: str):
        key = (parent_node, choice)
        self.choice_rationales[key] = {
            "rationale": rationale,
            "purpose": purpose
        }

    def add_node(self, name: str):
        if name not in self.nodes:
            self.nodes[name] = TraversalNode(name=name)

    def add_prompt_to_node(self, node_name: str, prompt: str):
        self.add_node(node_name)
        self.nodes[node_name].prompt = prompt

    def mark_leaf(self, node_name: str):
        self.add_node(node_name)
        self.nodes[node_name].is_leaf = True

    def add_edge(self, from_node: str, to_node: str):
        self.add_node(from_node)
        self.add_node(to_node)
        self.edges.append((from_node, to_node))

    def add_prompt_to_edge(self, from_node: str, to_node: str, prompt: str):
        key = (from_node, to_node)
        self.edge_prompts.setdefault(key, []).append(prompt)

    def add_choice(self, parent_node: str, choices):
        """
        Store selected child choices for a node.
        """
        self.node_choices.setdefault(parent_node, [])
        self.node_choices[parent_node].extend(choices)

    def render(self, filename: str = "langgraph.png",
               format: str = "png") -> str:

        dot = graphviz.Digraph(format=format)
        dot.attr(rankdir='TB')
        dot.attr('node', fontsize='11', fontname='Arial')
        dot.attr('edge', fontsize='9', fontname='Arial')

        # Add nodes
        for name, node in self.nodes.items():
            if node.is_leaf:
                dot.node(
                    name,
                    label=name,
                    shape="box",
                    style="filled",
                    fillcolor="lightgrey"
                )
            else:
                dot.node(name, label=name, shape="ellipse")

        # Add edges
        for (a, b) in self.edges:
            prompts = self.edge_prompts.get((a, b), [])

            if prompts:
                lines = []
                for i, p in enumerate(prompts):
                    formatted = p.replace("\n", "\\n")
                    tag = f"[{i+1}]" if len(prompts) > 1 else ""
                    lines.append(f"{tag} {formatted}".strip())
                label = "\\n".join(lines)
            else:
                label = ""

            dot.edge(a, b, label=label)

        outpath = dot.render(filename, cleanup=True)
        print(f"LangGraph saved to {outpath}")
        return outpath
