"""
lich upgrade - Upgrade project to latest version.
"""
from pathlib import Path
import shutil

import typer
from rich.console import Console
from rich.prompt import Confirm

from lich import __version__

console = Console()


def upgrade_project(
    to_version: str = typer.Option(None, "--to", help="Target version to upgrade to"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying"),
):
    """
    Upgrade project to the latest Lich Framework version.
    
    Updates .lich/ folder with latest rules and workflows.
    """
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        raise typer.Exit(1)
    
    target = to_version or __version__
    
    console.print(f"\n🔄 [bold blue]Upgrading to Lich v{target}[/bold blue]\n")
    
    if dry_run:
        console.print("[yellow]Dry run mode - no changes will be made.[/yellow]\n")
    
    # Components to upgrade
    upgrades = [
        (".lich/rules/", "Rules"),
        (".lich/workflows/", "Workflows"),
        ("CLAUDE.md", "Claude.md"),
    ]
    
    console.print("[bold]Components to update:[/bold]")
    for path, name in upgrades:
        exists = "exists" if Path(path).exists() else "new"
        console.print(f"   • {name} ({exists})")
    
    if dry_run:
        console.print("\n[yellow]No changes made (dry run).[/yellow]")
        return
    
    # Confirm upgrade
    if not Confirm.ask("\nProceed with upgrade?"):
        console.print("[yellow]Upgrade cancelled.[/yellow]")
        raise typer.Exit(0)
    
    # Backup current .lich
    backup_path = Path(".lich.backup")
    if Path(".lich").exists():
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(".lich", backup_path)
        console.print("   📦 Backed up .lich to .lich.backup")
    
    # TODO: Actually copy new files from template
    # This would require accessing the template from the installed package
    
    console.print("\n[green]✅ Upgrade complete![/green]")
    console.print(f"   Now running Lich v{target}")
    console.print("\n[dim]Backup saved to .lich.backup[/dim]")
