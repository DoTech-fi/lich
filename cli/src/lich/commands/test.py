"""
lich test - Test runner (pytest wrapper).
"""
import subprocess
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def test_command(
    path: str = typer.Argument(None, help="Specific test path or pattern"),
    unit: bool = typer.Option(False, "--unit", "-u", help="Run only unit tests"),
    integration: bool = typer.Option(False, "--integration", "-i", help="Run only integration tests"),
    coverage: bool = typer.Option(False, "--coverage", "-c", help="Run with coverage report"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch mode (re-run on changes)"),
):
    """
    Run project tests using pytest.
    
    Examples:
        lich test                    # Run all tests
        lich test --unit             # Run unit tests only
        lich test --coverage         # With coverage report
        lich test backend/tests/     # Specific path
    """
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        raise typer.Exit(1)
    
    console.print("\n🧪 [bold blue]Running Tests[/bold blue]\n")
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add path
    if path:
        cmd.append(path)
    elif unit:
        cmd.append("backend/tests/unit")
    elif integration:
        cmd.append("backend/tests/integration")
    else:
        cmd.append("backend/tests")
    
    # Add options
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if coverage:
        cmd.extend(["--cov=backend", "--cov-report=term-missing"])
    
    # Watch mode
    if watch:
        import importlib.util
        if importlib.util.find_spec("pytest_watch"):
            cmd = ["ptw", "--"] + cmd[2:]  # Replace with ptw
        else:
            console.print("[yellow]Watch mode requires pytest-watch: pip install pytest-watch[/yellow]")
            raise typer.Exit(1)
    
    # Run
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]\n")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        console.print("\n[green]✅ All tests passed![/green]")
    else:
        console.print("\n[red]❌ Some tests failed[/red]")
    
    raise typer.Exit(result.returncode)
