"""
Tests for lich routes command.
"""
import pytest
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app


class TestRoutesCommand:
    """Tests for routes command."""
    
    def test_routes_fails_outside_project(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        """Test that routes fails when not in Lich project."""
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["routes"])
        
        assert result.exit_code == 1
        assert "Not a Lich project" in result.output
    
    def test_routes_shows_no_routes_message(self, runner: CliRunner, in_lich_project: Path):
        """Test that routes shows message when no API folder."""
        # Remove api/http folder
        import shutil
        api_path = in_lich_project / "backend" / "api" / "http"
        shutil.rmtree(api_path, ignore_errors=True)
        
        result = runner.invoke(app, ["routes"])
        
        assert result.exit_code == 0
        assert "No API routes found" in result.output or "missing" in result.output
    
    def test_routes_parses_router_files(self, runner: CliRunner, in_lich_project: Path):
        """Test that routes parses FastAPI router files."""
        # Create a sample router file
        api_file = in_lich_project / "backend" / "api" / "http" / "users.py"
        api_file.write_text('''
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def list_users():
    return []

@router.post("/")
async def create_user():
    return {}

@router.delete("/{id}")
async def delete_user(id: str):
    pass
''')
        
        result = runner.invoke(app, ["routes"])
        
        assert result.exit_code == 0
        assert "GET" in result.output
        assert "POST" in result.output
        assert "DELETE" in result.output
