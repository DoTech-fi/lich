"""
Tests for lich seed command.
"""
import pytest
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app


class TestSeedCommand:
    """Tests for seed command."""
    
    def test_seed_fails_outside_project(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        """Test that seed fails when not in Lich project."""
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["seed"])
        
        assert result.exit_code == 1
        assert "Not a Lich project" in result.output
    
    def test_seed_creates_seeds_folder(self, runner: CliRunner, in_lich_project: Path):
        """Test that seed creates seeds folder if missing."""
        # Remove seeds folder
        import shutil
        seeds_path = in_lich_project / "backend" / "seeds"
        shutil.rmtree(seeds_path, ignore_errors=True)
        
        result = runner.invoke(app, ["seed"])
        
        assert result.exit_code == 0
        assert seeds_path.exists()
        assert (seeds_path / "users.py").exists()
    
    def test_seed_list_seeders(self, runner: CliRunner, in_lich_project: Path):
        """Test that seed --list shows available seeders."""
        # Create a seeder
        seeds_path = in_lich_project / "backend" / "seeds"
        (seeds_path / "__init__.py").write_text("")
        (seeds_path / "products.py").write_text("def run(db): pass")
        
        result = runner.invoke(app, ["seed", "--list"])
        
        assert result.exit_code == 0
        assert "products" in result.output
