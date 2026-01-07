import subprocess

def register_ops_tools(mcp):
    """Register Ops tools (Deploy/Backup)."""

    @mcp.tool()
    def lich_deploy(env: str = "staging", dry_run: bool = True) -> str:
        """Deploy project via Ansible (wrapper around 'lich deploy')."""
        cmd = ["lich", "deploy", "--env", env]
        if dry_run:
            cmd.append("--dry-run")
            
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
