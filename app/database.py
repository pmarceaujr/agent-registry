import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://registry:registry_dev_pw@localhost:55432/registry",
)

# The engine manages a pool of connections.
# pool_pre_ping checks connection is alive before connecting.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a sesion
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# Every model class inherits from Base, so SQLAlchemy knows about all tables.
class Base(DeclarativeBase):
    pass


# FastAPI "dependency": opens a session for a request, always closes it after.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()