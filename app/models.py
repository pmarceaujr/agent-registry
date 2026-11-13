import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Points at the live version. use_alter=True tells Alembic to add this
    # foreign key AFTER both tables exist (the two tables reference each other).
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agent_versions.id", use_alter=True, name="fk_agents_current_version")
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    versions: Mapped[list["AgentVersion"]] = relationship(
        back_populates="agent",
        foreign_keys="AgentVersion.agent_id",
        cascade="all, delete-orphan",
    )
    current_version: Mapped["AgentVersion | None"] = relationship(
        foreign_keys=[current_version_id], post_update=True
    )


class AgentVersion(Base):
    __tablename__ = "agent_versions"
    # An agent can't have two "version 3"s
    __table_args__ = (UniqueConstraint("agent_id", "version_number", name="uq_agent_version_number"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer)
    # JSONB stores flexible config (model name, prompt, temperature...) and is queryable
    config: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    agent: Mapped["Agent"] = relationship(back_populates="versions", foreign_keys=[agent_id])