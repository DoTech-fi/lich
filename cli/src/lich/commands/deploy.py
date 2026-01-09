"""
lich deploy - Deployment commands with setup and environment support.

Usage:
    lich deploy setup                    # Interactive setup
    lich deploy stage admin              # Deploy admin to staging
    lich deploy prod backend --version v1.2.3  # Deploy specific version
"""
import subprocess
import os
from pathlib import Path
from typing import Optional
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

deploy_app = typer.Typer(
    name="deploy",
    help="🚀 Deploy your Lich project",
    no_args_is_help=True,
)

DEPLOY_CONFIG_PATH = Path(".lich/deploy.yml")
SECRETS_PATH = Path(".secrets")
VALID_COMPONENTS = ["backend", "web", "admin", "landing"]


def _load_secrets() -> dict:
    """Load secrets from .secrets file."""
    secrets = {}
    if SECRETS_PATH.exists():
        with open(SECRETS_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    secrets[key] = value
    return secrets


def _validate_component(component: str):
    """Validate component name."""
    if component not in VALID_COMPONENTS:
        console.print(f"[red]Invalid component: {component}[/red]")
        console.print(f"[yellow]Choose from: {', '.join(VALID_COMPONENTS)}[/yellow]")
        raise typer.Exit(1)


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


def _load_deploy_config() -> dict:
    """Load deploy configuration from .lich/deploy.yml."""
    if not DEPLOY_CONFIG_PATH.exists():
        return {}
    with open(DEPLOY_CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}


def _save_deploy_config(config: dict):
    """Save deploy configuration to .lich/deploy.yml."""
    DEPLOY_CONFIG_PATH.parent.mkdir(exist_ok=True)
    with open(DEPLOY_CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def _get_ssh_config_hosts() -> list[str]:
    """Get list of hosts from ~/.ssh/config."""
    ssh_config = Path.home() / ".ssh" / "config"
    hosts = []
    if ssh_config.exists():
        with open(ssh_config) as f:
            for line in f:
                if line.strip().lower().startswith("host ") and "*" not in line:
                    host = line.strip().split()[1]
                    hosts.append(host)
    return hosts


# ============================================
# SETUP COMMAND
# ============================================

@deploy_app.command(name="setup")
def deploy_setup():
    """
    🛠️ Setup deployment configuration.
    
    Interactive setup for staging and production environments.
    Saves configuration to .lich/deploy.yml
    
    Examples:
        lich deploy setup
    """
    _check_lich_project()
    
    console.print(Panel.fit("🛠️ Deploy Setup", style="bold blue"))
    
    # Load existing config
    config = _load_deploy_config()
    
    # Ask which environment to configure
    console.print("\n[bold]Step 1: Select Environment[/bold]")
    env_choice = Prompt.ask(
        "Which environment?",
        choices=["staging", "production", "both"],
        default="staging"
    )
    
    environments = ["staging", "production"] if env_choice == "both" else [env_choice]
    
    for env in environments:
        console.print(f"\n[bold cyan]━━━ Configuring {env.upper()} ━━━[/bold cyan]")
        
        # Connection method
        console.print("\n[bold]Step 2: Connection Method[/bold]")
        connection = Prompt.ask(
            "How do you connect?",
            choices=["ssh-config", "manual"],
            default="ssh-config"
        )
        
        env_config = {"connection": connection}
        
        if connection == "ssh-config":
            # Show available hosts from SSH config
            ssh_hosts = _get_ssh_config_hosts()
            if ssh_hosts:
                console.print(f"  [dim]Available hosts: {', '.join(ssh_hosts[:5])}{'...' if len(ssh_hosts) > 5 else ''}[/dim]")
            
            ssh_name = Prompt.ask("SSH config name")
            env_config["ssh_name"] = ssh_name
            
        else:
            # Manual connection
            host = Prompt.ask("Server host/IP")
            user = Prompt.ask("SSH username", default="deploy")
            
            # Key or password
            auth_method = Prompt.ask(
                "Authentication",
                choices=["key", "password"],
                default="key"
            )
            
            env_config["host"] = host
            env_config["user"] = user
            env_config["auth"] = auth_method
            
            if auth_method == "key":
                key_path = Prompt.ask("SSH key path", default="~/.ssh/id_rsa")
                env_config["key_path"] = key_path
            else:
                console.print("  [yellow]⚠️ Password will be prompted during deploy[/yellow]")
        
        # Deploy path
        deploy_path = Prompt.ask("Deploy path on server", default="/opt/app")
        env_config["path"] = deploy_path
        
        # Docker or bare metal
        runtime = Prompt.ask(
            "Runtime",
            choices=["docker-compose", "bare-metal"],
            default="docker-compose"
        )
        env_config["runtime"] = runtime
        
        # Git repo (one time, shared across environments)
        if "git_repo" not in config:
            console.print("\n[bold]Git Repository[/bold]")
            git_repo = Prompt.ask("Git repo URL (SSH format)", default="git@github.com:user/repo.git")
            config["git_repo"] = git_repo
            
            is_private = Confirm.ask("Is this a private repo?", default=True)
            if is_private:
                console.print("  [dim]Make sure GITHUB_TOKEN is in .secrets file[/dim]")
                config["private_repo"] = True
        
        config[env] = env_config
        console.print(f"  [green]✓ {env} configured[/green]")
    
    # Save config
    _save_deploy_config(config)
    console.print(f"\n[green]✓ Saved to {DEPLOY_CONFIG_PATH}[/green]")
    
    # Show summary
    console.print("\n[bold]Configuration Summary:[/bold]")
    for env, cfg in config.items():
        if cfg.get("connection") == "ssh-config":
            console.print(f"  {env}: SSH config → {cfg.get('ssh_name')}")
        else:
            console.print(f"  {env}: {cfg.get('user')}@{cfg.get('host')}")
    
    console.print("\n[dim]Run 'lich deploy stage <component>' to deploy[/dim]")


# ============================================
# DEPLOY COMMANDS
# ============================================

def _run_deploy(env: str, component: str, version: Optional[str] = None, dry_run: bool = False):
    """Run deployment for a component to an environment."""
    _check_lich_project()
    _validate_component(component)
    
    config = _load_deploy_config()
    
    if env not in config:
        console.print(f"[red]Environment '{env}' not configured[/red]")
        console.print("[yellow]Run 'lich deploy setup' first[/yellow]")
        raise typer.Exit(1)
    
    env_config = config[env]
    
    console.print(Panel.fit(f"🚀 Deploy {component} → {env}", style="bold blue"))
    
    # Show deploy info
    if env_config.get("connection") == "ssh-config":
        console.print(f"  [blue]Server: {env_config.get('ssh_name')} (SSH config)[/blue]")
    else:
        console.print(f"  [blue]Server: {env_config.get('user')}@{env_config.get('host')}[/blue]")
    
    console.print(f"  [blue]Component: {component}[/blue]")
    console.print(f"  [blue]Version: {version or 'latest'}[/blue]")
    console.print(f"  [blue]Path: {env_config.get('path')}[/blue]")
    
    if dry_run:
        console.print("\n[yellow]DRY RUN - No changes will be made[/yellow]")
        return
    
    # Check Ansible
    if not _check_ansible_installed():
        console.print("[red]Error: Ansible is not installed[/red]")
        console.print("[yellow]Install with: pip install ansible[/yellow]")
        raise typer.Exit(1)
    
    # Build SSH connection string
    if env_config.get("connection") == "ssh-config":
        ssh_host = env_config.get("ssh_name")
    else:
        ssh_host = f"{env_config.get('user')}@{env_config.get('host')}"
    
    # Build Ansible command
    playbook = f"deploy-{component}.yml"
    playbook_path = Path("deploy") / playbook
    
    if not playbook_path.exists():
        console.print(f"[yellow]Playbook not found: {playbook_path}[/yellow]")
        console.print("[dim]Creating placeholder...[/dim]")
        _create_placeholder_playbook(playbook_path, component)
    
    cmd = [
        "ansible-playbook",
        str(playbook_path),
        "-i", f"{ssh_host},",  # Comma makes it a host list
        "-e", f"deploy_component={component}",
        "-e", f"deploy_path={env_config.get('path')}",
        "-e", f"deploy_env={env}",
    ]
    
    if version:
        cmd.extend(["-e", f"deploy_version={version}"])
    
    # Add secrets from .secrets file
    secrets = _load_secrets()
    if secrets.get("GITHUB_TOKEN"):
        cmd.extend(["-e", f"github_token={secrets.get('GITHUB_TOKEN')}"])
    
    if env_config.get("connection") != "ssh-config":
        if env_config.get("auth") == "password":
            cmd.append("--ask-pass")
        elif env_config.get("key_path"):
            cmd.extend(["--private-key", os.path.expanduser(env_config.get("key_path"))])
    
    console.print(f"\n[dim]Running: {' '.join(cmd[:6])}...[/dim]\n")
    
    # Run with live stdout
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        
        # Stream output in real-time
        for line in process.stdout:
            console.print(line, end="")
        
        process.wait()
        
        if process.returncode == 0:
            console.print(f"\n[green]✓ {component} deployed to {env}![/green]")
        else:
            console.print("\n[red]✗ Deployment failed[/red]")
            raise typer.Exit(1)
            
    except FileNotFoundError:
        console.print("[red]Error: ansible-playbook not found[/red]")
        console.print("[yellow]Install with: pip install ansible[/yellow]")
        raise typer.Exit(1)


def _create_placeholder_playbook(path: Path, component: str):
    """Create a placeholder Ansible playbook."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""---
# Deployment playbook for {component}
# Generated by lich deploy

- name: Deploy {component}
  hosts: all
  become: yes
  
  vars:
    deploy_component: "{component}"
    deploy_path: "/opt/app"
    deploy_version: "latest"
  
  tasks:
    - name: Show deployment info
      debug:
        msg: "Deploying {{{{ deploy_component }}}} version {{{{ deploy_version }}}} to {{{{ deploy_path }}}}"
    
    - name: Pull latest code
      git:
        repo: "{{{{ lookup('env', 'GIT_REPO') }}}}"
        dest: "{{{{ deploy_path }}}}"
        version: "{{{{ deploy_version }}}}"
      when: deploy_version != 'latest'
    
    - name: Build and restart (docker-compose)
      shell: |
        cd {{{{ deploy_path }}}}
        docker-compose pull {component}
        docker-compose up -d {component}
      when: deploy_component in ['backend', 'web', 'admin', 'landing']
"""
    
    path.write_text(content)
    console.print(f"  [green]✓ Created {path}[/green]")


@deploy_app.command(name="stage")
def deploy_stage(
    component: str = typer.Argument(..., help="Component to deploy (backend, web, admin, landing)"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version/tag to deploy"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without deploying"),
):
    """
    🚀 Deploy to staging environment.
    
    Examples:
        lich deploy stage admin
        lich deploy stage backend --version v1.2.3
    """
    _run_deploy("staging", component, version, dry_run)


@deploy_app.command(name="prod")
def deploy_prod(
    component: str = typer.Argument(..., help="Component to deploy (backend, web, admin, landing)"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version/tag to deploy"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without deploying"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """
    🚀 Deploy to production environment.
    
    Examples:
        lich deploy prod admin --version v1.2.3
    """
    if not force:
        confirm = Confirm.ask(f"[yellow]⚠️ Deploy {component} to PRODUCTION?[/yellow]")
        if not confirm:
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)
    
    _run_deploy("production", component, version, dry_run)


@deploy_app.command(name="status")
def deploy_status():
    """
    📊 Show deployment configuration status.
    """
    _check_lich_project()
    
    config = _load_deploy_config()
    
    if not config:
        console.print("[yellow]No deployment configured[/yellow]")
        console.print("[dim]Run 'lich deploy setup' to configure[/dim]")
        return
    
    console.print(Panel.fit("📊 Deployment Configuration", style="bold blue"))
    
    for env, cfg in config.items():
        console.print(f"\n[bold]{env.upper()}[/bold]")
        if cfg.get("connection") == "ssh-config":
            console.print(f"  Connection: SSH config → {cfg.get('ssh_name')}")
        else:
            console.print(f"  Connection: {cfg.get('user')}@{cfg.get('host')}")
        console.print(f"  Path: {cfg.get('path')}")
        console.print(f"  Runtime: {cfg.get('runtime', 'docker-compose')}")
