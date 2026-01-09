"""
lich ci - Run CI checks locally before pushing.

Usage:
    lich ci                 # Run all checks
    lich ci --act           # Run all checks using act (Docker)
    lich ci backend         # Backend only
    lich ci backend --act   # Backend only using act
    lich ci web             # Web app only
    lich ci admin           # Admin panel only
    lich ci landing         # Landing page only
    lich ci setup           # Setup act for local CI
"""
import subprocess
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.panel import Panel

from lich.commands.ci_utils import (
    check_docker_running,
    check_act_installed,
    show_docker_not_running_error,
    show_act_not_installed_error,
    install_act,
    run_act_workflow,
    ensure_act_ready,
)

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


@ci_app.command(name="setup")
def ci_setup():
    """
    🛠️ Setup act for local CI.
    
    Detects your system, configures act, and creates necessary config files:
    - .actrc (act configuration)
    - .secrets (GitHub token and other secrets)
    - .ci-vars (optional: CI variables)
    - .ci-env (optional: CI environment)
    
    Examples:
        lich ci setup
    """
    import platform
    from pathlib import Path
    
    console.print(Panel.fit("🛠️ Setting up act for Local CI", style="bold blue"))
    
    # Step 1: Detect OS and Architecture
    console.print("\n[bold]Step 1: Detecting System...[/bold]")
    os_name = platform.system()
    machine = platform.machine().lower()
    
    is_arm = machine in ("arm64", "aarch64")
    is_intel = machine in ("x86_64", "amd64", "i386", "i686")
    
    os_display = {"Darwin": "macOS", "Linux": "Linux", "Windows": "Windows"}.get(os_name, os_name)
    arch_display = "ARM (Apple Silicon)" if is_arm else "Intel/AMD (x86_64)" if is_intel else machine
    
    console.print(f"  📍 OS: [bold]{os_display}[/bold]")
    console.print(f"  🔧 Architecture: [bold]{arch_display}[/bold]")
    
    # Step 2: Check Docker
    console.print("\n[bold]Step 2: Checking Docker...[/bold]")
    if not check_docker_running():
        show_docker_not_running_error()
        raise typer.Exit(1)
    console.print("[green]✓ Docker is running[/green]")
    
    # Step 3: Check act
    console.print("\n[bold]Step 3: Checking act...[/bold]")
    if not check_act_installed():
        console.print("[yellow]act is not installed[/yellow]")
        install_now = typer.confirm("Would you like to install act now?", default=True)
        if install_now:
            if not install_act():
                raise typer.Exit(1)
        else:
            show_act_not_installed_error()
            raise typer.Exit(1)
    else:
        console.print("[green]✓ act is installed[/green]")
    
    # Step 4: Create .actrc config file
    console.print("\n[bold]Step 4: Creating .actrc config...[/bold]")
    
    actrc_lines = []
    if os_name == "Darwin" and is_arm:
        actrc_lines.append("--container-architecture=linux/amd64")
        console.print("  📦 ARM Mac detected → using linux/amd64 containers")
    
    actrc_lines.append("--reuse")
    actrc_lines.append("--secret-file=.secrets")
    console.print("  ♻️  Container reuse enabled")
    console.print("  🔐 Secrets file: .secrets")
    
    actrc_path = Path.cwd() / ".actrc"
    _write_file_if_not_exists(actrc_path, "\n".join(actrc_lines) + "\n", ".actrc")
    
    # Step 5: Create .secrets file
    console.print("\n[bold]Step 5: Creating .secrets file...[/bold]")
    
    secrets_content = '''# CI Secrets - DO NOT COMMIT THIS FILE!
# Add your secrets here in KEY="value" format

# GitHub Token (required for private repos and API calls)
# Get yours at: https://github.com/settings/tokens
GITHUB_TOKEN="ghp_your_token_here"

# Add more secrets as needed:
# DATABASE_URL="postgresql://..."
# API_KEY="..."
'''
    
    secrets_path = Path.cwd() / ".secrets"
    _write_file_if_not_exists(secrets_path, secrets_content, ".secrets")
    
    # Add .secrets to .gitignore
    _add_to_gitignore([".secrets", ".ci-env"])
    
    # Show important notice about GitHub repo secrets
    console.print("\n  [yellow]⚠️ IMPORTANT:[/yellow]")
    console.print("  [dim]Secrets need to be set in TWO places:[/dim]")
    console.print("  [dim]1. Local: Edit .secrets file with your values[/dim]")
    console.print("  [dim]2. GitHub: Repo → Settings → Secrets → Actions → New secret[/dim]")
    
    # Step 6: Optional .ci-vars file
    console.print("\n[bold]Step 6: CI Variables (optional)...[/bold]")
    console.print("  [dim]Variables are for non-sensitive configuration:[/dim]")
    console.print("  [dim]  • API_URL, APP_NAME, NODE_ENV[/dim]")
    console.print("  [dim]  • These CAN be committed to git[/dim]")
    
    create_vars = typer.confirm("Create .ci-vars file?", default=False)
    if create_vars:
        vars_content = '''# CI Variables - Safe to commit
# Non-sensitive configuration for CI

NODE_ENV=test
APP_NAME=myapp
# API_URL=https://api.example.com
'''
        vars_path = Path.cwd() / ".ci-vars"
        _write_file_if_not_exists(vars_path, vars_content, ".ci-vars")
        
        # Add --var-file to .actrc
        with open(actrc_path, "a") as f:
            f.write("--var-file=.ci-vars\n")
        console.print("  [green]✓ Added --var-file=.ci-vars to .actrc[/green]")
    
    # Step 7: Optional .ci-env file
    console.print("\n[bold]Step 7: CI Environment (optional)...[/bold]")
    console.print("  [dim]Environment file for container environment variables:[/dim]")
    console.print("  [dim]  • DEBUG=true, LOG_LEVEL=info[/dim]")
    console.print("  [dim]  • May contain sensitive values - added to .gitignore[/dim]")
    
    create_env = typer.confirm("Create .ci-env file?", default=False)
    if create_env:
        env_content = '''# CI Environment Variables
# These are passed to the container

DEBUG=false
LOG_LEVEL=info
# DATABASE_URL=postgresql://localhost/test
'''
        env_path = Path.cwd() / ".ci-env"
        _write_file_if_not_exists(env_path, env_content, ".ci-env")
        
        # Add --env-file to .actrc
        with open(actrc_path, "a") as f:
            f.write("--env-file=.ci-env\n")
        console.print("  [green]✓ Added --env-file=.ci-env to .actrc[/green]")
    
    # Summary
    console.print("\n")
    
    summary_lines = [
        "[green]✓ act is ready![/green]",
        "",
        f"System: {os_display} ({arch_display})",
    ]
    
    if os_name == "Darwin" and is_arm:
        summary_lines.append("Container arch: linux/amd64 (ARM emulation)")
    
    summary_lines.extend([
        "",
        "Files created:",
        "  .actrc     - act configuration",
        "  .secrets   - your secrets (edit this!)",
    ])
    
    if create_vars:
        summary_lines.append("  .ci-vars   - CI variables")
    if create_env:
        summary_lines.append("  .ci-env    - CI environment")
    
    summary_lines.extend([
        "",
        "Next steps:",
        "  1. Edit .secrets with your GITHUB_TOKEN",
        "  2. Run: lich ci -a",
    ])
    
    console.print(Panel.fit(
        "\n".join(summary_lines),
        title="Setup Complete",
        border_style="green",
    ))


def _write_file_if_not_exists(path: Path, content: str, name: str) -> bool:
    """Write file if it doesn't exist, return True if created."""
    if path.exists():
        console.print(f"  [yellow]⚠️ {name} already exists[/yellow]")
        update = typer.confirm(f"Overwrite {name}?", default=False)
        if update:
            with open(path, "w") as f:
                f.write(content)
            console.print(f"  [green]✓ Updated {name}[/green]")
            return True
        return False
    else:
        with open(path, "w") as f:
            f.write(content)
        console.print(f"  [green]✓ Created {name}[/green]")
        return True


def _add_to_gitignore(files: list):
    """Add files to .gitignore if not already present."""
    gitignore_path = Path.cwd() / ".gitignore"
    
    existing = set()
    if gitignore_path.exists():
        with open(gitignore_path) as f:
            existing = set(line.strip() for line in f if line.strip() and not line.startswith("#"))
    
    to_add = [f for f in files if f not in existing]
    
    if to_add:
        with open(gitignore_path, "a") as f:
            f.write("\n# CI Secrets (added by lich ci setup)\n")
            for file in to_add:
                f.write(f"{file}\n")
        console.print(f"  [green]✓ Added {', '.join(to_add)} to .gitignore[/green]")


@ci_app.command(name="backend")
def ci_backend(
    local: bool = typer.Option(False, "--local", "-l", help="Run locally (without Docker)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode"),
    insecure_secrets: bool = typer.Option(False, "--insecure-secrets", help="Show secrets in logs"),
    secret: Optional[list[str]] = typer.Option(None, "--secret", "-s", help="Secret KEY=VALUE (repeatable)"),
    var: Optional[list[str]] = typer.Option(None, "--var", help="Variable KEY=VALUE (repeatable)"),
):
    """Run CI for backend only."""
    _check_lich_project()
    
    if local:
        console.print(Panel.fit("🔄 Backend CI (Local)", style="bold blue"))
        if not run_backend_ci():
            raise typer.Exit(1)
    else:
        console.print(Panel.fit("🐳 Backend CI (Docker/act)", style="bold blue"))
        if not ensure_act_ready():
            raise typer.Exit(1)
        if not run_act_workflow("ci-backend.yml", job="backend-test", verbose=verbose, quiet=quiet, insecure_secrets=insecure_secrets, secrets=secret, vars=var):
            raise typer.Exit(1)
    
    console.print("\n[green]✓ Backend CI passed![/green]")


@ci_app.command(name="web")
def ci_web(
    local: bool = typer.Option(False, "--local", "-l", help="Run locally (without Docker)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode"),
    insecure_secrets: bool = typer.Option(False, "--insecure-secrets", help="Show secrets in logs"),
    secret: Optional[list[str]] = typer.Option(None, "--secret", "-s", help="Secret KEY=VALUE (repeatable)"),
    var: Optional[list[str]] = typer.Option(None, "--var", help="Variable KEY=VALUE (repeatable)"),
):
    """Run CI for web app only."""
    _check_lich_project()
    
    if local:
        console.print(Panel.fit("🔄 Web App CI (Local)", style="bold blue"))
        if not run_frontend_ci("web"):
            raise typer.Exit(1)
    else:
        console.print(Panel.fit("🐳 Web App CI (Docker/act)", style="bold blue"))
        if not ensure_act_ready():
            raise typer.Exit(1)
        if not run_act_workflow("ci-web.yml", job="web-test", verbose=verbose, quiet=quiet, insecure_secrets=insecure_secrets, secrets=secret, vars=var):
            raise typer.Exit(1)
    
    console.print("\n[green]✓ Web CI passed![/green]")


@ci_app.command(name="admin")
def ci_admin(
    local: bool = typer.Option(False, "--local", "-l", help="Run locally (without Docker)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode"),
    insecure_secrets: bool = typer.Option(False, "--insecure-secrets", help="Show secrets in logs"),
    secret: Optional[list[str]] = typer.Option(None, "--secret", "-s", help="Secret KEY=VALUE (repeatable)"),
    var: Optional[list[str]] = typer.Option(None, "--var", help="Variable KEY=VALUE (repeatable)"),
):
    """Run CI for admin panel only."""
    _check_lich_project()
    
    if local:
        console.print(Panel.fit("🔄 Admin Panel CI (Local)", style="bold blue"))
        if not run_frontend_ci("admin"):
            raise typer.Exit(1)
    else:
        console.print(Panel.fit("🐳 Admin Panel CI (Docker/act)", style="bold blue"))
        if not ensure_act_ready():
            raise typer.Exit(1)
        if not run_act_workflow("ci-admin.yml", job="admin-test", verbose=verbose, quiet=quiet, insecure_secrets=insecure_secrets, secrets=secret, vars=var):
            raise typer.Exit(1)
    
    console.print("\n[green]✓ Admin CI passed![/green]")


@ci_app.command(name="landing")
def ci_landing(
    local: bool = typer.Option(False, "--local", "-l", help="Run locally (without Docker)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode"),
    insecure_secrets: bool = typer.Option(False, "--insecure-secrets", help="Show secrets in logs"),
    secret: Optional[list[str]] = typer.Option(None, "--secret", "-s", help="Secret KEY=VALUE (repeatable)"),
    var: Optional[list[str]] = typer.Option(None, "--var", help="Variable KEY=VALUE (repeatable)"),
):
    """Run CI for landing page only."""
    _check_lich_project()
    
    if local:
        console.print(Panel.fit("🔄 Landing Page CI (Local)", style="bold blue"))
        if not run_frontend_ci("landing"):
            raise typer.Exit(1)
    else:
        console.print(Panel.fit("🐳 Landing Page CI (Docker/act)", style="bold blue"))
        if not ensure_act_ready():
            raise typer.Exit(1)
        if not run_act_workflow("ci-landing.yml", job="landing-test", verbose=verbose, quiet=quiet, insecure_secrets=insecure_secrets, secrets=secret, vars=var):
            raise typer.Exit(1)
    
    console.print("\n[green]✓ Landing CI passed![/green]")

