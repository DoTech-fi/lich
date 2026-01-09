"""
CI Utilities for act-based local CI.

Provides Docker/act checks and beautiful error handling.
"""
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown


console = Console()


def check_docker_running() -> bool:
    """
    Check if Docker daemon is running.
    
    Returns:
        True if Docker is running, False otherwise.
    """
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except subprocess.TimeoutExpired:
        return False


def show_docker_not_running_error():
    """Display a beautiful error when Docker is not running."""
    os_name = platform.system().lower()
    
    if os_name == "darwin":
        quick_start = "• **Mac**: Open Docker Desktop app"
    elif os_name == "linux":
        quick_start = "• **Linux**: `sudo systemctl start docker`"
    else:
        quick_start = "• **Windows**: Open Docker Desktop app"
    
    error_md = f"""
## 🐳 Docker is not running!

Please start Docker daemon first before running CI with `--act`.

### 💡 Quick Start

{quick_start}

### Then run your CI command again:

```bash
lich ci --act
```
"""
    
    console.print(Panel(
        Markdown(error_md),
        title="[red]Docker Required[/red]",
        border_style="red",
        padding=(1, 2),
    ))


def check_act_installed() -> bool:
    """
    Check if act is installed.
    
    Returns:
        True if act is installed, False otherwise.
    """
    return shutil.which("act") is not None


def show_act_not_installed_error():
    """Display a beautiful error when act is not installed."""
    os_name = platform.system().lower()
    
    if os_name == "darwin":
        install_cmd = "brew install act"
    elif os_name == "linux":
        install_cmd = "curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    else:
        install_cmd = "choco install act-cli"
    
    error_md = f"""
## 🎭 act is not installed!

**act** runs your GitHub Actions locally using Docker.

### 📦 Install act

```bash
{install_cmd}
```

### Or run setup:

```bash
lich ci setup
```

Learn more: https://github.com/nektos/act
"""
    
    console.print(Panel(
        Markdown(error_md),
        title="[yellow]act Required[/yellow]",
        border_style="yellow",
        padding=(1, 2),
    ))


def install_act() -> bool:
    """
    Install act based on the current OS.
    
    Returns:
        True if installation successful, False otherwise.
    """
    os_name = platform.system().lower()
    
    console.print("[dim]Installing act...[/dim]")
    
    try:
        if os_name == "darwin":
            # macOS - use Homebrew
            if not shutil.which("brew"):
                console.print("[red]Homebrew not found. Please install Homebrew first.[/red]")
                console.print("Visit: https://brew.sh")
                return False
            
            result = subprocess.run(
                ["brew", "install", "act"],
                capture_output=True,
                text=True,
            )
            
        elif os_name == "linux":
            # Linux - use install script
            result = subprocess.run(
                ["bash", "-c", "curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"],
                capture_output=True,
                text=True,
            )
            
        else:
            # Windows - use chocolatey or scoop
            if shutil.which("choco"):
                result = subprocess.run(
                    ["choco", "install", "act-cli", "-y"],
                    capture_output=True,
                    text=True,
                )
            elif shutil.which("scoop"):
                result = subprocess.run(
                    ["scoop", "install", "act"],
                    capture_output=True,
                    text=True,
                )
            else:
                console.print("[red]Please install Chocolatey or Scoop first.[/red]")
                return False
        
        if result.returncode == 0:
            console.print("[green]✓ act installed successfully![/green]")
            return True
        else:
            console.print(f"[red]Installation failed: {result.stderr}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]Installation error: {e}[/red]")
        return False


def get_github_token() -> Optional[str]:
    """
    Get GitHub token from environment or config.
    
    Returns:
        GitHub token if found, None otherwise.
    """
    # Check environment variable first
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    
    # Check .env file
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    
    # Check ~/.actrc
    actrc = Path.home() / ".actrc"
    if actrc.exists():
        with open(actrc) as f:
            for line in f:
                if line.startswith("-s GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip()
    
    return None


def is_arm_mac() -> bool:
    """
    Check if running on ARM Mac (M1/M2/M3).
    
    Returns:
        True if ARM Mac, False otherwise.
    """
    os_name = platform.system().lower()
    machine = platform.machine().lower()
    
    return os_name == "darwin" and machine in ("arm64", "aarch64")


def run_act_workflow(
    workflow: str = "ci.yml",
    job: Optional[str] = None,
    event: str = "push",
    reuse: bool = True,
    verbose: bool = False,
    quiet: bool = False,
    insecure_secrets: bool = False,
    secrets: Optional[list] = None,
    vars: Optional[list] = None,
) -> bool:
    """
    Run a GitHub Actions workflow locally using act.
    
    Args:
        workflow: Workflow file name (default: ci.yml)
        job: Specific job to run (optional)
        event: Event type (default: push)
        reuse: Reuse containers between runs (default: True)
        verbose: Enable verbose output
        quiet: Suppress output from steps
        insecure_secrets: Show secrets in logs (NOT RECOMMENDED)
        secrets: List of secrets in KEY=VALUE format
        vars: List of variables in KEY=VALUE format
        
    Returns:
        True if workflow passed, False otherwise.
    """
    # Build act command
    # Build act command
    # act -W .github/workflows/workflow.yml
    cmd = ["act", "-W", f".github/workflows/{workflow}"]
    
    # Only add event if explicitly provided and not default
    if event and event != "push":
        cmd.insert(1, event)
    
    if job:
        cmd.extend(["-j", job])
    
    # Add container architecture for ARM Macs (M1/M2/M3)
    if is_arm_mac():
        cmd.extend(["--container-architecture", "linux/amd64"])
        console.print("[dim]Detected ARM Mac - using linux/amd64 containers[/dim]")
    
    # Reuse containers between runs (faster)
    if reuse:
        cmd.append("--reuse")
    
    # Output control
    if verbose:
        cmd.append("--verbose")
    if quiet:
        cmd.append("--quiet")
    if insecure_secrets:
        cmd.append("--insecure-secrets")
        console.print("[yellow]⚠️ Secrets will be shown in logs![/yellow]")
    
    # Add inline secrets
    if secrets:
        for secret in secrets:
            cmd.extend(["-s", secret])
    
    # Add inline variables
    if vars:
        for var in vars:
            cmd.extend(["--var", var])
    
    # Add GitHub token if available (and not already provided)
    token = get_github_token()
    if token and not any(s.startswith("GITHUB_TOKEN=") for s in (secrets or [])):
        cmd.extend(["-s", f"GITHUB_TOKEN={token}"])
    
    # Check workflow file exists
    workflow_path = Path.cwd() / ".github" / "workflows" / workflow
    if not workflow_path.exists():
        console.print(f"[red]Workflow not found: {workflow_path}[/red]")
        return False
    
    cmd_str = " ".join(cmd)
    console.print(f"[dim]Running: {cmd_str}...[/dim]")
    
    try:
        result = subprocess.run(cmd, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        show_act_not_installed_error()
        return False


def ensure_act_ready() -> bool:
    """
    Ensure both Docker and act are ready.
    
    Returns:
        True if ready, False otherwise (with error displayed).
    """
    # Check Docker first
    if not check_docker_running():
        show_docker_not_running_error()
        return False
    
    # Check act
    if not check_act_installed():
        show_act_not_installed_error()
        return False
    
    return True
