"""
MCP Tools for Development Environment Management.
"""
from . import run_lich_command


def lich_dev_start(force: bool = False) -> str:
    """
    Start the full development environment.

    Starts Docker containers, backend, and frontend apps.

    Args:
        force: If True, force kill processes using required ports.
    """
    cmd = ["lich", "start"]
    if force:
        cmd.append("--force")
    return run_lich_command(cmd)


def lich_dev_stop(docker: bool = False) -> str:
    """
    Stop all running development services.

    Args:
        docker: If True, also stop Docker containers.
    """
    cmd = ["lich", "stop"]
    if docker:
        cmd.append("--docker")
    return run_lich_command(cmd)


_TOOLS = [lich_dev_start, lich_dev_stop]


def register_dev_tools(mcp):
    """Register Development environment tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
