"""
lich shell - Interactive Python shell with project context.
"""
import sys
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def shell_command():
    """
    Start an interactive Python shell with project context.
    
    Uses IPython if available, falls back to standard Python REPL.
    """
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        raise typer.Exit(1)
    
    console.print("\n🐚 [bold blue]Lich Shell[/bold blue]\n")
    
    # Check for backend folder
    backend_path = Path("backend")
    if not backend_path.exists():
        console.print("[yellow]⚠️ Backend folder not found[/yellow]")
    
    # Prepare startup script
    startup_code = '''
import os
import sys

# Add backend to path
backend_path = "backend"
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)

print("🧙 Lich Shell - Python REPL with project context")
print("")
print("Available imports:")
print("  from internal.entities import *")
print("  from internal.services import *")
print("")
'''
    
    # Try IPython first
    try:
        import IPython
        console.print("[dim]Starting IPython...[/dim]\n")
        
        # Start IPython with backend in path
        sys.path.insert(0, str(backend_path))
        IPython.start_ipython(argv=[], user_ns={
            "__name__": "__main__",
        })
    except ImportError:
        # Fall back to standard Python
        console.print("[dim]IPython not found, using standard Python...[/dim]\n")
        console.print("[dim]Tip: pip install ipython for a better experience[/dim]\n")
        
        import code
        sys.path.insert(0, str(backend_path))
        code.interact(
            banner=startup_code,
            local={"__name__": "__main__"}
        )
