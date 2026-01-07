"""
lich lint - Code linting commands.

Usage:
    lich lint                   # Lint all (Python + TypeScript)
    lich lint --backend         # Python only (ruff)
    lich lint --frontend        # TypeScript only (eslint)
    lich lint --fix             # Auto-fix issues
"""
import subprocess
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

lint_app = typer.Typer(
    name="lint",
    help="🧹 Code linting for Python and TypeScript",
    no_args_is_help=False,
)


def _check_lich_project():
    """Check if we're in a Lich project."""
    if not (Path(".lich").exists() or Path("backend").exists()):
        console.print("[red]Error: Not in a Lich project directory[/red]")
        raise typer.Exit(1)


def _run_command(cmd: list, cwd: Path = None) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or Path.cwd(),
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def _check_tool_installed(tool: str) -> bool:
    """Check if a tool is installed."""
    code, _, _ = _run_command(["which", tool])
    return code == 0


def lint_python(fix: bool = False) -> dict:
    """Lint Python code with ruff."""
    results = {"tool": "python", "passed": True, "issues": 0, "fixed": 0}
    
    backend_path = Path("backend")
    if not backend_path.exists():
        console.print("[yellow]  ⚠ No backend directory found[/yellow]")
        return results
    
    console.print("\n[blue]🐍 Linting Python code with ruff...[/blue]")
    
    # Check for ruff
    if not _check_tool_installed("ruff"):
        console.print("[yellow]  ⚠ ruff not installed. Install with: pip install ruff[/yellow]")
        # Fallback to flake8
        if _check_tool_installed("flake8"):
            console.print("[blue]  Using flake8 instead...[/blue]")
            code, stdout, stderr = _run_command(["flake8", str(backend_path), "--count"])
            if code != 0:
                results["passed"] = False
                # Count issues from output
                lines = stdout.strip().split('\n')
                if lines:
                    try:
                        results["issues"] = int(lines[-1])
                    except ValueError:
                        results["issues"] = len(lines)
        return results
    
    # Run ruff check
    cmd = ["ruff", "check", str(backend_path)]
    if fix:
        cmd.append("--fix")
    
    code, stdout, stderr = _run_command(cmd)
    
    if stdout:
        lines = [line for line in stdout.strip().split('\n') if line]
        results["issues"] = len(lines)
        
        # Show first 10 issues
        if lines:
            results["passed"] = False
            console.print(f"[red]  Found {len(lines)} issue(s)[/red]")
            for line in lines[:10]:
                console.print(f"    {line}")
            if len(lines) > 10:
                console.print(f"    ... and {len(lines) - 10} more")
    
    if code == 0:
        console.print("[green]  ✓ Python code looks good![/green]")
        results["passed"] = True
    
    # Run ruff format check
    console.print("[blue]🎨 Checking Python formatting...[/blue]")
    cmd = ["ruff", "format", "--check", str(backend_path)]
    if fix:
        cmd = ["ruff", "format", str(backend_path)]
    
    code, stdout, stderr = _run_command(cmd)
    if code != 0 and not fix:
        console.print("[yellow]  ⚠ Some files need formatting. Run with --fix to auto-format[/yellow]")
    elif fix:
        console.print("[green]  ✓ Code formatted[/green]")
    else:
        console.print("[green]  ✓ Code is properly formatted[/green]")
    
    return results


def lint_frontend(fix: bool = False) -> dict:
    """Lint TypeScript/JavaScript with eslint."""
    results = {"tool": "frontend", "passed": True, "issues": 0}
    
    apps_dir = Path("apps")
    if not apps_dir.exists():
        console.print("[yellow]  ⚠ No apps directory found[/yellow]")
        return results
    
    console.print("\n[blue]📦 Linting frontend apps with eslint...[/blue]")
    
    for app_dir in apps_dir.iterdir():
        if app_dir.is_dir() and (app_dir / "package.json").exists():
            console.print(f"  Linting [cyan]{app_dir.name}[/cyan]...")
            
            # Check if eslint is available in the project
            eslint_config = any([
                (app_dir / ".eslintrc").exists(),
                (app_dir / ".eslintrc.js").exists(),
                (app_dir / ".eslintrc.json").exists(),
                (app_dir / "eslint.config.js").exists(),
                (app_dir / "eslint.config.mjs").exists(),
            ])
            
            if not eslint_config:
                console.print(f"    [yellow]⚠ No eslint config found in {app_dir.name}[/yellow]")
                continue
            
            # Run npm run lint or npx eslint
            cmd = ["npm", "run", "lint"]
            if fix:
                cmd = ["npm", "run", "lint", "--", "--fix"]
            
            code, stdout, stderr = _run_command(cmd, cwd=app_dir)
            
            if code != 0:
                results["passed"] = False
                # Count approximate issues
                issue_lines = [line for line in (stdout + stderr).split('\n') if 'error' in line.lower() or 'warning' in line.lower()]
                results["issues"] += len(issue_lines)
                console.print(f"    [red]✗ Found issues in {app_dir.name}[/red]")
                # Show first few lines of output
                for line in (stdout + stderr).split('\n')[:5]:
                    if line.strip():
                        console.print(f"      {line}")
            else:
                console.print(f"    [green]✓ {app_dir.name} looks good![/green]")
    
    return results


@lint_app.callback(invoke_without_command=True)
def lint_command(
    ctx: typer.Context,
    backend: bool = typer.Option(False, "--backend", "-b", help="Lint Python code only"),
    frontend: bool = typer.Option(False, "--frontend", "-f", help="Lint TypeScript only"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix issues where possible"),
):
    """
    🧹 Run code linting on your Lich project.
    
    By default, lints both Python and TypeScript code.
    
    Examples:
        lich lint              # Lint everything
        lich lint --backend    # Python only
        lich lint --fix        # Auto-fix issues
    """
    _check_lich_project()
    
    # If no specific flags, run all
    run_all = not (backend or frontend)
    
    results = []
    
    console.print(Panel.fit("🧹 Lich Code Linter", style="bold blue"))
    
    if run_all or backend:
        results.append(lint_python(fix))
    
    if run_all or frontend:
        results.append(lint_frontend(fix))
    
    # Summary
    total_issues = sum(r["issues"] for r in results)
    passed = all(r["passed"] for r in results)
    
    console.print("\n")
    if passed:
        console.print(Panel.fit("[green]✓ All code looks good![/green]", title="Summary"))
    else:
        console.print(Panel.fit(
            f"[red]✗ Found {total_issues} issue(s). Run with --fix to auto-fix.[/red]",
            title="Summary"
        ))
        raise typer.Exit(1)
