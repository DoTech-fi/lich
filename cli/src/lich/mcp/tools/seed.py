"""
MCP Tools for Database Seeding.
"""
from typing import Optional

from lich.commands._validate import ValidationError, validate_identifier

from . import run_lich_command


def lich_seed(name: Optional[str] = None, fresh: bool = False) -> str:
    """
    Seed the database with test data.

    Args:
        name: Specific seeder to run (e.g., 'users'). If None, runs all seeders.
        fresh: If True, re-run migrations before seeding.
    """
    # M1: validate name before passing to subprocess (only when provided)
    if name:
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"

    cmd = ["lich", "seed"]
    if name:
        cmd.append(name)
    if fresh:
        cmd.append("--fresh")
    return run_lich_command(cmd)


def lich_seed_list() -> str:
    """
    List all available database seeders.
    """
    return run_lich_command(["lich", "seed", "--list"])


_TOOLS = [lich_seed, lich_seed_list]


def register_seed_tools(mcp):
    """Register Seed-related tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
