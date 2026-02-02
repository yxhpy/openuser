"""Database initialization and migration utilities"""

import os
from pathlib import Path

from alembic import command
from alembic.config import Config

from src.models.base import Base, DatabaseManager


def get_alembic_config() -> Config:
    """Get Alembic configuration"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    alembic_ini = project_root / "alembic.ini"

    if not alembic_ini.exists():
        raise FileNotFoundError(f"alembic.ini not found at {alembic_ini}")

    config = Config(str(alembic_ini))
    return config


def init_database(database_url: str) -> None:
    """
    Initialize database with all tables

    Args:
        database_url: Database connection URL
    """
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()
    print("Database tables created successfully")


def create_migration(message: str) -> None:
    """
    Create a new Alembic migration

    Args:
        message: Migration message
    """
    config = get_alembic_config()
    command.revision(config, message=message, autogenerate=True)
    print(f"Migration created: {message}")


def run_migrations() -> None:
    """Run all pending Alembic migrations"""
    config = get_alembic_config()
    command.upgrade(config, "head")
    print("Migrations applied successfully")


def rollback_migration(revision: str = "-1") -> None:
    """
    Rollback to a specific migration

    Args:
        revision: Target revision (default: -1 for previous)
    """
    config = get_alembic_config()
    command.downgrade(config, revision)
    print(f"Rolled back to revision: {revision}")
