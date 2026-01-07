"""
lich secret - Secret management commands.

Usage:
    lich secret generate            # Generate secure secrets
    lich secret rotate              # Rotate existing secrets
    lich secret check               # Check secret strength
"""
import secrets
import string
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

secret_app = typer.Typer(
    name="secret",
    help="🔐 Secret generation and management",
    no_args_is_help=True,
)


def _check_lich_project():
    """Check if we're in a Lich project."""
    if not (Path(".lich").exists() or Path("backend").exists()):
        console.print("[red]Error: Not in a Lich project directory[/red]")
        raise typer.Exit(1)


def _generate_secret(length: int = 32, charset: str = "alphanum") -> str:
    """Generate a cryptographically secure secret."""
    if charset == "alphanum":
        alphabet = string.ascii_letters + string.digits
    elif charset == "hex":
        return secrets.token_hex(length // 2)
    elif charset == "urlsafe":
        return secrets.token_urlsafe(length)
    else:
        alphabet = string.ascii_letters + string.digits + string.punctuation
    
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _read_env_file(env_path: Path) -> dict:
    """Read environment file into a dict."""
    env_vars = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                env_vars[key.strip()] = value.strip()
    return env_vars


def _write_env_file(env_path: Path, env_vars: dict):
    """Write dict back to environment file."""
    lines = []
    for key, value in env_vars.items():
        lines.append(f"{key}={value}")
    env_path.write_text('\n'.join(lines) + '\n')


@secret_app.command(name="generate")
def generate_secrets(
    length: int = typer.Option(32, "--length", "-l", help="Secret length"),
    count: int = typer.Option(1, "--count", "-c", help="Number of secrets to generate"),
    format: str = typer.Option("hex", "--format", "-f", help="Format: hex, alphanum, urlsafe, full"),
    copy: bool = typer.Option(False, "--copy", help="Copy to clipboard (requires pyperclip)"),
):
    """
    🎲 Generate cryptographically secure secrets.
    
    Examples:
        lich secret generate                    # Single hex secret
        lich secret generate -l 64 -c 3         # 3 secrets, 64 chars
        lich secret generate -f urlsafe         # URL-safe format
    """
    console.print(Panel.fit("🔐 Secret Generator", style="bold blue"))
    
    table = Table()
    table.add_column("#", style="dim")
    table.add_column("Secret", style="green")
    table.add_column("Length", style="cyan")
    
    generated = []
    for i in range(count):
        secret = _generate_secret(length, format)
        generated.append(secret)
        table.add_row(str(i + 1), secret, str(len(secret)))
    
    console.print(table)
    
    if copy and count == 1:
        try:
            import pyperclip
            pyperclip.copy(generated[0])
            console.print("\n[green]✓ Copied to clipboard[/green]")
        except ImportError:
            console.print("\n[yellow]Install pyperclip to use --copy: pip install pyperclip[/yellow]")


@secret_app.command(name="rotate")
def rotate_secrets(
    env_file: str = typer.Option(".env", "--env", "-e", help="Environment file to update"),
    key: str = typer.Option(None, "--key", "-k", help="Specific key to rotate (default: all secrets)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change"),
):
    """
    🔄 Rotate secrets in your environment file.
    
    By default, rotates common secret keys like SECRET_KEY, JWT_SECRET_KEY.
    
    Examples:
        lich secret rotate                      # Rotate all secrets
        lich secret rotate --key JWT_SECRET    # Rotate specific key
        lich secret rotate --dry-run            # Preview changes
    """
    _check_lich_project()
    
    env_path = Path(env_file)
    if not env_path.exists():
        console.print(f"[red]Environment file not found: {env_file}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel.fit("🔄 Secret Rotation", style="bold blue"))
    
    # Common secret key patterns
    secret_patterns = [
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "JWT_SECRET",
        "API_SECRET",
        "ENCRYPTION_KEY",
        "SESSION_SECRET",
    ]
    
    env_vars = _read_env_file(env_path)
    rotated = []
    
    for var_key, var_value in env_vars.items():
        should_rotate = False
        
        if key:
            # Specific key requested
            should_rotate = var_key == key
        else:
            # Check if it matches secret patterns
            should_rotate = any(pattern in var_key.upper() for pattern in secret_patterns)
        
        if should_rotate:
            new_secret = _generate_secret(32, "hex")
            if dry_run:
                console.print(f"  [yellow]Would rotate:[/yellow] {var_key}")
                console.print(f"    [dim]Old: {var_value[:20]}...[/dim]")
                console.print(f"    [green]New: {new_secret[:20]}...[/green]")
            else:
                env_vars[var_key] = new_secret
                rotated.append(var_key)
    
    if not dry_run and rotated:
        _write_env_file(env_path, env_vars)
        console.print(f"\n[green]✓ Rotated {len(rotated)} secret(s)[/green]")
        for key in rotated:
            console.print(f"  - {key}")
        console.print("\n[yellow]⚠ Remember to restart your services![/yellow]")
    elif dry_run and rotated:
        console.print(f"\n[blue]Would rotate {len(rotated)} secret(s)[/blue]")
    elif not rotated:
        console.print("[yellow]No secrets found to rotate[/yellow]")


@secret_app.command(name="check")
def check_secrets(
    env_file: str = typer.Option(".env", "--env", "-e", help="Environment file to check"),
):
    """
    🔍 Check secret strength and security issues.
    
    Scans for:
    - Weak or default secrets
    - Short secrets (< 32 chars)
    - Common patterns
    """
    _check_lich_project()
    
    env_path = Path(env_file)
    if not env_path.exists():
        console.print(f"[red]Environment file not found: {env_file}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel.fit("🔍 Secret Security Check", style="bold blue"))
    
    # Weak patterns to check for
    weak_patterns = [
        "changeme", "change_me", "change-me",
        "secret", "password", "your-",
        "example", "test", "demo",
        "123456", "qwerty", "admin",
    ]
    
    env_vars = _read_env_file(env_path)
    issues = []
    
    secret_keys = [k for k in env_vars if any(
        p in k.upper() for p in ["SECRET", "KEY", "PASSWORD", "TOKEN"]
    )]
    
    for key in secret_keys:
        value = env_vars[key].lower()
        
        # Check length
        if len(env_vars[key]) < 32:
            issues.append({
                "key": key,
                "severity": "warning",
                "message": f"Secret is short ({len(env_vars[key])} chars, recommend 32+)"
            })
        
        # Check for weak patterns
        for pattern in weak_patterns:
            if pattern in value:
                issues.append({
                    "key": key,
                    "severity": "critical",
                    "message": f"Contains weak pattern: '{pattern}'"
                })
                break
    
    if issues:
        table = Table(title="Security Issues Found")
        table.add_column("Key", style="cyan")
        table.add_column("Severity", style="red")
        table.add_column("Issue")
        
        for issue in issues:
            severity_style = "red bold" if issue["severity"] == "critical" else "yellow"
            table.add_row(
                issue["key"],
                f"[{severity_style}]{issue['severity'].upper()}[/]",
                issue["message"]
            )
        
        console.print(table)
        console.print("\n[yellow]Run 'lich secret rotate' to fix these issues[/yellow]")
        raise typer.Exit(1)
    else:
        console.print("[green]✓ All secrets look good![/green]")
