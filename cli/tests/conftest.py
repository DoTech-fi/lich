"""
Shared fixtures for Lich CLI tests.
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from typer.testing import CliRunner

from lich.cli import app


@pytest.fixture
def runner() -> CliRunner:
    """Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def lich_project(temp_dir: Path) -> Path:
    """Create a mock Lich project structure."""
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    
    # Create .lich marker file
    (project_dir / ".lich").write_text('{"version": "1.3.0"}')
    
    # Create backend structure
    backend = project_dir / "backend"
    (backend / "internal" / "entities").mkdir(parents=True)
    (backend / "internal" / "services").mkdir(parents=True)
    (backend / "internal" / "ports").mkdir(parents=True)
    (backend / "internal" / "adapters" / "db").mkdir(parents=True)
    (backend / "internal" / "dto").mkdir(parents=True)
    (backend / "internal" / "events").mkdir(parents=True)
    (backend / "internal" / "listeners").mkdir(parents=True)
    (backend / "internal" / "jobs").mkdir(parents=True)
    (backend / "internal" / "policies").mkdir(parents=True)
    (backend / "api" / "http").mkdir(parents=True)
    (backend / "api" / "middleware").mkdir(parents=True)
    (backend / "tests" / "factories").mkdir(parents=True)
    (backend / "seeds").mkdir(parents=True)
    
    return project_dir


@pytest.fixture
def in_lich_project(lich_project: Path, monkeypatch):
    """Change to the Lich project directory."""
    monkeypatch.chdir(lich_project)
    return lich_project
