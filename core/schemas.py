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

class PruneDecision(BaseModel):
    decision: str
    reason: str

    @field_validator("decision")
    def validate_decision(cls, v):
        if v.upper() not in ("KEEP", "PRUNE"):
            raise ValueError("decision must be KEEP or PRUNE")
        return v.upper()