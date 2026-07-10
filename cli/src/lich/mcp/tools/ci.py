"""
MCP Tools for CI (Continuous Integration) checks — CI runs take minutes, so async.
"""
import shutil
import subprocess

from . import run_lich_command_async


async def lich_ci_setup() -> str:
    """
    Setup act for local CI.

    Creates .actrc, .secrets, and optionally .ci-vars and .ci-env files.
    Checks if Docker is running and act is installed.
    """
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

    if not shutil.which("act"):
        return (
            "✓ Docker is running\n"
            "❌ act is not installed\n\n"
            "Install act:\n"
            "• Mac: brew install act\n"
            "• Linux: curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash\n\n"
            "Then run: lich ci setup"
        )

    return await run_lich_command_async(["lich", "ci", "setup"])


async def _run_ci(app: str, local: bool) -> str:
    cmd = ["lich", "ci", app]
    if local:
        cmd.append("-l")
    return await run_lich_command_async(cmd)


async def lich_ci_backend(local: bool = False) -> str:
    """
    Run CI checks for backend only.

    By default runs with Docker/act. Use local=True for direct execution.

    Args:
        local: If True, run locally without Docker (faster for dev).
    """
    return await _run_ci("backend", local)


async def lich_ci_web(local: bool = False) -> str:
    """
    Run CI checks for web app only.

    Args:
        local: If True, run locally without Docker.
    """
    return await _run_ci("web", local)


async def lich_ci_admin(local: bool = False) -> str:
    """
    Run CI checks for admin panel only.

    Args:
        local: If True, run locally without Docker.
    """
    return await _run_ci("admin", local)


async def lich_ci_landing(local: bool = False) -> str:
    """
    Run CI checks for landing page only.

    Args:
        local: If True, run locally without Docker.
    """
    return await _run_ci("landing", local)


async def lich_ci_all(local: bool = False) -> str:
    """
    Run CI checks for all components sequentially (backend, web, admin, landing).

    By default runs with Docker/act. Use local=True for direct execution.

    Args:
        local: If True, run locally without Docker (faster for dev).
    """
    results = []
    for component in ["backend", "web", "admin", "landing"]:
        output = await _run_ci(component, local)
        if output.startswith("ERROR"):
            status = f"❌ (failed)"
        else:
            status = "✅"
        results.append(f"=== {component} {status} ===\n{output}")
    return "\n".join(results)


_TOOLS = [lich_ci_setup, lich_ci_backend, lich_ci_web, lich_ci_admin, lich_ci_landing, lich_ci_all]


def register_ci_tools(mcp):
    """Register CI-related tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
