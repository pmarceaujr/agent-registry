import uuid
from datetime import datetime

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

    id: uuid.UUID
    name: str
    description: str | None
    current_version_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime