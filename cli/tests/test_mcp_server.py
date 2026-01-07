from lich.server import mcp
import pytest
from mcp.types import Tool

def test_mcp_server_tools():
    """Verify that Lich tools are registered in the MCP server."""
    # FastMCP exposes a .list_tools() method (async) or we can check internal registry
    # For unit testing, we can check the internal _tools registry if accessible,
    # or just verity the function names are decorated.
    
    # In FastMCP (mcp-python-sdk), tools are stored in mcp._tool_manager._tools
    # But that's internal. Let's try to mock the listing.
    
    # Actually, simpler: FastMCP object has a `list_tools` awaitable. 
    # But since we want to avoid async complexity in this simple test script without asyncio runner,
    # we can inspect the decorated functions directly if FastMCP exposes them.
    
    # Let's try to inspect the `mcp` object details in the test output
    # to confirm registration.
    
    tools = [t.name for t in mcp._tool_manager.list_tools()]
    
    print(f"Registered Tools: {tools}")
    
    assert "lich_init" in tools
    assert "lich_make_service" in tools
    assert "lich_make_entity" in tools
    assert "lich_check_project" in tools

if __name__ == "__main__":
    test_mcp_server_tools()
    print("✅ MCP Server Verification Passed!")
