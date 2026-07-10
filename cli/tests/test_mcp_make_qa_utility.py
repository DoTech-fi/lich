"""
Tests for mcp/tools/make.py, mcp/tools/qa.py, mcp/tools/utility.py, mcp/tools/git.py
to increase coverage on these low-coverage MCP tool modules.
"""
import pytest
import json
from unittest.mock import patch, MagicMock

from lich.mcp.tools import make as mcp_make
from lich.mcp.tools import qa as mcp_qa
from lich.mcp.tools import utility as mcp_utility
from lich.mcp.tools import git as mcp_git


# ============================================================
# mcp/tools/make.py  (currently 30%)
# ============================================================

class TestMcpMakeTools:
    """Tests for mcp/tools/make.py tool functions."""

    def test_make_service_invalid_name(self, in_lich_project):
        result = mcp_make.lich_make_service("123-invalid")
        assert "ERROR" in result

    def test_make_service_valid_name(self, in_lich_project):
        result = mcp_make.lich_make_service("PaymentService")
        assert "PaymentService" in result
        assert "ERROR" not in result

    def test_make_entity_invalid_name(self, in_lich_project):
        result = mcp_make.lich_make_entity("-badname")
        assert "ERROR" in result

    def test_make_entity_valid_name(self, in_lich_project):
        result = mcp_make.lich_make_entity("User")
        assert "User" in result
        assert "ERROR" not in result

    def test_make_api_invalid(self, in_lich_project):
        result = mcp_make.lich_make_api("")
        assert "ERROR" in result

    def test_make_api_valid(self, in_lich_project):
        result = mcp_make.lich_make_api("UserResource")
        assert "UserResource" in result

    def test_make_dto_invalid(self, in_lich_project):
        result = mcp_make.lich_make_dto("--bad")
        assert "ERROR" in result

    def test_make_dto_valid(self, in_lich_project):
        result = mcp_make.lich_make_dto("CreateUserDTO")
        assert "CreateUserDTO" in result

    def test_make_factory_valid(self, in_lich_project):
        result = mcp_make.lich_make_factory("UserFactory")
        assert "UserFactory" in result

    def test_make_factory_invalid(self, in_lich_project):
        result = mcp_make.lich_make_factory("123bad")
        assert "ERROR" in result

    def test_make_middleware_valid(self, in_lich_project):
        result = mcp_make.lich_make_middleware("AuthMiddleware")
        assert "AuthMiddleware" in result

    def test_make_middleware_invalid(self, in_lich_project):
        result = mcp_make.lich_make_middleware("")
        assert "ERROR" in result

    def test_make_event_valid(self, in_lich_project):
        result = mcp_make.lich_make_event("UserCreated")
        assert "UserCreated" in result

    def test_make_event_invalid(self, in_lich_project):
        result = mcp_make.lich_make_event("-bad")
        assert "ERROR" in result

    def test_make_listener_valid(self, in_lich_project):
        result = mcp_make.lich_make_listener("SendWelcomeEmail", event="UserCreated")
        assert "SendWelcomeEmail" in result
        assert "UserCreated" in result

    def test_make_listener_invalid_name(self, in_lich_project):
        result = mcp_make.lich_make_listener("--bad", event="UserCreated")
        assert "ERROR" in result

    def test_make_listener_invalid_event(self, in_lich_project):
        result = mcp_make.lich_make_listener("MyListener", event="--bad")
        assert "ERROR" in result

    def test_make_job_valid(self, in_lich_project):
        result = mcp_make.lich_make_job("SendEmail")
        assert "SendEmail" in result

    def test_make_job_invalid(self, in_lich_project):
        result = mcp_make.lich_make_job("123bad")
        assert "ERROR" in result

    def test_make_policy_valid(self, in_lich_project):
        result = mcp_make.lich_make_policy("AdminPolicy")
        assert "AdminPolicy" in result

    def test_make_policy_invalid(self, in_lich_project):
        result = mcp_make.lich_make_policy("")
        assert "ERROR" in result

    def test_register_make_tools_registers_10(self):
        """register_make_tools registers all 10 tools."""
        registered = []
        mock_mcp = MagicMock()
        # mcp.tool() returns a decorator that we capture
        mock_mcp.tool.return_value = lambda fn: registered.append(fn) or fn
        mcp_make.register_make_tools(mock_mcp)
        assert len(registered) == 10


# ============================================================
# mcp/tools/qa.py  (currently 35%)
# ============================================================

class TestMcpQaTools:
    """Tests for mcp/tools/qa.py."""

    def test_lich_lint_backend_calls_lint_python(self, in_lich_project, monkeypatch):
        """lich_lint_backend calls lint_python and returns JSON."""
        fake_result = {"tool": "python", "passed": True, "issues": []}
        monkeypatch.setattr("lich.mcp.tools.qa.lint_python", lambda fix=False: fake_result)
        out = mcp_qa.lich_lint_backend()
        data = json.loads(out)
        assert data["passed"] is True

    def test_lich_lint_backend_with_fix(self, in_lich_project, monkeypatch):
        """lich_lint_backend passes fix=True to lint_python."""
        captured = {}
        def fake_lint(fix=False):
            captured["fix"] = fix
            return {"tool": "python", "passed": True, "issues": []}
        monkeypatch.setattr("lich.mcp.tools.qa.lint_python", fake_lint)
        mcp_qa.lich_lint_backend(fix=True)
        assert captured["fix"] is True

    def test_lich_lint_frontend_calls_lint_frontend(self, in_lich_project, monkeypatch):
        """lich_lint_frontend calls lint_frontend and returns JSON."""
        fake_result = {"tool": "frontend", "passed": True, "issues": []}
        monkeypatch.setattr("lich.mcp.tools.qa.lint_frontend", lambda fix=False: fake_result)
        out = mcp_qa.lich_lint_frontend()
        data = json.loads(out)
        assert data["tool"] == "frontend"

    def test_lich_security_scan_backend(self, in_lich_project, monkeypatch):
        """lich_security_scan with target=backend calls scan_python_security."""
        called = []
        monkeypatch.setattr("lich.mcp.tools.qa.scan_python_security", lambda: called.append("python") or {"tool": "python", "passed": True, "issues": []})
        monkeypatch.setattr("lich.mcp.tools.qa.scan_frontend_security", lambda: {"tool": "frontend", "passed": True, "issues": []})
        monkeypatch.setattr("lich.mcp.tools.qa.scan_secrets", lambda: {"tool": "secrets", "passed": True, "issues": []})
        monkeypatch.setattr("lich.mcp.tools.qa.scan_docker", lambda: {"tool": "docker", "passed": True, "issues": []})
        out = mcp_qa.lich_security_scan(target="backend")
        assert "python" in called
        data = json.loads(out)
        assert len(data) == 1

    def test_lich_security_scan_all(self, in_lich_project, monkeypatch):
        """lich_security_scan with target=all calls all scanners."""
        fake = {"passed": True, "issues": []}
        monkeypatch.setattr("lich.mcp.tools.qa.scan_python_security", lambda: {**fake, "tool": "python"})
        monkeypatch.setattr("lich.mcp.tools.qa.scan_frontend_security", lambda: {**fake, "tool": "frontend"})
        monkeypatch.setattr("lich.mcp.tools.qa.scan_secrets", lambda: {**fake, "tool": "secrets"})
        monkeypatch.setattr("lich.mcp.tools.qa.scan_docker", lambda: {**fake, "tool": "docker"})
        out = mcp_qa.lich_security_scan(target="all")
        data = json.loads(out)
        assert len(data) == 4

    def test_lich_security_scan_secrets(self, in_lich_project, monkeypatch):
        """lich_security_scan with target=secrets calls only scan_secrets."""
        called = []
        monkeypatch.setattr("lich.mcp.tools.qa.scan_python_security", lambda: called.append("python") or {})
        monkeypatch.setattr("lich.mcp.tools.qa.scan_secrets", lambda: {"tool": "secrets", "passed": True, "issues": []})
        monkeypatch.setattr("lich.mcp.tools.qa.scan_frontend_security", lambda: called.append("frontend") or {})
        monkeypatch.setattr("lich.mcp.tools.qa.scan_docker", lambda: called.append("docker") or {})
        out = mcp_qa.lich_security_scan(target="secrets")
        assert "python" not in called
        assert "frontend" not in called

    def test_lich_test_basic(self, monkeypatch):
        """lich_test calls run_lich_command with ['lich', 'test']."""
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.qa.run_lich_command", fake_run)
        out = mcp_qa.lich_test()
        assert captured["cmd"] == ["lich", "test"]

    def test_lich_test_unit_flag(self, monkeypatch):
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.qa.run_lich_command", fake_run)
        mcp_qa.lich_test(unit=True)
        assert "--unit" in captured["cmd"]

    def test_lich_test_integration_flag(self, monkeypatch):
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.qa.run_lich_command", fake_run)
        mcp_qa.lich_test(integration=True)
        assert "--integration" in captured["cmd"]

    def test_lich_test_coverage_flag(self, monkeypatch):
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.qa.run_lich_command", fake_run)
        mcp_qa.lich_test(coverage=True)
        assert "--coverage" in captured["cmd"]

    def test_register_qa_tools_registers_4(self):
        """register_qa_tools registers 4 tools."""
        registered = []
        mock_mcp = MagicMock()
        mock_mcp.tool.return_value = lambda fn: registered.append(fn) or fn
        mcp_qa.register_qa_tools(mock_mcp)
        assert len(registered) == 4


# ============================================================
# mcp/tools/utility.py  (currently 38%)
# ============================================================

class TestMcpUtilityTools:
    """Tests for mcp/tools/utility.py."""

    def test_lich_adopt_calls_run_lich_command(self, monkeypatch):
        """lich_adopt builds correct command."""
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.utility.run_lich_command", fake_run)
        out = mcp_utility.lich_adopt("/some/path")
        assert captured["cmd"] == ["lich", "adopt", "/some/path", "-o", ".", "--dry-run"]
        assert out == "ok"

    def test_lich_adopt_not_dry_run(self, monkeypatch):
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.utility.run_lich_command", fake_run)
        mcp_utility.lich_adopt("/some/path", dry_run=False)
        assert "--dry-run" not in captured["cmd"]

    def test_lich_adopt_rejects_empty_path(self):
        """lich_adopt rejects empty path."""
        out = mcp_utility.lich_adopt("")
        assert "ERROR" in out

    def test_lich_adopt_rejects_dash_path(self):
        """lich_adopt rejects dash-prefixed path."""
        out = mcp_utility.lich_adopt("-bad")
        assert "ERROR" in out

    def test_lich_adopt_rejects_dash_output(self):
        """lich_adopt rejects dash-prefixed output."""
        out = mcp_utility.lich_adopt("/good/path", output="-bad")
        assert "ERROR" in out

    def test_lich_adopt_custom_output(self, monkeypatch):
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.utility.run_lich_command", fake_run)
        mcp_utility.lich_adopt("/src", output="/dst")
        assert "/dst" in captured["cmd"]

    def test_lich_upgrade_basic(self, monkeypatch):
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.utility.run_lich_command", fake_run)
        mcp_utility.lich_upgrade()
        assert captured["cmd"] == ["lich", "upgrade"]

    def test_lich_upgrade_force(self, monkeypatch):
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.utility.run_lich_command", fake_run)
        mcp_utility.lich_upgrade(force=True)
        assert "--force" in captured["cmd"]

    def test_lich_version_calls_version(self, monkeypatch):
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "v1.0.0"
        monkeypatch.setattr("lich.mcp.tools.utility.run_lich_command", fake_run)
        out = mcp_utility.lich_version()
        assert captured["cmd"] == ["lich", "version"]
        assert out == "v1.0.0"

    def test_register_utility_tools_registers_3(self):
        """register_utility_tools registers 3 tools."""
        registered = []
        mock_mcp = MagicMock()
        mock_mcp.tool.return_value = lambda fn: registered.append(fn) or fn
        mcp_utility.register_utility_tools(mock_mcp)
        assert len(registered) == 3


# ============================================================
# mcp/tools/git.py  (currently 62%)
# ============================================================

class TestMcpGitTools:
    """Tests for mcp/tools/git.py."""

    def test_lich_git_commit_rejects_empty_message(self):
        """lich_git_commit rejects empty message."""
        out = mcp_git.lich_git_commit("")
        assert "ERROR" in out

    def test_lich_git_commit_rejects_dash_message(self):
        """lich_git_commit rejects dash-prefixed message."""
        out = mcp_git.lich_git_commit("-bad")
        assert "ERROR" in out

    def test_lich_git_commit_valid(self, monkeypatch):
        """lich_git_commit calls git_commit with the message."""
        called = {}
        def fake_commit(message):
            called["msg"] = message
        monkeypatch.setattr("lich.mcp.tools.git.git_commit", fake_commit)
        out = mcp_git.lich_git_commit("feat: add feature")
        assert called["msg"] == "feat: add feature"
        assert "feat: add feature" in out

    def test_lich_git_tag_invalid_version(self):
        """lich_git_tag rejects invalid git ref."""
        out = mcp_git.lich_git_tag("../bad")
        assert "ERROR" in out

    def test_lich_git_tag_valid(self, monkeypatch):
        """lich_git_tag calls git_tag with valid version."""
        called = {}
        def fake_tag(version, push=False):
            called["version"] = version
            called["push"] = push
        monkeypatch.setattr("lich.mcp.tools.git.git_tag", fake_tag)
        out = mcp_git.lich_git_tag("v1.2.3")
        assert called["version"] == "v1.2.3"
        assert called["push"] is False
        assert "v1.2.3" in out

    def test_lich_git_tag_with_push(self, monkeypatch):
        """lich_git_tag passes push=True."""
        called = {}
        def fake_tag(version, push=False):
            called["push"] = push
        monkeypatch.setattr("lich.mcp.tools.git.git_tag", fake_tag)
        mcp_git.lich_git_tag("v1.0.0", push=True)
        assert called["push"] is True

    def test_lich_git_push(self, monkeypatch):
        """lich_git_push calls git_push."""
        called = {}
        def fake_push(tags=False):
            called["tags"] = tags
        monkeypatch.setattr("lich.mcp.tools.git.git_push", fake_push)
        out = mcp_git.lich_git_push()
        assert called["tags"] is False
        assert "Pushed" in out

    def test_lich_git_push_with_tags(self, monkeypatch):
        """lich_git_push passes tags=True."""
        called = {}
        def fake_push(tags=False):
            called["tags"] = tags
        monkeypatch.setattr("lich.mcp.tools.git.git_push", fake_push)
        mcp_git.lich_git_push(tags=True)
        assert called["tags"] is True

    def test_register_git_tools_registers_3(self):
        """register_git_tools registers 3 tools."""
        registered = []
        mock_mcp = MagicMock()
        mock_mcp.tool.return_value = lambda fn: registered.append(fn) or fn
        mcp_git.register_git_tools(mock_mcp)
        assert len(registered) == 3
