"""Tests for database initialization utilities"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from alembic.config import Config

from src.models.db_init import (
    get_alembic_config,
    init_database,
    create_migration,
    run_migrations,
    rollback_migration,
)


class TestDatabaseInit:
    """Test database initialization utilities"""

    def test_get_alembic_config(self) -> None:
        """Test getting Alembic configuration"""
        config = get_alembic_config()
        assert isinstance(config, Config)
        assert config.config_file_name is not None
        assert "alembic.ini" in str(config.config_file_name)

    def test_get_alembic_config_not_found(self) -> None:
        """Test error when alembic.ini not found"""
        with patch("src.models.db_init.Path") as mock_path:
            mock_path.return_value.parent.parent.parent = Path("/nonexistent")
            with pytest.raises(FileNotFoundError):
                get_alembic_config()

    def test_init_database(self) -> None:
        """Test database initialization"""
        with patch("src.models.db_init.DatabaseManager") as mock_db:
            mock_instance = Mock()
            mock_db.return_value = mock_instance

            init_database("sqlite:///:memory:")

            mock_db.assert_called_once_with("sqlite:///:memory:")
            mock_instance.create_tables.assert_called_once()

    def test_create_migration(self) -> None:
        """Test creating a migration"""
        with patch("src.models.db_init.get_alembic_config") as mock_config:
            with patch("src.models.db_init.command") as mock_command:
                mock_cfg = Mock()
                mock_config.return_value = mock_cfg

                create_migration("test migration")

                mock_command.revision.assert_called_once_with(
                    mock_cfg, message="test migration", autogenerate=True
                )

    def test_run_migrations(self) -> None:
        """Test running migrations"""
        with patch("src.models.db_init.get_alembic_config") as mock_config:
            with patch("src.models.db_init.command") as mock_command:
                mock_cfg = Mock()
                mock_config.return_value = mock_cfg

                run_migrations()

                mock_command.upgrade.assert_called_once_with(mock_cfg, "head")

    def test_rollback_migration_default(self) -> None:
        """Test rolling back to previous migration"""
        with patch("src.models.db_init.get_alembic_config") as mock_config:
            with patch("src.models.db_init.command") as mock_command:
                mock_cfg = Mock()
                mock_config.return_value = mock_cfg

                rollback_migration()

                mock_command.downgrade.assert_called_once_with(mock_cfg, "-1")

    def test_rollback_migration_specific(self) -> None:
        """Test rolling back to specific revision"""
        with patch("src.models.db_init.get_alembic_config") as mock_config:
            with patch("src.models.db_init.command") as mock_command:
                mock_cfg = Mock()
                mock_config.return_value = mock_cfg

                rollback_migration("abc123")

                mock_command.downgrade.assert_called_once_with(mock_cfg, "abc123")
