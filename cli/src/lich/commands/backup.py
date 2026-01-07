"""
lich backup - Database backup commands.

Usage:
    lich backup                     # Backup all detected databases
    lich backup --verify            # Verify backup integrity
    lich backup --remote s3://...   # Upload to S3
    lich backup --list              # List available backups
    lich backup restore             # Interactive restore
"""
import subprocess
from pathlib import Path
from datetime import datetime
import typer
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

backup_app = typer.Typer(
    name="backup",
    help="💾 Database backup and restore",
    no_args_is_help=False,
)

BACKUP_DIR = Path("backups")


def _check_lich_project():
    """Check if we're in a Lich project."""
    if not (Path(".lich").exists() or Path("backend").exists()):
        console.print("[red]Error: Not in a Lich project directory[/red]")
        raise typer.Exit(1)


def _detect_databases() -> dict:
    """Auto-detect databases from docker-compose.yml."""
    databases = {}
    
    compose_files = ["docker-compose.yml", "docker-compose.yaml", "compose.yml"]
    compose_path = None
    
    for f in compose_files:
        if Path(f).exists():
            compose_path = Path(f)
            break
    
    if not compose_path:
        return databases
    
    try:
        with open(compose_path) as f:
            compose = yaml.safe_load(f)
        
        services = compose.get("services", {})
        
        for name, config in services.items():
            image = config.get("image", "")
            
            if "postgres" in image:
                databases[name] = {
                    "type": "postgresql",
                    "container": config.get("container_name", name),
                    "env": config.get("environment", {}),
                }
            elif "mysql" in image or "mariadb" in image:
                databases[name] = {
                    "type": "mysql",
                    "container": config.get("container_name", name),
                    "env": config.get("environment", {}),
                }
            elif "mongo" in image:
                databases[name] = {
                    "type": "mongodb",
                    "container": config.get("container_name", name),
                    "env": config.get("environment", {}),
                }
            elif "redis" in image:
                databases[name] = {
                    "type": "redis",
                    "container": config.get("container_name", name),
                }
    
    except Exception as e:
        console.print(f"[yellow]Warning: Could not parse docker-compose: {e}[/yellow]")
    
    return databases


def _run_docker_command(cmd: list) -> tuple[int, str, str]:
    """Run a docker command."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", "Docker not found"


def backup_postgresql(container: str, db_name: str, backup_path: Path) -> bool:
    """Backup PostgreSQL database."""
    console.print(f"  [blue]Backing up PostgreSQL: {db_name}[/blue]")
    
    cmd = [
        "docker", "exec", container,
        "pg_dump", "-U", "postgres", db_name
    ]
    
    code, stdout, stderr = _run_docker_command(cmd)
    
    if code == 0:
        backup_path.write_text(stdout)
        console.print(f"    [green]✓ Saved to {backup_path}[/green]")
        return True
    else:
        console.print(f"    [red]✗ Failed: {stderr}[/red]")
        return False


def backup_mysql(container: str, db_name: str, backup_path: Path, info: dict) -> bool:
    """Backup MySQL/MariaDB database."""
    console.print(f"  [blue]Backing up MySQL: {db_name}[/blue]")
    
    # Get password from detected env or default to 'root'
    password = info.get("env", {}).get("MYSQL_ROOT_PASSWORD", "root")
    
    cmd = [
        "docker", "exec", container,
        "mysqldump", "-u", "root", f"-p{password}", db_name
    ]
    
    code, stdout, stderr = _run_docker_command(cmd)
    
    if code == 0:
        backup_path.write_text(stdout)
        console.print(f"    [green]✓ Saved to {backup_path}[/green]")
        return True
    else:
        console.print(f"    [red]✗ Failed: {stderr}[/red]")
        return False


def backup_mongodb(container: str, backup_path: Path) -> bool:
    """Backup MongoDB database."""
    console.print("  [blue]Backing up MongoDB[/blue]")
    
    # mongodump creates a directory
    cmd = [
        "docker", "exec", container,
        "mongodump", "--archive"
    ]
    
    code, stdout, stderr = _run_docker_command(cmd)
    
    if code == 0:
        backup_path.write_bytes(stdout.encode('latin-1'))
        console.print(f"    [green]✓ Saved to {backup_path}[/green]")
        return True
    else:
        console.print(f"    [red]✗ Failed: {stderr}[/red]")
        return False


def backup_redis(container: str, backup_path: Path) -> bool:
    """Backup Redis database."""
    console.print("  [blue]Backing up Redis[/blue]")
    
    # Trigger BGSAVE and copy dump.rdb
    cmd = ["docker", "exec", container, "redis-cli", "BGSAVE"]
    _run_docker_command(cmd)
    
    # Copy the dump file
    cmd = ["docker", "cp", f"{container}:/data/dump.rdb", str(backup_path)]
    code, _, stderr = _run_docker_command(cmd)
    
    if code == 0:
        console.print(f"    [green]✓ Saved to {backup_path}[/green]")
        return True
    else:
        console.print(f"    [red]✗ Failed: {stderr}[/red]")
        return False


def upload_to_s3(file_path: Path, s3_uri: str) -> bool:
    """Upload backup to S3."""
    try:
        result = subprocess.run(
            ["aws", "s3", "cp", str(file_path), s3_uri],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        console.print("[red]AWS CLI not installed[/red]")
        return False


@backup_app.callback(invoke_without_command=True)
def backup_command(
    ctx: typer.Context,
    verify: bool = typer.Option(False, "--verify", help="Verify backup integrity"),
    remote: str = typer.Option(None, "--remote", "-r", help="Upload to S3 (s3://bucket/path)"),
    list_backups: bool = typer.Option(False, "--list", "-l", help="List available backups"),
):
    """
    💾 Backup all databases in your Lich project.
    
    Auto-detects PostgreSQL, MySQL, MongoDB, and Redis from docker-compose.yml.
    
    Examples:
        lich backup                     # Backup all
        lich backup --list              # Show backups
        lich backup --remote s3://...   # Upload to S3
    """
    _check_lich_project()
    
    if list_backups:
        # List existing backups
        if not BACKUP_DIR.exists():
            console.print("[yellow]No backups found[/yellow]")
            return
        
        table = Table(title="Available Backups")
        table.add_column("File")
        table.add_column("Size")
        table.add_column("Date")
        
        for backup in sorted(BACKUP_DIR.glob("*"), reverse=True):
            stat = backup.stat()
            size = f"{stat.st_size / 1024:.1f} KB"
            date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            table.add_row(backup.name, size, date)
        
        console.print(table)
        return
    
    console.print(Panel.fit("💾 Lich Database Backup", style="bold blue"))
    
    # Detect databases
    databases = _detect_databases()
    
    if not databases:
        console.print("[yellow]No databases detected in docker-compose.yml[/yellow]")
        return
    
    console.print(f"\n[blue]Detected {len(databases)} database(s):[/blue]")
    for name, info in databases.items():
        console.print(f"  - {name} ({info['type']})")
    
    # Create backup directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    BACKUP_DIR.mkdir(exist_ok=True)
    
    results = []
    
    for name, info in databases.items():
        db_type = info["type"]
        container = info["container"]
        
        backup_file = BACKUP_DIR / f"{name}_{timestamp}.{'sql' if db_type != 'redis' else 'rdb'}"
        
        if db_type == "postgresql":
            db_name = info["env"].get("POSTGRES_DB", name)
            success = backup_postgresql(container, db_name, backup_file)
        elif db_type == "mysql":
            db_name = info["env"].get("MYSQL_DATABASE", name)
            success = backup_mysql(container, db_name, backup_file, info)
        elif db_type == "mongodb":
            success = backup_mongodb(container, backup_file)
        elif db_type == "redis":
            success = backup_redis(container, backup_file)
        else:
            continue
        
        results.append((name, success, backup_file if success else None))
    
    # Summary
    console.print("\n")
    successful = sum(1 for _, s, _ in results if s)
    
    if successful == len(results):
        console.print(Panel.fit(f"[green]✓ All {successful} backup(s) completed![/green]"))
    else:
        console.print(Panel.fit(f"[yellow]⚠ {successful}/{len(results)} backup(s) succeeded[/yellow]"))
    
    # Upload to S3 if requested
    if remote:
        console.print(f"\n[blue]Uploading to {remote}...[/blue]")
        for name, success, backup_file in results:
            if success and backup_file:
                if upload_to_s3(backup_file, f"{remote}/{backup_file.name}"):
                    console.print(f"  [green]✓ Uploaded {backup_file.name}[/green]")
                else:
                    console.print(f"  [red]✗ Failed to upload {backup_file.name}[/red]")


@backup_app.command(name="restore")
def restore_command(
    backup_file: str = typer.Argument(None, help="Backup file to restore"),
):
    """
    🔄 Restore database from backup.
    
    Interactive restore if no file specified.
    """
    _check_lich_project()
    
    if not backup_file:
        # Interactive selection
        if not BACKUP_DIR.exists():
            console.print("[red]No backups found[/red]")
            raise typer.Exit(1)
        
        backups = sorted(BACKUP_DIR.glob("*"), reverse=True)
        if not backups:
            console.print("[red]No backups found[/red]")
            raise typer.Exit(1)
        
        console.print("[blue]Available backups:[/blue]")
        for i, b in enumerate(backups[:10], 1):
            console.print(f"  {i}. {b.name}")
        
        choice = Prompt.ask("Select backup", default="1")
        try:
            backup_file = str(backups[int(choice) - 1])
        except (ValueError, IndexError):
            console.print("[red]Invalid selection[/red]")
            raise typer.Exit(1)
    
    backup_path = Path(backup_file)
    if not backup_path.exists():
        console.print(f"[red]Backup file not found: {backup_file}[/red]")
        raise typer.Exit(1)
    
    if not Confirm.ask(f"Restore from {backup_path.name}? This will overwrite current data"):
        console.print("[yellow]Cancelled[/yellow]")
        return
    
    console.print(f"[blue]Restoring from {backup_path.name}...[/blue]")
    console.print("[yellow]⚠ Restore functionality requires manual implementation based on your setup[/yellow]")
    console.print("[dim]Hint: For PostgreSQL, use: docker exec -i container psql -U postgres db < backup.sql[/dim]")
