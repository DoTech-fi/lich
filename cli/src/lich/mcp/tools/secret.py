"""
MCP Tools for Secret Management.
"""
import subprocess


def register_secret_tools(mcp):
    """Register Secret management tools."""

    @mcp.tool()
    def lich_secret_generate(length: int = 32, count: int = 1, format: str = "hex") -> str:
        """
        Generate cryptographically secure secrets.
        
        Args:
            length: Length of each secret (default: 32).
            count: Number of secrets to generate (default: 1).
            format: Format: 'hex', 'alphanum', 'urlsafe', 'full'.
        """
        cmd = ["lich", "secret", "generate", "-l", str(length), "-c", str(count), "-f", format]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_secret_rotate(key: str = None, env_file: str = ".env", dry_run: bool = True) -> str:
        """
        Rotate secrets in your environment file.
        
        Args:
            key: Specific key to rotate (default: all secret keys).
            env_file: Environment file path (default: '.env').
            dry_run: If True, show what would change without actually changing.
        """
        cmd = ["lich", "secret", "rotate", "-e", env_file]
        if key:
            cmd.extend(["-k", key])
        if dry_run:
            cmd.append("--dry-run")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_secret_check(env_file: str = ".env") -> str:
        """
        Check secret strength and security issues.
        
        Scans for weak secrets, short secrets, and common patterns.
        
        Args:
            env_file: Environment file to check (default: '.env').
        """
        cmd = ["lich", "secret", "check", "-e", env_file]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"
