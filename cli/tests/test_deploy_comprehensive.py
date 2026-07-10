"""Comprehensive tests for lich deploy command and helpers."""
import subprocess
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from lich.cli import app
import lich.commands.deploy as deploy


def _write_deploy_config(
    project_dir: Path,
    host: str = "192.0.2.10",
    user: str = "root",
    path: str = "/opt/app",
    connection: str = "manual",
    ssh_name: str = "myserver",
    private_repo: bool = False,
):
    """Write a valid deploy.yml into project_dir/.lich/."""
    lich_dir = project_dir / ".lich"
    lich_dir.mkdir(exist_ok=True)
    production = {
        "connection": connection,
        "path": path,
        "runtime": "docker-compose",
    }
    if connection == "ssh-config":
        production["ssh_name"] = ssh_name
    else:
        production["host"] = host
        production["user"] = user
    config = {
        "production": production,
        "git_repo": "git@github.com:acme/app.git",
        "private_repo": private_repo,
    }
    (lich_dir / "deploy.yml").write_text(yaml.dump(config))
    return lich_dir / "deploy.yml"


@pytest.fixture
def project(temp_dir: Path, monkeypatch):
    """A directory that passes _check_lich_project (has backend/)."""
    monkeypatch.chdir(temp_dir)
    (temp_dir / "backend").mkdir()
    return temp_dir


# ============================================
# HELPER FUNCTIONS
# ============================================

class TestHelpers:
    def test_load_secrets_parses_file(self, project):
        (project / ".secrets").write_text(
            '# comment\nKEY=value\nQUOTED="quoted-val"\nEMPTY_LINE_BELOW=\n\nNOEQ\n'
        )
        secrets = deploy._load_secrets()
        assert secrets["KEY"] == "value"
        assert secrets["QUOTED"] == "quoted-val"
        assert "NOEQ" not in secrets
        assert secrets["EMPTY_LINE_BELOW"] == ""

    def test_load_secrets_missing_file(self, project):
        assert deploy._load_secrets() == {}

    def test_validate_component_valid(self):
        # Should not raise for a valid component
        deploy._validate_component("backend")

    def test_validate_component_invalid_exits(self):
        with pytest.raises(deploy.typer.Exit) as exc:
            deploy._validate_component("nonsense")
        assert exc.value.exit_code == 1

    def test_safe_local_path_accepts_normal(self):
        assert deploy._safe_local_path("/home/user/key", "key") == "/home/user/key"

    def test_safe_local_path_rejects_dash(self):
        with pytest.raises(deploy.typer.Exit):
            deploy._safe_local_path("-oProxyCommand=evil", "key")

    def test_safe_local_path_rejects_empty(self):
        with pytest.raises(deploy.typer.Exit):
            deploy._safe_local_path("   ", "key")

    def test_prompt_validated_returns_valid(self, monkeypatch):
        monkeypatch.setattr(deploy.Prompt, "ask", lambda *a, **k: "/opt/app")
        result = deploy._prompt_validated("Path", deploy.validate_deploy_path, default="/opt/app")
        assert result == "/opt/app"

    def test_prompt_validated_retries_on_invalid(self, monkeypatch):
        answers = iter(["/opt/app\"; rm -rf /", "/opt/good"])
        monkeypatch.setattr(deploy.Prompt, "ask", lambda *a, **k: next(answers))
        result = deploy._prompt_validated("Path", deploy.validate_deploy_path)
        assert result == "/opt/good"

    def test_load_deploy_config_missing(self, project):
        assert deploy._load_deploy_config() == {}

    def test_save_and_load_deploy_config_roundtrip(self, project):
        cfg = {"production": {"host": "1.2.3.4"}, "git_repo": "git@github.com:a/b.git"}
        deploy._save_deploy_config(cfg)
        assert (project / ".lich" / "deploy.yml").exists()
        loaded = deploy._load_deploy_config()
        assert loaded["production"]["host"] == "1.2.3.4"

    def test_get_ssh_config_hosts(self, monkeypatch, temp_dir):
        fake_home = temp_dir / "home"
        (fake_home / ".ssh").mkdir(parents=True)
        (fake_home / ".ssh" / "config").write_text(
            "Host myserver\n  HostName 1.2.3.4\nHost *\n  User root\nHost other\n"
        )
        monkeypatch.setattr(deploy.Path, "home", classmethod(lambda cls: fake_home))
        hosts = deploy._get_ssh_config_hosts()
        assert "myserver" in hosts
        assert "other" in hosts
        # wildcard host is skipped
        assert "*" not in hosts

    def test_generate_secure_string_length_and_charset(self):
        s = deploy._generate_secure_string(24)
        assert len(s) == 24
        assert all(c.isalnum() for c in s)

    def test_extract_repo_info_ssh_format(self):
        provider, owner, repo = deploy._extract_repo_info("git@github.com:acme/app.git")
        assert provider == "github"
        assert owner == "acme"
        assert repo == "app"

    def test_extract_repo_info_https_gitlab(self):
        provider, owner, repo = deploy._extract_repo_info("https://gitlab.com/team/proj.git")
        assert provider == "gitlab"
        assert owner == "team"
        assert repo == "proj"

    def test_build_clone_cmd_quotes_unsafe_path(self):
        # A path with shell metacharacters must be single-quoted
        cmd = deploy._build_clone_cmd('/opt/a b', "git@github.com:acme/app.git")
        assert "git clone" in cmd
        assert "'/opt/a b'" in cmd

    def test_build_clone_cmd_includes_values(self):
        cmd = deploy._build_clone_cmd("/opt/app", "git@github.com:acme/app.git")
        assert "git clone" in cmd
        assert "/opt/app" in cmd
        assert "git@github.com:acme/app.git" in cmd


class TestCheckSSHConnection:
    def test_returns_true_on_success(self, monkeypatch):
        monkeypatch.setattr(deploy, "_run_ssh_command", lambda host, cmd, **kw: (0, "ok"))
        assert deploy._check_ssh_connection("host") is True

    def test_returns_false_on_failure(self, monkeypatch):
        monkeypatch.setattr(deploy, "_run_ssh_command", lambda host, cmd, **kw: (1, ""))
        assert deploy._check_ssh_connection("host") is False


# ============================================
# _resolve_ssh_target
# ============================================

class TestResolveSSHTarget:
    def test_manual_connection(self):
        config = {
            "production": {"connection": "manual", "user": "root", "host": "192.0.2.10", "path": "/opt/app"},
            "git_repo": "git@github.com:acme/app.git",
        }
        ssh_host, deploy_path, git_repo = deploy._resolve_ssh_target(config, "production")
        assert ssh_host == "root@192.0.2.10"
        assert deploy_path == "/opt/app"
        assert git_repo == "git@github.com:acme/app.git"

    def test_ssh_config_connection(self):
        config = {
            "production": {"connection": "ssh-config", "ssh_name": "myserver", "path": "/srv/app"},
            "git_repo": "git@github.com:acme/app.git",
        }
        ssh_host, deploy_path, _ = deploy._resolve_ssh_target(config, "production")
        assert ssh_host == "myserver"
        assert deploy_path == "/srv/app"

    def test_missing_environment_exits(self):
        with pytest.raises(deploy.typer.Exit) as exc:
            deploy._resolve_ssh_target({"git_repo": "x"}, "production")
        assert exc.value.exit_code == 1

    def test_invalid_path_exits(self):
        config = {
            "production": {"connection": "manual", "user": "root", "host": "1.2.3.4", "path": "$(evil)"},
            "git_repo": "git@github.com:acme/app.git",
        }
        with pytest.raises(deploy.typer.Exit):
            deploy._resolve_ssh_target(config, "production")


# ============================================
# deploy status
# ============================================

class TestDeployStatus:
    def test_no_config(self, runner: CliRunner, project):
        result = runner.invoke(app, ["deploy", "status"])
        assert result.exit_code == 0
        assert "No deployment configured" in result.output

    def test_invalid_ssh_destination_continues(self, runner: CliRunner, project, monkeypatch):
        # Write a config with an option-smuggling host that fails validation
        lich_dir = project / ".lich"
        lich_dir.mkdir(exist_ok=True)
        config = {
            "production": {"connection": "ssh-config", "ssh_name": "-oProxyCommand=x", "path": "/opt/app"},
            "git_repo": "git@github.com:acme/app.git",
        }
        (lich_dir / "deploy.yml").write_text(yaml.dump(config))
        result = runner.invoke(app, ["deploy", "status"])
        assert result.exit_code == 0
        assert "Invalid SSH destination" in result.output

    def test_offline_server(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)
        monkeypatch.setattr(deploy, "_check_ssh_connection", lambda host: False)
        result = runner.invoke(app, ["deploy", "status"])
        assert result.exit_code == 0
        assert "Offline" in result.output

    def test_online_server(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)
        monkeypatch.setattr(deploy, "_check_ssh_connection", lambda host: True)
        monkeypatch.setattr(
            deploy, "_run_ssh_command",
            lambda host, cmd, **kw: (0, "abc123 initial commit (2 hours ago)"),
        )
        result = runner.invoke(app, ["deploy", "status"])
        assert result.exit_code == 0
        assert "Online" in result.output

    def test_environment_filter_not_found(self, runner: CliRunner, project):
        _write_deploy_config(project)
        result = runner.invoke(app, ["deploy", "status", "staging"])
        assert result.exit_code == 0
        assert "not found" in result.output


# ============================================
# _run_deploy (via deploy prod/stage)
# ============================================

class TestRunDeploy:
    def test_invalid_component_exits(self, runner: CliRunner, project):
        _write_deploy_config(project)
        result = runner.invoke(app, ["deploy", "prod", "database", "--force"])
        assert result.exit_code == 1
        assert "Invalid component" in result.output

    def test_missing_environment_exits(self, runner: CliRunner, project):
        # Config exists but has no 'staging' environment
        _write_deploy_config(project)
        result = runner.invoke(app, ["deploy", "stage", "backend"])
        assert result.exit_code == 1
        assert "not configured" in result.output

    def test_dry_run_makes_no_ssh_calls(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)

        def _boom(*a, **k):
            raise AssertionError("SSH must not be called during dry-run")

        monkeypatch.setattr(deploy, "_check_ssh_connection", _boom)
        monkeypatch.setattr(deploy, "_run_ssh_command", _boom)
        result = runner.invoke(app, ["deploy", "prod", "backend", "--force", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_successful_deploy(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)
        monkeypatch.setattr(deploy, "_check_ssh_connection", lambda host: True)

        def fake_ssh(host, cmd, **kw):
            if "docker-compose.prod.yml" in cmd and "test -f" in cmd:
                return 0, "dev"
            if "docker compose ps" in cmd:
                return 0, "app-backend|Up 2 minutes"
            return 0, "output line"

        monkeypatch.setattr(deploy, "_run_ssh_command", fake_ssh)
        result = runner.invoke(app, ["deploy", "prod", "backend", "--force"])
        assert result.exit_code == 0
        assert "Deployed backend" in result.output

    def test_deploy_with_version(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)
        monkeypatch.setattr(deploy, "_check_ssh_connection", lambda host: True)
        captured = []

        def fake_ssh(host, cmd, **kw):
            captured.append(cmd)
            if "test -f" in cmd:
                return 0, "dev"
            if "docker compose ps" in cmd:
                return 0, "app-backend|Up"
            return 0, "ok"

        monkeypatch.setattr(deploy, "_run_ssh_command", fake_ssh)
        result = runner.invoke(app, ["deploy", "prod", "backend", "--force", "--version", "v1.2.3"])
        assert result.exit_code == 0
        assert any("checkout" in c and "v1.2.3" in c for c in captured)

    def test_connection_failure_exits(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)
        monkeypatch.setattr(deploy, "_check_ssh_connection", lambda host: False)
        result = runner.invoke(app, ["deploy", "prod", "backend", "--force"])
        assert result.exit_code == 1
        assert "Cannot connect" in result.output


# ============================================
# deploy prod / stage confirmation
# ============================================

class TestDeployProdConfirmation:
    def test_prod_cancelled_by_confirm(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)
        monkeypatch.setattr(deploy.Confirm, "ask", lambda *a, **k: False)
        result = runner.invoke(app, ["deploy", "prod", "backend"])
        assert result.exit_code == 0
        assert "Cancelled" in result.output

    def test_prod_confirmed_proceeds_to_dry_run(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)
        monkeypatch.setattr(deploy.Confirm, "ask", lambda *a, **k: True)
        result = runner.invoke(app, ["deploy", "prod", "backend", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_prod_force_skips_confirm(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)

        def _boom(*a, **k):
            raise AssertionError("Confirm.ask must not be called with --force")

        monkeypatch.setattr(deploy.Confirm, "ask", _boom)
        result = runner.invoke(app, ["deploy", "prod", "backend", "--force", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_stage_dry_run(self, runner: CliRunner, project, monkeypatch):
        lich_dir = project / ".lich"
        lich_dir.mkdir(exist_ok=True)
        config = {
            "staging": {"connection": "manual", "host": "192.0.2.20", "user": "root", "path": "/opt/app"},
            "git_repo": "git@github.com:acme/app.git",
        }
        (lich_dir / "deploy.yml").write_text(yaml.dump(config))
        result = runner.invoke(app, ["deploy", "stage", "backend", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output


# ============================================
# deploy logs
# ============================================

class TestDeployLogs:
    def test_missing_environment_exits(self, runner: CliRunner, project):
        _write_deploy_config(project)  # only 'production'
        result = runner.invoke(app, ["deploy", "logs", "staging"])
        assert result.exit_code == 1
        assert "not configured" in result.output

    def test_invalid_component_exits(self, runner: CliRunner, project):
        _write_deploy_config(project)
        result = runner.invoke(app, ["deploy", "logs", "production", "-c", "database"])
        assert result.exit_code == 1
        assert "Invalid component" in result.output

    def test_valid_runs_ssh(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd

            class R:
                returncode = 0

            return R()

        monkeypatch.setattr(deploy.subprocess, "run", fake_run)
        result = runner.invoke(app, ["deploy", "logs", "production", "-c", "backend"])
        assert result.exit_code == 0
        assert captured["cmd"][0] == "ssh"
        assert "root@192.0.2.10" in captured["cmd"]
        assert any("docker compose logs" in part for part in captured["cmd"])


# ============================================
# deploy init
# ============================================

class TestDeployInit:
    def test_missing_environment_exits(self, runner: CliRunner, project):
        _write_deploy_config(project)  # only production
        result = runner.invoke(app, ["deploy", "init", "staging"])
        assert result.exit_code == 1
        assert "not configured" in result.output

    def test_ssh_connection_failure_exits(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)
        monkeypatch.setattr(deploy, "_check_ssh_connection", lambda host: False)
        result = runner.invoke(app, ["deploy", "init", "production", "--skip-docker"])
        assert result.exit_code == 1
        assert "Cannot connect" in result.output

    def test_successful_flow(self, runner: CliRunner, project, monkeypatch):
        _write_deploy_config(project)
        monkeypatch.setattr(deploy, "_check_ssh_connection", lambda host: True)
        monkeypatch.setattr(deploy, "_run_ssh_command", lambda host, cmd, **kw: (0, ""))
        result = runner.invoke(app, ["deploy", "init", "production", "--skip-docker"])
        assert result.exit_code == 0
        assert "initialized successfully" in result.output


# ============================================
# deploy setup happy path
# ============================================

class TestDeploySetup:
    def test_setup_happy_path(self, runner: CliRunner, project, monkeypatch):
        prompt_answers = iter([
            "production",   # which environment
            "manual",       # how do you connect
            "203.0.113.5",  # host
            "root",         # user
            "/opt/app",     # deploy path
            "docker-compose",  # runtime
            "git@github.com:acme/app.git",  # git repo URL
            "example.com",  # main domain
            "api.example.com",  # api subdomain
            "admin.example.com",  # admin subdomain
        ])

        def fake_prompt(*args, **kwargs):
            return next(prompt_answers)

        confirm_answers = iter([
            False,  # is this a private repo?
            False,  # configure environment variables now?
        ])

        def fake_confirm(*args, **kwargs):
            return next(confirm_answers)

        monkeypatch.setattr(deploy.Prompt, "ask", fake_prompt)
        monkeypatch.setattr(deploy.Confirm, "ask", fake_confirm)
        monkeypatch.setattr(deploy, "_check_ssh_connection", lambda host: True)
        monkeypatch.setattr(
            deploy.subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="git@github.com:acme/app.git\n", stderr=""),
        )

        result = runner.invoke(app, ["deploy", "setup"])
        assert result.exit_code == 0, result.output
        cfg = yaml.safe_load((project / ".lich" / "deploy.yml").read_text())
        assert cfg["production"]["host"] == "203.0.113.5"
        assert cfg["domains"]["main"] == "example.com"


# ============================================
# remote helper steps
# ============================================

class _FakeProgress:
    def add_task(self, *a, **k):
        return 1

    def update(self, *a, **k):
        pass

    def remove_task(self, *a, **k):
        pass

    def stop(self):
        pass


class TestRemoteHelpers:
    def test_setup_traefik_remote_runs_ssh(self, monkeypatch):
        captured = {}

        def fake_ssh(host, cmd, **kw):
            captured["cmd"] = cmd
            return (0, "")

        monkeypatch.setattr(deploy, "_run_ssh_command", fake_ssh)
        config = {"domains": {"main": "example.com"}}
        deploy._setup_traefik_remote(_FakeProgress(), config, "root@1.2.3.4", "/opt/app")
        assert "traefik.yml" in captured["cmd"]
        assert "example.com" in captured["cmd"]

    def test_setup_traefik_remote_no_domains_noop(self, monkeypatch):
        def _boom(*a, **k):
            raise AssertionError("SSH should not run without domains")

        monkeypatch.setattr(deploy, "_run_ssh_command", _boom)
        deploy._setup_traefik_remote(_FakeProgress(), {}, "root@1.2.3.4", "/opt/app")

    def test_start_services_remote_success(self, monkeypatch):
        captured = {}

        def fake_ssh(host, cmd, **kw):
            captured["cmd"] = cmd
            return (0, "")

        monkeypatch.setattr(deploy, "_run_ssh_command", fake_ssh)
        deploy._start_services_remote(_FakeProgress(), "root@1.2.3.4", "/opt/app")
        assert "docker compose" in captured["cmd"]

    def test_clone_repo_remote_success(self, monkeypatch):
        captured = {}

        def fake_ssh(host, cmd, **kw):
            captured["cmd"] = cmd
            return (0, "")

        monkeypatch.setattr(deploy, "_run_ssh_command", fake_ssh)
        deploy._clone_repo_remote(_FakeProgress(), "root@1.2.3.4", "/opt/app", "git@github.com:acme/app.git")
        assert "git clone" in captured["cmd"]

    def test_clone_repo_remote_failure_exits(self, monkeypatch):
        monkeypatch.setattr(deploy, "_run_ssh_command", lambda host, cmd, **kw: (1, "boom"))
        with pytest.raises(deploy.typer.Exit):
            deploy._clone_repo_remote(_FakeProgress(), "root@1.2.3.4", "/opt/app", "git@github.com:acme/app.git")
