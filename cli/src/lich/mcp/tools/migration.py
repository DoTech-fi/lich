"""
MCP Tools for Database Migrations (Alembic wrapper) — stateful and slow, so async.
"""
from lich.commands._validate import ValidationError, validate_identifier

from . import run_lich_command_async


async def lich_migration_init() -> str:
    """
    Initialize Alembic migrations for the project.

    Creates the alembic directory structure and configuration files.
    """
    return await run_lich_command_async(["lich", "migration", "init"])


async def lich_migration_create(message: str, autogenerate: bool = True) -> str:
    """
    Create a new database migration.

    Args:
        message: Migration message/name (e.g., 'add_users_table').
        autogenerate: If True, auto-generate from model changes.
    """
    try:
        message = validate_identifier(message)
    except ValidationError as e:
        return f"ERROR: {e}"
    cmd = ["lich", "migration", "create", message]
    if not autogenerate:
        cmd.append("--manual")
    return await run_lich_command_async(cmd)


async def lich_migration_up(revision: str = "head") -> str:
    """
    Apply database migrations (upgrade).

    Args:
        revision: Target revision (default: 'head' for latest).
    """
    return await run_lich_command_async(["lich", "migration", "up", revision])


async def lich_migration_down(revision: str = "-1") -> str:
    """
    Rollback database migrations (downgrade).

    Args:
        revision: Target revision (default: '-1' for one step back).
    """
    return await run_lich_command_async(["lich", "migration", "down", revision])


async def lich_migration_status() -> str:
    """
    Show current database migration status.

    Displays current revision and migration history.
    """
    return await run_lich_command_async(["lich", "migration", "status"])


async def lich_migration_heads() -> str:
    """
    Show available migration heads.
    """
    return await run_lich_command_async(["lich", "migration", "heads"])


_TOOLS = [
    lich_migration_init,
    lich_migration_create,
    lich_migration_up,
    lich_migration_down,
    lich_migration_heads,
    lich_migration_status,
]


def register_migration_tools(mcp):
    """Register Migration-related tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
