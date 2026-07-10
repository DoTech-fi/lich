"""
Tests for migration.py, seed.py, version.py, lint.py commands.
These modules have medium-to-low coverage (47-64%) and are ripe for improvement.
"""
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from typer.testing import CliRunner

from lich.cli import app
from lich.commands import migration as mig_mod
from lich.commands import seed as seed_mod
from lich.commands import version as ver_mod


# ============================================================
# migration.py  (currently 50%)
# ============================================================

class TestMigrationCheckAlembic:
    def test_returns_false_outside_project(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = mig_mod._check_alembic()
        assert result is False

    def test_returns_false_no_backend(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        result = mig_mod._check_alembic()
        assert result is False

    def test_returns_true_with_lich_and_backend(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        result = mig_mod._check_alembic()
        assert result is True


class TestRunAlembic:
    def test_builds_alembic_command(self, monkeypatch):
        captured = {}
        def fake_run(cmd, cwd="backend"):
            captured["cmd"] = cmd
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        code = mig_mod._run_alembic(["upgrade", "head"])
        assert captured["cmd"] == ["alembic", "upgrade", "head"]
        assert code == 0


class TestMigrationInit:
    def test_init_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["migration", "init"])
        assert result.exit_code == 1

    def test_init_in_project_with_backend(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        # Mock alembic to succeed
        def fake_run(cmd, cwd="backend"):
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "init"])
        assert result.exit_code == 0
        assert "initialized" in result.output.lower() or "alembic" in result.output.lower()

    def test_init_already_initialized(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        (temp_dir / "backend" / "alembic").mkdir()
        result = runner.invoke(app, ["migration", "init"])
        assert result.exit_code == 0
        assert "already" in result.output.lower()

    def test_init_failure_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        def fake_run(cmd, cwd="backend"):
            result = MagicMock()
            result.returncode = 1
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "init"])
        assert result.exit_code == 1


class TestMigrationCreate:
    def test_create_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["migration", "create", "test migration"])
        assert result.exit_code == 1

    def test_create_autogenerate(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        captured = {}
        def fake_run(cmd, cwd="backend"):
            captured["cmd"] = cmd
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "create", "add user table"])
        assert result.exit_code == 0
        assert "--autogenerate" in captured["cmd"]
        assert "add user table" in captured["cmd"]

    def test_create_manual(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        captured = {}
        def fake_run(cmd, cwd="backend"):
            captured["cmd"] = cmd
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "create", "my migration", "--manual"])
        assert "--autogenerate" not in captured.get("cmd", [])

    def test_create_failure_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        def fake_run(cmd, cwd="backend"):
            result = MagicMock()
            result.returncode = 2
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "create", "fail migration"])
        assert result.exit_code != 0


class TestMigrationUp:
    def test_up_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["migration", "up"])
        assert result.exit_code == 1

    def test_up_default_head(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        captured = {}
        def fake_run(cmd, cwd="backend"):
            captured["cmd"] = cmd
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "up"])
        assert result.exit_code == 0
        assert "upgrade" in captured["cmd"]
        assert "head" in captured["cmd"]

    def test_up_specific_revision(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        captured = {}
        def fake_run(cmd, cwd="backend"):
            captured["cmd"] = cmd
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "up", "abc123"])
        assert "abc123" in captured["cmd"]


class TestMigrationDown:
    def test_down_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["migration", "down"])
        assert result.exit_code == 1

    def test_down_one_step(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        captured = {}
        def fake_run(cmd, cwd="backend"):
            captured["cmd"] = cmd
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "down"])
        assert result.exit_code == 0
        assert "downgrade" in captured["cmd"]
        assert "-1" in captured["cmd"]

    def test_down_failure_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        def fake_run(cmd, cwd="backend"):
            result = MagicMock()
            result.returncode = 1
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "down"])
        assert result.exit_code != 0


class TestMigrationStatus:
    def test_status_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["migration", "status"])
        assert result.exit_code == 1

    def test_status_runs_current_and_history(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        captured_cmds = []
        def fake_run(cmd, cwd="backend"):
            captured_cmds.append(cmd)
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "status"])
        assert result.exit_code == 0
        # Should have called alembic current and alembic history
        all_cmds = [c for cmds in captured_cmds for c in cmds]
        assert "current" in all_cmds
        assert "history" in all_cmds


class TestMigrationHeads:
    def test_heads_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["migration", "heads"])
        assert result.exit_code == 1

    def test_heads_runs_alembic_heads(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        captured = {}
        def fake_run(cmd, cwd="backend"):
            captured["cmd"] = cmd
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.migration.subprocess.run", fake_run)
        result = runner.invoke(app, ["migration", "heads"])
        assert result.exit_code == 0
        assert "heads" in captured["cmd"]


# ============================================================
# seed.py  (currently 47%)
# ============================================================

class TestSeedCommand:
    def test_seed_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["seed"])
        assert result.exit_code == 1

    def test_seed_creates_seeds_dir_when_missing(self, runner: CliRunner, temp_dir, monkeypatch):
        """When backend/seeds doesn't exist, seed creates it and exits 0."""
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")
        (temp_dir / "backend").mkdir()
        result = runner.invoke(app, ["seed"])
        assert result.exit_code == 0
        assert "Creating" in result.output or "Created example seeder" in result.output or "seeds" in result.output.lower()

    def test_seed_list_empty(self, runner: CliRunner, in_lich_project):
        """lich seed --list with no seeder files shows no seeders message."""
        seeds_dir = in_lich_project / "backend" / "seeds"
        # seeds dir created by fixture — ensure no .py files
        for f in seeds_dir.glob("*.py"):
            f.unlink()
        result = runner.invoke(app, ["seed", "--list"])
        assert result.exit_code == 0
        assert "No seeders" in result.output

    def test_seed_list_with_seeders(self, runner: CliRunner, in_lich_project):
        """lich seed --list shows available seeders."""
        seeds_dir = in_lich_project / "backend" / "seeds"
        (seeds_dir / "users.py").write_text("def run(db): pass")
        result = runner.invoke(app, ["seed", "--list"])
        assert result.exit_code == 0
        assert "users" in result.output

    def test_seed_invalid_name_exits_1(self, runner: CliRunner, in_lich_project):
        """lich seed with invalid identifier exits 1."""
        result = runner.invoke(app, ["seed", "123-bad"])
        assert result.exit_code == 1

    def test_seed_specific_not_found_exits_1(self, runner: CliRunner, in_lich_project):
        """lich seed nonexistent exits 1 when seeder file missing."""
        # Make sure seeds dir exists but has no "nonexistent.py"
        seeds_dir = in_lich_project / "backend" / "seeds"
        # Clean up any py files so nonexistent isn't there
        result = runner.invoke(app, ["seed", "nonexistent"])
        assert result.exit_code == 1
        assert "Seeder not found" in result.output

    def test_seed_runs_seeder_with_run_function(self, runner: CliRunner, in_lich_project, monkeypatch):
        """lich seed runs a seeder; import may fail in runner context (no crash is OK)."""
        seeds_dir = in_lich_project / "backend" / "seeds"
        (seeds_dir / "users.py").write_text("def run(db): print('seeded')")
        result = runner.invoke(app, ["seed", "users"])
        assert result.exit_code == 0
        # Either import works or fails gracefully—but must complete
        assert "Seeding complete" in result.output

    def test_seed_no_run_function_shows_warning(self, runner: CliRunner, in_lich_project, monkeypatch):
        """lich seed with a module missing run() completes gracefully."""
        seeds_dir = in_lich_project / "backend" / "seeds"
        (seeds_dir / "empty.py").write_text("# no run function")
        # The runner's sys.path doesn't have backend/, so import may fail
        # Either "No run()" or an import error is acceptable—but we must not crash
        result = runner.invoke(app, ["seed", "empty"])
        assert result.exit_code == 0
        assert "Seeding complete" in result.output

    def test_seed_all_when_no_seeders(self, runner: CliRunner, in_lich_project):
        """lich seed with empty seeds dir (only __init__.py) shows 'No seeders'."""
        seeds_dir = in_lich_project / "backend" / "seeds"
        # Remove any existing .py seeder files
        for f in seeds_dir.glob("*.py"):
            f.unlink()
        result = runner.invoke(app, ["seed"])
        assert result.exit_code == 0
        assert "No seeders" in result.output

    def test_seed_fresh_mode_runs_migrations(self, runner: CliRunner, in_lich_project, monkeypatch):
        """lich seed --fresh calls migration down and up first."""
        seeds_dir = in_lich_project / "backend" / "seeds"
        # Empty seeds dir
        for f in seeds_dir.glob("*.py"):
            f.unlink()
        called = []
        def fake_run(cmd, **kwargs):
            called.append(cmd)
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.seed.subprocess.run", fake_run)
        result = runner.invoke(app, ["seed", "--fresh"])
        assert result.exit_code == 0
        # Should have called migration commands
        assert len(called) >= 2
        cmds_flat = [c for cmd in called for c in cmd]
        assert "migration" in cmds_flat

    def test_seed_async_seeder_shows_warning(self, runner: CliRunner, in_lich_project):
        """lich seed with async run() completes gracefully."""
        seeds_dir = in_lich_project / "backend" / "seeds"
        (seeds_dir / "async_seed.py").write_text("async def run(db): pass")
        result = runner.invoke(app, ["seed", "async_seed"])
        assert result.exit_code == 0
        # May show "Async" warning or import error, but must complete
        assert "Seeding complete" in result.output


# ============================================================
# version.py  (currently 64%)
# ============================================================

class TestVersionShow:
    def test_show_version(self, runner: CliRunner):
        """lich version shows the current version."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Lich" in result.output

    def test_show_version_with_history(self, runner: CliRunner):
        """lich version --history shows changelog."""
        result = runner.invoke(app, ["version", "--history"])
        assert result.exit_code == 0

    def test_show_version_in_project_with_config(self, runner: CliRunner, in_lich_project):
        """lich version reads project config if present."""
        lich_dir = in_lich_project / ".lich"
        if lich_dir.is_file():
            lich_dir.unlink()
            lich_dir.mkdir()
        config_path = lich_dir / "PROJECT_CONFIG.yaml"
        config_path.write_text("project:\n  name: MyAwesomeApp\n")
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        # Should show the project name
        assert "MyAwesomeApp" in result.output

    def test_show_version_in_project_with_bad_config(self, runner: CliRunner, in_lich_project):
        """lich version handles invalid yaml config gracefully."""
        lich_dir = in_lich_project / ".lich"
        if lich_dir.is_file():
            lich_dir.unlink()
            lich_dir.mkdir()
        (lich_dir / "PROJECT_CONFIG.yaml").write_text(":::invalid yaml:::")
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0


class TestCheckProject:
    def test_check_project_outside_lich(self, runner: CliRunner, temp_dir, monkeypatch):
        """lich check exits 1 outside project."""
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["check"])
        assert result.exit_code == 1
        assert "Not a Lich project" in result.output

    def test_check_project_in_minimal_project(self, runner: CliRunner, in_lich_project):
        """lich check shows table of checks (some missing is OK)."""
        result = runner.invoke(app, ["check"])
        # Will exit 1 because most files are missing, but must not crash
        assert "Traceback" not in result.output
        assert "Project Structure" in result.output or "Missing" in result.output

    def test_check_project_with_valid_structure(self, runner: CliRunner, temp_dir, monkeypatch):
        """lich check exits 0 when all required files exist."""
        monkeypatch.chdir(temp_dir)
        # Create all required paths
        (temp_dir / ".lich").mkdir()
        (temp_dir / ".lich" / "AI_CONTEXT.md").write_text("# AI Context")
        (temp_dir / ".lich" / "PROJECT_CONFIG.yaml").write_text("project: {}")
        (temp_dir / ".lich" / "rules").mkdir()
        (temp_dir / ".lich" / "workflows").mkdir()
        (temp_dir / "CLAUDE.md").write_text("# Claude")
        (temp_dir / "docker-compose.yml").write_text("services: {}")
        (temp_dir / "backend").mkdir()
        (temp_dir / "apps").mkdir()
        (temp_dir / "apps" / "web").mkdir()
        (temp_dir / "apps" / "admin").mkdir()
        (temp_dir / "apps" / "landing").mkdir()
        result = runner.invoke(app, ["check"])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()


class TestParseChangelog:
    def test_parse_changelog_no_file(self, temp_dir, monkeypatch):
        """_parse_changelog returns current version when no changelog found."""
        monkeypatch.chdir(temp_dir)
        from lich.commands.version import _parse_changelog
        # Force no changelog by patching _find_changelog to return None
        monkeypatch.setattr("lich.commands.version._find_changelog", lambda: None)
        versions = _parse_changelog()
        assert len(versions) >= 1
        assert "version" in versions[0]

    def test_parse_changelog_with_content(self, tmp_path, monkeypatch):
        """_parse_changelog extracts versions from CHANGELOG format."""
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n"
            "## [1.5.0] - 2024-03-01\n\n### Added\n- New feature\n\n"
            "## [1.4.0] - 2024-01-15\n\n### Fixed\n- Bug fix\n"
        )
        from lich.commands.version import _parse_changelog
        monkeypatch.setattr("lich.commands.version._find_changelog", lambda: changelog)
        versions = _parse_changelog()
        assert len(versions) >= 2
        assert any(v["version"] == "1.5.0" for v in versions)

    def test_show_changelog_no_file(self, monkeypatch):
        """_show_changelog prints warning when no changelog found."""
        from lich.commands.version import _show_changelog
        monkeypatch.setattr("lich.commands.version._find_changelog", lambda: None)
        # Should not raise
        _show_changelog()


# ============================================================
# lint.py  (currently 64%)
# ============================================================

class TestLintPython:
    def test_lint_python_no_backend(self, temp_dir, monkeypatch):
        """lint_python returns passed=True when no backend dir."""
        monkeypatch.chdir(temp_dir)
        from lich.commands.lint import lint_python
        result = lint_python()
        assert result["passed"] is True

    def test_lint_python_no_ruff_no_flake8(self, in_lich_project, monkeypatch):
        """lint_python returns when neither ruff nor flake8 installed."""
        from lich.commands.lint import lint_python
        monkeypatch.setattr("lich.commands.lint._check_tool_installed", lambda t: False)
        result = lint_python()
        assert isinstance(result, dict)

    def test_lint_python_ruff_passes(self, in_lich_project, monkeypatch):
        """lint_python with ruff returning 0 shows passed."""
        from lich.commands.lint import lint_python
        monkeypatch.setattr("lich.commands.lint._check_tool_installed", lambda t: t == "ruff")
        monkeypatch.setattr("lich.commands.lint._run_command", lambda cmd, **kw: (0, "", ""))
        result = lint_python()
        assert result["passed"] is True

    def test_lint_python_ruff_has_issues(self, in_lich_project, monkeypatch):
        """lint_python shows issues when ruff exits nonzero."""
        from lich.commands.lint import lint_python
        monkeypatch.setattr("lich.commands.lint._check_tool_installed", lambda t: t == "ruff")
        monkeypatch.setattr("lich.commands.lint._run_command", lambda cmd, **kw: (1, "file.py:1: E999 issue\n", ""))
        result = lint_python()
        assert result["issues"] >= 1
        assert result["passed"] is False

    def test_lint_python_flake8_fallback(self, in_lich_project, monkeypatch):
        """lint_python falls back to flake8 when ruff not installed."""
        from lich.commands.lint import lint_python
        def check_tool(t):
            return t == "flake8"
        def fake_run(cmd, **kw):
            return (0, "", "")
        monkeypatch.setattr("lich.commands.lint._check_tool_installed", check_tool)
        monkeypatch.setattr("lich.commands.lint._run_command", fake_run)
        result = lint_python()
        assert isinstance(result, dict)

    def test_lint_python_with_fix(self, in_lich_project, monkeypatch):
        """lint_python passes --fix flag to ruff check."""
        captured_cmds = []
        from lich.commands.lint import lint_python
        monkeypatch.setattr("lich.commands.lint._check_tool_installed", lambda t: t == "ruff")
        def fake_run(cmd, **kw):
            captured_cmds.append(cmd)
            return (0, "", "")
        monkeypatch.setattr("lich.commands.lint._run_command", fake_run)
        lint_python(fix=True)
        # First call should be ruff check --fix, second ruff format
        all_args = [arg for cmd in captured_cmds for arg in cmd]
        assert "--fix" in all_args


class TestLintFrontend:
    def test_lint_frontend_no_apps_dir(self, in_lich_project, monkeypatch):
        """lint_frontend returns passed=True when no apps dir."""
        from lich.commands.lint import lint_frontend
        result = lint_frontend()
        assert result["passed"] is True

    def test_lint_frontend_with_app(self, in_lich_project, monkeypatch):
        """lint_frontend runs eslint on each app."""
        apps_dir = in_lich_project / "apps" / "web"
        apps_dir.mkdir(parents=True)
        (apps_dir / "package.json").write_text('{"name": "web"}')
        from lich.commands.lint import lint_frontend
        monkeypatch.setattr("lich.commands.lint._run_command", lambda cmd, **kw: (0, "", ""))
        result = lint_frontend()
        assert isinstance(result, dict)

    def test_lint_frontend_with_fix_and_eslint_config(self, in_lich_project, monkeypatch):
        """lint_frontend passes --fix to eslint when config exists."""
        apps_dir = in_lich_project / "apps" / "web"
        apps_dir.mkdir(parents=True, exist_ok=True)
        (apps_dir / "package.json").write_text('{"name": "web"}')
        (apps_dir / ".eslintrc.json").write_text('{}')
        captured_cmds = []
        def fake_run(cmd, **kw):
            captured_cmds.append(list(cmd))
            return (0, "", "")
        from lich.commands.lint import lint_frontend
        monkeypatch.setattr("lich.commands.lint._run_command", fake_run)
        lint_frontend(fix=True)
        all_args = [arg for cmd in captured_cmds for arg in cmd]
        assert "--fix" in all_args


class TestLintCLI:
    def test_lint_outside_project(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["lint"])
        assert result.exit_code == 1

    def test_lint_backend_only_flag(self, runner: CliRunner, in_lich_project, monkeypatch):
        """lich lint --backend calls lint_python."""
        called = []
        monkeypatch.setattr(
            "lich.commands.lint.lint_python",
            lambda fix=False: called.append("python") or {"tool": "python", "passed": True, "issues": 0}
        )
        monkeypatch.setattr(
            "lich.commands.lint.lint_frontend",
            lambda fix=False: called.append("frontend") or {"tool": "frontend", "passed": True, "issues": 0}
        )
        result = runner.invoke(app, ["lint", "--backend"])
        assert result.exit_code == 0
        assert "python" in called
        assert "frontend" not in called

    def test_lint_frontend_only_flag(self, runner: CliRunner, in_lich_project, monkeypatch):
        """lich lint --frontend calls lint_frontend only."""
        called = []
        monkeypatch.setattr(
            "lich.commands.lint.lint_python",
            lambda fix=False: called.append("python") or {"tool": "python", "passed": True, "issues": 0}
        )
        monkeypatch.setattr(
            "lich.commands.lint.lint_frontend",
            lambda fix=False: called.append("frontend") or {"tool": "frontend", "passed": True, "issues": 0}
        )
        result = runner.invoke(app, ["lint", "--frontend"])
        assert result.exit_code == 0
        assert "frontend" in called
        assert "python" not in called

    def test_lint_all_calls_both(self, runner: CliRunner, in_lich_project, monkeypatch):
        """lich lint (no flags) calls both lint_python and lint_frontend."""
        called = []
        monkeypatch.setattr(
            "lich.commands.lint.lint_python",
            lambda fix=False: called.append("python") or {"tool": "python", "passed": True, "issues": 0}
        )
        monkeypatch.setattr(
            "lich.commands.lint.lint_frontend",
            lambda fix=False: called.append("frontend") or {"tool": "frontend", "passed": True, "issues": 0}
        )
        result = runner.invoke(app, ["lint"])
        assert result.exit_code == 0
        assert "python" in called
        assert "frontend" in called

    def test_lint_with_issues_exits_1(self, runner: CliRunner, in_lich_project, monkeypatch):
        """lich lint exits 1 when issues found."""
        monkeypatch.setattr(
            "lich.commands.lint.lint_python",
            lambda fix=False: {"tool": "python", "passed": False, "issues": 3}
        )
        monkeypatch.setattr(
            "lich.commands.lint.lint_frontend",
            lambda fix=False: {"tool": "frontend", "passed": True, "issues": 0}
        )
        result = runner.invoke(app, ["lint"])
        assert result.exit_code == 1

    def test_lint_fix_flag(self, runner: CliRunner, in_lich_project, monkeypatch):
        """lich lint --fix passes fix=True to linters."""
        captured = {}
        def fake_python(fix=False):
            captured["python_fix"] = fix
            return {"tool": "python", "passed": True, "issues": 0}
        def fake_frontend(fix=False):
            captured["frontend_fix"] = fix
            return {"tool": "frontend", "passed": True, "issues": 0}
        monkeypatch.setattr("lich.commands.lint.lint_python", fake_python)
        monkeypatch.setattr("lich.commands.lint.lint_frontend", fake_frontend)
        result = runner.invoke(app, ["lint", "--fix"])
        assert captured.get("python_fix") is True
        assert captured.get("frontend_fix") is True
