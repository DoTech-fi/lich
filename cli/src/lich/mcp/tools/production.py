"""
MCP Tools for Production Readiness Checks.
"""
from . import run_lich_command


def lich_production_ready_check(as_json: bool = True) -> str:
    """
    Check if the project is production-ready.

    Runs comprehensive checks for security, configuration, and best practices.

    Args:
        as_json: If True, return results as JSON for easier parsing.
    """
    cmd = ["lich", "production-ready"]
    if as_json:
        cmd.append("--json")
    return run_lich_command(cmd)


def lich_production_ready_fix(dry_run: bool = True) -> str:
    """
    Auto-fix common production readiness issues.

    Can fix issues like weak secrets, debug mode, etc.

    Args:
        dry_run: If True, show what would be fixed without actually fixing.
    """
    cmd = ["lich", "production-ready", "fix"]
    if dry_run:
        cmd.append("--dry-run")
    return run_lich_command(cmd)


_TOOLS = [lich_production_ready_check, lich_production_ready_fix]


def register_production_tools(mcp):
    """Register Production-readiness tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
