# pruning/structure_utils.py

from .models import LeafMeta, ParentMeta


# Find the shallowest terminal folder depth

def find_shallowest_terminal_folder_depth(tree):

    min_depth = float("inf")            # sets the minimum depth to infinity initially

    def dfs(node, depth):

        nonlocal min_depth              # Use the min_depth variable from the outer function.

        if node.get("type") != "folder":
            return

        children = node.get("children", [])

        has_subfolder = any(
            child.get("type") == "folder"
            for child in children
        )

        if not has_subfolder:
            min_depth = min(min_depth, depth)
            return

        for child in children:
            if child.get("type") == "folder":
                dfs(child, depth + 1)

    dfs(tree, 0)

    return min_depth


# Trim tree to certain depth

def trim_tree_to_depth(node, max_depth, current_depth=0):
    """
    Keep everything exactly as it is until depth max_depth.
    If a folder is deeper than max_depth, remove it and everything under it.
    Files are always preserved if they are within the allowed depth.
    """

    if current_depth > max_depth:
        return None

    trimmed_children = []

    for child in node.get("children", []):

        child_type = child.get("type")

        if child.get("type") == "folder":
            trimmed = trim_tree_to_depth(child, max_depth, current_depth + 1)

            if trimmed is not None:
                trimmed_children.append(trimmed)

        else:
            if current_depth + 1 <= max_depth:
                trimmed_children.append(child)

    node["children"] = trimmed_children
    return node


# Extract prunable nodes (files + terminal folders)

def extract_prunable_nodes(tree):
    """
    Extract:
    - All files
    - All terminal folders (no subfolders)
    Preserve JSON order.
    """

    results = []

    def dfs(node, parents):

        children = node.get("children", [])

        parent_meta = ParentMeta(
            name=node.get("name"),
            description=node.get("description", ""),
            full_path=node.get("full_path", ""),
            type=node.get("type"),
            mandatory=node.get("mandatory", "no")
        )

        new_parents = parents + [parent_meta]

        # Case 1: File
        if node.get("type") == "file":
            results.append(
                LeafMeta(
                    name=node.get("name"),
                    description=node.get("description", ""),
                    full_path=node.get("full_path", ""),
                    mandatory=node.get("mandatory", "no"),
                    depth=len(parents),
                    parents=parents
                )
            )
            return

        # Case 2: Folder
        if node.get("type") == "folder":

            has_subfolder = any(
                child.get("type") == "folder"
                for child in children
            )

            # Terminal folder
            if not has_subfolder:
                results.append(
                    LeafMeta(
                        name=node.get("name"),
                        description=node.get("description", ""),
                        full_path=node.get("full_path", ""),
                        mandatory=node.get("mandatory", "no"),
                        depth=len(parents),
                        parents=parents
                    )
                )
                return

            # Continue traversal
            for child in children:
                dfs(child, new_parents)

    dfs(tree, [])

    return results

# Build System Context

def build_system_context(user_requirement, tech_stack_summary, trimmed_tree_json):

    return f"""
You are an AI architecture pruning engine.

You will receive leaf node metadata one by one and must decide whether the node should remain in the project structure.

USER REQUIREMENT:
{user_requirement}

TECH STACK:
{tech_stack_summary}

BASE PROJECT STRUCTURE (COMMON CONTEXT):
{trimmed_tree_json}

Rules:
1. The base structure above represents the common architecture.
2. Leaf nodes provided later extend this structure.
3. If mandatory == "yes" → decision MUST be KEEP.
4. If mandatory == "no" → decide intelligently.

Return ONLY valid JSON:

{{
  "decision": "KEEP or PRUNE",
  "reason": "short explanation"
}}

Do NOT output markdown.
Do NOT output explanations outside JSON.
"""