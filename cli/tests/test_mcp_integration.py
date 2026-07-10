from unittest.mock import MagicMock
import pytest
from mcp.server.fastmcp import FastMCP

# Import the registration functions
from lich.mcp.tools import project, make, git, qa, ops

# We need to mock the underlying commands BEFORE importing/registering them
# However, the registration functions import them at module level.
# So we should patch them where they are imported in the tool modules.

def test_mcp_wiring(mocker):
    """Verify that MCP tools are correctly wired to their underlying implementations."""
    mcp = FastMCP("TestLich")

    mock_init = mocker.patch("lich.mcp.tools.project.init_project")
    mock_make_service = mocker.patch("lich.mcp.tools.make.make_service")
    mock_git_commit = mocker.patch("lich.mcp.tools.git.git_commit")
    mock_run = mocker.patch(
        "lich.mcp.tools.ops.run_lich_command", return_value="Deploy success"
    )

    project.register_project_tools(mcp)
    make.register_make_tools(mcp)
    git.register_git_tools(mcp)
    qa.register_qa_tools(mcp)
    ops.register_ops_tools(mcp)

    tools_map = {t.name: t.fn for t in mcp._tool_manager.list_tools()}

    result = tools_map["lich_deploy_status"]()
    mock_run.assert_called_once_with(["lich", "deploy", "status"])
    assert result == "Deploy success"

    mock_run.reset_mock()
    tools_map["lich_deploy_stage"](component="web", version="1.2.3", dry_run=True)
    mock_run.assert_called_once_with(
        ["lich", "deploy", "stage", "web", "--version", "1.2.3", "--dry-run"]
    )

@pytest.mark.asyncio
async def test_mcp_execution_flow(mocker):
    """
    Test invoking the tools via the MCP interface.
    """
    mcp = FastMCP("TestLich")
    
    # Mock implementations
    mock_init = mocker.patch("lich.mcp.tools.project.init_project", return_value="Created")
    mock_make_service = mocker.patch("lich.mcp.tools.make.make_service")
    mock_git_commit = mocker.patch("lich.mcp.tools.git.git_commit")

    # Register
    project.register_project_tools(mcp)
    make.register_make_tools(mcp)
    git.register_git_tools(mcp)
    
    # Call Tools using FastMCP's internal call_tool method
    # FastMCP typically exposes a way to call tools programmatically.
    # If not, we can assume the server loop handles it.
    
    # Alternative: We can refactor `register_*` to NOT define inner functions, 
    # but decorate module-level functions. That is much better for testing.
    # But given current structure:
    
    # We can inspect `mcp._tool_manager._tools` to find the callable.
    
    tools_map = {t.name: t.fn for t in mcp._tool_manager.list_tools()}
    
    # Test: lich_init
    assert "lich_init" in tools_map
    # Our tools are synchronous, so we call them directly
    tools_map["lich_init"](project_name="test_proj", template_url="cx", output_dir=".")
    mock_init.assert_called_once()
    
    # Test: lich_make_service
    assert "lich_make_service" in tools_map
    tools_map["lich_make_service"](name="OrderService")
    mock_make_service.assert_called_once_with("OrderService")
    
    # Test: lich_git_commit
    assert "lich_git_commit" in tools_map
    tools_map["lich_git_commit"](message="feat: test")
    mock_git_commit.assert_called_once_with(message="feat: test")

