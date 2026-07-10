from pathlib import Path
from lich.commands.init import init_project


def lich_init(project_name: str, output_dir: str = "."):
    """Initialize a new Lich project using the default Lich template."""
    result = init_project(
        name=project_name,
        output_dir=output_dir,
        no_input=True,
    )
    return str(result)


def lich_check_project() -> str:
    """Check if the current directory is a valid Lich project."""
    if Path(".lich").exists():
        return "Valid Lich Project Detected ✅"
    return "Not a Lich Project ❌"


_TOOLS = [lich_init, lich_check_project]


def register_project_tools(mcp):
    """Register Project-related tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
