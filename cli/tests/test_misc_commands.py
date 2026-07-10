"""
Tests for shell, test, middleware, production-ready commands and version_check.
"""
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.production_ready import AutoFixer, ProductionReadinessChecker


class TestHelpSurfaces:
    def test_shell_help(self, runner: CliRunner):
        result = runner.invoke(app, ["shell", "--help"])
        assert result.exit_code == 0

    def test_test_help(self, runner: CliRunner):
        result = runner.invoke(app, ["test", "--help"])
        assert result.exit_code == 0

    def test_middleware_help(self, runner: CliRunner):
        result = runner.invoke(app, ["middleware", "--help"])
        assert result.exit_code == 0
        # Should mention subcommands
        assert "enable" in result.output or "list" in result.output or "disable" in result.output

    def test_middleware_list_help(self, runner: CliRunner):
        result = runner.invoke(app, ["middleware", "list", "--help"])
        assert result.exit_code == 0

    def test_production_ready_help(self, runner: CliRunner):
        result = runner.invoke(app, ["production-ready", "--help"])
        assert result.exit_code == 0


class TestOutsideProjectGuards:
    def test_middleware_list_outside_project(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["middleware", "list"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_production_ready_outside_project(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["production-ready"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_shell_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["shell"])
        assert result.exit_code == 1
        assert "Not a Lich project" in result.output

    def test_test_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["test"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output


class TestMiddlewareInProject:
    def test_middleware_list_in_project_no_main_py(self, runner: CliRunner, in_lich_project):
        """middleware list exits 1 when backend/main.py doesn't exist."""
        result = runner.invoke(app, ["middleware", "list"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_middleware_list_with_main_py(self, runner: CliRunner, in_lich_project):
        """middleware list exits 0 when backend/main.py exists."""
        (in_lich_project / "backend").mkdir(exist_ok=True)
        (in_lich_project / "backend" / "main.py").write_text("# main.py\n")
        result = runner.invoke(app, ["middleware", "list"])
        assert result.exit_code == 0
        assert "Traceback" not in result.output

    def test_middleware_enable_unknown_name(self, runner: CliRunner, in_lich_project):
        """middleware enable with unknown name exits 1."""
        (in_lich_project / "backend").mkdir(exist_ok=True)
        (in_lich_project / "backend" / "main.py").write_text("")
        result = runner.invoke(app, ["middleware", "enable", "nonexistent"])
        assert result.exit_code == 1
        assert "Unknown middleware" in result.output


class TestAutoFixer:
    def test_read_file_missing_returns_empty(self, temp_dir):
        """ProductionReadinessChecker._read_file returns '' for missing files."""
        checker = ProductionReadinessChecker(temp_dir)
        assert checker._read_file(temp_dir / "nope.txt") == ""

    def test_auto_fixer_init_no_side_effects(self, temp_dir):
        """AutoFixer can be constructed with a path without side effects."""
        fixer = AutoFixer(temp_dir)
        assert fixer.project_path == temp_dir
        assert fixer.fixes_applied == []

    def test_auto_fixer_fix_secret_key_sets_strong_key(self, temp_dir):
        """fix_secret_key generates a new secret when current is weak."""
        env_file = temp_dir / ".env"
        env_file.write_text("SECRET_KEY=changeme\n")
        fixer = AutoFixer(temp_dir)
        changed = fixer.fix_secret_key()
        assert changed is True
        new_content = env_file.read_text()
        assert "changeme" not in new_content
        assert "SECRET_KEY=" in new_content

    def test_auto_fixer_fix_debug_false(self, temp_dir):
        """fix_debug_false sets DEBUG=false."""
        env_file = temp_dir / ".env"
        env_file.write_text("DEBUG=true\n")
        fixer = AutoFixer(temp_dir)
        changed = fixer.fix_debug_false()
        assert changed is True
        assert "DEBUG=false" in env_file.read_text()

    def test_auto_fixer_no_fix_when_already_strong(self, temp_dir):
        """fix_secret_key returns False when secret is already strong."""
        strong = "a" * 64
        env_file = temp_dir / ".env"
        env_file.write_text(f"SECRET_KEY={strong}\n")
        fixer = AutoFixer(temp_dir)
        changed = fixer.fix_secret_key()
        assert changed is False


class TestProductionReadyChecks:
    def test_production_ready_in_project_no_crash(self, runner: CliRunner, in_lich_project):
        """production-ready runs inside a project without crashing."""
        result = runner.invoke(app, ["production-ready"])
        assert "Traceback" not in result.output
        # Will exit 1 (project not production-ready) but must not traceback
        assert result.exit_code in (0, 1)

    def test_check_debug_false_detects_debug_true(self, temp_dir):
        """check_debug_false returns False when DEBUG=true."""
        (temp_dir / ".env").write_text("DEBUG=true\n")
        checker = ProductionReadinessChecker(temp_dir)
        result = checker.check_debug_false()
        assert result.passed is False

    def test_check_secret_key_short(self, temp_dir):
        """check_secret_key_length fails for short keys."""
        (temp_dir / ".env").write_text("SECRET_KEY=short\n")
        checker = ProductionReadinessChecker(temp_dir)
        result = checker.check_secret_key_length()
        assert result.passed is False


class TestVersionCheck:
    def test_check_compatibility_outside_project(self, temp_dir, monkeypatch):
        """check_compatibility returns immediately if not in a Lich project."""
        monkeypatch.chdir(temp_dir)
        from lich.version_check import check_compatibility
        # Should not raise, even without a .lich directory
        check_compatibility()

    def test_check_compatibility_in_project_no_version_file(self, in_lich_project):
        """check_compatibility handles missing .lich/lich.version gracefully."""
        from lich.version_check import check_compatibility
        # .lich exists but no version file inside it (it's a file not a dir in conftest)
        check_compatibility()

    def test_check_compatibility_with_version_file(self, in_lich_project):
        """check_compatibility parses a version file without crashing."""
        # Make .lich a directory with a version file
        lich_marker = in_lich_project / ".lich"
        lich_marker.unlink()  # remove the JSON file
        lich_marker.mkdir()
        (lich_marker / "lich.version").write_text("1.0.0")
        from lich.version_check import check_compatibility
        check_compatibility()

    def test_check_compatibility_never_raises(self, temp_dir, monkeypatch):
        """check_compatibility swallows all exceptions gracefully."""
        monkeypatch.chdir(temp_dir)
        from lich.version_check import check_compatibility
        # Patching network/file behavior should still not raise
        check_compatibility()
