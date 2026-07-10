"""Comprehensive tests for lich ci, ci_utils, and security commands."""
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from lich.cli import app
import lich.commands.ci as ci
import lich.commands.ci_utils as ci_utils
import lich.commands.security as security


@pytest.fixture
def project(temp_dir: Path, monkeypatch):
    """A directory that passes _check_lich_project (has backend/)."""
    monkeypatch.chdir(temp_dir)
    (temp_dir / "backend").mkdir()
    return temp_dir


# ============================================
# ci.py
# ============================================

class TestRunBackendCI:
    def test_no_backend_dir(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        assert ci.run_backend_ci() is True

    def test_all_pass(self, project, monkeypatch):
        monkeypatch.setattr(ci, "_run_command", lambda *a, **k: True)
        assert ci.run_backend_ci() is True

    def test_lint_fail_returns_false(self, project, monkeypatch):
        def fake(cmd, **kwargs):
            # ruff check fails, everything else passes
            return "ruff" not in cmd

        monkeypatch.setattr(ci, "_run_command", fake)
        assert ci.run_backend_ci() is False


class TestRunFrontendCI:
    def test_no_app_dir(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        assert ci.run_frontend_ci("web") is True

    def test_build_fail_returns_false(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        app_dir = temp_dir / "apps" / "web"
        app_dir.mkdir(parents=True)
        (app_dir / "node_modules").mkdir()

        def fake(cmd, **kwargs):
            return "build" not in cmd

        monkeypatch.setattr(ci, "_run_command", fake)
        assert ci.run_frontend_ci("web") is False


class TestCIAll:
    def test_no_backend_no_apps_passes(self, temp_dir, monkeypatch, runner: CliRunner):
        monkeypatch.chdir(temp_dir)
        (temp_dir / ".lich").write_text("{}")  # marker file to pass project check
        monkeypatch.setattr(ci, "run_backend_ci", lambda: True)
        result = runner.invoke(app, ["ci"])
        assert result.exit_code == 0
        assert "All CI checks passed" in result.output

    def test_failure_exits_1(self, project, monkeypatch, runner: CliRunner):
        monkeypatch.setattr(ci, "run_backend_ci", lambda: False)
        result = runner.invoke(app, ["ci"])
        assert result.exit_code == 1
        assert "CI failed" in result.output


class TestCIBackendLocal:
    def test_local_success(self, project, monkeypatch, runner: CliRunner):
        monkeypatch.setattr(ci, "run_backend_ci", lambda: True)
        result = runner.invoke(app, ["ci", "backend", "--local"])
        assert result.exit_code == 0
        assert "Backend CI passed" in result.output

    def test_local_failure(self, project, monkeypatch, runner: CliRunner):
        monkeypatch.setattr(ci, "run_backend_ci", lambda: False)
        result = runner.invoke(app, ["ci", "backend", "--local"])
        assert result.exit_code == 1


class TestCIFrontendLocal:
    @pytest.mark.parametrize("cmd_name", ["web", "admin", "landing"])
    def test_local_success(self, project, monkeypatch, runner: CliRunner, cmd_name):
        monkeypatch.setattr(ci, "run_frontend_ci", lambda app_name: True)
        result = runner.invoke(app, ["ci", cmd_name, "--local"])
        assert result.exit_code == 0
        assert "CI passed" in result.output

    def test_local_failure_exits(self, project, monkeypatch, runner: CliRunner):
        monkeypatch.setattr(ci, "run_frontend_ci", lambda app_name: False)
        result = runner.invoke(app, ["ci", "web", "--local"])
        assert result.exit_code == 1


class TestCISetupHelpers:
    def test_detect_system_returns_four(self):
        result = ci._detect_system()
        assert isinstance(result, tuple)
        assert len(result) == 4
        os_name, is_arm, os_display, arch_display = result
        assert isinstance(is_arm, bool)
        assert isinstance(os_display, str)

    def test_create_actrc_arm_mac(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        path = ci._create_actrc("Darwin", is_arm=True)
        content = path.read_text()
        assert "--container-architecture=linux/amd64" in content
        assert "--secret-file=.secrets" in content

    def test_create_actrc_non_arm(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        path = ci._create_actrc("Linux", is_arm=False)
        content = path.read_text()
        assert "--container-architecture" not in content
        assert "--reuse" in content

    def test_create_secrets_file(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        ci._create_secrets_file()
        secrets = (temp_dir / ".secrets").read_text()
        assert "GITHUB_TOKEN" in secrets
        gitignore = (temp_dir / ".gitignore").read_text()
        assert ".secrets" in gitignore

    def test_print_ci_setup_summary_arm(self):
        # Should not raise for ARM mac inputs
        ci._print_ci_setup_summary("macOS", "ARM (Apple Silicon)", "Darwin", True, True, True)

    def test_print_ci_setup_summary_non_arm(self):
        ci._print_ci_setup_summary("Linux", "Intel/AMD (x86_64)", "Linux", False, False, False)


# ============================================
# ci_utils.py
# ============================================

class TestCheckDockerRunning:
    def test_running(self, monkeypatch):
        monkeypatch.setattr(
            ci_utils.subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 0),
        )
        assert ci_utils.check_docker_running() is True

    def test_not_running(self, monkeypatch):
        monkeypatch.setattr(
            ci_utils.subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 1),
        )
        assert ci_utils.check_docker_running() is False

    def test_docker_not_found(self, monkeypatch):
        def raise_fnf(*a, **k):
            raise FileNotFoundError()

        monkeypatch.setattr(ci_utils.subprocess, "run", raise_fnf)
        assert ci_utils.check_docker_running() is False


class TestCheckActInstalled:
    def test_installed(self, monkeypatch):
        monkeypatch.setattr(ci_utils.shutil, "which", lambda x: "/usr/bin/act")
        assert ci_utils.check_act_installed() is True

    def test_not_installed(self, monkeypatch):
        monkeypatch.setattr(ci_utils.shutil, "which", lambda x: None)
        assert ci_utils.check_act_installed() is False


class TestErrorDisplays:
    def test_docker_error_no_crash(self):
        ci_utils.show_docker_not_running_error()

    def test_act_error_no_crash(self):
        ci_utils.show_act_not_installed_error()


class TestInstallAct:
    def test_macos_brew_success(self, monkeypatch):
        monkeypatch.setattr(ci_utils.platform, "system", lambda: "Darwin")
        monkeypatch.setattr(ci_utils.shutil, "which", lambda x: "/usr/bin/brew")
        monkeypatch.setattr(
            ci_utils.subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="", stderr=""),
        )
        assert ci_utils.install_act() is True

    def test_macos_no_brew(self, monkeypatch):
        monkeypatch.setattr(ci_utils.platform, "system", lambda: "Darwin")
        monkeypatch.setattr(ci_utils.shutil, "which", lambda x: None)
        assert ci_utils.install_act() is False

    def test_linux_success(self, monkeypatch):
        monkeypatch.setattr(ci_utils.platform, "system", lambda: "Linux")
        monkeypatch.setattr(
            ci_utils.subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="", stderr=""),
        )
        assert ci_utils.install_act() is True

    def test_install_failure(self, monkeypatch):
        monkeypatch.setattr(ci_utils.platform, "system", lambda: "Linux")
        monkeypatch.setattr(
            ci_utils.subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 1, stdout="", stderr="boom"),
        )
        assert ci_utils.install_act() is False


class TestGetGithubToken:
    def test_from_env(self, monkeypatch, temp_dir):
        monkeypatch.chdir(temp_dir)
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_from_env")
        assert ci_utils.get_github_token() == "ghp_from_env"

    def test_from_env_file(self, monkeypatch, temp_dir):
        monkeypatch.chdir(temp_dir)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        (temp_dir / ".env").write_text('GITHUB_TOKEN="ghp_from_file"\n')
        assert ci_utils.get_github_token() == "ghp_from_file"

    def test_from_actrc(self, monkeypatch, temp_dir):
        monkeypatch.chdir(temp_dir)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        fake_home = temp_dir / "home"
        fake_home.mkdir()
        (fake_home / ".actrc").write_text("-s GITHUB_TOKEN=ghp_from_actrc\n")
        monkeypatch.setattr(ci_utils.Path, "home", classmethod(lambda cls: fake_home))
        assert ci_utils.get_github_token() == "ghp_from_actrc"

    def test_returns_none(self, monkeypatch, temp_dir):
        monkeypatch.chdir(temp_dir)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        fake_home = temp_dir / "home"
        fake_home.mkdir()
        monkeypatch.setattr(ci_utils.Path, "home", classmethod(lambda cls: fake_home))
        assert ci_utils.get_github_token() is None


class TestIsArmMac:
    def test_true_on_arm_mac(self, monkeypatch):
        monkeypatch.setattr(ci_utils.platform, "system", lambda: "Darwin")
        monkeypatch.setattr(ci_utils.platform, "machine", lambda: "arm64")
        assert ci_utils.is_arm_mac() is True

    def test_false_on_intel_mac(self, monkeypatch):
        monkeypatch.setattr(ci_utils.platform, "system", lambda: "Darwin")
        monkeypatch.setattr(ci_utils.platform, "machine", lambda: "x86_64")
        assert ci_utils.is_arm_mac() is False

    def test_false_on_linux(self, monkeypatch):
        monkeypatch.setattr(ci_utils.platform, "system", lambda: "Linux")
        monkeypatch.setattr(ci_utils.platform, "machine", lambda: "aarch64")
        assert ci_utils.is_arm_mac() is False


class TestRunActWorkflow:
    def test_workflow_not_found(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        assert ci_utils.run_act_workflow("nonexistent.yml") is False

    def _make_workflow(self, temp_dir, name="ci.yml"):
        wf_dir = temp_dir / ".github" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        (wf_dir / name).write_text("name: ci\n")

    def test_success(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        self._make_workflow(temp_dir)
        monkeypatch.setattr(ci_utils, "is_arm_mac", lambda: False)
        monkeypatch.setattr(
            ci_utils.subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a[0], 0),
        )
        assert ci_utils.run_act_workflow("ci.yml") is True

    def test_failure(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        self._make_workflow(temp_dir)
        monkeypatch.setattr(ci_utils, "is_arm_mac", lambda: False)
        monkeypatch.setattr(
            ci_utils.subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a[0], 1),
        )
        assert ci_utils.run_act_workflow("ci.yml") is False

    def test_builds_full_command(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        self._make_workflow(temp_dir)
        monkeypatch.setattr(ci_utils, "is_arm_mac", lambda: True)
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            return subprocess.CompletedProcess(cmd, 0)

        monkeypatch.setattr(ci_utils.subprocess, "run", fake_run)
        result = ci_utils.run_act_workflow(
            "ci.yml", job="build", verbose=True, quiet=True,
            secrets=["S=1"], vars=["V=2"],
        )
        assert result is True
        cmd = captured["cmd"]
        assert "-j" in cmd and "build" in cmd
        assert "--verbose" in cmd
        assert "--quiet" in cmd
        assert "--container-architecture" in cmd  # ARM mac
        assert "-s" in cmd and "S=1" in cmd
        assert "--var" in cmd and "V=2" in cmd

    def test_act_not_found_returns_false(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        self._make_workflow(temp_dir)
        monkeypatch.setattr(ci_utils, "is_arm_mac", lambda: False)

        def raise_fnf(*a, **k):
            raise FileNotFoundError()

        monkeypatch.setattr(ci_utils.subprocess, "run", raise_fnf)
        assert ci_utils.run_act_workflow("ci.yml") is False


class TestEnsureActReady:
    def test_ready(self, monkeypatch):
        monkeypatch.setattr(ci_utils, "check_docker_running", lambda: True)
        monkeypatch.setattr(ci_utils, "check_act_installed", lambda: True)
        assert ci_utils.ensure_act_ready() is True

    def test_docker_down(self, monkeypatch):
        monkeypatch.setattr(ci_utils, "check_docker_running", lambda: False)
        assert ci_utils.ensure_act_ready() is False

    def test_act_missing(self, monkeypatch):
        monkeypatch.setattr(ci_utils, "check_docker_running", lambda: True)
        monkeypatch.setattr(ci_utils, "check_act_installed", lambda: False)
        assert ci_utils.ensure_act_ready() is False


# ============================================
# security.py
# ============================================

class TestScanPythonSecurity:
    def test_no_backend(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = security.scan_python_security()
        assert result["passed"] is True
        assert any("No backend" in i["message"] for i in result["issues"])

    def test_bandit_finds_issues(self, project, monkeypatch):
        monkeypatch.setattr(security, "_check_tool_installed", lambda tool: tool == "bandit")
        bandit_json = (
            '{"results": [{"issue_severity": "HIGH", "test_id": "B101", '
            '"issue_text": "assert used", "filename": "app.py", "line_number": 5}]}'
        )
        monkeypatch.setattr(security, "_run_command", lambda cmd, **k: (1, bandit_json, ""))
        result = security.scan_python_security()
        assert result["passed"] is False
        assert any("assert used" in i["message"] for i in result["issues"])

    def test_bandit_no_issues(self, project, monkeypatch):
        monkeypatch.setattr(security, "_check_tool_installed", lambda tool: tool == "bandit")
        monkeypatch.setattr(security, "_run_command", lambda cmd, **k: (0, "", ""))
        result = security.scan_python_security()
        assert result["passed"] is True
        assert result["issues"] == []


class TestScanFrontendSecurity:
    def test_no_apps_dir(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = security.scan_frontend_security()
        assert result["passed"] is True
        assert any("No apps" in i["message"] for i in result["issues"])

    def test_npm_audit_finds_vulns(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        app_dir = temp_dir / "apps" / "web"
        app_dir.mkdir(parents=True)
        (app_dir / "package.json").write_text("{}")
        audit_json = (
            '{"vulnerabilities": {"lodash": {"severity": "high", '
            '"via": [{"title": "Prototype pollution"}]}}}'
        )
        monkeypatch.setattr(security, "_run_command", lambda cmd, **k: (1, audit_json, ""))
        result = security.scan_frontend_security()
        assert result["passed"] is False
        assert any("lodash" in i["message"] for i in result["issues"])


class TestScanSecrets:
    def test_gitleaks_finds(self, project, monkeypatch):
        monkeypatch.setattr(security, "_check_tool_installed", lambda tool: tool == "gitleaks")
        leaks_json = '[{"RuleID": "aws-key", "Description": "AWS key", "File": "config.py", "StartLine": 3}]'
        monkeypatch.setattr(security, "_run_command", lambda cmd, **k: (1, leaks_json, ""))
        result = security.scan_secrets()
        assert result["passed"] is False
        assert any("AWS key" in i["message"] for i in result["issues"])

    def test_gitleaks_clean(self, project, monkeypatch):
        monkeypatch.setattr(security, "_check_tool_installed", lambda tool: tool == "gitleaks")
        monkeypatch.setattr(security, "_run_command", lambda cmd, **k: (0, "", ""))
        result = security.scan_secrets()
        assert result["passed"] is True

    def test_git_secrets_fallback(self, project, monkeypatch):
        monkeypatch.setattr(security, "_check_tool_installed", lambda tool: tool == "git-secrets")
        monkeypatch.setattr(security, "_run_command", lambda cmd, **k: (1, "", "secret found"))
        result = security.scan_secrets()
        assert result["passed"] is False
        assert any("secret found" in i["message"] for i in result["issues"])

    def test_neither_installed(self, project, monkeypatch):
        monkeypatch.setattr(security, "_check_tool_installed", lambda tool: False)
        result = security.scan_secrets()
        assert result["passed"] is True
        assert result["issues"] == []


class TestScanDocker:
    def test_trivy_not_installed(self, project, monkeypatch):
        monkeypatch.setattr(security, "_check_tool_installed", lambda tool: False)
        result = security.scan_docker()
        assert result["passed"] is True

    def test_trivy_finds_misconfig(self, project, monkeypatch):
        (project / "Dockerfile").write_text("FROM python:3.11\n")
        monkeypatch.setattr(security, "_check_tool_installed", lambda tool: True)
        trivy_json = (
            '{"Results": [{"Misconfigurations": [{"Severity": "HIGH", '
            '"Title": "Run as root"}]}]}'
        )
        monkeypatch.setattr(security, "_run_command", lambda cmd, **k: (0, trivy_json, ""))
        result = security.scan_docker()
        assert result["passed"] is False
        assert any("Run as root" in i["message"] for i in result["issues"])


class TestDisplayResults:
    def test_json_output(self, capsys):
        import io
        from rich.console import Console
        buf = io.StringIO()
        results = [{"tool": "python", "passed": True, "issues": []}]
        # Redirect the module console to capture output
        security.console.file = buf
        try:
            security.display_results(results, as_json=True)
        finally:
            security.console.file = None
        output = buf.getvalue()
        assert '"tool": "python"' in output

    def test_table_with_issues(self):
        results = [{
            "tool": "python",
            "passed": False,
            "issues": [{"severity": "high", "message": "bad", "file": "a.py", "line": 3}],
        }]
        # Should not raise while rendering the table
        security.display_results(results, as_json=False)

    def test_table_without_issues(self):
        results = [{"tool": "python", "passed": True, "issues": []}]
        security.display_results(results, as_json=False)


class TestSecurityScanCommand:
    def test_backend_only(self, project, monkeypatch, runner: CliRunner):
        called = {}

        def fake_backend(fix=False):
            called["backend"] = True
            return {"tool": "python", "passed": True, "issues": []}

        def fake_frontend(fix=False):
            called["frontend"] = True
            return {"tool": "frontend", "passed": True, "issues": []}

        monkeypatch.setattr(security, "scan_python_security", fake_backend)
        monkeypatch.setattr(security, "scan_frontend_security", fake_frontend)
        result = runner.invoke(app, ["security", "--backend"])
        assert result.exit_code == 0
        assert called.get("backend") is True
        assert "frontend" not in called

    def test_secrets_only(self, project, monkeypatch, runner: CliRunner):
        called = {}

        def fake_secrets(fix=False):
            called["secrets"] = True
            return {"tool": "secrets", "passed": True, "issues": []}

        def fake_backend(fix=False):
            raise AssertionError("backend should not run")

        monkeypatch.setattr(security, "scan_secrets", fake_secrets)
        monkeypatch.setattr(security, "scan_python_security", fake_backend)
        result = runner.invoke(app, ["security", "--secrets"])
        assert result.exit_code == 0
        assert called.get("secrets") is True

    def test_json_flag(self, project, monkeypatch, runner: CliRunner):
        monkeypatch.setattr(
            security, "scan_python_security",
            lambda fix=False: {"tool": "python", "passed": True, "issues": []},
        )
        result = runner.invoke(app, ["security", "--backend", "--json"])
        assert result.exit_code == 0
        assert '"tool"' in result.output

    def test_exit_1_on_issues(self, project, monkeypatch, runner: CliRunner):
        monkeypatch.setattr(
            security, "scan_python_security",
            lambda fix=False: {
                "tool": "python", "passed": False,
                "issues": [{"severity": "high", "message": "vuln"}],
            },
        )
        result = runner.invoke(app, ["security", "--backend"])
        assert result.exit_code == 1
