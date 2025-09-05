from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

"""Database configuration.

Uses env var DATABASE_URL if provided, falling back to local SQLite for demo.
Automatically applies SQLite-only connect_args and enables pool_pre_ping for
managed databases like PostgreSQL to keep connections healthy.
"""

# Resolve database URL from environment (e.g., postgresql+psycopg://user:pass@host:5432/db)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./iris_regtech.db")

# Apply SQLite-specific connect args only when using SQLite
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()