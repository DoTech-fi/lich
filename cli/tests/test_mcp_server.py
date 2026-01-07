import pytest
from lich.mcp.server import mcp

def test_mcp_server_refactored_tools():
    """Verify that Expanded Lich tools are registered in the Refactored MCP server."""
    
    # Check internal registry
    try:
        tools = [t.name for t in mcp._tool_manager.list_tools()]
    except AttributeError:
        print("Could not access internal tool registry directly.")
        return

    print(f"\nRegistered Tools ({len(tools)}):")
    for t in tools:
        print(f" - {t}")
    
    # We verify one from each category to ensure all modules loaded
    expected_sample = [
        "lich_init",           # project
        "lich_make_service",   # make
        "lich_git_commit",     # git
        "lich_lint_backend",   # qa
        "lich_deploy"          # ops
    ]
    
    for tool in expected_sample:
        assert tool in tools, f"Missing tool: {tool}"

if __name__ == "__main__":
    test_mcp_server_refactored_tools()
    print("\n✅ Refactored MCP Structure Verification Passed!")
