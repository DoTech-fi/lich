"""
Tests for lich adopt command.
"""
import pytest
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app


class TestAdoptCommand:
    """Tests for adopt command."""
    
    def test_adopt_help(self, runner: CliRunner):
        """Test that adopt help shows options."""
        result = runner.invoke(app, ["adopt", "--help"])
        
        assert result.exit_code == 0
        # Check for key elements, case-insensitive
        output_lower = result.output.lower()
        assert "path" in output_lower
        assert "dry" in output_lower or "--dry-run" in result.output
    
    def test_adopt_nonexistent_path(self, runner: CliRunner, temp_dir: Path):
        """Test that adopt fails with nonexistent path."""
        result = runner.invoke(app, ["adopt", str(temp_dir / "nonexistent")])
        
        assert result.exit_code == 1
        assert "not exist" in result.output.lower() or "not found" in result.output.lower()
    
    def test_adopt_dry_run_analyzes_project(self, runner: CliRunner, temp_dir: Path):
        """Test that adopt --dry-run analyzes project without creating."""
        # Create a fake Python project
        project_dir = temp_dir / "my_python_project"
        project_dir.mkdir()
        
        # Create requirements.txt with FastAPI
        (project_dir / "requirements.txt").write_text("fastapi==0.100.0\nsqlalchemy==2.0.0\n")
        (project_dir / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()")
        
        result = runner.invoke(app, ["adopt", str(project_dir), "--dry-run"])
        
        assert result.exit_code == 0
        assert "Analysis" in result.output or "FastAPI" in result.output
