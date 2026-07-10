"""
Tests for lich backup command.
"""
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.backup import _detect_databases


COMPOSE_POSTGRES_REDIS = """
services:
  db:
    image: postgres:16
    container_name: myapp_db
    environment:
      POSTGRES_DB: myapp
  cache:
    image: redis:7
    container_name: myapp_redis
"""

COMPOSE_MYSQL_MONGO = """
services:
  db:
    image: mysql:8
    container_name: myapp_mysql
    environment:
      MYSQL_DATABASE: myapp
      MYSQL_ROOT_PASSWORD: secret
  docs:
    image: mongo:7
    container_name: myapp_mongo
"""

COMPOSE_NO_DB = """
services:
  nginx:
    image: nginx:latest
"""


class TestDetectDatabases:
    def test_detects_postgres_type(self, in_lich_project):
        (in_lich_project / "docker-compose.yml").write_text(COMPOSE_POSTGRES_REDIS)
        dbs = _detect_databases()
        types = {v["type"] for v in dbs.values()}
        assert "postgresql" in types

    def test_detects_redis_type(self, in_lich_project):
        (in_lich_project / "docker-compose.yml").write_text(COMPOSE_POSTGRES_REDIS)
        dbs = _detect_databases()
        types = {v["type"] for v in dbs.values()}
        assert "redis" in types

    def test_detects_mysql(self, in_lich_project):
        (in_lich_project / "docker-compose.yml").write_text(COMPOSE_MYSQL_MONGO)
        dbs = _detect_databases()
        types = {v["type"] for v in dbs.values()}
        assert "mysql" in types

    def test_detects_mongodb(self, in_lich_project):
        (in_lich_project / "docker-compose.yml").write_text(COMPOSE_MYSQL_MONGO)
        dbs = _detect_databases()
        types = {v["type"] for v in dbs.values()}
        assert "mongodb" in types

    def test_no_compose_returns_empty(self, in_lich_project):
        # No docker-compose.yml in project dir
        result = _detect_databases()
        assert result == {}

    def test_no_db_services_returns_empty(self, in_lich_project):
        (in_lich_project / "docker-compose.yml").write_text(COMPOSE_NO_DB)
        result = _detect_databases()
        assert result == {}

    def test_container_name_is_captured(self, in_lich_project):
        (in_lich_project / "docker-compose.yml").write_text(COMPOSE_POSTGRES_REDIS)
        dbs = _detect_databases()
        # db service has container_name myapp_db
        assert dbs["db"]["container"] == "myapp_db"

    def test_yaml_error_returns_empty(self, in_lich_project):
        (in_lich_project / "docker-compose.yml").write_text(":::invalid yaml:::")
        result = _detect_databases()
        assert result == {}


class TestBackupCLI:
    def test_backup_help(self, runner: CliRunner):
        result = runner.invoke(app, ["backup", "--help"])
        assert result.exit_code == 0

    def test_restore_subcommand_help(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["backup", "restore", "--help"])
        assert result.exit_code == 0
        assert "restore" in result.output.lower()

    def test_backup_no_compose_no_db(self, runner: CliRunner, in_lich_project):
        """Without a docker-compose.yml, backup exits 0 with 'No databases' message."""
        result = runner.invoke(app, ["backup"])
        assert result.exit_code == 0
        assert "No databases" in result.output
        assert "Traceback" not in result.output

    def test_backup_list_no_backups(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["backup", "--list"])
        assert result.exit_code == 0
        assert "No backups found" in result.output

    def test_restore_no_backup_dir_exits_1(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["backup", "restore", "nonexistent.sql"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_backup_outside_project_exits_1(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["backup"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output
