# core/schemas_project_blueprint.py

from pydantic import BaseModel
from typing import List, Optional


class ProjectMeta(BaseModel):
    name: str
    version: str
    language: str
    type: str
    description: str


class EntryPoint(BaseModel):
    name: str
    type: str
    description: str


class Component(BaseModel):
    name: str
    responsibility: str


class Architecture(BaseModel):
    pattern: str
    entry_points: List[EntryPoint]
    components: List[Component]
    data_flow_summary: str


class ExternalService(BaseModel):
    name: str
    role: str
    purpose: Optional[str] = None


class Infrastructure(BaseModel):
    external_services: List[ExternalService]


class Dependency(BaseModel):
    name: str
    version: Optional[str] = None
    purpose: str


class Dependencies(BaseModel):
    internal: List[Dependency]
    external: List[Dependency]


class ProjectBlueprint(BaseModel):
    project_meta: ProjectMeta
    architecture: Architecture
    infrastructure: Infrastructure
    dependencies: Dependencies