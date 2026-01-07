from pathlib import Path
from packaging import version
from rich.console import Console
from rich.panel import Panel

from lich import __version__ as cli_version_str

console = Console()

def check_compatibility():
    """
    Check if the current project is compatible with the installed CLI version.
    Run this at the start of CLI commands.
    """
    # Only check if we are in a Lich project
    if not Path(".lich").exists():
        return

    version_file = Path(".lich/lich.version")
    
    if not version_file.exists():
        # Case: Legacy Project (pre-v1.6.0)
        # We don't want to nag too much, but we should warn on first usage or critical commands.
        # For now, just a subtle warning.
        message = (
            f"[yellow]⚠️  Unknown Project Version[/yellow]\n"
            f"This project doesn't have a version file (likely created with Lich < v1.6.0).\n"
            f"Current CLI is [bold]v{cli_version_str}[/bold].\n\n"
            f"👉 Recommended: Run [bold cyan]lich upgrade[/bold cyan] to sync latest configurations."
        )
        console.print(Panel(message, title="Compatibility Check", border_style="yellow", expand=False))
        return

    try:
        project_version_str = version_file.read_text().strip()
        cli_ver = version.parse(cli_version_str)
        proj_ver = version.parse(project_version_str)
        
        # Check for Major Version Mismatch (Breaking Changes)
        # e.g. CLI v2.0 vs Project v1.5
        if cli_ver.major > proj_ver.major:
            message = (
                f"[bold red]⛔ MAJOR VERSION MISMATCH[/bold red]\n"
                f"Project: v{project_version_str} | CLI: v{cli_version_str}\n\n"
                f"The installed CLI has breaking changes compatible only with newer projects.\n"
                f"Please run [bold cyan]lich upgrade[/bold cyan] to update your project configuration."
            )
            console.print(Panel(message, title="Critical Compatibility Warning", border_style="red"))
            # We don't exit(1) to allow users to run 'upgrade', but we warn loudly.
            
        # Check if CLI is OLDER than Project (Downgrade risk)
        # e.g. CLI v1.5 vs Project v1.6
        elif cli_ver < proj_ver:
             message = (
                f"[bold yellow]⚠️  OUTDATED CLI[/bold yellow]\n"
                f"Project: v{project_version_str} | CLI: v{cli_version_str}\n\n"
                f"Your CLI is older than this project.\n"
                f"Please run [bold green]pip install --upgrade lich[/bold green]."
            )
             console.print(Panel(message, title="Compatibility Warning", border_style="yellow"))

    except Exception:
        # If parsing fails, ignore.
        pass
