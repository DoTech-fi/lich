"""
lich production-ready - Check production readiness of your Lich project.

Usage:
    lich production-ready           # Run all checks
    lich production-ready --json    # Output as JSON
"""
import re
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, field
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

production_ready_app = typer.Typer(
    name="production-ready",
    help="🚀 Check if your project is production-ready",
    no_args_is_help=False,
)


@dataclass
class CheckResult:
    """Result of a single check."""
    name: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class CheckCategory:
    """Category of checks with results."""
    name: str
    icon: str
    checks: List[CheckResult] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks if c.severity == "error")
    
    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)


class ProductionReadinessChecker:
    """Check production readiness of a Lich project."""
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.env_file = self.project_path / ".env"
        self.env_vars = self._load_env()
    
    def _load_env(self) -> Dict[str, str]:
        """Load environment variables from .env file."""
        env_vars = {}
        if self.env_file.exists():
            for line in self.env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    env_vars[key.strip()] = value.strip().strip('"\'')
        return env_vars
    
    def _read_file(self, path: Path) -> str:
        """Read file content safely."""
        try:
            return path.read_text()
        except Exception:
            return ""
    
    # ========== Security Checks ==========
    
    def check_security_middlewares(self) -> CheckResult:
        """Check if security middlewares are enabled."""
        main_py = self._read_file(self.project_path / "backend" / "main.py")
        enabled = "SecurityHeadersMiddleware" in main_py and "#" not in main_py.split("SecurityHeadersMiddleware")[0].split("\n")[-1]
        
        # Also check env
        security_enabled = self.env_vars.get("SECURITY_ENABLED", "false").lower() == "true"
        
        return CheckResult(
            name="Security middlewares enabled",
            passed=enabled or security_enabled,
            message="SecurityHeadersMiddleware should be active" if not enabled else "Enabled",
            severity="error"
        )
    
    def check_cors_not_wildcard(self) -> CheckResult:
        """Check CORS is not wildcard in production."""
        cors = self.env_vars.get("CORS_ORIGINS", "*")
        is_wildcard = cors == "*" or cors == '["*"]'
        
        return CheckResult(
            name="CORS not wildcard",
            passed=not is_wildcard,
            message="CORS_ORIGINS should not be '*' in production" if is_wildcard else f"CORS: {cors[:50]}...",
            severity="error"
        )
    
    def check_debug_false(self) -> CheckResult:
        """Check DEBUG is false."""
        debug = self.env_vars.get("DEBUG", "true").lower()
        is_debug = debug in ("true", "1", "yes")
        
        return CheckResult(
            name="DEBUG mode disabled",
            passed=not is_debug,
            message="DEBUG should be false in production" if is_debug else "DEBUG=false",
            severity="error"
        )
    
    def check_secret_key_length(self) -> CheckResult:
        """Check secret key is at least 32 chars."""
        secret = self.env_vars.get("SECRET_KEY", "")
        length = len(secret)
        weak_patterns = ["changeme", "secret", "your-secret", "change-me"]
        is_weak = any(p in secret.lower() for p in weak_patterns)
        
        return CheckResult(
            name="Secret key strength",
            passed=length >= 32 and not is_weak,
            message=f"SECRET_KEY is {'weak/default' if is_weak else f'{length} chars (needs ≥32)'}",
            severity="error"
        )
    
    def check_jwt_secret_length(self) -> CheckResult:
        """Check JWT secret is at least 32 chars."""
        secret = self.env_vars.get("JWT_SECRET_KEY", self.env_vars.get("JWT_SECRET", ""))
        if not secret:
            return CheckResult(
                name="JWT secret strength",
                passed=True,
                message="No JWT configured",
                severity="info"
            )
        
        length = len(secret)
        return CheckResult(
            name="JWT secret strength",
            passed=length >= 32,
            message=f"JWT secret is {length} chars (needs ≥32)",
            severity="error"
        )
    
    def check_no_hardcoded_secrets(self) -> CheckResult:
        """Check for hardcoded secrets in code."""
        patterns = [
            r'password\s*=\s*["\'][^"\']{3,}["\']',
            r'secret\s*=\s*["\'][^"\']{3,}["\']',
            r'api_key\s*=\s*["\'][^"\']{3,}["\']',
        ]
        
        issues = []
        backend = self.project_path / "backend"
        if backend.exists():
            for py_file in backend.rglob("*.py"):
                content = self._read_file(py_file)
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        rel_path = py_file.relative_to(self.project_path)
                        issues.append(str(rel_path))
                        break
        
        return CheckResult(
            name="No hardcoded secrets",
            passed=len(issues) == 0,
            message=f"Potential secrets in: {', '.join(issues[:3])}" if issues else "No hardcoded secrets found",
            severity="warning"
        )
    
    # ========== Quality Checks ==========
    
    def check_test_coverage(self) -> CheckResult:
        """Check test coverage is at least 80%."""
        # Look for coverage report
        coverage_file = self.project_path / "backend" / "coverage.xml"
        htmlcov = self.project_path / "backend" / "htmlcov" / "index.html"
        
        coverage = None
        if coverage_file.exists():
            content = self._read_file(coverage_file)
            match = re.search(r'line-rate="([\d.]+)"', content)
            if match:
                coverage = float(match.group(1)) * 100
        elif htmlcov.exists():
            content = self._read_file(htmlcov)
            match = re.search(r'(\d+)%', content)
            if match:
                coverage = int(match.group(1))
        
        if coverage is None:
            return CheckResult(
                name="Test coverage ≥80%",
                passed=False,
                message="No coverage report found. Run: pytest --cov",
                severity="warning"
            )
        
        return CheckResult(
            name="Test coverage ≥80%",
            passed=coverage >= 80,
            message=f"Coverage: {coverage:.1f}%",
            severity="warning"
        )
    
    def check_no_todos(self) -> CheckResult:
        """Check for TODO/FIXME comments."""
        todos = []
        backend = self.project_path / "backend"
        if backend.exists():
            for py_file in backend.rglob("*.py"):
                content = self._read_file(py_file)
                if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', content, re.IGNORECASE):
                    rel_path = py_file.relative_to(self.project_path)
                    todos.append(str(rel_path))
        
        return CheckResult(
            name="No TODO/FIXME in code",
            passed=len(todos) == 0,
            message=f"Found in {len(todos)} files" if todos else "No TODOs found",
            severity="warning"
        )
    
    def check_env_in_compose(self) -> CheckResult:
        """Check all .env vars are in docker-compose."""
        compose_file = self.project_path / "docker-compose.yml"
        if not compose_file.exists():
            return CheckResult(
                name="Env vars in docker-compose",
                passed=True,
                message="No docker-compose.yml found",
                severity="info"
            )
        
        compose_content = self._read_file(compose_file)
        missing = []
        important_vars = ["DATABASE_URL", "REDIS_URL", "SECRET_KEY"]
        
        for var in important_vars:
            if var in self.env_vars and var not in compose_content:
                missing.append(var)
        
        return CheckResult(
            name="Env vars in docker-compose",
            passed=len(missing) == 0,
            message=f"Missing: {', '.join(missing)}" if missing else "All important vars present",
            severity="warning"
        )
    
    # ========== Operations Checks ==========
    
    def check_docker_tags(self) -> CheckResult:
        """Check Docker images use specific tags (not :latest)."""
        compose_file = self.project_path / "docker-compose.yml"
        if not compose_file.exists():
            return CheckResult(
                name="Docker images use specific tags",
                passed=True,
                message="No docker-compose.yml found",
                severity="info"
            )
        
        content = self._read_file(compose_file)
        has_latest = ":latest" in content
        
        return CheckResult(
            name="Docker images use specific tags",
            passed=not has_latest,
            message="Found :latest tag; use specific versions" if has_latest else "All images use specific tags",
            severity="warning"
        )
    
    def check_health_includes_db(self) -> CheckResult:
        """Check health check includes DB/Redis."""
        health_file = self.project_path / "backend" / "api" / "http" / "health.py"
        if not health_file.exists():
            return CheckResult(
                name="Health check includes DB/Redis",
                passed=False,
                message="No health.py found",
                severity="warning"
            )
        
        content = self._read_file(health_file)
        has_db = "database" in content.lower() or "postgres" in content.lower()
        has_redis = "redis" in content.lower()
        
        return CheckResult(
            name="Health check includes DB/Redis",
            passed=has_db,
            message=f"DB: {'✓' if has_db else '✗'}, Redis: {'✓' if has_redis else 'N/A'}",
            severity="warning"
        )
    
    def check_ssl_configured(self) -> CheckResult:
        """Check SSL/HTTPS is configured."""
        traefik_config = self.project_path / "infra" / "ansible" / "roles" / "traefik"
        compose_content = self._read_file(self.project_path / "docker-compose.yml")
        
        has_ssl = (
            traefik_config.exists() or 
            "letsencrypt" in compose_content.lower() or
            "https" in compose_content.lower() or
            "443" in compose_content
        )
        
        return CheckResult(
            name="SSL/HTTPS configured",
            passed=has_ssl,
            message="SSL configuration found" if has_ssl else "No SSL configuration detected",
            severity="error"
        )
    
    def check_rate_limiting(self) -> CheckResult:
        """Check rate limiting is enabled."""
        main_py = self._read_file(self.project_path / "backend" / "main.py")
        rate_limit_enabled = "RateLimitMiddleware" in main_py
        
        return CheckResult(
            name="Rate limiting enabled",
            passed=rate_limit_enabled,
            message="RateLimitMiddleware found" if rate_limit_enabled else "No rate limiting configured",
            severity="warning"
        )
    
    def check_backup_strategy(self) -> CheckResult:
        """Check backup strategy is defined."""
        backup_role = self.project_path / "infra" / "ansible" / "roles" / "backup"
        backup_script = self.project_path / "scripts" / "backup.sh"
        
        has_backup = backup_role.exists() or backup_script.exists()
        
        return CheckResult(
            name="Backup strategy defined",
            passed=has_backup,
            message="Backup configuration found" if has_backup else "No backup strategy detected",
            severity="warning"
        )
    
    def check_structured_logging(self) -> CheckResult:
        """Check structured logging is enabled."""
        logger_setup = self.project_path / "backend" / "pkg" / "logger" / "setup.py"
        main_py = self._read_file(self.project_path / "backend" / "main.py")
        
        has_logging = logger_setup.exists() or "structlog" in main_py or "setup_logging" in main_py
        
        return CheckResult(
            name="Structured logging enabled",
            passed=has_logging,
            message="Logging configuration found" if has_logging else "No structured logging detected",
            severity="warning"
        )
    
    def run_all_checks(self) -> List[CheckCategory]:
        """Run all production readiness checks."""
        categories = []
        
        # Security checks
        security = CheckCategory("Security", "🔒")
        security.checks = [
            self.check_security_middlewares(),
            self.check_cors_not_wildcard(),
            self.check_debug_false(),
            self.check_secret_key_length(),
            self.check_jwt_secret_length(),
            self.check_no_hardcoded_secrets(),
        ]
        categories.append(security)
        
        # Quality checks
        quality = CheckCategory("Quality", "✨")
        quality.checks = [
            self.check_test_coverage(),
            self.check_no_todos(),
            self.check_env_in_compose(),
        ]
        categories.append(quality)
        
        # Operations checks
        operations = CheckCategory("Operations", "⚙️")
        operations.checks = [
            self.check_docker_tags(),
            self.check_health_includes_db(),
            self.check_ssl_configured(),
            self.check_rate_limiting(),
            self.check_backup_strategy(),
            self.check_structured_logging(),
        ]
        categories.append(operations)
        
        return categories


def display_results(categories: List[CheckCategory], as_json: bool = False):
    """Display check results."""
    if as_json:
        output = {
            "passed": all(c.passed for c in categories),
            "categories": [
                {
                    "name": cat.name,
                    "passed": cat.passed,
                    "checks": [
                        {
                            "name": c.name,
                            "passed": c.passed,
                            "message": c.message,
                            "severity": c.severity,
                        }
                        for c in cat.checks
                    ]
                }
                for cat in categories
            ]
        }
        console.print(json.dumps(output, indent=2))
        return
    
    all_passed = all(c.passed for c in categories)
    total_checks = sum(len(c.checks) for c in categories)
    passed_checks = sum(c.passed_count for c in categories)
    
    console.print("\n")
    
    for category in categories:
        console.print(f"\n{category.icon} [bold]{category.name}[/bold]")
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Status", width=3)
        table.add_column("Check")
        table.add_column("Message", style="dim")
        
        for check in category.checks:
            status = "[green]✓[/green]" if check.passed else "[red]✗[/red]" if check.severity == "error" else "[yellow]⚠[/yellow]"
            table.add_row(status, check.name, check.message)
        
        console.print(table)
    
    console.print("\n")
    if all_passed:
        console.print(Panel.fit(
            f"[green]✓ Production Ready! ({passed_checks}/{total_checks} checks passed)[/green]",
            title="🚀 Result"
        ))
    else:
        console.print(Panel.fit(
            f"[red]✗ Not Production Ready ({passed_checks}/{total_checks} checks passed)[/red]",
            title="🚀 Result"
        ))


def _check_lich_project():
    """Check if we're in a Lich project."""
    if not (Path(".lich").exists() or Path("backend").exists()):
        console.print("[red]Error: Not in a Lich project directory[/red]")
        raise typer.Exit(1)


class AutoFixer:
    """Auto-fix common production readiness issues."""
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.env_file = self.project_path / ".env"
        self.fixes_applied = []
    
    def _read_env(self) -> Dict[str, str]:
        """Read .env file."""
        env_vars = {}
        if self.env_file.exists():
            for line in self.env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    env_vars[key.strip()] = value.strip().strip('"\'')
        return env_vars
    
    def _write_env(self, env_vars: Dict[str, str]):
        """Write .env file."""
        lines = []
        if self.env_file.exists():
            # Preserve comments and structure
            for line in self.env_file.read_text().splitlines():
                if line.strip().startswith('#') or not line.strip():
                    lines.append(line)
                elif '=' in line:
                    key = line.split('=')[0].strip()
                    if key in env_vars:
                        lines.append(f"{key}={env_vars[key]}")
                        del env_vars[key]
                    else:
                        lines.append(line)
            # Add remaining new vars
            for key, value in env_vars.items():
                lines.append(f"{key}={value}")
        else:
            for key, value in env_vars.items():
                lines.append(f"{key}={value}")
        
        self.env_file.write_text('\n'.join(lines) + '\n')
    
    def fix_secret_key(self) -> bool:
        """Generate strong secret key."""
        import secrets as secrets_module
        env_vars = self._read_env()
        current = env_vars.get("SECRET_KEY", "")
        weak_patterns = ["changeme", "secret", "your-secret", "change-me"]
        
        if len(current) < 32 or any(p in current.lower() for p in weak_patterns):
            new_secret = secrets_module.token_urlsafe(48)
            env_vars["SECRET_KEY"] = new_secret
            self._write_env(env_vars)
            self.fixes_applied.append("Generated strong SECRET_KEY")
            return True
        return False
    
    def fix_jwt_secret(self) -> bool:
        """Generate strong JWT secret."""
        import secrets as secrets_module
        env_vars = self._read_env()
        
        for key in ["JWT_SECRET_KEY", "JWT_SECRET"]:
            if key in env_vars and len(env_vars[key]) < 32:
                env_vars[key] = secrets_module.token_urlsafe(48)
                self._write_env(env_vars)
                self.fixes_applied.append(f"Generated strong {key}")
                return True
        return False
    
    def fix_debug_false(self) -> bool:
        """Set DEBUG=false."""
        env_vars = self._read_env()
        if env_vars.get("DEBUG", "true").lower() in ("true", "1", "yes"):
            env_vars["DEBUG"] = "false"
            self._write_env(env_vars)
            self.fixes_applied.append("Set DEBUG=false")
            return True
        return False
    
    def fix_security_enabled(self) -> bool:
        """Set SECURITY_ENABLED=true."""
        env_vars = self._read_env()
        if env_vars.get("SECURITY_ENABLED", "false").lower() != "true":
            env_vars["SECURITY_ENABLED"] = "true"
            self._write_env(env_vars)
            self.fixes_applied.append("Set SECURITY_ENABLED=true")
            return True
        return False
    
    def run_all_fixes(self) -> List[str]:
        """Run all auto-fixes."""
        self.fix_secret_key()
        self.fix_jwt_secret()
        self.fix_debug_false()
        self.fix_security_enabled()
        return self.fixes_applied


@production_ready_app.callback(invoke_without_command=True)
def production_ready_command(
    ctx: typer.Context,
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
    fix: bool = typer.Option(False, "--fix", "-f", help="Auto-fix issues where possible"),
):
    """
    🚀 Check if your project is production-ready.
    
    Runs security, quality, and operations checks to ensure
    your project is ready for production deployment.
    
    Examples:
        lich production-ready           # Run all checks
        lich production-ready --fix     # Auto-fix issues
        lich production-ready --json    # JSON output for CI/CD
    """
    _check_lich_project()
    
    console.print(Panel.fit("🚀 Production Readiness Check", style="bold blue"))
    
    # Run auto-fixes first if requested
    if fix:
        console.print("\n[bold yellow]🔧 Running Auto-Fix...[/bold yellow]")
        fixer = AutoFixer()
        fixes = fixer.run_all_fixes()
        if fixes:
            for f in fixes:
                console.print(f"  [green]✓[/green] {f}")
        else:
            console.print("  [dim]No auto-fixes needed[/dim]")
        console.print()
    
    checker = ProductionReadinessChecker()
    categories = checker.run_all_checks()
    
    display_results(categories, output_json)
    
    # Exit with error if not production ready
    if not all(c.passed for c in categories):
        raise typer.Exit(1)
