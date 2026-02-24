import json
from pruning.pruning_pipeline import run_pruning_pipeline


if __name__ == "__main__":

    with open("data/folder_structure.json") as f:
        tree = json.load(f)

    user_requirement = "Build a backend for an online bakery shop"
    tech_stack = "React + Node.js + PostgreSQL"

    pruned_tree, decisions = run_pruning_pipeline(
        tree,
        user_requirement,
        tech_stack
    )

    print("\n=== DECISIONS ===")
    print(json.dumps(decisions, indent=2))

    with open("data/pruned_structure.json", "w") as f:
        json.dump(pruned_tree, f, indent=2)

    print("\nPruned structure saved to data/pruned_structure.json")
