"""Base database configuration and declarative base"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class DatabaseManager:
    """Database connection and session management"""

    def __init__(self, database_url: str, echo: bool = False) -> None:
        """
        Initialize database manager

        Args:
            database_url: Database connection URL
            echo: Whether to echo SQL statements
        """
        self.engine = create_engine(database_url, echo=echo, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self) -> None:
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self) -> None:
        """Drop all tables in the database"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()


# Global database manager instance
_db_manager: DatabaseManager | None = None


def get_db():
    """
    Get database session dependency for FastAPI.

    Yields:
        Database session
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(
            database_url="sqlite:///./test.db",  # TODO: Load from config
            echo=False
        )
    session = _db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

