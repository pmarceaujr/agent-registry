from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Lowercase letters, digits and hyphens, starting with a letter or digit (e.g. "invoice-bot").
NAME_PATTERN = r"^[a-z0-9][a-z0-9-]*$"


class AgentCreate(BaseModel):
    """What a client sends to create an agent."""
    name: str = Field(min_length=3, max_length=100, pattern=NAME_PATTERN, examples=["invoice-bot"])
    description: str | None = Field(default=None, max_length=2000)


class AgentUpdate(BaseModel):
    """PATCH body: every field is optional. Only the fields the client sends get changed."""
    name: str | None = Field(default=None, min_length=3, max_length=100, pattern=NAME_PATTERN)
    description: str | None = Field(default=None, max_length=2000)


class AgentRead(BaseModel):
    """What the API returns."""
    model_config = ConfigDict(from_attributes=True)  # lets Pydantic read SQLAlchemy objects

    id: UUID
    name: str
    description: str | None
    current_version_id: UUID | None
    created_at: datetime
    updated_at: datetime

class VersionCreate(BaseModel):
    # Free-form JSON for now; min_length=1 rejects an empty {} with a 422
    config: dict[str, Any] = Field(min_length=1)


class VersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agent_id: UUID
    version_number: int
    config: dict[str, Any]
    created_at: datetime    

class RollbackRequest(BaseModel):
    version_number: int = Field(ge=1)   # 0 or negative -> 422


class RollbackResult(BaseModel):
    agent_id: UUID
    previous_version_number: int | None
    current_version_number: int
    current_version_id: UUID    