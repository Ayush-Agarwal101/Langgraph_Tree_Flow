from .models import LeafMeta, ParentMeta


# ============================================================
# 1️⃣ Find shallowest terminal folder depth
# ============================================================

def find_shallowest_terminal_folder_depth(tree):

    min_depth = float("inf")

    def dfs(node, depth):

        nonlocal min_depth

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


# ============================================================
# 2️⃣ Trim tree to certain depth
# ============================================================

def trim_tree_to_depth(node, max_depth, current_depth=0):
    """
    Keep tree only until max_depth.
    Remove deeper children.
    Files are ignored in trimming logic.
    """

    if current_depth >= max_depth:
        node["children"] = []
        return node

    trimmed_children = []

    for child in node.get("children", []):
        if child.get("type") == "folder":
            trimmed_children.append(
                trim_tree_to_depth(child, max_depth, current_depth + 1)
            )
        else:
            # ignore files in trimming
            continue

    node["children"] = trimmed_children
    return node


# ============================================================
# 3️⃣ Extract prunable nodes (files + terminal folders)
# ============================================================

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

# ============================================================
# 4️⃣ Build System Context
# ============================================================

def build_system_context(user_requirement,
                         tech_stack_summary,
                         trimmed_tree_json):

    return f"""
You are a strict project structure pruning engine.

USER REQUIREMENT:
{user_requirement}

TECH STACK:
{tech_stack_summary}

COMMON FOLDER STRUCTURE CONTEXT:
{trimmed_tree_json}

Rules:
1. If mandatory == "yes" → decision MUST be KEEP.
2. If mandatory == "no" → decide intelligently.
3. Return ONLY valid JSON:
   {{
     "decision": "KEEP or PRUNE",
     "reason": "short explanation"
   }}
4. Do NOT output folder structure.
5. Do NOT output markdown.
6. Do NOT output extra text.
"""

