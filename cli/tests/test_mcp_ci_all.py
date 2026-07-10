"""Tests for the lich_ci_all MCP tool."""
from mcp.server.fastmcp import FastMCP

from lich.mcp.tools import ci


def _get_tool(name: str):
    mcp = FastMCP("TestLich")
    ci.register_ci_tools(mcp)
    tools_map = {t.name: t.fn for t in mcp._tool_manager.list_tools()}
    return tools_map.get(name)


def test_ci_all_is_registered():
    assert _get_tool("lich_ci_all") is not None


def test_ci_all_runs_all_components(mocker):
    mock_run = mocker.patch("lich.mcp.tools.ci.subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    tool = _get_tool("lich_ci_all")
    output = tool(local=True)

    called_cmds = [call.args[0] for call in mock_run.call_args_list]
    assert ["lich", "ci", "backend", "-l"] in called_cmds
    assert ["lich", "ci", "web", "-l"] in called_cmds
    assert ["lich", "ci", "admin", "-l"] in called_cmds
    assert ["lich", "ci", "landing", "-l"] in called_cmds
    assert "backend" in output and "landing" in output
