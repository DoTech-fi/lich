"""
lich upgrade - Upgrade project to latest version.
"""
import os
import re
import shutil
import sys
import subprocess
from pathlib import Path
from packaging import version

import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from lich import __version__
from lich.commands.common import (
    get_local_template_path as _get_local_template_path,
    download_template as _download_template,
)

console = Console()

# Path to CHANGELOG.md (for dev environment)
CHANGELOG_PATH = Path(__file__).parent.parent.parent.parent.parent / "CHANGELOG.md"

# Files to always overwrite from the template
SYNC_TARGETS = [
    (".lich/rules", ".lich/rules"),
    (".lich/workflows", ".lich/workflows"),
    (".lich/LICH_AI_PROMPT.md", ".lich/LICH_AI_PROMPT.md"),
    ("AGENTS.md", "AGENTS.md"),
    ("CLAUDE.md", "CLAUDE.md"),
    # .github/workflows intentionally excluded — project-specific, rendered at init
]

# Files to add ONLY if missing (safe injection)
MISSING_TARGETS = [
    ("apps/admin/.eslintrc.json", "apps/admin/.eslintrc.json"),
    ("apps/web/.eslintrc.json", "apps/web/.eslintrc.json"),
    ("apps/landing/.eslintrc.json", "apps/landing/.eslintrc.json"),
]


def _parse_versions() -> list:
    """Parse available versions from CHANGELOG."""
    versions = []

    # Try to fetch CHANGELOG from GitHub if not local
    content = ""
    if CHANGELOG_PATH.exists():
        with open(CHANGELOG_PATH) as f:
            content = f.read()
    else:
        # Fallback to local version only
        return [{"version": __version__, "date": "current", "highlights": "Current CLI version"}]

    try:
        pattern = r'## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})'
        matches = re.findall(pattern, content)

        sections = content.split("## [")
        for i, match in enumerate(matches):
            ver, date = match
            highlights = ""

            if i + 1 < len(sections):
                section = sections[i + 1]
                added_match = re.search(r'### Added\n- (.+)', section)
                if added_match:
                    highlights = added_match.group(1)[:50]

            versions.append({
                "version": ver,
                "date": date,
                "highlights": highlights
            })
    except Exception:
        versions = [{"version": __version__, "date": "current", "highlights": "Current version"}]

    return versions


def _check_and_update_cli(dry_run: bool = False):
    """Check PyPI for updates and offer to upgrade CLI."""
    target_version = None

    # 1. Check for updates (safely)
    try:
        response = requests.get("https://pypi.org/pypi/lich/json", timeout=3)
        if response.status_code == 200:
            data = response.json()
            latest_version_str = data["info"]["version"]

            current_ver = version.parse(__version__)
            latest_ver = version.parse(latest_version_str)

            if latest_ver > current_ver:
                target_version = latest_version_str
    except Exception as e:
        console.print(f"[dim]Note: Failed to check for updates: {e}[/dim]")
        return

    # 2. Perform update (outside try/except)
    if target_version:
        console.print(f"\n[bold yellow]🚀 New Lich CLI version available: v{target_version}[/bold yellow]")
        console.print(f"[dim]Current version: v{__version__}[/dim]\n")

        if dry_run:
            console.print(f"[cyan]Would run: pip install --upgrade lich=={target_version}[/cyan]")
            return

        if Confirm.ask(f"Allow [bold cyan]lich upgrade[/bold cyan] to install v{target_version} first?"):
            console.print("[dim]Upgrading CLI...[/dim]")
            try:
                # Upgrade pip first to ensure we can install packages correctly
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

                # Now upgrade lich
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--upgrade", f"lich=={target_version}"])
                console.print(f"[green]✅ CLI upgraded to v{target_version}! Restarting...[/green]")

                # Restart the process into the new version
                os.execvp(sys.argv[0], sys.argv)
            except subprocess.CalledProcessError as e:
                console.print(f"[red]❌ Failed to upgrade CLI: {e}[/red]")
                # Continue with project upgrade if CLI upgrade fails? Or stop?
                # Probably better to just warn and continue.


def _copy_and_render(src: Path, dst: Path) -> bool:
    """Copy a template file, substituting the project slug and unescaping
    GitHub Actions variables. Returns True if rendered as text."""
    try:
        content = src.read_text(encoding="utf-8")
        current_slug = Path.cwd().name
        content = content.replace("{{ cookiecutter.project_slug }}", current_slug)
        content = content.replace("{{cookiecutter.project_slug}}", current_slug)
        content = content.replace('{{ "{{" }}', '{{')
        content = content.replace('{{ "}}" }}', '}}')
        dst.write_text(content, encoding="utf-8")
        return True
    except UnicodeDecodeError:
        shutil.copy2(src, dst)
        return False


def _recursive_copy(src_dir: Path, dst_dir: Path) -> None:
    """Recursively copy and render template files."""
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    dst_dir.mkdir(parents=True)
    for item in src_dir.iterdir():
        dst_item = dst_dir / item.name
        if item.is_dir():
            _recursive_copy(item, dst_item)
        else:
            if item.suffix in ['.md', '.yml', '.yaml', '.json', '.py', '.js', '.ts', '.css', '.html']:
                _copy_and_render(item, dst_item)
            else:
                shutil.copy2(item, dst_item)


def _resolve_template_source(local: bool, to_version: str) -> Path:
    """Pick local dev template or download; return the project-slug source dir or exit."""
    local_path = _get_local_template_path()
    if local and local_path:
        template_base = str(local_path)
        console.print("[dim]Using local template (development mode)[/dim]")
    elif local_path and not to_version:
        console.print("[dim]Local dev template detected. Use --local to use it.[/dim]")
        template_base = _download_template()
    else:
        template_base = _download_template()

    source_dir = Path(template_base) / "{{cookiecutter.project_slug}}"
    if not source_dir.exists():
        console.print(f"[red]❌ Invalid template structure. Could not find project slug dir in {template_base}[/red]")
        raise typer.Exit(1)
    return source_dir


def _print_upgrade_preview() -> None:
    """List what will be overwritten / added."""
    console.print("\n[bold]The following components will be updated/overwritten:[/bold]")
    for src, dst in SYNC_TARGETS:
        exists = "exists" if Path(dst).exists() else "new"
        console.print(f"   • {dst} ({exists})")
    console.print("\n[bold]The following files will be added if missing:[/bold]")
    for src, dst in MISSING_TARGETS:
        if not Path(dst).exists():
            console.print(f"   • {dst} (missing - will be created)")


def _backup_lich_dir() -> None:
    """Snapshot .lich to .lich.backup before overwriting."""
    backup_path = Path(".lich.backup")
    if Path(".lich").exists():
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(".lich", backup_path)
        console.print("\n📦 [dim]Backed up .lich to .lich.backup[/dim]")


def _sync_files(source_dir: Path) -> None:
    """Overwrite SYNC_TARGETS from the template source."""
    console.print("\n[bold]Syncing files...[/bold]")
    version_file = Path(".lich/lich.version")
    version_file.parent.mkdir(parents=True, exist_ok=True)
    version_file.write_text(f"{__version__}\n")
    console.print(f"   ✅ Updated file: [cyan].lich/lich.version[/cyan] (v{__version__})")

    for src_rel, dst_rel in SYNC_TARGETS:
        src_path = source_dir / src_rel
        dst_path = Path(dst_rel)
        if not src_path.exists():
            console.print(f"   [yellow]⚠️ Source not found: {src_rel} (skipping)[/yellow]")
            continue
        try:
            if src_path.is_dir():
                _recursive_copy(src_path, dst_path)
                console.print(f"   ✅ Updated directory: [cyan]{dst_rel}[/cyan]")
            else:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                _copy_and_render(src_path, dst_path)
                console.print(f"   ✅ Updated file: [cyan]{dst_rel}[/cyan]")
        except (OSError, shutil.Error) as e:
            console.print(f"   [red]❌ Failed to update {dst_rel}: {e}[/red]")


def _inject_missing_files(source_dir: Path) -> None:
    """Create MISSING_TARGETS files that don't exist yet."""
    console.print("\n[bold]Checking for new framework files...[/bold]")
    for src_rel, dst_rel in MISSING_TARGETS:
        src_path = source_dir / src_rel
        dst_path = Path(dst_rel)
        if dst_path.exists() or not src_path.exists():
            continue
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            _copy_and_render(src_path, dst_path)
            console.print(f"   ✅ Created missing file: [cyan]{dst_rel}[/cyan]")
        except (OSError, shutil.Error) as e:
            console.print(f"   [red]❌ Failed to create {dst_rel}: {e}[/red]")


def upgrade_project(
    to_version: str = typer.Option(None, "--to", help="Target version to upgrade to (informational)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying"),
    local: bool = typer.Option(False, "--local", help="Use local template (development)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """
    Upgrade project configuration to the latest Lich Toolkit version.

    This command updates:
    - .lich/rules/
    - .lich/workflows/
    - .lich/LICH_AI_PROMPT.md
    - AGENTS.md
    - CLAUDE.md

    It preserves your project code but ensures AI rules and workflows are up to date.
    """
    if not local:
        _check_and_update_cli(dry_run=dry_run)

    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project (no .lich folder found)![/red]")
        raise typer.Exit(1)

    console.print("\n🔄 [bold blue]Lich Toolkit Upgrade[/bold blue]\n")
    console.print(f"[bold]Installed CLI Version:[/bold] v{__version__}")

    source_dir = _resolve_template_source(local, to_version)
    _print_upgrade_preview()

    if dry_run:
        console.print("\n[yellow]Dry run mode - no changes will be made.[/yellow]")
        return

    if not force:
        console.print()
        if not Confirm.ask("Proceed with upgrade? (This will overwrite the listed files)"):
            console.print("[yellow]Upgrade cancelled.[/yellow]")
            raise typer.Exit(0)

    _backup_lich_dir()
    _sync_files(source_dir)
    _inject_missing_files(source_dir)

    console.print("\n[green]✅ Project configuration upgraded successfully![/green]")
    console.print(Panel.fit(
        "[bold yellow]⚠️  Important:[/bold yellow] You MUST run [bold cyan]lich setup[/bold cyan] now.\n\n"
        "Then, [bold red]RESTART[/bold red] this AI tool (Antigravity/Cursor/VSCode) to apply changes.",
        border_style="yellow",
        title="Next Steps"
    ))
