# pruning/pruning_pipeline.py

import copy
from .structure_utils import (
    find_shallowest_terminal_folder_depth,
    trim_tree_to_depth,
    extract_prunable_nodes,
    build_system_context
)
from .pruning_session import PruningSession
from .decision_tracker import DecisionTracker
from .tree_pruner import prune_tree


def run_pruning_pipeline(tree,
                         user_requirement,
                         tech_stack):

    tree_copy = copy.deepcopy(tree)

    # STEP 1 — find shallowest terminal folder depth
    min_depth = find_shallowest_terminal_folder_depth(tree_copy)

    # STEP 2 — trim common structure
    trimmed_tree = trim_tree_to_depth(
        copy.deepcopy(tree_copy),
        min_depth - 1
    )

    # STEP 3 — extract all prunable nodes
    prunable_nodes = extract_prunable_nodes(tree_copy)

    system_context = build_system_context(
        user_requirement,
        tech_stack,
        trimmed_tree
    )

    session = PruningSession(system_context)
    tracker = DecisionTracker()

    # STEP 5 — evaluate one by one
    for node in prunable_nodes:

        decision = session.evaluate_leaf(node)

        if node.mandatory.lower() == "yes":
            final_decision = "KEEP"
        else:
            final_decision = decision.decision

        tracker.add(
            node.full_path,
            final_decision,
            decision.reason,
            node.mandatory
        )

    # STEP 6 — prune
    pruned_tree = prune_tree(tree_copy, tracker.all())

    return pruned_tree, tracker.all()
