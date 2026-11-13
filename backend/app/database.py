import os
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# Keep the existing SQLite database for local development. Set DATABASE_URL
# in the deployment environment to use Supabase PostgreSQL.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./saloon.db")

engine_options = {}

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    # SQLAlchemy uses psycopg 3 explicitly; this avoids depending on psycopg2.
    if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
    elif SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

    parsed_url = urlparse(SQLALCHEMY_DATABASE_URL)
    is_supabase_transaction_pooler = (
        parsed_url.port == 6543
        and parsed_url.hostname
        and parsed_url.hostname.endswith(".pooler.supabase.com")
    )

    engine_options["pool_pre_ping"] = True
    if is_supabase_transaction_pooler:
        # Transaction poolers are intended for short-lived/serverless requests.
        # Psycopg's automatic prepared statements must be disabled in this mode.
        engine_options["poolclass"] = NullPool
        engine_options["connect_args"] = {"prepare_threshold": None}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
