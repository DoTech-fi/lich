"""
Dev commands for local development orchestration.
"""
import os
import sys
import time
import signal
import subprocess
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="Manage local development environment")
console = Console()

PID_DIR = Path(".pids")
LOG_DIR = Path(".logs")

def _check_port(port: int) -> bool:
    """Check if a port is in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def _kill_port(port: int):
    """Kill process listening on port."""
    try:
        # lsof -ti :port
        result = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(["kill", "-9", pid], check=False)
            console.print(f"[green]✅ Freed port {port}[/green]")
    except Exception:
        pass

def _ensure_dirs():
    PID_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

def _start_process(name: str, cmd: list, cwd: str, env=None):
    """Start a background process and save PID."""
    log_file = LOG_DIR / f"{name}.log"
    pid_file = PID_DIR / f"{name}.pid"
    
    with open(log_file, "w") as out:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=out,
            stderr=subprocess.STDOUT,
            env=env,
            preexec_fn=os.setsid  # Create new process group
        )
    
    with open(pid_file, "w") as f:
        f.write(str(process.pid))
        
    return process

@app.command("start")
def start_dev(
    force: bool = typer.Option(False, "--force", "-f", help="Force kill usage ports")
):
    """Start the full development environment (Docker, Backend, Frontend)."""
    console.print(Panel("🚀 Starting Development Environment", style="bold blue"))
    _ensure_dirs()

    # 1. Check Docker
    if subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        console.print("[bold red]❌ Docker is not running![/bold red]")
        raise typer.Exit(1)

    # 2. Check Ports
    ports = {8000: "Backend", 3000: "Web App", 3002: "Admin", 4321: "Landing"}
    for port, name in ports.items():
        if _check_port(port):
            if force or typer.confirm(f"⚠️  Port {port} ({name}) is in use. Kill process?"):
                _kill_port(port)
            else:
                console.print(f"[red]Cannot start with port {port} in use[/red]")
                raise typer.Exit(1)

    # 3. Start Docker Compose
    console.print("\n[bold green]📦 Starting Docker services...[/bold green]")
    # Check for docker-compose.yml
    if not Path("docker-compose.yml").exists():
        console.print("[red]❌ docker-compose.yml not found![/red]")
        raise typer.Exit(1)
        
    subprocess.run(["docker-compose", "up", "-d", "postgres", "redis", "adminer"], check=False)
    
    # Wait for DB
    console.print("⏳ Waiting for database...")
    # Simple sleep for now, better to use pg_isready if available
    time.sleep(3) 

    # 4. Start Backend
    console.print("\n[bold green]🐍 Starting Backend...[/bold green]")
    backend_dir = Path("backend")
    if not backend_dir.exists():
        console.print("[red]backend directory not found[/red]")
    else:
        # Venv check
        venv_python = backend_dir / "venv" / "bin" / "python"
        if not venv_python.exists():
            console.print("   Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=backend_dir)
            subprocess.run(["./venv/bin/pip", "install", "-r", "requirements.txt", "-q"], cwd=backend_dir)
        
        # Copy .env
        if not (backend_dir / ".env").exists() and (backend_dir / ".env.example").exists():
            import shutil
            shutil.copy(backend_dir / ".env.example", backend_dir / ".env")

        env = os.environ.copy()
        _start_process("backend", ["./venv/bin/python", "main.py"], str(backend_dir), env)
        
        # Seed DB
        console.print("[green]🌱 Seeding Database...[/green]")
        subprocess.run(["./venv/bin/python", "scripts/seed_db.py"], cwd=backend_dir, check=False)

    # 5. Start Frontends
    apps_dir = Path("apps")
    for app_name, port in [("web", 3000), ("admin", 3002), ("landing", 4321)]:
        app_path = apps_dir / app_name
        if app_path.exists():
            console.print(f"\n[bold green]⚛️  Starting {app_name.title()}...[/bold green]")
            if not (app_path / "node_modules").exists():
                 console.print("   Installing dependencies...")
                 subprocess.run(["npm", "install", "--silent"], cwd=app_path)
            
            _start_process(app_name, ["npm", "run", "dev"], str(app_path))

    console.print("\n[bold green]✅ All services started![/bold green]")
    console.print("📁 Logs are in .logs/ directory")
    console.print("🛑 Run 'lich dev stop' to stop environment")

@app.command("stop")
def stop_dev(
    docker: bool = typer.Option(False, "--docker", "-d", help="Also stop docker containers")
):
    """Stop all running development services."""
    console.print(Panel("🛑 Stopping Development Environment", style="bold red"))

    # 1. Kill PIDs
    if PID_DIR.exists():
        for pid_file in PID_DIR.glob("*.pid"):
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, signal.SIGTERM)
                console.print(f"Killed process {pid} ({pid_file.stem})")
            except ProcessLookupError:
                pass
            except Exception as e:
                console.print(f"Error killing {pid_file}: {e}")
            finally:
                pid_file.unlink()

    # 2. Cleanup Ports (fallback)
    _kill_port(8000)
    _kill_port(3000)
    _kill_port(3002)
    _kill_port(4321)

    # 3. Docker
    if docker or typer.confirm("Stop Docker services?"):
        console.print("Stopping Docker services...")
        subprocess.run(["docker-compose", "down"], check=False)

    console.print("[bold green]✅ Environment Stopped[/bold green]")

if __name__ == "__main__":
    app()
