# pruning/pruning_session.py

from core.llm_structured import StructuredLLM
from core.schemas import PruneDecision


class PruningSession:

    def __init__(self, system_context, model=None):
        self.system_context = system_context
        self.llm = StructuredLLM(model=model)

    def evaluate_leaf(self, leaf_meta):
        prompt = f"""
    You are a strict pruning decision engine.

    Return ONLY a JSON object in this exact format:

    {{
      "decision": "KEEP or PRUNE",
      "reason": "short explanation"
    }}

    Rules:
    - If Mandatory is "yes" → decision MUST be KEEP.
    - You MUST ALWAYS include a short reason field.
    - If Mandatory is "yes", explain that it is mandatory.
    - If Mandatory is "no", decide intelligently.
    - Do NOT output folder structure.
    - Do NOT output extra fields.
    - Do NOT output markdown.
    - Do NOT output explanation outside JSON.

    Leaf Node:

    Name: {leaf_meta.name}
    Description: {leaf_meta.description}
    Full Path: {leaf_meta.full_path}
    Mandatory: {leaf_meta.mandatory}

    Parent Hierarchy:
    """

        for p in leaf_meta.parents:
            prompt += f"- {p.name}: {p.description}\n"

        return self.llm.call(
            prompt=prompt,
            schema=PruneDecision,
            system_context= self.system_context
        )
