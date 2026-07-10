# Lich v2 — Phases 2–4: Quality + Continuous, Plugins, Deploy + Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **DRAFT (2026-07-10, written pre-v1-hardening and pre-Phase-1):** Phase 2 is near-executable; Phases 3–4 are detailed-task-level and MUST get a refinement pass before execution. Tasks marked **[RE-VERIFY]** depend on earlier phases' actual output (module names, function signatures, TUI structure). Long code bodies in Phases 3–4 are representative, not exhaustive — interfaces and acceptance criteria are binding, exact bodies are not. Double-check pass planned with Opus.

**Goal:** Ship v2 Phases 2–4 per the spec (`docs/superpowers/specs/2026-04-14-lich-v2-design.md` §9–§16): self-validating generation, continuous mode, knowledge-graph context assembly, the plugin system, architecture guardian, Zenith/FairBroker deploy, spec marketplace, and project insights.

**Architecture:** All new code lives under `cli/src/lich/` per the spec module map (§3): validators under `codegen/validators/`, memory under `memory/`, plugins under `plugins/`, deploy adapters under `deploy/`. Validators are AST-based (stdlib `ast`), memory is plain markdown + a JSON index (no embeddings), plugins use Python entry points (`lich.plugins`), deploy adapters shell out to provider CLIs via `asyncio.create_subprocess_exec` (never `shell=True` — spec D11).

**Tech Stack:** Python 3.10+, Typer, Textual, Jinja2, pyyaml, stdlib `ast`/`json`/`re`. No new heavy dependencies; `vulture` (dead code) is optional and vendored behind an extra.

**Path note:** the parent directive said `validation/architecture.py`; the spec module map (§3) says `codegen/validators/architecture.py`. This plan follows the **spec**.

---

## Phase 2: Quality + Continuous (near-executable)

### Task 2.1: Architecture validator — AST-based compliance checks

**Files:**
- Create: `cli/src/lich/codegen/validators/__init__.py`
- Create: `cli/src/lich/codegen/validators/architecture.py`
- Test: `cli/tests/test_arch_validator.py`

Implements spec §9 checks 1, 2, 3, 5 (entity isolation, services-use-ports, every-entity-has-port, DTO boundary). Checks 6–7 (circular imports, tests-exist) come in Task 2.2's pipeline via existing tools (`lich lint`, `lich test`).

- [ ] **Step 1: Write the failing tests**

```python
# cli/tests/test_arch_validator.py
"""Architecture validator tests — run against synthetic project trees."""
from pathlib import Path

import pytest

from lich.codegen.validators.architecture import (
    Violation,
    check_entity_isolation,
    check_services_use_ports,
    check_entities_have_ports,
    check_api_uses_dtos,
    validate_project,
)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """Minimal hexagonal backend tree."""
    (tmp_path / "backend/internal/entities").mkdir(parents=True)
    (tmp_path / "backend/internal/ports").mkdir(parents=True)
    (tmp_path / "backend/internal/services").mkdir(parents=True)
    (tmp_path / "backend/internal/adapters/db").mkdir(parents=True)
    (tmp_path / "backend/api/http").mkdir(parents=True)
    return tmp_path


def _w(root: Path, rel: str, code: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(code)


def test_clean_entity_passes(project):
    _w(project, "backend/internal/entities/user.py",
       "from dataclasses import dataclass\n@dataclass\nclass User:\n    name: str\n")
    assert check_entity_isolation(project) == []


def test_entity_importing_adapter_flagged(project):
    _w(project, "backend/internal/entities/user.py",
       "from internal.adapters.db.user_repo import UserRepo\nclass User: ...\n")
    violations = check_entity_isolation(project)
    assert len(violations) == 1
    assert violations[0].rule == "entity-isolation"
    assert "user.py" in violations[0].file


def test_entity_importing_sqlalchemy_flagged(project):
    _w(project, "backend/internal/entities/user.py",
       "import sqlalchemy\nclass User: ...\n")
    assert check_entity_isolation(project)[0].rule == "entity-isolation"


def test_service_importing_adapter_flagged(project):
    _w(project, "backend/internal/services/user_service.py",
       "from internal.adapters.db.user_repo import PostgresUserRepo\n")
    violations = check_services_use_ports(project)
    assert violations and violations[0].rule == "service-uses-ports"


def test_service_importing_port_passes(project):
    _w(project, "backend/internal/services/user_service.py",
       "from internal.ports.repositories import UserRepository\n")
    assert check_services_use_ports(project) == []


def test_entity_without_port_flagged(project):
    _w(project, "backend/internal/entities/order.py",
       "from dataclasses import dataclass\n@dataclass\nclass Order:\n    total: int\n")
    _w(project, "backend/internal/ports/repositories.py", "class UserRepository: ...\n")
    violations = check_entities_have_ports(project)
    assert violations and violations[0].rule == "entity-has-port"
    assert "Order" in violations[0].message


def test_api_returning_entity_flagged(project):
    _w(project, "backend/api/http/users.py",
       "from internal.entities.user import User\n"
       "def get_user() -> User: ...\n")
    violations = check_api_uses_dtos(project)
    assert violations and violations[0].rule == "api-uses-dtos"


def test_api_using_dto_passes(project):
    _w(project, "backend/api/http/users.py",
       "from internal.dto.responses import UserResponse\n"
       "def get_user() -> 'UserResponse': ...\n")
    assert check_api_uses_dtos(project) == []


def test_validate_project_aggregates(project):
    _w(project, "backend/internal/entities/user.py", "import sqlalchemy\n")
    report = validate_project(project)
    assert report.passed is False
    assert any(v.rule == "entity-isolation" for v in report.violations)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_arch_validator.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'lich.codegen'`

- [ ] **Step 3: Write the validator**

```python
# cli/src/lich/codegen/validators/__init__.py
"""Clean Architecture compliance validators (spec §9)."""
```

```python
# cli/src/lich/codegen/validators/architecture.py
"""AST-based Clean Architecture compliance checks.

Rules (spec §9):
  entity-isolation   — entities must not import adapters or ORM libs
  service-uses-ports — services import ports, never adapters
  entity-has-port    — every entity class has a matching port
  api-uses-dtos      — API modules must not return entities directly
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

FORBIDDEN_IN_ENTITIES = ("adapters", "sqlalchemy", "beanie", "motor", "fastapi")
ADAPTER_MARKER = "adapters"
PORT_MARKER = "ports"


@dataclass
class Violation:
    rule: str
    file: str
    line: int
    message: str


@dataclass
class Report:
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.violations


def _iter_py(root: Path, sub: str) -> list[Path]:
    d = root / sub
    return sorted(d.rglob("*.py")) if d.is_dir() else []


def _imports(tree: ast.AST) -> list[tuple[str, int]]:
    """All imported module dotted-paths with line numbers."""
    out: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend((a.name, node.lineno) for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append((node.module, node.lineno))
    return out


def _parse(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text())
    except SyntaxError:
        return None  # lint catches this; not an architecture violation


def check_entity_isolation(root: Path) -> list[Violation]:
    violations = []
    for f in _iter_py(root, "backend/internal/entities"):
        tree = _parse(f)
        if tree is None:
            continue
        for mod, line in _imports(tree):
            if any(bad in mod.split(".") for bad in FORBIDDEN_IN_ENTITIES):
                violations.append(Violation(
                    "entity-isolation", str(f), line,
                    f"entity imports '{mod}' — entities must stay pure"))
    return violations


def check_services_use_ports(root: Path) -> list[Violation]:
    violations = []
    for f in _iter_py(root, "backend/internal/services"):
        tree = _parse(f)
        if tree is None:
            continue
        for mod, line in _imports(tree):
            if ADAPTER_MARKER in mod.split("."):
                violations.append(Violation(
                    "service-uses-ports", str(f), line,
                    f"service imports adapter '{mod}' — depend on ports instead"))
    return violations


def _class_names(root: Path, sub: str) -> set[str]:
    names: set[str] = set()
    for f in _iter_py(root, sub):
        tree = _parse(f)
        if tree is None:
            continue
        names |= {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    return names


def check_entities_have_ports(root: Path) -> list[Violation]:
    entities = _class_names(root, "backend/internal/entities")
    port_text = " ".join(
        f.read_text() for f in _iter_py(root, "backend/internal/ports"))
    return [
        Violation("entity-has-port", "backend/internal/ports", 0,
                  f"entity '{e}' has no matching port (no '{e}' reference in ports/)")
        for e in sorted(entities)
        if e not in ("BaseEntity",) and e not in port_text
    ]


def check_api_uses_dtos(root: Path) -> list[Violation]:
    violations = []
    for f in _iter_py(root, "backend/api"):
        tree = _parse(f)
        if tree is None:
            continue
        entity_imports = {
            mod.rsplit(".", 1)[-1] if "." in mod else mod
            for mod, _ in _imports(tree) if ".entities." in f".{mod}."
        }
        imported_entity_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "entities" in node.module.split("."):
                imported_entity_names |= {a.name for a in node.names}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                ret = node.returns
                if isinstance(ret, ast.Name) and ret.id in imported_entity_names:
                    violations.append(Violation(
                        "api-uses-dtos", str(f), node.lineno,
                        f"endpoint '{node.name}' returns entity '{ret.id}' — return a DTO"))
    return violations


def validate_project(root: Path) -> Report:
    report = Report()
    for check in (check_entity_isolation, check_services_use_ports,
                  check_entities_have_ports, check_api_uses_dtos):
        report.violations.extend(check(root))
    return report
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_arch_validator.py -v`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/codegen/validators/ cli/tests/test_arch_validator.py
git commit -m "feat(v2): AST-based architecture compliance validator"
```

---

### Task 2.2: Self-validation pipeline **[RE-VERIFY: generator API lands in Phase 1]**

**Files:**
- Create: `cli/src/lich/codegen/pipeline.py`
- Test: `cli/tests/test_validation_pipeline.py`
- Modify: `cli/src/lich/codegen/engine.py` (Phase 1 output — wire pipeline after generation)

Flow per spec §9: generated code → `ruff` → arch check → auto-fix (max 3 rounds) → report with warnings if still failing.

- [ ] **Step 1: Write failing tests** — pipeline with mocked runners: (a) all green → `passed=True, rounds=1`; (b) lint fails once, `ruff --fix` fixes it → `passed=True, rounds=2`; (c) persistent arch violation → `passed=False`, violations surfaced, exactly 3 rounds attempted. Use dependency-injected runner callables so no subprocess in tests.

```python
# cli/tests/test_validation_pipeline.py (core cases; representative but complete enough to run)
from lich.codegen.pipeline import ValidationPipeline, StepResult

def test_all_green_single_round(tmp_path):
    p = ValidationPipeline(
        lint=lambda root: StepResult(True, ""),
        arch=lambda root: StepResult(True, ""),
        autofix=lambda root, errors: False,
    )
    r = p.run(tmp_path)
    assert r.passed and r.rounds == 1

def test_autofix_recovers(tmp_path):
    calls = {"n": 0}
    def lint(root):
        calls["n"] += 1
        return StepResult(calls["n"] > 1, "E501 line too long")
    p = ValidationPipeline(lint=lint,
                           arch=lambda root: StepResult(True, ""),
                           autofix=lambda root, errors: True)
    r = p.run(tmp_path)
    assert r.passed and r.rounds == 2

def test_gives_up_after_three_rounds(tmp_path):
    p = ValidationPipeline(lint=lambda root: StepResult(False, "E999"),
                           arch=lambda root: StepResult(True, ""),
                           autofix=lambda root, errors: True)
    r = p.run(tmp_path)
    assert not r.passed and r.rounds == 3 and "E999" in r.warnings[0]
```

- [ ] **Step 2: Verify fail** — `pytest tests/test_validation_pipeline.py` → `ModuleNotFoundError`

- [ ] **Step 3: Implement `pipeline.py`**

```python
# cli/src/lich/codegen/pipeline.py
"""Self-validating generation loop (spec §9). DI-friendly: runners injected."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

MAX_ROUNDS = 3

@dataclass
class StepResult:
    ok: bool
    output: str

@dataclass
class PipelineResult:
    passed: bool
    rounds: int
    warnings: list[str] = field(default_factory=list)

class ValidationPipeline:
    def __init__(self,
                 lint: Callable[[Path], StepResult],
                 arch: Callable[[Path], StepResult],
                 autofix: Callable[[Path, str], bool]):
        self.lint, self.arch, self.autofix = lint, arch, autofix

    def run(self, root: Path) -> PipelineResult:
        for round_no in range(1, MAX_ROUNDS + 1):
            failures = [r for r in (self.lint(root), self.arch(root)) if not r.ok]
            if not failures:
                return PipelineResult(True, round_no)
            if round_no < MAX_ROUNDS:
                self.autofix(root, "\n".join(f.output for f in failures))
        return PipelineResult(False, MAX_ROUNDS,
                              warnings=[f.output for f in failures])
```

Default runners (wired in `engine.py`, **[RE-VERIFY]** against Phase 1's actual engine): `lint` → `ruff check` via `asyncio.create_subprocess_exec`; `arch` → `validate_project()` from Task 2.1; `autofix` → `ruff check --fix` first (deterministic), then ONE AI call through the Phase 1 `AIProvider` with the error context (spec: test failures go to AI, lint/imports stay deterministic).

- [ ] **Step 4: Verify pass** — `pytest tests/test_validation_pipeline.py -v` → PASS
- [ ] **Step 5: Wire into `engine.py` after generation [RE-VERIFY]** — every `generate()` call ends with `pipeline.run(project_root)`; result shown in TUI/CLI output.
- [ ] **Step 6: Commit** — `git commit -m "feat(v2): self-validation pipeline with bounded auto-fix"`

---

### Task 2.3: Memory index — extend `MemoryIndex` with the graph-walk API (spec task 2.11)

> **CONTRACT: `2026-07-10-CONTRACTS.md` §C3.** `cli/src/lich/memory/index.py` ALREADY EXISTS
> (created by Phase 1b Task 2). This task EXTENDS that class — never recreate the file.
> Additions: `@classmethod build()`, `resolve_mentions()`, `walk()`; migrate `edges` from
> `list` to `set` (keep `save()` output sorted). There is NO `@classmethod load(path)` —
> it would clash with the existing instance `load()`; load via `MemoryIndex(vault).load()`.
> The canonical `Note` model lives in `lich.memory.notes` (§C2) — do not define a second one here.

**Files:**
- Modify: `cli/src/lich/memory/index.py` (created by Phase 1b Task 2)
- Test: `cli/tests/test_memory_index.py` (append; Phase 1b's existing tests must stay green)
- Depends on: Phase 1b Task 1 (`memory/notes.py`) and Task 2 (`memory/index.py`) **[RE-VERIFY against the as-landed files]**

- [ ] **Step 1: Write failing tests**

```python
# cli/tests/test_memory_index.py
from pathlib import Path

import pytest

from lich.memory.index import MemoryIndex

# NOTE: put the `vault` fixture and `_note` helper in cli/tests/conftest.py —
# test_assembler.py (Task 2.4) reuses them.

def _note(root: Path, name: str, body: str, type_: str = "entity"):
    (root / f"{name}.md").write_text(
        f"---\ntype: {type_}\nname: {name}\n---\n\n{body}\n")

@pytest.fixture
def vault(tmp_path):
    _note(tmp_path, "Product", "Belongs to [[User]]. Tagged via [[Tag]].")
    _note(tmp_path, "User", "Buys [[Product]].")
    _note(tmp_path, "Tag", "Labels.")
    _note(tmp_path, "decision-positive-prices", "Price > 0 on [[Product]]", "decision")
    return tmp_path

def test_build_extracts_nodes_and_edges(vault):
    idx = MemoryIndex.build(vault)
    assert set(idx.nodes) >= {"Product", "User", "Tag", "decision-positive-prices"}
    assert ("Product", "User") in idx.edges and ("Product", "Tag") in idx.edges

def test_resolve_mentions_finds_entities_in_task_text(vault):
    idx = MemoryIndex.build(vault)
    assert idx.resolve_mentions("add reviews to Product") == ["Product"]

def test_walk_two_hops(vault):
    idx = MemoryIndex.build(vault)
    names = set(idx.walk(["Product"], max_hops=2))
    assert {"Product", "User", "Tag", "decision-positive-prices"} <= names

def test_walk_one_hop_excludes_second_degree(vault):
    _note(vault, "Order", "Has [[LineItem]].")
    _note(vault, "LineItem", "Line.")
    idx = MemoryIndex.build(vault)
    names = set(idx.walk(["Order"], max_hops=1))
    assert "LineItem" in names  # 1 hop
    # LineItem's own neighbors beyond hop 1 would be excluded (none here)

def test_round_trip_json(vault):
    idx = MemoryIndex.build(vault)   # build() persists via rebuild() -> save()
    loaded = MemoryIndex(vault)
    loaded.load()                    # instance load, per CONTRACTS §C3
    assert loaded.edges == idx.edges
```

- [ ] **Step 2: Verify fail** — `ModuleNotFoundError: lich.memory`
- [ ] **Step 3: Implement**

```python
# cli/src/lich/memory/index.py — EXTENSIONS to the Phase 1b MemoryIndex (CONTRACTS §C3).
# The class, __init__(vault_dir), rebuild(), update_note(), neighbors(), save(), load()
# already exist. Apply these MIGRATIONS to the existing methods:
#
#   __init__:     self.edges: set[tuple[str, str]] = set()          # was: list
#   _index_file:  self.edges.add((note.name, target))               # was: .append(...)
#   update_note:  self.edges = {(s, d) for s, d in self.edges if s != name}
#   save():       "edges": sorted(list(e) for e in self.edges)      # deterministic on disk
#   load():       self.edges = {tuple(e) for e in data["edges"]}
#
# The on-disk .index.json schema is unchanged; Phase 1b indexes stay readable.
# Then ADD these methods to the class (imports: `import re` if not present):

_TASK_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")


    @classmethod
    def build(cls, vault_dir: Path) -> "MemoryIndex":
        """Construct + full rebuild (persists .index.json via rebuild() -> save())."""
        idx = cls(vault_dir)
        idx.rebuild()
        return idx

    def resolve_mentions(self, task: str) -> list[str]:
        """Note names literally mentioned in free task text, sorted."""
        words = set(_TASK_WORD.findall(task))
        return sorted(n for n in self.nodes if n in words)

    def walk(self, start: list[str], max_hops: int = 2) -> list[str]:
        """BFS over the link graph. Returns note NAMES, start nodes first (CONTRACTS §C3:
        callers needing bodies use read_note(vault_dir / nodes[name]["path"]))."""
        seen = [n for n in start if n in self.nodes]
        frontier, visited = set(seen), set(seen)
        for _ in range(max_hops):
            frontier = {nb for n in frontier for nb in self.neighbors(n)} - visited
            frontier &= set(self.nodes)
            seen.extend(sorted(frontier))
            visited |= frontier
        return seen
```

- [ ] **Step 4: Verify pass** — `pytest tests/test_memory_index.py -v` → PASS
- [ ] **Step 5: Incremental rebuild hook** — `notes.py` write path calls `MemoryIndex.build(vault).save(vault / ".index.json")` after each note write (full rebuild is fine at v2 scale; measure before optimizing). **[RE-VERIFY against Phase 1 notes.py]**
- [ ] **Step 6: Commit** — `git commit -m "feat(v2): memory graph index over .lich/memory/"`

---

### Task 2.4: Context Assembler (spec task 2.12 — the killer feature)

**Files:**
- Create: `cli/src/lich/memory/assembler.py`
- Test: `cli/tests/test_assembler.py`
- Modify: `cli/src/lich/ai/provider.py` **[RE-VERIFY: Phase 1 AIProvider API]**

- [ ] **Step 1: Write failing tests**

```python
# cli/tests/test_assembler.py
from lich.memory.assembler import ContextAssembler, estimate_tokens
from lich.memory.index import MemoryIndex

def test_estimate_tokens_chars_over_four():
    assert estimate_tokens("x" * 400) == 100

def test_assemble_includes_start_node_first(vault):  # reuse vault fixture
    asm = ContextAssembler(MemoryIndex.build(vault))
    out = asm.assemble("add reviews to Product", budget_tokens=8000)
    assert out.index("# Product") < out.index("# User")

def test_assemble_respects_budget(vault):
    asm = ContextAssembler(MemoryIndex.build(vault))
    out = asm.assemble("add reviews to Product", budget_tokens=40)
    assert estimate_tokens(out) <= 40

def test_assemble_no_mentions_returns_empty(vault):
    asm = ContextAssembler(MemoryIndex.build(vault))
    assert asm.assemble("refactor logging", budget_tokens=8000) == ""
```

- [ ] **Step 2: Verify fail**
- [ ] **Step 3: Implement**

```python
# cli/src/lich/memory/assembler.py
"""Graph-walk note retrieval within a token budget (spec Feature 12).

Replaces whole-codebase reads for BYOA models — critical for small-context
local models (e.g. Qwen3-32B, 32K window).
"""
from __future__ import annotations

from .index import MemoryIndex
from .notes import read_note


def estimate_tokens(text: str) -> int:
    """Provider-agnostic heuristic: ~4 chars per token."""
    return len(text) // 4


class ContextAssembler:
    def __init__(self, index: MemoryIndex):
        self.index = index

    def assemble(self, task: str, budget_tokens: int = 8_000) -> str:
        start = self.index.resolve_mentions(task)
        if not start:
            return ""
        names = self.index.walk(start, max_hops=2)  # note NAMES, start first (CONTRACTS §C3)
        return self.pack(names, budget_tokens)

    def pack(self, names: list[str], budget_tokens: int) -> str:
        parts: list[str] = []
        used = 0
        for name in names:
            note = read_note(self.index.vault_dir / self.index.nodes[name]["path"])
            chunk = f"# {note.name}\n{note.body.strip()}\n"
            cost = estimate_tokens(chunk)
            if used + cost > budget_tokens:
                continue  # earlier (closer) notes have priority; skip what doesn't fit
            parts.append(chunk)
            used += cost
        return "\n".join(parts)
```

- [ ] **Step 4: Verify pass** — PASS
- [ ] **Step 5: Wire into AI adapter [RE-VERIFY]** — before each `ask()`/`ask_structured()` in a project context, prepend `assembler.assemble(task, budget)` to the prompt; budget from `lich config` key `ai.context_budget` (default 8000). Acceptance (spec Phase 2 criteria): `add_feature` builds context from the graph with **no whole-codebase reads**.
- [ ] **Step 6: Commit**

---

### Task 2.5: Continuous mode + diff-based modification **[RE-VERIFY: TUI/builder from Phase 1]**

**Files:**
- Create: `cli/src/lich/codegen/patcher.py`
- Create: `cli/src/lich/concepts/workflows/add_feature.yaml`, `add_entity.yaml`
- Modify: `cli/src/lich/tui/builder.py`
- Test: `cli/tests/test_patcher.py`

Spec §10 flow: read existing → AI plans additions+modifications → show plan → generate new + patch existing → self-validate (Task 2.2 pipeline).

- [ ] **Step 1: Failing tests for `patcher.py`** — apply-unified-diff to a file (happy path), reject on context mismatch (stale diff), dry-run returns preview without writing. (Representative signatures below are binding.)
- [ ] **Step 2: Implement patcher**

```python
# cli/src/lich/codegen/patcher.py — binding interface
class PatchError(Exception): ...

def preview(path: Path, diff: str) -> str: ...        # patched text, no write
def apply(path: Path, diff: str) -> None: ...          # atomic write or PatchError
```

Implementation: stdlib `difflib`-based context matching (no external `patch` binary). AI is asked (Phase 1 prompt templates) to return unified diffs; `preview()` renders in TUI for approval before `apply()`.

- [ ] **Step 3: `add_feature.yaml` / `add_entity.yaml` concepts** — steps: `read_memory` (Task 2.4 assembler) → `plan` (AI, structured JSON: new_files[], modified_files[]) → `show_plan` (TUI approval gate) → `generate` (engine) + `patch` (patcher) → `validate` (pipeline). Follow the Phase 1 `create_app.yaml` step schema exactly. **[RE-VERIFY schema]**
- [ ] **Step 4: TUI wiring** — `lich tui` on an existing project (detect `.lich` marker) opens in continuous mode: prompt box → concept dispatch. **[RE-VERIFY]**
- [ ] **Step 5: Verify** — `pytest tests/test_patcher.py -v` PASS; manual TUI smoke: open on a generated project, request "add email field to User", see plan + diff + approval.
- [ ] **Step 6: Commit**

---

### Task 2.6: Session notes writer (spec task 2.13) **[RE-VERIFY: session lifecycle from Phase 1 TUI]**

**Files:**
- Create: `cli/src/lich/memory/session.py`
- Test: `cli/tests/test_session_notes.py`
- Modify: `cli/src/lich/tui/builder.py` (write on session end)

- [ ] **Step 1: Failing test** — `SessionRecorder` collects events (`asked`, `generated`, `modified`, `decided`); `flush(vault)` writes `session-YYYY-MM-DD-HHMM.md` with frontmatter `type: session`, wikilinks to touched entities, and triggers index rebuild.
- [ ] **Step 2: Implement** — recorder is append-only in memory; `flush()` renders markdown (template string, no Jinja needed) and calls `notes.write_note()`. Timestamps injected via constructor (`now: datetime`) for testability.
- [ ] **Step 3: Wire** — TUI `on_unmount` / builder `close_session()` calls `flush()`.
- [ ] **Step 4: Verify + commit**

---

### Task 2.7: Phase 2 completion

- [ ] Full suite: `cd cli && python3 -m pytest -q` → green
- [ ] Acceptance criteria from spec Phase 2 checklist verified one by one (validation-before-show, add-feature works, pre-commit hook → moved to Phase 3 guardian task, insights → moved to Phase 4, assembler budget respected)
- [ ] CHANGELOG entry, version bump — **RESOLVED (2026-07-10, D17): lich CLI v2 releases as `2.0.0-alpha.N` pre-releases (GA = `2.0.0`); `lich-core` starts at `0.1.0` and reaches `1.0.0` at v2 GA.** Commit.

---

## Phase 3: Plugin System (detailed-task level — refinement pass required)

### Task 3.1: `LichPlugin` protocol + entry-point discovery

**Files:** `cli/src/lich/plugins/interface.py`, `cli/src/lich/plugins/registry.py`, tests.

Binding interface (spec §11):

```python
# interface.py
class LichPlugin(Protocol):
    name: str
    version: str
    manifest_path: Path          # lich-plugin.yaml inside the package

# registry.py
def discover() -> dict[str, LichPlugin]:
    """importlib.metadata.entry_points(group='lich.plugins')"""
```

Verification: a test-local dummy package registered via `entry_points` fixture (use `importlib.metadata` monkeypatching — no real pip install in unit tests) is discovered by name.

### Task 3.2: `lich-plugin.yaml` schema + validation

**Files:** `cli/src/lich/plugins/schema.py`, tests.

Dataclasses mirroring spec §11 exactly: `provides.scaffold` (entities/services/apis/frontend/migrations), `provides.runtime` (middleware/cli_commands/ai_rules/env_vars), `requires.python`. `load_manifest(path) -> PluginManifest` with actionable `ManifestError` per missing/unknown field. Test matrix: valid full manifest (the spec's payments example verbatim), missing `name`, unknown top-level key, bad env_var entry.

### Task 3.3: Plugin manager — add / remove / list / info

**Files:** `cli/src/lich/plugins/manager.py`, `cli/src/lich/commands/plugin.py` (Typer sub-app), tests.

- `add <name-or-path>`: PyPI name → `pip install` via `asyncio.create_subprocess_exec` (list argv, never shell — D11 + v1 hardening `_shell.py` conventions); local path → `pip install -e`. Then `discover()` + manifest validation + scaffold injection (Task 3.4).
- `remove`: un-scaffold is NOT attempted (user owns scaffolded code — spec D4); runtime parts deactivate on uninstall. Print what stays and why.
- `list` / `info`: table via Rich from discovered manifests.
- Verification: CliRunner tests with a fixture plugin dir; `pip` calls mocked.

### Task 3.4: Scaffold injection

**Files:** `cli/src/lich/plugins/scaffold.py`, tests.

For each `provides.scaffold` item, render the plugin's Jinja2 templates through the **Phase 1 codegen engine** (same `engine.py` entry point — no second render path) into the target project; entity strings reuse the Phase 1 field parser. Conflict policy: existing file → skip + warn (never overwrite user code). **[RE-VERIFY engine API]**

### Task 3.5: Runtime injection

Runtime parts (middleware, CLI commands) activate via the `lich.plugins` entry points consumed by `lich_core.create_app()` (Phase 0) and `cli.py` plugin sub-app registration. env_vars from manifest are appended to the project's `.env.example` with `# from plugin: <name>` markers. **[RE-VERIFY lich-core hook signature]**

### Task 3.6: `lich make plugin <name>` scaffold (spec 3.9)

Generates a plugin package skeleton: `pyproject.toml` with entry point, `lich-plugin.yaml` stub passing schema validation, one example scaffold template, README. Verification: scaffold → `pip install -e` → `lich plugin list` shows it.

### Task 3.7: Architecture Guardian CLI (spec §12; moved here from Phase 2 per plan scope)

**Files:** `cli/src/lich/commands/guardian.py`, tests.

- `lich guardian check` — runs Task 2.1 `validate_project()` + secret-pattern grep (reuse v1 `secret.py` patterns) on the current project; Rich table of violations; exit 1 on any.
- `lich guardian install` — writes `.git/hooks/pre-commit` shell stub calling `lich guardian check` (respect existing hooks: append, don't clobber — v1 vault-hook precedent).
- `lich guardian fix` — **RESOLVED (2026-07-10, D19): conservative scope.** Deterministic fixes only: import rewrites (adapters→ports where unambiguous) + formatting. Logic violations are REPORT-ONLY with suggested fixes; AI-assisted fixes happen exclusively via the TUI with explicit user approval — `guardian fix` never invokes AI.

### Task 3.8: First plugin `lich-plugin-auth` (spec 3.7) + plugin docs

Dogfood: package the template's auth scaffold as the first real plugin; write `docs/wiki/plugins.md` (authoring guide: manifest reference, entry point, scaffold vs runtime decision table from D4). Acceptance: `lich plugin add ./plugins/lich-plugin-auth` on a fresh generated project yields working login endpoints.

### Task 3.9: Phase 3 completion — suite green, spec Phase 3 acceptance checklist, CHANGELOG, bump, commit.

---

## Phase 4: Deploy + Marketplace (detailed-task level — refinement pass required)

### Task 4.1: Zenith deploy adapter

**Files:** `cli/src/lich/deploy/zenith.py`, `cli/src/lich/commands/deploy.py` (add `lich deploy zenith`), tests.

Spec §13 flow as discrete, individually-testable steps: `check_cli()` (zenith binary on PATH) → `login()` (interactive passthrough) → `build()` (docker build, list argv) → `push()` → `deploy()` → `health()` (poll returned URL `/api/health`, timeout 120s). Each step returns `StepOutcome(ok, detail)`; command renders a Rich progress checklist. All subprocess via `asyncio.create_subprocess_exec`. Tests: mocked subprocess per step, failure at each step surfaces the right message.

**VERIFIED 2026-07-10 against /Users/babak/codes/DoTech/Zenith — Zenith is READY, and has MORE than assumed:** the CLI binary is `zen` (not `zenith`): `zen deploy --image <registry>/<image>:<tag> [--name] [--env staging|production] [--replicas N]`, plus `zen apply -f manifest.yaml`. There is also a full REST API the adapter may use directly instead of shelling out: `POST /api/v1/deploy` (body: app, image, environment, replicas → returns deployment_id, url), `GET /api/v1/deployments/{id}` (status polling), `PUT /api/v1/apps/{appId}/env`, `POST /api/v1/apps/{appId}/rollback`. Auth: Bearer JWT for users, deploy tokens `znt_id_xxx:znt_sk_xxx` for CI/CD (CLI stores token after `zen login`). Sources: Zenith/cli/cmd/deploy/deploy.go, cli/internal/api/client.go, services/api/internal/handlers/deploy.go. **Prefer the REST API path for the adapter** (no binary dependency); keep `zen` CLI passthrough for login only. [RE-VERIFY endpoint shapes at execution time]

### Task 4.2: FairBroker deploy adapter

**Files:** `cli/src/lich/deploy/fairbroker.py`, tests.

Same step pattern: `check_account()` → `provision()` → `deploy()` → URL output.

**RESOLVED 2026-07-10 (D20, verified against /Users/babak/codes/DoTech/tempVPS/fairbroker):** FairBroker has **no programmatic provisioning surface today** — provisioning runs only through internal Temporal workflows (`ProvisionVPSWorkflow`, `ProvisionContainerWorkflow` in backend/internal/workers/workflows/) triggered by user order + payment (`POST /api/orders` → `POST /api/orders/{id}/pay`); the REST API covers service *management* (start/stop/reboot/terminate), not creation, and auth is user-JWT only (no server-to-server tokens). Decision: **this task ships interface-only in v2** (`FairBrokerAdapter` protocol with `check_account/provision/deploy` raising `NotImplementedError` + a clear "coming when FairBroker exposes a provisioning API" message in the CLI). Prerequisite logged for the FairBroker backlog: expose `POST /api/v1/internal/provision` with dedicated provisioning tokens; the adapter gets implemented the release after that lands. Do NOT build an order-simulation workaround — fragile and abuses the payment flow.

### Task 4.3: Spec export/import (spec 4.5–4.6)

**Files:** `cli/src/lich/spec/exporter.py`, `importer.py`, tests.

- `lich spec export` → single `lich-spec.yaml`: entities (from memory graph — the index already knows them), features, plugins list, lich version. Deterministic, no AI.
- `lich spec import <file|url>` → drives the Phase 1 `create_app` concept with the imported spec instead of AI extraction (skips Phase-1/2 of the build loop).
- Round-trip test: export a generated project → import into empty dir → same entity set.

### Task 4.4: Marketplace client (spec §14)

`lich marketplace browse/search/fork/publish`, GitHub-based initially: a curated repo of `lich-spec.yaml` files; browse/search = GitHub API over the repo index (unauthenticated, cached); fork = download spec + `lich spec import`; publish = PR instructions (no direct write in v2).
**RESOLVED (2026-07-10, D18): interim home is the public GitHub repo `DoTech-fi/lich-specs`; YAML specs, publish-by-PR with human review; no backend service in v2 (freezenith.com website deferred to v3).**

### Task 4.5: Project insights (spec §15; moved from Phase 2 per plan scope)

**Files:** `cli/src/lich/commands/insights.py`, tests.

`lich insights` table: entity count + endpoint count (memory index / route scan reusing v1 `routes.py`), coverage % (parse `coverage.json` if present, else "run lich test --cov"), architecture compliance score (`1 - violations/checks` from Task 2.1), dead code (via `vulture` if installed — optional extra `lich[insights]`, degrade gracefully), security warnings (v1 `secret.py` scan), last deploy (`.lich/deploy.yml` state from v1). Each metric is an independent provider function returning `Metric(name, value, hint)` — testable in isolation.

### Task 4.6: Phase 4 completion — suite green, spec Phase 4 acceptance checklist, CHANGELOG, bump, commit, tag.

---

## Execution Order & Dependencies

- Phase 2 requires: Phase 1 (engine, AI provider, TUI, notes.py) and benefits from v1 Phase 3 (`_shell.py`, async MCP conventions).
- Phase 3 requires: Phase 0 (lich-core `create_app()` hooks) for runtime injection; Tasks 3.1–3.6 can run against a stub hook if Phase 0 slips (flag at refinement).
- Phase 4 requires: Phase 2 memory index (spec export) and Phase 1 concepts (spec import). Zenith/FairBroker adapters are independent of Phase 3.

## Open Questions (for the Opus double-check pass)

1. ~~FairBroker provisioning contract (Task 4.2)~~ — **RESOLVED 2026-07-10 (D20): no provisioning API exists in FairBroker today (verified in codebase); adapter ships interface-only in v2, implementation gated on FairBroker exposing `POST /api/v1/internal/provision`. Zenith verified READY (REST API preferred over `zen` CLI). Details in Task 4.1/4.2.**
2. ~~Marketplace interim home (Task 4.4)~~ — **RESOLVED 2026-07-10 (D18): `DoTech-fi/lich-specs` GitHub repo, publish-by-PR.**
3. ~~v2 version scheme (Task 2.7)~~ — **RESOLVED 2026-07-10 (D17): lich CLI `2.0.0-alpha.N`; lich-core `0.1.0` → `1.0.0` at GA.**
4. ~~Guardian `fix` scope (Task 3.7)~~ — **RESOLVED 2026-07-10 (D19): imports + formatting only; logic report-only; AI fixes only via TUI approval.**

## Spec coverage self-check (for the reviewer)

| Spec item | Task |
|---|---|
| §9 self-validating generation | 2.1, 2.2 |
| §10 continuous mode + diffs | 2.5 |
| §16/2.11–2.14 memory index, assembler, session notes | 2.3, 2.4, 2.6 (TUI memory screen deferred into 2.5's TUI work — P2 in spec) |
| §11 plugin system 3.1–3.10 | 3.1–3.6, 3.8 (3.8 covers first plugin; second plugin `notifications` P2 — deliberately dropped, log at execution) |
| §12 guardian | 3.7 |
| §13 Zenith/FairBroker | 4.1, 4.2 |
| §14 marketplace | 4.4 |
| §15 insights | 4.5 |
| spec export/import 4.5–4.6 | 4.3 |
