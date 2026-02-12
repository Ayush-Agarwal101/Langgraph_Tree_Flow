# core/schemas.py

from pydantic import BaseModel, field_validator
from typing import List

# Node Decision Schema (Single Choice Mode)
class NodeDecision(BaseModel):
    choice: str
    rationale: str
    purpose: str

    @field_validator("choice")
    def validate_choice(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("choice must be non-empty string")
        return v.strip()

# Meta JSON Schema

class NodeRecord(BaseModel):
    node_path: str
    choice: str
    rationale: str
    purpose: str
    llm_prompt: str


class LangGraphMeta(BaseModel):
    original_user_prompt: str
    generated_at: str
    decisions: List[NodeRecord]
    tech_stack_summary: str

class PruneDecision(BaseModel):
    decision: str
    reason: str

    @field_validator("decision")
    def validate_decision(cls, v):
        if v.upper() not in ("KEEP", "PRUNE"):
            raise ValueError("decision must be KEEP or PRUNE")
        return v.upper()