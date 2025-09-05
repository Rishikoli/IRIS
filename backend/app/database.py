import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
 
# Load environment variables from a local .env file (backend/.env) if present
# This allows DATABASE_URL and other secrets to be provided without setting OS-level env vars.
try:
    from dotenv import load_dotenv  # type: ignore
    # Attempt to load ../../backend/.env relative to this file
    _ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    load_dotenv(dotenv_path=_ENV_PATH)
except Exception:
    # dotenv is optional; if not installed or .env missing, we fallback to OS env
    pass

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Please configure it to your PostgreSQL URL, e.g. "
        "postgresql+psycopg2://USER:PASS@HOST:5432/DBNAME"
    )

# For SQLite, need special connect args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# SQLAlchemy engine and session
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
    # Helps keep long-lived connections healthy (esp. with Postgres)
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Base declarative class
Base = declarative_base()

# Dependency for FastAPI routes
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
