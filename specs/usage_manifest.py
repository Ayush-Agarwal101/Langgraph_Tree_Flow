# specs/usage_manifest.py

import json
from datetime import datetime


def init_manifest(final_prompt: str) -> dict:
    return {
        "final_prompt": final_prompt.strip(),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "records": []
    }


def record_decision(
    manifest: dict,
    path: str,
    decision: str,
    reason: str,
    model: str = "mistral"
):
    manifest["records"].append({
        "path": path,
        "decision": decision,
        "reason": reason,
        "model": model
    })


def save_manifest(manifest: dict, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
