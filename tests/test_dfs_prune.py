# tests/test_dfs_prune.py

# run - python -m tests.test_dfs_prune

import json

from core.dfs_pruner import dfs_traverse
from specs.usage_manifest import init_manifest, save_manifest


FINAL_PROMPT = """
Frontend: React + Vite
Backend: Node.js + Express
Deployment: Docker
"""


def test_dfs_pruning():
    with open("data/folder_structure.json", "r", encoding="utf-8") as f:
        tree = json.load(f)

    tree["name"] = "project_root"

    prune_decisions = {
        "metadata": {
            "strategy": "dfs_leaf_only",
            "leaf_definition": "folder with no subfolders",
            "mandatory_rule": "always keep"
        },
        "decisions": {}
    }

    usage_manifest = init_manifest(FINAL_PROMPT)

    dfs_traverse(
        node=tree,
        path_stack=[],
        final_prompt=FINAL_PROMPT,
        prune_decisions=prune_decisions,
        usage_manifest=usage_manifest
    )

    # Save outputs
    with open("specs/prune_decisions.json", "w", encoding="utf-8") as f:
        json.dump(prune_decisions, f, indent=2)

    save_manifest(usage_manifest, "specs/usage_manifest.json")

    # Generate pruned paths list
    pruned_paths = [
        path
        for path, data in prune_decisions["decisions"].items()
        if data["decision"] == "PRUNE"
    ]

    with open("specs/pruned_paths.json", "w", encoding="utf-8") as f:
        json.dump(
            {"pruned_paths": pruned_paths},
            f,
            indent=2
        )

    print(f"Pruned paths written: {len(pruned_paths)}")
