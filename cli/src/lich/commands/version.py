"""
lich version / lich check - Version and project validation.
"""
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.table import Table

from lich import __version__

console = Console()


def show_version():
    """
    Show Lich Framework version.
    """
    console.print(f"\n🧙 [bold blue]Lich Framework[/bold blue] v{__version__}\n")
    
    # Also show project version if in a project
    if Path(".lich/PROJECT_CONFIG.yaml").exists():
        try:
            with open(".lich/PROJECT_CONFIG.yaml") as f:
                config = yaml.safe_load(f)
            project_name = config.get("project", {}).get("name", "Unknown")
            console.print(f"📁 Current project: [green]{project_name}[/green]")
        except Exception:
            pass


def check_project():
    """
    Validate the current Lich project structure.
    
    Checks for required files and directories.
    """
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        console.print("   .lich folder not found.")
        raise typer.Exit(1)
    
    console.print("\n🔍 [bold blue]Checking project structure...[/bold blue]\n")
    
    # Required files/directories
    checks = [
        (".lich/AI_CONTEXT.md", "AI Context"),
        (".lich/PROJECT_CONFIG.yaml", "Project Config"),
        (".lich/rules/", "Rules folder"),
        (".lich/workflows/", "Workflows folder"),
        ("CLAUDE.md", "Claude.md"),
        ("docker-compose.yml", "Docker Compose"),
        ("backend/", "Backend folder"),
        ("apps/web/", "Web App"),
        ("apps/admin/", "Admin Panel"),
        ("apps/landing/", "Landing Page"),
    ]
    
    table = Table(title="Project Structure Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    all_ok = True
    for path, name in checks:
        exists = Path(path).exists()
        status = "✅ OK" if exists else "❌ Missing"
        if not exists:
            all_ok = False
        table.add_row(name, status)
    
    console.print(table)
    
    if all_ok:
        console.print("\n[green]✅ Project structure is valid![/green]")
    else:
        console.print("\n[yellow]⚠️ Some components are missing.[/yellow]")
        raise typer.Exit(1)
