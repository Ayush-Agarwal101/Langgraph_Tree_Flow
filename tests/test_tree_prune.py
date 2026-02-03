# tests/test_tree_prune.py
# run with: python -m tests.test_tree_prune

import json

from core.tree_pruner import extract_pruned_paths, prune_tree

print(">>> test_tree_prune.py STARTED")

# ---------- LOAD ORIGINAL TREE ----------
with open("data/folder_structure.json", "r", encoding="utf-8") as f:
    original_tree = json.load(f)

# ---------- LOAD PRUNE DECISIONS ----------
with open("specs/prune_decisions.json", "r", encoding="utf-8") as f:
    prune_decisions = json.load(f)

pruned_paths = extract_pruned_paths(prune_decisions)

print(f">>> Pruned paths count: {len(pruned_paths)}")

# ---------- RUN PRUNING ----------
pruned_tree = prune_tree(
    node=original_tree,
    path_stack=[],
    pruned_paths=pruned_paths
)

# ---------- SAVE RESULT ----------
with open("specs/pruned_structure.json", "w", encoding="utf-8") as f:
    json.dump(pruned_tree, f, indent=2)

print(">>> pruned_structure.json written")
print(">>> test_tree_prune.py FINISHED")
