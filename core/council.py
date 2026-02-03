# core/council.py

def council_decide_leaf(
    final_prompt: str,
    path: str,
    leaf_description: dict,
    mandatory: bool
) -> dict:
    """
    Unified decision interface.
    Later replaced by multi-LLM council.
    """

    if mandatory:
        return {
            "decision": "KEEP",
            "description": leaf_description.get("purpose", ""),
            "reason": "Marked mandatory"
        }

    # TEMP logic (replace internals later)
    # IMPORTANT: signature must NEVER change
    return {
        "decision": "KEEP",   # or "PRUNE"
        "description": leaf_description.get("purpose", ""),
        "reason": "Relevant to final prompt"
    }
