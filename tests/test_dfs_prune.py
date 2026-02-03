# tests/test_dfs_prune.py
# run with: python -m tests.test_dfs_prune

import json

from core.dfs_pruner import dfs_traverse
from specs.usage_manifest import init_manifest, save_manifest

print(">>> test_dfs_prune.py STARTED")

FINAL_PROMPT = """
Build a Spotify-like frontend using React.
Build tool: Vite
Styling: Tailwind CSS
State management: React Context
No backend.
"""

def run_dfs_pruning():
    # ---------- LOAD STRUCTURE ----------
    with open("data/folder_structure.json", "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Wrap into a DFS-compatible root node
    tree = raw

    print(">>> Tree prepared")

    # ---------- INIT OUTPUTS ----------
    prune_decisions = {
        "metadata": {
            "final_prompt": FINAL_PROMPT.strip(),
            "strategy": "dfs_leaf_only",
            "leaf_definition": "folder with no subfolders",
            "mandatory_rule": "always keep"
        },
        "decisions": {}
    }

    usage_manifest = init_manifest(FINAL_PROMPT)

    # ---------- RUN DFS ----------
    print(">>> Calling dfs_traverse")

    dfs_traverse(
        node=tree,
        path_stack=[],
        final_prompt=FINAL_PROMPT,
        prune_decisions=prune_decisions,
        usage_manifest=usage_manifest
    )

    print(">>> dfs_traverse finished")
    print(">>> Decisions collected:", len(prune_decisions["decisions"]))

    # ---------- WRITE FILES ----------
    with open("specs/prune_decisions.json", "w", encoding="utf-8") as f:
        json.dump(prune_decisions, f, indent=2)

    print(">>> prune_decisions.json written")

    pruned_paths = [
        path
        for path, data in prune_decisions["decisions"].items()
        if data["decision"] == "PRUNE"
    ]

    with open("specs/pruned_paths.json", "w", encoding="utf-8") as f:
        json.dump({"pruned_paths": pruned_paths}, f, indent=2)

    print(">>> pruned_paths.json written")

    save_manifest(usage_manifest, "specs/usage_manifest.json")
    print(">>> usage_manifest.json written")


# ---------- ACTUAL EXECUTION ----------
run_dfs_pruning()

print(">>> test_dfs_prune.py FINISHED")
