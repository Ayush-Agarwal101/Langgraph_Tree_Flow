# pruning/pruning_session.py

from core.llm_structured import StructuredLLM
from core.schemas import PruneDecision


class PruningSession:

    def __init__(self, system_context, model=None):
        self.system_context = system_context
        self.llm = StructuredLLM(model=model)

    def evaluate_leaf(self, leaf_meta, previous_decisions=None):
        prompt = "Leaf Node Metadata\n\n"

        if previous_decisions:
            prompt += "Previous pruning decisions:\n"

            for path, d in previous_decisions.items():
                prompt += f"- {path} → {d['decision']}\n"

            prompt += "\n"

        prompt += f"""
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
