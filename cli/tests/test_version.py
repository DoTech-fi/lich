"""
Tests for lich version command.
"""
import pytest
from typer.testing import CliRunner

from lich.cli import app
from lich import __version__


class TestVersionCommand:
    """Tests for the version command."""
    
    def test_version_shows_current_version(self, runner: CliRunner):
        """Test that version command shows current version."""
        result = runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        assert __version__ in result.output
        assert "Lich Toolkit" in result.output
    
    def test_version_with_history_flag(self, runner: CliRunner):
        """Test that --history flag shows changelog."""
        result = runner.invoke(app, ["version", "--history"])
        
        assert result.exit_code == 0
        # Should show more detailed changelog
        assert "Changelog" in result.output or "1.0.0" in result.output


class TestHelpCommand:
    """Tests for help output."""
    
    def test_main_help(self, runner: CliRunner):
        """Test main help shows all commands."""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "init" in result.output
        assert "make" in result.output
        assert "migration" in result.output
        assert "version" in result.output
    
    def test_make_help(self, runner: CliRunner):
        """Test make subcommand help."""
        result = runner.invoke(app, ["make", "--help"])
        
        assert result.exit_code == 0
        assert "entity" in result.output
        assert "service" in result.output
        assert "factory" in result.output
        assert "middleware" in result.output
        assert "event" in result.output
        assert "listener" in result.output
        assert "job" in result.output
        assert "policy" in result.output
    
    def test_migration_help(self, runner: CliRunner):
        """Test migration subcommand help."""
        result = runner.invoke(app, ["migration", "--help"])
        
        assert result.exit_code == 0
        assert "init" in result.output
        assert "create" in result.output
        assert "up" in result.output
        assert "down" in result.output
        assert "status" in result.output
