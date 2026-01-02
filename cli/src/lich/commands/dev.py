"""
lich dev / lich stop - Manage development environment.
"""
import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def _is_lich_project() -> bool:
    """Check if current directory is a Lich project."""
    return Path(".lich").exists() and Path("docker-compose.yml").exists()


def _run_script(script_name: str) -> int:
    """Run a shell script and return exit code."""
    script_path = Path(script_name)
    if not script_path.exists():
        console.print(f"[red]❌ {script_name} not found[/red]")
        return 1
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    # Run script
    result = subprocess.run(["bash", str(script_path)])
    return result.returncode


def start_dev():
    """
    Start the development environment.
    
    Runs docker-compose and starts all services.
    """
    if not _is_lich_project():
        console.print("[red]❌ Not a Lich project![/red]")
        console.print("   Run this command from the project root.")
        raise typer.Exit(1)
    
    console.print("\n🚀 [bold blue]Starting development environment...[/bold blue]\n")
    
    # Check for dev-start.sh
    if Path("dev-start.sh").exists():
        exit_code = _run_script("dev-start.sh")
        if exit_code != 0:
            raise typer.Exit(exit_code)
    else:
        # Fallback to docker-compose
        result = subprocess.run(["docker", "compose", "up", "-d"])
        if result.returncode != 0:
            raise typer.Exit(result.returncode)
        
        console.print("\n[green]✅ Services started![/green]")
        console.print("\n🌐 [bold]Service URLs:[/bold]")
        console.print("   Web App:      http://localhost:3000")
        console.print("   Admin Panel:  http://localhost:3002")
        console.print("   Landing Page: http://localhost:4321")
        console.print("   API Docs:     http://localhost:8000/api/docs")


def stop_dev():
    """
    Stop the development environment.
    
    Stops all docker-compose services.
    """
    if not _is_lich_project():
        console.print("[red]❌ Not a Lich project![/red]")
        raise typer.Exit(1)
    
    console.print("\n🛑 [bold blue]Stopping development environment...[/bold blue]\n")
    
    # Check for dev-stop.sh
    if Path("dev-stop.sh").exists():
        exit_code = _run_script("dev-stop.sh")
        if exit_code != 0:
            raise typer.Exit(exit_code)
    else:
        # Fallback to docker-compose
        result = subprocess.run(["docker", "compose", "down"])
        if result.returncode != 0:
            raise typer.Exit(result.returncode)
        
        console.print("[green]✅ Services stopped![/green]")
