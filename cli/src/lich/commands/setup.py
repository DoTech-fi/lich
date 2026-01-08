"""
Lich Setup Command - Configure AI tools for MCP integration.

Supports: Antigravity (Gemini CLI), Claude Desktop, Cursor, VS Code
Cross-platform: macOS, Linux, Windows
"""
import json
import os
import platform
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

setup_app = typer.Typer(
    name="setup",
    help="🔧 Configure AI tools for Lich MCP integration",
    no_args_is_help=False,
)

console = Console()

# ============================================================================
# Path Configuration (Cross-platform)
# ============================================================================

def get_os_type() -> str:
    """Detect operating system."""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    elif system == "Windows":
        return "windows"
    return "unknown"


def get_home_dir() -> Path:
    """Get user home directory."""
    return Path.home()


    """Get Antigravity (Gemini CLI) config path."""
    home = get_home_dir()
    # Antigravity reads MCP config from ~/.gemini/antigravity/mcp_config.json
    return home / ".gemini" / "antigravity" / "mcp_config.json"


def get_claude_config_path() -> Path:
    """Get Claude Desktop config path."""
    home = get_home_dir()
    os_type = get_os_type()
    
    if os_type == "windows":
        appdata = os.environ.get("APPDATA", str(home / "AppData" / "Roaming"))
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    else:
        return home / ".claude" / "claude_desktop_config.json"


def get_cursor_config_path() -> Path:
    """Get Cursor config path (project-level)."""
    return Path.cwd() / ".cursor" / "mcp.json"


def get_vscode_config_path() -> Path:
    """Get VS Code config path (project-level)."""
    return Path.cwd() / ".vscode" / "mcp.json"


# ============================================================================
# Lich MCP Configuration Templates
# ============================================================================

def get_lich_executable_path() -> str:
    """Get the full path to lich executable.
    
    This is important because AI tools (Antigravity, Claude, etc.) may not
    have access to pyenv shims or other shell environment customizations.
    """
    lich_path = shutil.which("lich")
    if lich_path:
        return lich_path
    # Fallback to just "lich" if which fails
    return "lich"


def get_lich_mcp_config_antigravity() -> dict:
    """Lich MCP config for Antigravity."""
    lich_cmd = get_lich_executable_path()
    return {
        "mcpServers": {
            "lich": {
                "command": lich_cmd,
                "args": ["serve"],
                "transportType": "stdio"
            }
        }
    }


def get_lich_mcp_config_claude() -> dict:
    """Lich MCP config for Claude Desktop."""
    lich_cmd = get_lich_executable_path()
    return {
        "mcpServers": {
            "lich": {
                "command": lich_cmd,
                "args": ["serve"]
            }
        }
    }


def get_lich_mcp_config_cursor() -> dict:
    """Lich MCP config for Cursor."""
    lich_cmd = get_lich_executable_path()
    return {
        "mcpServers": {
            "lich": {
                "command": lich_cmd,
                "args": ["serve"]
            }
        }
    }


def get_lich_mcp_config_vscode() -> dict:
    """Lich MCP config for VS Code."""
    lich_cmd = get_lich_executable_path()
    return {
        "servers": {
            "lich": {
                "command": lich_cmd,
                "args": ["serve"],
                "type": "stdio"
            }
        }
    }


# ============================================================================
# Config Merging & File Operations
# ============================================================================

def backup_config(config_path: Path) -> Optional[Path]:
    """Create backup of existing config."""
    if config_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config_path.with_suffix(f".backup_{timestamp}.json")
        shutil.copy2(config_path, backup_path)
        return backup_path
    return None


def merge_mcp_config(existing: dict, new_config: dict) -> dict:
    """Merge Lich MCP config into existing config without overwriting other servers."""
    result = existing.copy()
    
    # Handle mcpServers key (Antigravity, Claude, Cursor)
    if "mcpServers" in new_config:
        if "mcpServers" not in result:
            result["mcpServers"] = {}
        result["mcpServers"]["lich"] = new_config["mcpServers"]["lich"]
    
    # Handle servers key (VS Code)
    if "servers" in new_config:
        if "servers" not in result:
            result["servers"] = {}
        result["servers"]["lich"] = new_config["servers"]["lich"]
    
    return result


def write_config(config_path: Path, config: dict, tool_name: str) -> bool:
    """Write config to file, creating directories if needed."""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        console.print(f"✅ Configured {tool_name} at [cyan]{config_path}[/cyan]")
        return True
    except Exception as e:
        console.print(f"❌ Failed to configure {tool_name}: {e}", style="red")
        return False


def configure_tool(config_path: Path, new_config: dict, tool_name: str) -> bool:
    """Configure a single AI tool."""
    # Read existing config
    existing = {}
    if config_path.exists():
        try:
            with open(config_path) as f:
                existing = json.load(f)
            # Check if already configured
            if "mcpServers" in existing and "lich" in existing.get("mcpServers", {}):
                console.print(f"ℹ️  {tool_name} already configured (updating)", style="yellow")
            if "servers" in existing and "lich" in existing.get("servers", {}):
                console.print(f"ℹ️  {tool_name} already configured (updating)", style="yellow")
            # Backup
            backup_path = backup_config(config_path)
            if backup_path:
                console.print(f"📦 Backup created: [dim]{backup_path}[/dim]")
        except json.JSONDecodeError:
            console.print("⚠️  Existing config is invalid, will overwrite", style="yellow")
    
    # Merge and write
    merged = merge_mcp_config(existing, new_config)
    return write_config(config_path, merged, tool_name)


# ============================================================================
# CLI Commands
# ============================================================================

@setup_app.callback(invoke_without_command=True)
def setup_interactive(ctx: typer.Context):
    """
    🔧 Configure AI tools for Lich MCP integration (interactive mode).
    """
    if ctx.invoked_subcommand is not None:
        return
    
    console.print(Panel.fit(
        "🔧 [bold]Lich MCP Setup[/bold]\n\n"
        "Configure your AI tools to use Lich's 47+ MCP tools.",
        border_style="cyan"
    ))
    
    # Show detected OS
    os_type = get_os_type()
    os_display = {"macos": "macOS", "linux": "Linux", "windows": "Windows"}.get(os_type, os_type)
    console.print(f"\n📍 Detected OS: [bold]{os_display}[/bold]")
    
    # Tool selection
    console.print("\n[bold]Which AI tool do you want to configure?[/bold]\n")
    console.print("  [1] Antigravity (Google Gemini CLI)")
    console.print("  [2] Claude Desktop")
    console.print("  [3] Cursor")
    console.print("  [4] VS Code")
    console.print("  [5] All of the above")
    console.print()
    
    choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"], default="1")
    
    console.print()
    
    if choice == "1":
        configure_antigravity()
    elif choice == "2":
        configure_claude()
    elif choice == "3":
        configure_cursor()
    elif choice == "4":
        configure_vscode()
    elif choice == "5":
        configure_all()
    
    console.print("\n[dim]ℹ️  Restart your AI tool to activate Lich MCP[/dim]")


@setup_app.command("antigravity")
def configure_antigravity():
    """Configure Antigravity (Google Gemini CLI)."""
    config_path = get_antigravity_config_path()
    new_config = get_lich_mcp_config_antigravity()
    configure_tool(config_path, new_config, "Antigravity")


@setup_app.command("claude")
def configure_claude():
    """Configure Claude Desktop."""
    config_path = get_claude_config_path()
    new_config = get_lich_mcp_config_claude()
    configure_tool(config_path, new_config, "Claude Desktop")


@setup_app.command("cursor")
def configure_cursor():
    """Configure Cursor (project-level)."""
    config_path = get_cursor_config_path()
    new_config = get_lich_mcp_config_cursor()
    configure_tool(config_path, new_config, "Cursor")
    console.print(f"[dim]   (Config is project-specific: {config_path})[/dim]")


@setup_app.command("vscode")
def configure_vscode():
    """Configure VS Code (project-level)."""
    config_path = get_vscode_config_path()
    new_config = get_lich_mcp_config_vscode()
    configure_tool(config_path, new_config, "VS Code")
    console.print(f"[dim]   (Config is project-specific: {config_path})[/dim]")


@setup_app.command("all")
def configure_all():
    """Configure all AI tools."""
    console.print("[bold]Configuring all AI tools...[/bold]\n")
    configure_antigravity()
    configure_claude()
    configure_cursor()
    configure_vscode()


@setup_app.command("status")
def show_status():
    """Show current configuration status."""
    console.print(Panel.fit(
        "🔍 [bold]Lich MCP Configuration Status[/bold]",
        border_style="cyan"
    ))
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("AI Tool")
    table.add_column("Config Path")
    table.add_column("Status")
    
    tools = [
        ("Antigravity", get_antigravity_config_path(), "mcpServers"),
        ("Claude Desktop", get_claude_config_path(), "mcpServers"),
        ("Cursor", get_cursor_config_path(), "mcpServers"),
        ("VS Code", get_vscode_config_path(), "servers"),
    ]
    
    for name, path, key in tools:
        if path.exists():
            try:
                with open(path) as f:
                    config = json.load(f)
                if key in config and "lich" in config.get(key, {}):
                    status = "[green]✅ Configured[/green]"
                else:
                    status = "[yellow]⚠️ File exists, Lich not configured[/yellow]"
            except Exception:
                status = "[red]❌ Invalid config[/red]"
        else:
            status = "[dim]Not configured[/dim]"
        
        table.add_row(name, str(path), status)
    
    console.print(table)
