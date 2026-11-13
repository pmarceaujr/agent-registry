from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Agent
from app.schemas import AgentCreate, AgentRead

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
def create_agent(payload: AgentCreate, db: Session = Depends(get_db)):
    agent = Agent(name=payload.name, description=payload.description)
    db.add(agent)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An agent named '{payload.name}' already exists.",
        )
    db.refresh(agent)  # reload server-generated values (created_at, etc.)
    return agent


@router.get("", response_model=list[AgentRead])
def list_agents(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Agent).order_by(Agent.created_at, Agent.id).limit(limit).offset(offset)
    return db.scalars(stmt).all()