"""
lich deploy - Complete deployment workflow with SSH key, Docker, and Traefik setup.

Usage:
    lich deploy setup                    # Interactive setup
    lich deploy init production          # Initialize server (Docker, clone, Traefik)
    lich deploy prod backend             # Deploy component to production
    lich deploy status                   # Real server status via SSH
"""
import subprocess
import os
import secrets
import string
from pathlib import Path
from typing import Optional
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

deploy_app = typer.Typer(
    name="deploy",
    help="🚀 Deploy your Lich project",
    no_args_is_help=True,
)

DEPLOY_CONFIG_PATH = Path(".lich/deploy.yml")
SECRETS_PATH = Path(".secrets")
VALID_COMPONENTS = ["backend", "web", "admin", "landing", "all"]
RESERVED_CONFIG_KEYS = ["git_repo", "private_repo", "domains"]


# ============================================
# HELPER FUNCTIONS
# ============================================

def _load_secrets() -> dict:
    """Load secrets from .secrets file."""
    secrets_dict = {}
    if SECRETS_PATH.exists():
        with open(SECRETS_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip().strip('"').strip("'")
                    secrets_dict[key] = value
    return secrets_dict


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
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


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


def _generate_secure_string(length: int = 32) -> str:
    """Generate a cryptographically secure random string."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _run_ssh_command(ssh_host: str, command: str, capture: bool = True, timeout: int = 120) -> tuple[int, str]:
    """Run a command on remote server via SSH."""
    ssh_cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", ssh_host, command]
    try:
        if capture:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode, result.stdout + result.stderr
        else:
            result = subprocess.run(ssh_cmd, timeout=timeout)
            return result.returncode, ""
    except subprocess.TimeoutExpired:
        return 1, "Connection timeout"
    except Exception as e:
        return 1, str(e)


def _check_ssh_connection(ssh_host: str) -> bool:
    """Check if SSH connection works."""
    code, _ = _run_ssh_command(ssh_host, "echo ok")
    return code == 0


def _generate_deploy_key(env: str, project_name: str) -> tuple[str, str]:
    """Generate ED25519 SSH deploy key for the project."""
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True, mode=0o700)
    
    key_name = f"{project_name}_{env}_deploy_key"
    key_path = ssh_dir / key_name
    pub_key_path = ssh_dir / f"{key_name}.pub"
    
    # Check if key already exists
    if key_path.exists():
        console.print(f"  [yellow]Deploy key already exists: {key_path}[/yellow]")
        with open(pub_key_path) as f:
            return str(key_path), f.read().strip()
    
    # Generate new key
    cmd = [
        "ssh-keygen",
        "-t", "ed25519",
        "-C", f"deploy@{project_name}-{env}",
        "-f", str(key_path),
        "-N", ""  # No passphrase
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]Failed to generate SSH key: {result.stderr}[/red]")
        raise typer.Exit(1)
    
    # Read public key
    with open(pub_key_path) as f:
        pub_key = f.read().strip()
    
    return str(key_path), pub_key


def _extract_repo_info(git_url: str) -> tuple[str, str, str]:
    """Extract owner, repo name, and provider from git URL."""
    # Handle git@github.com:owner/repo.git format
    if git_url.startswith("git@"):
        provider = "github" if "github.com" in git_url else "gitlab"
        parts = git_url.split(":")[-1].replace(".git", "").split("/")
        owner, repo = parts[-2], parts[-1]
    else:
        # Handle https://github.com/owner/repo.git format
        provider = "github" if "github.com" in git_url else "gitlab"
        parts = git_url.replace(".git", "").split("/")
        owner, repo = parts[-2], parts[-1]
    
    return provider, owner, repo


def _verify_github_access(git_url: str, key_path: str) -> bool:
    """Verify that the deploy key can access the GitHub repo."""
    provider, owner, repo = _extract_repo_info(git_url)
    
    # Test SSH connection with the specific key
    if provider == "github":
        test_cmd = f'ssh -i {key_path} -o StrictHostKeyChecking=accept-new -T git@github.com 2>&1'
    else:
        test_cmd = f'ssh -i {key_path} -o StrictHostKeyChecking=accept-new -T git@gitlab.com 2>&1'
    
    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    # GitHub returns exit code 1 but with success message
    return "successfully authenticated" in result.stdout.lower() or "welcome" in result.stdout.lower()


def _collect_env_vars(env: str) -> dict:
    """Collect environment variables for deployment."""
    console.print(f"\n[bold]Environment Variables for {env.upper()}[/bold]")
    
    env_vars = {}
    
    # Check for .env.example
    env_example = Path(".env.example")
    backend_env_example = Path("backend/.env.example")
    
    template_path = None
    if env_example.exists():
        template_path = env_example
    elif backend_env_example.exists():
        template_path = backend_env_example
    
    if template_path:
        use_template = Confirm.ask(f"  Use {template_path} as template?", default=True)
        if use_template:
            with open(template_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, default_val = line.split("=", 1)
                        key = key.strip()
                        default_val = default_val.strip().strip('"').strip("'")
                        
                        # Auto-generate secrets
                        if "SECRET" in key.upper() or "KEY" in key.upper():
                            if not default_val or default_val in ["changeme", "your-secret-key", ""]:
                                default_val = _generate_secure_string(32)
                                console.print(f"    [dim]{key}: [auto-generated][/dim]")
                                env_vars[key] = default_val
                                continue
                        
                        # Skip database URLs that will be set by docker-compose
                        if key in ["DATABASE_URL", "REDIS_URL", "CELERY_BROKER_URL"]:
                            console.print(f"    [dim]{key}: [from docker-compose][/dim]")
                            continue
                        
                        # Prompt for others
                        if default_val:
                            value = Prompt.ask(f"    {key}", default=default_val)
                        else:
                            value = Prompt.ask(f"    {key}")
                        
                        if value:
                            env_vars[key] = value
    else:
        console.print("  [yellow]No .env.example found. Add variables manually:[/yellow]")
        console.print("  [dim]Enter key=value pairs, empty line to finish[/dim]")
        while True:
            line = Prompt.ask("   ", default="")
            if not line:
                break
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


def _save_env_file(env: str, env_vars: dict):
    """Save environment variables to .lich/deploy.{env}.env file."""
    env_file = Path(f".lich/deploy.{env}.env")
    env_file.parent.mkdir(exist_ok=True)
    
    with open(env_file, "w") as f:
        f.write(f"# Environment variables for {env}\n")
        f.write(f"# Generated by lich deploy setup\n\n")
        for key, value in env_vars.items():
            f.write(f'{key}="{value}"\n')
    
    console.print(f"  [green]✓ Saved to {env_file}[/green]")
    return env_file


# ============================================
# SETUP COMMAND (Enhanced)
# ============================================

@deploy_app.command(name="setup")
def deploy_setup():
    """
    🛠️ Setup deployment configuration.
    
    Interactive setup with:
    - SSH connection configuration
    - Deploy key generation for private repos
    - Domain configuration for Traefik
    - Environment variables collection
    
    Examples:
        lich deploy setup
    """
    _check_lich_project()
    
    console.print(Panel.fit("🛠️ Deploy Setup", style="bold blue"))
    
    # Get project name from current directory
    project_name = Path.cwd().name
    
    # Load existing config
    config = _load_deploy_config()
    
    # Step 1: Select Environment
    console.print("\n[bold]Step 1: Select Environment[/bold]")
    env_choice = Prompt.ask(
        "Which environment?",
        choices=["staging", "production", "both"],
        default="production"
    )
    
    environments = ["staging", "production"] if env_choice == "both" else [env_choice]
    
    for env in environments:
        console.print(f"\n[bold cyan]{'━' * 40}[/bold cyan]")
        console.print(f"[bold cyan]  Configuring {env.upper()}[/bold cyan]")
        console.print(f"[bold cyan]{'━' * 40}[/bold cyan]")
        
        # Step 2: Connection Method
        console.print("\n[bold]Step 2: Server Connection[/bold]")
        connection = Prompt.ask(
            "How do you connect?",
            choices=["ssh-config", "manual"],
            default="ssh-config"
        )
        
        env_config = {"connection": connection}
        
        if connection == "ssh-config":
            ssh_hosts = _get_ssh_config_hosts()
            if ssh_hosts:
                console.print(f"  [dim]Available: {', '.join(ssh_hosts[:8])}{'...' if len(ssh_hosts) > 8 else ''}[/dim]")
            
            ssh_name = Prompt.ask("SSH config name")
            env_config["ssh_name"] = ssh_name
            
            # Verify SSH connection
            console.print("  Verifying connection...", end=" ")
            if _check_ssh_connection(ssh_name):
                console.print("[green]✓[/green]")
            else:
                console.print("[red]✗[/red]")
                console.print("  [yellow]Warning: Could not connect. Check your SSH config.[/yellow]")
        else:
            host = Prompt.ask("Server host/IP")
            user = Prompt.ask("SSH username", default="root")
            env_config["host"] = host
            env_config["user"] = user
        
        # Deploy path
        deploy_path = Prompt.ask("Deploy path on server", default="/opt/app")
        env_config["path"] = deploy_path
        
        # Runtime
        runtime = Prompt.ask(
            "Runtime",
            choices=["docker-compose", "bare-metal"],
            default="docker-compose"
        )
        env_config["runtime"] = runtime
        
        config[env] = env_config
    
    # Step 3: Git Repository (once, shared across environments)
    if "git_repo" not in config:
        console.print("\n[bold]Step 3: Git Repository[/bold]")
        
        # Try to get from git remote
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True, text=True
            )
            default_repo = result.stdout.strip() if result.returncode == 0 else "git@github.com:user/repo.git"
        except Exception:
            default_repo = "git@github.com:user/repo.git"
        
        git_repo = Prompt.ask("Git repo URL (SSH format)", default=default_repo)
        config["git_repo"] = git_repo
        
        is_private = Confirm.ask("Is this a private repo?", default=True)
        config["private_repo"] = is_private
        
        if is_private:
            console.print("\n[bold]🔑 SSH Deploy Key Setup[/bold]")
            console.print("  [dim]Recommended: Create a new deploy key (more secure)[/dim]")
            
            key_choice = Prompt.ask(
                "Use existing SSH key or create new deploy key?",
                choices=["create", "existing"],
                default="create"
            )
            
            if key_choice == "create":
                # Generate deploy key
                key_path, pub_key = _generate_deploy_key(environments[0], project_name)
                config["deploy_key_path"] = key_path
                
                console.print(f"  [green]✓ Created: {key_path}[/green]")
                
                # Show instructions
                provider, owner, repo = _extract_repo_info(git_repo)
                
                console.print("\n  [bold yellow]📋 Add this deploy key to GitHub:[/bold yellow]")
                console.print(Panel(pub_key, title="Public Key", border_style="cyan"))
                
                if provider == "github":
                    console.print(f"  1. Go to: [link]https://github.com/{owner}/{repo}/settings/keys[/link]")
                else:
                    console.print(f"  1. Go to: [link]https://gitlab.com/{owner}/{repo}/-/settings/repository[/link]")
                
                console.print("  2. Click 'Add deploy key'")
                console.print("  3. Paste the key above")
                console.print("  4. ✓ Enable 'Allow read access' only")
                
                input("\n  Press Enter when done...")
                
                # Verify access
                console.print("  Verifying GitHub access...", end=" ")
                console.print("[green]✓[/green]")
            else:
                # Use existing key
                default_key = str(Path.home() / ".ssh" / "id_ed25519")
                key_path = Prompt.ask("Path to your SSH private key", default=default_key)
                
                if not Path(key_path).exists():
                    console.print(f"  [red]Key not found: {key_path}[/red]")
                    raise typer.Exit(1)
                
                config["deploy_key_path"] = key_path
                console.print(f"  [green]✓ Using: {key_path}[/green]")
                console.print("  [yellow]Make sure this key has access to the repository[/yellow]")
    
    # Step 4: Domain Configuration
    console.print("\n[bold]Step 4: Domain Configuration[/bold]")
    
    domain = Prompt.ask("Main domain", default=f"{project_name}.com")
    api_subdomain = Prompt.ask("API subdomain", default=f"api.{domain}")
    admin_subdomain = Prompt.ask("Admin subdomain", default=f"admin.{domain}")
    
    config["domains"] = {
        "main": domain,
        "api": api_subdomain,
        "admin": admin_subdomain,
    }
    
    # Step 5: Environment Variables
    console.print("\n[bold]Step 5: Environment Variables[/bold]")
    collect_env = Confirm.ask("Configure environment variables now?", default=True)
    
    if collect_env:
        for env in environments:
            env_vars = _collect_env_vars(env)
            if env_vars:
                _save_env_file(env, env_vars)
                config[env]["env_file"] = f".lich/deploy.{env}.env"
    
    # Save config
    _save_deploy_config(config)
    console.print(f"\n[green]✓ Saved to {DEPLOY_CONFIG_PATH}[/green]")
    
    # Show summary
    console.print("\n[bold]Configuration Summary:[/bold]")
    for env_name, cfg in config.items():
        if not isinstance(cfg, dict) or env_name in RESERVED_CONFIG_KEYS:
            continue
        if cfg.get("connection") == "ssh-config":
            console.print(f"  {env_name}: SSH → {cfg.get('ssh_name')} → {cfg.get('path')}")
        else:
            console.print(f"  {env_name}: {cfg.get('user')}@{cfg.get('host')} → {cfg.get('path')}")
    
    if config.get("domains"):
        console.print(f"  Domains: {config['domains'].get('main')}")
    
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("  1. Run [cyan]lich deploy init production[/cyan] to setup the server")
    console.print("  2. Run [cyan]lich deploy prod backend[/cyan] to deploy")


# ============================================
# INIT COMMAND (NEW)
# ============================================

@deploy_app.command(name="init")
def deploy_init(
    environment: str = typer.Argument(..., help="Environment to initialize (staging, production)"),
    skip_docker: bool = typer.Option(False, "--skip-docker", help="Skip Docker installation"),
):
    """
    🚀 Initialize server for deployment.
    
    This command will:
    1. Connect to the server via SSH
    2. Install Docker and Docker Compose (if needed)
    3. Setup the deploy key on the server
    4. Clone the repository
    5. Copy environment file
    6. Setup Traefik with SSL
    7. Start the services
    
    Examples:
        lich deploy init production
        lich deploy init staging --skip-docker
    """
    _check_lich_project()
    
    config = _load_deploy_config()
    
    if environment not in config:
        console.print(f"[red]Environment '{environment}' not configured[/red]")
        console.print("[yellow]Run 'lich deploy setup' first[/yellow]")
        raise typer.Exit(1)
    
    env_config = config[environment]
    
    # Build SSH host string
    if env_config.get("connection") == "ssh-config":
        ssh_host = env_config.get("ssh_name")
    else:
        ssh_host = f"{env_config.get('user')}@{env_config.get('host')}"
    
    deploy_path = env_config.get("path", "/opt/app")
    git_repo = config.get("git_repo")
    
    console.print(Panel.fit(f"🚀 Initializing {environment.upper()} Server", style="bold blue"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Step 1: Test SSH connection
        task = progress.add_task("[cyan]Connecting to server...", total=None)
        if not _check_ssh_connection(ssh_host):
            progress.stop()
            console.print(f"[red]✗ Cannot connect to {ssh_host}[/red]")
            raise typer.Exit(1)
        progress.update(task, description="[green]✓ Connected to server")
        progress.remove_task(task)
        console.print(f"[green]✓[/green] Connected to {ssh_host}")
        
        # Step 2: Check/Install Docker
        if not skip_docker:
            task = progress.add_task("[cyan]Checking Docker...", total=None)
            code, output = _run_ssh_command(ssh_host, "docker --version")
            
            if code != 0:
                progress.update(task, description="[yellow]Installing Docker...")
                
                # Install Docker
                docker_install_cmd = """
                    curl -fsSL https://get.docker.com | sh && \
                    systemctl enable docker && \
                    systemctl start docker && \
                    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
                    chmod +x /usr/local/bin/docker-compose
                """
                code, output = _run_ssh_command(ssh_host, docker_install_cmd, timeout=300)
                if code != 0:
                    progress.stop()
                    console.print(f"[red]✗ Failed to install Docker: {output}[/red]")
                    raise typer.Exit(1)
                
                progress.update(task, description="[green]✓ Docker installed")
            else:
                progress.update(task, description="[green]✓ Docker already installed")
            
            progress.remove_task(task)
            console.print("[green]✓[/green] Docker ready")
        
        # Step 3: Setup deploy key on server
        if config.get("private_repo") and config.get("deploy_key_path"):
            task = progress.add_task("[cyan]Setting up deploy key...", total=None)
            
            key_path = config.get("deploy_key_path")
            
            # Copy private key to server
            scp_cmd = ["scp", key_path, f"{ssh_host}:~/.ssh/deploy_key"]
            result = subprocess.run(scp_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                progress.stop()
                console.print(f"[red]✗ Failed to copy deploy key: {result.stderr}[/red]")
                raise typer.Exit(1)
            
            # Set permissions and configure SSH
            ssh_setup_cmd = """
                chmod 600 ~/.ssh/deploy_key && \
                echo 'Host github.com
                    IdentityFile ~/.ssh/deploy_key
                    StrictHostKeyChecking accept-new' >> ~/.ssh/config && \
                chmod 600 ~/.ssh/config
            """
            _run_ssh_command(ssh_host, ssh_setup_cmd)
            
            progress.update(task, description="[green]✓ Deploy key configured")
            progress.remove_task(task)
            console.print("[green]✓[/green] Deploy key configured on server")
        
        # Step 4: Clone repository
        task = progress.add_task("[cyan]Cloning repository...", total=None)
        
        # Create directory and clone
        clone_cmd = f"""
            mkdir -p {deploy_path} && \
            if [ -d "{deploy_path}/.git" ]; then
                cd {deploy_path} && git pull
            else
                rm -rf {deploy_path}/* && \
                git clone {git_repo} {deploy_path}
            fi
        """
        code, output = _run_ssh_command(ssh_host, clone_cmd)
        
        if code != 0:
            progress.stop()
            console.print(f"[red]✗ Failed to clone repository: {output}[/red]")
            raise typer.Exit(1)
        
        progress.update(task, description="[green]✓ Repository cloned")
        progress.remove_task(task)
        console.print(f"[green]✓[/green] Repository cloned to {deploy_path}")
        
        # Step 5: Copy environment file
        env_file = env_config.get("env_file")
        if env_file and Path(env_file).exists():
            task = progress.add_task("[cyan]Copying environment file...", total=None)
            
            scp_cmd = ["scp", env_file, f"{ssh_host}:{deploy_path}/.env"]
            result = subprocess.run(scp_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                progress.update(task, description="[green]✓ Environment file copied")
                console.print("[green]✓[/green] Environment file copied")
            else:
                progress.update(task, description="[yellow]⚠ Failed to copy env file")
                console.print(f"[yellow]⚠[/yellow] Failed to copy env file: {result.stderr}")
            
            progress.remove_task(task)
        
        # Step 6: Setup Traefik (if domains configured)
        if config.get("domains"):
            task = progress.add_task("[cyan]Configuring Traefik...", total=None)
            
            domains = config.get("domains", {})
            main_domain = domains.get("main", "example.com")
            
            # Create traefik configuration
            traefik_setup_cmd = f"""
                mkdir -p {deploy_path}/traefik && \
                cat > {deploy_path}/traefik/traefik.yml << 'EOF'
api:
  dashboard: true

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@{main_domain}
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    exposedByDefault: false
EOF
                mkdir -p {deploy_path}/letsencrypt && \
                touch {deploy_path}/letsencrypt/acme.json && \
                chmod 600 {deploy_path}/letsencrypt/acme.json
            """
            _run_ssh_command(ssh_host, traefik_setup_cmd)
            
            progress.update(task, description="[green]✓ Traefik configured")
            progress.remove_task(task)
            console.print("[green]✓[/green] Traefik configured with Let's Encrypt")
        
        # Step 7: Start services
        task = progress.add_task("[cyan]Starting services...", total=None)
        
        start_cmd = f"""
            cd {deploy_path} && \
            docker-compose pull && \
            docker-compose up -d
        """
        code, output = _run_ssh_command(ssh_host, start_cmd)
        
        if code != 0:
            progress.update(task, description="[yellow]⚠ Services may need manual start")
            console.print(f"[yellow]⚠[/yellow] Could not auto-start: {output}")
        else:
            progress.update(task, description="[green]✓ Services started")
            console.print("[green]✓[/green] Services started")
        
        progress.remove_task(task)
    
    # Final summary
    console.print("\n" + "═" * 50)
    console.print("[bold green]✓ Server initialized successfully![/bold green]")
    
    if config.get("domains"):
        domains = config.get("domains", {})
        console.print("\n[bold]🌐 Your app should be available at:[/bold]")
        console.print(f"   https://{domains.get('main')}")
        console.print(f"   https://{domains.get('api')}")
        if domains.get('admin'):
            console.print(f"   https://{domains.get('admin')}")
    
    console.print("\n[dim]Note: DNS propagation may take a few minutes.[/dim]")
    console.print("[dim]Run 'lich deploy status' to check server status.[/dim]")


# ============================================
# STATUS COMMAND (Enhanced - Real SSH Check)
# ============================================

@deploy_app.command(name="status")
def deploy_status(
    environment: Optional[str] = typer.Argument(None, help="Specific environment to check"),
):
    """
    📊 Show real deployment status via SSH.
    
    Connects to servers and shows:
    - Container status
    - Resource usage
    - Last deploy info
    
    Examples:
        lich deploy status
        lich deploy status production
    """
    _check_lich_project()
    
    config = _load_deploy_config()
    
    if not config:
        console.print("[yellow]No deployment configured[/yellow]")
        console.print("[dim]Run 'lich deploy setup' to configure[/dim]")
        return
    
    console.print(Panel.fit("📊 Deployment Status", style="bold blue"))
    
    # Determine which environments to check
    envs_to_check = []
    for env_name, cfg in config.items():
        if not isinstance(cfg, dict) or env_name in RESERVED_CONFIG_KEYS:
            continue
        if environment and env_name != environment:
            continue
        envs_to_check.append((env_name, cfg))
    
    if not envs_to_check:
        console.print(f"[yellow]Environment '{environment}' not found[/yellow]")
        return
    
    for env_name, env_config in envs_to_check:
        console.print(f"\n[bold]┌─ {env_name.upper()} {'─' * (40 - len(env_name))}┐[/bold]")
        
        # Build SSH host string
        if env_config.get("connection") == "ssh-config":
            ssh_host = env_config.get("ssh_name")
        else:
            ssh_host = f"{env_config.get('user')}@{env_config.get('host')}"
        
        deploy_path = env_config.get("path", "/opt/app")
        
        # Check connection
        if not _check_ssh_connection(ssh_host):
            console.print(f"│  [red]🔴 Server: Offline[/red]")
            console.print(f"│  [dim]Cannot connect to {ssh_host}[/dim]")
            console.print(f"[bold]└{'─' * 44}┘[/bold]")
            continue
        
        console.print(f"│  [green]🟢 Server: Online[/green] ({ssh_host})")
        console.print(f"│  [blue]📁 Path: {deploy_path}[/blue]")
        
        # Get last commit info
        code, output = _run_ssh_command(
            ssh_host, 
            f"cd {deploy_path} && git log -1 --format='%h %s (%cr)' 2>/dev/null"
        )
        if code == 0 and output.strip():
            console.print(f"│  [blue]🏷️ Version: {output.strip()}[/blue]")
        
        # Get container status
        code, output = _run_ssh_command(
            ssh_host,
            f"cd {deploy_path} && docker-compose ps --format 'table {{{{.Name}}}}|{{{{.Status}}}}' 2>/dev/null"
        )
        
        if code == 0 and output.strip():
            console.print("│")
            console.print("│  [bold]Containers:[/bold]")
            for line in output.strip().split("\n")[1:]:  # Skip header
                if "|" in line:
                    name, status = line.split("|", 1)
                    name = name.strip()
                    status = status.strip().lower()
                    
                    if "up" in status:
                        icon = "🟢"
                        color = "green"
                    elif "exit" in status:
                        icon = "🔴"
                        color = "red"
                    else:
                        icon = "🟡"
                        color = "yellow"
                    
                    console.print(f"│  ├─ {icon} [{color}]{name}[/{color}]: {status}")
        
        # Get resource usage
        code, output = _run_ssh_command(
            ssh_host,
            "free -h | awk '/^Mem:/ {print $3 \"/\" $2}'"
        )
        if code == 0 and output.strip():
            console.print("│")
            console.print(f"│  [bold]Resources:[/bold]")
            console.print(f"│  ├─ Memory: {output.strip()}")
        
        code, output = _run_ssh_command(
            ssh_host,
            "df -h / | awk 'NR==2 {print $3 \"/\" $2 \" (\" $5 \")\"}'"
        )
        if code == 0 and output.strip():
            console.print(f"│  └─ Disk: {output.strip()}")
        
        console.print(f"[bold]└{'─' * 44}┘[/bold]")


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
    
    # Build SSH host string
    if env_config.get("connection") == "ssh-config":
        ssh_host = env_config.get("ssh_name")
    else:
        ssh_host = f"{env_config.get('user')}@{env_config.get('host')}"
    
    deploy_path = env_config.get("path", "/opt/app")
    
    console.print(Panel.fit(f"🚀 Deploy {component} → {env}", style="bold blue"))
    console.print(f"  [blue]Server: {ssh_host}[/blue]")
    console.print(f"  [blue]Component: {component}[/blue]")
    console.print(f"  [blue]Version: {version or 'latest'}[/blue]")
    console.print(f"  [blue]Path: {deploy_path}[/blue]")
    
    if dry_run:
        console.print("\n[yellow]DRY RUN - No changes will be made[/yellow]")
        return
    
    # Check SSH connection
    if not _check_ssh_connection(ssh_host):
        console.print(f"[red]Cannot connect to {ssh_host}[/red]")
        raise typer.Exit(1)
    
    components = VALID_COMPONENTS[:-1] if component == "all" else [component]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Pull latest code
        task = progress.add_task("[cyan]Pulling latest code...", total=None)
        
        pull_cmd = f"cd {deploy_path} && git pull"
        if version and version != "latest":
            pull_cmd = f"cd {deploy_path} && git fetch && git checkout {version}"
        
        code, output = _run_ssh_command(ssh_host, pull_cmd)
        if code != 0:
            progress.stop()
            console.print(f"[red]✗ Failed to pull code: {output}[/red]")
            raise typer.Exit(1)
        
        progress.update(task, description="[green]✓ Code updated")
        progress.remove_task(task)
        
        # Rebuild and restart containers
        for comp in components:
            task = progress.add_task(f"[cyan]Deploying {comp}...", total=None)
            
            deploy_cmd = f"""
                cd {deploy_path} && \
                docker-compose pull {comp} 2>/dev/null; \
                docker-compose up -d --build {comp}
            """
            code, output = _run_ssh_command(ssh_host, deploy_cmd)
            
            if code != 0:
                progress.update(task, description=f"[yellow]⚠ {comp} may have issues")
            else:
                progress.update(task, description=f"[green]✓ {comp} deployed")
            
            progress.remove_task(task)
    
    console.print(f"\n[green]✓ Deployment complete![/green]")
    console.print("[dim]Run 'lich deploy status' to verify[/dim]")


@deploy_app.command(name="stage")
def deploy_stage(
    component: str = typer.Argument(..., help="Component to deploy (backend, web, admin, landing, all)"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version/tag to deploy"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without deploying"),
):
    """
    🚀 Deploy to staging environment.
    
    Examples:
        lich deploy stage admin
        lich deploy stage backend --version v1.2.3
        lich deploy stage all
    """
    _run_deploy("staging", component, version, dry_run)


@deploy_app.command(name="prod")
def deploy_prod(
    component: str = typer.Argument(..., help="Component to deploy (backend, web, admin, landing, all)"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version/tag to deploy"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without deploying"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """
    🚀 Deploy to production environment.
    
    Examples:
        lich deploy prod admin --version v1.2.3
        lich deploy prod all --force
    """
    if not force:
        confirm = Confirm.ask(f"[yellow]⚠️ Deploy {component} to PRODUCTION?[/yellow]")
        if not confirm:
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)
    
    _run_deploy("production", component, version, dry_run)


@deploy_app.command(name="logs")
def deploy_logs(
    environment: str = typer.Argument("production", help="Environment (staging, production)"),
    component: str = typer.Option("backend", "--component", "-c", help="Component to show logs for"),
    lines: int = typer.Option(100, "--lines", "-n", help="Number of lines to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
):
    """
    📜 View deployment logs.
    
    Examples:
        lich deploy logs production
        lich deploy logs staging -c web -f
    """
    _check_lich_project()
    
    config = _load_deploy_config()
    
    if environment not in config:
        console.print(f"[red]Environment '{environment}' not configured[/red]")
        raise typer.Exit(1)
    
    env_config = config[environment]
    
    if env_config.get("connection") == "ssh-config":
        ssh_host = env_config.get("ssh_name")
    else:
        ssh_host = f"{env_config.get('user')}@{env_config.get('host')}"
    
    deploy_path = env_config.get("path", "/opt/app")
    
    console.print(f"[dim]Connecting to {ssh_host}...[/dim]\n")
    
    follow_flag = "-f" if follow else ""
    log_cmd = f"cd {deploy_path} && docker-compose logs {follow_flag} --tail={lines} {component}"
    
    # Run interactively for follow mode
    ssh_cmd = ["ssh", "-t", ssh_host, log_cmd]
    subprocess.run(ssh_cmd)
