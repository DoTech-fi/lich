import json
from lich.commands.lint import lint_python, lint_frontend
from lich.commands.security import (
    scan_python_security, scan_frontend_security,
    scan_secrets, scan_docker
)

from . import run_lich_command


def lich_lint_backend(fix: bool = False) -> str:
    """Run Python Linter (Ruff)."""
    result = lint_python(fix=fix)
    return json.dumps(result, indent=2)


def lich_lint_frontend(fix: bool = False) -> str:
    """Run Frontend Linter (ESLint)."""
    result = lint_frontend(fix=fix)
    return json.dumps(result, indent=2)


def lich_security_scan(target: str = "backend") -> str:
    """
    Run security scan.
    Target options: 'backend', 'frontend', 'secrets', 'docker', 'all'.
    """
    results = []
    if target in ["backend", "all"]:
        results.append(scan_python_security())
    if target in ["frontend", "all"]:
        results.append(scan_frontend_security())
    if target in ["secrets", "all"]:
        results.append(scan_secrets())
    if target in ["docker", "all"]:
        results.append(scan_docker())

    return json.dumps(results, indent=2)


def lich_test(unit: bool = False, integration: bool = False, coverage: bool = False) -> str:
    """Run project tests via subprocess (pytest wrapper)."""
    cmd = ["lich", "test"]
    if unit:
        cmd.append("--unit")
    if integration:
        cmd.append("--integration")
    if coverage:
        cmd.append("--coverage")
    return run_lich_command(cmd)


_TOOLS = [lich_lint_backend, lich_lint_frontend, lich_security_scan, lich_test]


def register_qa_tools(mcp):
    """Register QA tools (Lint/Test/Security)."""
    for tool in _TOOLS:
        mcp.tool()(tool)
