"""
Tests for lich dev (start/stop) helpers and doctor.
"""
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner

from lich.cli import app
import lich.commands.dev as dev_mod


class TestDevHelpers:
    def test_check_port_free_low_port(self):
        """Port 1 is never listening on a dev machine."""
        assert dev_mod._check_port(1) is False

    def test_check_port_returns_bool(self):
        """_check_port always returns a bool."""
        result = dev_mod._check_port(65535)
        assert isinstance(result, bool)

    def test_ensure_dirs_creates_pid_and_log(self, in_lich_project):
        """_ensure_dirs creates .pids and .logs directories."""
        # They are relative paths, so chdir matters
        dev_mod._ensure_dirs()
        assert dev_mod.PID_DIR.exists()
        assert dev_mod.LOG_DIR.exists()

    def test_pid_dir_constant(self):
        assert dev_mod.PID_DIR == Path(".pids")

    def test_log_dir_constant(self):
        assert dev_mod.LOG_DIR == Path(".logs")

    def test_stop_with_no_processes(self, runner: CliRunner, in_lich_project):
        """stop exits 0 when no PIDs exist and docker confirm is answered 'n'."""
        # Answer 'n' to "Stop Docker services?" confirm
        result = runner.invoke(app, ["stop"], input="n\n")
        assert result.exit_code == 0
        assert "Traceback" not in result.output

    def test_stop_help(self, runner: CliRunner):
        result = runner.invoke(app, ["stop", "--help"])
        assert result.exit_code == 0

    def test_start_help(self, runner: CliRunner):
        result = runner.invoke(app, ["start", "--help"])
        assert result.exit_code == 0

    def test_stop_stale_pid_is_cleaned(self, runner: CliRunner, in_lich_project):
        """stop gracefully handles a stale PID that no longer exists."""
        dev_mod._ensure_dirs()
        # Write a PID that definitely doesn't exist
        stale_pid_file = dev_mod.PID_DIR / "stale_service.pid"
        stale_pid_file.write_text("999999999")
        result = runner.invoke(app, ["stop"], input="n\n")
        assert result.exit_code == 0
        # PID file should be cleaned up
        assert not stale_pid_file.exists()


class TestDoctor:
    def test_doctor_help(self, runner: CliRunner):
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0

    def test_doctor_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 1
        assert "Not a Lich project" in result.output
        assert "Traceback" not in result.output

    def test_doctor_in_project_runs(self, runner: CliRunner, in_lich_project):
        """doctor runs without crash inside a Lich project."""
        result = runner.invoke(app, ["doctor"])
        # Produces diagnostics report; never a traceback
        assert "Traceback" not in result.output
        # Should include either PASS or FAIL checks
        assert ("PASS" in result.output) or ("FAIL" in result.output)

    def test_doctor_shows_score(self, runner: CliRunner, in_lich_project):
        """doctor output includes a health score."""
        result = runner.invoke(app, ["doctor"])
        assert "Health Score" in result.output or "%" in result.output

    def test_doctor_check_path_found(self, in_lich_project):
        """_check_path returns True for existing paths."""
        from lich.commands.doctor import _check_path
        ok, msg = _check_path(in_lich_project, "test dir")
        assert ok is True
        assert "Found" in msg

    def test_doctor_check_path_missing(self, temp_dir):
        """_check_path returns False for missing paths."""
        from lich.commands.doctor import _check_path
        ok, msg = _check_path(temp_dir / "nonexistent", "missing")
        assert ok is False
        assert "Missing" in msg
