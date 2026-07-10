"""
Tests for lich ci command helpers.
"""
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.ci import _write_file_if_not_exists, _add_to_gitignore


class TestCIHelpers:
    def test_write_file_if_not_exists_creates(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        target = temp_dir / ".actrc"
        _write_file_if_not_exists(target, "content-a\n", ".actrc")
        assert target.read_text() == "content-a\n"

    def test_write_file_if_not_exists_preserves(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        target = temp_dir / ".actrc"
        target.write_text("original\n")
        # Without interactive confirmation (runner not involved), the file should be preserved.
        # _write_file_if_not_exists calls typer.confirm which raises an error in non-interactive
        # mode — test that the original content is intact when the file pre-exists.
        import unittest.mock as mock
        with mock.patch("lich.commands.ci.typer.confirm", return_value=False):
            _write_file_if_not_exists(target, "new-content\n", ".actrc")
        assert target.read_text() == "original\n"

    def test_add_to_gitignore(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        _add_to_gitignore([".secrets", ".ci-env"])
        content = Path(".gitignore").read_text()
        assert ".secrets" in content
        assert ".ci-env" in content


class TestCICLI:
    def test_ci_help_lists_apps(self, runner: CliRunner):
        result = runner.invoke(app, ["ci", "--help"])
        assert result.exit_code == 0
        for sub in ("setup", "backend", "web", "admin", "landing"):
            assert sub in result.output

    def test_ci_web_outside_project_fails(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["ci", "web"])
        assert result.exit_code == 1
