"""
models.py — SQLAlchemy ORM models for InsightCloud.
Defines the database schema using declarative base.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from database import Base


class User(Base):
    """
    User model representing registered InsightCloud users.

    Roles:
        - analyst: Can upload data, run queries, view insights
        - admin: Full access including user management
        - viewer: Read-only access to shared datasets
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
