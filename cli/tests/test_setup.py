"""
Tests for lich setup command.
"""
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from lich.commands.setup import (
    get_os_type,
    get_antigravity_config_path,
    get_claude_config_path,
    get_cursor_config_path,
    get_vscode_config_path,
    get_lich_mcp_config_antigravity,
    get_lich_mcp_config_claude,
    get_lich_mcp_config_cursor,
    get_lich_mcp_config_vscode,
    merge_mcp_config,
    setup_app,
)

runner = CliRunner()


class TestOSDetection:
    """Test OS detection functions."""
    
    @patch("platform.system", return_value="Darwin")
    def test_detect_macos(self, mock_system):
        assert get_os_type() == "macos"
    
    @patch("platform.system", return_value="Linux")
    def test_detect_linux(self, mock_system):
        assert get_os_type() == "linux"
    
    @patch("platform.system", return_value="Windows")
    def test_detect_windows(self, mock_system):
        assert get_os_type() == "windows"
    
    @patch("platform.system", return_value="FreeBSD")
    def test_detect_unknown(self, mock_system):
        assert get_os_type() == "unknown"


class TestConfigPaths:
    """Test config path resolution."""
    
    def test_antigravity_path(self):
        path = get_antigravity_config_path()
        assert path.name == "settings.json"
        assert ".gemini" in str(path)
    
    @patch("lich.commands.setup.get_os_type", return_value="macos")
    def test_claude_path_macos(self, mock_os):
        path = get_claude_config_path()
        assert path.name == "claude_desktop_config.json"
        assert ".claude" in str(path)
    
    @patch("lich.commands.setup.get_os_type", return_value="windows")
    @patch.dict(os.environ, {"APPDATA": "/mock/appdata"})
    def test_claude_path_windows(self, mock_os):
        path = get_claude_config_path()
        assert path.name == "claude_desktop_config.json"
        assert "Claude" in str(path)
    
    def test_cursor_path(self):
        path = get_cursor_config_path()
        assert path.name == "mcp.json"
        assert ".cursor" in str(path)
    
    def test_vscode_path(self):
        path = get_vscode_config_path()
        assert path.name == "mcp.json"
        assert ".vscode" in str(path)


class TestConfigTemplates:
    """Test MCP config templates."""
    
    @patch("lich.commands.setup.get_lich_executable_path", return_value="lich")
    def test_antigravity_config(self, mock_path):
        config = get_lich_mcp_config_antigravity()
        assert "mcpServers" in config
        assert "lich" in config["mcpServers"]
        assert config["mcpServers"]["lich"]["command"] == "lich"
        assert config["mcpServers"]["lich"]["args"] == ["serve"]
        assert config["mcpServers"]["lich"]["transportType"] == "stdio"
    
    @patch("lich.commands.setup.get_lich_executable_path", return_value="lich")
    def test_claude_config(self, mock_path):
        config = get_lich_mcp_config_claude()
        assert "mcpServers" in config
        assert "lich" in config["mcpServers"]
        assert config["mcpServers"]["lich"]["command"] == "lich"
    
    @patch("lich.commands.setup.get_lich_executable_path", return_value="lich")
    def test_cursor_config(self, mock_path):
        config = get_lich_mcp_config_cursor()
        assert "mcpServers" in config
        assert "lich" in config["mcpServers"]
    
    @patch("lich.commands.setup.get_lich_executable_path", return_value="lich")
    def test_vscode_config(self, mock_path):
        config = get_lich_mcp_config_vscode()
        assert "servers" in config
        assert "lich" in config["servers"]
        assert config["servers"]["lich"]["type"] == "stdio"


class TestConfigMerging:
    """Test config merging logic."""
    
    def test_merge_empty_existing(self):
        existing = {}
        new = {"mcpServers": {"lich": {"command": "lich"}}}
        result = merge_mcp_config(existing, new)
        assert result == new
    
    def test_merge_preserves_other_servers(self):
        existing = {
            "mcpServers": {
                "other-server": {"command": "other"}
            }
        }
        new = {"mcpServers": {"lich": {"command": "lich"}}}
        result = merge_mcp_config(existing, new)
        
        assert "other-server" in result["mcpServers"]
        assert "lich" in result["mcpServers"]
    
    def test_merge_updates_existing_lich(self):
        existing = {
            "mcpServers": {
                "lich": {"command": "old-lich", "args": ["old"]}
            }
        }
        new = {"mcpServers": {"lich": {"command": "lich", "args": ["serve"]}}}
        result = merge_mcp_config(existing, new)
        
        assert result["mcpServers"]["lich"]["command"] == "lich"
        assert result["mcpServers"]["lich"]["args"] == ["serve"]
    
    def test_merge_vscode_format(self):
        existing = {"servers": {"other": {"command": "other"}}}
        new = {"servers": {"lich": {"command": "lich"}}}
        result = merge_mcp_config(existing, new)
        
        assert "other" in result["servers"]
        assert "lich" in result["servers"]
    
    def test_merge_preserves_other_keys(self):
        existing = {"someOtherKey": "value", "mcpServers": {}}
        new = {"mcpServers": {"lich": {"command": "lich"}}}
        result = merge_mcp_config(existing, new)
        
        assert result["someOtherKey"] == "value"


class TestCLICommands:
    """Test CLI command execution."""
    
    def test_status_command(self):
        from lich.cli import app
        result = runner.invoke(app, ["setup", "status"])
        assert result.exit_code == 0
        assert "Antigravity" in result.output or "Configuration Status" in result.output
    
    def test_setup_help(self):
        from lich.cli import app
        result = runner.invoke(app, ["setup", "--help"])
        assert result.exit_code == 0
        assert "antigravity" in result.output
        assert "claude" in result.output
        assert "cursor" in result.output
        assert "vscode" in result.output


class TestConfigureAntigravity:
    """Test Antigravity configuration."""
    
    def test_configure_antigravity_creates_config(self, tmp_path):
        config_path = tmp_path / ".gemini" / "settings.json"
        
        with patch("lich.commands.setup.get_antigravity_config_path", return_value=config_path):
            from lich.cli import app
            result = runner.invoke(app, ["setup", "antigravity"])
            
            assert result.exit_code == 0
            assert config_path.exists()
            
            with open(config_path) as f:
                config = json.load(f)
            
            assert "mcpServers" in config
            assert "lich" in config["mcpServers"]
    
    def test_configure_antigravity_merges_existing(self, tmp_path):
        config_path = tmp_path / ".gemini" / "settings.json"
        config_path.parent.mkdir(parents=True)
        
        # Create existing config with another server
        existing = {"mcpServers": {"other-mcp": {"command": "other"}}}
        with open(config_path, "w") as f:
            json.dump(existing, f)
        
        with patch("lich.commands.setup.get_antigravity_config_path", return_value=config_path):
            from lich.cli import app
            result = runner.invoke(app, ["setup", "antigravity"])
            
            assert result.exit_code == 0
            
            with open(config_path) as f:
                config = json.load(f)
            
            # Both servers should exist
            assert "other-mcp" in config["mcpServers"]
            assert "lich" in config["mcpServers"]
