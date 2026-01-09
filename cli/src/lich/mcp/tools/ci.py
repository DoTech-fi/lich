"""
MCP Tools for CI (Continuous Integration) checks.
"""
import subprocess


def register_ci_tools(mcp):
    """Register CI-related tools."""

    @mcp.tool()
    def lich_ci_setup() -> str:
        """
        Setup act for local CI.
        
        Creates .actrc, .secrets, and optionally .ci-vars and .ci-env files.
        Checks if Docker is running and act is installed.
        """
        import shutil
        
        # Check Docker
        docker_result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
        )
        
        if docker_result.returncode != 0:
            return (
                "❌ Docker is not running!\n\n"
                "Please start Docker first:\n"
                "• Mac: Open Docker Desktop app\n"
                "• Linux: sudo systemctl start docker\n\n"
                "Then run: lich ci setup"
            )
        
        # Check act
        if not shutil.which("act"):
            return (
                "✓ Docker is running\n"
                "❌ act is not installed\n\n"
                "Install act:\n"
                "• Mac: brew install act\n"
                "• Linux: curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash\n\n"
                "Then run: lich ci setup"
            )
        
        # Run setup
        cmd = ["lich", "ci", "setup"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_ci_backend(local: bool = False) -> str:
        """
        Run CI checks for backend only.
        
        By default runs with Docker/act. Use local=True for direct execution.
        
        Args:
            local: If True, run locally without Docker (faster for dev).
        """
        cmd = ["lich", "ci", "backend"]
        if local:
            cmd.append("-l")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_ci_web(local: bool = False) -> str:
        """
        Run CI checks for web app only.
        
        By default runs with Docker/act. Use local=True for direct execution.
        
        Args:
            local: If True, run locally without Docker.
        """
        cmd = ["lich", "ci", "web"]
        if local:
            cmd.append("-l")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_ci_admin(local: bool = False) -> str:
        """
        Run CI checks for admin panel only.
        
        By default runs with Docker/act. Use local=True for direct execution.
        
        Args:
            local: If True, run locally without Docker.
        """
        cmd = ["lich", "ci", "admin"]
        if local:
            cmd.append("-l")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"

    @mcp.tool()
    def lich_ci_landing(local: bool = False) -> str:
        """
        Run CI checks for landing page only.
        
        By default runs with Docker/act. Use local=True for direct execution.
        
        Args:
            local: If True, run locally without Docker.
        """
        cmd = ["lich", "ci", "landing"]
        if local:
            cmd.append("-l")
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.stdout + res.stderr
        except FileNotFoundError:
            return "lich command not found"
