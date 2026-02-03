import json
from core.dfs_pruner import dfs_prune, generate_yaml_from_paths
from specs.usage_manifest import init_manifest, save_manifest


FINAL_PROMPT = """
Frontend: React with Vite
Backend: Node.js with Express
Deployment: Docker
"""

if __name__ == "__main__":
    with open("folder_structure.json", "r", encoding="utf-8") as f:
        tree = json.load(f)

    tree["name"] = "project_root"

    accepted_paths = []
    manifest = init_manifest(FINAL_PROMPT)

    dfs_prune(
        node=tree,
        final_prompt=FINAL_PROMPT,
        path_stack=[],
        accepted_paths=accepted_paths,
        manifest=manifest
    )

    # YAML output
    yaml_output = generate_yaml_from_paths(accepted_paths)
    with open("accepted_paths.yaml", "w") as f:
        f.write(yaml_output)

    # Manifest output
    save_manifest(manifest)

    print("DFS pruning complete.")
    print("accepted_paths.yaml written")
    print("usage_manifest.json written")
