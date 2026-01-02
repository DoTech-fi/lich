"""
Lich CLI - Main Typer application.
"""
import typer
from rich.console import Console

from lich import __version__
from lich.commands import init, dev, version, upgrade, adopt
from lich.commands.migration import migration_app

# Create main Typer app
app = typer.Typer(
    name="lich",
    help="🧙 Lich Framework - AI-Ready Full-Stack Project Generator",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()

# Register commands
app.command(name="init", help="Create a new Lich project")(init.init_project)
app.command(name="adopt", help="Adopt an existing Python project")(adopt.adopt_project)
app.command(name="dev", help="Start development environment")(dev.start_dev)
app.command(name="stop", help="Stop development environment")(dev.stop_dev)
app.command(name="version", help="Show Lich version")(version.show_version)
app.command(name="check", help="Validate project structure")(version.check_project)
app.command(name="upgrade", help="Upgrade project to latest version")(upgrade.upgrade_project)

# Register sub-apps
app.add_typer(migration_app, name="migration")


@app.callback()
def main():
    """
    🧙 Lich Framework - AI-Ready Full-Stack Project Generator
    
    Create production-ready full-stack projects with a single command.
    """
    pass


if __name__ == "__main__":
    app()
