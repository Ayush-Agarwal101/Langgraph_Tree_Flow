# usage_manifest.py

import json
from datetime import datetime
from typing import List, Dict


def init_manifest(project_prompt: str) -> Dict:
    return {
        "project_prompt": project_prompt.strip(),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "paths": {}
    }


def path_to_string(path_stack: List[Dict[str, str]]) -> str:
    return "/".join(p["name"] for p in path_stack)


def record_decision(
    manifest: Dict,
    path_stack: List[Dict[str, str]],
    decision: str,
    reason: str,
    model: str = "mistral"
):
    path_key = path_to_string(path_stack)

    manifest["paths"][path_key] = {
        "decision": decision,        # KEEP | PRUNE | CONDITIONAL (future)
        "reason": reason,
        "votes": {
            model: decision
        }
    }


def save_manifest(manifest: Dict, filename: str = "usage_manifest.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
