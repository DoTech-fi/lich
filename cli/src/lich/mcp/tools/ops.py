"""
MCP Tools for Ops (Deploy/Backup) — long-running, so async.
"""
from typing import Optional

from . import run_lich_command_async


def lich_deploy_setup() -> str:
    """
    Setup deployment configuration.

    Interactive setup for staging and production environments.
    Configures SSH connection, deploy path, and git repo.
    """
    return (
        "Deploy setup is interactive. Run manually:\n\n"
        "  lich deploy setup\n\n"
        "This will ask:\n"
        "- Environment (staging/production)\n"
        "- SSH config or manual connection\n"
        "- Deploy path on server\n"
        "- Git repository URL"
    )


async def lich_deploy_stage(component: str, version: Optional[str] = None, dry_run: bool = False) -> str:
    """
    Deploy a component to staging environment.

    Args:
        component: Component to deploy (backend, web, admin, landing)
        version: Version/tag to deploy (optional, defaults to latest)
        dry_run: If True, preview without deploying
    """
    cmd = ["lich", "deploy", "stage", component]
    if version:
        cmd.extend(["--version", version])
    if dry_run:
        cmd.append("--dry-run")
    return await run_lich_command_async(cmd)


async def lich_deploy_prod(component: str, version: Optional[str] = None, dry_run: bool = False) -> str:
    """
    Deploy a component to production environment.

    WARNING: This deploys to production! Use --dry-run first.

    Args:
        component: Component to deploy (backend, web, admin, landing)
        version: Version/tag to deploy (optional, defaults to latest)
        dry_run: If True, preview without deploying
    """
    cmd = ["lich", "deploy", "prod", component, "--force"]  # --force for non-interactive
    if version:
        cmd.extend(["--version", version])
    if dry_run:
        cmd.append("--dry-run")
    return await run_lich_command_async(cmd)


async def lich_deploy_status() -> str:
    """
    Show deployment configuration status.

    Displays configured environments and their connection settings.
    """
    return await run_lich_command_async(["lich", "deploy", "status"])


async def lich_backup(list_backups: bool = False) -> str:
    """Manage database backups."""
    cmd = ["lich", "backup"]
    if list_backups:
        cmd.append("--list")
    return await run_lich_command_async(cmd)


_TOOLS = [lich_deploy_setup, lich_deploy_stage, lich_deploy_prod, lich_deploy_status, lich_backup]


def register_ops_tools(mcp):
    """Register Ops tools (Deploy/Backup)."""
    for tool in _TOOLS:
        mcp.tool()(tool)
