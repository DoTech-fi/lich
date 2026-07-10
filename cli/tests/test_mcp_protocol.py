"""
Protocol-level smoke test: spawn the real MCP server over stdio and speak
JSON-RPC to it. Guards against stdout pollution and registration regressions
that in-process tests cannot catch.
"""
import asyncio
import os
import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command=sys.executable,
    args=["-m", "lich", "serve"],
    env={**os.environ, "PYTHONPATH": "src"},
)

# Keep in sync with test_mcp_server.py's canonical count.
MIN_EXPECTED_TOOLS = 52


async def _run_smoke() -> tuple[list[str], str]:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            call_result = await session.call_tool("lich_routes", {"verbose": False})
            text = call_result.content[0].text
            return tool_names, text


@pytest.mark.asyncio
async def test_mcp_stdio_protocol_smoke():
    tool_names, routes_text = await asyncio.wait_for(_run_smoke(), timeout=60)

    assert len(tool_names) >= MIN_EXPECTED_TOOLS
    assert "lich_routes" in tool_names
    assert "lich_make_entity" in tool_names

    # Outside a lich project the tool returns an error string --
    # what matters here is that the call completed over the protocol
    # and returned text, not that routes exist.
    assert isinstance(routes_text, str)
    assert len(routes_text) > 0
