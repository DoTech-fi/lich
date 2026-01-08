"""
MCP Tools for Database Seeding.
"""
import subprocess


def register_seed_tools(mcp):
    """Register Seed-related tools."""

    @mcp.tool()
    def lich_seed(name: str = None, fresh: bool = False) -> str:
        """
        Seed the database with test data.
        
        Args:
            name: Specific seeder to run (e.g., 'users'). If None, runs all seeders.
            fresh: If True, re-run migrations before seeding.
        """
        cmd = ["lich", "seed"]
        if name:
            cmd.append(name)
        if fresh:
            cmd.append("--fresh")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_seed_list() -> str:
        """
        List all available database seeders.
        """
        cmd = ["lich", "seed", "--list"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"
