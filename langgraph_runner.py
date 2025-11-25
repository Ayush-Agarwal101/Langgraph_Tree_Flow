# ---------- langgraph_runner.py ----------
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import graphviz


@dataclass
class TraversalNode:
    name: str
    prompts: List[str] = field(default_factory=list)
    is_leaf: bool = False


class LangGraphRecorder:
    def __init__(self):
        self.nodes: Dict[str, TraversalNode] = {}
        self.edges: List[Tuple[str, str]] = []
        self.edge_prompts: Dict[Tuple[str, str], str] = {}

    def add_node(self, name: str):
        if name not in self.nodes:
            self.nodes[name] = TraversalNode(name=name)

    def add_prompt_to_node(self, node_name: str, prompt: str):
        self.add_node(node_name)
        self.nodes[node_name].prompts.append(prompt)

    def mark_leaf(self, node_name: str):
        self.add_node(node_name)
        self.nodes[node_name].is_leaf = True

    def add_edge(self, from_node: str, to_node: str):
        self.add_node(from_node)
        self.add_node(to_node)
        self.edges.append((from_node, to_node))

    def add_prompt_to_edge(self, from_node: str, to_node: str, prompt: str):
        key = (from_node, to_node)
        self.edge_prompts[key] = prompt

    def add_choice(self, node_name: str, choices: List[str]):
        self.add_node(node_name)

    def render(self, filename: str = "langgraph.png", format: str = "png") -> str:
        dot = graphviz.Digraph(format=format)
        # Add nodes
        for name, node in self.nodes.items():
            label = name
            if node.is_leaf:
                dot.node(name, label=label, shape="box", style="filled", fillcolor="lightgrey")
            else:
                dot.node(name, label=label)
        # Add edges with small labels
        for (a, b) in self.edges:
            label = self.edge_prompts.get((a, b), "")
            short_label = (label[:60] + "...") if label and len(label) > 60 else label
            dot.edge(a, b, label=short_label)

        outpath = dot.render(filename, cleanup=True)
        print(f"LangGraph saved to {outpath}")
        return outpath
