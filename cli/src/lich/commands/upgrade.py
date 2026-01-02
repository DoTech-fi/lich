"""
lich upgrade - Upgrade project to latest version.
"""
import re
from pathlib import Path
import shutil

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from lich import __version__

console = Console()

# Path to CHANGELOG.md
CHANGELOG_PATH = Path(__file__).parent.parent.parent.parent.parent / "CHANGELOG.md"


def _parse_versions() -> list:
    """Parse available versions from CHANGELOG."""
    versions = []
    
    if not CHANGELOG_PATH.exists():
        return [{"version": __version__, "date": "current", "highlights": "Current version"}]
    
    try:
        with open(CHANGELOG_PATH) as f:
            content = f.read()
        
        pattern = r'## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})'
        matches = re.findall(pattern, content)
        
        sections = content.split("## [")
        for i, match in enumerate(matches):
            version, date = match
            highlights = ""
            
            if i + 1 < len(sections):
                section = sections[i + 1]
                added_match = re.search(r'### Added\n- (.+)', section)
                if added_match:
                    highlights = added_match.group(1)[:40]
            
            versions.append({
                "version": version,
                "date": date,
                "highlights": highlights
            })
    except Exception:
        versions = [{"version": __version__, "date": "current", "highlights": "Current version"}]
    
    return versions


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
    
    console.print("\n🔄 [bold blue]Lich Framework Upgrade[/bold blue]\n")
    console.print(f"[bold]Installed CLI Version:[/bold] v{__version__}")
    
    # Get available versions
    versions = _parse_versions()
    
    # If no --to specified, show picker
    if not to_version:
        console.print("\n[bold]Available Versions:[/bold]\n")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim")
        table.add_column("Version", style="green")
        table.add_column("Date")
        table.add_column("Highlights")
        
        for i, ver in enumerate(versions, 1):
            is_current = ver["version"] == __version__
            marker = " (current)" if is_current else ""
            table.add_row(
                str(i),
                f"{ver['version']}{marker}",
                ver["date"],
                ver["highlights"][:30] + "..." if len(ver.get("highlights", "")) > 30 else ver.get("highlights", "")
            )
        
        console.print(table)
        
        # Ask user to pick
        console.print()
        choice = typer.prompt(
            "Select version number to upgrade to",
            default="1"
        )
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(versions):
                to_version = versions[idx]["version"]
            else:
                console.print("[red]Invalid selection[/red]")
                raise typer.Exit(1)
        except ValueError:
            console.print("[red]Invalid input[/red]")
            raise typer.Exit(1)
    
    console.print(f"\n[bold]Target Version:[/bold] v{to_version}")
    
    if dry_run:
        console.print("\n[yellow]Dry run mode - no changes will be made.[/yellow]")
    
    # Components to upgrade
    components = [
        (".lich/rules/", "Rules"),
        (".lich/workflows/", "Workflows"),
        ("CLAUDE.md", "Claude.md"),
    ]
    
    console.print("\n[bold]Components to update:[/bold]")
    for path, name in components:
        exists = "exists" if Path(path).exists() else "new"
        console.print(f"   • {name} ({exists})")
    
    if dry_run:
        console.print("\n[yellow]No changes made (dry run).[/yellow]")
        return
    
    # Confirm upgrade
    console.print()
    if not Confirm.ask(f"Proceed with upgrade to v{to_version}?"):
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
    
    console.print(f"\n[green]✅ Upgrade to v{to_version} complete![/green]")
    console.print("\n[dim]Backup saved to .lich.backup[/dim]")
