# core/folder_graph_builder_pruned.py
# command to run: python core/folder_graph_builder.py --json-file pruned_structure.json --output specs/pruned_structure_graph

import json
import graphviz
import argparse


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def visualize_structure(data: dict, output_file: str = "folder_structure"):
    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="TB")
    dot.attr("node", fontname="Arial", fontsize="10")

    def add_node_recursive(node: dict, parent_id: str | None = None):
        node_type = node.get("type", "folder")
        name = node.get("name", "unknown")
        full_path = node.get("full_path", name)
        mandatory = node.get("mandatory", "no")
        description = node.get("description", "")

        # Unique ID for Graphviz
        node_id = full_path

        # Choose style based on type
        if node_type == "folder":
            shape = "box"
        else:
            shape = "note"

        # Color based on mandatory
        if mandatory == "yes":
            fillcolor = "lightblue"
        else:
            fillcolor = "lightgrey"

        # Create label
        label = f"{name}\n({node_type})"
        if description:
            label += f"\n{description}"

        dot.node(
            node_id,
            label=label,
            shape=shape,
            style="filled",
            fillcolor=fillcolor,
        )

        # Add edge from parent
        if parent_id:
            dot.edge(parent_id, node_id)

        # Recurse into children (LIST!)
        children = node.get("children", [])
        for child in children:
            add_node_recursive(child, node_id)

    # Start recursion
    add_node_recursive(data)

    # Render file
    output_path = dot.render(output_file, cleanup=True)
    print(f"Visualization saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize folder structure JSON")
    parser.add_argument("--json-file", required=True, help="Path to folder_structure.json")
    parser.add_argument("--output", default="folder_structure", help="Output PNG filename (without extension)")
    args = parser.parse_args()

    structure = load_json(args.json_file)
    visualize_structure(structure, args.output)
