"""
lich migration - Database migration commands using Alembic.
"""
import subprocess
from pathlib import Path

import typer
from rich.console import Console

console = Console()

migration_app = typer.Typer(
    name="migration",
    help="Database migration commands (Alembic wrapper)",
    no_args_is_help=True,
)


def _check_alembic() -> bool:
    """Check if we're in a Lich project with Alembic."""
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        return False
    
    if not Path("backend").exists():
        console.print("[red]❌ Backend folder not found![/red]")
        return False
    
    return True


def _run_alembic(args: list, cwd: str = "backend") -> int:
    """Run alembic command."""
    cmd = ["alembic"] + args
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]\n")
    
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


@migration_app.command("init")
def migration_init():
    """
    Initialize Alembic migrations for the project.
    """
    if not _check_alembic():
        raise typer.Exit(1)
    
    console.print("\n🔧 [bold blue]Initializing Alembic...[/bold blue]\n")
    
    alembic_dir = Path("backend/alembic")
    if alembic_dir.exists():
        console.print("[yellow]Alembic already initialized.[/yellow]")
        return
    
    exit_code = _run_alembic(["init", "alembic"])
    
    if exit_code == 0:
        console.print("\n[green]✅ Alembic initialized![/green]")
        console.print("\nNext steps:")
        console.print("   1. Edit backend/alembic.ini - set database URL")
        console.print("   2. Edit backend/alembic/env.py - import your models")
        console.print("   3. Run: lich migration create 'initial'")
    else:
        console.print("[red]❌ Failed to initialize Alembic[/red]")
        raise typer.Exit(exit_code)


@migration_app.command("create")
def migration_create(
    message: str = typer.Argument(..., help="Migration message"),
    autogenerate: bool = typer.Option(True, "--auto/--manual", help="Auto-generate from models"),
):
    """
    Create a new migration.
    """
    if not _check_alembic():
        raise typer.Exit(1)
    
    console.print(f"\n📝 [bold blue]Creating migration: {message}[/bold blue]\n")
    
    args = ["revision"]
    if autogenerate:
        args.append("--autogenerate")
    args.extend(["-m", message])
    
    exit_code = _run_alembic(args)
    
    if exit_code == 0:
        console.print("\n[green]✅ Migration created![/green]")
    else:
        console.print("[red]❌ Failed to create migration[/red]")
        raise typer.Exit(exit_code)


@migration_app.command("up")
def migration_up(
    revision: str = typer.Argument("head", help="Target revision (default: head)"),
):
    """
    Apply migrations (upgrade).
    """
    if not _check_alembic():
        raise typer.Exit(1)
    
    console.print(f"\n⬆️ [bold blue]Applying migrations to: {revision}[/bold blue]\n")
    
    exit_code = _run_alembic(["upgrade", revision])
    
    if exit_code == 0:
        console.print("\n[green]✅ Migrations applied![/green]")
    else:
        console.print("[red]❌ Migration failed[/red]")
        raise typer.Exit(exit_code)


@migration_app.command("down")
def migration_down(
    revision: str = typer.Argument("-1", help="Target revision (default: -1 step back)"),
):
    """
    Rollback migrations (downgrade).
    """
    if not _check_alembic():
        raise typer.Exit(1)
    
    console.print(f"\n⬇️ [bold blue]Rolling back to: {revision}[/bold blue]\n")
    
    exit_code = _run_alembic(["downgrade", revision])
    
    if exit_code == 0:
        console.print("\n[green]✅ Rollback complete![/green]")
    else:
        console.print("[red]❌ Rollback failed[/red]")
        raise typer.Exit(exit_code)


@migration_app.command("status")
def migration_status():
    """
    Show current migration status.
    """
    if not _check_alembic():
        raise typer.Exit(1)
    
    console.print("\n📊 [bold blue]Migration Status[/bold blue]\n")
    
    console.print("[bold]Current revision:[/bold]")
    _run_alembic(["current"])
    
    console.print("\n[bold]Migration history:[/bold]")
    _run_alembic(["history", "--verbose"])


@migration_app.command("heads")
def migration_heads():
    """
    Show available migration heads.
    """
    if not _check_alembic():
        raise typer.Exit(1)
    
    console.print("\n🎯 [bold blue]Migration Heads[/bold blue]\n")
    _run_alembic(["heads"])
