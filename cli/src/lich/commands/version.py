"""
lich version / lich check - Version and project validation.
"""
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

from lich import __version__

console = Console()

# Path to CHANGELOG.md (relative to package)
CHANGELOG_PATH = Path(__file__).parent.parent.parent.parent.parent / "CHANGELOG.md"


def show_version(
    history: bool = typer.Option(False, "--history", "-H", help="Show version history"),
):
    """
    Show Lich Toolkit version and available versions.
    """
    console.print("\n🧙 [bold blue]Lich Toolkit[/bold blue]")
    console.print(f"\n[bold]Current Version:[/bold] v{__version__}")
    
    # Show project version if in a project
    if Path(".lich/PROJECT_CONFIG.yaml").exists():
        try:
            with open(".lich/PROJECT_CONFIG.yaml") as f:
                config = yaml.safe_load(f)
            project_name = config.get("project", {}).get("name", "Unknown")
            console.print(f"[dim]📁 In project: {project_name}[/dim]")
        except Exception:
            pass
    
    # Show changelog/history
    if history:
        console.print("\n" + "─" * 50)
        _show_changelog()
    else:
        console.print("\n[bold]Available Versions:[/bold]")
        _show_available_versions()
        console.print("\n[dim]Run 'lich version --history' for detailed changelog[/dim]")


def _show_available_versions():
    """Show table of available versions."""
    # Read CHANGELOG to extract versions
    versions = _parse_changelog()
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Version", style="green")
    table.add_column("Date")
    table.add_column("Highlights")
    
    for ver in versions:
        table.add_row(ver["version"], ver["date"], ver["highlights"])
    
    console.print(table)


def _show_changelog():
    """Show full changelog."""
    if CHANGELOG_PATH.exists():
        with open(CHANGELOG_PATH) as f:
            content = f.read()
        md = Markdown(content)
        console.print(md)
    else:
        console.print("[yellow]CHANGELOG.md not found[/yellow]")


def _parse_changelog() -> list:
    """Parse CHANGELOG.md for version info."""
    versions = []
    
    if not CHANGELOG_PATH.exists():
        return [{"version": __version__, "date": "current", "highlights": "Current version"}]
    
    try:
        with open(CHANGELOG_PATH) as f:
            content = f.read()
        
        import re
        # Match ## [X.X.X] - YYYY-MM-DD
        pattern = r'## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})'
        matches = re.findall(pattern, content)
        
        # Get first "Added" item for each version
        sections = content.split("## [")
        for i, match in enumerate(matches):
            version, date = match
            highlights = "See changelog"
            
            # Try to find first added item
            if i + 1 < len(sections):
                section = sections[i + 1]
                added_match = re.search(r'### Added\n- (.+)', section)
                if added_match:
                    highlights = added_match.group(1)[:40] + "..."
            
            versions.append({
                "version": version,
                "date": date,
                "highlights": highlights
            })
    except Exception:
        versions = [{"version": __version__, "date": "current", "highlights": "Current version"}]
    
    return versions


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
