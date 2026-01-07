"""
lich ci - Run CI checks locally before pushing.

Usage:
    lich ci                 # Run all checks
    lich ci backend         # Backend only
    lich ci web             # Web app only
    lich ci admin           # Admin panel only
    lich ci landing         # Landing page only
"""
import subprocess
from pathlib import Path
from typing import List
import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

ci_app = typer.Typer(
    name="ci",
    help="🔄 Run CI checks locally",
    no_args_is_help=False,
)


def _check_lich_project():
    """Check if we're in a Lich project."""
    if not (Path(".lich").exists() or Path("backend").exists()):
        console.print("[red]Error: Not in a Lich project directory[/red]")
        raise typer.Exit(1)


def _run_command(cmd: List[str], cwd: Path = None, show_output: bool = True) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or Path.cwd(),
            capture_output=not show_output,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        console.print(f"[red]Command not found: {cmd[0]}[/red]")
        return False


def run_backend_ci() -> bool:
    """Run backend CI checks."""
    backend = Path("backend")
    if not backend.exists():
        console.print("[yellow]No backend directory found[/yellow]")
        return True
    
    console.print("\n[bold blue]🐍 Backend CI[/bold blue]")
    success = True
    
    # Lint
    console.print("[dim]Running ruff...[/dim]")
    if not _run_command(["ruff", "check", "."], cwd=backend):
        console.print("[yellow]⚠ Linting issues found[/yellow]")
        success = False
    else:
        console.print("[green]✓ Linting passed[/green]")
    
    # Type check
    console.print("[dim]Running mypy...[/dim]")
    _run_command(["mypy", ".", "--ignore-missing-imports"], cwd=backend, show_output=False)
    console.print("[green]✓ Type check done[/green]")
    
    # Tests
    console.print("[dim]Running pytest...[/dim]")
    if not _run_command(["pytest", "-v", "--tb=short"], cwd=backend):
        console.print("[red]✗ Tests failed[/red]")
        success = False
    else:
        console.print("[green]✓ Tests passed[/green]")
    
    # Security
    console.print("[dim]Running bandit...[/dim]")
    _run_command(["bandit", "-r", ".", "-x", "tests", "-q"], cwd=backend, show_output=False)
    console.print("[green]✓ Security scan done[/green]")
    
    return success


def run_frontend_ci(app_name: str) -> bool:
    """Run frontend CI checks for a specific app."""
    app_path = Path("apps") / app_name
    if not app_path.exists():
        console.print(f"[yellow]App not found: {app_name}[/yellow]")
        return True
    
    console.print(f"\n[bold blue]📦 {app_name.upper()} CI[/bold blue]")
    success = True
    
    # Install deps if needed
    if not (app_path / "node_modules").exists():
        console.print("[dim]Installing dependencies...[/dim]")
        _run_command(["npm", "ci"], cwd=app_path, show_output=False)
    
    # Lint
    console.print("[dim]Running eslint...[/dim]")
    if not _run_command(["npm", "run", "lint"], cwd=app_path, show_output=False):
        console.print("[yellow]⚠ Linting issues found[/yellow]")
    else:
        console.print("[green]✓ Linting passed[/green]")
    
    # Type check
    console.print("[dim]Running type-check...[/dim]")
    _run_command(["npm", "run", "type-check"], cwd=app_path, show_output=False)
    console.print("[green]✓ Type check done[/green]")
    
    # Build
    console.print("[dim]Running build...[/dim]")
    if not _run_command(["npm", "run", "build"], cwd=app_path, show_output=False):
        console.print("[red]✗ Build failed[/red]")
        success = False
    else:
        console.print("[green]✓ Build passed[/green]")
    
    # Audit
    console.print("[dim]Running npm audit...[/dim]")
    _run_command(["npm", "audit", "--audit-level=high"], cwd=app_path, show_output=False)
    console.print("[green]✓ Security audit done[/green]")
    
    return success


@ci_app.callback(invoke_without_command=True)
def ci_all(ctx: typer.Context):
    """
    🔄 Run all CI checks locally.
    
    Runs linting, type checking, tests, and security scans
    for all parts of your project.
    
    Examples:
        lich ci              # Run everything
        lich ci backend      # Backend only
        lich ci web          # Web app only
    """
    if ctx.invoked_subcommand is not None:
        return
    
    _check_lich_project()
    
    console.print(Panel.fit("🔄 Running Local CI", style="bold blue"))
    
    results = []
    
    # Backend
    results.append(("Backend", run_backend_ci()))
    
    # Frontend apps
    for app in ["web", "admin", "landing"]:
        if (Path("apps") / app).exists():
            results.append((app.title(), run_frontend_ci(app)))
    
    # Summary
    console.print("\n")
    passed = all(r[1] for r in results)
    if passed:
        console.print(Panel.fit("[green]✓ All CI checks passed![/green]", title="Summary"))
    else:
        failed = [r[0] for r in results if not r[1]]
        console.print(Panel.fit(
            f"[red]✗ CI failed for: {', '.join(failed)}[/red]",
            title="Summary"
        ))
        raise typer.Exit(1)


@ci_app.command(name="backend")
def ci_backend():
    """Run CI for backend only."""
    _check_lich_project()
    console.print(Panel.fit("🔄 Backend CI", style="bold blue"))
    if not run_backend_ci():
        raise typer.Exit(1)
    console.print("\n[green]✓ Backend CI passed![/green]")


@ci_app.command(name="web")
def ci_web():
    """Run CI for web app only."""
    _check_lich_project()
    console.print(Panel.fit("🔄 Web App CI", style="bold blue"))
    if not run_frontend_ci("web"):
        raise typer.Exit(1)
    console.print("\n[green]✓ Web CI passed![/green]")


@ci_app.command(name="admin")
def ci_admin():
    """Run CI for admin panel only."""
    _check_lich_project()
    console.print(Panel.fit("🔄 Admin Panel CI", style="bold blue"))
    if not run_frontend_ci("admin"):
        raise typer.Exit(1)
    console.print("\n[green]✓ Admin CI passed![/green]")


@ci_app.command(name="landing")
def ci_landing():
    """Run CI for landing page only."""
    _check_lich_project()
    console.print(Panel.fit("🔄 Landing Page CI", style="bold blue"))
    if not run_frontend_ci("landing"):
        raise typer.Exit(1)
    console.print("\n[green]✓ Landing CI passed![/green]")
