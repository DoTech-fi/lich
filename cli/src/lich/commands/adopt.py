"""
lich adopt - Adopt an existing Python project into Lich architecture.
"""
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

console = Console()


def _detect_framework(project_path: Path) -> dict:
    """Detect the framework used in the existing project."""
    info = {
        "framework": "unknown",
        "has_fastapi": False,
        "has_flask": False,
        "has_django": False,
        "has_sqlalchemy": False,
        "has_alembic": False,
        "database": "unknown",
        "has_redis": False,
        "has_docker": False,
        "has_tests": False,
    }
    
    # Check requirements.txt or pyproject.toml
    req_files = ["requirements.txt", "pyproject.toml", "setup.py"]
    requirements_content = ""
    
    for req_file in req_files:
        req_path = project_path / req_file
        if req_path.exists():
            with open(req_path) as f:
                requirements_content += f.read().lower()
    
    # Detect frameworks
    if "fastapi" in requirements_content:
        info["framework"] = "fastapi"
        info["has_fastapi"] = True
    elif "flask" in requirements_content:
        info["framework"] = "flask"
        info["has_flask"] = True
    elif "django" in requirements_content:
        info["framework"] = "django"
        info["has_django"] = True
    
    # Detect database
    if "psycopg" in requirements_content or "asyncpg" in requirements_content:
        info["database"] = "postgresql"
    elif "pymongo" in requirements_content or "motor" in requirements_content:
        info["database"] = "mongodb"
    
    # Detect other components
    if "sqlalchemy" in requirements_content:
        info["has_sqlalchemy"] = True
    if "alembic" in requirements_content:
        info["has_alembic"] = True
    if "redis" in requirements_content:
        info["has_redis"] = True
    
    # Check for docker
    if (project_path / "Dockerfile").exists() or (project_path / "docker-compose.yml").exists():
        info["has_docker"] = True
    
    # Check for tests
    if (project_path / "tests").exists() or (project_path / "test").exists():
        info["has_tests"] = True
    
    return info


def _count_python_files(project_path: Path) -> dict:
    """Count Python files and analyze structure."""
    stats = {
        "total_files": 0,
        "total_lines": 0,
        "has_api_folder": False,
        "has_models_folder": False,
        "has_services_folder": False,
        "main_file": None,
    }
    
    for py_file in project_path.rglob("*.py"):
        if ".venv" in str(py_file) or "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
        stats["total_files"] += 1
        try:
            with open(py_file) as f:
                stats["total_lines"] += len(f.readlines())
        except (OSError, IOError):
            pass
        
        if py_file.name == "main.py" or py_file.name == "app.py":
            stats["main_file"] = str(py_file.relative_to(project_path))
    
    # Check folder structure
    if (project_path / "api").exists() or (project_path / "routes").exists():
        stats["has_api_folder"] = True
    if (project_path / "models").exists():
        stats["has_models_folder"] = True
    if (project_path / "services").exists():
        stats["has_services_folder"] = True
    
    return stats


def adopt_project(
    path: str = typer.Argument(..., help="Path to existing project"),
    output: str = typer.Option(".", "--output", "-o", help="Output directory for new Lich project"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Only analyze, don't create project"),
):
    """
    Adopt an existing Python project into Lich architecture.
    
    Analyzes the existing project and creates a new Lich project
    configured based on the analysis.
    """
    project_path = Path(path).resolve()
    
    if not project_path.exists():
        console.print(f"[red]❌ Path not found: {path}[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n🔍 [bold blue]Analyzing project: {project_path.name}[/bold blue]\n")
    
    # Detect framework and components
    info = _detect_framework(project_path)
    stats = _count_python_files(project_path)
    
    # Display analysis
    console.print("[bold]📊 Project Analysis:[/bold]\n")
    
    table = Table(show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Framework", info["framework"].title())
    table.add_row("Database", info["database"].title())
    table.add_row("Has SQLAlchemy", "✅" if info["has_sqlalchemy"] else "❌")
    table.add_row("Has Alembic", "✅" if info["has_alembic"] else "❌")
    table.add_row("Has Redis", "✅" if info["has_redis"] else "❌")
    table.add_row("Has Docker", "✅" if info["has_docker"] else "❌")
    table.add_row("Has Tests", "✅" if info["has_tests"] else "❌")
    table.add_row("Python Files", str(stats["total_files"]))
    table.add_row("Total Lines", str(stats["total_lines"]))
    table.add_row("Main File", stats["main_file"] or "Not found")
    
    console.print(table)
    
    # Suggested Lich configuration
    console.print("\n[bold]🎯 Suggested Lich Configuration:[/bold]\n")
    
    suggested = {
        "project_name": project_path.name.replace("_", " ").replace("-", " ").title(),
        "auth_strategy": "jwt_builtin",
        "database": info["database"] if info["database"] != "unknown" else "postgresql",
        "use_redis": "yes" if info["has_redis"] else "no",
        "is_microservice": "yes" if stats["total_files"] < 20 else "no",
        "include_admin_panel": "no" if stats["total_files"] < 20 else "yes",
    }
    
    for key, value in suggested.items():
        console.print(f"   {key}: [green]{value}[/green]")
    
    if dry_run:
        console.print("\n[yellow]Dry run mode - no project created.[/yellow]")
        return
    
    # Confirm and create
    console.print()
    if not Confirm.ask("Create Lich project with these settings?"):
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(0)
    
    console.print("\n[bold]📦 Creating Lich project...[/bold]")
    
    # Import cookiecutter and create project
    try:
        from cookiecutter.main import cookiecutter
        
        template_path = Path(__file__).parent.parent.parent.parent.parent / "template"
        
        result = cookiecutter(
            str(template_path),
            output_dir=output,
            no_input=True,
            extra_context={
                "project_name": suggested["project_name"],
                "auth_strategy": suggested["auth_strategy"],
                "database": suggested["database"],
                "use_redis": suggested["use_redis"],
                "is_microservice": suggested["is_microservice"],
                "include_admin_panel": suggested["include_admin_panel"],
            },
        )
        
        console.print(f"\n[green]✅ Lich project created: {Path(result).name}[/green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"   1. cd {Path(result).name}")
        console.print("   2. Copy your business logic to backend/internal/")
        console.print("   3. Migrate models to backend/internal/entities/")
        console.print("   4. Run: lich dev")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
