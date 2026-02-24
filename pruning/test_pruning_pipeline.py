import os
import json

from .structure_utils import (
    find_shallowest_terminal_folder_depth,
    trim_tree_to_depth,
    extract_prunable_nodes
)

from .tree_pruner import prune_tree
from .decision_tracker import DecisionTracker


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "folder_structure.json")


def load_tree():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_depth():
    tree = load_tree()
    depth = find_shallowest_terminal_folder_depth(tree)
    print("Shallowest terminal folder depth:", depth)


def test_trim():
    tree = load_tree()
    depth = find_shallowest_terminal_folder_depth(tree)
    trimmed = trim_tree_to_depth(tree, depth - 1)
    print("\nTrimmed structure:\n")
    print(json.dumps(trimmed, indent=2))


def test_metadata_extraction():
    tree = load_tree()
    nodes = extract_prunable_nodes(tree)

    print("\nTotal prunable nodes:", len(nodes))
    print("\nFirst few nodes:\n")

    for node in nodes[:5]:
        print("Name:", node.name)
        print("Path:", node.full_path)
        print("Mandatory:", node.mandatory)
        print("Parents:", [p.name for p in node.parents])
        print("-" * 40)


def test_prune_simulation():
    tree = load_tree()
    nodes = extract_prunable_nodes(tree)

    tracker = DecisionTracker()

    # Simulate keeping only first 3 nodes
    for node in nodes[:3]:
        tracker.add(
            node.full_path,
            "KEEP",
            "Test keep",
            node.mandatory
        )

    pruned = prune_tree(tree, tracker.all())

    print("\nPruned structure preview:\n")
    print(json.dumps(pruned, indent=2))


if __name__ == "__main__":

    print("\n=== TEST DEPTH ===")
    test_depth()

    print("\n=== TEST TRIM ===")
    test_trim()

    print("\n=== TEST METADATA EXTRACTION ===")
    test_metadata_extraction()

    print("\n=== TEST PRUNE SIMULATION ===")
    test_prune_simulation()
