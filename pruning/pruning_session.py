from core.llm_structured import StructuredLLM
from core.schemas import PruneDecision


class PruningSession:

    def __init__(self, system_context, model=None):
        self.messages = [
            {"role": "system", "content": system_context}
        ]
        self.llm = StructuredLLM(model=model)

    def evaluate_leaf(self, leaf_meta):
        prompt = f"""
    You are a strict pruning decision engine.

    Your task:
    Return ONLY a JSON object in this exact format:

    {{
      "decision": "KEEP or PRUNE",
      "reason": "short explanation"
    }}

    Rules:
    - If Mandatory is "yes" → decision MUST be KEEP.
    - If Mandatory is "no" → decide intelligently.
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

        decision = self.llm.call(
            prompt=prompt,
            schema=PruneDecision
        )

        return decision
