"""
Shared helpers for Lich CLI commands.

Single home for logic that was previously copy-pasted across command modules:
- project detection (ensure_lich_project / is_lich_project)
- generic subprocess runners (run_command / run_command_ok)
- tool availability checks (check_tool_installed)

Security-sensitive local/remote execution for deploy lives in _shell.py — do
not merge the two: _shell handles quoting for remote scripts, common handles
plain local tool invocations.
"""
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()


def ensure_lich_project() -> None:
    """Exit with code 1 if the cwd is not a Lich project (.lich or backend/)."""
    if not (Path(".lich").exists() or Path("backend").exists()):
        console.print("[red]Error: Not in a Lich project directory[/red]")
        raise typer.Exit(1)


def is_lich_project() -> bool:
    """Return True if the cwd has a .lich marker (strict check used by make)."""
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        return False
    return True


def run_command(
    cmd: list, cwd: Optional[Path] = None, capture: bool = True
) -> tuple[int, str, str]:
    """Run a command; return (exit_code, stdout, stderr). -1 if binary missing."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            cwd=cwd or Path.cwd(),
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def run_command_ok(
    cmd: list, cwd: Optional[Path] = None, show_output: bool = True
) -> bool:
    """Run a command; return True on exit code 0. Prints error if binary missing."""
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


def check_tool_installed(tool: str) -> bool:
    """Return True if `tool` is on PATH (shutil.which, no subprocess)."""
    return shutil.which(tool) is not None
