"""
lich init - Create a new Lich project.
"""
import os
from pathlib import Path
from typing import Optional

import typer
from cookiecutter.main import cookiecutter
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

# Path to the template (relative to CLI package)
# cli/src/lich/commands/init.py -> ../../.. -> cli -> .. -> lich-framework/template
TEMPLATE_PATH = Path(__file__).parent.parent.parent.parent.parent / "template"


def init_project(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name"),
    project_type: Optional[str] = typer.Option(None, "--type", "-t", help="Project type"),
    output_dir: Optional[str] = typer.Option(".", "--output", "-o", help="Output directory"),
    no_input: bool = typer.Option(False, "--no-input", help="Use defaults without prompting"),
):
    """
    Create a new Lich project.
    
    Examples:
        lich init
        lich init --name "My App" --type saas_platform
        lich init --no-input
    """
    console.print("\n🧙 [bold blue]Lich Framework[/bold blue] - Project Generator\n")
    
    # Check if template exists
    if not TEMPLATE_PATH.exists():
        # Try alternative path (when installed as package)
        alt_template = Path(__file__).parent.parent / "template"
        if alt_template.exists():
            template_path = alt_template
        else:
            console.print("[red]❌ Template not found![/red]")
            console.print(f"   Expected at: {TEMPLATE_PATH}")
            raise typer.Exit(1)
    else:
        template_path = TEMPLATE_PATH
    
    # Build extra context from options
    extra_context = {}
    if name:
        extra_context["project_name"] = name
    if project_type:
        extra_context["project_type"] = project_type
    
    try:
        # Run cookiecutter
        result = cookiecutter(
            str(template_path),
            output_dir=output_dir,
            no_input=no_input,
            extra_context=extra_context if extra_context else None,
        )
        
        project_name = Path(result).name
        
        console.print(f"\n[green]✅ Project created successfully![/green]")
        console.print(f"\n[bold]Next steps:[/bold]")
        console.print(f"   cd {project_name}")
        console.print(f"   lich dev")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
