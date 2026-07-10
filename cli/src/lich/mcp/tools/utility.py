"""
MCP Tools for Utility Commands (adopt, upgrade, version).
"""
from . import run_lich_command


def lich_adopt(path: str, output: str = ".", dry_run: bool = True) -> str:
    """
    Adopt an existing Python project into Lich architecture.

    Analyzes the project and suggests a Lich configuration.

    Args:
        path: Path to existing Python project.
        output: Output directory for new Lich project.
        dry_run: If True, only analyze without creating project.
    """
    # M2: guard against empty or dash-prefixed path/output (option smuggling)
    if not path or path.startswith("-"):
        return "ERROR: 'path' must not be empty or start with '-'."
    if not output or output.startswith("-"):
        return "ERROR: 'output' must not be empty or start with '-'."

    cmd = ["lich", "adopt", path, "-o", output]
    if dry_run:
        cmd.append("--dry-run")
    return run_lich_command(cmd)


def lich_upgrade(force: bool = False) -> str:
    """
    Upgrade project to the latest Lich Toolkit version.

    Updates .lich/rules/, .lich/workflows/, AGENTS.md, CLAUDE.md.

    Args:
        force: If True, skip confirmation prompt.
    """
    cmd = ["lich", "upgrade"]
    if force:
        cmd.append("--force")
    return run_lich_command(cmd)


def lich_version() -> str:
    """
    Show Lich Toolkit version information.
    """
    return run_lich_command(["lich", "version"])


_TOOLS = [lich_adopt, lich_upgrade, lich_version]


def register_utility_tools(mcp):
    """Register Utility tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
