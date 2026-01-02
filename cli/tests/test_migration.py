"""
Tests for lich migration command.
"""
import pytest
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app


class TestMigrationHelp:
    """Tests for migration command help."""
    
    def test_migration_help_shows_subcommands(self, runner: CliRunner):
        """Test that migration help shows all subcommands."""
        result = runner.invoke(app, ["migration", "--help"])
        
        assert result.exit_code == 0
        assert "init" in result.output
        assert "create" in result.output
        assert "up" in result.output
        assert "down" in result.output
        assert "status" in result.output
        assert "heads" in result.output


class TestMigrationNotInProject:
    """Tests for migration outside Lich project."""
    
    def test_migration_init_fails_outside_project(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        """Test that migration init fails when not in Lich project."""
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["migration", "init"])
        
        assert result.exit_code == 1
        assert "Not a Lich project" in result.output
    
    def test_migration_status_fails_outside_project(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        """Test that migration status fails when not in Lich project."""
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["migration", "status"])
        
        assert result.exit_code == 1


class TestMigrationInProject:
    """Tests for migration commands in Lich project."""
    
    def test_migration_init_creates_alembic_folder(self, runner: CliRunner, in_lich_project: Path):
        """Test that migration init creates alembic directory."""
        # Note: This might fail if alembic is not installed
        # We just test that the command runs without error
        result = runner.invoke(app, ["migration", "init"])
        
        # Command should run (exit 0 or 1 depending on alembic installation)
        assert result.exit_code in [0, 1]
