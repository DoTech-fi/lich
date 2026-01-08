"""
Lich CLI - Main Typer application.
"""
import typer
from rich.console import Console
from lich import __version__
from lich.commands import init, dev, version, upgrade, adopt, shell, routes, test, seed, git
from lich.commands.migration import migration_app
from lich.commands.make import make_app
from lich.commands.middleware import middleware_app
from lich.commands.security import security_app
from lich.commands.lint import lint_app
from lich.commands.deploy import deploy_app
from lich.commands.backup import backup_app
from lich.commands.secret import secret_app
from lich.commands.production_ready import production_ready_app
from lich.commands.ci import ci_app
from lich.commands.setup import setup_app
from lich.version_check import check_compatibility
from lich.mcp import server as mcp_server


def _version_callback(value: bool):
    """Print version and exit."""
    if value:
        print(f"lich {__version__}")
        raise typer.Exit()


# Create main Typer app
app = typer.Typer(
    name="lich",
    help="🧙 Lich Toolkit - AI-Ready Full-Stack Project Generator",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()

# Register commands
app.command(name="init", help="Create a new Lich project")(init.init_project)
app.command(name="adopt", help="Adopt an existing Python project")(adopt.adopt_project)
app.command(name="start", help="Start development environment")(dev.start_dev)
app.command(name="stop", help="Stop development environment")(dev.stop_dev)
app.command(name="version", help="Show Lich version")(version.show_version)
app.command(name="check", help="Validate project structure")(version.check_project)
app.command(name="upgrade", help="Upgrade project to latest version")(upgrade.upgrade_project)
app.command(name="shell", help="Interactive Python shell")(shell.shell_command)
app.command(name="routes", help="List all API routes")(routes.routes_command)
app.command(name="test", help="Run project tests")(test.test_command)
app.command(name="seed", help="Seed database with test data")(seed.seed_command)
app.command(name="commit", help="Create a Semantic Commit")(git.git_commit)
app.command(name="tag", help="Create a Version Tag")(git.git_tag)
app.command(name="push", help="Push changes to remote")(git.git_push)

# Register MCP Server
app.command(name="serve", help="Start Lich MCP Server")(mcp_server.start_server)

# Register sub-apps
app.add_typer(migration_app, name="migration")
app.add_typer(make_app, name="make")
app.add_typer(middleware_app, name="middleware")
app.add_typer(security_app, name="security")
app.add_typer(lint_app, name="lint")
app.add_typer(deploy_app, name="deploy")
app.add_typer(backup_app, name="backup")
app.add_typer(secret_app, name="secret")
app.add_typer(production_ready_app, name="production-ready")
app.add_typer(ci_app, name="ci")
app.add_typer(setup_app, name="setup")


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    🧙 Lich Toolkit - AI-Ready Full-Stack Project Generator
    
    Create production-ready full-stack projects with a single command.
    """
    check_compatibility()


if __name__ == "__main__":
    app()
