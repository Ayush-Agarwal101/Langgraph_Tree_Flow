# core/langgraph_runner.py
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import graphviz


@dataclass
class TraversalNode:
    name: str
    is_leaf: bool = False
    is_framework: bool = False


class LangGraphRecorder:
    def __init__(self):
        self.nodes: Dict[str, TraversalNode] = {}
        self.edges: List[Tuple[str, str]] = []
        self.edge_prompts: Dict[Tuple[str, str], List[str]] = {}
        self.merge_mode_nodes: Dict[str, str] = {}  # node_name -> framework_name
        self.choice_rationales: Dict[Tuple[str, str], Dict[str, str]] = {}
        # Structure: {(parent_node, choice): {"rationale": "...", "purpose": "..."}}
    
    def add_choice_rationale(self, parent_node: str, choice: str, rationale: str, purpose: str):
        """
        Store the rationale and purpose for a choice.
        
        Args:
            parent_node: The node where choice was made
            choice: The option that was chosen
            rationale: Why this choice was made
            purpose: What this choice will be used for
        """
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

    def mark_leaf(self, node_name: str):
        self.add_node(node_name)
        self.nodes[node_name].is_leaf = True

    def mark_framework(self, node_name: str):
        """Mark a node as a framework node for special visualization."""
        self.add_node(node_name)
        self.nodes[node_name].is_framework = True

    def mark_merge_mode(self, node_name: str, framework_name: str):
        """Mark that this node is part of a framework's merge collection."""
        self.add_node(node_name)
        self.merge_mode_nodes[node_name] = framework_name

    def add_edge(self, from_node: str, to_node: str):
        self.add_node(from_node)
        self.add_node(to_node)
        self.edges.append((from_node, to_node))

    def add_prompt_to_edge(self, from_node: str, to_node: str, prompt: str):
        key = (from_node, to_node)
        self.edge_prompts.setdefault(key, []).append(prompt)

    def add_choice(self, node_name: str, choices: List[str]):
        self.add_node(node_name)

    def render(self, filename: str = "langgraph.png", format: str = "png") -> str:
        dot = graphviz.Digraph(format=format)
        dot.attr(rankdir='TB')  # Top to Bottom layout
        dot.attr('node', fontsize='11', fontname='Arial')
        dot.attr('edge', fontsize='9', fontname='Arial')
        
        # Detect framework nodes (check if they're marked or have final prompts in edges)
        framework_nodes = set()
        for name, node in self.nodes.items():
            if node.is_framework:
                framework_nodes.add(name)
        
        # Also check edges for FINAL prompts
        for (a, b), prompts in self.edge_prompts.items():
            for prompt in prompts:
                if "FINAL" in prompt or "final prompt" in prompt.lower():
                    framework_nodes.add(b)
        
        # Add nodes with different styles
        for name, node in self.nodes.items():
            # Style based on node type
            if name in framework_nodes:
                # Framework nodes with final prompts - highlighted in blue
                dot.node(name, label=name, shape="box", style="filled", 
                        fillcolor="lightblue", color="blue", penwidth="2.5")
            elif node.is_leaf:
                # Regular leaf nodes
                dot.node(name, label=name, shape="box", style="filled", 
                        fillcolor="lightgrey")
            else:
                # Regular nodes
                dot.node(name, label=name, shape="ellipse")
        
        # Add edges with labels
        for (a, b) in self.edges:
            prompts = self.edge_prompts.get((a, b), [])
            if prompts:
                lines = []
                for i, p in enumerate(prompts):
                    # Graphviz needs \\n for line breaks
                    formatted = p.replace("\n", "\\n")
                    
                    # Add tag for clarity if multiple prompts
                    if len(prompts) > 1:
                        tag = f"[{i+1}]"
                    else:
                        tag = ""
                    
                    lines.append(f"{tag} {formatted}".strip())
                
                label = "\\n".join(lines)
            else:
                label = ""

            # Check if edge leads to a framework node
            if b in framework_nodes:
                dot.edge(a, b, label=label, color="blue", penwidth="1.8")
            else:
                dot.edge(a, b, label=label)

        outpath = dot.render(filename, cleanup=True)
        print(f"LangGraph saved to {outpath}")
        return outpath