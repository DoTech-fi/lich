"""
MCP Tools for Development Environment Management.
"""
import subprocess


def register_dev_tools(mcp):
    """Register Development environment tools."""

    @mcp.tool()
    def lich_dev_start(force: bool = False) -> str:
        """
        Start the full development environment.
        
        Starts Docker containers, backend, and frontend apps.
        
        Args:
            force: If True, force kill processes using required ports.
        """
        cmd = ["lich", "start"]
        if force:
            cmd.append("--force")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_dev_stop(docker: bool = False) -> str:
        """
        Stop all running development services.
        
        Args:
            docker: If True, also stop Docker containers.
        """
        cmd = ["lich", "stop"]
        if docker:
            cmd.append("--docker")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"
