# pruning/models.py

from dataclasses import dataclass
from typing import List


@dataclass
class ParentMeta:
    name: str
    description: str
    full_path: str
    type: str
    mandatory: str


@dataclass
class LeafMeta:
    name: str
    description: str
    full_path: str
    mandatory: str
    depth: int
    parents: List[ParentMeta]
