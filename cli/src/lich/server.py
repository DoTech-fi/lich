from mcp.server.fastmcp import FastMCP
from pathlib import Path
from typing import Optional
from lich.commands.make import make_service, make_entity
from lich.commands.init import init_project

# Initialize FastMCP Server
mcp = FastMCP("Lich Framework")

@mcp.tool()
def lich_init(project_name: str, template_url: str = "https://github.com/DoTech-fi/lich-fastapi", output_dir: str = "."):
    """
    Initialize a new Lich project using a cookiecutter template.
    """
    result = init_project(
        template=template_url,
        no_input=True,
        output_dir=Path(output_dir),
        extra_context={"project_slug": project_name}
    )
    return str(result)

@mcp.tool()
def lich_make_service(name: str):
    """
    Create a new Backend Service (Use Case) in the current Lich project.
    """
    make_service(name)
    return f"Service '{name}' created successfully."

@mcp.tool()
def lich_make_entity(name: str):
    """
    Create a new Domain Entity in the current Lich project.
    """
    make_entity(name)
    return f"Entity '{name}' created successfully."

@mcp.tool()
def lich_check_project() -> str:
    """
    Check if the current directory is a valid Lich project.
    """
    if Path(".lich").exists():
        return "Valid Lich Project Detected ✅"
    return "Not a Lich Project ❌"

def start_server():
    """Start the MCP server on stdio."""
    mcp.run()
