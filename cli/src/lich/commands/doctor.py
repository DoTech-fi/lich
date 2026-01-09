"""
lich doctor - Diagnose project health and structure.
"""
import os
from pathlib import Path
from typing import List, Tuple

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def _check_path(path: Path, description: str) -> Tuple[bool, str]:
    """Check if path exists and return status tuple."""
    if path.exists():
        return True, f"[green]✅ Found[/green] {description}"
    return False, f"[red]❌ Missing[/red] {description}"

def doctor():
    """
    Diagnose the current project's health and adherence to Lich standards.
    
    Checks for:
    - Vital project structure (apps, packages, deployments)
    - Critical configuration files (.env, docker-compose, eslintrc)
    - Infrastructure readiness
    """
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project (no .lich folder found)![/red]")
        console.print("[dim]Run this command from the root of a valid Lich project.[/dim]")
        raise typer.Exit(1)

    console.print("\n🩺 [bold blue]Lich Project Doctor[/bold blue]\n")

    checks = []
    
    # 1. Vital Structure
    checks.append(("[bold]Structure[/bold]", "", ""))
    checks.append(_check_path(Path("apps"), "Apps directory"))
    checks.append(_check_path(Path("packages"), "Packages directory"))
    checks.append(_check_path(Path("deployments"), "Deployments directory"))
    
    # 2. Critical Configuration
    checks.append(("[bold]Configuration[/bold]", "", ""))
    checks.append(_check_path(Path(".env"), "Environment file (.env)"))
    checks.append(_check_path(Path("deployments/docker/docker-compose.yml"), "Docker Compose file"))
    
    # 3. Application Health (Frontend/Backend)
    checks.append(("[bold]Applications[/bold]", "", ""))
    
    # Backend
    if Path("apps/backend").exists():
        checks.append(_check_path(Path("apps/backend/pyproject.toml"), "Backend config (pyproject.toml)"))
        checks.append(_check_path(Path("apps/backend/alembic.ini"), "Backend migrations (alembic.ini)"))

    # Frontend Apps (Check strict mode compliance)
    frontend_apps = ["admin", "web", "landing"]
    for app in frontend_apps:
        app_path = Path(f"apps/{app}")
        if app_path.exists():
            checks.append(_check_path(app_path / "package.json", f"{app.capitalize()} App (package.json)"))
            checks.append(_check_path(app_path / ".eslintrc.json", f"{app.capitalize()} ESLint Config"))
            checks.append(_check_path(app_path / "tsconfig.json", f"{app.capitalize()} TypeScript Config"))

    # Display Results
    table = Table(box=None, show_header=False)
    table.add_column("Status", width=5)
    table.add_column("Check")
    
    passed_count = 0
    total_checks = 0
    
    for status, msg, *rest in checks:
        if status == "[bold]Structure[/bold]" or str(status).startswith("[bold]"):
            table.add_row("", "")
            table.add_row("", status)
            continue
            
        total_checks += 1
        icon = "✅" if status else "❌"
        # msg already has color tags from _check_path or generic
        # Parse status from tuple
        if status:
            passed_count += 1
            table.add_row("[green]PASS[/green]", msg.replace("✅ ", "").replace("❌ ", ""))
        else:
            table.add_row("[red]FAIL[/red]", msg.replace("✅ ", "").replace("❌ ", ""))

    console.print(table)
    
    # Summary
    score = int((passed_count / total_checks) * 100) if total_checks > 0 else 0
    color = "green" if score == 100 else "yellow" if score > 70 else "red"
    
    console.print()
    console.print(Panel(
        f"Health Score: [bold {color}]{score}%[/bold {color}]\n"
        f"Passed: [green]{passed_count}[/green] / {total_checks}",
        title="Diagnostic Summary",
        border_style=color
    ))

    if score < 100:
        console.print("\n[bold yellow]💡 Suggestions:[/bold yellow]")
        console.print("Run [bold cyan]lich upgrade[/bold cyan] to attempt to fix missing framework files.")
        console.print("Run [bold cyan]lich setup[/bold cyan] to ensure your environment is configured.")
