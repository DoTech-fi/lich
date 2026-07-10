"""
Safe subprocess execution helpers.

Rules enforced here:
- Local commands are ALWAYS argument lists. shell=True is never used.
- Remote (SSH) commands are strings executed by the remote shell, so every
  interpolated value MUST be quoted with quote() at the call site.
"""
import subprocess
from pathlib import Path
from shlex import quote  # re-exported: call sites use `from lich.commands._shell import quote`

__all__ = ["run_local", "run_remote", "quote"]


def run_local(
    cmd: list[str],
    cwd: str | Path | None = None,
    timeout: int | None = None,
    capture: bool = True,
) -> tuple[int, str]:
    """Run a local command (argument list, never a shell string).

    Returns (returncode, combined stdout+stderr). Execution-environment
    errors (missing binary, bad cwd, permissions, timeout) do not raise -
    they return (1, message) instead.
    """
    if isinstance(cmd, str):
        raise TypeError("cmd must be an argument list, not a string")
    try:
        if capture:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd
            )
            return result.returncode, result.stdout + result.stderr
        result = subprocess.run(cmd, timeout=timeout, cwd=cwd)
        return result.returncode, ""
    except subprocess.TimeoutExpired:
        return 1, "Command timeout"
    except FileNotFoundError:
        return 1, f"Command not found: {cmd[0]}"
    except (NotADirectoryError, PermissionError) as e:
        return 1, f"Cannot execute {cmd[0]}: {e}"


def run_remote(
    ssh_host: str,
    script: str,
    timeout: int = 120,
    capture: bool = True,
) -> tuple[int, str]:
    """Run a script on a remote host via SSH.

    The script runs in the remote shell: every value interpolated into it
    must be pre-quoted with quote().
    """
    if not ssh_host or ssh_host.startswith("-"):
        raise ValueError(f"Invalid SSH host: {ssh_host!r}")
    ssh_cmd = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=10",
        ssh_host,
        script,
    ]
    return run_local(ssh_cmd, timeout=timeout, capture=capture)
