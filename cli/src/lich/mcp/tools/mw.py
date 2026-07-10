"""
MCP Tools for Middleware Management.
"""
from . import run_lich_command


def lich_middleware_list() -> str:
    """
    List all available middlewares and their status (enabled/disabled).

    Shows timing, security, logging, and rate_limit middleware status.
    """
    return run_lich_command(["lich", "middleware", "list"])


def lich_middleware_enable(name: str) -> str:
    """
    Enable a middleware in the project.

    Args:
        name: Middleware name - 'timing', 'security', 'logging', or 'rate_limit'.
    """
    return run_lich_command(["lich", "middleware", "enable", name])


def lich_middleware_disable(name: str) -> str:
    """
    Disable a middleware in the project.

    Args:
        name: Middleware name - 'timing', 'security', 'logging', or 'rate_limit'.
    """
    return run_lich_command(["lich", "middleware", "disable", name])


_TOOLS = [lich_middleware_list, lich_middleware_enable, lich_middleware_disable]


def register_middleware_tools(mcp):
    """Register Middleware management tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
