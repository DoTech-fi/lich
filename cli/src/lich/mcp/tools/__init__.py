"""MCP Tools package - shared utilities."""
import re
import os


def clean_cli_output(text: str) -> str:
    """Remove ANSI escape codes and problematic characters from CLI output.
    
    Use this for all subprocess outputs to prevent MCP JSON parsing errors.
    """
    if not text:
        return ""
    # Remove ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    # Remove spinner characters
    text = re.sub(r'[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]', '', text)
    return text


def run_lich_command(cmd: list, force_no_color: bool = True) -> str:
    """Run a lich CLI command and return cleaned output.

    Args:
        cmd: Command list to run (e.g., ["lich", "deploy", "prod", "web"])
        force_no_color: If True, set NO_COLOR=1 to disable rich formatting

    Returns:
        Cleaned output string (stdout + stderr), or "ERROR (exit N): <output>"
        if the subprocess exits with a non-zero return code.
    """
    import subprocess

    try:
        env = os.environ.copy()
        if force_no_color:
            env['NO_COLOR'] = '1'
        res = subprocess.run(cmd, capture_output=True, text=True, env=env)
        output = clean_cli_output(res.stdout + res.stderr)
        if res.returncode != 0:
            return f"ERROR (exit {res.returncode}): {output}"
        return output
    except FileNotFoundError:
        return "lich command not found"


async def run_lich_command_async(cmd: list, force_no_color: bool = True) -> str:
    """Async variant of run_lich_command for long-running tools.

    Uses asyncio.create_subprocess_exec (never a shell) so a slow deploy/CI/
    migration doesn't block the MCP server's event loop. Non-zero exits are
    prefixed with 'ERROR (exit N):' so AI callers can detect failure.
    """
    import asyncio

    env = os.environ.copy()
    if force_no_color:
        env["NO_COLOR"] = "1"
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
        )
        out, _ = await proc.communicate()
        text = clean_cli_output(out.decode(errors="replace"))
        if proc.returncode != 0:
            return f"ERROR (exit {proc.returncode}):\n{text}"
        return text
    except FileNotFoundError:
        return f"Command not found: {cmd[0]}"
