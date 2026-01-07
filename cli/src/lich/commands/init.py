"""
lich init - Create a new Lich project.
"""
import os
import tempfile
from pathlib import Path
from typing import Optional
import zipfile

import typer
import requests
from cookiecutter.main import cookiecutter
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from lich import __version__

console = Console()

# GitHub repository for template
GITHUB_REPO = "DoTech-fi/lich"
GITHUB_BRANCH = "main"
TEMPLATE_URL = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"


def _get_local_template_path() -> Path:
    """Get local template path (for development)."""
    # Try relative to CLI package (development mode)
    dev_path = Path(__file__).parent.parent.parent.parent.parent / "template"
    if dev_path.exists():
        return dev_path
    return None


def _download_template() -> str:
    """Download template from GitHub and return path."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Downloading template from GitHub...", total=None)
        
        # Download to temp directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "lich.zip")
        
        try:
            # Use requests for better SSL handling
            response = requests.get(TEMPLATE_URL, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
        except requests.exceptions.SSLError:
            console.print("[red]❌ SSL Certificate Error[/red]")
            console.print("[dim]Try running: /Applications/Python*/Install\\ Certificates.command[/dim]")
            console.print("[dim]Or: pip install certifi[/dim]")
            raise typer.Exit(1)
        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ Failed to download template: {e}[/red]")
            console.print("[dim]Check your internet connection.[/dim]")
            raise typer.Exit(1)
        
        # Extract
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            console.print("[red]❌ Downloaded file is not a valid zip![/red]")
            raise typer.Exit(1)
        
        # Find template directory (lich-main/template)
        extracted_dir = os.path.join(temp_dir, f"lich-{GITHUB_BRANCH}", "template")
        
        if not os.path.exists(extracted_dir):
            console.print("[red]❌ Template not found in downloaded archive![/red]")
            raise typer.Exit(1)
        
        return extracted_dir


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
