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
        Cleaned output string (stdout + stderr)
    """
    import subprocess
    
    try:
        env = os.environ.copy()
        if force_no_color:
            env['NO_COLOR'] = '1'
        res = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return clean_cli_output(res.stdout + res.stderr)
    except FileNotFoundError:
        return "lich command not found"
