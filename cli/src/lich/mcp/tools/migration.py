"""
MCP Tools for Database Migrations (Alembic wrapper).
"""
import subprocess


def register_migration_tools(mcp):
    """Register Migration-related tools."""

    @mcp.tool()
    def lich_migration_init() -> str:
        """
        Initialize Alembic migrations for the project.
        
        Creates the alembic directory structure and configuration files.
        """
        cmd = ["lich", "migration", "init"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_migration_create(message: str, autogenerate: bool = True) -> str:
        """
        Create a new database migration.
        
        Args:
            message: Migration message/name (e.g., 'add_users_table').
            autogenerate: If True, auto-generate from model changes.
        """
        cmd = ["lich", "migration", "create", message]
        if not autogenerate:
            cmd.append("--manual")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_migration_up(revision: str = "head") -> str:
        """
        Apply database migrations (upgrade).
        
        Args:
            revision: Target revision (default: 'head' for latest).
        """
        cmd = ["lich", "migration", "up", revision]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_migration_down(revision: str = "-1") -> str:
        """
        Rollback database migrations (downgrade).
        
        Args:
            revision: Target revision (default: '-1' for one step back).
        """
        cmd = ["lich", "migration", "down", revision]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_migration_status() -> str:
        """
        Show current database migration status.
        
        Displays current revision and migration history.
        """
        cmd = ["lich", "migration", "status"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_migration_heads() -> str:
        """
        Show available migration heads.
        """
        cmd = ["lich", "migration", "heads"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"
