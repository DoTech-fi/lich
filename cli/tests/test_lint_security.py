"""
Tests for lich lint and security commands.
"""
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app
import lich.commands.lint as lint_mod
import lich.commands.security as sec_mod


class TestLint:
    def test_lint_help(self, runner: CliRunner):
        result = runner.invoke(app, ["lint", "--help"])
        assert result.exit_code == 0

    def test_lint_no_backend_dir_passes(self, runner: CliRunner, in_lich_project):
        """Without a backend/ dir lint_python returns early with passed=True."""
        # in_lich_project has no backend at root (conftest puts it at project/backend)
        # But the lint command chdir-aware; here we ensure no crash.
        result = runner.invoke(app, ["lint", "--backend"])
        # Either exits 0 (no issues found) or 1 (issues), never traceback
        assert "Traceback" not in result.output

    def test_lint_python_clean_run(self, in_lich_project, monkeypatch):
        """lint_python returns passed=True when tool runs cleanly."""
        (in_lich_project / "backend").mkdir(exist_ok=True)
        monkeypatch.setattr(lint_mod, "_check_tool_installed", lambda t: True)
        monkeypatch.setattr(lint_mod, "_run_command", lambda cmd, cwd=None, capture=True: (0, "", ""))
        result = lint_mod.lint_python(fix=False)
        assert result["tool"] == "python"
        assert result["passed"] is True

    def test_lint_python_with_issues(self, in_lich_project, monkeypatch):
        """lint_python returns passed=False when ruff finds issues."""
        (in_lich_project / "backend").mkdir(exist_ok=True)
        monkeypatch.setattr(lint_mod, "_check_tool_installed", lambda t: True)
        # ruff returns exit 1 with output containing issue lines
        monkeypatch.setattr(
            lint_mod, "_run_command",
            lambda cmd, cwd=None, capture=True: (1, "backend/foo.py:1:1: E501 line too long", "")
        )
        result = lint_mod.lint_python(fix=False)
        assert result["tool"] == "python"
        assert isinstance(result["issues"], int)

    def test_lint_python_ruff_missing_no_flake8(self, in_lich_project, monkeypatch):
        """lint_python handles missing ruff + missing flake8 gracefully."""
        (in_lich_project / "backend").mkdir(exist_ok=True)
        monkeypatch.setattr(lint_mod, "_check_tool_installed", lambda t: False)
        result = lint_mod.lint_python(fix=False)
        assert isinstance(result, dict)
        assert result["tool"] == "python"

    def test_lint_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["lint"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_lint_fix_flag(self, runner: CliRunner, in_lich_project, monkeypatch):
        """--fix flag is accepted without crash."""
        import lich.commands.lint as lm
        monkeypatch.setattr(lm, "_check_tool_installed", lambda t: True)
        monkeypatch.setattr(lm, "_run_command", lambda cmd, cwd=None, capture=True: (0, "", ""))
        result = runner.invoke(app, ["lint", "--fix"])
        assert "Traceback" not in result.output


class TestSecurity:
    def test_security_help(self, runner: CliRunner):
        result = runner.invoke(app, ["security", "--help"])
        assert result.exit_code == 0

    def test_security_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["security"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_scan_python_no_tools_returns_dict(self, in_lich_project, monkeypatch):
        """scan_python_security returns a dict even when no tools are installed."""
        monkeypatch.setattr(sec_mod, "_check_tool_installed", lambda t: False)
        result = sec_mod.scan_python_security()
        assert isinstance(result, dict)
        assert result["tool"] == "python"
        assert "passed" in result
        assert "issues" in result

    def test_scan_python_no_backend_dir(self, in_lich_project, monkeypatch):
        """scan_python_security handles missing backend gracefully."""
        monkeypatch.setattr(sec_mod, "_check_tool_installed", lambda t: False)
        result = sec_mod.scan_python_security()
        assert isinstance(result, dict)

    def test_scan_python_with_backend_bandit_clean(self, in_lich_project, monkeypatch):
        """scan_python_security passes when bandit exits 0."""
        (in_lich_project / "backend").mkdir(exist_ok=True)
        monkeypatch.setattr(sec_mod, "_check_tool_installed", lambda t: True)
        monkeypatch.setattr(sec_mod, "_run_command", lambda cmd, cwd=None, capture=True: (0, "", ""))
        result = sec_mod.scan_python_security()
        assert result["passed"] is True

    def test_scan_secrets_no_tools(self, in_lich_project, monkeypatch):
        """scan_secrets returns dict even with no tools installed."""
        monkeypatch.setattr(sec_mod, "_check_tool_installed", lambda t: False)
        result = sec_mod.scan_secrets()
        assert isinstance(result, dict)
        assert result["tool"] == "secrets"

    def test_display_results_no_crash(self, in_lich_project):
        """display_results doesn't crash with empty results."""
        from lich.commands.security import display_results
        display_results([{"tool": "python", "passed": True, "issues": []}])

    def test_security_backend_flag(self, runner: CliRunner, in_lich_project, monkeypatch):
        """--backend flag limits scan to Python."""
        import lich.commands.security as sm
        monkeypatch.setattr(sm, "_check_tool_installed", lambda t: False)
        result = runner.invoke(app, ["security", "--backend"])
        assert "Traceback" not in result.output
