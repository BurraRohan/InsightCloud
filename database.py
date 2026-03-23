"""
database.py — SQLAlchemy database setup for InsightCloud.
Uses SQLite for local development. Configurable via DATABASE_URL in .env.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# Create engine with SQLite-specific settings
# check_same_thread=False is required for SQLite with Streamlit (multi-threaded)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Session factory — each call to SessionLocal() creates a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session.
    Yields a session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables defined in models.
    Call this once on application startup.
    """
    import models  # noqa: F401 — import to register models with Base
    Base.metadata.create_all(bind=engine)
