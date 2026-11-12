"""
Tests for lich upgrade command.
"""
import re
from pathlib import Path
from typer.testing import CliRunner

import pytest

from lich.cli import app
from lich.commands.common import get_local_template_path

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _plain(text: str) -> str:
    """Strip ANSI color codes so substring assertions survive Rich colorization.

    Rich splits option flags like ``--dry-run`` across color spans
    (``--dry`` + ``-run``) when the help output is colorized, which happens
    in CI but not in a plain local terminal.
    """
    return _ANSI_RE.sub("", text)


class TestUpgrade:
    def test_upgrade_help(self, runner: CliRunner):
        result = runner.invoke(app, ["upgrade", "--help"])
        assert result.exit_code == 0
        assert "--dry-run" in _plain(result.output)

    def test_upgrade_fails_outside_project(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["upgrade", "--local"])
        assert result.exit_code == 1
        assert "not a lich project" in result.output.lower()

    def test_upgrade_dry_run_local(self, runner: CliRunner, temp_dir, monkeypatch):
        """Dry run with --local uses the dev template (no network needed)."""
        assert get_local_template_path() is not None, "Local template must exist in dev checkout"
        # Need .lich as a directory for _backup_lich_dir (though dry-run exits before backup)
        monkeypatch.chdir(temp_dir)
        lich_dir = temp_dir / ".lich"
        lich_dir.mkdir()
        result = runner.invoke(app, ["upgrade", "--dry-run", "--local"])
        assert result.exit_code == 0
        assert "dry run" in result.output.lower()
        assert ".lich/rules" in result.output
