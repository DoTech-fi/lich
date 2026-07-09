# Lich v1 Hardening — Phase 2: Correctness Sprint (v1.13.1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make everything the framework claims actually true: all tests green, MCP tool count accurate, generated frontend actually compiles, Keycloak auth path works, and known template bugs fixed. Ships as v1.13.1.

**Architecture:** Two codebases are touched: the CLI package at `cli/` (tests run with pytest from `cli/`) and the cookiecutter template at `template/` (verified via a new generation smoke-test harness in the CLI test suite that renders the template with `cookiecutter --no-input` and asserts on the output).

**Tech Stack:** Python 3.10+, Typer, FastMCP, pytest, pytest-mock, cookiecutter, Jinja2 templates.

**Spec:** `docs/superpowers/specs/2026-07-10-lich-v1-hardening-design.md` (Phase 2 section).

**Two deviations from the spec, decided during planning (verified against the real code):**

1. **tsx Jinja fix strategy changed.** The spec said "per-strategy variants of AuthContext.tsx". Investigation found **13** ts/tsx files contain Jinja conditionals (not just AuthContext) — all are currently copied verbatim because `*.tsx`/`*.ts` are in `_copy_without_render` (added in v1.12.12), which means **the generated frontend today contains literal Jinja syntax and cannot compile**. Per-strategy variants of 13 files is infeasible. The correct fix: remove `*.tsx`/`*.jsx`/`*.ts` from `_copy_without_render` (these 13 files already use `{% raw %}` guards where they contain JSX `{{ }}`), and add `{% raw %}` guards to the only 2 files that have bare JSX `{{ }}` without guards: `apps/admin/src/app/page.tsx` and `apps/web/src/app/logout/page.tsx`.
2. **DB session semantics: no task.** The spec listed "commit only on success, rollback on exception" for `connection.py` — the current code already does exactly this (verified: `try/yield/commit`, `except/rollback/raise`, `finally/close`). Nothing to do.

**Also discovered during planning (affects Task 0):** `import lich` currently resolves to site-packages (regular install), NOT the working tree. Any edit under `cli/src/` is invisible to tests until an editable install is done. Task 0 fixes this first.

---

### Task 0: Editable install of the CLI

**Files:** none (environment only)

- [ ] **Step 1: Install the CLI in editable mode**

```bash
cd /Users/babak/codes/DoTech/lich-framework/cli && pip install -e . -q
```

- [ ] **Step 2: Verify imports resolve to the working tree**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -c "import lich; print(lich.__file__)"`
Expected: a path containing `lich-framework/cli/src/lich/__init__.py` (NOT `site-packages`)

- [ ] **Step 3: Baseline test run**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest -q 2>&1 | tail -3`
Expected: `5 failed, 75 passed` (possibly `4 failed` if the editable install alone fixed `test_version_with_history_flag` — either is fine; note which).

No commit (no repo changes).

---

### Task 1: Implement `lich_ci_all` MCP tool

The test suite and the docs both promise `lich_ci_all`, but it was never implemented.

**Files:**
- Modify: `cli/src/lich/mcp/tools/ci.py`
- Test: `cli/tests/test_mcp_ci_all.py` (create)

- [ ] **Step 1: Write the failing test**

Create `cli/tests/test_mcp_ci_all.py`:

```python
"""Tests for the lich_ci_all MCP tool."""
from mcp.server.fastmcp import FastMCP

from lich.mcp.tools import ci


def _get_tool(name: str):
    mcp = FastMCP("TestLich")
    ci.register_ci_tools(mcp)
    tools_map = {t.name: t.fn for t in mcp._tool_manager.list_tools()}
    return tools_map.get(name)


def test_ci_all_is_registered():
    assert _get_tool("lich_ci_all") is not None


def test_ci_all_runs_all_components(mocker):
    mock_run = mocker.patch("lich.mcp.tools.ci.subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    tool = _get_tool("lich_ci_all")
    output = tool(local=True)

    called_cmds = [call.args[0] for call in mock_run.call_args_list]
    assert ["lich", "ci", "backend", "-l"] in called_cmds
    assert ["lich", "ci", "web", "-l"] in called_cmds
    assert ["lich", "ci", "admin", "-l"] in called_cmds
    assert ["lich", "ci", "landing", "-l"] in called_cmds
    assert "backend" in output and "landing" in output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_mcp_ci_all.py -v`
Expected: FAIL — `test_ci_all_is_registered` asserts None is not None

- [ ] **Step 3: Implement `lich_ci_all`**

In `cli/src/lich/mcp/tools/ci.py`, add inside `register_ci_tools(mcp)`, after the `lich_ci_landing` function (keep the same indentation as the other `@mcp.tool()` functions):

```python
    @mcp.tool()
    def lich_ci_all(local: bool = False) -> str:
        """
        Run CI checks for all components sequentially (backend, web, admin, landing).

        By default runs with Docker/act. Use local=True for direct execution.

        Args:
            local: If True, run locally without Docker (faster for dev).
        """
        results = []
        for component in ["backend", "web", "admin", "landing"]:
            cmd = ["lich", "ci", component]
            if local:
                cmd.append("-l")
            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                status = "✅" if res.returncode == 0 else f"❌ (exit {res.returncode})"
                results.append(f"=== {component} {status} ===\n{res.stdout}{res.stderr}")
            except FileNotFoundError:
                return "lich command not found"
        return "\n".join(results)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_mcp_ci_all.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add cli/src/lich/mcp/tools/ci.py cli/tests/test_mcp_ci_all.py && git commit -m "feat(mcp): implement lich_ci_all tool (runs all components sequentially)"
```

---

### Task 2: Fix the MCP tool inventory test (47 → 52, real tool names)

The expected list in `test_mcp_server.py` is stale: it expects `lich_deploy` (never existed under that name) and is missing `lich_deploy_setup/stage/prod/status`, `lich_ci_setup`, `lich_ci_landing`. With `lich_ci_all` from Task 1, the real count is **52**.

**Files:**
- Modify: `cli/tests/test_mcp_server.py`

- [ ] **Step 1: Update the expected tool list**

In `cli/tests/test_mcp_server.py`, replace the `# Ops tools (2)` block:

```python
    # Ops tools (2)
    "lich_deploy",
    "lich_backup",
```

with:

```python
    # Ops tools (5)
    "lich_deploy_setup",
    "lich_deploy_stage",
    "lich_deploy_prod",
    "lich_deploy_status",
    "lich_backup",
```

and replace the `# CI tools (4)` block:

```python
    # CI tools (4)
    "lich_ci_all",
    "lich_ci_backend",
    "lich_ci_web",
    "lich_ci_admin",
```

with:

```python
    # CI tools (7)
    "lich_ci_setup",
    "lich_ci_all",
    "lich_ci_backend",
    "lich_ci_web",
    "lich_ci_admin",
    "lich_ci_landing",
```

Wait — that is 6 CI entries plus 1 already counted; the full CI list is: `lich_ci_setup`, `lich_ci_all`, `lich_ci_backend`, `lich_ci_web`, `lich_ci_admin`, `lich_ci_landing` (6 tools). Use exactly those 6 lines with the comment `# CI tools (6)`.

- [ ] **Step 2: Derive the count instead of hardcoding it**

Replace:

```python
EXPECTED_TOOL_COUNT = 47
```

with:

```python
EXPECTED_TOOL_COUNT = len(ALL_EXPECTED_TOOLS)  # currently 52
```

And in `test_all_mcp_tools_registered`, replace the two assertions at the end:

```python
    # Check we have exactly 47 tools
    assert len(tools) == EXPECTED_TOOL_COUNT, f"Expected {EXPECTED_TOOL_COUNT} tools, found {len(tools)}"
    
    # Check each expected tool exists
    for tool in ALL_EXPECTED_TOOLS:
        assert tool in tools, f"Missing tool: {tool}"
```

with a symmetric set comparison (catches both missing AND undocumented extras):

```python
    expected = set(ALL_EXPECTED_TOOLS)
    actual = set(tools)
    assert actual == expected, (
        f"Missing: {sorted(expected - actual)}; Unexpected: {sorted(actual - expected)}"
    )
    assert len(tools) == EXPECTED_TOOL_COUNT
```

Also update the module docstring comment on line 4 from `# All 47 expected tools` to `# All expected tools (count asserted = len of this list)` and the docstrings mentioning "47" in `test_all_mcp_tools_registered` (`"""Verify that ALL registered Lich tools match the expected inventory."""`) and the `__main__` print at the bottom (`print(f"\n✅ All {EXPECTED_TOOL_COUNT} MCP Tools Verified!")` — already uses the constant, fine).

- [ ] **Step 3: Update the category tests**

In `TestMCPToolCategories`, replace `test_ops_tools_exist`:

```python
    def test_ops_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        ops_tools = [
            "lich_deploy_setup", "lich_deploy_stage",
            "lich_deploy_prod", "lich_deploy_status", "lich_backup",
        ]
        for t in ops_tools:
            assert t in tools
```

and replace `test_ci_tools_exist`:

```python
    def test_ci_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        ci_tools = [
            "lich_ci_setup", "lich_ci_all", "lich_ci_backend",
            "lich_ci_web", "lich_ci_admin", "lich_ci_landing",
        ]
        for t in ci_tools:
            assert t in tools
```

- [ ] **Step 4: Run the file to verify it passes**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_mcp_server.py -v`
Expected: all 17 tests pass

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add cli/tests/test_mcp_server.py && git commit -m "test(mcp): fix stale tool inventory — 52 tools, symmetric set assertion"
```

---

### Task 3: Fix `test_mcp_wiring` (broken mock target, no-op body)

The test patches `lich.mcp.tools.ops.subprocess.run` but `ops.py` no longer imports `subprocess` (it uses `run_lich_command` from `lich.mcp.tools`) — hence `AttributeError`. The test body also ends in `pass`, asserting nothing.

**Files:**
- Modify: `cli/tests/test_mcp_integration.py`

- [ ] **Step 1: Rewrite `test_mcp_wiring` with real assertions**

Replace the entire `test_mcp_wiring` function (lines 12–63) with:

```python
def test_mcp_wiring(mocker):
    """
    Verify that MCP tools are correctly wired to their underlying implementations.
    """
    mcp = FastMCP("TestLich")

    mock_init = mocker.patch("lich.mcp.tools.project.init_project")
    mock_make_service = mocker.patch("lich.mcp.tools.make.make_service")
    mock_git_commit = mocker.patch("lich.mcp.tools.git.git_commit")
    # ops.py imports run_lich_command via `from . import run_lich_command`,
    # so patch the name bound in the ops module namespace:
    mock_run = mocker.patch(
        "lich.mcp.tools.ops.run_lich_command", return_value="Deploy success"
    )

    project.register_project_tools(mcp)
    make.register_make_tools(mcp)
    git.register_git_tools(mcp)
    qa.register_qa_tools(mcp)
    ops.register_ops_tools(mcp)

    tools_map = {t.name: t.fn for t in mcp._tool_manager.list_tools()}

    # Ops wiring: lich_deploy_status delegates to run_lich_command
    result = tools_map["lich_deploy_status"]()
    mock_run.assert_called_once_with(["lich", "deploy", "status"])
    assert result == "Deploy success"

    # Ops wiring: lich_deploy_stage builds the right command
    mock_run.reset_mock()
    tools_map["lich_deploy_stage"](component="web", version="1.2.3", dry_run=True)
    mock_run.assert_called_once_with(
        ["lich", "deploy", "stage", "web", "--version", "1.2.3", "--dry-run"]
    )
```

Keep the imports at the top of the file and `test_mcp_execution_flow` unchanged. Delete the `if __name__ == "__main__":` block at the bottom (lines 110–118) — it is dead scaffolding.

- [ ] **Step 2: Run the file to verify it passes**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_mcp_integration.py -v`
Expected: 2 passed

- [ ] **Step 3: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add cli/tests/test_mcp_integration.py && git commit -m "test(mcp): fix wiring test mock target and add real assertions"
```

---

### Task 4: `run_lich_command` checks the exit code

Currently a failing subprocess returns its output with no indication of failure — the AI calling the tool sees success.

**Files:**
- Modify: `cli/src/lich/mcp/tools/__init__.py`
- Test: `cli/tests/test_mcp_run_command.py` (create)

- [ ] **Step 1: Write the failing test**

Create `cli/tests/test_mcp_run_command.py`:

```python
"""Tests for the shared run_lich_command helper."""
from unittest.mock import MagicMock

from lich.mcp.tools import run_lich_command


def _mock_result(returncode: int, stdout: str = "", stderr: str = ""):
    res = MagicMock()
    res.returncode = returncode
    res.stdout = stdout
    res.stderr = stderr
    return res


def test_success_returns_clean_output(mocker):
    mocker.patch("subprocess.run", return_value=_mock_result(0, stdout="all good\n"))
    assert run_lich_command(["lich", "routes"]) == "all good\n"


def test_failure_is_prefixed_with_error_and_exit_code(mocker):
    mocker.patch(
        "subprocess.run", return_value=_mock_result(2, stderr="boom\n")
    )
    output = run_lich_command(["lich", "deploy", "prod", "web"])
    assert output.startswith("ERROR (exit 2):")
    assert "boom" in output


def test_missing_binary_message(mocker):
    mocker.patch("subprocess.run", side_effect=FileNotFoundError)
    assert run_lich_command(["lich", "routes"]) == "lich command not found"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_mcp_run_command.py -v`
Expected: `test_failure_is_prefixed_with_error_and_exit_code` FAILS (no ERROR prefix); the other two pass

- [ ] **Step 3: Implement the returncode check**

In `cli/src/lich/mcp/tools/__init__.py`, replace the body of `run_lich_command` (the `try` block):

```python
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
```

Also update the docstring `Returns:` line to: `Cleaned output string (stdout + stderr); prefixed with "ERROR (exit N):" on non-zero exit.`

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_mcp_run_command.py tests/test_mcp_integration.py tests/test_mcp_server.py -v`
Expected: all pass (wiring test from Task 3 patches `run_lich_command` itself, so it is unaffected)

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add cli/src/lich/mcp/tools/__init__.py cli/tests/test_mcp_run_command.py && git commit -m "fix(mcp): surface subprocess exit codes as ERROR prefix in tool output"
```

---

### Task 5: `lich version --history` finds the changelog

`CHANGELOG_PATH` is computed as `Path(__file__).parents[4]/CHANGELOG.md`, which only works for a dev checkout — a site-packages install walks into site-packages' parents and finds nothing. The editable install (Task 0) masks this in dev; make resolution robust anyway.

**Files:**
- Modify: `cli/src/lich/commands/version.py`

- [ ] **Step 1: Replace the module-level constant with a resolver**

In `cli/src/lich/commands/version.py`, replace:

```python
# Path to CHANGELOG.md (relative to package)
CHANGELOG_PATH = Path(__file__).parent.parent.parent.parent.parent / "CHANGELOG.md"
```

with:

```python
def _find_changelog() -> "Path | None":
    """Locate CHANGELOG.md: dev checkout first, then working directory."""
    candidates = [
        Path(__file__).resolve().parents[4] / "CHANGELOG.md",  # repo root (dev/editable)
        Path.cwd() / "CHANGELOG.md",
        Path.cwd().parent / "CHANGELOG.md",
    ]
    for candidate in candidates:
        try:
            if candidate.exists():
                return candidate
        except OSError:
            continue
    return None
```

- [ ] **Step 2: Use the resolver at both call sites**

In `_show_changelog()`, replace:

```python
    if CHANGELOG_PATH.exists():
        with open(CHANGELOG_PATH) as f:
```

with:

```python
    changelog = _find_changelog()
    if changelog:
        with open(changelog) as f:
```

In `_parse_changelog()`, replace:

```python
    if not CHANGELOG_PATH.exists():
        return [{"version": __version__, "date": "current", "highlights": "Current version"}]
    
    try:
        with open(CHANGELOG_PATH) as f:
```

with:

```python
    changelog = _find_changelog()
    if not changelog:
        return [{"version": __version__, "date": "current", "highlights": "Current version"}]
    
    try:
        with open(changelog) as f:
```

- [ ] **Step 3: Run the version tests**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_version.py -v`
Expected: 5 passed (including `test_version_with_history_flag`)

- [ ] **Step 4: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add cli/src/lich/commands/version.py && git commit -m "fix(version): robust CHANGELOG.md resolution for --history"
```

---

### Task 6: Update the "47 MCP tools" claim everywhere (real count: 52)

**Files:**
- Modify: `docs/wiki/SETUP_GUIDE.md:3`
- Modify: `site-docs/integrations/mcp.md:3,141,232-233,263,297`
- Modify: `site-docs/index.md:29,74,85`

- [ ] **Step 1: Apply the count edits**

| File:line | Old | New |
|---|---|---|
| `docs/wiki/SETUP_GUIDE.md:3` | `Lich's 47+ MCP tools` | `Lich's 52 MCP tools` |
| `site-docs/integrations/mcp.md:3` | `47 MCP Tools - Full Control for AI Assistants` | `52 MCP Tools - Full Control for AI Assistants` |
| `site-docs/integrations/mcp.md:141` | `## 🛠️ Available Tools (47 Total)` | `## 🛠️ Available Tools (52 Total)` |
| `site-docs/integrations/mcp.md:297` | `The AI should list all 47 tools with descriptions.` | `The AI should list all 52 tools with descriptions.` |
| `site-docs/index.md:29` | `**47 MCP tools**` | `**52 MCP tools**` |
| `site-docs/index.md:74` | `🤖 Lich MCP (47 Tools)` | `🤖 Lich MCP (52 Tools)` |
| `site-docs/index.md:85` | `47 MCP Tools for Complete Control` | `52 MCP Tools for Complete Control` |

- [ ] **Step 2: Fix the Deployment tool table and example**

In `site-docs/integrations/mcp.md`, replace the Deployment table (lines ~228–233):

```markdown
### Deployment

| Tool | Description |
|------|-------------|
| `lich_deploy` | Deploy via Ansible |
| `lich_backup` | Database backup operations |
```

with:

```markdown
### Deployment

| Tool | Description |
|------|-------------|
| `lich_deploy_setup` | Configure deploy environments (interactive) |
| `lich_deploy_stage` | Deploy a component to staging |
| `lich_deploy_prod` | Deploy a component to production |
| `lich_deploy_status` | Show deployment configuration status |
| `lich_backup` | Database backup operations |
```

In the Quality Assurance table (~line 200), add one row after `lich_ci_admin`:

```markdown
| `lich_ci_landing` | Run landing page CI |
| `lich_ci_setup` | Set up act for local CI |
```

At line ~263, replace `` 5. `lich_deploy` → Deploys to staging `` with `` 5. `lich_deploy_stage` → Deploys to staging ``.

- [ ] **Step 3: Verify no stale claims remain**

Run: `cd /Users/babak/codes/DoTech/lich-framework && grep -rn "47" README.md docs/wiki site-docs 2>/dev/null | grep -i tool`
Expected: no output

Run: `grep -n "lich_deploy\b" site-docs/integrations/mcp.md`
Expected: no output (only `lich_deploy_*` names remain)

- [ ] **Step 4: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add docs/wiki/SETUP_GUIDE.md site-docs/integrations/mcp.md site-docs/index.md && git commit -m "docs: correct MCP tool count to 52 and document real deploy/ci tool names"
```

---

### Task 7: Template generation smoke-test harness (red)

New CLI-side test file that renders the template with cookiecutter and asserts on the output. The tsx assertions will FAIL until Task 8 — that is the point (TDD at template scale).

**Files:**
- Test: `cli/tests/test_template_generation.py` (create)

- [ ] **Step 1: Write the harness and the failing assertions**

Create `cli/tests/test_template_generation.py`:

```python
"""
Template generation smoke tests.

Renders the cookiecutter template into a tmp dir and asserts the output
is actually valid (no leaked Jinja, backend compiles, key fixes present).
"""
import py_compile
import subprocess
import sys
from pathlib import Path

import pytest

TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "template"


def _generate(tmp_path: Path, **extra_context) -> Path:
    """Render the template with default answers plus overrides."""
    ctx = [f"{k}={v}" for k, v in extra_context.items()]
    cmd = [
        sys.executable, "-m", "cookiecutter", "--no-input",
        "-o", str(tmp_path), str(TEMPLATE_DIR), *ctx,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"cookiecutter failed:\n{res.stderr}"
    project = tmp_path / "my_awesome_project"
    assert project.is_dir()
    return project


@pytest.fixture(scope="module")
def jwt_project(tmp_path_factory) -> Path:
    """Default generation: jwt_builtin + postgresql."""
    return _generate(tmp_path_factory.mktemp("gen-jwt"))


@pytest.fixture(scope="module")
def keycloak_project(tmp_path_factory) -> Path:
    return _generate(tmp_path_factory.mktemp("gen-kc"), auth_strategy="keycloak")


def _frontend_sources(project: Path):
    apps = project / "apps"
    return [
        p for p in list(apps.rglob("*.tsx")) + list(apps.rglob("*.ts"))
        if "node_modules" not in p.parts
    ]


def test_no_jinja_leaks_into_frontend(jwt_project):
    """Generated ts/tsx must contain no unrendered Jinja syntax."""
    offenders = []
    for src in _frontend_sources(jwt_project):
        text = src.read_text()
        if "{%" in text or "{{ cookiecutter" in text:
            offenders.append(str(src.relative_to(jwt_project)))
    assert not offenders, f"Unrendered Jinja in: {offenders}"


def test_authcontext_jwt_has_login(jwt_project):
    text = (jwt_project / "apps/web/src/context/AuthContext.tsx").read_text()
    assert "login" in text and "LoginRequest" in text


def test_authcontext_keycloak_has_no_builtin_login(keycloak_project):
    text = (keycloak_project / "apps/web/src/context/AuthContext.tsx").read_text()
    assert "LoginRequest" not in text
    assert "{%" not in text


def test_generated_backend_compiles(jwt_project):
    """Every generated backend .py must at least parse."""
    for py in (jwt_project / "backend").rglob("*.py"):
        py_compile.compile(str(py), doraise=True)


def test_generated_backend_compiles_keycloak(keycloak_project):
    for py in (keycloak_project / "backend").rglob("*.py"):
        py_compile.compile(str(py), doraise=True)
```

- [ ] **Step 2: Run to verify the expected red/green split**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_generation.py -v`
Expected: `test_no_jinja_leaks_into_frontend`, `test_authcontext_jwt_has_login`, and `test_authcontext_keycloak_has_no_builtin_login` FAIL (tsx files still copied verbatim with Jinja inside). Both `*_compiles` tests PASS. If a compile test fails instead, STOP and report — that is an unknown bug.

- [ ] **Step 3: Commit the red harness**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add cli/tests/test_template_generation.py && git commit -m "test(template): add generation smoke harness (tsx Jinja assertions red)"
```

---

### Task 8: Render ts/tsx through Jinja (fix the broken generated frontend)

**Files:**
- Modify: `template/cookiecutter.json`
- Modify: `template/{{cookiecutter.project_slug}}/apps/admin/src/app/page.tsx`
- Modify: `template/{{cookiecutter.project_slug}}/apps/web/src/app/logout/page.tsx`

- [ ] **Step 1: Remove the blanket exclusions**

In `template/cookiecutter.json`, change `_copy_without_render`:

```json
  "_copy_without_render": [
    "*.png",
    "*.jpg",
    "*.ico",
    "*.woff",
    "*.woff2",
    "infra/ansible/**/*"
  ]
```

(removing `"*.tsx"`, `"*.jsx"`, `"*.ts"` — there are zero `.jsx` files, 13 of 16 ts/tsx files already carry `{% raw %}` guards where needed, and the remaining 2 are fixed in Step 2).

- [ ] **Step 2: Add `{% raw %}` guards to the two unguarded files**

Open `template/{{cookiecutter.project_slug}}/apps/admin/src/app/page.tsx` and `template/{{cookiecutter.project_slug}}/apps/web/src/app/logout/page.tsx`. In each, find every occurrence of JSX double-brace syntax — patterns like `style={{ ... }}` or `value={{ ... }}` — and wrap the braces:

- `style={{ display: 'flex' }}` becomes `style={% raw %}{{{% endraw %} display: 'flex' {% raw %}}}{% endraw %}`

Use the existing guarded files as reference for the exact idiom, e.g. `template/{{cookiecutter.project_slug}}/apps/web/src/context/AuthContext.tsx` line 120:

```
<div style={% raw %}{{{% endraw %} display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' {% raw %}}}{% endraw %}>
```

To find every occurrence: `grep -n "{{" "template/{{cookiecutter.project_slug}}/apps/admin/src/app/page.tsx" "template/{{cookiecutter.project_slug}}/apps/web/src/app/logout/page.tsx"` — after editing, that grep must only show lines that also contain `{% raw %}`.

- [ ] **Step 3: Run the generation tests**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_generation.py -v`
Expected: ALL pass. If cookiecutter now fails with a `TemplateSyntaxError` naming a specific `.tsx`/`.ts` file, that file has an unguarded `{{` the grep missed — add `{% raw %}` guards there the same way and re-run.

- [ ] **Step 4: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add template/cookiecutter.json "template/{{cookiecutter.project_slug}}/apps/admin/src/app/page.tsx" "template/{{cookiecutter.project_slug}}/apps/web/src/app/logout/page.tsx" && git commit -m "fix(template): render ts/tsx through Jinja — generated frontend was emitted with raw template syntax"
```

---

### Task 9: Keycloak external-auth user creation path

In keycloak mode, `get_current_user` builds a `CreateUserRequest` from token claims. Failure modes: missing email claim → `EmailStr` validation error (500); `preferred_username` containing dots (e.g. `john.doe`, common in Keycloak) → username validator rejects (500); auto-created users get `status=PENDING`. Fix: a dedicated `create_external_user` service method that bypasses the registration DTO.

**Files:**
- Modify: `template/{{cookiecutter.project_slug}}/backend/internal/services/user_service.py`
- Modify: `template/{{cookiecutter.project_slug}}/backend/internal/services/auth_deps.py`
- Test: extend `cli/tests/test_template_generation.py`

- [ ] **Step 1: Add failing generation assertions**

Append to `cli/tests/test_template_generation.py`:

```python
def test_keycloak_has_external_user_path(keycloak_project):
    service = (keycloak_project / "backend/internal/services/user_service.py").read_text()
    assert "create_external_user" in service

    deps = (keycloak_project / "backend/internal/services/auth_deps.py").read_text()
    assert "create_external_user" in deps
    # The buggy DTO-based auto-creation must be gone:
    assert "CreateUserRequest(" not in deps
```

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_generation.py::test_keycloak_has_external_user_path -v`
Expected: FAIL

- [ ] **Step 2: Add `create_external_user` to the service**

In `template/{{cookiecutter.project_slug}}/backend/internal/services/user_service.py`, directly after the `create_user` method (after its `return await self.user_repo.create(user)` line) add:

```python
    {%- if cookiecutter.auth_strategy == 'keycloak' %}
    async def create_external_user(
        self,
        email: str,
        username: Optional[str] = None,
        first_name: str = "",
        last_name: str = "",
        keycloak_id: Optional[str] = None,
    ) -> User:
        """
        Create a user provisioned by an external identity provider (Keycloak).

        Bypasses the registration DTO: external users have no local password,
        the IdP already verified their email, and IdP usernames may contain
        characters the registration validator rejects (e.g. dots).
        """
        if not email:
            raise ValidationError("External identity has no email claim")

        existing = await self.user_repo.get_by_email(email)
        if existing:
            return existing

        base_username = username or email.split("@")[0]
        candidate = base_username
        counter = 1
        while await self.user_repo.get_by_username(candidate):
            candidate = f"{base_username}{counter}"
            counter += 1

        user = User(
            email=email,
            username=candidate,
            first_name=first_name or "",
            last_name=last_name or "",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            is_verified=True,
            keycloak_id=keycloak_id,
        )
        return await self.user_repo.create(user)
    {%- endif %}
```

Note: `ValidationError` is already imported in this file (used by `change_password`); `Optional` is already imported. Verify with `grep -n "ValidationError\|Optional" "template/{{cookiecutter.project_slug}}/backend/internal/services/user_service.py" | head -4` — if either import is missing, add it to the existing import lines.

- [ ] **Step 3: Use it in `auth_deps.py`**

In `template/{{cookiecutter.project_slug}}/backend/internal/services/auth_deps.py`, inside the keycloak block, replace:

```python
        # Get or create user
        user = await user_service.user_repo.get_by_keycloak_id(keycloak_id)
        if not user:
            # Auto-create user from Keycloak data
            from internal.dto.requests import CreateUserRequest
            request = CreateUserRequest(
                email=payload.get("email", ""),
                username=payload.get("preferred_username"),
                first_name=payload.get("given_name"),
                last_name=payload.get("family_name"),
            )
            user = await user_service.create_user(request)
            user.keycloak_id = keycloak_id
            user = await user_service.user_repo.update(user)
        
        return user
```

with:

```python
        # Get or create user
        user = await user_service.user_repo.get_by_keycloak_id(keycloak_id)
        if not user:
            email = payload.get("email")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has no email claim",
                )
            user = await user_service.create_external_user(
                email=email,
                username=payload.get("preferred_username"),
                first_name=payload.get("given_name", ""),
                last_name=payload.get("family_name", ""),
                keycloak_id=keycloak_id,
            )
        
        return user
```

- [ ] **Step 4: Run the generation tests**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_generation.py -v`
Expected: ALL pass (including both compile tests — they parse the new code)

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add "template/{{cookiecutter.project_slug}}/backend/internal/services/user_service.py" "template/{{cookiecutter.project_slug}}/backend/internal/services/auth_deps.py" cli/tests/test_template_generation.py && git commit -m "fix(template): dedicated external-auth user creation for Keycloak (missing email / dotted usernames / pending status)"
```

---

### Task 10: Rate limiter evicts stale IPs

The in-memory limiter cleans only the *requesting* IP's timestamps; every other IP's entry lives forever — unbounded memory growth.

**Files:**
- Modify: `template/{{cookiecutter.project_slug}}/backend/api/middleware/rate_limit.py`
- Create: `template/{{cookiecutter.project_slug}}/backend/tests/test_rate_limit.py`
- Test: extend `cli/tests/test_template_generation.py`

- [ ] **Step 1: Add failing generation assertion**

Append to `cli/tests/test_template_generation.py`:

```python
def test_rate_limiter_has_stale_eviction(jwt_project):
    text = (jwt_project / "backend/api/middleware/rate_limit.py").read_text()
    assert "_sweep_stale" in text
    assert (jwt_project / "backend/tests/test_rate_limit.py").exists()
```

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_generation.py::test_rate_limiter_has_stale_eviction -v`
Expected: FAIL

- [ ] **Step 2: Implement the sweep**

In `template/{{cookiecutter.project_slug}}/backend/api/middleware/rate_limit.py`, replace `__init__`:

```python
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
        self._last_sweep = time.time()

    def _sweep_stale(self, now: float) -> None:
        """Evict IPs with no requests in the last minute (prevents unbounded growth)."""
        if now - self._last_sweep < 60:
            return
        minute_ago = now - 60
        stale = [
            ip for ip, timestamps in self.requests.items()
            if not timestamps or timestamps[-1] <= minute_ago
        ]
        for ip in stale:
            del self.requests[ip]
        self._last_sweep = now
```

And in `dispatch`, immediately after `minute_ago = now - 60`, add:

```python
        # Periodically evict IPs that stopped sending requests
        self._sweep_stale(now)
```

- [ ] **Step 3: Add the template-side unit test**

Create `template/{{cookiecutter.project_slug}}/backend/tests/test_rate_limit.py`:

```python
"""
Unit tests for the in-memory rate limiter.
"""
import time

from api.middleware.rate_limit import RateLimitMiddleware


def test_sweep_evicts_stale_ips():
    mw = RateLimitMiddleware(app=None, requests_per_minute=60)
    mw.requests["1.2.3.4"] = [time.time() - 120]  # last seen 2 minutes ago
    mw.requests["5.6.7.8"] = [time.time()]        # active now
    mw._last_sweep = time.time() - 61             # force a sweep

    mw._sweep_stale(time.time())

    assert "1.2.3.4" not in mw.requests
    assert "5.6.7.8" in mw.requests


def test_sweep_is_throttled():
    mw = RateLimitMiddleware(app=None, requests_per_minute=60)
    mw.requests["1.2.3.4"] = [time.time() - 120]
    mw._last_sweep = time.time()  # swept just now

    mw._sweep_stale(time.time())

    # Not 60s since last sweep — stale entry survives this call
    assert "1.2.3.4" in mw.requests
```

(This runs inside generated projects via their own pytest; the golden-path e2e in Phase 4 executes it.)

- [ ] **Step 4: Run the generation tests**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_generation.py -v`
Expected: ALL pass

- [ ] **Step 5: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add "template/{{cookiecutter.project_slug}}/backend/api/middleware/rate_limit.py" "template/{{cookiecutter.project_slug}}/backend/tests/test_rate_limit.py" cli/tests/test_template_generation.py && git commit -m "fix(template): rate limiter evicts stale IPs (memory leak)"
```

---

### Task 11: Rewrite the generated `test_user_service.py` to match the real service API

The shipped test file cannot run at all: it constructs `UserService(user_repository=...)` (real kwarg: `user_repo`), calls `create_user(email=..., password=...)` (real signature: `create_user(request: CreateUserRequest)`), calls `get_user_by_id` (real name: `get_user`), and expects `ValueError("Email already exists")` (real: `ConflictError("User with this email already exists")`).

**Files:**
- Rewrite: `template/{{cookiecutter.project_slug}}/backend/tests/test_user_service.py`
- Test: extend `cli/tests/test_template_generation.py`

- [ ] **Step 1: Add failing generation assertion**

Append to `cli/tests/test_template_generation.py`:

```python
def test_generated_user_service_test_matches_real_api(jwt_project):
    text = (jwt_project / "backend/tests/test_user_service.py").read_text()
    assert "user_repository=" not in text      # real kwarg is user_repo
    assert "get_user_by_id" not in text        # real method is get_user
    assert "CreateUserRequest" in text         # real signature takes a DTO
    assert "ConflictError" in text             # real exception type
```

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_generation.py::test_generated_user_service_test_matches_real_api -v`
Expected: FAIL

- [ ] **Step 2: Rewrite the template test file**

Replace the entire contents of `template/{{cookiecutter.project_slug}}/backend/tests/test_user_service.py` with:

```python
"""
Unit tests for User Service.
Tests business logic with mocked dependencies.
"""
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from internal.services.user_service import UserService
from internal.entities.user import User, UserRole, UserStatus
from internal.dto.requests import CreateUserRequest
from pkg.errors.exceptions import ConflictError, NotFoundError


@pytest.fixture
def mock_user_repo():
    """Mock user repository; lookups miss by default."""
    repo = AsyncMock()
    repo.get_by_email.return_value = None
    repo.get_by_username.return_value = None
    repo.get_by_id.return_value = None
    return repo


@pytest.fixture
def user_service(mock_user_repo):
    return UserService(user_repo=mock_user_repo)


def _make_request(**overrides) -> CreateUserRequest:
    data = {
        "email": "test@example.com",
        "username": "testuser",
        {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
        "password": "SecurePass123",
        {%- endif %}
    }
    data.update(overrides)
    return CreateUserRequest(**data)


def _make_user(**overrides) -> User:
    defaults = dict(
        email="test@example.com",
        username="testuser",
        status=UserStatus.PENDING,
    )
    defaults.update(overrides)
    return User(**defaults)


class TestUserService:
    """Tests for UserService business logic."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_user_repo):
        mock_user_repo.create.return_value = _make_user()

        user = await user_service.create_user(_make_request())

        assert user.email == "test@example.com"
        mock_user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service, mock_user_repo):
        mock_user_repo.get_by_email.return_value = _make_user(username="existing")

        with pytest.raises(ConflictError, match="email already exists"):
            await user_service.create_user(_make_request())

    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service, mock_user_repo):
        existing = _make_user()
        mock_user_repo.get_by_id.return_value = existing

        user = await user_service.get_user(existing.id)

        assert user.id == existing.id
        mock_user_repo.get_by_id.assert_called_once_with(existing.id)

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service, mock_user_repo):
        with pytest.raises(NotFoundError):
            await user_service.get_user(uuid4())

    @pytest.mark.asyncio
    async def test_activate_user(self, user_service, mock_user_repo):
        user = _make_user(status=UserStatus.PENDING)
        mock_user_repo.get_by_id.return_value = user
        mock_user_repo.update.side_effect = lambda u: u

        result = await user_service.activate_user(user.id)

        assert result.status == UserStatus.ACTIVE
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_suspend_user(self, user_service, mock_user_repo):
        user = _make_user(status=UserStatus.ACTIVE)
        mock_user_repo.get_by_id.return_value = user
        mock_user_repo.update.side_effect = lambda u: u

        result = await user_service.suspend_user(user.id)

        assert result.status == UserStatus.SUSPENDED

    @pytest.mark.asyncio
    async def test_delete_user(self, user_service, mock_user_repo):
        user = _make_user()
        mock_user_repo.get_by_id.return_value = user
        mock_user_repo.delete.return_value = True

        result = await user_service.delete_user(user.id)

        assert result is True
        mock_user_repo.delete.assert_called_once_with(user.id)

    @pytest.mark.asyncio
    async def test_delete_super_admin_is_rejected(self, user_service, mock_user_repo):
        from pkg.errors.exceptions import ValidationError

        user = _make_user(role=UserRole.SUPER_ADMIN)
        mock_user_repo.get_by_id.return_value = user

        with pytest.raises(ValidationError, match="super admin"):
            await user_service.delete_user(user.id)
```

- [ ] **Step 3: Run the generation tests**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest tests/test_template_generation.py -v`
Expected: ALL pass (the compile tests parse the rewritten file for both jwt and keycloak contexts — the Jinja conditional around `password` makes it valid in both)

- [ ] **Step 4: Commit**

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add "template/{{cookiecutter.project_slug}}/backend/tests/test_user_service.py" cli/tests/test_template_generation.py && git commit -m "fix(template): rewrite user service tests to match the real service API"
```

---

### Task 12: Phase completion — full suite, changelog, version bump

**Files:**
- Modify: `cli/pyproject.toml`
- Modify: `CHANGELOG.md`
- Modify: `template/cookiecutter.json`

- [ ] **Step 1: Full test suite green**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && python3 -m pytest -q 2>&1 | tail -3`
Expected: `0 failed` — around 95+ passed (80 original + new files), 0 failures. If anything fails, fix before proceeding.

- [ ] **Step 2: Bump version**

In `cli/pyproject.toml`: `version = "1.12.15"` → `version = "1.13.1"`.
In `template/cookiecutter.json`: `"_lich_version": "1.12.12"` → `"_lich_version": "1.13.1"`.

- [ ] **Step 3: Changelog entry**

At the top of `CHANGELOG.md` (after the intro lines, before `## [1.12.15]`), insert:

```markdown
## [1.13.1] - 2026-07-10

### Fixed
- **Generated frontend was broken**: `.tsx`/`.ts` files were copied verbatim with raw Jinja syntax inside (regression from v1.12.12). Templates now render through Jinja with `{% raw %}` guards where JSX uses `{{ }}`.
- **Keycloak auth**: auto-created users no longer fail on missing email claims, dotted usernames, or pending status — new `create_external_user` service path.
- **MCP**: tool failures now return `ERROR (exit N):` prefixed output instead of silently looking like success.
- **MCP**: implemented the documented-but-missing `lich_ci_all` tool; tool inventory test now matches the real 52 registered tools (docs claimed 47).
- **Rate limiter**: in-memory limiter evicts stale IPs (unbounded memory growth).
- **Generated tests**: `test_user_service.py` now matches the real service API (it previously could not run at all).
- **`lich version --history`**: robust CHANGELOG resolution outside dev checkouts.

### Added
- Template generation smoke-test harness in the CLI test suite (`test_template_generation.py`): renders the template and asserts no Jinja leaks, backend compiles, and key fixes are present.
```

- [ ] **Step 4: Final verification and commit**

Run: `cd /Users/babak/codes/DoTech/lich-framework/cli && pip install -e . -q && python3 -m pytest -q 2>&1 | tail -3`
Expected: all pass with the new version installed

```bash
cd /Users/babak/codes/DoTech/lich-framework && git add cli/pyproject.toml CHANGELOG.md template/cookiecutter.json && git commit -m "chore: release v1.13.1 — correctness sprint (Phase 2 of v1 hardening)"
```

- [ ] **Step 5 (manual, optional): Update the BabakOS vault note**

`/Users/babak/codes/knowledge/babakOS/BabakOS/90-Shared/lich-framework.md` says "47 MCP tools" — update to 52 when releasing (the post-commit vault hook updates activity but not this claim).

---

## Execution Notes for Sonnet

- Always run tests from `cli/` (`pytest.ini` lives there). Template paths contain literal `{{cookiecutter.project_slug}}` — quote them in shell commands.
- Task 0 is mandatory first; without the editable install your edits are invisible to tests.
- Tasks 1–5 are CLI-side and sequential (2 depends on 1). Tasks 7–11 are template-side and sequential (8–11 depend on 7's harness). Task 6 (docs) can run any time after 1.
- If a step's expected output doesn't match, STOP and re-read the file — do not force the assertion to pass.
