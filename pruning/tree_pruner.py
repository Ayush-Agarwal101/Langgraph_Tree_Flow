def prune_tree(node, decisions):

    if node.get("is_leaf", False):
        d = decisions.get(node["full_path"])
        if d and d["decision"] == "PRUNE":
            return None
        return node

    new_children = []

    for child in node.get("children", []):
        pruned = prune_tree(child, decisions)
        if pruned:
            new_children.append(pruned)

    node["children"] = new_children

    if not new_children and not node.get("is_leaf", False):
        return None

    return node
