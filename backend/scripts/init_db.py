#!/usr/bin/env python3
"""
Initialize the database schema for the IRIS backend using SQLAlchemy metadata.

- Respects DATABASE_URL env var; defaults to SQLite per app.database
- Imports all model modules to ensure they are registered to Base
- Creates all tables if they do not exist (idempotent)
"""
from __future__ import annotations
import os
import sys

# Ensure backend root is on sys.path so `app.*` imports work when running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine

# Import all model modules so that tables are registered with Base
import app.models  # noqa: F401
try:
    # Optional module with additional models
    import app.models.announcements  # noqa: F401
except Exception:
    pass


def main():
    print(f"Initializing database at: {os.getenv('DATABASE_URL', 'sqlite:///./iris_regtech.db')}")
    Base.metadata.create_all(bind=engine)
    print("Database schema initialized (create_all).")


if __name__ == "__main__":
    main()
