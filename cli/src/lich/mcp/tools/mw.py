"""
MCP Tools for Middleware Management.
"""
import subprocess


def register_middleware_tools(mcp):
    """Register Middleware management tools."""

    @mcp.tool()
    def lich_middleware_list() -> str:
        """
        List all available middlewares and their status (enabled/disabled).
        
        Shows timing, security, logging, and rate_limit middleware status.
        """
        cmd = ["lich", "middleware", "list"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_middleware_enable(name: str) -> str:
        """
        Enable a middleware in the project.
        
        Args:
            name: Middleware name - 'timing', 'security', 'logging', or 'rate_limit'.
        """
        cmd = ["lich", "middleware", "enable", name]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_middleware_disable(name: str) -> str:
        """
        Disable a middleware in the project.
        
        Args:
            name: Middleware name - 'timing', 'security', 'logging', or 'rate_limit'.
        """
        cmd = ["lich", "middleware", "disable", name]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"
