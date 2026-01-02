"""
lich seed - Database seeding.
"""
import importlib
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def seed_command(
    name: str = typer.Argument(None, help="Specific seeder to run (e.g., users)"),
    fresh: bool = typer.Option(False, "--fresh", "-f", help="Re-run migrations before seeding"),
    list_seeders: bool = typer.Option(False, "--list", "-l", help="List available seeders"),
):
    """
    Seed the database with test data.
    
    Looks for seeders in backend/seeds/ directory.
    Each seeder should have a run() function.
    
    Examples:
        lich seed              # Run all seeders
        lich seed users        # Run specific seeder
        lich seed --fresh      # Re-migrate and seed
        lich seed --list       # List available seeders
    """
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        raise typer.Exit(1)
    
    seeds_path = Path("backend/seeds")
    
    # Create seeds folder if missing
    if not seeds_path.exists():
        console.print("[yellow]Creating backend/seeds/ directory...[/yellow]")
        seeds_path.mkdir(parents=True)
        
        # Create example seeder
        example_seeder = '''"""
Example seeder - Users.
"""

async def run(db_session):
    """
    Seed the database with users.
    
    Args:
        db_session: Database session
    """
    print("Seeding users...")
    
    # Example:
    # from internal.entities.user import User
    # 
    # users = [
    #     User.create(email="admin@example.com", role="admin"),
    #     User.create(email="user@example.com", role="user"),
    # ]
    # 
    # for user in users:
    #     await db_session.save(user)
    
    print("✅ Users seeded!")
'''
        (seeds_path / "users.py").write_text(example_seeder)
        (seeds_path / "__init__.py").write_text("")
        console.print("[green]Created example seeder: backend/seeds/users.py[/green]")
        return
    
    # List seeders
    if list_seeders:
        _list_seeders(seeds_path)
        return
    
    console.print("\n🌱 [bold blue]Database Seeding[/bold blue]\n")
    
    # Fresh migration
    if fresh:
        console.print("[yellow]Running fresh migrations...[/yellow]")
        subprocess.run(["lich", "migration", "down", "base"])
        subprocess.run(["lich", "migration", "up"])
        console.print("")
    
    # Get seeders to run
    seeders = []
    if name:
        seeder_file = seeds_path / f"{name}.py"
        if not seeder_file.exists():
            console.print(f"[red]❌ Seeder not found: {name}[/red]")
            raise typer.Exit(1)
        seeders = [name]
    else:
        seeders = [
            f.stem for f in seeds_path.glob("*.py")
            if not f.name.startswith("_")
        ]
    
    if not seeders:
        console.print("[yellow]No seeders found[/yellow]")
        return
    
    console.print(f"Running seeders: {', '.join(seeders)}\n")
    
    # Run seeders
    for seeder_name in seeders:
        console.print(f"[dim]Seeding: {seeder_name}...[/dim]")
        
        # Import and run seeder
        try:
            sys.path.insert(0, "backend")
            module = importlib.import_module(f"seeds.{seeder_name}")
            
            if hasattr(module, "run"):
                # TODO: Pass actual DB session
                # For now, just call sync version or skip async
                import asyncio
                if asyncio.iscoroutinefunction(module.run):
                    console.print("   [yellow]Async seeder - manual run required[/yellow]")
                else:
                    module.run(None)
                    console.print(f"   [green]✅ {seeder_name} complete[/green]")
            else:
                console.print("   [yellow]No run() function found[/yellow]")
        except Exception as e:
            console.print(f"   [red]❌ Error: {e}[/red]")
    
    console.print("\n[green]✅ Seeding complete![/green]")


def _list_seeders(seeds_path: Path):
    """List available seeders."""
    console.print("\n🌱 [bold blue]Available Seeders[/bold blue]\n")
    
    seeders = [
        f.stem for f in seeds_path.glob("*.py")
        if not f.name.startswith("_")
    ]
    
    if not seeders:
        console.print("[yellow]No seeders found[/yellow]")
        console.print("[dim]Create one: backend/seeds/users.py[/dim]")
        return
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Seeder")
    table.add_column("Path")
    
    for seeder in seeders:
        table.add_row(seeder, f"backend/seeds/{seeder}.py")
    
    console.print(table)
