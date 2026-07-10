"""
MCP Tools for Routes - List all API routes.
"""
from . import run_lich_command


def lich_routes(verbose: bool = False) -> str:
    """
    List all API routes in the project.

    Returns a JSON list of routes with method, path, function, and file.
    """
    cmd = ["lich", "routes"]
    if verbose:
        cmd.append("--verbose")
    return run_lich_command(cmd)


_TOOLS = [lich_routes]


def register_routes_tools(mcp):
    """Register Routes-related tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
