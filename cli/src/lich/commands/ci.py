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


from lich.commands.common import (
    ensure_lich_project as _check_lich_project,
    run_command_ok as _run_command,
)


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


# ---------------------------------------------------------------------------
# ci_setup helpers
# ---------------------------------------------------------------------------

def _detect_system() -> tuple:
    """Step 1: detect and print OS/arch. Returns (os_name, is_arm, os_display, arch_display)."""
    import platform
    os_name = platform.system()
    machine = platform.machine().lower()
    is_arm = machine in ("arm64", "aarch64")
    is_intel = machine in ("x86_64", "amd64", "i386", "i686")
    os_display = {"Darwin": "macOS", "Linux": "Linux", "Windows": "Windows"}.get(os_name, os_name)
    arch_display = "ARM (Apple Silicon)" if is_arm else "Intel/AMD (x86_64)" if is_intel else machine
    console.print(f"  📍 OS: [bold]{os_display}[/bold]")
    console.print(f"  🔧 Architecture: [bold]{arch_display}[/bold]")
    return os_name, is_arm, os_display, arch_display


def _ensure_docker_and_act() -> None:
    """Steps 2-3: verify Docker is running and act is installed (offer install)."""
    console.print("\n[bold]Step 2: Checking Docker...[/bold]")
    if not check_docker_running():
        show_docker_not_running_error()
        raise typer.Exit(1)
    console.print("[green]✓ Docker is running[/green]")

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


def _create_actrc(os_name: str, is_arm: bool) -> Path:
    """Step 4: write .actrc (if missing/confirmed overwrite) and return its path."""
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
    return actrc_path


def _create_secrets_file() -> None:
    """Step 5: write .secrets template, add gitignore entries, and print notice."""
    secrets_content = '''# CI Secrets - DO NOT COMMIT THIS FILE!
# Add your secrets here in KEY="value" format

# GitHub Token (required for private repos and API calls)
# Get yours at: https://github.com/settings/tokens
GITHUB_TOKEN="ghp_your_token_here"

# Add more secrets as needed:
# DATABASE_URL="postgresql://..."
# API_KEY="..."
'''
    console.print("\n[bold]Step 5: Creating .secrets file...[/bold]")
    secrets_path = Path.cwd() / ".secrets"
    _write_file_if_not_exists(secrets_path, secrets_content, ".secrets")

    # Add .secrets to .gitignore
    _add_to_gitignore([".secrets", ".ci-env"])

    # Show important notice about GitHub repo secrets
    console.print("\n  [yellow]⚠️ IMPORTANT:[/yellow]")
    console.print("  [dim]Secrets need to be set in TWO places:[/dim]")
    console.print("  [dim]1. Local: Edit .secrets file with your values[/dim]")
    console.print("  [dim]2. GitHub: Repo → Settings → Secrets → Actions → New secret[/dim]")


def _maybe_create_optional_file(
    actrc_path: Path,
    step_title: str,
    description_lines: list,
    prompt: str,
    filename: str,
    content: str,
    actrc_flag: str,
) -> bool:
    """Steps 6-7 shared: optionally create a config file and register it in .actrc."""
    console.print(f"\n[bold]{step_title}[/bold]")
    for line in description_lines:
        console.print(f"  [dim]{line}[/dim]")
    if not typer.confirm(prompt, default=False):
        return False
    path = Path.cwd() / filename
    _write_file_if_not_exists(path, content, filename)
    with open(actrc_path, "a") as f:
        f.write(f"{actrc_flag}={filename}\n")
    console.print(f"  [green]✓ Added {actrc_flag}={filename} to .actrc[/green]")
    return True


def _print_ci_setup_summary(
    os_display: str, arch_display: str, os_name: str,
    is_arm: bool, create_vars: bool, create_env: bool,
) -> None:
    """Print the final setup-complete summary panel."""
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
    console.print(Panel.fit("🛠️ Setting up act for Local CI", style="bold blue"))

    console.print("\n[bold]Step 1: Detecting System...[/bold]")
    os_name, is_arm, os_display, arch_display = _detect_system()

    _ensure_docker_and_act()
    actrc_path = _create_actrc(os_name, is_arm)
    _create_secrets_file()

    create_vars = _maybe_create_optional_file(
        actrc_path,
        "Step 6: CI Variables (optional)...",
        [
            "Variables are for non-sensitive configuration:",
            "  • API_URL, APP_NAME, NODE_ENV",
            "  • These CAN be committed to git",
        ],
        "Create .ci-vars file?",
        ".ci-vars",
        '''# CI Variables - Safe to commit
# Non-sensitive configuration for CI

NODE_ENV=test
APP_NAME=myapp
# API_URL=https://api.example.com
''',
        "--var-file",
    )
    create_env = _maybe_create_optional_file(
        actrc_path,
        "Step 7: CI Environment (optional)...",
        [
            "Environment file for container environment variables:",
            "  • DEBUG=true, LOG_LEVEL=info",
            "  • May contain sensitive values - added to .gitignore",
        ],
        "Create .ci-env file?",
        ".ci-env",
        '''# CI Environment Variables
# These are passed to the container

DEBUG=false
LOG_LEVEL=info
# DATABASE_URL=postgresql://localhost/test
''',
        "--env-file",
    )

    _print_ci_setup_summary(os_display, arch_display, os_name, is_arm, create_vars, create_env)


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


def _add_to_gitignore(files: list) -> None:
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


# ---------------------------------------------------------------------------
# Shared runner for the three nearly-identical frontend app CI commands
# ---------------------------------------------------------------------------

def _run_app_ci(
    app_name: str,
    workflow: str,
    job: str,
    display: str,
    local: bool,
    verbose: bool,
    quiet: bool,
    insecure_secrets: bool,
    secret: Optional[list],
    var: Optional[list],
) -> None:
    """Shared CI runner for web, admin, and landing frontend apps."""
    _check_lich_project()
    if local:
        console.print(Panel.fit(f"🔄 {display} CI (Local)", style="bold blue"))
        if not run_frontend_ci(app_name):
            raise typer.Exit(1)
    else:
        console.print(Panel.fit(f"🐳 {display} CI (Docker/act)", style="bold blue"))
        if not ensure_act_ready():
            raise typer.Exit(1)
        if not run_act_workflow(
            workflow, job=job, verbose=verbose, quiet=quiet,
            insecure_secrets=insecure_secrets, secrets=secret, vars=var,
        ):
            raise typer.Exit(1)
    console.print(f"\n[green]✓ {display} CI passed![/green]")


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
    _run_app_ci("web", "ci-web.yml", "web-test", "Web App", local, verbose, quiet, insecure_secrets, secret, var)


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
    _run_app_ci("admin", "ci-admin.yml", "admin-test", "Admin Panel", local, verbose, quiet, insecure_secrets, secret, var)


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
    _run_app_ci("landing", "ci-landing.yml", "landing-test", "Landing Page", local, verbose, quiet, insecure_secrets, secret, var)
