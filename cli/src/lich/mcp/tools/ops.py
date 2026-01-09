"""
MCP Tools for Ops (Deploy/Backup).
"""
import subprocess


def register_ops_tools(mcp):
    """Register Ops tools (Deploy/Backup)."""

    @mcp.tool()
    def lich_deploy_setup() -> str:
        """
        Setup deployment configuration.
        
        Interactive setup for staging and production environments.
        Configures SSH connection, deploy path, and git repo.
        """
        return (
            "Deploy setup is interactive. Run manually:\n\n"
            "  lich deploy setup\n\n"
            "This will ask:\n"
            "• Environment (staging/production)\n"
            "• SSH config or manual connection\n"
            "• Deploy path on server\n"
            "• Git repository URL"
        )

    @mcp.tool()
    def lich_deploy_stage(component: str, version: str = None, dry_run: bool = False) -> str:
        """
        Deploy a component to staging environment.
        
        Args:
            component: Component to deploy (backend, web, admin, landing)
            version: Version/tag to deploy (optional, defaults to latest)
            dry_run: If True, preview without deploying
        """
        cmd = ["lich", "deploy", "stage", component]
        if version:
            cmd.extend(["--version", version])
        if dry_run:
            cmd.append("--dry-run")
            
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_deploy_prod(component: str, version: str = None, dry_run: bool = False) -> str:
        """
        Deploy a component to production environment.
        
        WARNING: This deploys to production! Use --dry-run first.
        
        Args:
            component: Component to deploy (backend, web, admin, landing)
            version: Version/tag to deploy (optional, defaults to latest)
            dry_run: If True, preview without deploying
        """
        cmd = ["lich", "deploy", "prod", component, "--force"]  # --force for non-interactive
        if version:
            cmd.extend(["--version", version])
        if dry_run:
            cmd.append("--dry-run")
            
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_deploy_status() -> str:
        """
        Show deployment configuration status.
        
        Displays configured environments and their connection settings.
        """
        cmd = ["lich", "deploy", "status"]
            
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_backup(list_backups: bool = False) -> str:
        """Manage database backups."""
        cmd = ["lich", "backup"]
        if list_backups:
            cmd.append("--list")
            
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"
