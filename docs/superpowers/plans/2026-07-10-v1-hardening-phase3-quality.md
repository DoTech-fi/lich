# Lich v1 Hardening — Phase 3: Quality Sprint (v1.14.0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate code duplication, break up oversized functions, make every MCP tool unit-testable and long-running tools async, add mypy, and raise CLI test coverage toward 80%.

**Architecture:** Extract shared helpers into `cli/src/lich/commands/common.py`; decompose the four 180–244-line functions into focused module-level helpers; move MCP tool functions out of `register_*()` closures to module level (registration becomes a loop) and convert subprocess-heavy tools to `async def` on `asyncio.create_subprocess_exec`; new test files per untested command module using the existing `CliRunner` + fixture style.

**Tech Stack:** Python 3.10+, Typer, Rich, FastMCP (`mcp.server.fastmcp` — supports async tool functions natively), pytest + pytest-asyncio + pytest-mock + pytest-cov, mypy, ruff.

**Prerequisites:**
- Phases 1 (v1.13.0, security) and 2 (v1.13.1, correctness) are merged. Work on branch `hardening/phase3-quality` cut from `main` after the v1.13.1 merge.
- Line numbers in this plan are from commit `1346437`. Phases 1–2 may have shifted them — **always locate code by function name, not line number**.
- Phase 1 introduced `cli/src/lich/commands/_shell.py` (`run_local`, `run_remote` with `shlex.quote`). Do NOT modify it. `_shell.py` stays the runner for deploy's local/SSH security-sensitive calls; the new `common.run_command` (3-tuple) is the canonical generic runner for lint/git/security, and `common.run_command_ok` (bool) for ci. Do not create a third variant anywhere.
- All commands below run from `/Users/babak/codes/DoTech/lich-framework/cli` unless stated otherwise.

**Verification baseline before starting:**

Run: `pytest -q`
Expected: all tests pass (Phase 2 fixed the 5 failures). If anything fails, STOP and report — do not start Phase 3 on a red suite.

---

## Task 1: Create `commands/common.py` (shared helpers) — tests first

**Files:**
- Create: `cli/tests/test_common.py`
- Create: `cli/src/lich/commands/common.py`

**Background (read before coding):** there are currently 8 copies of `_check_lich_project` — 7 identical raising versions (deploy, lint, secret, backup, ci, security, production_ready) checking `.lich` OR `backend`, and one different version in `make.py` that returns `bool` and checks only `.lich`. Both behaviors must be preserved. `_run_command` exists in 4 flavors: git/lint (tuple, cwd param), security (tuple, capture param, no cwd), ci (bool, show_output param).

- [ ] **Step 1: Write the failing tests**

Create `cli/tests/test_common.py`:

```python
"""
Tests for lich.commands.common shared helpers.
"""
import pytest
import typer
from pathlib import Path

from lich.commands.common import (
    ensure_lich_project,
    is_lich_project,
    run_command,
    run_command_ok,
    check_tool_installed,
)


class TestProjectChecks:
    def test_ensure_lich_project_passes_in_project(self, in_lich_project):
        # .lich marker exists in fixture -> should not raise
        ensure_lich_project()

    def test_ensure_lich_project_passes_with_backend_only(self, temp_dir, monkeypatch):
        (temp_dir / "backend").mkdir()
        monkeypatch.chdir(temp_dir)
        ensure_lich_project()

    def test_ensure_lich_project_raises_outside_project(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        with pytest.raises(typer.Exit):
            ensure_lich_project()

    def test_is_lich_project_true_with_lich_marker(self, in_lich_project):
        assert is_lich_project() is True

    def test_is_lich_project_false_with_backend_only(self, temp_dir, monkeypatch):
        # is_lich_project mirrors make.py's stricter check: .lich only
        (temp_dir / "backend").mkdir()
        monkeypatch.chdir(temp_dir)
        assert is_lich_project() is False


class TestRunCommand:
    def test_run_command_success(self):
        code, out, err = run_command(["python3", "-c", "print('hello')"])
        assert code == 0
        assert "hello" in out
        assert err == ""

    def test_run_command_failure_code(self):
        code, out, err = run_command(["python3", "-c", "import sys; sys.exit(3)"])
        assert code == 3

    def test_run_command_missing_binary(self):
        code, out, err = run_command(["definitely-not-a-real-binary-xyz"])
        assert code == -1
        assert "Command not found" in err

    def test_run_command_respects_cwd(self, temp_dir):
        code, out, _ = run_command(
            ["python3", "-c", "import os; print(os.getcwd())"], cwd=temp_dir
        )
        assert code == 0
        assert str(temp_dir.resolve()) in out

    def test_run_command_ok_true_on_success(self):
        assert run_command_ok(["python3", "-c", "pass"], show_output=False) is True

    def test_run_command_ok_false_on_failure(self):
        assert run_command_ok(["python3", "-c", "import sys; sys.exit(1)"], show_output=False) is False

    def test_run_command_ok_false_on_missing_binary(self):
        assert run_command_ok(["definitely-not-a-real-binary-xyz"]) is False


class TestCheckToolInstalled:
    def test_existing_tool(self):
        assert check_tool_installed("python3") is True

    def test_missing_tool(self):
        assert check_tool_installed("definitely-not-a-real-binary-xyz") is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_common.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lich.commands.common'`

- [ ] **Step 3: Write the implementation**

Create `cli/src/lich/commands/common.py`:

```python
"""
Shared helpers for Lich CLI commands.

Single home for logic that was previously copy-pasted across command modules:
- project detection (ensure_lich_project / is_lich_project)
- generic subprocess runners (run_command / run_command_ok)
- tool availability checks (check_tool_installed)

Security-sensitive local/remote execution for deploy lives in _shell.py — do
not merge the two: _shell handles quoting for remote scripts, common handles
plain local tool invocations.
"""
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()


def ensure_lich_project() -> None:
    """Exit with code 1 if the cwd is not a Lich project (.lich or backend/)."""
    if not (Path(".lich").exists() or Path("backend").exists()):
        console.print("[red]Error: Not in a Lich project directory[/red]")
        raise typer.Exit(1)


def is_lich_project() -> bool:
    """Return True if the cwd has a .lich marker (strict check used by make)."""
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        return False
    return True


def run_command(
    cmd: list, cwd: Optional[Path] = None, capture: bool = True
) -> tuple[int, str, str]:
    """Run a command; return (exit_code, stdout, stderr). -1 if binary missing."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            cwd=cwd or Path.cwd(),
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def run_command_ok(
    cmd: list, cwd: Optional[Path] = None, show_output: bool = True
) -> bool:
    """Run a command; return True on exit code 0. Prints error if binary missing."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or Path.cwd(),
            capture_output=not show_output,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        console.print(f"[red]Command not found: {cmd[0]}[/red]")
        return False


def check_tool_installed(tool: str) -> bool:
    """Return True if `tool` is on PATH (shutil.which, no subprocess)."""
    return shutil.which(tool) is not None
```

Note: `is_lich_project` prints the make.py-style error itself, matching current make.py behavior so its call sites stay one-liners. `check_tool_installed` replaces `which`-subprocess with `shutil.which` — same semantics, no process spawn.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_common.py -v`
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add tests/test_common.py src/lich/commands/common.py
git commit -m "feat(cli): add commands/common.py with shared project/subprocess helpers"
```

---

## Task 2: Migrate all `_check_lich_project` copies to common

**Files:**
- Modify: `cli/src/lich/commands/deploy.py` (delete local `_check_lich_project`, ~line 64)
- Modify: `cli/src/lich/commands/lint.py` (~line 25)
- Modify: `cli/src/lich/commands/secret.py` (~line 26)
- Modify: `cli/src/lich/commands/backup.py` (~line 32)
- Modify: `cli/src/lich/commands/ci.py` (~line 40)
- Modify: `cli/src/lich/commands/security.py` (~line 30)
- Modify: `cli/src/lich/commands/production_ready.py` (~line 459)
- Modify: `cli/src/lich/commands/make.py` (~line 18)

- [ ] **Step 1: Replace the 7 raising copies**

In each of deploy.py, lint.py, secret.py, backup.py, ci.py, security.py, production_ready.py:

1. Delete the local function (all 7 are byte-identical):

```python
def _check_lich_project():
    """Check if we're in a Lich project."""
    if not (Path(".lich").exists() or Path("backend").exists()):
        console.print("[red]Error: Not in a Lich project directory[/red]")
        raise typer.Exit(1)
```

2. Add to the module's imports:

```python
from lich.commands.common import ensure_lich_project as _check_lich_project
```

The alias keeps every existing call site (`_check_lich_project()`) untouched — zero behavioral diff, minimal churn.

- [ ] **Step 2: Replace the make.py bool copy**

In `make.py`, delete:

```python
def _check_lich_project() -> bool:
    """Check if we're in a Lich project."""
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        return False
    return True
```

Add to make.py imports:

```python
from lich.commands.common import is_lich_project as _check_lich_project
```

Call sites (`if not _check_lich_project():` at ~lines 52, 182, 246, 321) stay untouched.

- [ ] **Step 3: Verify no local copies remain**

Run: `grep -rn "def _check_lich_project" src/lich/`
Expected: no output

- [ ] **Step 4: Run the full suite**

Run: `pytest -q`
Expected: all pass (test_make.py exercises the make path, test_seed/test_routes exercise raising path)

- [ ] **Step 5: Commit**

```bash
git add src/lich/commands/
git commit -m "refactor(cli): dedupe _check_lich_project (8 copies -> common)"
```

---

## Task 3: Migrate `_run_command` and `_check_tool_installed` copies to common

**Files:**
- Modify: `cli/src/lich/commands/git.py` (delete `_run_command` ~line 10)
- Modify: `cli/src/lich/commands/lint.py` (delete `_run_command` ~line 32, `_check_tool_installed` ~line 46)
- Modify: `cli/src/lich/commands/security.py` (delete `_run_command` ~line 37, `_check_tool_installed` ~line 51)
- Modify: `cli/src/lich/commands/ci.py` (delete `_run_command` ~line 47)

- [ ] **Step 1: git.py, lint.py**

Both have the identical tuple version with `cwd` param. Delete the local function and add:

```python
from lich.commands.common import run_command as _run_command
```

- [ ] **Step 2: security.py**

security.py's version has signature `_run_command(cmd: list, capture: bool = True)` (no `cwd`, always `Path.cwd()`). `common.run_command(cmd, cwd=None, capture=True)` is a superset — positional call sites like `_run_command(["bandit", ...])` keep working, and any `_run_command(cmd, capture=False)` call must be changed to keyword form `_run_command(cmd, capture=False)` (already keyword — verify with `grep -n "_run_command(" src/lich/commands/security.py`; if any call passes `capture` positionally as the 2nd arg, change it to `capture=`).

Delete the local function, add the same import as Step 1. Also delete `_check_tool_installed` from both lint.py and security.py and add:

```python
from lich.commands.common import check_tool_installed as _check_tool_installed
```

- [ ] **Step 3: ci.py**

ci.py's version returns bool. Delete it and add:

```python
from lich.commands.common import run_command_ok as _run_command
```

Signature match: `_run_command(cmd, cwd=..., show_output=...)` — identical parameter names, no call-site changes.

- [ ] **Step 4: Verify and run suite**

Run: `grep -rn "def _run_command\|def _check_tool_installed" src/lich/commands/`
Expected: no output

Run: `pytest -q`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/lich/commands/
git commit -m "refactor(cli): dedupe _run_command and _check_tool_installed into common"
```

---

## Task 4: Dedupe template download helpers (init.py / upgrade.py)

**Files:**
- Modify: `cli/src/lich/commands/common.py` (add template helpers)
- Modify: `cli/src/lich/commands/init.py` (delete `_get_local_template_path` ~line 26, `_download_template` ~line 35)
- Modify: `cli/src/lich/commands/upgrade.py` (delete same two, ~lines 35 and 44)
- Test: `cli/tests/test_common.py`

- [ ] **Step 1: Add failing test**

Append to `cli/tests/test_common.py`:

```python
class TestTemplateHelpers:
    def test_get_local_template_path_in_dev_checkout(self):
        from lich.commands.common import get_local_template_path
        # In this repo checkout, template/ exists next to cli/
        path = get_local_template_path()
        assert path is not None
        assert path.name == "template"
        assert path.exists()
```

Run: `pytest tests/test_common.py::TestTemplateHelpers -v`
Expected: FAIL with ImportError

- [ ] **Step 2: Add helpers to common.py**

The two copies differ only in the spinner text ("Downloading template..." vs "Downloading latest template...") and `Optional` annotation — merge to one with the generic text. Append to `common.py` (and extend its imports):

```python
import os
import tempfile
import zipfile

import requests
from rich.progress import Progress, SpinnerColumn, TextColumn

GITHUB_REPO = "DoTech-fi/lich"
GITHUB_BRANCH = "main"
TEMPLATE_URL = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"


def get_local_template_path() -> Optional[Path]:
    """Get local template path (repo checkout / development mode)."""
    dev_path = Path(__file__).parent.parent.parent.parent.parent / "template"
    if dev_path.exists():
        return dev_path
    return None


def download_template() -> str:
    """Download the project template from GitHub, return the extracted path."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Downloading template from GitHub...", total=None)

        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "lich.zip")

        try:
            response = requests.get(TEMPLATE_URL, stream=True, timeout=60)
            response.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.SSLError:
            console.print("[red]❌ SSL Certificate Error[/red]")
            console.print("[dim]Try running: /Applications/Python*/Install\\ Certificates.command[/dim]")
            console.print("[dim]Or: pip install certifi[/dim]")
            raise typer.Exit(1)
        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ Failed to download template: {e}[/red]")
            console.print("[dim]Check your internet connection.[/dim]")
            raise typer.Exit(1)

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            console.print("[red]❌ Downloaded file is not a valid zip![/red]")
            raise typer.Exit(1)

        extracted_dir = os.path.join(temp_dir, f"lich-{GITHUB_BRANCH}", "template")
        if not os.path.exists(extracted_dir):
            console.print("[red]❌ Template not found in downloaded archive![/red]")
            raise typer.Exit(1)

        return extracted_dir
```

- [ ] **Step 3: Update init.py and upgrade.py**

In both files: delete the local `_get_local_template_path` and `_download_template` definitions AND the now-unused module constants `GITHUB_REPO`/`GITHUB_BRANCH`/`TEMPLATE_URL` (check with grep whether anything else in the file uses them first: `grep -n "TEMPLATE_URL\|GITHUB_REPO\|GITHUB_BRANCH" src/lich/commands/init.py src/lich/commands/upgrade.py`). Add:

```python
from lich.commands.common import (
    get_local_template_path as _get_local_template_path,
    download_template as _download_template,
)
```

Remove imports that become unused in init.py/upgrade.py (`tempfile`, `zipfile`, `os`, `requests`, `Progress`, `SpinnerColumn`, `TextColumn` — verify each with grep before removing; upgrade.py still uses some elsewhere).

- [ ] **Step 4: Run suite + lint**

Run: `pytest -q && ruff check src/lich --ignore=E501`
Expected: tests pass, ruff reports no unused-import errors

- [ ] **Step 5: Commit**

```bash
git add src/lich/commands/ tests/test_common.py
git commit -m "refactor(cli): dedupe template download helpers into common"
```

---

## Task 5: Break up `deploy_setup` (212 lines → orchestrator + 5 helpers)

**Files:**
- Modify: `cli/src/lich/commands/deploy.py`
- Test: `cli/tests/test_deploy.py` (created in this task)

The split follows the function's existing "Step N" comments. All helpers are module-level, placed directly above `deploy_setup`. Bodies are moved verbatim except where noted.

- [ ] **Step 1: Write failing tests for the pure helpers**

Create `cli/tests/test_deploy.py`:

```python
"""
Tests for lich deploy command helpers.
"""
import pytest
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.deploy import (
    _extract_repo_info,
    _load_deploy_config,
    _save_deploy_config,
)


class TestRepoInfo:
    def test_ssh_github_format(self):
        provider, owner, repo = _extract_repo_info("git@github.com:DoTech-fi/lich.git")
        assert provider == "github"
        assert owner == "DoTech-fi"
        assert repo == "lich"

    def test_gitlab_format(self):
        provider, owner, repo = _extract_repo_info("git@gitlab.com:group/proj.git")
        assert provider == "gitlab"
        assert owner == "group"
        assert repo == "proj"


class TestDeployConfig:
    def test_load_missing_config_returns_empty(self, in_lich_project):
        assert _load_deploy_config() == {}

    def test_save_and_load_roundtrip(self, in_lich_project):
        cfg = {"production": {"connection": "manual", "host": "1.2.3.4"}}
        _save_deploy_config(cfg)
        assert _load_deploy_config() == cfg


class TestDeployCLI:
    def test_deploy_help(self, runner: CliRunner):
        result = runner.invoke(app, ["deploy", "--help"])
        assert result.exit_code == 0
        assert "setup" in result.output

    def test_deploy_init_unconfigured_env_fails(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["deploy", "init", "production"])
        assert result.exit_code == 1
        assert "not configured" in result.output.lower()
```

Note: `in_lich_project` fixture uses a `.lich` FILE, but `_save_deploy_config` does `DEPLOY_CONFIG_PATH.parent.mkdir(exist_ok=True)` on `.lich/` — this collides. In the two `TestDeployConfig` tests, first remove the marker file and create the dir:

```python
    @pytest.fixture(autouse=True)
    def lich_dir(self, in_lich_project):
        marker = Path(".lich")
        if marker.is_file():
            marker.unlink()
            marker.mkdir()
        return in_lich_project
```

(Place this fixture inside `TestDeployConfig` only.)

Run: `pytest tests/test_deploy.py -v`
Expected: PASS for helpers that already exist (`_extract_repo_info`, config roundtrip, CLI tests). This task's tests are regression protection for the refactor — they must pass BEFORE and AFTER the split. If any fail before the split, STOP and report.

- [ ] **Step 2: Extract helpers**

In `deploy.py`, add these module-level functions above `deploy_setup`, moving the corresponding blocks out of `deploy_setup` verbatim:

```python
def _prompt_environments() -> list[str]:
    """Step 1: which environments to configure."""
    console.print("\n[bold]Step 1: Select Environment[/bold]")
    env_choice = Prompt.ask(
        "Which environment?",
        choices=["staging", "production", "both"],
        default="production",
    )
    return ["staging", "production"] if env_choice == "both" else [env_choice]


def _configure_environment(env: str) -> dict:
    """Step 2 for one environment: connection, deploy path, runtime."""
    console.print(f"\n[bold cyan]{'━' * 40}[/bold cyan]")
    console.print(f"[bold cyan]  Configuring {env.upper()}[/bold cyan]")
    console.print(f"[bold cyan]{'━' * 40}[/bold cyan]")

    console.print("\n[bold]Step 2: Server Connection[/bold]")
    connection = Prompt.ask(
        "How do you connect?",
        choices=["ssh-config", "manual"],
        default="ssh-config",
    )
    env_config = {"connection": connection}

    if connection == "ssh-config":
        ssh_hosts = _get_ssh_config_hosts()
        if ssh_hosts:
            console.print(f"  [dim]Available: {', '.join(ssh_hosts[:8])}{'...' if len(ssh_hosts) > 8 else ''}[/dim]")
        ssh_name = Prompt.ask("SSH config name")
        env_config["ssh_name"] = ssh_name
        console.print("  Verifying connection...", end=" ")
        if _check_ssh_connection(ssh_name):
            console.print("[green]✓[/green]")
        else:
            console.print("[red]✗[/red]")
            console.print("  [yellow]Warning: Could not connect. Check your SSH config.[/yellow]")
    else:
        host = Prompt.ask("Server host/IP")
        user = Prompt.ask("SSH username", default="root")
        env_config["host"] = host
        env_config["user"] = user

    deploy_path = Prompt.ask("Deploy path on server", default="/opt/app")
    env_config["path"] = deploy_path

    runtime = Prompt.ask(
        "Runtime",
        choices=["docker-compose", "bare-metal"],
        default="docker-compose",
    )
    env_config["runtime"] = runtime
    return env_config


def _configure_git_repo(config: dict, environments: list[str], project_name: str) -> None:
    """Step 3: git repo + deploy key. Mutates config in place."""
    reconfigure_git = True
    if "git_repo" in config:
        console.print("\n[bold]Step 3: Git Repository[/bold]")
        console.print(f"  [dim]Current: {config['git_repo']}[/dim]")
        reconfigure_git = Confirm.ask("Reconfigure git settings?", default=False)

    if reconfigure_git and "git_repo" not in config:
        console.print("\n[bold]Step 3: Git Repository[/bold]")

    if not reconfigure_git:
        return

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True,
        )
        default_repo = result.stdout.strip() if result.returncode == 0 else "git@github.com:user/repo.git"
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        default_repo = "git@github.com:user/repo.git"

    git_repo = Prompt.ask("Git repo URL (SSH format)", default=default_repo)
    config["git_repo"] = git_repo

    is_private = Confirm.ask("Is this a private repo?", default=True)
    config["private_repo"] = is_private
    if not is_private:
        return

    console.print("\n[bold]🔑 SSH Deploy Key Setup[/bold]")
    console.print("  [dim]Recommended: Create a new deploy key (more secure)[/dim]")
    key_choice = Prompt.ask(
        "Use existing SSH key or create new deploy key?",
        choices=["create", "existing"],
        default="create",
    )

    if key_choice == "create":
        key_path, pub_key = _generate_deploy_key(environments[0], project_name)
        config["deploy_key_path"] = key_path
        console.print(f"  [green]✓ Created: {key_path}[/green]")

        provider, owner, repo = _extract_repo_info(git_repo)
        console.print("\n  [bold yellow]📋 Add this deploy key to GitHub:[/bold yellow]")
        console.print(Panel(pub_key, title="Public Key", border_style="cyan"))
        if provider == "github":
            console.print(f"  1. Go to: [link]https://github.com/{owner}/{repo}/settings/keys[/link]")
        else:
            console.print(f"  1. Go to: [link]https://gitlab.com/{owner}/{repo}/-/settings/repository[/link]")
        console.print("  2. Click 'Add deploy key'")
        console.print("  3. Paste the key above")
        console.print("  4. ✓ Enable 'Allow read access' only")
        Prompt.ask("\n  Press Enter when done", default="")
        console.print("  Verifying GitHub access...", end=" ")
        console.print("[green]✓[/green]")
    else:
        default_key = str(Path.home() / ".ssh" / "id_ed25519")
        key_path = Prompt.ask("Path to your SSH private key", default=default_key)
        if not Path(key_path).exists():
            console.print(f"  [red]Key not found: {key_path}[/red]")
            raise typer.Exit(1)
        config["deploy_key_path"] = key_path
        console.print(f"  [green]✓ Using: {key_path}[/green]")
        console.print("  [yellow]Make sure this key has access to the repository[/yellow]")


def _configure_domains(project_name: str) -> dict:
    """Step 4: domain configuration."""
    console.print("\n[bold]Step 4: Domain Configuration[/bold]")
    domain = Prompt.ask("Main domain", default=f"{project_name}.com")
    api_subdomain = Prompt.ask("API subdomain", default=f"api.{domain}")
    admin_subdomain = Prompt.ask("Admin subdomain", default=f"admin.{domain}")
    return {"main": domain, "api": api_subdomain, "admin": admin_subdomain}


def _print_setup_summary(config: dict) -> None:
    """Configuration summary + next steps."""
    console.print("\n[bold]Configuration Summary:[/bold]")
    for env_name, cfg in config.items():
        if not isinstance(cfg, dict) or env_name in RESERVED_CONFIG_KEYS:
            continue
        if cfg.get("connection") == "ssh-config":
            console.print(f"  {env_name}: SSH → {cfg.get('ssh_name')} → {cfg.get('path')}")
        else:
            console.print(f"  {env_name}: {cfg.get('user')}@{cfg.get('host')} → {cfg.get('path')}")

    if config.get("domains"):
        console.print(f"  Domains: {config['domains'].get('main')}")

    console.print("\n[bold]Next Steps:[/bold]")
    console.print("  1. Run [cyan]lich deploy init production[/cyan] to setup the server")
    console.print("  2. Run [cyan]lich deploy prod backend[/cyan] to deploy")
```

Then reduce `deploy_setup` to the orchestrator (keep its decorator/docstring exactly as-is):

```python
def deploy_setup():
    """
    (keep existing docstring)
    """
    _check_lich_project()
    console.print(Panel.fit("🛠️ Deploy Setup", style="bold blue"))

    project_name = Path.cwd().name
    config = _load_deploy_config()

    environments = _prompt_environments()
    for env in environments:
        config[env] = _configure_environment(env)

    _configure_git_repo(config, environments, project_name)
    config["domains"] = _configure_domains(project_name)

    console.print("\n[bold]Step 5: Environment Variables[/bold]")
    if Confirm.ask("Configure environment variables now?", default=True):
        for env in environments:
            env_vars = _collect_env_vars(env)
            if env_vars:
                _save_env_file(env, env_vars)
                config[env]["env_file"] = f".lich/deploy.{env}.env"

    _save_deploy_config(config)
    console.print(f"\n[green]✓ Saved to {DEPLOY_CONFIG_PATH}[/green]")
    _print_setup_summary(config)
```

IMPORTANT behavioral preservation notes:
- Original code sets `config["domains"]` unconditionally — the orchestrator does the same.
- If Phase 1 changed any of these blocks (validation on `deploy_path`, `git_url`), move the CURRENT block content, not the code shown here — this plan shows pre-Phase-1 bodies as orientation. The split boundaries stay the same.
- Also note the bare `except Exception` in the git-remote block was narrowed here to `(subprocess.SubprocessError, FileNotFoundError, OSError)` — this is one of the Task 10 sites, done during the move to avoid touching the same lines twice. Skip it in Task 10.

- [ ] **Step 3: Verify size and suite**

Run: `python3 - <<'EOF'
import ast, pathlib
src = pathlib.Path("src/lich/commands/deploy.py").read_text()
for node in ast.walk(ast.parse(src)):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        n = node.end_lineno - node.lineno
        if n > 80:
            print(f"{node.name}: {n} lines")
EOF`
Expected: `deploy_init` may still print (next task); `deploy_setup` must NOT print.

Run: `pytest tests/test_deploy.py -q && pytest -q`
Expected: all pass

- [ ] **Step 4: Commit**

```bash
git add src/lich/commands/deploy.py tests/test_deploy.py
git commit -m "refactor(cli): split deploy_setup into focused helpers"
```

---

## Task 6: Break up `deploy_init` (244 lines → orchestrator + 7 helpers)

**Files:**
- Modify: `cli/src/lich/commands/deploy.py`

Same recipe. The seven blocks (each currently a "Step N" section) become module-level helpers. Move bodies verbatim (post-Phase-1 content).

- [ ] **Step 1: Extract helpers**

```python
def _resolve_ssh_target(config: dict, environment: str) -> tuple[str, str, str]:
    """Resolve (ssh_host, deploy_path, git_repo) for an environment or exit."""
    if environment not in config:
        console.print(f"[red]Environment '{environment}' not configured[/red]")
        console.print("[yellow]Run 'lich deploy setup' first[/yellow]")
        raise typer.Exit(1)

    env_config = config[environment]
    if env_config.get("connection") == "ssh-config":
        ssh_host = env_config.get("ssh_name")
    else:
        ssh_host = f"{env_config.get('user')}@{env_config.get('host')}"
    return ssh_host, env_config.get("path", "/opt/app"), config.get("git_repo")


def _ensure_docker(progress, ssh_host: str) -> None:
    """Step 2: check/install Docker on the server."""
    task = progress.add_task("[cyan]Checking Docker...", total=None)
    code, output = _run_ssh_command(ssh_host, "docker --version")
    if code != 0:
        progress.update(task, description="[yellow]Installing Docker...")
        docker_install_cmd = """
            curl -fsSL https://get.docker.com | sh && \\
            systemctl enable docker && \\
            systemctl start docker && \\
            curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \\
            chmod +x /usr/local/bin/docker-compose
        """
        code, output = _run_ssh_command(ssh_host, docker_install_cmd, timeout=300)
        if code != 0:
            progress.stop()
            console.print(f"[red]✗ Failed to install Docker: {output}[/red]")
            raise typer.Exit(1)
        progress.update(task, description="[green]✓ Docker installed")
    else:
        progress.update(task, description="[green]✓ Docker already installed")
    progress.remove_task(task)
    console.print("[green]✓[/green] Docker ready")


def _setup_deploy_key_on_server(progress, config: dict, ssh_host: str) -> None:
    """Step 3: copy deploy key to server and configure SSH."""
    task = progress.add_task("[cyan]Setting up deploy key...", total=None)
    key_path = config.get("deploy_key_path")

    scp_cmd = ["scp", key_path, f"{ssh_host}:~/.ssh/deploy_key"]
    result = subprocess.run(scp_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        progress.stop()
        console.print(f"[red]✗ Failed to copy deploy key: {result.stderr}[/red]")
        raise typer.Exit(1)

    ssh_setup_cmd = """
        chmod 600 ~/.ssh/deploy_key && \\
        echo 'Host github.com
            IdentityFile ~/.ssh/deploy_key
            StrictHostKeyChecking accept-new' >> ~/.ssh/config && \\
        chmod 600 ~/.ssh/config
    """
    _run_ssh_command(ssh_host, ssh_setup_cmd)
    progress.update(task, description="[green]✓ Deploy key configured")
    progress.remove_task(task)
    console.print("[green]✓[/green] Deploy key configured on server")


def _clone_repo_on_server(progress, ssh_host: str, deploy_path: str, git_repo: str) -> None:
    """Step 4: clone or pull the repository. (Phase 1 quoted these vars — keep its version.)"""
    task = progress.add_task("[cyan]Cloning repository...", total=None)
    clone_cmd = f"""
        mkdir -p {deploy_path} && \\
        if [ -d "{deploy_path}/.git" ]; then
            cd {deploy_path} && git pull
        else
            rm -rf {deploy_path}/* && \\
            git clone {git_repo} {deploy_path}
        fi
    """
    code, output = _run_ssh_command(ssh_host, clone_cmd)
    if code != 0:
        progress.stop()
        console.print(f"[red]✗ Failed to clone repository: {output}[/red]")
        raise typer.Exit(1)
    progress.update(task, description="[green]✓ Repository cloned")
    progress.remove_task(task)
    console.print(f"[green]✓[/green] Repository cloned to {deploy_path}")


def _copy_env_file_to_server(progress, env_config: dict, ssh_host: str, deploy_path: str) -> None:
    """Step 5: copy environment file if configured."""
    env_file = env_config.get("env_file")
    if not (env_file and Path(env_file).exists()):
        return
    task = progress.add_task("[cyan]Copying environment file...", total=None)
    scp_cmd = ["scp", env_file, f"{ssh_host}:{deploy_path}/.env"]
    result = subprocess.run(scp_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        progress.update(task, description="[green]✓ Environment file copied")
        console.print("[green]✓[/green] Environment file copied")
    else:
        progress.update(task, description="[yellow]⚠ Failed to copy env file")
        console.print(f"[yellow]⚠[/yellow] Failed to copy env file: {result.stderr}")
    progress.remove_task(task)


def _setup_traefik_on_server(progress, config: dict, ssh_host: str, deploy_path: str) -> None:
    """Step 6: write traefik config + letsencrypt storage. Move the existing
    traefik_setup_cmd heredoc block verbatim (including the acme email using
    the main domain)."""
    if not config.get("domains"):
        return
    task = progress.add_task("[cyan]Configuring Traefik...", total=None)
    domains = config.get("domains", {})
    main_domain = domains.get("main", "example.com")
    traefik_setup_cmd = f"""
        mkdir -p {deploy_path}/traefik && \\
        cat > {deploy_path}/traefik/traefik.yml << 'EOF'
api:
  dashboard: true

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@{main_domain}
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    exposedByDefault: false
EOF
        mkdir -p {deploy_path}/letsencrypt && \\
        touch {deploy_path}/letsencrypt/acme.json && \\
        chmod 600 {deploy_path}/letsencrypt/acme.json
    """
    _run_ssh_command(ssh_host, traefik_setup_cmd)
    progress.update(task, description="[green]✓ Traefik configured")
    progress.remove_task(task)
    console.print("[green]✓[/green] Traefik configured with Let's Encrypt")


def _start_services_on_server(progress, ssh_host: str, deploy_path: str) -> None:
    """Step 7: docker compose pull && up -d."""
    task = progress.add_task("[cyan]Starting services...", total=None)
    start_cmd = f"""
        cd {deploy_path} && \\
        docker compose pull && \\
        docker compose up -d
    """
    code, output = _run_ssh_command(ssh_host, start_cmd, timeout=180)
    if code != 0:
        progress.update(task, description="[yellow]⚠ Services may need manual start")
        console.print(f"[yellow]⚠[/yellow] Could not auto-start: {output}")
    else:
        progress.update(task, description="[green]✓ Services started")
        console.print("[green]✓[/green] Services started")
    progress.remove_task(task)


def _print_init_summary(config: dict) -> None:
    """Final summary with URLs."""
    console.print("\n" + "═" * 50)
    console.print("[bold green]✓ Server initialized successfully![/bold green]")
    if config.get("domains"):
        domains = config.get("domains", {})
        console.print("\n[bold]🌐 Your app should be available at:[/bold]")
        console.print(f"   https://{domains.get('main')}")
        console.print(f"   https://{domains.get('api')}")
        if domains.get("admin"):
            console.print(f"   https://{domains.get('admin')}")
    console.print("\n[dim]Note: DNS propagation may take a few minutes.[/dim]")
    console.print("[dim]Run 'lich deploy status' to check server status.[/dim]")
```

New `deploy_init` body (keep decorator, signature, and docstring exactly as-is):

```python
    _check_lich_project()
    config = _load_deploy_config()
    ssh_host, deploy_path, git_repo = _resolve_ssh_target(config, environment)
    env_config = config[environment]

    console.print(Panel.fit(f"🚀 Initializing {environment.upper()} Server", style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Connecting to server...", total=None)
        if not _check_ssh_connection(ssh_host):
            progress.stop()
            console.print(f"[red]✗ Cannot connect to {ssh_host}[/red]")
            raise typer.Exit(1)
        progress.update(task, description="[green]✓ Connected to server")
        progress.remove_task(task)
        console.print(f"[green]✓[/green] Connected to {ssh_host}")

        if not skip_docker:
            _ensure_docker(progress, ssh_host)

        if config.get("private_repo") and config.get("deploy_key_path"):
            _setup_deploy_key_on_server(progress, config, ssh_host)

        _clone_repo_on_server(progress, ssh_host, deploy_path, git_repo)
        _copy_env_file_to_server(progress, env_config, ssh_host, deploy_path)
        _setup_traefik_on_server(progress, config, ssh_host, deploy_path)
        _start_services_on_server(progress, ssh_host, deploy_path)

    _print_init_summary(config)
```

REMINDER: if Phase 1 replaced `_run_ssh_command`/f-string blocks with `_shell.run_remote` + quoting, move THAT code into the helpers — do not resurrect the unquoted f-strings shown here.

- [ ] **Step 2: Verify no >80-line functions remain in deploy.py**

Run the same AST one-liner from Task 5 Step 3.
Expected: no output for deploy.py

Run: `pytest -q`
Expected: all pass

- [ ] **Step 3: Commit**

```bash
git add src/lich/commands/deploy.py
git commit -m "refactor(cli): split deploy_init into focused helpers"
```

---

## Task 7: Break up `upgrade_project` (201 lines) and add upgrade tests

**Files:**
- Modify: `cli/src/lich/commands/upgrade.py`
- Create: `cli/tests/test_upgrade.py`

- [ ] **Step 1: Write regression tests (must pass before AND after)**

Create `cli/tests/test_upgrade.py`:

```python
"""
Tests for lich upgrade command.
"""
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.common import get_local_template_path


class TestUpgrade:
    def test_upgrade_help(self, runner: CliRunner):
        result = runner.invoke(app, ["upgrade", "--help"])
        assert result.exit_code == 0
        assert "--dry-run" in result.output

    def test_upgrade_fails_outside_project(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["upgrade", "--local"])
        assert result.exit_code == 1
        assert "not a lich project" in result.output.lower()

    def test_upgrade_dry_run_local(self, runner: CliRunner, in_lich_project):
        # dev checkout has template/ so --local resolves without network
        assert get_local_template_path() is not None
        result = runner.invoke(app, ["upgrade", "--dry-run", "--local"])
        assert result.exit_code == 0
        assert "dry run" in result.output.lower()
        assert ".lich/rules" in result.output
```

Run: `pytest tests/test_upgrade.py -v`
Expected: 3 passed (against current code). If not, STOP and report.

- [ ] **Step 2: Extract helpers**

Move the two nested functions (`copy_and_render`, `recursive_copy`) to module level and extract three more. New module-level functions in upgrade.py:

```python
SYNC_TARGETS = [
    (".lich/rules", ".lich/rules"),
    (".lich/workflows", ".lich/workflows"),
    (".lich/LICH_AI_PROMPT.md", ".lich/LICH_AI_PROMPT.md"),
    ("AGENTS.md", "AGENTS.md"),
    ("CLAUDE.md", "CLAUDE.md"),
    # .github/workflows intentionally excluded — project-specific, rendered at init
]

MISSING_TARGETS = [
    ("apps/admin/.eslintrc.json", "apps/admin/.eslintrc.json"),
    ("apps/web/.eslintrc.json", "apps/web/.eslintrc.json"),
    ("apps/landing/.eslintrc.json", "apps/landing/.eslintrc.json"),
]


def _copy_and_render(src: Path, dst: Path) -> bool:
    """Copy a template file, substituting the project slug and unescaping
    GitHub Actions variables. Returns True if rendered as text."""
    try:
        content = src.read_text(encoding="utf-8")
        current_slug = Path.cwd().name
        content = content.replace("{{ cookiecutter.project_slug }}", current_slug)
        content = content.replace("{{cookiecutter.project_slug}}", current_slug)
        content = content.replace('{{ "{{" }}', '{{')
        content = content.replace('{{ "}}" }}', '}}')
        dst.write_text(content, encoding="utf-8")
        return True
    except UnicodeDecodeError:
        shutil.copy2(src, dst)
        return False


def _recursive_copy(src_dir: Path, dst_dir: Path) -> None:
    """Recursively copy and render template files."""
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    dst_dir.mkdir(parents=True)
    for item in src_dir.iterdir():
        dst_item = dst_dir / item.name
        if item.is_dir():
            _recursive_copy(item, dst_item)
        else:
            if item.suffix in ['.md', '.yml', '.yaml', '.json', '.py', '.js', '.ts', '.css', '.html']:
                _copy_and_render(item, dst_item)
            else:
                shutil.copy2(item, dst_item)


def _resolve_template_source(local: bool, to_version: str) -> Path:
    """Pick local dev template or download; return the project-slug source dir or exit."""
    local_path = _get_local_template_path()
    if local and local_path:
        template_base = str(local_path)
        console.print("[dim]Using local template (development mode)[/dim]")
    elif local_path and not to_version:
        console.print("[dim]Local dev template detected. Use --local to use it.[/dim]")
        template_base = _download_template()
    else:
        template_base = _download_template()

    source_dir = Path(template_base) / "{{cookiecutter.project_slug}}"
    if not source_dir.exists():
        console.print(f"[red]❌ Invalid template structure. Could not find project slug dir in {template_base}[/red]")
        raise typer.Exit(1)
    return source_dir


def _print_upgrade_preview() -> None:
    """List what will be overwritten / added."""
    console.print("\n[bold]The following components will be updated/overwritten:[/bold]")
    for src, dst in SYNC_TARGETS:
        exists = "exists" if Path(dst).exists() else "new"
        console.print(f"   • {dst} ({exists})")
    console.print("\n[bold]The following files will be added if missing:[/bold]")
    for src, dst in MISSING_TARGETS:
        if not Path(dst).exists():
            console.print(f"   • {dst} (missing - will be created)")


def _backup_lich_dir() -> None:
    """Snapshot .lich to .lich.backup before overwriting."""
    backup_path = Path(".lich.backup")
    if Path(".lich").exists():
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(".lich", backup_path)
        console.print("\n📦 [dim]Backed up .lich to .lich.backup[/dim]")


def _sync_files(source_dir: Path) -> None:
    """Overwrite SYNC_TARGETS from the template source."""
    console.print("\n[bold]Syncing files...[/bold]")
    version_file = Path(".lich/lich.version")
    version_file.parent.mkdir(parents=True, exist_ok=True)
    version_file.write_text(f"{__version__}\n")
    console.print(f"   ✅ Updated file: [cyan].lich/lich.version[/cyan] (v{__version__})")

    for src_rel, dst_rel in SYNC_TARGETS:
        src_path = source_dir / src_rel
        dst_path = Path(dst_rel)
        if not src_path.exists():
            console.print(f"   [yellow]⚠️ Source not found: {src_rel} (skipping)[/yellow]")
            continue
        try:
            if src_path.is_dir():
                _recursive_copy(src_path, dst_path)
                console.print(f"   ✅ Updated directory: [cyan]{dst_rel}[/cyan]")
            else:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                _copy_and_render(src_path, dst_path)
                console.print(f"   ✅ Updated file: [cyan]{dst_rel}[/cyan]")
        except (OSError, shutil.Error) as e:
            console.print(f"   [red]❌ Failed to update {dst_rel}: {e}[/red]")


def _inject_missing_files(source_dir: Path) -> None:
    """Create MISSING_TARGETS files that don't exist yet."""
    console.print("\n[bold]Checking for new framework files...[/bold]")
    for src_rel, dst_rel in MISSING_TARGETS:
        src_path = source_dir / src_rel
        dst_path = Path(dst_rel)
        if dst_path.exists() or not src_path.exists():
            continue
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            _copy_and_render(src_path, dst_path)
            console.print(f"   ✅ Created missing file: [cyan]{dst_rel}[/cyan]")
        except (OSError, shutil.Error) as e:
            console.print(f"   [red]❌ Failed to create {dst_rel}: {e}[/red]")
```

New `upgrade_project` body (keep decorator/signature/docstring):

```python
    if not local:
        _check_and_update_cli(dry_run=dry_run)

    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project (no .lich folder found)![/red]")
        raise typer.Exit(1)

    console.print("\n🔄 [bold blue]Lich Toolkit Upgrade[/bold blue]\n")
    console.print(f"[bold]Installed CLI Version:[/bold] v{__version__}")

    source_dir = _resolve_template_source(local, to_version)
    _print_upgrade_preview()

    if dry_run:
        console.print("\n[yellow]Dry run mode - no changes will be made.[/yellow]")
        return

    if not force:
        console.print()
        if not Confirm.ask("Proceed with upgrade? (This will overwrite the listed files)"):
            console.print("[yellow]Upgrade cancelled.[/yellow]")
            raise typer.Exit(0)

    _backup_lich_dir()
    _sync_files(source_dir)
    _inject_missing_files(source_dir)

    console.print("\n[green]✅ Project configuration upgraded successfully![/green]")
    console.print(Panel.fit(
        "[bold yellow]⚠️  Important:[/bold yellow] You MUST run [bold cyan]lich setup[/bold cyan] now.\n\n"
        "Then, [bold red]RESTART[/bold red] this AI tool (Antigravity/Cursor/VSCode) to apply changes.",
        border_style="yellow",
        title="Next Steps"
    ))
```

Note: the two `except Exception` sites at old lines 361/381 are narrowed to `(OSError, shutil.Error)` as part of this move — skip them in Task 10.

- [ ] **Step 3: Verify**

Run: `pytest tests/test_upgrade.py -q && pytest -q`
Expected: all pass. Also run the AST size check from Task 5 Step 3 against upgrade.py — no function > 80 lines.

- [ ] **Step 4: Commit**

```bash
git add src/lich/commands/upgrade.py tests/test_upgrade.py
git commit -m "refactor(cli): split upgrade_project into module-level helpers"
```

---

## Task 8: Break up `ci_setup` and factor ci_web/ci_admin/ci_landing

**Files:**
- Modify: `cli/src/lich/commands/ci.py`
- Create: `cli/tests/test_ci_command.py`

- [ ] **Step 1: Write failing/regression tests**

Create `cli/tests/test_ci_command.py`:

```python
"""
Tests for lich ci command helpers.
"""
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.ci import _write_file_if_not_exists, _add_to_gitignore


class TestCIHelpers:
    def test_write_file_if_not_exists_creates(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        target = temp_dir / ".actrc"
        _write_file_if_not_exists(target, "content-a\n", ".actrc")
        assert target.read_text() == "content-a\n"

    def test_write_file_if_not_exists_preserves(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        target = temp_dir / ".actrc"
        target.write_text("original\n")
        _write_file_if_not_exists(target, "new-content\n", ".actrc")
        assert target.read_text() == "original\n"

    def test_add_to_gitignore(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        _add_to_gitignore([".secrets", ".ci-env"])
        content = Path(".gitignore").read_text()
        assert ".secrets" in content
        assert ".ci-env" in content


class TestCICLI:
    def test_ci_help_lists_apps(self, runner: CliRunner):
        result = runner.invoke(app, ["ci", "--help"])
        assert result.exit_code == 0
        for sub in ("setup", "backend", "web", "admin", "landing"):
            assert sub in result.output

    def test_ci_web_outside_project_fails(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["ci", "web"])
        assert result.exit_code == 1
```

Run: `pytest tests/test_ci_command.py -v`
Expected: 5 passed against current code (these are regression anchors). If `_add_to_gitignore`'s real behavior differs (e.g. requires existing .gitignore), read the function at ci.py:387 and adjust the test to the ACTUAL current behavior before proceeding.

- [ ] **Step 2: Extract ci_setup helpers**

Split along the existing "Step N" comments into module-level functions (bodies moved verbatim):

```python
def _detect_system() -> tuple[str, bool, str, str]:
    """Step 1: return (os_name, is_arm, os_display, arch_display)."""
    import platform
    os_name = platform.system()
    machine = platform.machine().lower()
    is_arm = machine in ("arm64", "aarch64")
    is_intel = machine in ("x86_64", "amd64", "i386", "i686")
    os_display = {"Darwin": "macOS", "Linux": "Linux", "Windows": "Windows"}.get(os_name, os_name)
    arch_display = "ARM (Apple Silicon)" if is_arm else "Intel/AMD (x86_64)" if is_intel else machine
    console.print(f"  📍 OS: [bold]{os_display}[/bold]")
    console.print(f"  🔧 Architecture: [bold]{arch_display}[/bold]")
    return os_name, is_arm, os_display, arch_display


def _ensure_docker_and_act() -> None:
    """Steps 2-3: verify Docker is running and act installed (offer install)."""
    console.print("\n[bold]Step 2: Checking Docker...[/bold]")
    if not check_docker_running():
        show_docker_not_running_error()
        raise typer.Exit(1)
    console.print("[green]✓ Docker is running[/green]")

    console.print("\n[bold]Step 3: Checking act...[/bold]")
    if not check_act_installed():
        console.print("[yellow]act is not installed[/yellow]")
        install_now = typer.confirm("Would you like to install act now?", default=True)
        if install_now:
            if not install_act():
                raise typer.Exit(1)
        else:
            show_act_not_installed_error()
            raise typer.Exit(1)
    else:
        console.print("[green]✓ act is installed[/green]")


def _create_actrc(os_name: str, is_arm: bool) -> Path:
    """Step 4: write .actrc (if missing) and return its path."""
    console.print("\n[bold]Step 4: Creating .actrc config...[/bold]")
    actrc_lines = []
    if os_name == "Darwin" and is_arm:
        actrc_lines.append("--container-architecture=linux/amd64")
        console.print("  📦 ARM Mac detected → using linux/amd64 containers")
    actrc_lines.append("--reuse")
    actrc_lines.append("--secret-file=.secrets")
    console.print("  ♻️  Container reuse enabled")
    console.print("  🔐 Secrets file: .secrets")
    actrc_path = Path.cwd() / ".actrc"
    _write_file_if_not_exists(actrc_path, "\n".join(actrc_lines) + "\n", ".actrc")
    return actrc_path


def _create_secrets_file() -> None:
    """Step 5: write .secrets template + gitignore entries + notice.
    Move the existing secrets_content block, _write_file_if_not_exists call,
    _add_to_gitignore call, and the IMPORTANT notice prints here verbatim."""
    ...


def _maybe_create_optional_file(
    actrc_path: Path, step_title: str, description_lines: list[str],
    prompt: str, filename: str, content: str, actrc_flag: str,
) -> bool:
    """Steps 6-7 shared shape: optionally create .ci-vars / .ci-env and register in .actrc."""
    console.print(f"\n[bold]{step_title}[/bold]")
    for line in description_lines:
        console.print(f"  [dim]{line}[/dim]")
    if not typer.confirm(prompt, default=False):
        return False
    path = Path.cwd() / filename
    _write_file_if_not_exists(path, content, filename)
    with open(actrc_path, "a") as f:
        f.write(f"{actrc_flag}={filename}\n")
    console.print(f"  [green]✓ Added {actrc_flag}={filename} to .actrc[/green]")
    return True
```

For `_create_secrets_file`, the `...` above means: move the existing Step 5 block from `ci_setup` verbatim (the `secrets_content` heredoc string, `_write_file_if_not_exists(secrets_path, ...)`, `_add_to_gitignore([".secrets", ".ci-env"])`, and the three "IMPORTANT" console prints). Do not retype it — cut and paste from the current function.

New `ci_setup` body (keep decorator/docstring):

```python
    console.print(Panel.fit("🛠️ Setting up act for Local CI", style="bold blue"))

    console.print("\n[bold]Step 1: Detecting System...[/bold]")
    os_name, is_arm, os_display, arch_display = _detect_system()

    _ensure_docker_and_act()
    actrc_path = _create_actrc(os_name, is_arm)
    _create_secrets_file()

    create_vars = _maybe_create_optional_file(
        actrc_path,
        "Step 6: CI Variables (optional)...",
        ["Variables are for non-sensitive configuration:", "  • API_URL, APP_NAME, NODE_ENV", "  • These CAN be committed to git"],
        "Create .ci-vars file?",
        ".ci-vars",
        '''# CI Variables - Safe to commit
# Non-sensitive configuration for CI

NODE_ENV=test
APP_NAME=myapp
# API_URL=https://api.example.com
''',
        "--var-file",
    )
    create_env = _maybe_create_optional_file(
        actrc_path,
        "Step 7: CI Environment (optional)...",
        ["Environment file for container environment variables:", "  • DEBUG=true, LOG_LEVEL=info", "  • May contain sensitive values - added to .gitignore"],
        "Create .ci-env file?",
        ".ci-env",
        '''# CI Environment Variables
# These are passed to the container

DEBUG=false
LOG_LEVEL=info
# DATABASE_URL=postgresql://localhost/test
''',
        "--env-file",
    )

    _print_ci_setup_summary(os_display, arch_display, os_name, is_arm, create_vars, create_env)
```

And extract the summary block into:

```python
def _print_ci_setup_summary(os_display: str, arch_display: str, os_name: str,
                            is_arm: bool, create_vars: bool, create_env: bool) -> None:
    """Final panel. Move the existing summary_lines block verbatim."""
```

(Move the existing summary construction + `console.print(Panel.fit(...))` into it.)

- [ ] **Step 3: Factor the three identical app commands**

In ci.py, add one shared implementation and make the three commands thin wrappers:

```python
def _run_app_ci(
    app_name: str,
    workflow: str,
    job: str,
    display: str,
    local: bool,
    verbose: bool,
    quiet: bool,
    insecure_secrets: bool,
    secret: Optional[list[str]],
    var: Optional[list[str]],
) -> None:
    """Shared CI runner for the three frontend apps."""
    _check_lich_project()
    if local:
        console.print(Panel.fit(f"🔄 {display} CI (Local)", style="bold blue"))
        if not run_frontend_ci(app_name):
            raise typer.Exit(1)
    else:
        console.print(Panel.fit(f"🐳 {display} CI (Docker/act)", style="bold blue"))
        if not ensure_act_ready():
            raise typer.Exit(1)
        if not run_act_workflow(workflow, job=job, verbose=verbose, quiet=quiet,
                                insecure_secrets=insecure_secrets, secrets=secret, vars=var):
            raise typer.Exit(1)
    console.print(f"\n[green]✓ {display} CI passed![/green]")


@ci_app.command(name="web")
def ci_web(
    local: bool = typer.Option(False, "--local", "-l", help="Run locally (without Docker)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode"),
    insecure_secrets: bool = typer.Option(False, "--insecure-secrets", help="Show secrets in logs"),
    secret: Optional[list[str]] = typer.Option(None, "--secret", "-s", help="Secret KEY=VALUE (repeatable)"),
    var: Optional[list[str]] = typer.Option(None, "--var", help="Variable KEY=VALUE (repeatable)"),
):
    """Run CI for web app only."""
    _run_app_ci("web", "ci-web.yml", "web-test", "Web App", local, verbose, quiet, insecure_secrets, secret, var)


@ci_app.command(name="admin")
def ci_admin(
    local: bool = typer.Option(False, "--local", "-l", help="Run locally (without Docker)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode"),
    insecure_secrets: bool = typer.Option(False, "--insecure-secrets", help="Show secrets in logs"),
    secret: Optional[list[str]] = typer.Option(None, "--secret", "-s", help="Secret KEY=VALUE (repeatable)"),
    var: Optional[list[str]] = typer.Option(None, "--var", help="Variable KEY=VALUE (repeatable)"),
):
    """Run CI for admin panel only."""
    _run_app_ci("admin", "ci-admin.yml", "admin-test", "Admin Panel", local, verbose, quiet, insecure_secrets, secret, var)


@ci_app.command(name="landing")
def ci_landing(
    local: bool = typer.Option(False, "--local", "-l", help="Run locally (without Docker)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode"),
    insecure_secrets: bool = typer.Option(False, "--insecure-secrets", help="Show secrets in logs"),
    secret: Optional[list[str]] = typer.Option(None, "--secret", "-s", help="Secret KEY=VALUE (repeatable)"),
    var: Optional[list[str]] = typer.Option(None, "--var", help="Variable KEY=VALUE (repeatable)"),
):
    """Run CI for landing page only."""
    _run_app_ci("landing", "ci-landing.yml", "landing-test", "Landing Page", local, verbose, quiet, insecure_secrets, secret, var)
```

If Phase 2 added `lich ci all` as a CLI command, route it through `_run_app_ci` per app too.

- [ ] **Step 4: Verify**

Run: `pytest tests/test_ci_command.py -q && pytest -q`
Expected: all pass. AST size check on ci.py — no function > 80 lines.

- [ ] **Step 5: Commit**

```bash
git add src/lich/commands/ci.py tests/test_ci_command.py
git commit -m "refactor(cli): split ci_setup, factor ci web/admin/landing into shared runner"
```

---

## Task 9: Exception hygiene — narrow the remaining bare `except Exception` sites

**Files:**
- Modify: `cli/src/lich/version_check.py`
- Modify: `cli/src/lich/commands/{backup,deploy,upgrade,ci_utils,version,setup,production_ready,dev,init,adopt,routes}.py`

Sites in `deploy.py` (git-remote block) and `upgrade.py` (sync/inject blocks) were already narrowed in Tasks 5–7. `make.py:718` looks like a site but is INSIDE a generated-code template string (Celery job template) — leave it alone. `seed.py:130` executes arbitrary user seeder modules, so `except Exception` is legitimate there — keep it, but add a comment `# intentionally broad: runs user-authored seeder code` above it.

- [ ] **Step 1: Apply the narrowing table**

Locate each by function context (line numbers approximate):

| File / context | Old | New |
|---|---|---|
| `version_check.py:62` (PyPI version check + parse; comment says "If parsing fails, ignore.") | `except Exception:` `pass` | `except (requests.RequestException, KeyError, ValueError):` `pass` — add `import requests` if not present |
| `backup.py:87` (`_detect_databases` compose parse) | `except Exception as e:` | `except (yaml.YAMLError, OSError, KeyError) as e:` |
| `deploy.py:117` (`_run_ssh_command`) | `except Exception as e:` `return 1, str(e)` | `except OSError as e:` `return 1, str(e)` (TimeoutExpired already handled above) |
| `upgrade.py:136` (`_parse changelog versions`) | `except Exception:` | `except (OSError, ValueError, KeyError):` |
| `upgrade.py:159` (PyPI update check) | `except Exception as e:` | `except (requests.RequestException, KeyError, version.InvalidVersion) as e:` — `version` here is `packaging.version`, already imported in that function's scope; verify with grep |
| `ci_utils.py:184` (`install_act` subprocess) | `except Exception as e:` | `except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:` |
| `version.py:36` (PROJECT_CONFIG.yaml read) | `except Exception:` `pass` | `except (yaml.YAMLError, OSError):` `pass` |
| `version.py:110` (changelog parse — same shape as upgrade.py:136) | `except Exception:` | `except (OSError, ValueError, KeyError):` |
| `setup.py:191` (write editor config json) | `except Exception as e:` | `except OSError as e:` |
| `setup.py:344` (read/parse editor config json) | `except Exception:` | `except (json.JSONDecodeError, OSError):` |
| `production_ready.py:75` (`AutoFixer._read_file`) | `except Exception:` `return ""` | `except OSError:` `return ""` |
| `dev.py:36` (`_kill_port` lsof/kill) | `except Exception:` `pass` | `except (subprocess.SubprocessError, FileNotFoundError, OSError):` `console.print(f"[dim]Could not free port {port}[/dim]")` |
| `dev.py:157` (kill PID files loop) | `except Exception as e:` | `except (ValueError, PermissionError, OSError) as e:` (ProcessLookupError already handled separately above) |
| `init.py:138` (cookiecutter run) | `except Exception as e:` | `except (CookiecutterException, OSError) as e:` — add `from cookiecutter.exceptions import CookiecutterException` |
| `adopt.py:207` (cookiecutter run) | `except Exception as e:` | `except (CookiecutterException, OSError) as e:` — same import |
| `routes.py:43` (parse route file) | `except Exception as e:` | `except (OSError, UnicodeDecodeError) as e:` |

For every site: keep the existing handler body (message/exit/return) unchanged — only the exception tuple changes, except `dev.py:36` which gains the dim print (it was a silent `pass`).

- [ ] **Step 2: Verify count**

Run: `grep -rn "except Exception" src/lich/ | grep -v test`
Expected: exactly 1 hit — `seed.py` (the intentionally-broad seeder runner). `make.py`'s hit is inside a string literal; if grep still shows it, that's fine — confirm it's inside the `'''...'''` job template.

- [ ] **Step 3: Run suite**

Run: `pytest -q && ruff check src/lich --ignore=E501`
Expected: all pass

- [ ] **Step 4: Commit**

```bash
git add src/lich/
git commit -m "refactor(cli): narrow bare except Exception to specific exceptions"
```

---

## Task 10: MCP — add async subprocess helper

**Files:**
- Modify: `cli/src/lich/mcp/tools/__init__.py`
- Create: `cli/tests/test_mcp_helpers.py`

- [ ] **Step 1: Write the failing tests**

Create `cli/tests/test_mcp_helpers.py`:

```python
"""
Tests for MCP shared helpers (sync + async runners).
"""
import pytest

from lich.mcp.tools import clean_cli_output, run_lich_command_async


class TestCleanOutput:
    def test_strips_ansi(self):
        assert clean_cli_output("\x1b[31mred\x1b[0m") == "red"

    def test_empty(self):
        assert clean_cli_output("") == ""


class TestAsyncRunner:
    @pytest.mark.asyncio
    async def test_success_returns_output(self):
        out = await run_lich_command_async(["python3", "-c", "print('async-ok')"])
        assert "async-ok" in out
        assert not out.startswith("ERROR")

    @pytest.mark.asyncio
    async def test_nonzero_exit_prefixed(self):
        out = await run_lich_command_async(
            ["python3", "-c", "import sys; print('boom'); sys.exit(2)"]
        )
        assert out.startswith("ERROR (exit 2):")
        assert "boom" in out

    @pytest.mark.asyncio
    async def test_missing_binary(self):
        out = await run_lich_command_async(["definitely-not-a-real-binary-xyz"])
        assert "not found" in out
```

Run: `pytest tests/test_mcp_helpers.py -v`
Expected: FAIL with ImportError (`run_lich_command_async`)

If pytest errors with "async def functions are not natively supported", add to `cli/pytest.ini` under `[pytest]`:

```ini
asyncio_mode = strict
```

(pytest-asyncio is already in dev deps; `strict` + explicit `@pytest.mark.asyncio` markers is the compatible mode.)

- [ ] **Step 2: Implement**

Append to `cli/src/lich/mcp/tools/__init__.py`:

```python
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
```

Consistency check: Phase 2 added returncode handling to the sync `run_lich_command` — make sure both helpers use the same `ERROR (exit N):` prefix format; align the sync one if Phase 2 chose different wording (grep: `grep -n "ERROR" src/lich/mcp/tools/__init__.py`).

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_mcp_helpers.py -v`
Expected: 5 passed

- [ ] **Step 4: Commit**

```bash
git add src/lich/mcp/tools/__init__.py tests/test_mcp_helpers.py cli/pytest.ini 2>/dev/null || git add src/lich/mcp/tools/__init__.py tests/test_mcp_helpers.py pytest.ini
git commit -m "feat(mcp): async subprocess helper with returncode-aware errors"
```

---

## Task 11: MCP — module-level + async: ops.py and migration.py

**Files:**
- Modify: `cli/src/lich/mcp/tools/ops.py`
- Modify: `cli/src/lich/mcp/tools/migration.py`

Pattern for ALL tool files from here on: tools become module-level functions, `_TOOLS` lists them, `register_*_tools(mcp)` becomes a loop. FastMCP registers coroutine functions transparently (`mcp.tool()(fn)` works for both sync and async fn).

- [ ] **Step 1: Rewrite ops.py**

Replace the entire content of `cli/src/lich/mcp/tools/ops.py` with:

```python
"""
MCP Tools for Ops (Deploy/Backup) — long-running, so async.
"""
from typing import Optional

from . import run_lich_command_async


def lich_deploy_setup() -> str:
    """
    Setup deployment configuration.

    Interactive setup for staging and production environments.
    Configures SSH connection, deploy path, and git repo.
    """
    return (
        "Deploy setup is interactive. Run manually:\n\n"
        "  lich deploy setup\n\n"
        "This will ask:\n"
        "- Environment (staging/production)\n"
        "- SSH config or manual connection\n"
        "- Deploy path on server\n"
        "- Git repository URL"
    )


async def lich_deploy_stage(component: str, version: Optional[str] = None, dry_run: bool = False) -> str:
    """
    Deploy a component to staging environment.

    Args:
        component: Component to deploy (backend, web, admin, landing)
        version: Version/tag to deploy (optional, defaults to latest)
        dry_run: If True, preview without deploying
    """
    cmd = ["lich", "deploy", "stage", component]
    if version:
        cmd.extend(["--version", version])
    if dry_run:
        cmd.append("--dry-run")
    return await run_lich_command_async(cmd)


async def lich_deploy_prod(component: str, version: Optional[str] = None, dry_run: bool = False) -> str:
    """
    Deploy a component to production environment.

    WARNING: This deploys to production! Use --dry-run first.

    Args:
        component: Component to deploy (backend, web, admin, landing)
        version: Version/tag to deploy (optional, defaults to latest)
        dry_run: If True, preview without deploying
    """
    cmd = ["lich", "deploy", "prod", component, "--force"]  # --force for non-interactive
    if version:
        cmd.extend(["--version", version])
    if dry_run:
        cmd.append("--dry-run")
    return await run_lich_command_async(cmd)


async def lich_deploy_status() -> str:
    """
    Show deployment configuration status.

    Displays configured environments and their connection settings.
    """
    return await run_lich_command_async(["lich", "deploy", "status"])


async def lich_backup(list_backups: bool = False) -> str:
    """Manage database backups."""
    cmd = ["lich", "backup"]
    if list_backups:
        cmd.append("--list")
    return await run_lich_command_async(cmd)


_TOOLS = [lich_deploy_setup, lich_deploy_stage, lich_deploy_prod, lich_deploy_status, lich_backup]


def register_ops_tools(mcp):
    """Register Ops tools (Deploy/Backup)."""
    for tool in _TOOLS:
        mcp.tool()(tool)
```

- [ ] **Step 2: Rewrite migration.py**

Replace the entire content of `cli/src/lich/mcp/tools/migration.py` with:

```python
"""
MCP Tools for Database Migrations (Alembic wrapper) — stateful and slow, so async.
"""
from . import run_lich_command_async


async def lich_migration_init() -> str:
    """
    Initialize Alembic migrations for the project.

    Creates the alembic directory structure and configuration files.
    """
    return await run_lich_command_async(["lich", "migration", "init"])


async def lich_migration_create(message: str, autogenerate: bool = True) -> str:
    """
    Create a new database migration.

    Args:
        message: Migration message/name (e.g., 'add_users_table').
        autogenerate: If True, auto-generate from model changes.
    """
    cmd = ["lich", "migration", "create", message]
    if not autogenerate:
        cmd.append("--manual")
    return await run_lich_command_async(cmd)


async def lich_migration_up(revision: str = "head") -> str:
    """
    Apply database migrations (upgrade).

    Args:
        revision: Target revision (default: 'head' for latest).
    """
    return await run_lich_command_async(["lich", "migration", "up", revision])


async def lich_migration_down(revision: str = "-1") -> str:
    """
    Rollback database migrations (downgrade).

    Args:
        revision: Target revision (default: '-1' for one step back).
    """
    return await run_lich_command_async(["lich", "migration", "down", revision])


async def lich_migration_status() -> str:
    """
    Show current database migration status.

    Displays current revision and migration history.
    """
    return await run_lich_command_async(["lich", "migration", "status"])


async def lich_migration_heads() -> str:
    """
    Show available migration heads.
    """
    return await run_lich_command_async(["lich", "migration", "heads"])


_TOOLS = [
    lich_migration_init,
    lich_migration_create,
    lich_migration_up,
    lich_migration_down,
    lich_migration_heads,
    lich_migration_status,
]


def register_migration_tools(mcp):
    """Register Migration-related tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
```

Phase 1 note: if Phase 1 added identifier validation to `lich_migration_create` (message validation), preserve that validation code inside the module-level function.

- [ ] **Step 3: Verify tool registration count unchanged**

Run: `pytest tests/test_mcp_server.py -v`
Expected: all pass (Phase 2 fixed the counts; this refactor must not change them)

- [ ] **Step 4: Commit**

```bash
git add src/lich/mcp/tools/ops.py src/lich/mcp/tools/migration.py
git commit -m "refactor(mcp): ops+migration tools to module level, async subprocess"
```

---

## Task 12: MCP — module-level + async: ci.py

**Files:**
- Modify: `cli/src/lich/mcp/tools/ci.py`

- [ ] **Step 1: Rewrite**

Replace the content of `cli/src/lich/mcp/tools/ci.py`. The five `lich_ci_*` runner tools share one shape — implement via a private async runner. `lich_ci_setup` keeps its Docker/act pre-checks (fast, sync subprocess is fine for `docker info`, but make the whole tool async for uniformity since it can invoke the CLI):

```python
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


_TOOLS = [lich_ci_setup, lich_ci_backend, lich_ci_web, lich_ci_admin, lich_ci_landing]


def register_ci_tools(mcp):
    """Register CI-related tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
```

IMPORTANT: Phase 2 implemented `lich_ci_all`. Whatever its Phase 2 implementation is, move it to module level as an `async def` routed through `_run_ci`/`run_lich_command_async` and append it to `_TOOLS`. Do not drop it — `test_mcp_server.py` counts it.

- [ ] **Step 2: Verify + commit**

Run: `pytest tests/test_mcp_server.py -q`
Expected: pass

```bash
git add src/lich/mcp/tools/ci.py
git commit -m "refactor(mcp): CI tools to module level, async"
```

---

## Task 13: MCP — module-level for the remaining sync tool files

**Files:**
- Modify: `cli/src/lich/mcp/tools/{project,make,git,qa,routes,seed,secret,production,mw,dev,utility}.py`

Mechanical transformation, identical recipe per file:

1. Dedent every `@mcp.tool()`-decorated closure to module level and REMOVE the `@mcp.tool()` decorator line.
2. Keep each function's signature, docstring, and body byte-identical (including any Phase 1 validation).
3. In files that call `subprocess.run(...)` + `return res.stdout + res.stderr` + `except FileNotFoundError` (routes, seed, secret, production, mw, dev, utility): replace that whole try/except block with `return run_lich_command(cmd)` and add `from . import run_lich_command` — this routes them through the shared cleaned/returncode-aware runner (Phase 2 behavior) and drops the duplicated boilerplate. Remove the now-unused `import subprocess`.
4. Add `_TOOLS = [<every tool function in original order>]`.
5. Replace the register function body with the loop:

```python
def register_<name>_tools(mcp):
    """Register <Name> tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
```

Full example — new `cli/src/lich/mcp/tools/seed.py` (apply the same shape to the other files):

```python
"""
MCP Tools for Database Seeding.
"""
from typing import Optional

from . import run_lich_command


def lich_seed(name: Optional[str] = None, fresh: bool = False) -> str:
    """
    Seed the database with test data.

    Args:
        name: Specific seeder to run (e.g., 'users'). If None, runs all seeders.
        fresh: If True, re-run migrations before seeding.
    """
    cmd = ["lich", "seed"]
    if name:
        cmd.append(name)
    if fresh:
        cmd.append("--fresh")
    return run_lich_command(cmd)


def lich_seed_list() -> str:
    """
    List all available database seeders.
    """
    return run_lich_command(["lich", "seed", "--list"])


_TOOLS = [lich_seed, lich_seed_list]


def register_seed_tools(mcp):
    """Register Seed-related tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
```

Per-file `_TOOLS` contents (original order):

| File | _TOOLS |
|---|---|
| project.py | `[lich_init, lich_check_project]` (these call `init_project` directly — keep as-is, no subprocess change) |
| make.py | `[lich_make_service, lich_make_entity, lich_make_api, lich_make_dto, lich_make_factory, lich_make_middleware, lich_make_event, lich_make_listener, lich_make_job, lich_make_policy]` (direct function calls — keep) |
| git.py | `[lich_git_commit, lich_git_tag, lich_git_push]` (direct calls — keep) |
| qa.py | `[lich_lint_backend, lich_lint_frontend, lich_security_scan, lich_test]` (`lich_test` switches to `run_lich_command`; the other three call lint/scan functions directly — keep) |
| routes.py | `[lich_routes]` |
| secret.py | `[lich_secret_generate, lich_secret_rotate, lich_secret_check]` (keep Phase 1's length/count bounds) |
| production.py | `[lich_production_ready_check, lich_production_ready_fix]` |
| mw.py | `[lich_middleware_list, lich_middleware_enable, lich_middleware_disable]` |
| dev.py | `[lich_dev_start, lich_dev_stop]` |
| utility.py | `[lich_adopt, lich_upgrade, lich_version]` |

Type-hint fix while touching these: `lich_seed(name: str = None, ...)`, `lich_secret_rotate(key: str = None, ...)`, `lich_deploy_stage/prod(version: str = None)` are `Optional[str]` — annotate them as `Optional[str]` (shown in the examples above; mypy in Task 15 will require it).

- [ ] **Step 1: Apply to all 11 files**

- [ ] **Step 2: Verify every tool still registers and is importable at module level**

Run: `pytest tests/test_mcp_server.py -q`
Expected: pass

Run: `python3 -c "
from lich.mcp.tools.make import lich_make_entity
from lich.mcp.tools.seed import lich_seed
from lich.mcp.tools.ops import lich_deploy_prod
import inspect
assert not inspect.iscoroutinefunction(lich_seed)
assert inspect.iscoroutinefunction(lich_deploy_prod)
print('module-level imports OK')
"`
Expected: `module-level imports OK`

- [ ] **Step 3: Commit**

```bash
git add src/lich/mcp/tools/
git commit -m "refactor(mcp): all tools module-level; sync subprocess tools via run_lich_command"
```

---

## Task 14: MCP — functional tests for tools

**Files:**
- Create: `cli/tests/test_mcp_tools_functional.py`
- Delete/replace: the broken `cli/tests/test_mcp_integration.py` (its own comments admit it can't work against closures; the tools are now module-level, so replace it)

- [ ] **Step 1: Write the tests**

Create `cli/tests/test_mcp_tools_functional.py`:

```python
"""
Functional tests for MCP tools: command construction and error paths.
Tools are module-level (post-refactor), so we patch the runner in each
tool's module namespace and assert the exact CLI command built.
"""
import pytest

from lich.mcp.tools import ops, migration, seed, secret, ci


@pytest.fixture
def recorded_async(monkeypatch):
    """Patch run_lich_command_async in async tool modules; record cmds."""
    calls = []

    async def fake(cmd, force_no_color=True):
        calls.append(cmd)
        return "OK"

    monkeypatch.setattr(ops, "run_lich_command_async", fake)
    monkeypatch.setattr(migration, "run_lich_command_async", fake)
    return calls


@pytest.fixture
def recorded_sync(monkeypatch):
    """Patch run_lich_command in sync tool modules; record cmds."""
    calls = []

    def fake(cmd, force_no_color=True):
        calls.append(cmd)
        return "OK"

    monkeypatch.setattr(seed, "run_lich_command", fake)
    monkeypatch.setattr(secret, "run_lich_command", fake)
    return calls


class TestOpsTools:
    @pytest.mark.asyncio
    async def test_deploy_stage_full_flags(self, recorded_async):
        out = await ops.lich_deploy_stage("backend", version="1.2.3", dry_run=True)
        assert out == "OK"
        assert recorded_async == [
            ["lich", "deploy", "stage", "backend", "--version", "1.2.3", "--dry-run"]
        ]

    @pytest.mark.asyncio
    async def test_deploy_prod_forces_noninteractive(self, recorded_async):
        await ops.lich_deploy_prod("web")
        assert recorded_async == [["lich", "deploy", "prod", "web", "--force"]]

    @pytest.mark.asyncio
    async def test_backup_list(self, recorded_async):
        await ops.lich_backup(list_backups=True)
        assert recorded_async == [["lich", "backup", "--list"]]

    def test_deploy_setup_is_instructional(self):
        out = ops.lich_deploy_setup()
        assert "lich deploy setup" in out


class TestMigrationTools:
    @pytest.mark.asyncio
    async def test_migration_up_default_head(self, recorded_async):
        await migration.lich_migration_up()
        assert recorded_async == [["lich", "migration", "up", "head"]]

    @pytest.mark.asyncio
    async def test_migration_create_manual(self, recorded_async):
        await migration.lich_migration_create("add_users", autogenerate=False)
        assert recorded_async == [["lich", "migration", "create", "add_users", "--manual"]]

    @pytest.mark.asyncio
    async def test_migration_down_default_one_step(self, recorded_async):
        await migration.lich_migration_down()
        assert recorded_async == [["lich", "migration", "down", "-1"]]


class TestSyncTools:
    def test_seed_named_fresh(self, recorded_sync):
        seed.lich_seed(name="users", fresh=True)
        assert recorded_sync == [["lich", "seed", "users", "--fresh"]]

    def test_secret_generate_flags(self, recorded_sync):
        secret.lich_secret_generate(length=64, count=2, format="urlsafe")
        assert recorded_sync == [
            ["lich", "secret", "generate", "-l", "64", "-c", "2", "-f", "urlsafe"]
        ]


class TestErrorPropagation:
    @pytest.mark.asyncio
    async def test_async_tool_propagates_error_prefix(self, monkeypatch):
        async def failing(cmd, force_no_color=True):
            return "ERROR (exit 1):\nboom"

        monkeypatch.setattr(migration, "run_lich_command_async", failing)
        out = await migration.lich_migration_up()
        assert out.startswith("ERROR")
```

- [ ] **Step 2: Remove the broken integration test**

```bash
git rm tests/test_mcp_integration.py
```

(Its two tests were no-ops — one literally ends in `pass`; the replacement above tests real behavior.)

- [ ] **Step 3: Run**

Run: `pytest tests/test_mcp_tools_functional.py -v`
Expected: 11 passed

Run: `pytest -q`
Expected: all pass

- [ ] **Step 4: Commit**

```bash
git add tests/test_mcp_tools_functional.py
git commit -m "test(mcp): functional tests for tool command construction and errors"
```

---

## Task 15: mypy — config, CI step, and missing return type hints

**Files:**
- Modify: `cli/pyproject.toml`
- Modify: `.github/workflows/ci.yml` (repo root)
- Modify: various `cli/src/lich/**/*.py` (annotations only)

- [ ] **Step 1: Add mypy config to `cli/pyproject.toml`**

Append:

```toml
[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true
check_untyped_defs = false
warn_unused_ignores = true
exclude = ["tests/", "dist/"]
```

And add `"mypy>=1.10"` to the `dev` extra in `[project.optional-dependencies]`.

- [ ] **Step 2: Run mypy and fix reported errors**

Run: `pip install -e ".[dev]" && mypy src/lich`

Fix every error it reports. Expected recurring fixes (annotations only, no behavior changes):
- `Optional` defaults: any `param: str = None` / `Path = None` → `Optional[str]` / `Optional[Path]` (deploy helpers, MCP tools not already fixed in Tasks 11–13, `common.run_command(cwd: Optional[Path])` already correct).
- Missing return annotations on public functions — add `-> None` for procedures and concrete types elsewhere. Known offenders from review: `_write_env_file(...) -> None` (secret.py), `_save_deploy_config(...) -> None`, `_save_env_file(...) -> None` (deploy.py), `_ensure_dirs() -> None`, `_kill_port(port: int) -> None` (dev.py), `_add_to_gitignore(files: list) -> None` (ci.py), `git_commit/git_tag/git_push -> None` (git.py).
- `_get_local_template_path` in common already returns `Optional[Path]`.

This is lenient mode — do NOT chase strictness; the gate is just `mypy src/lich` exiting 0.

- [ ] **Step 3: Add CI step**

In `.github/workflows/ci.yml`, in the `lint` job after the Ruff step, add:

```yaml
      - name: Install mypy
        run: |
          pip install mypy
          cd cli
          pip install -e .

      - name: Run mypy
        run: |
          cd cli
          mypy src/lich
```

- [ ] **Step 4: Verify**

Run: `mypy src/lich && pytest -q`
Expected: `Success: no issues found` and tests pass

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/lich ../.github/workflows/ci.yml
git commit -m "chore: add mypy (lenient) to dev deps and CI; complete return type hints"
```

---

## Task 16: Coverage batch 1 — secret, git, backup

**Files:**
- Create: `cli/tests/test_secret.py`
- Create: `cli/tests/test_git.py`
- Create: `cli/tests/test_backup.py`

- [ ] **Step 1: Write `cli/tests/test_secret.py`**

```python
"""
Tests for lich secret command.
"""
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.secret import _generate_secret, _read_env_file, _write_env_file


class TestSecretHelpers:
    def test_generate_secret_length(self):
        assert len(_generate_secret(32)) == 32
        assert len(_generate_secret(64)) == 64

    def test_generate_secret_unique(self):
        assert _generate_secret(32) != _generate_secret(32)

    def test_env_file_roundtrip(self, temp_dir):
        env_path = temp_dir / ".env"
        _write_env_file(env_path, {"KEY1": "value1", "SECRET_KEY": "abc123"})
        loaded = _read_env_file(env_path)
        assert loaded["KEY1"] == "value1"
        assert loaded["SECRET_KEY"] == "abc123"


class TestSecretCLI:
    def test_generate_two_secrets(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["secret", "generate", "-l", "16", "-c", "2"])
        assert result.exit_code == 0

    def test_check_missing_env_file(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["secret", "check", "-e", "nonexistent.env"])
        # should fail or warn, never crash with traceback
        assert "Traceback" not in result.output
```

- [ ] **Step 2: Write `cli/tests/test_git.py`**

```python
"""
Tests for lich git commands (commit/tag/push).
"""
import subprocess
from typer.testing import CliRunner

from lich.cli import app


class TestGitCLI:
    def test_commit_help(self, runner: CliRunner):
        result = runner.invoke(app, ["commit", "--help"])
        assert result.exit_code == 0

    def test_tag_help(self, runner: CliRunner):
        result = runner.invoke(app, ["tag", "--help"])
        assert result.exit_code == 0

    def test_push_help(self, runner: CliRunner):
        result = runner.invoke(app, ["push", "--help"])
        assert result.exit_code == 0

    def test_no_local_run_command_copy(self):
        # dedup regression guard: git.py must use common.run_command
        import lich.commands.git as git_mod
        import inspect
        src = inspect.getsource(git_mod)
        assert "def _run_command" not in src
```

- [ ] **Step 3: Write `cli/tests/test_backup.py`**

```python
"""
Tests for lich backup command.
"""
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.backup import _detect_databases


COMPOSE = """
services:
  db:
    image: postgres:16
    container_name: myapp_db
  cache:
    image: redis:7
"""


class TestDetectDatabases:
    def test_detects_postgres_and_redis(self, in_lich_project):
        (in_lich_project / "docker-compose.yml").write_text(COMPOSE)
        dbs = _detect_databases()
        types = {v["type"] for v in dbs.values()}
        assert "postgresql" in types or "postgres" in types
        assert "redis" in types

    def test_no_compose_returns_empty(self, in_lich_project):
        assert _detect_databases() == {}


class TestBackupCLI:
    def test_backup_help(self, runner: CliRunner):
        result = runner.invoke(app, ["backup", "--help"])
        assert result.exit_code == 0
        assert "restore" in result.output
```

Adjustment rule for this batch: before finalizing each assert, READ the function under test (e.g. the exact `type` string `_detect_databases` stores — `"postgresql"` vs `"postgres"`) and pin the assert to the real value instead of the `or`. The `or`-form above is a placeholder for the first run only; the committed test must assert the exact string.

- [ ] **Step 4: Run and fix**

Run: `pytest tests/test_secret.py tests/test_git.py tests/test_backup.py -v`
Expected: all pass. Where a test reveals the real behavior differs from the assumption (e.g. `secret check` exit code), pin the test to the ACTUAL current behavior — Phase 3 is refactoring, not behavior change.

- [ ] **Step 5: Commit**

```bash
git add tests/test_secret.py tests/test_git.py tests/test_backup.py
git commit -m "test(cli): coverage for secret, git, backup commands"
```

---

## Task 17: Coverage batch 2 — lint, security, dev, doctor

**Files:**
- Create: `cli/tests/test_lint_security.py`
- Create: `cli/tests/test_dev_doctor.py`

- [ ] **Step 1: Write `cli/tests/test_lint_security.py`**

```python
"""
Tests for lich lint and security commands.
"""
from typer.testing import CliRunner

from lich.cli import app
import lich.commands.lint as lint_mod
import lich.commands.security as sec_mod


class TestLint:
    def test_lint_help(self, runner: CliRunner):
        result = runner.invoke(app, ["lint", "--help"])
        assert result.exit_code == 0

    def test_lint_python_clean_run(self, in_lich_project, monkeypatch):
        monkeypatch.setattr(lint_mod, "_check_tool_installed", lambda t: True)
        monkeypatch.setattr(lint_mod, "_run_command", lambda cmd, cwd=None, capture=True: (0, "", ""))
        result = lint_mod.lint_python(fix=False)
        assert result["tool"] == "python"
        assert result["passed"] is True

    def test_lint_python_missing_tool(self, in_lich_project, monkeypatch):
        monkeypatch.setattr(lint_mod, "_check_tool_installed", lambda t: False)
        result = lint_mod.lint_python(fix=False)
        # must not crash; read lint_python to pin the exact behavior (skip/warn)
        assert isinstance(result, dict)


class TestSecurity:
    def test_security_help(self, runner: CliRunner):
        result = runner.invoke(app, ["security", "--help"])
        assert result.exit_code == 0

    def test_scan_python_missing_tools(self, in_lich_project, monkeypatch):
        monkeypatch.setattr(sec_mod, "_check_tool_installed", lambda t: False)
        result = sec_mod.scan_python_security()
        assert isinstance(result, dict)
        assert result["tool"] == "python"
```

- [ ] **Step 2: Write `cli/tests/test_dev_doctor.py`**

```python
"""
Tests for lich dev (start/stop) helpers and doctor.
"""
from typer.testing import CliRunner

from lich.cli import app
import lich.commands.dev as dev_mod


class TestDevHelpers:
    def test_check_port_free(self):
        # port 1 is never listening on a dev machine
        assert dev_mod._check_port(1) is False

    def test_ensure_dirs(self, in_lich_project):
        dev_mod._ensure_dirs()
        assert dev_mod.PID_DIR.exists()
        assert dev_mod.LOG_DIR.exists()

    def test_stop_with_no_processes(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["stop"])
        assert result.exit_code == 0


class TestDoctor:
    def test_doctor_help(self, runner: CliRunner):
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0

    def test_doctor_reports_checks_in_project(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["doctor"])
        # produces a diagnostic report (pass or fail marks), never a traceback
        assert "Traceback" not in result.output
        assert ("✅" in result.output) or ("❌" in result.output)
```

Note: `dev_mod.PID_DIR` — verify the actual constant name at the top of dev.py (`PID_DIR`, `LOG_DIR` at ~lines 17–18) and use the real names.

- [ ] **Step 3: Run, pin, commit**

Run: `pytest tests/test_lint_security.py tests/test_dev_doctor.py -v`
Expected: all pass (pin loose asserts to actual behavior as in Task 16)

```bash
git add tests/test_lint_security.py tests/test_dev_doctor.py
git commit -m "test(cli): coverage for lint, security, dev, doctor"
```

---

## Task 18: Coverage batch 3 — shell, test, middleware, production-ready, version_check

**Files:**
- Create: `cli/tests/test_misc_commands.py`

- [ ] **Step 1: Write `cli/tests/test_misc_commands.py`**

```python
"""
Tests for shell, test, middleware, production-ready commands and version_check.
"""
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.production_ready import AutoFixer


class TestHelpSurfaces:
    def test_shell_help(self, runner: CliRunner):
        result = runner.invoke(app, ["shell", "--help"])
        assert result.exit_code == 0

    def test_test_help(self, runner: CliRunner):
        result = runner.invoke(app, ["test", "--help"])
        assert result.exit_code == 0

    def test_middleware_help(self, runner: CliRunner):
        result = runner.invoke(app, ["middleware", "--help"])
        assert result.exit_code == 0
        assert "enable" in result.output
        assert "disable" in result.output

    def test_production_ready_help(self, runner: CliRunner):
        result = runner.invoke(app, ["production-ready", "--help"])
        assert result.exit_code == 0


class TestOutsideProjectGuards:
    def test_middleware_list_outside_project(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["middleware", "list"])
        assert result.exit_code == 1

    def test_production_ready_outside_project(self, runner: CliRunner, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["production-ready"])
        assert result.exit_code == 1


class TestAutoFixer:
    def test_read_file_missing_returns_empty(self, temp_dir):
        fixer = AutoFixer.__new__(AutoFixer)  # skip __init__ side effects
        assert fixer._read_file(temp_dir / "nope.txt") == ""


class TestVersionCheck:
    def test_check_compatibility_never_raises(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        from lich.version_check import check_compatibility
        check_compatibility()  # network may fail; function must swallow gracefully
```

Note: read `AutoFixer.__init__` first — if it's side-effect-free, construct it normally instead of `__new__`. Read `middleware list` / `production-ready` guards to confirm exit code 1 outside a project (both import `_check_lich_project` alias — they should). Pin asserts to actual behavior.

- [ ] **Step 2: Run + commit**

Run: `pytest tests/test_misc_commands.py -v`
Expected: all pass

```bash
git add tests/test_misc_commands.py
git commit -m "test(cli): coverage for shell/test/middleware/production-ready/version_check"
```

---

## Task 19: Coverage measurement + gap fill

**Files:**
- Modify: `cli/pyproject.toml` (add pytest-cov to dev deps)
- Possibly add tests to existing test files

- [ ] **Step 1: Add pytest-cov**

In `cli/pyproject.toml` dev extras, add `"pytest-cov>=5.0"`. Run `pip install -e ".[dev]"`.

- [ ] **Step 2: Measure**

Run: `pytest --cov=lich --cov-report=term-missing -q | tail -40`

Record the TOTAL percentage. Target: **≥ 80%**.

- [ ] **Step 3: Fill gaps (repeat until ≥80% or hard blocker)**

Priority: whatever files show the lowest coverage in the report, focusing on cheap wins first — help-text paths, guard paths (`outside project` exits), pure helpers with mocked `run_command`. Rules:
- Every added test asserts real behavior (no `assert True`, no `exit_code in (0, 1)`).
- Interactive prompt flows (deploy_setup, ci_setup) may be tested by monkeypatching `rich.prompt.Prompt.ask` / `Confirm.ask` / `typer.confirm` sequences — e.g.:

```python
def test_deploy_setup_manual_flow(self, runner, in_lich_project, monkeypatch):
    answers = iter(["production", "manual", "1.2.3.4", "root", "/opt/app", "docker-compose",
                    "git@github.com:me/app.git", "example.com", "api.example.com", "admin.example.com"])
    monkeypatch.setattr("lich.commands.deploy.Prompt.ask", lambda *a, **k: next(answers))
    confirms = iter([False, False])  # not private repo, no env vars
    monkeypatch.setattr("lich.commands.deploy.Confirm.ask", lambda *a, **k: next(confirms))
    result = runner.invoke(app, ["deploy", "setup"])
    assert result.exit_code == 0
```

(Adapt the answer sequence to the actual prompt order after the Task 5 split; the `.lich` marker-file collision from Task 5 Step 1 applies here too.)
- If after honest effort the total plateaus below 80% because of untestable interactive/SSH surface, STOP at the plateau and record the real number in the completion notes — do NOT pad with fake asserts. The 80% CI gate decision happens in Phase 4.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml tests/
git commit -m "test(cli): coverage gap fill; add pytest-cov (measured: <ACTUAL>%)"
```

(Replace `<ACTUAL>` with the measured number.)

---

## Task 20: Phase completion — suite, changelog, version bump

**Files:**
- Modify: `cli/pyproject.toml` (version)
- Modify: `cli/src/lich/__init__.py` (`__version__`)
- Modify: `CHANGELOG.md` (repo root)

- [ ] **Step 1: Full verification**

Run, all from `cli/`:

```bash
pytest -q
mypy src/lich
ruff check src/lich --ignore=E501
pytest --cov=lich --cov-report=term -q | tail -3
grep -rn "def _check_lich_project\|def _run_command\|def _check_tool_installed\|def _download_template" src/lich/commands/ | grep -v common.py
grep -rn "except Exception" src/lich/ | grep -v seed.py
```

Expected: tests pass, mypy clean, ruff clean, coverage number recorded, both greps empty (make.py string-literal hit allowed on the last grep).

Run the AST oversized-function check (Task 5 Step 3) against deploy.py, ci.py, upgrade.py, make.py.
Expected: no function > 80 lines in deploy.py, ci.py, upgrade.py. (make.py's generators are template-emitters and were not in scope; report if any exceed 80.)

- [ ] **Step 2: Bump version to 1.14.0**

- `cli/pyproject.toml`: `version = "1.14.0"`
- `cli/src/lich/__init__.py`: `__version__ = "1.14.0"`

- [ ] **Step 3: Changelog entry**

Prepend to `CHANGELOG.md` (match the existing entry format in the file):

```markdown
## [1.14.0] - <today's date>

### Changed (Quality Sprint — Phase 3 of v1 hardening)
- Deduplicated CLI helpers into `commands/common.py` (project checks, subprocess runners, tool checks, template download)
- Split oversized functions: `deploy_setup`, `deploy_init`, `upgrade_project`, `ci_setup` (all < 80 lines)
- `ci web|admin|landing` now share one parameterized runner
- Narrowed all bare `except Exception` handlers to specific exceptions
- MCP tools moved to module level (unit-testable); deploy/CI/migration/backup tools are now async (`asyncio.create_subprocess_exec`)
- Sync MCP subprocess tools routed through the shared cleaned/returncode-aware runner

### Added
- mypy (lenient) in dev deps and CI
- Functional MCP tool tests; new test suites for secret, git, backup, lint, security, dev, doctor, misc commands (coverage: <ACTUAL>%)
```

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "chore: release v1.14.0 (Phase 3 quality sprint)"
```

- [ ] **Step 5: Open PR**

```bash
git push -u origin hardening/phase3-quality
gh pr create --title "Phase 3: Quality sprint (v1.14.0)" --body "Dedup, function splits, exception hygiene, async+testable MCP tools, mypy, coverage <ACTUAL>%. Spec: docs/superpowers/specs/2026-07-10-lich-v1-hardening-design.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

Human review checkpoint: do NOT merge without review (per spec's Sonnet execution model).

---

## Spec coverage self-check (for the reviewer)

| Spec Phase 3 requirement | Task(s) |
|---|---|
| common.py extraction (4 helper families) | 1–4 |
| Oversized function splits (4 functions) | 5–8 |
| ci_web/admin/landing factory | 8 |
| Exception hygiene (~20 sites) | 5, 7, 9 |
| MCP module-level tools | 11–13 |
| MCP async long-running tools | 10–12 |
| Shared validation module (CLI+MCP) | Done in Phase 1 (`_shell.py` + validators); Task 11/13 preserve it — no new work |
| mypy + type hints | 15 |
| Coverage → 80% | 16–19 |
| MCP functional tests | 14 |
