"""
lich deploy - Deployment commands using Ansible.

Usage:
    lich deploy --host myserver.com --user deploy --key ~/.ssh/id_rsa
    lich deploy --dry-run                    # Preview only
    lich deploy --env staging               # Use staging inventory
"""
import subprocess
import os
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

deploy_app = typer.Typer(
    name="deploy",
    help="🚀 Deploy your Lich project using Ansible",
    no_args_is_help=False,
)


def _check_lich_project():
    """Check if we're in a Lich project."""
    if not (Path(".lich").exists() or Path("backend").exists()):
        console.print("[red]Error: Not in a Lich project directory[/red]")
        raise typer.Exit(1)


def _check_ansible_installed() -> bool:
    """Check if Ansible is installed."""
    try:
        result = subprocess.run(["which", "ansible"], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _create_dynamic_inventory(host: str, user: str, key_file: str) -> Path:
    """Create a dynamic inventory file."""
    inventory_content = f"""[servers]
{host} ansible_user={user} ansible_ssh_private_key_file={key_file}

[servers:vars]
ansible_python_interpreter=/usr/bin/python3
"""
    inventory_path = Path(".lich") / "inventory.ini"
    inventory_path.parent.mkdir(exist_ok=True)
    inventory_path.write_text(inventory_content)
    return inventory_path


def _get_playbook_path(name: str) -> Optional[Path]:
    """Get path to a playbook."""
    paths_to_check = [
        Path("infra/ansible/playbooks") / f"{name}.yml",
        Path("ansible/playbooks") / f"{name}.yml",
        Path("deploy") / f"{name}.yml",
    ]
    for path in paths_to_check:
        if path.exists():
            return path
    return None


@deploy_app.callback(invoke_without_command=True)
def deploy_command(
    ctx: typer.Context,
    host: str = typer.Option(None, "--host", "-h", help="Target host (IP or domain)"),
    ip: str = typer.Option(None, "--ip", help="Target IP address (alias for --host)"),
    user: str = typer.Option("deploy", "--user", "-u", help="SSH username"),
    key_file: str = typer.Option(None, "--key", "-k", help="Path to SSH private key"),
    environment: str = typer.Option("production", "--env", "-e", help="Environment (staging, production)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying"),
    playbook: str = typer.Option("site", "--playbook", "-p", help="Playbook to run (default: site)"),
    tags: str = typer.Option(None, "--tags", "-t", help="Only run specific tags"),
):
    """
    🚀 Deploy your Lich project to a remote server.
    
    Requires Ansible to be installed. Uses playbooks from infra/ansible/.
    
    Examples:
        lich deploy --host server.com --user deploy
        lich deploy --env staging --dry-run
        lich deploy --tags app,nginx
    """
    _check_lich_project()
    
    if not _check_ansible_installed():
        console.print("[red]Error: Ansible is not installed[/red]")
        console.print("[yellow]Install with: pip install ansible[/yellow]")
        raise typer.Exit(1)
    
    console.print(Panel.fit("🚀 Lich Deployment", style="bold blue"))
    
    target_host = host or ip
    
    # Find or create inventory
    inventory_path = None
    if target_host:
        # Use dynamic inventory
        key = key_file or os.path.expanduser("~/.ssh/id_rsa")
        inventory_path = _create_dynamic_inventory(target_host, user, key)
        console.print(f"[blue]Using dynamic inventory for {target_host}[/blue]")
    else:
        # Look for environment-based inventory
        inv_paths = [
            Path(f"infra/ansible/inventory/{environment}.yml"),
            Path(f"infra/ansible/inventory/{environment}.ini"),
            Path(f"ansible/inventory/{environment}.yml"),
        ]
        for path in inv_paths:
            if path.exists():
                inventory_path = path
                break
        
        if not inventory_path:
            console.print(f"[red]No inventory found for environment: {environment}[/red]")
            console.print("[yellow]Either provide --host or create an inventory file[/yellow]")
            raise typer.Exit(1)
    
    # Find playbook
    playbook_path = _get_playbook_path(playbook)
    if not playbook_path:
        console.print(f"[red]Playbook not found: {playbook}.yml[/red]")
        console.print("[yellow]Create playbook at: infra/ansible/playbooks/site.yml[/yellow]")
        raise typer.Exit(1)
    
    console.print(f"[blue]Environment: {environment}[/blue]")
    console.print(f"[blue]Playbook: {playbook_path}[/blue]")
    console.print(f"[blue]Inventory: {inventory_path}[/blue]")
    
    # Build ansible-playbook command
    cmd = [
        "ansible-playbook",
        str(playbook_path),
        "-i", str(inventory_path),
    ]
    
    if dry_run:
        cmd.append("--check")
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]")
    
    if tags:
        cmd.extend(["--tags", tags])
    
    console.print(f"\n[dim]Running: {' '.join(cmd)}[/dim]\n")
    
    # Execute
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        console.print("\n[green]✓ Deployment completed successfully![/green]")
    else:
        console.print("\n[red]✗ Deployment failed[/red]")
        raise typer.Exit(1)
