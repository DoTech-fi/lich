"""
MCP Tools for Routes - List all API routes.
"""
import subprocess


def register_routes_tools(mcp):
    """Register Routes-related tools."""

    @mcp.tool()
    def lich_routes(verbose: bool = False) -> str:
        """
        List all API routes in the project.
        
        Returns a JSON list of routes with method, path, function, and file.
        """
        cmd = ["lich", "routes"]
        if verbose:
            cmd.append("--verbose")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"
