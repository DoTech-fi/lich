"""
lich upgrade - Upgrade project to latest version.
"""
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
import sys
import subprocess
from packaging import version

import typer
import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from lich import __version__

console = Console()

# GitHub repository for template
GITHUB_REPO = "DoTech-fi/lich"
GITHUB_BRANCH = "main"
TEMPLATE_URL = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"

# Path to CHANGELOG.md (for dev environment)
CHANGELOG_PATH = Path(__file__).parent.parent.parent.parent.parent / "CHANGELOG.md"


def _get_local_template_path() -> Optional[Path]:
    """Get local template path (for development)."""
    # Try relative to CLI package (development mode)
    dev_path = Path(__file__).parent.parent.parent.parent.parent / "template"
    if dev_path.exists():
        return dev_path
    return None


def _download_template() -> str:
    """Download template from GitHub and return path."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Downloading latest template from GitHub...", total=None)
        
        # Download to temp directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "lich.zip")
        
        try:
            # Use requests for better SSL handling
            response = requests.get(TEMPLATE_URL, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
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
        
        # Extract
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            console.print("[red]❌ Downloaded file is not a valid zip![/red]")
            raise typer.Exit(1)
        
        # Find template directory (lich-main/template)
        # Note: GitHub archives unzip to REPO-BRANCH folder
        extracted_root = os.path.join(temp_dir, f"lich-{GITHUB_BRANCH}")
        
        # In the repo, the template is in 'template' folder
        extracted_template = os.path.join(extracted_root, "template")
        
        if not os.path.exists(extracted_template):
            # Fallback: maybe the zip structure is different
             if os.path.exists(os.path.join(temp_dir, "template")):
                 return os.path.join(temp_dir, "template")
             
             console.print(f"[red]❌ Template not found in downloaded archive! Looked in: {extracted_template}[/red]")
             console.print(f"[dim]Root contents: {os.listdir(temp_dir)}[/dim]")
             raise typer.Exit(1)
        
        return extracted_template


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
            version, date = match
            highlights = ""
            
            if i + 1 < len(sections):
                section = sections[i + 1]
                added_match = re.search(r'### Added\n- (.+)', section)
                if added_match:
                    highlights = added_match.group(1)[:50]
            
            versions.append({
                "version": version,
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
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--upgrade", f"lich=={target_version}"])
                console.print(f"[green]✅ CLI upgraded to v{target_version}! Restarting...[/green]")
                
                # Restart the process into the new version
                os.execvp(sys.argv[0], sys.argv)
            except subprocess.CalledProcessError as e:
                console.print(f"[red]❌ Failed to upgrade CLI: {e}[/red]")
                # Continue with project upgrade if CLI upgrade fails? Or stop? 
                # Probably better to just warn and continue.


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
    # 0. Check for CLI updates first
    if not local:
        _check_and_update_cli(dry_run=dry_run)

    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project (no .lich folder found)![/red]")
        raise typer.Exit(1)
    
    console.print("\n🔄 [bold blue]Lich Toolkit Upgrade[/bold blue]\n")
    console.print(f"[bold]Installed CLI Version:[/bold] v{__version__}")
    
    # 1. Determine Source Template
    local_path = _get_local_template_path()
    if local and local_path:
        template_base = str(local_path)
        console.print("[dim]Using local template (development mode)[/dim]")
    elif local_path and not to_version: 
        # Hint that local is available
        console.print("[dim]Local dev template detected. Use --local to use it.[/dim]")
        template_base = _download_template()
    else:
        template_base = _download_template()

    # The actual files are inside {{cookiecutter.project_slug}}
    # We need to construct the source path
    source_dir = Path(template_base) / "{{cookiecutter.project_slug}}"
    
    if not source_dir.exists():
        console.print(f"[red]❌ Invalid template structure. Could not find project slug dir in {template_base}[/red]")
        raise typer.Exit(1)

    # 2. Define Sync Targets (Source Relative -> Dest Relative)
    sync_targets = [
        (".lich/rules", ".lich/rules"),
        (".lich/workflows", ".lich/workflows"),
        (".lich/LICH_AI_PROMPT.md", ".lich/LICH_AI_PROMPT.md"),
        ("AGENTS.md", "AGENTS.md"),
        ("CLAUDE.md", "CLAUDE.md"),
    ]
    
    # Check what will change
    console.print("\n[bold]The following components will be updated/overwritten:[/bold]")
    for src, dst in sync_targets:
        exists = "exists" if Path(dst).exists() else "new"
        console.print(f"   • {dst} ({exists})")
        
    if dry_run:
        console.print("\n[yellow]Dry run mode - no changes will be made.[/yellow]")
        return
    
    # 3. Confirm
    if not force:
        console.print()
        if not Confirm.ask("Proceed with upgrade? (This will overwrite the listed files)"):
            console.print("[yellow]Upgrade cancelled.[/yellow]")
            raise typer.Exit(0)
    
    # 4. Backup
    backup_path = Path(".lich.backup")
    if Path(".lich").exists():
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(".lich", backup_path)
        console.print("\n📦 [dim]Backed up .lich to .lich.backup[/dim]")

    # 5. Perform Sync
    console.print("\n[bold]Syncing files...[/bold]")
    
    # 5.1 Write Version File (Manual)
    version_file = Path(".lich/lich.version")
    version_file.parent.mkdir(parents=True, exist_ok=True)
    version_file.write_text(f"{__version__}\n")
    console.print(f"   ✅ Updated file: [cyan].lich/lich.version[/cyan] (v{__version__})")
    
    # 5.2 Sync other files
    # Helper to clean variables from templates if found
    def copy_and_render(src: Path, dst: Path):
        content = src.read_text()
        # Simple replacements for known upgrade targets
        # This is a basic fallback to avoid raw {{cookiecutter}} strings in upgraded projects
        # Ideally, we would reload the cookiecutter context, but that's complex to retrieve post-generation.
        # We try to infer or leave them if not critical.
        
        # We only really care if we are copying AGENTS.md or CLAUDE.md on top of existing ones
        # For now, we will assume the user has a valid project setup.
        
        # If the file has {{ cookiecutter.project_slug }}, we try to replace it with current dir name
        current_slug = Path.cwd().name
        content = content.replace("{{ cookiecutter.project_slug }}", current_slug)
        content = content.replace("{{cookiecutter.project_slug}}", current_slug)
        
        # For other variables, if they exist in destination, we might want to keep destination?
        # But upgrade is usually force-overwrite rules. 
        # For documentation files like CLAUDE.md, it's risky to overwrite if they are customized.
        
        dst.write_text(content)

    for src_rel, dst_rel in sync_targets:
        src_path = source_dir / src_rel
        dst_path = Path(dst_rel)
        
        if not src_path.exists():
            console.print(f"   [yellow]⚠️ Source not found: {src_rel} (skipping)[/yellow]")
            continue
            
        try:
            if src_path.is_dir():
                # For directories (rules/workflows), we treat them as pure rewrites/updates
                # These shouldn't have per-project cookiecutter variables usually
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                console.print(f"   ✅ Updated directory: [cyan]{dst_rel}[/cyan]")
            else:
                # File copy
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Check for templating
                src_content = src_path.read_text()
                if "{{" in src_content and "cookiecutter" in src_content:
                     copy_and_render(src_path, dst_path)
                     console.print(f"   ✅ Updated templated file: [cyan]{dst_rel}[/cyan]")
                else:
                     shutil.copy2(src_path, dst_path)
                     console.print(f"   ✅ Updated file: [cyan]{dst_rel}[/cyan]")
                
        except Exception as e:
            console.print(f"   [red]❌ Failed to update {dst_rel}: {e}[/red]")

    console.print("\n[green]✅ Project configuration upgraded successfully![/green]")
    console.print(Panel.fit(
        "[bold yellow]⚠️  Important:[/bold yellow] Please run [bold cyan]lich setup[/bold cyan] to ensure your AI tool configurations are up to date.\n"
        "This is especially important if you are upgrading to v1.7.9+.",
        border_style="yellow"
    ))
    console.print("[dim]You may now need to run `lich start` or check `AGENTS.md` for new commands.[/dim]")
