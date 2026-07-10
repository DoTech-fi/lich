"""
Shared helpers for Lich CLI commands.

Single home for logic that was previously copy-pasted across command modules:
- project detection (ensure_lich_project / is_lich_project)
- generic subprocess runners (run_command / run_command_ok)
- tool availability checks (check_tool_installed)
- template helpers (get_local_template_path / download_template)

Security-sensitive local/remote execution for deploy lives in _shell.py — do
not merge the two: _shell handles quoting for remote scripts, common handles
plain local tool invocations.
"""
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import requests
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

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


# ---------------------------------------------------------------------------
# Template helpers (shared between init.py and upgrade.py)
# ---------------------------------------------------------------------------

GITHUB_REPO = "DoTech-fi/lich"
GITHUB_BRANCH = "main"
TEMPLATE_URL = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"


def get_local_template_path() -> Optional[Path]:
    """Get local template path (repo checkout / development mode)."""
    dev_path = Path(__file__).parent.parent.parent.parent.parent / "template"
    if dev_path.exists():
        return dev_path
    return None


def download_template() -> str:
    """Download the project template from GitHub, return the extracted path."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Downloading template from GitHub...", total=None)

        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "lich.zip")

        try:
            response = requests.get(TEMPLATE_URL, stream=True, timeout=60)
            response.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.SSLError:
            console.print("[red]❌ SSL Certificate Error[/red]")
            console.print("[dim]Try running: /Applications/Python*/Install\\ Certificates.command[/dim]")
            console.print("[dim]Or: pip install certifi[/dim]")
            raise typer.Exit(1)
        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ Failed to download template: {e}[/red]")
            console.print("[dim]Check your internet connection.[/dim]")
            raise typer.Exit(1)

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            console.print("[red]❌ Downloaded file is not a valid zip![/red]")
            raise typer.Exit(1)

        extracted_root = os.path.join(temp_dir, f"lich-{GITHUB_BRANCH}")
        extracted_template = os.path.join(extracted_root, "template")

        if not os.path.exists(extracted_template):
            # Fallback: maybe the zip structure is different
            if os.path.exists(os.path.join(temp_dir, "template")):
                return os.path.join(temp_dir, "template")

            console.print(f"[red]❌ Template not found in downloaded archive! Looked in: {extracted_template}[/red]")
            console.print(f"[dim]Root contents: {os.listdir(temp_dir)}[/dim]")
            raise typer.Exit(1)

        return extracted_template
