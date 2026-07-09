# Lich v2 Phase 1b: TUI + Concept Engine + Memory Write Path — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **DRAFT (2026-07-10, written pre-v1-hardening):** Greenfield tasks are executable as-is. Tasks marked **[RE-VERIFY]** touch files v1 hardening will change — re-read before executing. Double-check pass planned with Opus.

**Goal:** Add the v2 TUI (Textual), Concept Engine (YAML workflows), and knowledge-graph memory write path (`.lich/memory/` Obsidian-compatible vault) to the Lich CLI.

**Architecture:** Three new packages under `cli/src/lich/`: `memory/` (notes, index, writer — pure stdlib+pyyaml), `concepts/` (loader/executor/registry — Jarvis pattern), `tui/` (builder = backend brain with zero Textual imports, Jarvis advisor.py pattern; Textual app + screens on top). CLI gains `lich tui` and `lich memory` commands.

**Tech Stack:** Python 3.10+, Typer, Textual >=0.50, pyyaml, pytest + pytest-asyncio. AI provider comes from Phase 1a (`lich/ai/provider.py`); this plan duck-types it and degrades gracefully without AI.

**Dependency:** Phase 1a plan (AI adapter). If not yet merged, everything here still works — AI paths return a "no AI configured" result (spec: graceful degradation).

---

## Task 1: `memory/notes.py` — note model, parse/write, wikilinks

**Files:**
- Create: `cli/src/lich/memory/__init__.py`
- Create: `cli/src/lich/memory/notes.py`
- Test: `cli/tests/test_memory_notes.py`

- [ ] **Step 1: Write the failing tests**

```python
# cli/tests/test_memory_notes.py
"""Tests for memory note model: frontmatter parse/write, wikilinks."""
from pathlib import Path

import pytest

from lich.memory.notes import Note, parse_wikilinks, read_note, write_note


SAMPLE = """---
type: entity
name: Product
created: 2026-07-10
fields: [name, price, status]
relations: [seller, tags]
---

# Product

Belongs to [[User]] via `seller`, tagged via [[Tag]] (m2m).
See [[decision-positive-prices]].
"""


def test_parse_wikilinks_finds_all_targets():
    assert parse_wikilinks(SAMPLE) == ["User", "Tag", "decision-positive-prices"]


def test_parse_wikilinks_ignores_alias_and_heading_parts():
    body = "See [[User|the user]] and [[Product#Invariants]]."
    assert parse_wikilinks(body) == ["User", "Product"]


def test_read_note_parses_frontmatter_and_body(tmp_path: Path):
    p = tmp_path / "Product.md"
    p.write_text(SAMPLE)
    note = read_note(p)
    assert note.name == "Product"
    assert note.type == "entity"
    assert note.meta["fields"] == ["name", "price", "status"]
    assert "# Product" in note.body
    assert note.links == ["User", "Tag", "decision-positive-prices"]


def test_write_note_roundtrips(tmp_path: Path):
    note = Note(
        name="Order",
        type="entity",
        body="# Order\n\nPlaced by [[User]].",
        meta={"created": "2026-07-10", "fields": ["total"]},
    )
    path = write_note(note, tmp_path)
    assert path == tmp_path / "Order.md"
    back = read_note(path)
    assert back.name == "Order"
    assert back.type == "entity"
    assert back.meta["fields"] == ["total"]
    assert back.links == ["User"]


def test_read_note_without_frontmatter_raises(tmp_path: Path):
    p = tmp_path / "bad.md"
    p.write_text("no frontmatter here")
    with pytest.raises(ValueError, match="frontmatter"):
        read_note(p)


def test_note_type_must_be_known():
    with pytest.raises(ValueError, match="type"):
        Note(name="X", type="banana", body="", meta={})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_memory_notes.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'lich.memory'`

- [ ] **Step 3: Implement**

```python
# cli/src/lich/memory/__init__.py
"""Knowledge-graph memory: Obsidian-compatible markdown vault under .lich/memory/."""
```

```python
# cli/src/lich/memory/notes.py
"""
Note model for .lich/memory/ — plain markdown with YAML frontmatter + [[wikilinks]].

A note file looks like:

    ---
    type: entity
    name: Product
    created: 2026-07-10
    ---

    # Product
    Body markdown with [[wikilinks]].
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

NOTE_TYPES = ("entity", "decision", "gotcha", "session")

# [[Target]], [[Target|alias]], [[Target#heading]] -> "Target"
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)


def parse_wikilinks(text: str) -> list[str]:
    """Extract wikilink targets in order of first appearance, deduplicated."""
    seen: list[str] = []
    for m in WIKILINK_RE.finditer(text):
        target = m.group(1).strip()
        if target and target not in seen:
            seen.append(target)
    return seen


@dataclass
class Note:
    """One memory note. `meta` holds frontmatter keys other than type/name."""

    name: str
    type: str
    body: str
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.type not in NOTE_TYPES:
            raise ValueError(f"Unknown note type '{self.type}' (expected one of {NOTE_TYPES})")

    @property
    def links(self) -> list[str]:
        return parse_wikilinks(self.body)

    @property
    def filename(self) -> str:
        return f"{self.name}.md"


def read_note(path: Path) -> Note:
    """Parse a note file. Raises ValueError on missing/invalid frontmatter."""
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: missing YAML frontmatter block")
    fm = yaml.safe_load(m.group(1)) or {}
    if not isinstance(fm, dict) or "type" not in fm or "name" not in fm:
        raise ValueError(f"{path}: frontmatter must contain 'type' and 'name'")
    note_type = fm.pop("type")
    name = fm.pop("name")
    return Note(name=str(name), type=str(note_type), body=m.group(2), meta=fm)


def write_note(note: Note, directory: Path) -> Path:
    """Write a note as markdown with frontmatter. Returns the file path."""
    directory.mkdir(parents=True, exist_ok=True)
    fm = {"type": note.type, "name": note.name, **note.meta}
    frontmatter = yaml.safe_dump(fm, default_flow_style=None, sort_keys=False).strip()
    path = directory / note.filename
    path.write_text(f"---\n{frontmatter}\n---\n\n{note.body.lstrip()}\n" if note.body.strip()
                    else f"---\n{frontmatter}\n---\n", encoding="utf-8")
    return path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_memory_notes.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/memory/ cli/tests/test_memory_notes.py
git commit -m "feat(memory): note model with frontmatter and wikilink parsing"
```

---

## Task 2: `memory/index.py` — link graph index (.index.json)

**Files:**
- Create: `cli/src/lich/memory/index.py`
- Test: `cli/tests/test_memory_index.py`

- [ ] **Step 1: Write the failing tests**

```python
# cli/tests/test_memory_index.py
"""Tests for the memory link-graph index."""
import json
from pathlib import Path

from lich.memory.index import MemoryIndex
from lich.memory.notes import Note, write_note


def make_vault(root: Path) -> Path:
    vault = root / ".lich" / "memory"
    write_note(Note("Product", "entity", "Belongs to [[User]] and [[Tag]].",
                    {"created": "2026-07-10"}), vault)
    write_note(Note("User", "entity", "Has many [[Product]].",
                    {"created": "2026-07-10"}), vault)
    write_note(Note("decision-positive-prices", "decision",
                    "Applies to [[Product]].", {"created": "2026-07-10"}), vault)
    return vault


def test_build_collects_nodes_and_edges(tmp_path: Path):
    vault = make_vault(tmp_path)
    idx = MemoryIndex(vault)
    idx.rebuild()
    assert set(idx.nodes) == {"Product", "User", "decision-positive-prices"}
    assert ("Product", "User") in idx.edges
    assert ("decision-positive-prices", "Product") in idx.edges


def test_rebuild_persists_index_json(tmp_path: Path):
    vault = make_vault(tmp_path)
    MemoryIndex(vault).rebuild()
    data = json.loads((vault / ".index.json").read_text())
    assert data["nodes"]["Product"]["type"] == "entity"
    assert ["Product", "User"] in data["edges"]


def test_load_reads_persisted_index(tmp_path: Path):
    vault = make_vault(tmp_path)
    MemoryIndex(vault).rebuild()
    idx2 = MemoryIndex(vault)
    idx2.load()
    assert "User" in idx2.nodes


def test_update_note_refreshes_single_node(tmp_path: Path):
    vault = make_vault(tmp_path)
    idx = MemoryIndex(vault)
    idx.rebuild()
    write_note(Note("Product", "entity", "Now links only [[Tag]].",
                    {"created": "2026-07-10"}), vault)
    idx.update_note("Product")
    assert ("Product", "User") not in idx.edges
    assert ("Product", "Tag") in idx.edges


def test_neighbors_returns_outgoing_and_incoming(tmp_path: Path):
    vault = make_vault(tmp_path)
    idx = MemoryIndex(vault)
    idx.rebuild()
    # Product -> User, Tag(out); decision -> Product (in)
    assert idx.neighbors("Product") == {"User", "Tag", "decision-positive-prices"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_memory_index.py -v`
Expected: FAIL — `ModuleNotFoundError` / `ImportError: cannot import name 'MemoryIndex'`

- [ ] **Step 3: Implement**

```python
# cli/src/lich/memory/index.py
"""
Link-graph index over .lich/memory/ — persisted at .lich/memory/.index.json.

Graph model: nodes = notes (by name), edges = wikilinks (source -> target).
Edges may point at names with no note file yet ("ghost" targets) — that is
valid Obsidian behavior and marks a note worth writing later.
"""
from __future__ import annotations

import json
from pathlib import Path

from lich.memory.notes import read_note

INDEX_FILENAME = ".index.json"


class MemoryIndex:
    """Incremental index of notes and their wikilink edges."""

    def __init__(self, vault_dir: Path):
        self.vault_dir = Path(vault_dir)
        self.nodes: dict[str, dict] = {}
        self.edges: list[tuple[str, str]] = []

    @property
    def path(self) -> Path:
        return self.vault_dir / INDEX_FILENAME

    def rebuild(self) -> None:
        """Full rebuild from all *.md files in the vault, then persist."""
        self.nodes = {}
        self.edges = []
        if self.vault_dir.exists():
            for md in sorted(self.vault_dir.glob("*.md")):
                self._index_file(md)
        self.save()

    def update_note(self, name: str) -> None:
        """Re-index a single note (after a write), then persist."""
        self.edges = [(s, d) for s, d in self.edges if s != name]
        self.nodes.pop(name, None)
        md = self.vault_dir / f"{name}.md"
        if md.exists():
            self._index_file(md)
        self.save()

    def _index_file(self, md: Path) -> None:
        try:
            note = read_note(md)
        except ValueError:
            return  # skip malformed files; validate_vault reports them
        self.nodes[note.name] = {"type": note.type, "path": md.name, "links": note.links}
        for target in note.links:
            self.edges.append((note.name, target))

    def neighbors(self, name: str) -> set[str]:
        """All nodes one hop away (outgoing + incoming edges)."""
        out = {d for s, d in self.edges if s == name}
        inc = {s for s, d in self.edges if d == name}
        return out | inc

    def save(self) -> None:
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        data = {"nodes": self.nodes, "edges": [list(e) for e in self.edges]}
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.nodes = data["nodes"]
        self.edges = [tuple(e) for e in data["edges"]]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_memory_index.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/memory/index.py cli/tests/test_memory_index.py
git commit -m "feat(memory): link-graph index with incremental update"
```

---

## Task 3: `memory/writer.py` — write path (entity notes, decisions, session skeleton)

**Files:**
- Create: `cli/src/lich/memory/writer.py`
- Test: `cli/tests/test_memory_writer.py`

- [ ] **Step 1: Write the failing tests**

```python
# cli/tests/test_memory_writer.py
"""Tests for the memory write path."""
from pathlib import Path

from lich.memory.notes import read_note
from lich.memory.writer import MemoryWriter


def test_upsert_entity_note_creates_note_with_relations_as_wikilinks(tmp_path: Path):
    w = MemoryWriter(project_root=tmp_path)
    path = w.upsert_entity_note(
        "Product",
        fields=[("name", "str"), ("price", "money")],
        relations=[("seller", "fk", "User"), ("tags", "m2m", "Tag")],
    )
    note = read_note(path)
    assert note.type == "entity"
    assert note.meta["fields"] == ["name", "price"]
    assert note.meta["relations"] == ["seller", "tags"]
    assert "[[User]]" in note.body and "[[Tag]]" in note.body
    assert "| price | money |" in note.body


def test_upsert_entity_note_overwrites_generated_section_only(tmp_path: Path):
    w = MemoryWriter(project_root=tmp_path)
    path = w.upsert_entity_note("Product", fields=[("name", "str")], relations=[])
    # Simulate a human adding notes below the generated section
    text = path.read_text() + "\n## Gotchas\n- hand-written note\n"
    path.write_text(text)
    w.upsert_entity_note("Product", fields=[("name", "str"), ("sku", "str")], relations=[])
    updated = path.read_text()
    assert "| sku | str |" in updated              # regenerated
    assert "- hand-written note" in updated        # preserved


def test_add_decision_creates_slugged_adr_note(tmp_path: Path):
    w = MemoryWriter(project_root=tmp_path)
    path = w.add_decision("Prices must be positive")
    note = read_note(path)
    assert note.type == "decision"
    assert note.name == "decision-prices-must-be-positive"
    assert "Prices must be positive" in note.body


def test_start_session_note_skeleton(tmp_path: Path):
    w = MemoryWriter(project_root=tmp_path)
    path = w.write_session_note(summary="Generated Product entity", changes=["Product"])
    note = read_note(path)
    assert note.type == "session"
    assert "[[Product]]" in note.body


def test_writer_updates_index_on_write(tmp_path: Path):
    w = MemoryWriter(project_root=tmp_path)
    w.upsert_entity_note("Product", fields=[("name", "str")],
                         relations=[("seller", "fk", "User")])
    assert (tmp_path / ".lich" / "memory" / ".index.json").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_memory_writer.py -v`
Expected: FAIL — `ImportError: cannot import name 'MemoryWriter'`

- [ ] **Step 3: Implement**

```python
# cli/src/lich/memory/writer.py
"""
Memory write path: entity notes after generation, ADR decisions, session notes.

Entity notes have a generated section (between GEN_START/GEN_END markers) that
lich owns and rewrites, and a free section below that humans/AI own.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from lich.memory.index import MemoryIndex
from lich.memory.notes import Note, read_note, write_note

GEN_START = "<!-- lich:generated -->"
GEN_END = "<!-- lich:end-generated -->"

VAULT_SUBDIR = Path(".lich") / "memory"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60]


class MemoryWriter:
    """Creates and updates notes in <project_root>/.lich/memory/."""

    def __init__(self, project_root: Path):
        self.vault_dir = Path(project_root) / VAULT_SUBDIR
        self.index = MemoryIndex(self.vault_dir)

    def upsert_entity_note(
        self,
        name: str,
        fields: list[tuple[str, str]],
        relations: list[tuple[str, str, str]],  # (field, kind, target_entity)
    ) -> Path:
        """Create or update an entity note; regenerate only the generated section."""
        field_rows = "\n".join(f"| {fname} | {ftype} |" for fname, ftype in fields)
        rel_lines = "\n".join(
            f"- `{fname}`: {kind} -> [[{target}]]" for fname, kind, target in relations
        ) or "_none_"
        generated = (
            f"{GEN_START}\n"
            f"## Fields\n| Field | Type |\n|---|---|\n{field_rows}\n\n"
            f"## Relations\n{rel_lines}\n"
            f"{GEN_END}"
        )

        path = self.vault_dir / f"{name}.md"
        if path.exists():
            old = read_note(path)
            if GEN_START in old.body and GEN_END in old.body:
                pattern = re.escape(GEN_START) + r".*?" + re.escape(GEN_END)
                body = re.sub(pattern, generated, old.body, flags=re.DOTALL)
            else:
                body = f"{old.body.rstrip()}\n\n{generated}\n"
            free_meta = {k: v for k, v in old.meta.items() if k not in ("fields", "relations")}
        else:
            body = f"# {name}\n\n{generated}\n"
            free_meta = {"created": date.today().isoformat()}

        meta = {
            **free_meta,
            "fields": [f for f, _ in fields],
            "relations": [f for f, _, _ in relations],
        }
        result = write_note(Note(name=name, type="entity", body=body, meta=meta),
                            self.vault_dir)
        self._refresh_index(name)
        return result

    def add_decision(self, text: str) -> Path:
        """ADR-style decision note named decision-<slug>."""
        name = f"decision-{_slugify(text)}"
        body = (
            f"# {text}\n\n"
            f"## Context\n_(fill in)_\n\n"
            f"## Decision\n{text}\n\n"
            f"## Consequences\n_(fill in)_\n"
        )
        path = write_note(
            Note(name=name, type="decision", body=body,
                 meta={"created": date.today().isoformat()}),
            self.vault_dir,
        )
        self._refresh_index(name)
        return path

    def write_session_note(self, summary: str, changes: list[str]) -> Path:
        """Session note skeleton — full summaries land in v2 Phase 2."""
        stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        name = f"session-{stamp}"
        changed = "\n".join(f"- [[{c}]]" for c in changes) or "_none_"
        body = f"# Session {stamp}\n\n## Summary\n{summary}\n\n## Changed\n{changed}\n"
        path = write_note(
            Note(name=name, type="session", body=body,
                 meta={"created": date.today().isoformat()}),
            self.vault_dir,
        )
        self._refresh_index(name)
        return path

    def _refresh_index(self, name: str) -> None:
        if self.index.path.exists():
            self.index.load()
            self.index.update_note(name)
        else:
            self.index.rebuild()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_memory_writer.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/memory/writer.py cli/tests/test_memory_writer.py
git commit -m "feat(memory): write path — entity notes, decisions, session skeleton"
```

---

## Task 4: `lich memory` CLI subcommands **[RE-VERIFY cli.py — v1 Phase 3 may refactor command registration]**

**Files:**
- Create: `cli/src/lich/commands/memory.py`
- Modify: `cli/src/lich/cli.py` (add import + `app.add_typer(memory_app, name="memory")`)
- Test: `cli/tests/test_memory_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
# cli/tests/test_memory_cli.py
"""Tests for `lich memory` subcommands."""
from pathlib import Path

from typer.testing import CliRunner

from lich.cli import app
from lich.commands.memory import _vault_dir
from lich.memory.notes import Note, write_note

runner = CliRunner()


def _seed_vault(project: Path) -> None:
    write_note(Note("Product", "entity", "Links [[User]]. Marketplace listing.",
                    {"created": "2026-07-10"}), _vault_dir(project))


def test_memory_show_prints_note(in_lich_project: Path):
    _seed_vault(in_lich_project)
    result = runner.invoke(app, ["memory", "show", "Product"])
    assert result.exit_code == 0
    assert "Marketplace listing" in result.output


def test_memory_show_missing_note_fails(in_lich_project: Path):
    result = runner.invoke(app, ["memory", "show", "Nope"])
    assert result.exit_code == 1


def test_memory_search_matches_body_text(in_lich_project: Path):
    _seed_vault(in_lich_project)
    result = runner.invoke(app, ["memory", "search", "marketplace"])
    assert result.exit_code == 0
    assert "Product" in result.output


def test_memory_decide_creates_decision_note(in_lich_project: Path):
    result = runner.invoke(app, ["memory", "decide", "Use UUID primary keys"])
    assert result.exit_code == 0
    note = _vault_dir(in_lich_project) / "decision-use-uuid-primary-keys.md"
    assert note.exists()


def test_memory_rebuild_index(in_lich_project: Path):
    _seed_vault(in_lich_project)
    result = runner.invoke(app, ["memory", "rebuild-index"])
    assert result.exit_code == 0
    assert (_vault_dir(in_lich_project) / ".index.json").exists()


def test_memory_outside_project_fails(temp_dir: Path, monkeypatch):
    monkeypatch.chdir(temp_dir)
    result = runner.invoke(app, ["memory", "show", "Product"])
    assert result.exit_code == 1
```

**Layout decision (read before coding):** `in_lich_project` / `temp_dir` fixtures already exist in `cli/tests/conftest.py`. Today's `.lich` marker is a FILE, which blocks creating the spec's `.lich/memory/` DIRECTORY. Resolution: the `_vault_dir(root)` helper (implemented in Step 3) returns `.lich/memory/` when `.lich` is a directory (v2 layout, where `.lich/rules/` also lives) and falls back to `.lich-memory/` for legacy file-marker projects. Do NOT modify shared conftest fixtures — other tests depend on the file marker; the tests above use `_vault_dir` so they pass under either layout (with the fixture's file marker they exercise the fallback path).

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_memory_cli.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'lich.commands.memory'`

- [ ] **Step 3: Implement the command module**

```python
# cli/src/lich/commands/memory.py
"""
`lich memory` — inspect and update the project knowledge vault (.lich/memory/).
"""
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from lich.memory.index import MemoryIndex
from lich.memory.notes import read_note
from lich.memory.writer import MemoryWriter

memory_app = typer.Typer(help="Project knowledge-graph memory (Obsidian-compatible)")
console = Console()


def _check_lich_project() -> Path:
    """Must run inside a Lich project. [RE-VERIFY: v1 Phase 3 moves this to commands/common.py — import from there if it exists.]"""
    root = Path.cwd()
    if not (root / ".lich").exists():
        console.print("[red]❌ Not a Lich project (no .lich marker found)[/red]")
        raise typer.Exit(1)
    return root


def _vault_dir(root: Path) -> Path:
    """Vault location: .lich/memory/ when .lich is a directory; legacy file marker -> .lich-memory/."""
    marker = root / ".lich"
    if marker.is_dir():
        return marker / "memory"
    return root / ".lich-memory"


class _ProjectMemoryWriter(MemoryWriter):
    """MemoryWriter bound to the resolved vault dir (handles legacy layout)."""

    def __init__(self, root: Path):
        super().__init__(project_root=root)
        self.vault_dir = _vault_dir(root)
        self.index = MemoryIndex(self.vault_dir)


@memory_app.command("show")
def memory_show(name: str = typer.Argument(..., help="Note name (without .md)")):
    """Render a note to the terminal."""
    root = _check_lich_project()
    path = _vault_dir(root) / f"{name}.md"
    if not path.exists():
        console.print(f"[red]❌ Note '{name}' not found in {path.parent}[/red]")
        raise typer.Exit(1)
    note = read_note(path)
    console.print(f"[dim]type: {note.type}  links: {', '.join(note.links) or '-'}[/dim]")
    console.print(Markdown(note.body))


@memory_app.command("search")
def memory_search(term: str = typer.Argument(..., help="Case-insensitive text match")):
    """List notes whose name, frontmatter, or body matches the term."""
    root = _check_lich_project()
    vault = _vault_dir(root)
    hits = []
    if vault.exists():
        needle = term.lower()
        for md in sorted(vault.glob("*.md")):
            if needle in md.stem.lower() or needle in md.read_text(encoding="utf-8").lower():
                hits.append(md.stem)
    if not hits:
        console.print(f"[yellow]No notes match '{term}'[/yellow]")
        raise typer.Exit(0)
    for h in hits:
        console.print(f"• {h}")


@memory_app.command("decide")
def memory_decide(text: str = typer.Argument(..., help="Decision statement")):
    """Record an ADR-style decision note."""
    root = _check_lich_project()
    path = _ProjectMemoryWriter(root).add_decision(text)
    console.print(f"[green]✅ Decision recorded: {path.name}[/green]")


@memory_app.command("rebuild-index")
def memory_rebuild_index():
    """Rebuild .index.json from all notes."""
    root = _check_lich_project()
    idx = MemoryIndex(_vault_dir(root))
    idx.rebuild()
    console.print(f"[green]✅ Indexed {len(idx.nodes)} notes, {len(idx.edges)} links[/green]")
```

- [ ] **Step 4: Wire into cli.py** **[RE-VERIFY exact import block — v1 phases touch cli.py]**

In `cli/src/lich/cli.py`, add to the existing sub-app imports:

```python
from lich.commands.memory import memory_app
```

and with the other `add_typer` lines:

```python
app.add_typer(memory_app, name="memory")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_memory_cli.py -v`
Expected: 6 passed

- [ ] **Step 6: Run the full suite (no regressions)**

Run: `cd cli && python3 -m pytest -q`
Expected: all green (plus any pre-existing known failures — count must not grow)

- [ ] **Step 7: Commit**

```bash
git add cli/src/lich/commands/memory.py cli/src/lich/cli.py cli/tests/test_memory_cli.py
git commit -m "feat(memory): lich memory CLI — show, search, decide, rebuild-index"
```

---

## Task 5: Obsidian compatibility validator

**Files:**
- Create: `cli/src/lich/memory/validate.py`
- Test: `cli/tests/test_memory_validate.py`

- [ ] **Step 1: Write the failing tests**

```python
# cli/tests/test_memory_validate.py
"""Vault must open cleanly in Obsidian: valid YAML frontmatter, resolvable links."""
from pathlib import Path

from lich.memory.notes import Note, write_note
from lich.memory.validate import validate_vault


def test_valid_vault_reports_no_errors(tmp_path: Path):
    write_note(Note("User", "entity", "See [[Product]].", {"created": "2026-07-10"}), tmp_path)
    write_note(Note("Product", "entity", "By [[User]].", {"created": "2026-07-10"}), tmp_path)
    report = validate_vault(tmp_path)
    assert report.errors == []
    assert report.unresolved_links == []


def test_malformed_frontmatter_is_an_error(tmp_path: Path):
    (tmp_path / "broken.md").write_text("---\n: not yaml [\n---\nbody")
    report = validate_vault(tmp_path)
    assert any("broken.md" in e for e in report.errors)


def test_unresolved_links_are_reported_not_errors(tmp_path: Path):
    write_note(Note("User", "entity", "See [[Ghost]].", {"created": "2026-07-10"}), tmp_path)
    report = validate_vault(tmp_path)
    assert report.errors == []
    assert ("User", "Ghost") in report.unresolved_links
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_memory_validate.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# cli/src/lich/memory/validate.py
"""Vault sanity: every note parses, links resolve (unresolved = warning, not error)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from lich.memory.notes import read_note


@dataclass
class VaultReport:
    errors: list[str] = field(default_factory=list)
    unresolved_links: list[tuple[str, str]] = field(default_factory=list)


def validate_vault(vault_dir: Path) -> VaultReport:
    report = VaultReport()
    notes = {}
    for md in sorted(Path(vault_dir).glob("*.md")):
        try:
            notes[md.stem] = read_note(md)
        except Exception as e:  # ValueError from read_note, yaml.YAMLError from bad YAML
            report.errors.append(f"{md.name}: {e}")
    names = set(notes)
    for name, note in notes.items():
        for target in note.links:
            if target not in names:
                report.unresolved_links.append((name, target))
    return report
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_memory_validate.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/memory/validate.py cli/tests/test_memory_validate.py
git commit -m "feat(memory): vault validator — frontmatter + link resolution"
```

---

## Task 6: `concepts/schema.py` — YAML concept model

**Files:**
- Create: `cli/src/lich/concepts/__init__.py`
- Create: `cli/src/lich/concepts/schema.py`
- Test: `cli/tests/test_concepts_schema.py`

- [ ] **Step 1: Write the failing tests**

```python
# cli/tests/test_concepts_schema.py
"""Tests for concept YAML schema."""
from pathlib import Path

import pytest

from lich.concepts.schema import ConceptYAML, OnErrorAction

MINIMAL = """
name: create_app
description: Create a new application from description
priority: 10
triggers:
  patterns:
    - "create {description}"
  keywords:
    - create
workflow:
  - id: project_config
    tool: read_project_config
    on_error: continue
  - id: ai_design
    tool: ai_extract_design
    args:
      description: "${user_input}"
    prompt_template: "extract_entities.j2"
ai_config:
  structured_output: true
"""


def test_from_file_parses_all_fields(tmp_path: Path):
    p = tmp_path / "concept.yaml"
    p.write_text(MINIMAL)
    c = ConceptYAML.from_file(p)
    assert c.name == "create_app"
    assert c.priority == 10
    assert c.triggers.keywords == ["create"]
    assert len(c.workflow) == 2
    assert c.workflow[0].on_error == OnErrorAction.CONTINUE
    assert c.workflow[1].args["description"] == "${user_input}"
    assert c.workflow[1].prompt_template == "extract_entities.j2"
    assert c.ai_config == {"structured_output": True}


def test_step_defaults(tmp_path: Path):
    p = tmp_path / "concept.yaml"
    p.write_text(MINIMAL)
    c = ConceptYAML.from_file(p)
    step = c.workflow[1]
    assert step.on_error == OnErrorAction.FAIL  # default when omitted


def test_missing_name_raises(tmp_path: Path):
    p = tmp_path / "concept.yaml"
    p.write_text("description: no name\nworkflow: []")
    with pytest.raises(ValueError, match="name"):
        ConceptYAML.from_file(p)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_concepts_schema.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# cli/src/lich/concepts/__init__.py
"""Concept Engine: YAML app-building workflows (adapted from Jarvis)."""
```

```python
# cli/src/lich/concepts/schema.py
"""Dataclasses for concept YAML files (see docs: v2 spec section 8)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml


class OnErrorAction(str, Enum):
    FAIL = "fail"
    STOP = "stop"
    SKIP = "skip"
    CONTINUE = "continue"


@dataclass
class Triggers:
    patterns: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


@dataclass
class WorkflowStep:
    id: str
    tool: str
    args: dict = field(default_factory=dict)
    on_error: OnErrorAction = OnErrorAction.FAIL
    prompt_template: str | None = None
    description: str | None = None


@dataclass
class ConceptYAML:
    name: str
    description: str
    workflow: list[WorkflowStep]
    priority: int = 5
    triggers: Triggers = field(default_factory=Triggers)
    ai_config: dict = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path | str) -> "ConceptYAML":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        if not data.get("name"):
            raise ValueError(f"{path}: concept must have a 'name'")
        trig = data.get("triggers") or {}
        steps = [
            WorkflowStep(
                id=s["id"],
                tool=s["tool"],
                args=s.get("args") or {},
                on_error=OnErrorAction(s.get("on_error", "fail")),
                prompt_template=s.get("prompt_template"),
                description=s.get("description"),
            )
            for s in (data.get("workflow") or [])
        ]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            workflow=steps,
            priority=int(data.get("priority", 5)),
            triggers=Triggers(
                patterns=list(trig.get("patterns") or []),
                keywords=list(trig.get("keywords") or []),
            ),
            ai_config=data.get("ai_config") or {},
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_concepts_schema.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/concepts/ cli/tests/test_concepts_schema.py
git commit -m "feat(concepts): YAML concept schema"
```

---

## Task 7: `concepts/loader.py` + the `create_app` concept fixture

**Files:**
- Create: `cli/src/lich/concepts/loader.py`
- Create: `cli/src/lich/concepts/library/create_app/concept.yaml`
- Test: `cli/tests/test_concepts_loader.py`

- [ ] **Step 1: Create the concept YAML (spec section 8 example, verbatim)**

```yaml
# cli/src/lich/concepts/library/create_app/concept.yaml
name: create_app
description: Create a new application from description
priority: 10

triggers:
  patterns:
    - "create {description}"
    - "build {description}"
    - "I want {description}"
  keywords:
    - create
    - build
    - new app

workflow:
  - id: project_config
    tool: read_project_config
    on_error: continue
  - id: existing_entities
    tool: read_existing_entities
    on_error: continue
  - id: architecture_rules
    tool: read_architecture_rules
    on_error: continue
  - id: ai_design
    tool: ai_extract_design
    args:
      description: "${user_input}"
      context:
        project: "${project_config}"
        entities: "${existing_entities}"
        rules: "${architecture_rules}"
    prompt_template: "extract_entities.j2"

ai_config:
  structured_output: true
```

- [ ] **Step 2: Write the failing tests**

```python
# cli/tests/test_concepts_loader.py
"""Tests for concept loading and matching."""
from pathlib import Path

from lich.concepts.loader import ConceptLoader

LIBRARY = Path(__file__).parent.parent / "src" / "lich" / "concepts" / "library"


def test_load_all_finds_create_app():
    loader = ConceptLoader(LIBRARY)
    loader.load_all()
    names = [c.name for c in loader.list_concepts()]
    assert "create_app" in names


def test_get_concept_returns_full_workflow():
    loader = ConceptLoader(LIBRARY)
    loader.load_all()
    c = loader.get_concept("create_app")
    assert c is not None
    assert [s.id for s in c.workflow] == [
        "project_config", "existing_entities", "architecture_rules", "ai_design"
    ]


def test_find_match_scores_keyword_query():
    loader = ConceptLoader(LIBRARY)
    loader.load_all()
    concept, score = loader.find_match("create a marketplace app")
    assert concept is not None and concept.name == "create_app"
    assert score >= 0.4


def test_find_match_below_threshold_returns_none():
    loader = ConceptLoader(LIBRARY)
    loader.load_all()
    concept, score = loader.find_match("completely unrelated words zzz")
    assert concept is None and score == 0.0


def test_dirs_starting_with_underscore_are_skipped(tmp_path: Path):
    d = tmp_path / "_template"
    d.mkdir()
    (d / "concept.yaml").write_text("name: nope\ndescription: x\nworkflow: []")
    loader = ConceptLoader(tmp_path)
    loader.load_all()
    assert loader.list_concepts() == []
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_concepts_loader.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'lich.concepts.loader'`

- [ ] **Step 4: Implement (Jarvis pattern, trimmed to what Lich needs now)**

```python
# cli/src/lich/concepts/loader.py
"""
Loads concepts from library/<name>/concept.yaml (Jarvis progressive-disclosure pattern:
lightweight metadata for matching, full workflow on demand).
"""
from __future__ import annotations

import re
from pathlib import Path

from lich.concepts.schema import ConceptYAML


class ConceptLoader:
    def __init__(self, concepts_dir: Path | str):
        self.concepts_dir = Path(concepts_dir)
        self._concepts: dict[str, ConceptYAML] = {}
        self._metadata: dict[str, dict] = {}

    def load_all(self) -> None:
        if not self.concepts_dir.exists():
            return
        for concept_dir in sorted(self.concepts_dir.iterdir()):
            if not concept_dir.is_dir() or concept_dir.name.startswith("_"):
                continue
            yaml_path = concept_dir / "concept.yaml"
            if yaml_path.exists():
                try:
                    c = ConceptYAML.from_file(yaml_path)
                except ValueError:
                    continue
                self._concepts[c.name] = c
                self._metadata[c.name] = {
                    "keywords": c.triggers.keywords,
                    "patterns": c.triggers.patterns,
                    "description": c.description,
                    "priority": c.priority,
                }

    def list_concepts(self) -> list[ConceptYAML]:
        return list(self._concepts.values())

    def get_concept(self, name: str) -> ConceptYAML | None:
        return self._concepts.get(name)

    def find_match(self, query: str) -> tuple[ConceptYAML | None, float]:
        """Best concept for a query, or (None, 0.0) under the 0.4 threshold."""
        q = query.lower()
        best, best_score = None, 0.0
        for name, meta in self._metadata.items():
            score = self._score(q, meta)
            score *= 0.8 + (meta["priority"] / 10.0) * 0.2
            if score > best_score:
                best, best_score = self._concepts[name], score
        if best_score < 0.4:
            return None, 0.0
        return best, best_score

    @staticmethod
    def _score(query: str, meta: dict) -> float:
        score = 0.0
        for pattern in meta["patterns"]:
            regex = re.escape(re.sub(r"\{[^}]+\}", "__V__", pattern)).replace("__V__", r".+")
            if re.search(regex, query, re.IGNORECASE):
                score += 0.6
                break
        matched = sum(1 for k in meta["keywords"] if k.lower() in query)
        if meta["keywords"]:
            score += min(0.4, 0.15 * matched)
        return min(score, 1.0)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_concepts_loader.py -v`
Expected: 5 passed

- [ ] **Step 6: Verify the YAML ships in the wheel** — add package data. In `cli/pyproject.toml`, under `[tool.setuptools]` (check the existing packaging config first with `grep -n "tool.setuptools" cli/pyproject.toml`; add if absent):

```toml
[tool.setuptools.package-data]
lich = ["concepts/library/*/concept.yaml"]
```

Run: `cd cli && python3 -c "from pathlib import Path; import lich.concepts as c; p = Path(c.__file__).parent/'library'/'create_app'/'concept.yaml'; print(p.exists())"`
Expected: `True`

- [ ] **Step 7: Commit**

```bash
git add cli/src/lich/concepts/ cli/tests/test_concepts_loader.py cli/pyproject.toml
git commit -m "feat(concepts): loader + create_app concept"
```

---

## Task 8: `concepts/executor.py` — workflow execution with `${var}` resolution

**Files:**
- Create: `cli/src/lich/concepts/executor.py`
- Test: `cli/tests/test_concepts_executor.py`

- [ ] **Step 1: Write the failing tests**

```python
# cli/tests/test_concepts_executor.py
"""Tests for concept workflow execution."""
import pytest

from lich.concepts.executor import ConceptExecutor
from lich.concepts.schema import ConceptYAML, OnErrorAction, WorkflowStep


def make_concept(steps):
    return ConceptYAML(name="t", description="test", workflow=steps)


@pytest.mark.asyncio
async def test_executes_steps_in_order_and_collects_results():
    calls = []
    registry = {
        "a": lambda: calls.append("a") or {"val": 1},
        "b": lambda: calls.append("b") or {"val": 2},
    }
    concept = make_concept([WorkflowStep("s1", "a"), WorkflowStep("s2", "b")])
    result = await ConceptExecutor(registry).execute(concept, context={})
    assert calls == ["a", "b"]
    assert result["success"] is True
    assert result["results"]["s1"] == {"val": 1}


@pytest.mark.asyncio
async def test_resolves_context_and_step_reference_args():
    registry = {
        "produce": lambda: {"out": "hello"},
        "consume": lambda x, env: {"got": x, "env": env},
    }
    concept = make_concept([
        WorkflowStep("p", "produce"),
        WorkflowStep("c", "consume", args={"x": "${p.out}", "env": "${env}"}),
    ])
    result = await ConceptExecutor(registry).execute(concept, context={"env": "dev"})
    assert result["results"]["c"] == {"got": "hello", "env": "dev"}


@pytest.mark.asyncio
async def test_async_tools_are_awaited():
    async def atool():
        return {"async": True}
    concept = make_concept([WorkflowStep("s", "atool")])
    result = await ConceptExecutor({"atool": atool}).execute(concept, context={})
    assert result["results"]["s"] == {"async": True}


@pytest.mark.asyncio
async def test_on_error_continue_keeps_going():
    def boom():
        raise RuntimeError("nope")
    registry = {"boom": boom, "ok": lambda: {"fine": 1}}
    concept = make_concept([
        WorkflowStep("s1", "boom", on_error=OnErrorAction.CONTINUE),
        WorkflowStep("s2", "ok"),
    ])
    result = await ConceptExecutor(registry).execute(concept, context={})
    assert "error" in result["results"]["s1"]
    assert result["results"]["s2"] == {"fine": 1}


@pytest.mark.asyncio
async def test_on_error_fail_stops_and_reports():
    def boom():
        raise RuntimeError("nope")
    concept = make_concept([
        WorkflowStep("s1", "boom", on_error=OnErrorAction.FAIL),
        WorkflowStep("s2", "boom"),
    ])
    result = await ConceptExecutor({"boom": boom}).execute(concept, context={})
    assert result["success"] is False
    assert "s2" not in result["results"]


@pytest.mark.asyncio
async def test_unknown_tool_is_step_error():
    concept = make_concept([WorkflowStep("s1", "missing", on_error=OnErrorAction.CONTINUE)])
    result = await ConceptExecutor({}).execute(concept, context={})
    assert "not found" in result["results"]["s1"]["error"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_concepts_executor.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# cli/src/lich/concepts/executor.py
"""
Executes concept workflows: deterministic tool steps + resolved ${var} args.
Adapted from Jarvis ConceptExecutor; response templating dropped (Lich concepts
end in structured data for the TUI, not a markdown template).
"""
from __future__ import annotations

import asyncio
from typing import Any

from lich.concepts.schema import ConceptYAML, OnErrorAction


class ConceptExecutor:
    def __init__(self, tool_registry: dict[str, Any]):
        self.tool_registry = tool_registry

    async def execute(self, concept: ConceptYAML, context: dict[str, Any]) -> dict[str, Any]:
        results: dict[str, Any] = {}
        errors: list[str] = []

        for step in concept.workflow:
            tool_fn = self.tool_registry.get(step.tool)
            if tool_fn is None:
                results[step.id] = {"error": f"Tool '{step.tool}' not found"}
                if step.on_error == OnErrorAction.FAIL:
                    return {"success": False, "results": results,
                            "errors": [results[step.id]["error"]]}
                continue

            args = self._resolve_args(step.args, context, results)
            try:
                if asyncio.iscoroutinefunction(tool_fn):
                    results[step.id] = await tool_fn(**args)
                else:
                    results[step.id] = tool_fn(**args)
            except Exception as e:  # tool errors become step errors by design
                msg = f"Step '{step.id}' failed: {e}"
                errors.append(msg)
                results[step.id] = {"error": str(e)}
                if step.on_error == OnErrorAction.FAIL:
                    return {"success": False, "results": results, "errors": errors}
                if step.on_error == OnErrorAction.STOP:
                    break
                # SKIP / CONTINUE fall through

        return {"success": not errors, "results": results,
                "errors": errors or None}

    @classmethod
    def _resolve_args(cls, args: dict, context: dict, results: dict) -> dict:
        return {k: cls._resolve_value(v, context, results) for k, v in args.items()}

    @classmethod
    def _resolve_value(cls, value: Any, context: dict, results: dict) -> Any:
        if isinstance(value, dict):
            return {k: cls._resolve_value(v, context, results) for k, v in value.items()}
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            var = value[2:-1]
            if var in context:
                return context[var]
            if "." in var:
                step_id, fld = var.split(".", 1)
                step_result = results.get(step_id)
                if isinstance(step_result, dict) and fld in step_result:
                    return step_result[fld]
            if var in results:
                return results[var]
            return value  # unresolved stays literal (matches Jarvis behavior)
        return value


__all__ = ["ConceptExecutor"]
```

Note: unlike Jarvis, nested dict args are resolved recursively (the `create_app` concept nests `context:` under `args:`). The tests for context/step resolution cover the flat case; the nested case is covered in Task 9's registry integration test.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_concepts_executor.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/concepts/executor.py cli/tests/test_concepts_executor.py
git commit -m "feat(concepts): executor with var resolution and on_error policies"
```

---

## Task 9: `concepts/registry.py` — context readers + memory reader

**Files:**
- Create: `cli/src/lich/concepts/registry.py`
- Test: `cli/tests/test_concepts_registry.py`

- [ ] **Step 1: Write the failing tests**

```python
# cli/tests/test_concepts_registry.py
"""Tests for the concept tool registry (context readers)."""
from pathlib import Path

import pytest

from lich.concepts.executor import ConceptExecutor
from lich.concepts.loader import ConceptLoader
from lich.concepts.registry import build_tool_registry
from lich.memory.notes import Note, write_note

LIBRARY = Path(__file__).parent.parent / "src" / "lich" / "concepts" / "library"


@pytest.fixture
def project_with_entities(in_lich_project: Path) -> Path:
    ent = in_lich_project / "backend" / "internal" / "entities"
    (ent / "user.py").write_text("class User:\n    pass\n")
    (ent / "product.py").write_text("class Product:\n    pass\n")
    (ent / "__init__.py").write_text("")
    return in_lich_project


def test_read_existing_entities_lists_entity_modules(project_with_entities: Path):
    registry = build_tool_registry(project_with_entities)
    result = registry["read_existing_entities"]()
    assert sorted(result["entities"]) == ["Product", "User"]


def test_read_project_config_reads_lich_marker(project_with_entities: Path):
    registry = build_tool_registry(project_with_entities)
    result = registry["read_project_config"]()
    assert result["version"] == "1.3.0"


def test_read_architecture_rules_missing_dir_is_empty(project_with_entities: Path):
    registry = build_tool_registry(project_with_entities)
    result = registry["read_architecture_rules"]()
    assert result == {"rules": []}


def test_read_memory_returns_note_bodies(project_with_entities: Path, monkeypatch):
    from lich.commands.memory import _vault_dir
    vault = _vault_dir(project_with_entities)
    write_note(Note("Product", "entity", "Marketplace listing.", {"created": "2026-07-10"}), vault)
    registry = build_tool_registry(project_with_entities)
    result = registry["read_memory"](names=["Product"])
    assert "Marketplace listing" in result["notes"]["Product"]


@pytest.mark.asyncio
async def test_create_app_concept_runs_context_steps(project_with_entities: Path):
    """End-to-end: create_app deterministic steps run; the AI step degrades gracefully."""
    loader = ConceptLoader(LIBRARY)
    loader.load_all()
    concept = loader.get_concept("create_app")
    registry = build_tool_registry(project_with_entities)  # no AI provider
    result = await ConceptExecutor(registry).execute(
        concept, context={"user_input": "create a shop"}
    )
    assert sorted(result["results"]["existing_entities"]["entities"]) == ["Product", "User"]
    assert "error" in result["results"]["ai_design"]  # no AI configured -> step error, not crash
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_concepts_registry.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# cli/src/lich/concepts/registry.py
"""
Tool registry for concept workflows: context readers over the current project,
the memory reader, and (when configured) AI tools from the Phase 1a adapter.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from lich.memory.notes import read_note

CLASS_RE = re.compile(r"^class\s+([A-Z]\w*)", re.MULTILINE)


def build_tool_registry(project_root: Path, ai_provider: object | None = None) -> dict[str, Any]:
    """
    Registry maps step tool names -> callables (spec section 8).
    ai_provider duck-types Phase 1a's AIProvider (async ask/ask_structured).
    [RE-VERIFY: once Phase 1a lands, import AIProvider for the type hint.]
    """
    root = Path(project_root)

    def read_project_config() -> dict:
        marker = root / ".lich"
        config_file = marker / "config.json" if marker.is_dir() else marker
        if config_file.exists() and config_file.is_file():
            try:
                return json.loads(config_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {"error": "invalid .lich marker"}
        return {}

    def read_existing_entities() -> dict:
        ent_dir = root / "backend" / "internal" / "entities"
        entities: list[str] = []
        if ent_dir.exists():
            for py in sorted(ent_dir.glob("*.py")):
                if py.name.startswith("_"):
                    continue
                entities.extend(CLASS_RE.findall(py.read_text(encoding="utf-8")))
        return {"entities": entities}

    def read_architecture_rules() -> dict:
        rules_dir = root / ".lich" / "rules" if (root / ".lich").is_dir() else root / "docs"
        rules: list[str] = []
        if rules_dir.exists():
            for md in sorted(rules_dir.glob("*.md")):
                rules.append(md.read_text(encoding="utf-8")[:4000])
        return {"rules": rules}

    def read_memory(names: list[str] | None = None) -> dict:
        from lich.commands.memory import _vault_dir  # late import avoids cycle
        vault = _vault_dir(root)
        notes: dict[str, str] = {}
        if vault.exists():
            targets = names or [p.stem for p in vault.glob("*.md")]
            for name in targets:
                p = vault / f"{name}.md"
                if p.exists():
                    notes[name] = read_note(p).body
        return {"notes": notes}

    async def ai_extract_design(description: str, context: dict | None = None) -> dict:
        if ai_provider is None:
            raise RuntimeError(
                "No AI provider configured — run 'lich config set ai.provider <name>' "
                "or use 'lich make entity X --fields ...' directly."
            )
        prompt = (
            "Extract entities for this app as JSON.\n"
            f"## Description\n{description}\n"
            f"## Context\n{json.dumps(context or {}, indent=2)[:8000]}\n"
        )
        raw = await ai_provider.ask(prompt)  # duck-typed Phase 1a protocol
        return {"raw": raw}

    return {
        "read_project_config": read_project_config,
        "read_existing_entities": read_existing_entities,
        "read_architecture_rules": read_architecture_rules,
        "read_memory": read_memory,
        "ai_extract_design": ai_extract_design,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_concepts_registry.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/concepts/registry.py cli/tests/test_concepts_registry.py
git commit -m "feat(concepts): tool registry — context readers, memory reader, AI hook"
```

---

## Task 10: `tui/builder.py` — backend brain (no Textual imports)

**Files:**
- Create: `cli/src/lich/tui/__init__.py`
- Create: `cli/src/lich/tui/builder.py`
- Test: `cli/tests/test_tui_builder.py`

- [ ] **Step 1: Write the failing tests**

```python
# cli/tests/test_tui_builder.py
"""Tests for the TUI backend brain. No Textual involved."""
from pathlib import Path

import pytest

from lich.tui.builder import Builder, EntitySpec


@pytest.fixture
def project(in_lich_project: Path) -> Path:
    ent = in_lich_project / "backend" / "internal" / "entities"
    (ent / "user.py").write_text("class User:\n    pass\n")
    return in_lich_project


def test_builder_has_no_textual_dependency():
    import lich.tui.builder as m
    import sys
    assert "textual" not in m.__dict__.get("__annotations__", {})
    assert not any(mod.startswith("textual") for mod in sys.modules
                   if getattr(sys.modules.get(mod), "__package__", "") == m.__package__)
    source = Path(m.__file__).read_text()
    assert "import textual" not in source and "from textual" not in source


def test_dashboard_counts_entities_and_notes(project: Path):
    b = Builder(project_root=project)
    dash = b.dashboard()
    assert dash["entities"] == ["User"]
    assert dash["note_count"] == 0
    assert dash["ai_available"] is False


@pytest.mark.asyncio
async def test_extract_entities_without_ai_returns_unavailable(project: Path):
    b = Builder(project_root=project)
    result = await b.extract_entities("a shop with products")
    assert result.ok is False
    assert "AI" in result.message


@pytest.mark.asyncio
async def test_extract_entities_parses_structured_ai_response(project: Path):
    class FakeAI:
        name = "fake"
        def is_available(self):
            return True
        async def ask_structured(self, prompt, schema):
            return {"entities": [
                {"name": "Product", "fields": [{"name": "price", "type": "money"}]},
            ]}
    b = Builder(project_root=project, ai_provider=FakeAI())
    result = await b.extract_entities("a shop")
    assert result.ok is True
    assert result.entities == [EntitySpec("Product", [("price", "money")])]


def test_generate_entity_calls_make_and_writes_memory(project: Path, monkeypatch):
    calls = []
    import lich.tui.builder as builder_mod
    monkeypatch.setattr(builder_mod, "_run_make_entity", lambda name: calls.append(name))
    b = Builder(project_root=project)
    result = b.generate_entity(EntitySpec("Product", [("price", "money")]))
    assert calls == ["Product"]
    assert result.ok is True
    from lich.commands.memory import _vault_dir
    assert (_vault_dir(project) / "Product.md").exists()


def test_memory_notes_lists_vault(project: Path):
    from lich.memory.notes import Note, write_note
    from lich.commands.memory import _vault_dir
    write_note(Note("Product", "entity", "x", {"created": "2026-07-10"}), _vault_dir(project))
    b = Builder(project_root=project)
    notes = b.memory_notes()
    assert notes == [{"name": "Product", "type": "entity"}]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_tui_builder.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'lich.tui'`

- [ ] **Step 3: Implement**

```python
# cli/src/lich/tui/__init__.py
"""Lich TUI: Textual app (app.py, screens/) on top of a Textual-free brain (builder.py)."""
```

```python
# cli/src/lich/tui/builder.py
"""
Backend brain for the TUI (Jarvis advisor.py pattern): holds project state,
orchestrates concepts / AI / codegen, returns plain data. NO Textual imports —
this module must stay import-safe for headless tests and future non-TUI frontends.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from lich.concepts.loader import ConceptLoader
from lich.concepts.registry import build_tool_registry
from lich.memory.writer import MemoryWriter
from lich.memory.index import MemoryIndex

CLASS_RE = re.compile(r"^class\s+([A-Z]\w*)", re.MULTILINE)

ENTITY_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                            },
                            "required": ["name", "type"],
                        },
                    },
                },
                "required": ["name", "fields"],
            },
        }
    },
    "required": ["entities"],
}


@dataclass(frozen=True)
class EntitySpec:
    name: str
    fields: list = field(default_factory=list)  # list[tuple[str, str]]

    def __eq__(self, other):
        return (isinstance(other, EntitySpec)
                and self.name == other.name
                and list(self.fields) == list(other.fields))


@dataclass
class ExtractResult:
    ok: bool
    message: str = ""
    entities: list = field(default_factory=list)


@dataclass
class GenerateResult:
    ok: bool
    message: str = ""


def _run_make_entity(name: str) -> None:
    """Indirection point for tests. [RE-VERIFY: v1 Phase 3 refactors make.py signatures.]"""
    from lich.commands.make import make_entity
    make_entity(name)


class Builder:
    """Executes concepts and orchestrates AI for app building (v2 spec section 6)."""

    def __init__(self, project_root: Path | None = None, ai_provider: object | None = None):
        self.root = Path(project_root) if project_root else Path.cwd()
        self.ai = ai_provider
        from lich.commands.memory import _vault_dir  # late import avoids cycle
        self.vault_dir = _vault_dir(self.root)
        self.writer = MemoryWriter(project_root=self.root)
        self.writer.vault_dir = self.vault_dir
        self.writer.index = MemoryIndex(self.vault_dir)

    # ---- state ----------------------------------------------------------

    def is_lich_project(self) -> bool:
        return (self.root / ".lich").exists()

    def list_entities(self) -> list[str]:
        ent_dir = self.root / "backend" / "internal" / "entities"
        names: list[str] = []
        if ent_dir.exists():
            for py in sorted(ent_dir.glob("*.py")):
                if not py.name.startswith("_"):
                    names.extend(CLASS_RE.findall(py.read_text(encoding="utf-8")))
        return names

    def memory_notes(self) -> list[dict]:
        from lich.memory.notes import read_note
        notes = []
        if self.vault_dir.exists():
            for md in sorted(self.vault_dir.glob("*.md")):
                try:
                    n = read_note(md)
                    notes.append({"name": n.name, "type": n.type})
                except ValueError:
                    continue
        return notes

    def dashboard(self) -> dict:
        return {
            "project": self.root.name,
            "is_lich": self.is_lich_project(),
            "entities": self.list_entities(),
            "note_count": len(self.memory_notes()),
            "ai_available": bool(self.ai and self.ai.is_available()),
        }

    # ---- AI flow --------------------------------------------------------

    async def extract_entities(self, description: str) -> ExtractResult:
        """Phase 2 of the build loop: one-shot AI extraction (graceful without AI)."""
        if not self.ai or not self.ai.is_available():
            return ExtractResult(
                ok=False,
                message="No AI provider configured. Use --fields for deterministic generation, "
                        "or run: lich config set ai.provider claude-cli",
            )
        data = await self.ai.ask_structured(
            f"Extract entities for: {description}", ENTITY_SCHEMA
        )
        entities = [
            EntitySpec(e["name"], [(f["name"], f["type"]) for f in e.get("fields", [])])
            for e in data.get("entities", [])
        ]
        return ExtractResult(ok=True, entities=entities)

    # ---- generation -----------------------------------------------------

    def generate_entity(self, spec: EntitySpec) -> GenerateResult:
        """Phase 4: deterministic generation + memory write path."""
        try:
            _run_make_entity(spec.name)
        except Exception as e:
            return GenerateResult(ok=False, message=f"Generation failed: {e}")
        self.writer.upsert_entity_note(spec.name, fields=list(spec.fields), relations=[])
        return GenerateResult(ok=True, message=f"Generated {spec.name} + memory note")

    # ---- concepts -------------------------------------------------------

    def concepts(self) -> ConceptLoader:
        loader = ConceptLoader(Path(__file__).parent.parent / "concepts" / "library")
        loader.load_all()
        return loader

    def tool_registry(self) -> dict:
        return build_tool_registry(self.root, ai_provider=self.ai)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_tui_builder.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/tui/ cli/tests/test_tui_builder.py
git commit -m "feat(tui): builder — Textual-free backend brain"
```

---

## Task 11: Textual app + screens, `lich tui` entry **[RE-VERIFY cli.py]**

**Files:**
- Modify: `cli/pyproject.toml` (add `"textual>=0.50.0"` to `dependencies`)
- Create: `cli/src/lich/tui/app.py`
- Create: `cli/src/lich/tui/screens/__init__.py`
- Create: `cli/src/lich/tui/screens/dashboard.py`
- Create: `cli/src/lich/tui/screens/new_entity.py`
- Create: `cli/src/lich/tui/screens/memory_browser.py`
- Modify: `cli/src/lich/cli.py` (register `lich tui`)
- Test: `cli/tests/test_tui_app.py`

- [ ] **Step 1: Add the dependency**

In `cli/pyproject.toml` `dependencies`, after `"mcp>=0.1.0",` add:

```toml
    "textual>=0.50.0",
```

Run: `cd cli && pip install -e ".[dev]" -q && python3 -c "import textual; print(textual.__version__)"`
Expected: a version >= 0.50

- [ ] **Step 2: Write the failing tests (Textual pilot)**

```python
# cli/tests/test_tui_app.py
"""Textual pilot tests — smoke-level: app boots, screens switch, builder wired."""
from pathlib import Path

import pytest

from lich.tui.app import LichTUI


@pytest.fixture
def project(in_lich_project: Path) -> Path:
    ent = in_lich_project / "backend" / "internal" / "entities"
    (ent / "user.py").write_text("class User:\n    pass\n")
    return in_lich_project


@pytest.mark.asyncio
async def test_app_boots_to_dashboard(project: Path):
    app = LichTUI(project_root=project)
    async with app.run_test() as pilot:
        assert app.screen.name == "dashboard"
        text = app.screen.query_one("#stats").renderable
        assert "User" in str(text)


@pytest.mark.asyncio
async def test_n_key_opens_new_entity_screen(project: Path):
    app = LichTUI(project_root=project)
    async with app.run_test() as pilot:
        await pilot.press("n")
        assert app.screen.name == "new_entity"


@pytest.mark.asyncio
async def test_m_key_opens_memory_browser(project: Path):
    app = LichTUI(project_root=project)
    async with app.run_test() as pilot:
        await pilot.press("m")
        assert app.screen.name == "memory"


@pytest.mark.asyncio
async def test_new_entity_manual_fields_generates(project: Path, monkeypatch):
    import lich.tui.builder as builder_mod
    made = []
    monkeypatch.setattr(builder_mod, "_run_make_entity", lambda name: made.append(name))
    app = LichTUI(project_root=project)
    async with app.run_test() as pilot:
        await pilot.press("n")
        app.screen.query_one("#entity-name").value = "Product"
        app.screen.query_one("#entity-fields").value = "price:money, name:str"
        await pilot.click("#generate-btn")
        await pilot.pause()
        assert made == ["Product"]
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd cli && python3 -m pytest tests/test_tui_app.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'lich.tui.app'`

- [ ] **Step 4: Implement the screens**

```python
# cli/src/lich/tui/screens/__init__.py
"""TUI screens. All business logic lives in tui/builder.py."""
```

```python
# cli/src/lich/tui/screens/dashboard.py
"""Dashboard: project stats + key bindings to other screens."""
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class DashboardScreen(Screen):
    """Entry screen: entity list, note count, AI status."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Vertical(Static(id="stats"))
        yield Footer()

    def on_mount(self) -> None:
        dash = self.app.builder.dashboard()
        entities = ", ".join(dash["entities"]) or "none yet"
        ai = "✓ available" if dash["ai_available"] else "✗ not configured (BYOA)"
        self.query_one("#stats", Static).update(
            f"[b]🧙 {dash['project']}[/b]\n\n"
            f"Entities: {entities}\n"
            f"Memory notes: {dash['note_count']}\n"
            f"AI: {ai}\n\n"
            f"[dim]n = new entity · m = memory · q = quit[/dim]"
        )
```

```python
# cli/src/lich/tui/screens/new_entity.py
"""New-entity flow: description (AI) or manual fields -> review -> generate."""
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from lich.tui.builder import EntitySpec


class NewEntityScreen(Screen):
    """Manual path works without AI (graceful degradation, spec section 7)."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Vertical(
            Static("[b]New Entity[/b] — name + fields (deterministic), "
                   "or description (AI)", id="title"),
            Input(placeholder="Entity name, e.g. Product", id="entity-name"),
            Input(placeholder='Fields, e.g. "price:money, name:str"', id="entity-fields"),
            Input(placeholder="…or describe the app for AI extraction", id="entity-desc"),
            Button("Generate", id="generate-btn", variant="success"),
            Static("", id="result"),
        )
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "generate-btn":
            return
        name = self.query_one("#entity-name", Input).value.strip()
        fields_raw = self.query_one("#entity-fields", Input).value.strip()
        desc = self.query_one("#entity-desc", Input).value.strip()
        out = self.query_one("#result", Static)

        if name and fields_raw:
            fields = [tuple(p.strip().split(":", 1)) for p in fields_raw.split(",") if ":" in p]
            result = self.app.builder.generate_entity(EntitySpec(name, fields))
            out.update(("[green]" if result.ok else "[red]") + result.message)
        elif desc:
            extract = await self.app.builder.extract_entities(desc)
            if not extract.ok:
                out.update(f"[yellow]{extract.message}[/yellow]")
                return
            lines = []
            for spec in extract.entities:
                r = self.app.builder.generate_entity(spec)
                lines.append(("✓ " if r.ok else "✗ ") + r.message)
            out.update("\n".join(lines))
        else:
            out.update("[red]Provide name+fields, or a description.[/red]")
```

```python
# cli/src/lich/tui/screens/memory_browser.py
"""Memory browser: note list + rendered markdown."""
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, ListItem, ListView, Markdown, Static

from lich.memory.notes import read_note


class MemoryBrowserScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Horizontal(
            ListView(id="note-list"),
            Markdown("", id="note-view"),
        )
        yield Footer()

    def on_mount(self) -> None:
        lv = self.query_one("#note-list", ListView)
        for meta in self.app.builder.memory_notes():
            lv.append(ListItem(Static(f"{meta['name']}  [dim]{meta['type']}[/dim]"),
                               name=meta["name"]))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        name = event.item.name
        path = self.app.builder.vault_dir / f"{name}.md"
        if path.exists():
            self.query_one("#note-view", Markdown).update(read_note(path).body)
```

- [ ] **Step 5: Implement the app**

```python
# cli/src/lich/tui/app.py
"""Lich TUI application shell. Business logic: tui/builder.py."""
from pathlib import Path

from textual.app import App
from textual.binding import Binding

from lich.tui.builder import Builder
from lich.tui.screens.dashboard import DashboardScreen
from lich.tui.screens.memory_browser import MemoryBrowserScreen
from lich.tui.screens.new_entity import NewEntityScreen


class LichTUI(App):
    """🧙 Lich — AI-powered full-stack app builder."""

    TITLE = "Lich"
    BINDINGS = [
        Binding("n", "goto('new_entity')", "New entity"),
        Binding("m", "goto('memory')", "Memory"),
        Binding("d", "goto('dashboard')", "Dashboard"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, project_root: Path | None = None, ai_provider: object | None = None):
        super().__init__()
        self.builder = Builder(project_root=project_root, ai_provider=ai_provider)

    def on_mount(self) -> None:
        self.install_screen(DashboardScreen(name="dashboard"), name="dashboard")
        self.install_screen(NewEntityScreen(name="new_entity"), name="new_entity")
        self.install_screen(MemoryBrowserScreen(name="memory"), name="memory")
        self.push_screen("dashboard")

    def action_goto(self, screen: str) -> None:
        self.switch_screen(screen)


def run_tui() -> None:
    """Entry point for `lich tui`. AI provider wiring lands with Phase 1a.
    [RE-VERIFY: pass the configured provider from lich config once Phase 1a is merged.]"""
    LichTUI().run()
```

- [ ] **Step 6: Wire `lich tui` into cli.py** **[RE-VERIFY import block]**

In `cli/src/lich/cli.py` add near the other command registrations:

```python
from lich.tui.app import run_tui
app.command(name="tui", help="Launch the Lich TUI app builder")(run_tui)
```

Caveat: this makes `import lich.cli` import Textual. If CLI startup time degrades noticeably (`time lich version` before/after), wrap in a lazy proxy instead:

```python
def _tui_command():
    """Launch the Lich TUI app builder."""
    from lich.tui.app import run_tui
    run_tui()
app.command(name="tui", help="Launch the Lich TUI app builder")(_tui_command)
```

Use the lazy variant by default — measured or not, it is strictly safer.

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd cli && python3 -m pytest tests/test_tui_app.py tests/test_tui_builder.py -v`
Expected: all passed

- [ ] **Step 8: Manual smoke test**

Run (in a scratch generated project or any dir with a `.lich` marker): `lich tui`
Expected: dashboard renders; `n` opens new-entity; `m` opens memory browser; `q` quits cleanly.

- [ ] **Step 9: Full suite + commit**

Run: `cd cli && python3 -m pytest -q`
Expected: no new failures.

```bash
git add cli/pyproject.toml cli/src/lich/tui/ cli/src/lich/cli.py cli/tests/test_tui_app.py
git commit -m "feat(tui): Textual app — dashboard, new-entity flow, memory browser, lich tui"
```

---

## Task 12: Integration — end-to-end flow test

**Files:**
- Test: `cli/tests/test_phase1b_integration.py`

- [ ] **Step 1: Write the integration test**

```python
# cli/tests/test_phase1b_integration.py
"""
End-to-end: TUI new-entity flow (AI path with fake provider) generates the entity
AND writes the memory note AND the note appears in the memory browser + index.
"""
from pathlib import Path

import pytest

from lich.commands.memory import _vault_dir
from lich.memory.index import MemoryIndex
from lich.tui.app import LichTUI


class FakeAI:
    name = "fake"
    def is_available(self):
        return True
    async def ask_structured(self, prompt, schema):
        return {"entities": [
            {"name": "Product", "fields": [{"name": "price", "type": "money"},
                                           {"name": "name", "type": "str"}]},
        ]}


@pytest.mark.asyncio
async def test_describe_generate_remember(in_lich_project: Path, monkeypatch):
    import lich.tui.builder as builder_mod
    monkeypatch.setattr(builder_mod, "_run_make_entity", lambda name: None)

    app = LichTUI(project_root=in_lich_project, ai_provider=FakeAI())
    async with app.run_test() as pilot:
        await pilot.press("n")
        app.screen.query_one("#entity-desc").value = "a shop that sells products"
        await pilot.click("#generate-btn")
        await pilot.pause()

        # memory note written
        vault = _vault_dir(in_lich_project)
        note = vault / "Product.md"
        assert note.exists()
        assert "| price | money |" in note.read_text()

        # index updated
        idx = MemoryIndex(vault)
        idx.load()
        assert "Product" in idx.nodes

        # memory browser sees it
        await pilot.press("m")
        await pilot.pause()
        items = app.screen.query("#note-list ListItem")
        assert any(li.name == "Product" for li in items)
```

- [ ] **Step 2: Run it**

Run: `cd cli && python3 -m pytest tests/test_phase1b_integration.py -v`
Expected: 1 passed

- [ ] **Step 3: Commit**

```bash
git add cli/tests/test_phase1b_integration.py
git commit -m "test: phase 1b integration — describe -> generate -> remember"
```

---

## Task 13: Phase completion

- [ ] **Step 1: Full suite**

Run: `cd cli && python3 -m pytest -q`
Expected: all green (no growth in any pre-existing failure count).

- [ ] **Step 2: Vault sanity on a real flow**

```bash
cd $(mktemp -d) && mkdir demo && cd demo
printf '{"version": "1.12.15"}' > .lich
mkdir -p backend/internal/entities
lich memory decide "Phase 1b works"
lich memory rebuild-index
lich memory search "works"
```
Expected: decision note created, index built, search finds `decision-phase-1b-works`.

- [ ] **Step 3: Update CHANGELOG.md** — add an Unreleased entry:

```markdown
## [Unreleased] — v2 Phase 1b
### Added
- `lich tui` — Textual app: dashboard, new-entity flow (AI + manual), memory browser
- `lich memory` — knowledge-graph vault: show, search, decide, rebuild-index
- Concept Engine: YAML workflows (create_app), executor, tool registry
- `.lich/memory/` Obsidian-compatible notes with auto entity notes on generation
```

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: changelog for v2 phase 1b (tui + concepts + memory)"
```

- [ ] **Step 5: Report** — list commits, confirm suite state, flag every [RE-VERIFY] item that was hit during execution. Do NOT bump the version and do NOT publish — v2 versioning is decided at the v2 release checkpoint by a human.

---

## Execution order & notes for the worker

- Tasks 1→5 (memory) and 6→9 (concepts) are independent chains; 10→12 need both.
- Task 4 contains a **layout decision** (file vs directory `.lich` marker) — read its Step 1 note fully before coding; do not modify shared conftest fixtures.
- pytest-asyncio is already in dev deps; ensure `asyncio_mode = auto` or use explicit `@pytest.mark.asyncio` (as written) — check `cli/pytest.ini` for an `asyncio_mode` line; if absent, the explicit markers used here work with pytest-asyncio defaults ≥0.23 in strict mode only when `asyncio_mode=strict` — if tests error with "async def functions are not natively supported", add `asyncio_mode = auto` under `[pytest]` in `cli/pytest.ini`.
- **[RE-VERIFY] index (files v1 hardening touches):** `cli/src/lich/cli.py` (Tasks 4, 11), `lich/commands/make.py` import in `_run_make_entity` (Task 10), `_check_lich_project` duplication (Task 4 — use `commands/common.py` if v1 Phase 3 has landed), MCP-adjacent conventions if exposing memory tools later (out of scope here).

## Spec coverage self-check (for the reviewer)

- TUI screens (spec §6): dashboard, new-entity (description→review→generate simplified to single screen for Phase 1b — full multi-screen wizard is Phase 2 continuous mode), memory browser. Welcome/init screen deferred: `lich init` already covers project creation; noted as deviation.
- Builder pattern (spec §6): Task 10, zero Textual imports, enforced by test.
- Concept Engine (spec §8): schema, loader (progressive disclosure + matching), executor (${var}, on_error), registry with context readers + `read_memory`; `create_app.yaml` verbatim fixture.
- Memory write path (spec §16/Feature 12): entity notes (generated-section markers preserve human edits), decisions, session skeleton, incremental index, Obsidian validation, CLI (show/search/decide/rebuild-index).
- Graceful degradation (spec §7): no-AI paths tested in builder, registry, and TUI.
- Context Assembler is **Phase 2** (per v2 spec implementation phasing) — only the `neighbors()` graph primitive lands here. Session note full summaries also Phase 2.
