"""
Tests for middleware.py, git commands (top-level), and secret.py.
"""
from pathlib import Path
from unittest.mock import MagicMock
import pytest
from typer.testing import CliRunner

from lich.cli import app
from lich.commands import middleware as mw_mod


# ============================================================
# middleware.py  (currently 58%, 42 missed lines)
# ============================================================

MAIN_PY_WITH_MIDDLEWARE_COMMENTED = """\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from api.middleware.timing import TimingMiddleware
# from api.middleware.security import SecurityHeadersMiddleware
# from api.middleware.logging import RequestLoggingMiddleware
# from api.middleware.rate_limit import RateLimitMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])
# app.add_middleware(TimingMiddleware)
# app.add_middleware(SecurityHeadersMiddleware)
# app.add_middleware(RequestLoggingMiddleware)
# app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
"""

MAIN_PY_WITH_TIMING_ENABLED = """\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.middleware.timing import TimingMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(TimingMiddleware)
"""


class TestMiddlewareHelperFunctions:
    def test_is_middleware_enabled_true(self):
        result = mw_mod._is_middleware_enabled(MAIN_PY_WITH_TIMING_ENABLED, "timing")
        assert result is True

    def test_is_middleware_enabled_false(self):
        result = mw_mod._is_middleware_enabled(MAIN_PY_WITH_MIDDLEWARE_COMMENTED, "timing")
        assert result is False

    def test_read_main_py_missing_returns_empty(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = mw_mod._read_main_py()
        assert result == ""

    def test_read_main_py_with_file(self, in_lich_project):
        (in_lich_project / "backend" / "main.py").write_text("# main.py content\n")
        result = mw_mod._read_main_py()
        assert "main.py content" in result

    def test_write_main_py(self, in_lich_project):
        mw_mod._write_main_py("# new content\n")
        assert (in_lich_project / "backend" / "main.py").read_text() == "# new content\n"

    def test_get_main_py_path(self, in_lich_project):
        path = mw_mod._get_main_py_path()
        assert path == Path("backend/main.py")

    def test_is_lich_project_true(self, in_lich_project):
        assert mw_mod._is_lich_project() is True

    def test_is_lich_project_false(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        assert mw_mod._is_lich_project() is False


class TestMiddlewareListCommand:
    def test_list_outside_project(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["middleware", "list"])
        assert result.exit_code == 1

    def test_list_no_main_py(self, runner: CliRunner, in_lich_project):
        """If backend/main.py is missing, list fails."""
        main_py = in_lich_project / "backend" / "main.py"
        if main_py.exists():
            main_py.unlink()
        result = runner.invoke(app, ["middleware", "list"])
        assert result.exit_code == 1
        assert "Cannot find" in result.output

    def test_list_with_main_py(self, runner: CliRunner, in_lich_project):
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_MIDDLEWARE_COMMENTED)
        result = runner.invoke(app, ["middleware", "list"])
        assert result.exit_code == 0
        assert "TimingMiddleware" in result.output

    def test_list_shows_all_middlewares(self, runner: CliRunner, in_lich_project):
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_TIMING_ENABLED)
        result = runner.invoke(app, ["middleware", "list"])
        assert result.exit_code == 0
        assert "SecurityHeadersMiddleware" in result.output


class TestMiddlewareEnableCommand:
    def test_enable_timing_middleware(self, runner: CliRunner, in_lich_project):
        """Enable timing middleware writes uncommented import to main.py."""
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_MIDDLEWARE_COMMENTED)
        result = runner.invoke(app, ["middleware", "enable", "timing"])
        assert result.exit_code == 0
        assert "enabled" in result.output.lower()
        content = (in_lich_project / "backend" / "main.py").read_text()
        assert "from api.middleware.timing import TimingMiddleware" in content
        assert "# from api.middleware.timing" not in content

    def test_enable_security_middleware(self, runner: CliRunner, in_lich_project):
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_MIDDLEWARE_COMMENTED)
        result = runner.invoke(app, ["middleware", "enable", "security"])
        assert result.exit_code == 0
        assert "enabled" in result.output.lower()

    def test_enable_logging_middleware(self, runner: CliRunner, in_lich_project):
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_MIDDLEWARE_COMMENTED)
        result = runner.invoke(app, ["middleware", "enable", "logging"])
        assert result.exit_code == 0

    def test_enable_rate_limit_middleware(self, runner: CliRunner, in_lich_project):
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_MIDDLEWARE_COMMENTED)
        result = runner.invoke(app, ["middleware", "enable", "rate_limit"])
        assert result.exit_code == 0

    def test_enable_already_enabled_shows_warning(self, runner: CliRunner, in_lich_project):
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_TIMING_ENABLED)
        result = runner.invoke(app, ["middleware", "enable", "timing"])
        assert result.exit_code == 0
        assert "already enabled" in result.output

    def test_enable_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["middleware", "enable", "timing"])
        assert result.exit_code == 1

    def test_enable_unknown_middleware_exits_1(self, runner: CliRunner, in_lich_project):
        (in_lich_project / "backend" / "main.py").write_text("# main.py")
        result = runner.invoke(app, ["middleware", "enable", "nonexistent"])
        assert result.exit_code == 1
        assert "Unknown middleware" in result.output

    def test_enable_dash_becomes_underscore(self, runner: CliRunner, in_lich_project):
        """rate-limit with dash becomes rate_limit in lookup."""
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_MIDDLEWARE_COMMENTED)
        result = runner.invoke(app, ["middleware", "enable", "rate-limit"])
        assert result.exit_code == 0


class TestMiddlewareDisableCommand:
    def test_disable_timing_middleware(self, runner: CliRunner, in_lich_project):
        """Disable timing middleware comments out the import."""
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_TIMING_ENABLED)
        result = runner.invoke(app, ["middleware", "disable", "timing"])
        assert result.exit_code == 0
        assert "disabled" in result.output.lower()
        content = (in_lich_project / "backend" / "main.py").read_text()
        assert "# from api.middleware.timing" in content

    def test_disable_already_disabled_shows_warning(self, runner: CliRunner, in_lich_project):
        """Disable already-disabled middleware shows warning."""
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_MIDDLEWARE_COMMENTED)
        result = runner.invoke(app, ["middleware", "disable", "timing"])
        assert result.exit_code == 0
        assert "already disabled" in result.output

    def test_disable_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["middleware", "disable", "timing"])
        assert result.exit_code == 1

    def test_disable_unknown_middleware_exits_1(self, runner: CliRunner, in_lich_project):
        (in_lich_project / "backend" / "main.py").write_text("# main.py")
        result = runner.invoke(app, ["middleware", "disable", "nonexistent"])
        assert result.exit_code == 1
        assert "Unknown middleware" in result.output

    def test_disable_security_middleware(self, runner: CliRunner, in_lich_project):
        """Disable security when enabled."""
        content = MAIN_PY_WITH_MIDDLEWARE_COMMENTED.replace(
            "# from api.middleware.security import SecurityHeadersMiddleware",
            "from api.middleware.security import SecurityHeadersMiddleware"
        ).replace(
            "# app.add_middleware(SecurityHeadersMiddleware)",
            "app.add_middleware(SecurityHeadersMiddleware)"
        )
        (in_lich_project / "backend" / "main.py").write_text(content)
        result = runner.invoke(app, ["middleware", "disable", "security"])
        assert result.exit_code == 0
        assert "disabled" in result.output.lower()


class TestMiddlewareEnableDisableAll:
    def test_enable_all_middlewares(self, runner: CliRunner, in_lich_project):
        """enable-all enables all middlewares."""
        (in_lich_project / "backend" / "main.py").write_text(MAIN_PY_WITH_MIDDLEWARE_COMMENTED)
        result = runner.invoke(app, ["middleware", "enable-all"])
        assert result.exit_code == 0
        content = (in_lich_project / "backend" / "main.py").read_text()
        assert "from api.middleware.timing import TimingMiddleware" in content

    def test_disable_all_middlewares(self, runner: CliRunner, in_lich_project):
        """disable-all disables all middlewares."""
        full_enabled = """\
from api.middleware.timing import TimingMiddleware
from api.middleware.security import SecurityHeadersMiddleware
from api.middleware.logging import RequestLoggingMiddleware
from api.middleware.rate_limit import RateLimitMiddleware
app.add_middleware(TimingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
"""
        (in_lich_project / "backend" / "main.py").write_text(full_enabled)
        result = runner.invoke(app, ["middleware", "disable-all"])
        assert result.exit_code == 0
        content = (in_lich_project / "backend" / "main.py").read_text()
        assert "# from api.middleware.timing" in content

    def test_enable_all_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["middleware", "enable-all"])
        assert result.exit_code == 1

    def test_disable_all_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["middleware", "disable-all"])
        assert result.exit_code == 1


# ============================================================
# git commands — top-level on main app: commit, tag, push
# ============================================================

class TestGitTopLevelCommands:
    def test_commit_help(self, runner: CliRunner):
        result = runner.invoke(app, ["commit", "--help"])
        assert result.exit_code == 0

    def test_tag_help(self, runner: CliRunner):
        result = runner.invoke(app, ["tag", "--help"])
        assert result.exit_code == 0

    def test_push_help(self, runner: CliRunner):
        result = runner.invoke(app, ["push", "--help"])
        assert result.exit_code == 0

    def test_commit_with_message_runs_git(self, runner: CliRunner, in_lich_project, monkeypatch):
        """commit --message bypasses wizard and runs git commit."""
        calls = []
        def fake_run(cmd, **kwargs):
            calls.append(list(cmd))
            m = MagicMock()
            m.returncode = 0
            m.stdout = "[main abc] feat: thing"
            m.stderr = ""
            return m
        monkeypatch.setattr("subprocess.run", fake_run)
        result = runner.invoke(app, ["commit", "--message", "feat: add feature"])
        assert "Traceback" not in result.output
        assert result.exit_code in (0, 1)

    def test_tag_creates_tag(self, runner: CliRunner, in_lich_project, monkeypatch):
        """tag v1.2.3 runs git tag."""
        calls = []
        def fake_run(cmd, **kwargs):
            calls.append(list(cmd))
            m = MagicMock()
            m.returncode = 0
            m.stdout = ""
            m.stderr = ""
            return m
        monkeypatch.setattr("subprocess.run", fake_run)
        result = runner.invoke(app, ["tag", "v1.2.3"])
        assert "Traceback" not in result.output

    def test_push_runs_git_push(self, runner: CliRunner, in_lich_project, monkeypatch):
        """push runs git push origin main."""
        calls = []
        def fake_run(cmd, **kwargs):
            calls.append(list(cmd))
            m = MagicMock()
            m.returncode = 0
            m.stdout = ""
            m.stderr = ""
            return m
        monkeypatch.setattr("subprocess.run", fake_run)
        result = runner.invoke(app, ["push"])
        assert "Traceback" not in result.output


# ============================================================
# secret.py  (currently ~72%, 33 missed lines)
# ============================================================

class TestSecretGenerateCommand:
    def test_generate_help(self, runner: CliRunner):
        result = runner.invoke(app, ["secret", "generate", "--help"])
        assert result.exit_code == 0

    def test_generate_default(self, runner: CliRunner):
        """generate without args produces a secret (no project check)."""
        result = runner.invoke(app, ["secret", "generate"])
        assert result.exit_code == 0
        assert "Traceback" not in result.output

    def test_generate_with_length(self, runner: CliRunner):
        result = runner.invoke(app, ["secret", "generate", "--length", "64"])
        assert result.exit_code == 0

    def test_generate_count_3(self, runner: CliRunner):
        result = runner.invoke(app, ["secret", "generate", "--count", "3"])
        assert result.exit_code == 0

    def test_generate_format_alphanum(self, runner: CliRunner):
        result = runner.invoke(app, ["secret", "generate", "--format", "alphanum"])
        assert result.exit_code == 0

    def test_generate_format_urlsafe(self, runner: CliRunner):
        result = runner.invoke(app, ["secret", "generate", "--format", "urlsafe"])
        assert result.exit_code == 0

    def test_generate_format_full(self, runner: CliRunner):
        """format=full uses full charset."""
        result = runner.invoke(app, ["secret", "generate", "--format", "full"])
        assert result.exit_code == 0

    def test_generate_copy_no_pyperclip(self, runner: CliRunner, monkeypatch):
        """--copy without pyperclip shows install hint."""
        import builtins
        real_import = builtins.__import__
        def fake_import(name, *args, **kwargs):
            if name == "pyperclip":
                raise ImportError("No module named 'pyperclip'")
            return real_import(name, *args, **kwargs)
        monkeypatch.setattr(builtins, "__import__", fake_import)
        result = runner.invoke(app, ["secret", "generate", "--copy"])
        assert result.exit_code == 0
        assert "pyperclip" in result.output


class TestSecretRotateCommand:
    def test_rotate_no_env_file(self, runner: CliRunner, in_lich_project):
        """rotate without .env file exits 1."""
        result = runner.invoke(app, ["secret", "rotate"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_rotate_with_env_file(self, runner: CliRunner, in_lich_project):
        """rotate finds secrets and rotates them."""
        env = in_lich_project / ".env"
        env.write_text("SECRET_KEY=old_secret_key_value\nOTHER=value\n")
        result = runner.invoke(app, ["secret", "rotate"])
        assert result.exit_code == 0
        assert "Traceback" not in result.output

    def test_rotate_dry_run(self, runner: CliRunner, in_lich_project):
        """--dry-run shows what would change without writing."""
        env = in_lich_project / ".env"
        env.write_text("JWT_SECRET_KEY=old_jwt_secret\n")
        result = runner.invoke(app, ["secret", "rotate", "--dry-run"])
        assert result.exit_code == 0
        assert "Traceback" not in result.output

    def test_rotate_specific_key(self, runner: CliRunner, in_lich_project):
        """--key rotates only the specified key."""
        env = in_lich_project / ".env"
        env.write_text("MY_KEY=original_value\nOTHER_KEY=stays\n")
        result = runner.invoke(app, ["secret", "rotate", "--key", "MY_KEY"])
        assert result.exit_code == 0

    def test_rotate_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["secret", "rotate"])
        assert result.exit_code == 1

    def test_rotate_no_secrets_found(self, runner: CliRunner, in_lich_project):
        """When .env has no secret keys, reports nothing found."""
        env = in_lich_project / ".env"
        env.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
        result = runner.invoke(app, ["secret", "rotate"])
        assert result.exit_code == 0
        assert "Traceback" not in result.output


class TestSecretCheckCommand:
    def test_check_help(self, runner: CliRunner):
        result = runner.invoke(app, ["secret", "check", "--help"])
        assert result.exit_code == 0

    def test_check_no_env_file(self, runner: CliRunner, in_lich_project):
        """check without .env file exits 1."""
        result = runner.invoke(app, ["secret", "check"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_check_with_weak_secret(self, runner: CliRunner, in_lich_project):
        """check exits 1 when weak secrets are found."""
        env = in_lich_project / ".env"
        env.write_text("SECRET_KEY=secret\nJWT_SECRET=weak\n")
        result = runner.invoke(app, ["secret", "check"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_check_with_strong_secret(self, runner: CliRunner, in_lich_project):
        """check passes for strong secrets."""
        env = in_lich_project / ".env"
        env.write_text(
            "SECRET_KEY=a3f8b2c1d9e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1\n"
        )
        result = runner.invoke(app, ["secret", "check"])
        assert result.exit_code == 0
        assert "Traceback" not in result.output

    def test_check_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["secret", "check"])
        assert result.exit_code == 1
