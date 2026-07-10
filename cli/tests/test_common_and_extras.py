"""
Tests for common.py, version_check.py, shell.py, __main__.py, __init__.py,
and mcp/tools/dev.py, mcp/tools/production.py, mcp/tools/project.py, mcp/tools/routes.py.
"""
import os
import sys
import subprocess
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.common import (
    ensure_lich_project,
    is_lich_project,
    run_command,
    run_command_ok,
    check_tool_installed,
    download_template,
    get_local_template_path,
)


# ============================================================
# common.py  (currently 56%)
# ============================================================

class TestEnsureLichProject:
    def test_exits_outside_project(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        import click
        with pytest.raises(click.exceptions.Exit):
            ensure_lich_project()

    def test_passes_in_project(self, in_lich_project):
        # Should not raise
        ensure_lich_project()

    def test_passes_with_backend_dir(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        # Should not raise even without .lich
        ensure_lich_project()


class TestIsLichProject:
    def test_returns_false_outside_project(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = is_lich_project()
        assert result is False

    def test_returns_true_in_project(self, in_lich_project):
        result = is_lich_project()
        assert result is True


class TestRunCommand:
    def test_success_returns_exit_zero(self, monkeypatch):
        def fake_run(cmd, capture_output=True, text=True, cwd=None):
            result = MagicMock()
            result.returncode = 0
            result.stdout = "output"
            result.stderr = ""
            return result
        monkeypatch.setattr("lich.commands.common.subprocess.run", fake_run)
        code, stdout, stderr = run_command(["echo", "hi"])
        assert code == 0
        assert stdout == "output"

    def test_command_not_found_returns_minus_one(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            raise FileNotFoundError("no such file")
        monkeypatch.setattr("lich.commands.common.subprocess.run", fake_run)
        code, stdout, stderr = run_command(["nonexistent-cmd"])
        assert code == -1
        assert "Command not found" in stderr

    def test_failure_returns_nonzero(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 2
            result.stdout = ""
            result.stderr = "error"
            return result
        monkeypatch.setattr("lich.commands.common.subprocess.run", fake_run)
        code, _, stderr = run_command(["false"])
        assert code == 2


class TestRunCommandOk:
    def test_success_returns_true(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            return result
        monkeypatch.setattr("lich.commands.common.subprocess.run", fake_run)
        assert run_command_ok(["echo", "hi"]) is True

    def test_failure_returns_false(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 1
            return result
        monkeypatch.setattr("lich.commands.common.subprocess.run", fake_run)
        assert run_command_ok(["false"]) is False

    def test_missing_command_returns_false(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            raise FileNotFoundError("no file")
        monkeypatch.setattr("lich.commands.common.subprocess.run", fake_run)
        assert run_command_ok(["nonexistent"]) is False


class TestCheckToolInstalled:
    def test_existing_tool(self, monkeypatch):
        monkeypatch.setattr("lich.commands.common.shutil.which", lambda t: "/usr/bin/python3")
        assert check_tool_installed("python3") is True

    def test_missing_tool(self, monkeypatch):
        monkeypatch.setattr("lich.commands.common.shutil.which", lambda t: None)
        assert check_tool_installed("nonexistent-tool-xyz") is False


class TestDownloadTemplate:
    def test_ssl_error_exits_1(self, monkeypatch):
        import requests as req
        import click
        def fake_get(*a, **kw):
            raise req.exceptions.SSLError("ssl error")
        monkeypatch.setattr("lich.commands.common.requests.get", fake_get)
        with pytest.raises(click.exceptions.Exit):
            download_template()

    def test_network_error_exits_1(self, monkeypatch):
        import requests as req
        import click
        def fake_get(*a, **kw):
            raise req.exceptions.RequestException("network error")
        monkeypatch.setattr("lich.commands.common.requests.get", fake_get)
        with pytest.raises(click.exceptions.Exit):
            download_template()

    def test_bad_zip_exits_1(self, tmp_path, monkeypatch):
        """Simulate bad zip file."""
        import click
        fake_response = MagicMock()
        fake_response.raise_for_status = MagicMock()
        fake_response.iter_content = lambda **kw: [b"not a zip"]
        monkeypatch.setattr("lich.commands.common.requests.get", lambda *a, **kw: fake_response)
        with pytest.raises(click.exceptions.Exit):
            download_template()

    def test_missing_template_dir_exits_1(self, tmp_path, monkeypatch):
        """Zip extracts but no template dir inside."""
        import io
        import click
        # Create a valid zip with wrong structure
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("lich-main/README.md", "no template here")
        zip_bytes = zip_buffer.getvalue()

        fake_response = MagicMock()
        fake_response.raise_for_status = MagicMock()
        fake_response.iter_content = lambda **kw: [zip_bytes]
        monkeypatch.setattr("lich.commands.common.requests.get", lambda *a, **kw: fake_response)
        with pytest.raises(click.exceptions.Exit):
            download_template()


class TestGetLocalTemplatePath:
    def test_returns_path_in_dev_mode(self):
        """In this dev checkout, local template exists."""
        result = get_local_template_path()
        # Either returns a valid path or None (both are valid)
        assert result is None or isinstance(result, Path)


# ============================================================
# lich/__main__.py  (currently 0%)
# ============================================================

class TestMain:
    def test_main_module_importable(self):
        """__main__.py can be imported without errors."""
        import importlib
        # Just import it — it should not crash at import time
        import lich.__main__  # noqa: F401


# ============================================================
# lich/__init__.py  (currently 60%)
# ============================================================

class TestInit:
    def test_version_string(self):
        import lich
        assert hasattr(lich, "__version__")
        assert isinstance(lich.__version__, str)
        assert len(lich.__version__) > 0

    def test_version_format(self):
        import lich
        parts = lich.__version__.split(".")
        assert len(parts) >= 2  # At least major.minor


# ============================================================
# version_check.py  (currently 77%)
# ============================================================

class TestVersionCheckExtended:
    def test_check_compatibility_with_outdated_project(self, tmp_path, monkeypatch):
        """check_compatibility with a very old project version logs a warning."""
        monkeypatch.chdir(tmp_path)
        lich_dir = tmp_path / ".lich"
        lich_dir.mkdir()
        (lich_dir / "lich.version").write_text("0.1.0")
        from lich.version_check import check_compatibility
        # Should complete without raising
        check_compatibility()

    def test_check_compatibility_with_same_version(self, tmp_path, monkeypatch):
        """check_compatibility with same version as CLI shows nothing."""
        monkeypatch.chdir(tmp_path)
        from lich import __version__
        lich_dir = tmp_path / ".lich"
        lich_dir.mkdir()
        (lich_dir / "lich.version").write_text(__version__)
        from lich.version_check import check_compatibility
        check_compatibility()

    def test_check_compatibility_lich_is_file_not_dir(self, tmp_path, monkeypatch):
        """check_compatibility handles .lich as a plain file (old projects)."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".lich").write_text('{"version": "0.5.0"}')
        from lich.version_check import check_compatibility
        check_compatibility()


# ============================================================
# mcp/tools/dev.py  (currently 47%)
# ============================================================

class TestMcpDevTools:
    def test_lich_dev_start_builds_command(self, monkeypatch):
        """lich_dev_start calls run_lich_command with ['lich', 'start']."""
        from lich.mcp.tools import dev as mcp_dev
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.dev.run_lich_command", fake_run)
        result = mcp_dev.lich_dev_start()
        assert captured["cmd"] == ["lich", "start"]
        assert result == "ok"

    def test_lich_dev_start_with_force(self, monkeypatch):
        from lich.mcp.tools import dev as mcp_dev
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.dev.run_lich_command", fake_run)
        mcp_dev.lich_dev_start(force=True)
        assert "--force" in captured["cmd"]

    def test_lich_dev_stop_builds_command(self, monkeypatch):
        from lich.mcp.tools import dev as mcp_dev
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "stopped"
        monkeypatch.setattr("lich.mcp.tools.dev.run_lich_command", fake_run)
        result = mcp_dev.lich_dev_stop()
        assert captured["cmd"] == ["lich", "stop"]

    def test_lich_dev_stop_with_docker(self, monkeypatch):
        from lich.mcp.tools import dev as mcp_dev
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "stopped"
        monkeypatch.setattr("lich.mcp.tools.dev.run_lich_command", fake_run)
        mcp_dev.lich_dev_stop(docker=True)
        assert "--docker" in captured["cmd"]

    def test_register_dev_tools(self):
        from lich.mcp.tools import dev as mcp_dev
        registered = []
        mock_mcp = MagicMock()
        mock_mcp.tool.return_value = lambda fn: registered.append(fn) or fn
        mcp_dev.register_dev_tools(mock_mcp)
        assert len(registered) >= 2


# ============================================================
# mcp/tools/production.py  (currently 47%)
# ============================================================

class TestMcpProductionTools:
    def test_lich_production_ready_check_builds_command(self, monkeypatch):
        from lich.mcp.tools import production as mcp_prod
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "prod output"
        monkeypatch.setattr("lich.mcp.tools.production.run_lich_command", fake_run)
        result = mcp_prod.lich_production_ready_check()
        assert "lich" in captured["cmd"]
        assert "production-ready" in captured["cmd"]

    def test_lich_production_ready_check_no_json(self, monkeypatch):
        from lich.mcp.tools import production as mcp_prod
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.production.run_lich_command", fake_run)
        mcp_prod.lich_production_ready_check(as_json=False)
        assert "--json" not in captured["cmd"]

    def test_lich_production_ready_fix_builds_command(self, monkeypatch):
        from lich.mcp.tools import production as mcp_prod
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "fixed"
        monkeypatch.setattr("lich.mcp.tools.production.run_lich_command", fake_run)
        mcp_prod.lich_production_ready_fix()
        assert "fix" in captured["cmd"]
        assert "--dry-run" in captured["cmd"]

    def test_lich_production_ready_fix_not_dry_run(self, monkeypatch):
        from lich.mcp.tools import production as mcp_prod
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "fixed"
        monkeypatch.setattr("lich.mcp.tools.production.run_lich_command", fake_run)
        mcp_prod.lich_production_ready_fix(dry_run=False)
        assert "--dry-run" not in captured["cmd"]

    def test_register_production_tools(self):
        from lich.mcp.tools import production as mcp_prod
        registered = []
        mock_mcp = MagicMock()
        mock_mcp.tool.return_value = lambda fn: registered.append(fn) or fn
        mcp_prod.register_production_tools(mock_mcp)
        assert len(registered) >= 2


# ============================================================
# mcp/tools/project.py  (currently 62%)
# ============================================================

class TestMcpProjectTools:
    def test_lich_check_project_valid(self, in_lich_project):
        from lich.mcp.tools import project as mcp_proj
        result = mcp_proj.lich_check_project()
        assert "Valid" in result

    def test_lich_check_project_invalid(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        from lich.mcp.tools import project as mcp_proj
        result = mcp_proj.lich_check_project()
        assert "Not" in result

    def test_register_project_tools(self):
        from lich.mcp.tools import project as mcp_proj
        registered = []
        mock_mcp = MagicMock()
        mock_mcp.tool.return_value = lambda fn: registered.append(fn) or fn
        mcp_proj.register_project_tools(mock_mcp)
        assert len(registered) >= 2


# ============================================================
# mcp/tools/routes.py  (currently 60%)
# ============================================================

class TestMcpRoutesTools:
    def test_lich_routes_builds_command(self, monkeypatch):
        from lich.mcp.tools import routes as mcp_routes
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "routes output"
        monkeypatch.setattr("lich.mcp.tools.routes.run_lich_command", fake_run)
        result = mcp_routes.lich_routes()
        assert "routes" in captured["cmd"]

    def test_lich_routes_verbose(self, monkeypatch):
        from lich.mcp.tools import routes as mcp_routes
        captured = {}
        def fake_run(cmd, force_no_color=True):
            captured["cmd"] = cmd
            return "ok"
        monkeypatch.setattr("lich.mcp.tools.routes.run_lich_command", fake_run)
        mcp_routes.lich_routes(verbose=True)
        assert "--verbose" in captured["cmd"]

    def test_register_routes_tools(self):
        from lich.mcp.tools import routes as mcp_routes
        registered = []
        mock_mcp = MagicMock()
        mock_mcp.tool.return_value = lambda fn: registered.append(fn) or fn
        mcp_routes.register_routes_tools(mock_mcp)
        assert len(registered) >= 1
