"""
MCP Tools for Utility Commands (adopt, upgrade, version).
"""
import subprocess


def register_utility_tools(mcp):
    """Register Utility tools."""

    @mcp.tool()
    def lich_adopt(path: str, output: str = ".", dry_run: bool = True) -> str:
        """
        Adopt an existing Python project into Lich architecture.
        
        Analyzes the project and suggests a Lich configuration.
        
        Args:
            path: Path to existing Python project.
            output: Output directory for new Lich project.
            dry_run: If True, only analyze without creating project.
        """
        cmd = ["lich", "adopt", path, "-o", output]
        if dry_run:
            cmd.append("--dry-run")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_upgrade(force: bool = False) -> str:
        """
        Upgrade project to the latest Lich Toolkit version.
        
        Updates .lich/rules/, .lich/workflows/, AGENTS.md, CLAUDE.md.
        
        Args:
            force: If True, skip confirmation prompt.
        """
        cmd = ["lich", "upgrade"]
        if force:
            cmd.append("--force")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_version() -> str:
        """
        Show Lich Toolkit version information.
        """
        cmd = ["lich", "version"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"
