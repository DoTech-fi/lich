"""
lich init - Create a new Lich project.
"""
from pathlib import Path
from typing import Optional

import typer
from cookiecutter.main import cookiecutter
from rich.console import Console

from lich import __version__
from lich.commands.common import (
    get_local_template_path as _get_local_template_path,
    download_template as _download_template,
)

console = Console()


def init_project(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name"),
    project_type: Optional[str] = typer.Option(None, "--type", "-t", help="Project type"),
    output_dir: Optional[str] = typer.Option(".", "--output", "-o", help="Output directory"),
    no_input: bool = typer.Option(False, "--no-input", help="Use defaults without prompting"),
    local: bool = typer.Option(False, "--local", help="Use local template (development)"),
):
    """
    Create a new Lich project.
    
    Examples:
        lich init
        lich init --name "My App" --type saas_platform
        lich init --no-input
    """
    console.print("\n🧙 [bold blue]Lich Toolkit[/bold blue] - Project Generator\n")
    
    # Get template path
    local_path = _get_local_template_path()
    
    if local and local_path:
        template_path = str(local_path)
        console.print("[dim]Using local template (development mode)[/dim]\n")
    elif local_path:
        # Local development - use local template
        template_path = str(local_path)
    else:
        # Production - download from GitHub
        template_path = _download_template()
    
    # Build extra context from options
    extra_context = {"_lich_version": __version__}
    if name:
        extra_context["project_name"] = name
    if project_type:
        extra_context["project_type"] = project_type
    
    try:
        # Run cookiecutter
        result = cookiecutter(
            template_path,
            output_dir=output_dir,
            no_input=no_input,
            extra_context=extra_context if extra_context else None,
        )
        
        project_name = Path(result).name
        
        console.print("\n[green]✅ Project created successfully![/green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"   cd {project_name}")
        console.print("   lich dev")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
