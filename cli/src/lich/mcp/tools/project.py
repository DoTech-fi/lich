from pathlib import Path
from lich.commands.init import init_project

def register_project_tools(mcp):
    """Register Project-related tools."""

    @mcp.tool()
    def lich_init(project_name: str, template_url: str = "https://github.com/DoTech-fi/lich-fastapi", output_dir: str = "."):
        """Initialize a new Lich project using a cookiecutter template."""
        result = init_project(
            template=template_url,
            no_input=True,
            output_dir=Path(output_dir),
            extra_context={"project_slug": project_name}
        )
        return str(result)

    @mcp.tool()
    def lich_check_project() -> str:
        """Check if the current directory is a valid Lich project."""
        if Path(".lich").exists():
            return "Valid Lich Project Detected ✅"
        return "Not a Lich Project ❌"
