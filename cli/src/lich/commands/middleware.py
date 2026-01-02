"""
Lich Middleware Commands - List, enable, and disable middlewares.
"""
import re
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()
middleware_app = typer.Typer(
    name="middleware",
    help="Manage API middlewares",
    no_args_is_help=True,
)


# Available middlewares (must match main.py comments)
MIDDLEWARES = {
    "timing": {
        "name": "TimingMiddleware",
        "import": "from api.middleware.timing import TimingMiddleware",
        "add": "app.add_middleware(TimingMiddleware)",
        "description": "Add response time headers",
    },
    "security": {
        "name": "SecurityHeadersMiddleware",
        "import": "from api.middleware.security import SecurityHeadersMiddleware",
        "add": "app.add_middleware(SecurityHeadersMiddleware)",
        "description": "OWASP security headers",
    },
    "logging": {
        "name": "RequestLoggingMiddleware",
        "import": "from api.middleware.logging import RequestLoggingMiddleware",
        "add": "app.add_middleware(RequestLoggingMiddleware)",
        "description": "Log all requests with timing",
    },
    "rate_limit": {
        "name": "RateLimitMiddleware",
        "import": "from api.middleware.rate_limit import RateLimitMiddleware",
        "add": "app.add_middleware(RateLimitMiddleware, requests_per_minute=60)",
        "description": "Prevent API abuse",
    },
}


def _is_lich_project() -> bool:
    """Check if current directory is a Lich project."""
    return Path(".lich").exists() or Path("backend/main.py").exists()


def _get_main_py_path() -> Path:
    """Get path to main.py."""
    return Path("backend/main.py")


def _read_main_py() -> str:
    """Read main.py content."""
    path = _get_main_py_path()
    if not path.exists():
        return ""
    return path.read_text()


def _write_main_py(content: str) -> None:
    """Write main.py content."""
    path = _get_main_py_path()
    path.write_text(content)


def _is_middleware_enabled(content: str, middleware_key: str) -> bool:
    """Check if a middleware is enabled (not commented out)."""
    mw = MIDDLEWARES[middleware_key]
    # Check if import is not commented
    import_pattern = rf'^{re.escape(mw["import"])}'
    has_import = bool(re.search(import_pattern, content, re.MULTILINE))
    return has_import


@middleware_app.command("list")
def list_middlewares():
    """
    List all available middlewares and their status.
    
    Example:
        lich middleware list
    """
    if not _is_lich_project():
        console.print("[red]❌ Not a Lich project. Run this in a Lich project directory.[/red]")
        raise typer.Exit(1)
    
    content = _read_main_py()
    if not content:
        console.print("[red]❌ Cannot find backend/main.py[/red]")
        raise typer.Exit(1)
    
    console.print("\n[bold]📦 Available Middlewares:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Status", width=8)
    table.add_column("Name", width=25)
    table.add_column("Description", width=35)
    
    # CORS is always enabled
    table.add_row("✅", "CORSMiddleware", "Cross-Origin Resource Sharing (always on)")
    
    for key, mw in MIDDLEWARES.items():
        enabled = _is_middleware_enabled(content, key)
        status = "✅" if enabled else "❌"
        table.add_row(status, mw["name"], mw["description"])
    
    console.print(table)
    console.print("\n[dim]To enable/disable: lich middleware enable <name> | lich middleware disable <name>[/dim]")


@middleware_app.command("enable")
def enable_middleware(
    name: str = typer.Argument(..., help="Middleware name: timing, security, logging, rate_limit"),
):
    """
    Enable a middleware by uncommenting it in main.py.
    
    Examples:
        lich middleware enable timing
        lich middleware enable security
        lich middleware enable logging
        lich middleware enable rate_limit
    """
    if not _is_lich_project():
        console.print("[red]❌ Not a Lich project.[/red]")
        raise typer.Exit(1)
    
    name = name.lower().replace("-", "_")
    if name not in MIDDLEWARES:
        console.print(f"[red]❌ Unknown middleware: {name}[/red]")
        console.print(f"[dim]Available: {', '.join(MIDDLEWARES.keys())}[/dim]")
        raise typer.Exit(1)
    
    content = _read_main_py()
    mw = MIDDLEWARES[name]
    
    if _is_middleware_enabled(content, name):
        console.print(f"[yellow]⚠️ {mw['name']} is already enabled[/yellow]")
        return
    
    # Uncomment the import
    content = content.replace(f"# {mw['import']}", mw["import"])
    
    # Uncomment the add_middleware
    content = content.replace(f"# {mw['add']}", mw["add"])
    
    _write_main_py(content)
    console.print(f"[green]✅ {mw['name']} enabled![/green]")
    console.print("[dim]File updated: backend/main.py[/dim]")


@middleware_app.command("disable")
def disable_middleware(
    name: str = typer.Argument(..., help="Middleware name: timing, security, logging, rate_limit"),
):
    """
    Disable a middleware by commenting it out in main.py.
    
    Examples:
        lich middleware disable timing
        lich middleware disable rate_limit
    """
    if not _is_lich_project():
        console.print("[red]❌ Not a Lich project.[/red]")
        raise typer.Exit(1)
    
    name = name.lower().replace("-", "_")
    if name not in MIDDLEWARES:
        console.print(f"[red]❌ Unknown middleware: {name}[/red]")
        console.print(f"[dim]Available: {', '.join(MIDDLEWARES.keys())}[/dim]")
        raise typer.Exit(1)
    
    content = _read_main_py()
    mw = MIDDLEWARES[name]
    
    if not _is_middleware_enabled(content, name):
        console.print(f"[yellow]⚠️ {mw['name']} is already disabled[/yellow]")
        return
    
    # Comment out the import (only if not already commented)
    content = re.sub(
        rf'^({re.escape(mw["import"])})$',
        r'# \1',
        content,
        flags=re.MULTILINE
    )
    
    # Comment out the add_middleware (only if not already commented)
    content = re.sub(
        rf'^({re.escape(mw["add"])})$',
        r'# \1',
        content,
        flags=re.MULTILINE
    )
    
    _write_main_py(content)
    console.print(f"[green]✅ {mw['name']} disabled![/green]")
    console.print("[dim]File updated: backend/main.py[/dim]")


@middleware_app.command("enable-all")
def enable_all_middlewares():
    """
    Enable all available middlewares.
    
    Example:
        lich middleware enable-all
    """
    if not _is_lich_project():
        console.print("[red]❌ Not a Lich project.[/red]")
        raise typer.Exit(1)
    
    for name in MIDDLEWARES:
        enable_middleware(name)


@middleware_app.command("disable-all")
def disable_all_middlewares():
    """
    Disable all optional middlewares.
    
    Example:
        lich middleware disable-all
    """
    if not _is_lich_project():
        console.print("[red]❌ Not a Lich project.[/red]")
        raise typer.Exit(1)
    
    for name in MIDDLEWARES:
        disable_middleware(name)
