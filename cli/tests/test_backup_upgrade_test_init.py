"""
Comprehensive tests covering backup.py, upgrade.py, test.py and init.py.
"""
import importlib.util
import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.backup import (
    _run_docker_command,
    backup_postgresql,
    backup_mysql,
    backup_mongodb,
    backup_redis,
    upload_to_s3,
)
from lich.commands.upgrade import (
    _parse_versions,
    _copy_and_render,
    _recursive_copy,
    _backup_lich_dir,
    _sync_files,
    _check_and_update_cli,
    CHANGELOG_PATH,
)
from lich import __version__


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_result(returncode: int, stdout: str = "", stderr: str = "") -> MagicMock:
    r = MagicMock()
    r.returncode = returncode
    r.stdout = stdout
    r.stderr = stderr
    return r


# ===========================================================================
# backup.py
# ===========================================================================


class TestRunDockerCommand:
    def test_success(self, monkeypatch):
        fake = _make_fake_result(0, "hello", "")
        monkeypatch.setattr("lich.commands.backup.subprocess.run", lambda *a, **k: fake)
        code, stdout, stderr = _run_docker_command(["docker", "ps"])
        assert code == 0
        assert stdout == "hello"
        assert stderr == ""

    def test_docker_not_found(self, monkeypatch):
        def _raise(*a, **k):
            raise FileNotFoundError("docker not found")
        monkeypatch.setattr("lich.commands.backup.subprocess.run", _raise)
        code, stdout, stderr = _run_docker_command(["docker", "ps"])
        assert code == -1
        assert stdout == ""
        assert "Docker not found" in stderr


class TestBackupFunctions:
    def test_backup_postgresql_success(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "lich.commands.backup._run_docker_command",
            lambda cmd: (0, "SQL DUMP OUTPUT", ""),
        )
        backup_file = tmp_path / "db.sql"
        result = backup_postgresql("my_container", "mydb", backup_file)
        assert result is True
        assert backup_file.read_text() == "SQL DUMP OUTPUT"

    def test_backup_postgresql_failure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "lich.commands.backup._run_docker_command",
            lambda cmd: (1, "", "pg_dump: error"),
        )
        backup_file = tmp_path / "db.sql"
        result = backup_postgresql("my_container", "mydb", backup_file)
        assert result is False
        assert not backup_file.exists()

    def test_backup_mysql_success(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "lich.commands.backup._run_docker_command",
            lambda cmd: (0, "SQL content", ""),
        )
        backup_file = tmp_path / "mysql.sql"
        result = backup_mysql("my_container", "mydb", backup_file, {"env": {"MYSQL_ROOT_PASSWORD": "secret"}})
        assert result is True
        assert backup_file.read_text() == "SQL content"

    def test_backup_mysql_failure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "lich.commands.backup._run_docker_command",
            lambda cmd: (1, "", "mysqldump: error"),
        )
        backup_file = tmp_path / "mysql.sql"
        result = backup_mysql("my_container", "mydb", backup_file, {})
        assert result is False

    def test_backup_mongodb_success(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "lich.commands.backup._run_docker_command",
            lambda cmd: (0, "binarydata", ""),
        )
        backup_file = tmp_path / "mongo.archive"
        result = backup_mongodb("my_container", backup_file)
        assert result is True
        assert backup_file.exists()

    def test_backup_mongodb_failure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "lich.commands.backup._run_docker_command",
            lambda cmd: (1, "", "mongodump: error"),
        )
        backup_file = tmp_path / "mongo.archive"
        result = backup_mongodb("my_container", backup_file)
        assert result is False

    def test_backup_redis_success(self, tmp_path, monkeypatch):
        # BGSAVE call returns 0, then cp call returns 0 and creates the file
        calls = []

        def fake_docker(cmd):
            calls.append(cmd)
            if "BGSAVE" in cmd:
                return (0, "Background saving started", "")
            else:
                # Simulate docker cp by creating the file
                backup_file = Path(cmd[-1])
                backup_file.write_bytes(b"RDB data")
                return (0, "", "")

        monkeypatch.setattr("lich.commands.backup._run_docker_command", fake_docker)
        backup_file = tmp_path / "dump.rdb"
        # Patch the cmd so docker cp writes to our tmp_path location
        # We need to intercept the cmd building - simplest: pass backup_path
        result = backup_redis("my_container", backup_file)
        assert result is True

    def test_backup_redis_failure(self, tmp_path, monkeypatch):
        calls = []

        def fake_docker(cmd):
            calls.append(cmd)
            if "BGSAVE" in cmd:
                return (0, "Background saving started", "")
            else:
                return (1, "", "docker cp failed")

        monkeypatch.setattr("lich.commands.backup._run_docker_command", fake_docker)
        backup_file = tmp_path / "dump.rdb"
        result = backup_redis("my_container", backup_file)
        assert result is False

    def test_upload_to_s3_success(self, tmp_path, monkeypatch):
        fake = _make_fake_result(0)
        monkeypatch.setattr("lich.commands.backup.subprocess.run", lambda *a, **k: fake)
        test_file = tmp_path / "backup.sql"
        test_file.write_text("data")
        result = upload_to_s3(test_file, "s3://bucket/path/backup.sql")
        assert result is True

    def test_upload_to_s3_failure(self, tmp_path, monkeypatch):
        fake = _make_fake_result(1)
        monkeypatch.setattr("lich.commands.backup.subprocess.run", lambda *a, **k: fake)
        test_file = tmp_path / "backup.sql"
        test_file.write_text("data")
        result = upload_to_s3(test_file, "s3://bucket/path/backup.sql")
        assert result is False

    def test_upload_to_s3_aws_not_found(self, tmp_path, monkeypatch):
        def _raise(*a, **k):
            raise FileNotFoundError("aws not found")
        monkeypatch.setattr("lich.commands.backup.subprocess.run", _raise)
        test_file = tmp_path / "backup.sql"
        test_file.write_text("data")
        result = upload_to_s3(test_file, "s3://bucket/path/backup.sql")
        assert result is False


COMPOSE_POSTGRES = """
services:
  db:
    image: postgres:16
    container_name: myapp_db
    environment:
      POSTGRES_DB: myapp
"""

COMPOSE_MYSQL = """
services:
  db:
    image: mysql:8
    container_name: myapp_mysql
    environment:
      MYSQL_DATABASE: myapp
      MYSQL_ROOT_PASSWORD: secret
"""


class TestBackupCommandWithDB:
    def test_backup_with_postgres_db(self, runner: CliRunner, in_lich_project, monkeypatch):
        (in_lich_project / "docker-compose.yml").write_text(COMPOSE_POSTGRES)
        monkeypatch.setattr(
            "lich.commands.backup._run_docker_command",
            lambda cmd: (0, "-- SQL DUMP --", ""),
        )
        result = runner.invoke(app, ["backup"])
        assert result.exit_code == 0
        assert "backup" in result.output.lower() or "Detected" in result.output
        assert "Traceback" not in result.output

    def test_backup_with_failed_db(self, runner: CliRunner, in_lich_project, monkeypatch):
        (in_lich_project / "docker-compose.yml").write_text(COMPOSE_POSTGRES)
        monkeypatch.setattr(
            "lich.commands.backup._run_docker_command",
            lambda cmd: (1, "", "connection refused"),
        )
        result = runner.invoke(app, ["backup"])
        assert result.exit_code == 0  # command itself doesn't fail, just logs
        assert "Traceback" not in result.output

    def test_backup_list_with_backups(self, runner: CliRunner, in_lich_project):
        backups_dir = in_lich_project / "backups"
        backups_dir.mkdir()
        backup_file = backups_dir / "db_20240101_120000.sql"
        backup_file.write_text("-- SQL --")
        result = runner.invoke(app, ["backup", "--list"])
        assert result.exit_code == 0
        assert "db_20240101_120000.sql" in result.output

    def test_backup_with_remote_upload(self, runner: CliRunner, in_lich_project, monkeypatch):
        (in_lich_project / "docker-compose.yml").write_text(COMPOSE_POSTGRES)

        upload_calls = []

        def fake_docker(cmd):
            return (0, "-- SQL DUMP --", "")

        def fake_upload(file_path, s3_uri):
            upload_calls.append((file_path, s3_uri))
            return True

        monkeypatch.setattr("lich.commands.backup._run_docker_command", fake_docker)
        monkeypatch.setattr("lich.commands.backup.upload_to_s3", fake_upload)

        result = runner.invoke(app, ["backup", "--remote", "s3://mybucket/backups"])
        assert result.exit_code == 0
        assert len(upload_calls) == 1
        assert "s3://mybucket/backups" in upload_calls[0][1]


class TestRestoreCommand:
    def test_restore_with_explicit_file_exists(self, runner: CliRunner, in_lich_project, monkeypatch):
        backup_file = in_lich_project / "mybackup.sql"
        backup_file.write_text("-- SQL --")
        monkeypatch.setattr("lich.commands.backup.Confirm.ask", lambda *a, **k: True)
        result = runner.invoke(app, ["backup", "restore", str(backup_file)])
        assert result.exit_code == 0
        assert "Restoring" in result.output or "restore" in result.output.lower()
        assert "Traceback" not in result.output

    def test_restore_with_explicit_file_not_exists(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["backup", "restore", "/nonexistent/backup.sql"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "Traceback" not in result.output

    def test_restore_interactive_no_backups(self, runner: CliRunner, in_lich_project):
        # No backups dir at all
        result = runner.invoke(app, ["backup", "restore"])
        assert result.exit_code == 1
        assert "No backups" in result.output

    def test_restore_interactive_with_backups(self, runner: CliRunner, in_lich_project, monkeypatch):
        backups_dir = in_lich_project / "backups"
        backups_dir.mkdir()
        (backups_dir / "db_20240101.sql").write_text("-- SQL --")

        monkeypatch.setattr("lich.commands.backup.Prompt.ask", lambda *a, **k: "1")
        monkeypatch.setattr("lich.commands.backup.Confirm.ask", lambda *a, **k: False)

        result = runner.invoke(app, ["backup", "restore"])
        assert result.exit_code == 0
        assert "Cancelled" in result.output


# ===========================================================================
# upgrade.py
# ===========================================================================


class TestParseVersions:
    def test_returns_fallback_when_no_changelog(self, tmp_path, monkeypatch):
        monkeypatch.setattr("lich.commands.upgrade.CHANGELOG_PATH", tmp_path / "MISSING.md")
        versions = _parse_versions()
        assert len(versions) >= 1
        assert versions[0]["version"] == __version__

    def test_parses_changelog(self, tmp_path, monkeypatch):
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [1.2.3] - 2024-01-01\n\n### Added\n- Cool feature\n"
        )
        monkeypatch.setattr("lich.commands.upgrade.CHANGELOG_PATH", changelog)
        versions = _parse_versions()
        found_versions = [v["version"] for v in versions]
        assert "1.2.3" in found_versions


class TestCopyAndRender:
    def test_substitutes_project_slug(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = tmp_path / "template.md"
        dst = tmp_path / "output.md"
        slug = tmp_path.name
        src.write_text("Project: {{ cookiecutter.project_slug }}", encoding="utf-8")
        _copy_and_render(src, dst)
        content = dst.read_text(encoding="utf-8")
        assert slug in content
        assert "cookiecutter" not in content

    def test_unescapes_github_actions_vars(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = tmp_path / "workflow.yml"
        dst = tmp_path / "output.yml"
        src.write_text('steps: {{ "{{" }} env.MY_VAR {{ "}}" }}', encoding="utf-8")
        _copy_and_render(src, dst)
        content = dst.read_text(encoding="utf-8")
        assert "{{" in content
        assert "}}" in content
        assert '"{{' not in content

    def test_handles_binary_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = tmp_path / "binary.bin"
        dst = tmp_path / "binary_out.bin"
        # Write actual binary data that can't decode as utf-8
        src.write_bytes(b"\xff\xfe\x00\x01\x80\x90")
        result = _copy_and_render(src, dst)
        assert result is False
        assert dst.exists()


class TestRecursiveCopy:
    def test_copies_directory_structure(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "sub").mkdir()
        (src / "file.md").write_text("# Hello")
        (src / "sub" / "nested.yml").write_text("key: value")

        dst = tmp_path / "dst"
        _recursive_copy(src, dst)

        assert (dst / "file.md").exists()
        assert (dst / "sub" / "nested.yml").exists()

    def test_overwrites_existing_dst(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "file.md").write_text("new content")

        dst = tmp_path / "dst"
        dst.mkdir()
        (dst / "old_file.txt").write_text("old")

        _recursive_copy(src, dst)

        assert (dst / "file.md").exists()
        # Old dst was rmtree'd
        assert not (dst / "old_file.txt").exists()


class TestBackupLichDir:
    def test_creates_backup(self, in_lich_project, monkeypatch):
        monkeypatch.chdir(in_lich_project)
        # .lich exists as a file in the fixture; replace with a dir
        lich = in_lich_project / ".lich"
        if lich.is_file():
            lich.unlink()
        lich.mkdir()
        (lich / "rules").write_text("rules content")

        _backup_lich_dir()

        backup = in_lich_project / ".lich.backup"
        assert backup.is_dir()
        assert (backup / "rules").read_text() == "rules content"

    def test_overwrites_existing_backup(self, in_lich_project, monkeypatch):
        monkeypatch.chdir(in_lich_project)
        lich = in_lich_project / ".lich"
        if lich.is_file():
            lich.unlink()
        lich.mkdir()
        (lich / "new.md").write_text("new")

        backup = in_lich_project / ".lich.backup"
        backup.mkdir()
        (backup / "old.md").write_text("old")

        _backup_lich_dir()

        assert backup.is_dir()
        assert (backup / "new.md").read_text() == "new"
        # Old file was removed because backup was rmtree'd and re-copied
        assert not (backup / "old.md").exists()


class TestSyncFiles:
    def test_writes_version_file(self, in_lich_project, monkeypatch):
        monkeypatch.chdir(in_lich_project)
        # Make .lich a dir
        lich = in_lich_project / ".lich"
        if lich.is_file():
            lich.unlink()
        lich.mkdir()

        # source_dir can be any dir; sync targets will just warn if missing
        source_dir = in_lich_project / "fake_source"
        source_dir.mkdir()

        _sync_files(source_dir)

        version_file = in_lich_project / ".lich" / "lich.version"
        assert version_file.exists()
        assert __version__ in version_file.read_text()

    def test_skips_missing_src(self, in_lich_project, monkeypatch, capsys):
        monkeypatch.chdir(in_lich_project)
        lich = in_lich_project / ".lich"
        if lich.is_file():
            lich.unlink()
        lich.mkdir()

        source_dir = in_lich_project / "empty_source"
        source_dir.mkdir()

        # Should not raise even when all SYNC_TARGETS are missing from source_dir
        _sync_files(source_dir)
        # version file still written
        assert (lich / "lich.version").exists()


class TestUpgradeProjectCommand:
    def test_upgrade_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["upgrade", "--local"])
        assert result.exit_code == 1
        assert "not a lich project" in result.output.lower()

    def test_upgrade_dry_run_local(self, runner: CliRunner, in_lich_project):
        from lich.commands.common import get_local_template_path
        assert get_local_template_path() is not None, "Local template must exist in dev checkout"
        lich = in_lich_project / ".lich"
        if lich.is_file():
            lich.unlink()
        lich.mkdir()
        result = runner.invoke(app, ["upgrade", "--dry-run", "--local"])
        assert result.exit_code == 0
        assert "dry run" in result.output.lower()

    def test_upgrade_force_local(self, runner: CliRunner, in_lich_project, monkeypatch):
        from lich.commands.common import get_local_template_path
        assert get_local_template_path() is not None
        lich = in_lich_project / ".lich"
        if lich.is_file():
            lich.unlink()
        lich.mkdir()
        result = runner.invoke(app, ["upgrade", "--force", "--local"])
        assert result.exit_code == 0
        assert "upgraded successfully" in result.output.lower()

    def test_upgrade_with_confirmation_yes(self, runner: CliRunner, in_lich_project, monkeypatch):
        from lich.commands.common import get_local_template_path
        assert get_local_template_path() is not None
        lich = in_lich_project / ".lich"
        if lich.is_file():
            lich.unlink()
        lich.mkdir()
        monkeypatch.setattr("lich.commands.upgrade.Confirm.ask", lambda *a, **k: True)
        result = runner.invoke(app, ["upgrade", "--local"])
        assert result.exit_code == 0
        assert "upgraded successfully" in result.output.lower()


class TestCheckAndUpdateCli:
    def test_no_update_needed(self, monkeypatch):
        import requests as _requests

        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.json.return_value = {"info": {"version": __version__}}
        monkeypatch.setattr("lich.commands.upgrade.requests.get", lambda *a, **k: fake_response)

        # Should return without raising
        _check_and_update_cli(dry_run=True)

    def test_update_available_dry_run(self, monkeypatch):
        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.json.return_value = {"info": {"version": "99.99.99"}}
        monkeypatch.setattr("lich.commands.upgrade.requests.get", lambda *a, **k: fake_response)

        sub_calls = []
        monkeypatch.setattr("lich.commands.upgrade.subprocess.check_call", lambda *a, **k: sub_calls.append(a))

        _check_and_update_cli(dry_run=True)

        # With dry_run=True no subprocess.check_call should happen
        assert len(sub_calls) == 0

    def test_network_error_returns_gracefully(self, monkeypatch):
        import requests as _requests

        def _raise(*a, **k):
            raise _requests.RequestException("network down")

        monkeypatch.setattr("lich.commands.upgrade.requests.get", _raise)
        # Should not raise, just print and return
        _check_and_update_cli(dry_run=False)


# ===========================================================================
# test.py
# ===========================================================================


class TestTestCommand:
    def test_runs_pytest_default(self, runner: CliRunner, in_lich_project, monkeypatch):
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            return _make_fake_result(0)

        monkeypatch.setattr("lich.commands.test.subprocess.run", fake_run)
        result = runner.invoke(app, ["test"])
        assert result.exit_code == 0
        assert "pytest" in captured["cmd"]

    def test_runs_pytest_with_path(self, runner: CliRunner, in_lich_project, monkeypatch):
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            return _make_fake_result(0)

        monkeypatch.setattr("lich.commands.test.subprocess.run", fake_run)
        result = runner.invoke(app, ["test", "mypath"])
        assert result.exit_code == 0
        assert "mypath" in captured["cmd"]

    def test_unit_flag(self, runner: CliRunner, in_lich_project, monkeypatch):
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            return _make_fake_result(0)

        monkeypatch.setattr("lich.commands.test.subprocess.run", fake_run)
        result = runner.invoke(app, ["test", "--unit"])
        assert result.exit_code == 0
        assert "backend/tests/unit" in captured["cmd"]

    def test_integration_flag(self, runner: CliRunner, in_lich_project, monkeypatch):
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            return _make_fake_result(0)

        monkeypatch.setattr("lich.commands.test.subprocess.run", fake_run)
        result = runner.invoke(app, ["test", "--integration"])
        assert result.exit_code == 0
        assert "backend/tests/integration" in captured["cmd"]

    def test_coverage_flag(self, runner: CliRunner, in_lich_project, monkeypatch):
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            return _make_fake_result(0)

        monkeypatch.setattr("lich.commands.test.subprocess.run", fake_run)
        result = runner.invoke(app, ["test", "--coverage"])
        assert result.exit_code == 0
        assert "--cov=backend" in captured["cmd"]

    def test_verbose_flag(self, runner: CliRunner, in_lich_project, monkeypatch):
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            return _make_fake_result(0)

        monkeypatch.setattr("lich.commands.test.subprocess.run", fake_run)
        result = runner.invoke(app, ["test", "--verbose"])
        assert result.exit_code == 0
        assert "-v" in captured["cmd"]

    def test_pytest_fails_exits_1(self, runner: CliRunner, in_lich_project, monkeypatch):
        monkeypatch.setattr(
            "lich.commands.test.subprocess.run",
            lambda *a, **k: _make_fake_result(1),
        )
        result = runner.invoke(app, ["test"])
        assert result.exit_code == 1
        assert "failed" in result.output.lower()

    def test_watch_without_pytest_watch_exits_1(self, runner: CliRunner, in_lich_project):
        # Patch importlib.util.find_spec at the stdlib level so the inline import in test.py sees None
        with patch("importlib.util.find_spec", return_value=None):
            result = runner.invoke(app, ["test", "--watch"])
        assert result.exit_code == 1
        assert "pytest-watch" in result.output.lower() or "watch" in result.output.lower()


# ===========================================================================
# init.py
# ===========================================================================


class TestInitProject:
    def test_init_calls_cookiecutter(self, tmp_path, monkeypatch):
        project_path = tmp_path / "myproject"
        project_path.mkdir()

        monkeypatch.setattr(
            "lich.commands.init.cookiecutter",
            lambda *a, **k: str(project_path),
        )
        runner = CliRunner()
        result = runner.invoke(app, ["init", "--no-input", "--local"])
        assert result.exit_code == 0
        assert "successfully" in result.output.lower()

    def test_init_cookiecutter_error_exits_1(self, tmp_path, monkeypatch):
        from cookiecutter.exceptions import CookiecutterException

        def _raise(*a, **k):
            raise CookiecutterException("fail")

        monkeypatch.setattr("lich.commands.init.cookiecutter", _raise)
        runner = CliRunner()
        result = runner.invoke(app, ["init", "--no-input", "--local"])
        assert result.exit_code == 1
        assert "error" in result.output.lower()

    def test_init_with_name_option(self, tmp_path, monkeypatch):
        project_path = tmp_path / "my-app"
        project_path.mkdir()

        captured = {}

        def fake_cookiecutter(*a, **k):
            captured["extra_context"] = k.get("extra_context", {})
            return str(project_path)

        monkeypatch.setattr("lich.commands.init.cookiecutter", fake_cookiecutter)
        runner = CliRunner()
        result = runner.invoke(app, ["init", "--no-input", "--local", "--name", "My App"])
        assert result.exit_code == 0
        assert captured["extra_context"].get("project_name") == "My App"

    def test_init_with_type_option(self, tmp_path, monkeypatch):
        project_path = tmp_path / "myproject"
        project_path.mkdir()

        captured = {}

        def fake_cookiecutter(*a, **k):
            captured["extra_context"] = k.get("extra_context", {})
            return str(project_path)

        monkeypatch.setattr("lich.commands.init.cookiecutter", fake_cookiecutter)
        runner = CliRunner()
        result = runner.invoke(app, ["init", "--no-input", "--local", "--type", "saas_platform"])
        assert result.exit_code == 0
        assert captured["extra_context"].get("project_type") == "saas_platform"
