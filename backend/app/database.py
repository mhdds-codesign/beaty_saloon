import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Vercel Functions have a read-only application filesystem. Use /tmp for the
# demo SQLite file there; locally keep the database inside the backend folder.
# NOTE: /tmp is ephemeral and local to a function instance. It is not durable
# storage and must not be used for production customer data.
if os.getenv("VERCEL") == "1":
    DATABASE_PATH = Path("/tmp/saloon.db")
else:
    DATABASE_PATH = Path(__file__).resolve().parents[1] / "saloon.db"

DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
