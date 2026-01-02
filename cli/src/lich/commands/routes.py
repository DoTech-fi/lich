"""
lich routes - List all API routes.
"""
import re
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def routes_command(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show more details"),
):
    """
    List all API routes in the project.
    
    Parses FastAPI routers and displays routes.
    """
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        raise typer.Exit(1)
    
    console.print("\n🛣️ [bold blue]API Routes[/bold blue]\n")
    
    # Find all router files
    api_path = Path("backend/api/http")
    if not api_path.exists():
        console.print("[yellow]No API routes found (backend/api/http/ missing)[/yellow]")
        raise typer.Exit(0)
    
    routes = []
    
    for py_file in api_path.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        
        try:
            content = py_file.read_text()
            routes.extend(_parse_fastapi_routes(py_file.name, content))
        except Exception as e:
            if verbose:
                console.print(f"[dim]Error parsing {py_file}: {e}[/dim]")
    
    if not routes:
        console.print("[yellow]No routes found[/yellow]")
        return
    
    # Display table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Method", style="green", width=8)
    table.add_column("Path", style="yellow")
    table.add_column("Function")
    table.add_column("File")
    
    for route in routes:
        method_style = {
            "GET": "green",
            "POST": "blue", 
            "PUT": "yellow",
            "DELETE": "red",
            "PATCH": "magenta",
        }.get(route["method"], "white")
        
        table.add_row(
            f"[{method_style}]{route['method']}[/{method_style}]",
            route["path"],
            route["function"],
            route["file"],
        )
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(routes)} routes[/dim]")


def _parse_fastapi_routes(filename: str, content: str) -> list:
    """Parse FastAPI routes from file content."""
    routes = []
    
    # Find router prefix
    prefix_match = re.search(r'prefix\s*=\s*["\']([^"\']+)["\']', content)
    prefix = prefix_match.group(1) if prefix_match else ""
    
    # Find route decorators
    # Match @router.get("/path"), @router.post("/path"), etc.
    pattern = r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
    
    for match in re.finditer(pattern, content, re.IGNORECASE):
        method = match.group(1).upper()
        path = match.group(2)
        
        # Find function name after decorator
        rest = content[match.end():]
        func_match = re.search(r'def\s+(\w+)\s*\(', rest)
        func_name = func_match.group(1) if func_match else "unknown"
        
        full_path = f"/api/v1{prefix}{path}"
        
        routes.append({
            "method": method,
            "path": full_path,
            "function": func_name,
            "file": filename,
        })
    
    return routes
