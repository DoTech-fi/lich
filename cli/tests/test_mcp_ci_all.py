"""Tests for the lich_ci_all MCP tool."""
import pytest
from mcp.server.fastmcp import FastMCP

from lich.mcp.tools import ci


def _get_tool(name: str):
    mcp = FastMCP("TestLich")
    ci.register_ci_tools(mcp)
    tools_map = {t.name: t.fn for t in mcp._tool_manager.list_tools()}
    return tools_map.get(name)


def test_ci_all_is_registered():
    assert _get_tool("lich_ci_all") is not None


@pytest.mark.asyncio
async def test_ci_all_runs_all_components(mocker):
    recorded = []

    async def fake_async(cmd, force_no_color=True):
        recorded.append(cmd)
        return "ok"

    mocker.patch("lich.mcp.tools.ci.run_lich_command_async", side_effect=fake_async)

    tool = _get_tool("lich_ci_all")
    output = await tool(local=True)

    assert ["lich", "ci", "backend", "-l"] in recorded
    assert ["lich", "ci", "web", "-l"] in recorded
    assert ["lich", "ci", "admin", "-l"] in recorded
    assert ["lich", "ci", "landing", "-l"] in recorded
    assert "backend" in output and "landing" in output
