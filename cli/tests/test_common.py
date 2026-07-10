"""
Tests for lich.commands.common shared helpers.
"""
import pytest
import typer
from pathlib import Path

from lich.commands.common import (
    ensure_lich_project,
    is_lich_project,
    run_command,
    run_command_ok,
    check_tool_installed,
)


class TestProjectChecks:
    def test_ensure_lich_project_passes_in_project(self, in_lich_project):
        # .lich marker exists in fixture -> should not raise
        ensure_lich_project()

    def test_ensure_lich_project_passes_with_backend_only(self, temp_dir, monkeypatch):
        (temp_dir / "backend").mkdir()
        monkeypatch.chdir(temp_dir)
        ensure_lich_project()

    def test_ensure_lich_project_raises_outside_project(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        with pytest.raises(typer.Exit):
            ensure_lich_project()

    def test_is_lich_project_true_with_lich_marker(self, in_lich_project):
        assert is_lich_project() is True

    def test_is_lich_project_false_with_backend_only(self, temp_dir, monkeypatch):
        # is_lich_project mirrors make.py's stricter check: .lich only
        (temp_dir / "backend").mkdir()
        monkeypatch.chdir(temp_dir)
        assert is_lich_project() is False


class TestRunCommand:
    def test_run_command_success(self):
        code, out, err = run_command(["python3", "-c", "print('hello')"])
        assert code == 0
        assert "hello" in out
        assert err == ""

    def test_run_command_failure_code(self):
        code, out, err = run_command(["python3", "-c", "import sys; sys.exit(3)"])
        assert code == 3

    def test_run_command_missing_binary(self):
        code, out, err = run_command(["definitely-not-a-real-binary-xyz"])
        assert code == -1
        assert "Command not found" in err

    def test_run_command_respects_cwd(self, temp_dir):
        code, out, _ = run_command(
            ["python3", "-c", "import os; print(os.getcwd())"], cwd=temp_dir
        )
        assert code == 0
        assert str(temp_dir.resolve()) in out

    def test_run_command_ok_true_on_success(self):
        assert run_command_ok(["python3", "-c", "pass"], show_output=False) is True

    def test_run_command_ok_false_on_failure(self):
        assert run_command_ok(["python3", "-c", "import sys; sys.exit(1)"], show_output=False) is False

    def test_run_command_ok_false_on_missing_binary(self):
        assert run_command_ok(["definitely-not-a-real-binary-xyz"]) is False


class TestCheckToolInstalled:
    def test_existing_tool(self):
        assert check_tool_installed("python3") is True

    def test_missing_tool(self):
        assert check_tool_installed("definitely-not-a-real-binary-xyz") is False
