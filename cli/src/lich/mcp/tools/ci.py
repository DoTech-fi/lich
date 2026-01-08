"""
MCP Tools for CI (Continuous Integration) checks.
"""
import subprocess


def register_ci_tools(mcp):
    """Register CI-related tools."""

    @mcp.tool()
    def lich_ci_all() -> str:
        """
        Run all CI checks locally.
        
        Runs linting, type checking, tests, and security scans for all parts.
        """
        cmd = ["lich", "ci"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_ci_backend() -> str:
        """
        Run CI checks for backend only.
        
        Runs Python linting (ruff), type checking (mypy), tests (pytest), 
        and security scanning (bandit).
        """
        cmd = ["lich", "ci", "backend"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_ci_web() -> str:
        """
        Run CI checks for web app only.
        
        Runs ESLint, TypeScript type checking, build validation, and npm audit.
        """
        cmd = ["lich", "ci", "web"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_ci_admin() -> str:
        """
        Run CI checks for admin panel only.
        
        Runs ESLint, TypeScript type checking, build validation, and npm audit.
        """
        cmd = ["lich", "ci", "admin"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"
