from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.routers import agents, versions

from app.database import get_db

app = FastAPI(title="Agent Registry", version="0.1.0")
app.include_router(agents.router, prefix="/v1")
app.include_router(versions.router, prefix="/v1")
app.include_router(versions.agent_actions, prefix="/v1")


@app.get("/health")
def health():
    return {"status": "API healthy and running"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    # Simplest possible query: proves the API can reach the database
    db.execute(text("SELECT 1"))
    return {"database": "Database connection healthy"}