"""
lich security - Security scanning commands.

Usage:
    lich security --backend     # Scan Python code (bandit + safety)
    lich security --frontend    # Scan NPM dependencies (npm audit)
    lich security --secrets     # Scan for hardcoded secrets
    lich security --docker      # Scan Docker images (trivy)
    lich security               # Run all scans
    lich security --fix         # Auto-fix where possible
    lich security --json        # Output as JSON
"""
import subprocess
import json
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

security_app = typer.Typer(
    name="security",
    help="🔒 Security scanning for backend, frontend, and Docker",
    no_args_is_help=False,
)


def _check_lich_project():
    """Check if we're in a Lich project."""
    if not (Path(".lich").exists() or Path("backend").exists()):
        console.print("[red]Error: Not in a Lich project directory[/red]")
        raise typer.Exit(1)


def _run_command(cmd: list, capture: bool = True) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            cwd=Path.cwd(),
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def _check_tool_installed(tool: str) -> bool:
    """Check if a security tool is installed."""
    code, _, _ = _run_command(["which", tool])
    return code == 0


def scan_python_security(fix: bool = False) -> dict:
    """Scan Python code with bandit and safety."""
    results = {"tool": "python", "passed": True, "issues": []}
    
    backend_path = Path("backend")
    if not backend_path.exists():
        results["issues"].append({"severity": "info", "message": "No backend directory found"})
        return results
    
    # Run bandit
    console.print("\n[blue]🔍 Running bandit (Python security linter)...[/blue]")
    if _check_tool_installed("bandit"):
        code, stdout, stderr = _run_command([
            "bandit", "-r", str(backend_path),
            "-f", "json", "-q"
        ])
        if code != 0 and stdout:
            try:
                bandit_results = json.loads(stdout)
                for issue in bandit_results.get("results", []):
                    results["issues"].append({
                        "severity": issue.get("issue_severity", "MEDIUM").lower(),
                        "message": f"[{issue.get('test_id')}] {issue.get('issue_text')}",
                        "file": issue.get("filename", ""),
                        "line": issue.get("line_number", 0),
                    })
                    results["passed"] = False
            except json.JSONDecodeError:
                pass
        else:
            console.print("[green]  ✓ No bandit issues found[/green]")
    else:
        console.print("[yellow]  ⚠ bandit not installed. Install with: pip install bandit[/yellow]")
    
    # Run safety (check dependencies)
    console.print("[blue]🔍 Running safety (dependency vulnerability check)...[/blue]")
    if _check_tool_installed("safety"):
        requirements_file = backend_path / "requirements.txt"
        if requirements_file.exists():
            code, stdout, stderr = _run_command([
                "safety", "check", "-r", str(requirements_file), "--json"
            ])
            if code != 0:
                try:
                    safety_results = json.loads(stdout)
                    for vuln in safety_results:
                        results["issues"].append({
                            "severity": "high",
                            "message": f"{vuln[0]}: {vuln[3]}",
                        })
                        results["passed"] = False
                except (json.JSONDecodeError, IndexError, TypeError):
                    pass
            else:
                console.print("[green]  ✓ No known vulnerabilities in dependencies[/green]")
    else:
        console.print("[yellow]  ⚠ safety not installed. Install with: pip install safety[/yellow]")
    
    return results


def scan_frontend_security(fix: bool = False) -> dict:
    """Scan frontend apps with npm audit."""
    results = {"tool": "frontend", "passed": True, "issues": []}
    
    apps_dir = Path("apps")
    if not apps_dir.exists():
        results["issues"].append({"severity": "info", "message": "No apps directory found"})
        return results
    
    console.print("\n[blue]🔍 Running npm audit on frontend apps...[/blue]")
    
    for app_dir in apps_dir.iterdir():
        if app_dir.is_dir() and (app_dir / "package.json").exists():
            console.print(f"  Scanning [cyan]{app_dir.name}[/cyan]...")
            
            cmd = ["npm", "audit", "--json"]
            if fix:
                cmd = ["npm", "audit", "fix", "--json"]
            
            code, stdout, stderr = _run_command(cmd)
            
            # npm audit returns non-zero if vulnerabilities found
            if stdout:
                try:
                    audit_results = json.loads(stdout)
                    vulns = audit_results.get("vulnerabilities", {})
                    for pkg, info in vulns.items():
                        results["issues"].append({
                            "severity": info.get("severity", "moderate"),
                            "message": f"[{app_dir.name}] {pkg}: {info.get('via', [{}])[0].get('title', 'Unknown vulnerability') if isinstance(info.get('via', []), list) and info.get('via') else 'Vulnerable'}",
                        })
                        results["passed"] = False
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass
            
            if code == 0:
                console.print(f"    [green]✓ No vulnerabilities in {app_dir.name}[/green]")
    
    return results


def scan_secrets(fix: bool = False) -> dict:
    """Scan for hardcoded secrets with git-secrets or gitleaks."""
    results = {"tool": "secrets", "passed": True, "issues": []}
    
    console.print("\n[blue]🔍 Scanning for hardcoded secrets...[/blue]")
    
    # Try gitleaks first (more modern)
    if _check_tool_installed("gitleaks"):
        code, stdout, stderr = _run_command([
            "gitleaks", "detect", "--source", ".", "--report-format", "json", "--no-git"
        ])
        if code != 0 and stdout:
            try:
                leaks = json.loads(stdout)
                for leak in leaks:
                    results["issues"].append({
                        "severity": "critical",
                        "message": f"[{leak.get('RuleID')}] {leak.get('Description', 'Secret detected')}",
                        "file": leak.get("File", ""),
                        "line": leak.get("StartLine", 0),
                    })
                    results["passed"] = False
            except (json.JSONDecodeError, TypeError):
                pass
        else:
            console.print("[green]  ✓ No hardcoded secrets found[/green]")
    elif _check_tool_installed("git-secrets"):
        code, stdout, stderr = _run_command(["git-secrets", "--scan"])
        if code != 0:
            results["issues"].append({
                "severity": "critical",
                "message": stderr or "Secrets found in repository",
            })
            results["passed"] = False
        else:
            console.print("[green]  ✓ No hardcoded secrets found[/green]")
    else:
        console.print("[yellow]  ⚠ Neither gitleaks nor git-secrets installed[/yellow]")
        console.print("[yellow]    Install gitleaks: brew install gitleaks[/yellow]")
    
    return results


def scan_docker(fix: bool = False) -> dict:
    """Scan Docker images with trivy."""
    results = {"tool": "docker", "passed": True, "issues": []}
    
    console.print("\n[blue]🔍 Scanning Docker configuration...[/blue]")
    
    if not _check_tool_installed("trivy"):
        console.print("[yellow]  ⚠ trivy not installed. Install with: brew install trivy[/yellow]")
        return results
    
    # Scan Dockerfiles
    dockerfiles = list(Path(".").rglob("Dockerfile*"))
    for dockerfile in dockerfiles:
        console.print(f"  Scanning [cyan]{dockerfile}[/cyan]...")
        code, stdout, stderr = _run_command([
            "trivy", "config", str(dockerfile.parent), "--format", "json"
        ])
        if stdout:
            try:
                trivy_results = json.loads(stdout)
                for result in trivy_results.get("Results", []):
                    for misconfig in result.get("Misconfigurations", []):
                        results["issues"].append({
                            "severity": misconfig.get("Severity", "MEDIUM").lower(),
                            "message": misconfig.get("Title", "Misconfiguration"),
                            "file": str(dockerfile),
                        })
                        results["passed"] = False
            except (json.JSONDecodeError, TypeError):
                pass
    
    if results["passed"]:
        console.print("[green]  ✓ No Docker misconfigurations found[/green]")
    
    return results


def display_results(all_results: list, as_json: bool = False):
    """Display scan results."""
    if as_json:
        console.print(json.dumps(all_results, indent=2))
        return
    
    total_issues = sum(len(r["issues"]) for r in all_results)
    passed = all(r["passed"] for r in all_results)
    
    console.print("\n")
    console.print(Panel.fit(
        f"[{'green' if passed else 'red'}]{'✓ All checks passed!' if passed else f'✗ Found {total_issues} issue(s)'}[/]",
        title="🔒 Security Scan Results",
    ))
    
    if not passed:
        table = Table(title="Issues Found")
        table.add_column("Severity", style="cyan")
        table.add_column("Tool", style="magenta")
        table.add_column("Message")
        table.add_column("Location")
        
        for result in all_results:
            for issue in result["issues"]:
                severity = issue.get("severity", "medium")
                severity_color = {
                    "critical": "red bold",
                    "high": "red",
                    "medium": "yellow",
                    "low": "blue",
                    "info": "dim",
                }.get(severity, "white")
                
                location = ""
                if issue.get("file"):
                    location = issue["file"]
                    if issue.get("line"):
                        location += f":{issue['line']}"
                
                table.add_row(
                    f"[{severity_color}]{severity.upper()}[/]",
                    result["tool"],
                    issue.get("message", ""),
                    location,
                )
        
        console.print(table)


@security_app.callback(invoke_without_command=True)
def security_scan(
    ctx: typer.Context,
    backend: bool = typer.Option(False, "--backend", "-b", help="Scan Python code (bandit + safety)"),
    frontend: bool = typer.Option(False, "--frontend", "-f", help="Scan NPM dependencies"),
    secrets: bool = typer.Option(False, "--secrets", "-s", help="Scan for hardcoded secrets"),
    docker: bool = typer.Option(False, "--docker", "-d", help="Scan Docker images"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix where possible"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """
    🔒 Run security scans on your Lich project.
    
    By default, runs all scans. Use flags to run specific scans.
    
    Examples:
        lich security                   # Run all scans
        lich security --backend         # Python only
        lich security --frontend --fix  # Frontend with auto-fix
        lich security --json            # JSON output
    """
    _check_lich_project()
    
    # If no specific flags, run all
    run_all = not (backend or frontend or secrets or docker)
    
    results = []
    
    console.print(Panel.fit("🔒 Lich Security Scanner", style="bold blue"))
    
    if run_all or backend:
        results.append(scan_python_security(fix))
    
    if run_all or frontend:
        results.append(scan_frontend_security(fix))
    
    if run_all or secrets:
        results.append(scan_secrets(fix))
    
    if run_all or docker:
        results.append(scan_docker(fix))
    
    display_results(results, output_json)
    
    # Exit with error if issues found
    if not all(r["passed"] for r in results):
        raise typer.Exit(1)
