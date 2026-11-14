from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Agent, AgentVersion
from app.schemas import VersionCreate, VersionRead

router = APIRouter(prefix="/agents/{agent_id}/versions", tags=["versions"])


def get_agent_or_404(db: Session, agent_id: UUID, lock: bool = False) -> Agent:
    stmt = select(Agent).where(Agent.id == agent_id)
    if lock:
        # SELECT ... FOR UPDATE: other transactions that try to lock this
        # same agent row wait until we commit or roll back.
        stmt = stmt.with_for_update()
    agent = db.scalars(stmt).first()
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.post("", response_model=VersionRead, status_code=status.HTTP_201_CREATED)
def publish_version(agent_id: UUID, payload: VersionCreate, db: Session = Depends(get_db)):
    agent = get_agent_or_404(db, agent_id, lock=True)

    latest = db.scalar(
        select(func.max(AgentVersion.version_number)).where(AgentVersion.agent_id == agent.id)
    )
    version = AgentVersion(
        agent_id=agent.id,
        version_number=(latest or 0) + 1,
        config=payload.config,
    )

    try:
        db.add(version)
        db.flush()                          # sends the INSERT now, so version.id exists
        agent.current_version_id = version.id
        db.commit()                         # INSERT + pointer UPDATE commit together
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Version number conflict; retry the publish",
        )

    db.refresh(version)
    return version


@router.get("", response_model=list[VersionRead])
def list_versions(
    agent_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    get_agent_or_404(db, agent_id)
    stmt = (
        select(AgentVersion)
        .where(AgentVersion.agent_id == agent_id)
        .order_by(AgentVersion.version_number.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(stmt).all()


@router.get("/{version_number}", response_model=VersionRead)
def get_version(agent_id: UUID, version_number: int, db: Session = Depends(get_db)):
    get_agent_or_404(db, agent_id)
    version = db.scalars(
        select(AgentVersion).where(
            AgentVersion.agent_id == agent_id,
            AgentVersion.version_number == version_number,
        )
    ).first()
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return version