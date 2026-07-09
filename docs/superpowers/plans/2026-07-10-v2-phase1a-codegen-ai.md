# Lich v2 Phase 1a: Smart Code Gen + AI Adapter (BYOA) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **DRAFT (2026-07-10, written pre-v1-hardening):** Greenfield tasks are executable as-is. Tasks marked **[RE-VERIFY]** touch files v1 hardening will change — re-read before executing. Double-check pass planned with Opus.

**Goal:** `lich make entity Product --fields "name:str, price:money, seller:fk(User), status:enum(draft,active,sold)"` generates 9 complete backend files via Jinja2 templates, and a BYOA AI adapter layer (Claude/Copilot/Gemini CLI + local OpenAI-compatible) provides `ask()`/`ask_structured()` for the later TUI.

**Architecture:** New `codegen/` package (parser → spec dataclasses → Jinja2 render → file writer) replaces f-string generation for field-aware entities; legacy skeleton path stays for bare `lich make entity X`. New `ai/` package defines an `AIProvider` protocol with four adapters, all subprocess calls via `asyncio.create_subprocess_exec` (spec decision D11), plus JSON extraction with one retry. Config persisted in `.lich/config.yml`.

**Tech Stack:** Python 3.10+, Typer, Jinja2 (new dep), pytest + pytest-asyncio, PyYAML, requests (already deps).

**Source spec:** `docs/superpowers/specs/2026-04-14-lich-v2-design.md` sections 5, 7, Appendix A.

---

## File Structure

```
cli/src/lich/
├── codegen/
│   ├── __init__.py
│   ├── spec.py                 # FieldSpec, RelationSpec, EntitySpec, TYPE_MAP
│   ├── field_parser.py         # "--fields" string → specs
│   ├── relation_parser.py      # fk()/m2m()/has_many() tokens → RelationSpec
│   ├── generator.py            # orchestrates render + write
│   └── templates/              # 9 Jinja2 templates (package data)
│       ├── entity.py.j2
│       ├── port.py.j2
│       ├── adapter.py.j2
│       ├── service.py.j2
│       ├── dto.py.j2
│       ├── api.py.j2
│       ├── factory.py.j2
│       ├── test_service.py.j2
│       └── migration_hint.py.j2
├── ai/
│   ├── __init__.py
│   ├── provider.py             # AIProvider protocol, errors
│   ├── structured.py           # JSON extraction + ask_structured helper
│   ├── factory.py              # get_provider() from .lich/config.yml
│   ├── prompts/
│   │   ├── extract_entities.j2
│   │   └── plan_feature.j2
│   └── adapters/
│       ├── __init__.py
│       ├── base.py             # subprocess CLI adapter base
│       ├── claude_cli.py
│       ├── copilot_cli.py
│       ├── gemini_cli.py
│       └── openai_compat.py    # local Qwen etc.
└── commands/
    ├── config.py               # NEW: lich config set/get/list
    └── make.py                 # MODIFIED: --fields wiring  [RE-VERIFY]

cli/tests/
├── test_field_parser.py
├── test_relation_parser.py
├── test_codegen_templates.py
├── test_generator.py
├── test_make_fields.py
├── test_ai_structured.py
├── test_ai_adapters.py
└── test_config_cmd.py
```

Execution order: Tasks 0→12 (codegen) and 13→16 (AI) are two independent tracks after Task 0; within each track tasks are sequential. Task 17 last.

---

## Task 0: Dependencies + package skeleton

**Files:**
- Modify: `cli/pyproject.toml`
- Create: `cli/src/lich/codegen/__init__.py`, `cli/src/lich/ai/__init__.py`, `cli/src/lich/ai/adapters/__init__.py`

- [ ] **Step 1: Add jinja2 dependency and package data**

In `cli/pyproject.toml`, change the `dependencies` list to:

```toml
dependencies = [
    "typer>=0.9.0",
    "cookiecutter>=2.5.0",
    "rich>=13.0.0",
    "pyyaml>=6.0",
    "requests>=2.28.0",
    "mcp>=0.1.0",
    "jinja2>=3.1.0",
]
```

After the `[tool.setuptools.packages.find]` block, add:

```toml
[tool.setuptools.package-data]
lich = ["codegen/templates/*.j2", "ai/prompts/*.j2"]
```

- [ ] **Step 2: Create empty packages**

```bash
mkdir -p cli/src/lich/codegen/templates cli/src/lich/ai/adapters cli/src/lich/ai/prompts
touch cli/src/lich/codegen/__init__.py cli/src/lich/ai/__init__.py cli/src/lich/ai/adapters/__init__.py
```

- [ ] **Step 3: Reinstall editable and verify**

Run: `cd cli && pip install -e ".[dev]" -q && python -c "import jinja2, lich.codegen, lich.ai; print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add cli/pyproject.toml cli/src/lich/codegen cli/src/lich/ai
git commit -m "feat(v2): codegen + ai package skeletons, jinja2 dependency"
```

---

## Task 1: Spec dataclasses + type map

**Files:**
- Create: `cli/src/lich/codegen/spec.py`
- Test: `cli/tests/test_field_parser.py` (started here, grown in Tasks 2–3)

- [ ] **Step 1: Write the failing test**

Create `cli/tests/test_field_parser.py`:

```python
"""Tests for codegen spec types and the --fields parser."""
import pytest

from lich.codegen.spec import FieldSpec, RelationSpec, EntitySpec, TYPE_MAP


class TestSpecTypes:
    def test_field_spec_defaults(self):
        f = FieldSpec(name="title", type="str")
        assert f.unique is False
        assert f.index is False
        assert f.nullable is False
        assert f.enum_values == []

    def test_type_map_covers_all_spec_types(self):
        for t in ["str", "int", "float", "bool", "text", "json",
                  "money", "file", "datetime", "enum"]:
            assert t in TYPE_MAP, f"missing type: {t}"

    def test_type_map_python_types(self):
        assert TYPE_MAP["str"].python == "str"
        assert TYPE_MAP["money"].python == "Decimal"
        assert TYPE_MAP["json"].python == "dict"
        assert TYPE_MAP["datetime"].python == "Optional[datetime]"

    def test_entity_spec_names(self):
        e = EntitySpec(name="ProductItem", fields=[], relations=[])
        assert e.snake == "product_item"
        assert e.pascal == "ProductItem"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd cli && python -m pytest tests/test_field_parser.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lich.codegen.spec'`

- [ ] **Step 3: Write the implementation**

Create `cli/src/lich/codegen/spec.py`:

```python
"""
Typed specs for code generation: what the parser produces
and what the Jinja2 templates consume.
"""
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TypeInfo:
    """How one field type renders in each layer."""
    python: str          # entity dataclass annotation
    default: str         # entity dataclass default expression
    sqlalchemy: str      # Column type expression
    pydantic: str        # DTO annotation
    faker: str           # factory expression


TYPE_MAP: dict[str, TypeInfo] = {
    "str":      TypeInfo("str", '""', "String(255)", "str", "fake.word()"),
    "int":      TypeInfo("int", "0", "Integer", "int", "fake.random_int(0, 1000)"),
    "float":    TypeInfo("float", "0.0", "Float", "float", "fake.pyfloat(positive=True)"),
    "bool":     TypeInfo("bool", "False", "Boolean", "bool", "fake.pybool()"),
    "text":     TypeInfo("str", '""', "Text", "str", "fake.paragraph()"),
    "json":     TypeInfo("dict", "field(default_factory=dict)", "JSON", "dict", "{}"),
    "money":    TypeInfo("Decimal", 'Decimal("0")', "Numeric(10, 2)", "Decimal",
                         'Decimal(str(fake.pyfloat(positive=True, max_value=999)))'),
    "file":     TypeInfo("Optional[str]", "None", "String(500)", "Optional[str]", "None"),
    "datetime": TypeInfo("Optional[datetime]", "None", "DateTime", "Optional[datetime]", "None"),
    # enum handled specially: python type is the generated Enum class
    "enum":     TypeInfo("", "", "String(50)", "", ""),
}

_SNAKE_1 = re.compile(r"(.)([A-Z][a-z]+)")
_SNAKE_2 = re.compile(r"([a-z0-9])([A-Z])")


def to_snake(name: str) -> str:
    return _SNAKE_2.sub(r"\1_\2", _SNAKE_1.sub(r"\1_\2", name)).lower()


@dataclass
class FieldSpec:
    name: str
    type: str                          # key into TYPE_MAP
    unique: bool = False
    index: bool = False
    nullable: bool = False
    enum_values: list[str] = field(default_factory=list)

    @property
    def enum_class(self) -> str:
        """Enum class name fragment, e.g. status -> Status."""
        return "".join(p.capitalize() for p in self.name.split("_"))


@dataclass
class RelationSpec:
    name: str                          # e.g. seller
    kind: str                          # fk | m2m | has_many
    target: str                        # e.g. User
    nullable: bool = False

    @property
    def target_snake(self) -> str:
        return to_snake(self.target)


@dataclass
class EntitySpec:
    name: str
    fields: list[FieldSpec]
    relations: list[RelationSpec]

    @property
    def pascal(self) -> str:
        return self.name[0].upper() + self.name[1:]

    @property
    def snake(self) -> str:
        return to_snake(self.name)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd cli && python -m pytest tests/test_field_parser.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/codegen/spec.py cli/tests/test_field_parser.py
git commit -m "feat(codegen): FieldSpec/RelationSpec/EntitySpec + type map"
```

---

## Task 2: Field parser — basic types

**Files:**
- Create: `cli/src/lich/codegen/field_parser.py`
- Test: `cli/tests/test_field_parser.py` (append)

- [ ] **Step 1: Append failing tests**

Append to `cli/tests/test_field_parser.py`:

```python
from lich.codegen.field_parser import parse_fields, FieldParseError


class TestBasicTypes:
    def test_single_field(self):
        fields, relations = parse_fields("name:str")
        assert len(fields) == 1 and relations == []
        assert fields[0].name == "name" and fields[0].type == "str"

    def test_all_basic_types(self):
        src = "a:str, b:int, c:float, d:bool, e:text, f:json, g:money, h:file, i:datetime"
        fields, _ = parse_fields(src)
        assert [f.type for f in fields] == [
            "str", "int", "float", "bool", "text", "json", "money", "file", "datetime"]

    def test_whitespace_tolerant(self):
        fields, _ = parse_fields("  name : str ,age:int ")
        assert [f.name for f in fields] == ["name", "age"]

    def test_unknown_type_raises(self):
        with pytest.raises(FieldParseError, match="Unknown type 'strr'"):
            parse_fields("name:strr")

    def test_missing_colon_raises(self):
        with pytest.raises(FieldParseError, match="Expected 'name:type'"):
            parse_fields("name")

    def test_invalid_identifier_raises(self):
        with pytest.raises(FieldParseError, match="Invalid field name"):
            parse_fields("2fast:str")

    def test_duplicate_field_raises(self):
        with pytest.raises(FieldParseError, match="Duplicate field 'name'"):
            parse_fields("name:str, name:int")

    def test_empty_string_raises(self):
        with pytest.raises(FieldParseError, match="No fields"):
            parse_fields("   ")
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_field_parser.py::TestBasicTypes -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lich.codegen.field_parser'`

- [ ] **Step 3: Implement the parser**

Create `cli/src/lich/codegen/field_parser.py`:

```python
"""
Parse a --fields string like
  "name:str, email:str(unique), status:enum(draft,active), seller:fk(User)"
into FieldSpec / RelationSpec lists.
"""
import re

from lich.codegen.relation_parser import RELATION_KINDS, parse_relation
from lich.codegen.spec import TYPE_MAP, FieldSpec, RelationSpec

IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# name : type ( args )   -- args optional, no nested parens
TOKEN_RE = re.compile(r"^\s*([^:\s]+)\s*:\s*([A-Za-z_]+)\s*(?:\(([^()]*)\))?\s*$")


class FieldParseError(ValueError):
    pass


def _split_tokens(source: str) -> list[str]:
    """Split on commas that are NOT inside parentheses."""
    tokens, depth, current = [], 0, []
    for ch in source:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise FieldParseError("Unbalanced parentheses in --fields")
        if ch == "," and depth == 0:
            tokens.append("".join(current))
            current = []
        else:
            current.append(ch)
    if depth != 0:
        raise FieldParseError("Unbalanced parentheses in --fields")
    tokens.append("".join(current))
    return [t for t in (t.strip() for t in tokens) if t]


def parse_fields(source: str) -> tuple[list[FieldSpec], list[RelationSpec]]:
    tokens = _split_tokens(source)
    if not tokens:
        raise FieldParseError("No fields given")

    fields: list[FieldSpec] = []
    relations: list[RelationSpec] = []
    seen: set[str] = set()

    for token in tokens:
        m = TOKEN_RE.match(token)
        if not m:
            raise FieldParseError(f"Expected 'name:type', got '{token.strip()}'")
        name, type_name, args = m.group(1), m.group(2), m.group(3)

        if not IDENT_RE.match(name):
            raise FieldParseError(f"Invalid field name '{name}'")
        if name in seen:
            raise FieldParseError(f"Duplicate field '{name}'")
        seen.add(name)

        if type_name in RELATION_KINDS:
            relations.append(parse_relation(name, type_name, args))
            continue

        if type_name not in TYPE_MAP:
            raise FieldParseError(
                f"Unknown type '{type_name}' for field '{name}'. "
                f"Valid: {', '.join(sorted(TYPE_MAP))}, {', '.join(sorted(RELATION_KINDS))}")

        fields.append(_build_field(name, type_name, args))
    return fields, relations


def _build_field(name: str, type_name: str, args: "str | None") -> FieldSpec:
    spec = FieldSpec(name=name, type=type_name)
    if type_name == "enum":
        if not args:
            raise FieldParseError(f"enum field '{name}' needs values: {name}:enum(a,b)")
        values = [v.strip() for v in args.split(",") if v.strip()]
        for v in values:
            if not IDENT_RE.match(v):
                raise FieldParseError(f"Invalid enum value '{v}' on field '{name}'")
        if len(values) < 2:
            raise FieldParseError(f"enum field '{name}' needs at least 2 values")
        spec.enum_values = values
        return spec

    for constraint in [c.strip() for c in (args or "").split(",") if c.strip()]:
        if constraint == "unique":
            spec.unique = True
        elif constraint == "index":
            spec.index = True
        elif constraint in ("null", "nullable"):
            spec.nullable = True
        else:
            raise FieldParseError(
                f"Unknown constraint '{constraint}' on field '{name}' (valid: unique, index, null)")
    return spec
```

- [ ] **Step 4: Create a minimal relation_parser so imports resolve**

Create `cli/src/lich/codegen/relation_parser.py` (fully tested in Task 4):

```python
"""
Parse relation tokens: seller:fk(User), tags:m2m(Tag), comments:has_many(Comment).
"""
import re

from lich.codegen.spec import RelationSpec

RELATION_KINDS = {"fk", "m2m", "has_many"}
TARGET_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class RelationParseError(ValueError):
    pass


def parse_relation(name: str, kind: str, args: "str | None") -> RelationSpec:
    if not args:
        raise RelationParseError(f"{kind} relation '{name}' needs a target: {name}:{kind}(Entity)")
    parts = [p.strip() for p in args.split(",") if p.strip()]
    target = parts[0]
    if not TARGET_RE.match(target):
        raise RelationParseError(f"Invalid relation target '{target}' on '{name}'")
    nullable = False
    for extra in parts[1:]:
        if extra in ("null", "nullable"):
            if kind != "fk":
                raise RelationParseError(f"'null' is only valid on fk relations ('{name}')")
            nullable = True
        else:
            raise RelationParseError(f"Unknown relation option '{extra}' on '{name}'")
    return RelationSpec(name=name, kind=kind, target=target, nullable=nullable)
```

- [ ] **Step 5: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_field_parser.py -v`
Expected: all passed (12 tests)

- [ ] **Step 6: Commit**

```bash
git add cli/src/lich/codegen/field_parser.py cli/src/lich/codegen/relation_parser.py cli/tests/test_field_parser.py
git commit -m "feat(codegen): --fields parser for basic types with error handling"
```

---

## Task 3: Field parser — constraints and enums

**Files:**
- Test: `cli/tests/test_field_parser.py` (append)
- Modify: none expected (implementation from Task 2 already covers; this task locks behavior with tests)

- [ ] **Step 1: Append the tests**

Append to `cli/tests/test_field_parser.py`:

```python
class TestConstraints:
    def test_unique(self):
        fields, _ = parse_fields("email:str(unique)")
        assert fields[0].unique is True

    def test_unique_and_index(self):
        fields, _ = parse_fields("slug:str(unique,index)")
        assert fields[0].unique and fields[0].index

    def test_nullable(self):
        fields, _ = parse_fields("bio:text(null)")
        assert fields[0].nullable is True

    def test_unknown_constraint_raises(self):
        with pytest.raises(FieldParseError, match="Unknown constraint 'uniqe'"):
            parse_fields("email:str(uniqe)")


class TestEnums:
    def test_enum_values(self):
        fields, _ = parse_fields("status:enum(draft,active,sold)")
        assert fields[0].type == "enum"
        assert fields[0].enum_values == ["draft", "active", "sold"]
        assert fields[0].enum_class == "Status"

    def test_enum_needs_values(self):
        with pytest.raises(FieldParseError, match="needs values"):
            parse_fields("status:enum")

    def test_enum_needs_two_values(self):
        with pytest.raises(FieldParseError, match="at least 2"):
            parse_fields("status:enum(only)")

    def test_enum_invalid_value(self):
        with pytest.raises(FieldParseError, match="Invalid enum value"):
            parse_fields("status:enum(a-b,c)")

    def test_mixed_fields_and_enum(self):
        fields, _ = parse_fields("name:str, status:enum(a,b), price:money")
        assert [f.type for f in fields] == ["str", "enum", "money"]
```

- [ ] **Step 2: Run the tests**

Run: `cd cli && python -m pytest tests/test_field_parser.py -v`
Expected: all passed (21 tests). If any fail, fix `field_parser.py` — the Task 2 implementation is supposed to already satisfy these; a failure means a real bug.

- [ ] **Step 3: Commit**

```bash
git add cli/tests/test_field_parser.py
git commit -m "test(codegen): constraint and enum parsing coverage"
```

---

## Task 4: Relation parser

**Files:**
- Test: `cli/tests/test_relation_parser.py`
- Modify: `cli/src/lich/codegen/relation_parser.py` (only if tests expose bugs)

- [ ] **Step 1: Write the tests**

Create `cli/tests/test_relation_parser.py`:

```python
"""Tests for relation token parsing."""
import pytest

from lich.codegen.field_parser import parse_fields
from lich.codegen.relation_parser import RelationParseError, parse_relation


class TestRelations:
    def test_fk(self):
        _, rels = parse_fields("seller:fk(User)")
        assert rels[0].kind == "fk"
        assert rels[0].target == "User"
        assert rels[0].nullable is False
        assert rels[0].target_snake == "user"

    def test_nullable_fk(self):
        _, rels = parse_fields("category:fk(Category,null)")
        assert rels[0].nullable is True

    def test_m2m(self):
        _, rels = parse_fields("tags:m2m(Tag)")
        assert rels[0].kind == "m2m" and rels[0].target == "Tag"

    def test_has_many(self):
        _, rels = parse_fields("comments:has_many(Comment)")
        assert rels[0].kind == "has_many"

    def test_pascal_target_snake(self):
        _, rels = parse_fields("owner:fk(SuperAdmin)")
        assert rels[0].target_snake == "super_admin"

    def test_missing_target_raises(self):
        with pytest.raises(RelationParseError, match="needs a target"):
            parse_relation("seller", "fk", None)

    def test_null_only_on_fk(self):
        with pytest.raises(RelationParseError, match="only valid on fk"):
            parse_fields("tags:m2m(Tag,null)")

    def test_fields_and_relations_split(self):
        fields, rels = parse_fields("name:str, seller:fk(User), tags:m2m(Tag)")
        assert len(fields) == 1 and len(rels) == 2
```

- [ ] **Step 2: Run the tests**

Run: `cd cli && python -m pytest tests/test_relation_parser.py -v`
Expected: 8 passed (implementation exists from Task 2 Step 4; failures are real bugs — fix `relation_parser.py`)

- [ ] **Step 3: Commit**

```bash
git add cli/tests/test_relation_parser.py cli/src/lich/codegen/relation_parser.py
git commit -m "test(codegen): relation parser coverage (fk/m2m/has_many)"
```

---

## Task 5: Template engine + entity template

**Files:**
- Create: `cli/src/lich/codegen/engine.py`, `cli/src/lich/codegen/templates/entity.py.j2`
- Test: `cli/tests/test_codegen_templates.py`

- [ ] **Step 1: Write the failing test**

Create `cli/tests/test_codegen_templates.py`:

```python
"""Render every codegen template and assert the output is valid Python with expected content."""
import ast

import pytest

from lich.codegen.engine import render_template
from lich.codegen.field_parser import parse_fields
from lich.codegen.spec import EntitySpec


@pytest.fixture
def product() -> EntitySpec:
    fields, relations = parse_fields(
        "name:str, price:money, status:enum(draft,active,sold), "
        "seller:fk(User), tags:m2m(Tag), category:fk(Category,null)")
    return EntitySpec(name="Product", fields=fields, relations=relations)


class TestEntityTemplate:
    def test_renders_valid_python(self, product):
        out = render_template("entity.py.j2", entity=product)
        ast.parse(out)  # raises SyntaxError if broken

    def test_contains_dataclass_and_base(self, product):
        out = render_template("entity.py.j2", entity=product)
        assert "@dataclass" in out
        assert "class Product(BaseEntity):" in out
        assert "from .base import BaseEntity" in out

    def test_enum_class_generated(self, product):
        out = render_template("entity.py.j2", entity=product)
        assert "class ProductStatus(Enum):" in out
        assert 'DRAFT = "draft"' in out
        assert "status: ProductStatus = ProductStatus.DRAFT" in out

    def test_money_uses_decimal(self, product):
        out = render_template("entity.py.j2", entity=product)
        assert "from decimal import Decimal" in out
        assert 'price: Decimal = Decimal("0")' in out

    def test_fk_becomes_id_field(self, product):
        out = render_template("entity.py.j2", entity=product)
        assert "seller_id: Optional[UUID] = None" in out
        assert "category_id: Optional[UUID] = None" in out

    def test_m2m_becomes_id_list(self, product):
        out = render_template("entity.py.j2", entity=product)
        assert "tag_ids: list[UUID] = field(default_factory=list)" in out
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lich.codegen.engine'`

- [ ] **Step 3: Write the engine**

Create `cli/src/lich/codegen/engine.py`:

```python
"""Jinja2 environment for code generation templates."""
from jinja2 import Environment, PackageLoader, StrictUndefined

from lich.codegen.spec import TYPE_MAP

_env: "Environment | None" = None


def get_env() -> Environment:
    global _env
    if _env is None:
        _env = Environment(
            loader=PackageLoader("lich.codegen", "templates"),
            undefined=StrictUndefined,      # typos fail loudly, not silently
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        _env.globals["TYPE_MAP"] = TYPE_MAP
    return _env


def render_template(name: str, **context) -> str:
    return get_env().get_template(name).render(**context)
```

- [ ] **Step 4: Write the entity template**

Create `cli/src/lich/codegen/templates/entity.py.j2`:

```jinja
"""
{{ entity.pascal }} entity - Pure domain model.
Generated by lich make entity. Edit freely - lich will not overwrite without --force.
"""
from dataclasses import dataclass, field
{% if entity.fields | selectattr("type", "equalto", "money") | list %}
from decimal import Decimal
{% endif %}
{% if entity.fields | selectattr("type", "equalto", "datetime") | list %}
from datetime import datetime
{% endif %}
{% if entity.fields | selectattr("type", "equalto", "enum") | list %}
from enum import Enum
{% endif %}
from typing import Optional
from uuid import UUID

from .base import BaseEntity

{% for f in entity.fields if f.type == "enum" %}

class {{ entity.pascal }}{{ f.enum_class }}(Enum):
    """Allowed values for {{ entity.pascal }}.{{ f.name }}."""
{% for v in f.enum_values %}
    {{ v | upper }} = "{{ v }}"
{% endfor %}
{% endfor %}


@dataclass
class {{ entity.pascal }}(BaseEntity):
    """
    {{ entity.pascal }} domain entity.

    PURE domain model - no ORM, no HTTP concerns.
{% for r in entity.relations if r.kind == "has_many" %}
    Reverse relation: {{ r.name }} -> list[{{ r.target }}] (query via {{ r.target }}Port).
{% endfor %}
    """

{% for f in entity.fields %}
{% if f.type == "enum" %}
    {{ f.name }}: {{ entity.pascal }}{{ f.enum_class }} = {{ entity.pascal }}{{ f.enum_class }}.{{ f.enum_values[0] | upper }}
{% elif TYPE_MAP[f.type].default.startswith("field(") %}
    {{ f.name }}: {{ TYPE_MAP[f.type].python }} = {{ TYPE_MAP[f.type].default }}
{% else %}
    {{ f.name }}: {{ TYPE_MAP[f.type].python }} = {{ TYPE_MAP[f.type].default }}
{% endif %}
{% endfor %}
{% for r in entity.relations if r.kind == "fk" %}
    {{ r.name }}_id: Optional[UUID] = None
{% endfor %}
{% for r in entity.relations if r.kind == "m2m" %}
    {{ r.name | rstrip_s }}_ids: list[UUID] = field(default_factory=list)
{% endfor %}

    def _validate(self):
        """Enforce {{ entity.pascal }} domain invariants."""
{% set required = entity.fields | selectattr("type", "equalto", "str") | rejectattr("nullable") | list %}
{% if required %}
{% for f in required %}
        if not self.{{ f.name }}:
            raise ValueError("{{ f.name }} is required")
{% endfor %}
{% else %}
        pass
{% endif %}
```

- [ ] **Step 5: Add the `rstrip_s` filter to the engine**

The m2m field name `tags` becomes `tag_ids`. In `cli/src/lich/codegen/engine.py`, inside `get_env()` after `_env.globals` line, add:

```python
        _env.filters["rstrip_s"] = lambda s: s[:-1] if s.endswith("s") else s
```

- [ ] **Step 6: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v`
Expected: 6 passed. If Jinja whitespace makes `ast.parse` fail, run `python -c "from lich.codegen.engine import render_template; from lich.codegen.field_parser import parse_fields; from lich.codegen.spec import EntitySpec; f,r = parse_fields('name:str, price:money, status:enum(a,b)'); print(render_template('entity.py.j2', entity=EntitySpec('Product', f, r)))"` and inspect the exact output. Fix indentation in the template, not the test.

- [ ] **Step 7: Commit**

```bash
git add cli/src/lich/codegen/engine.py cli/src/lich/codegen/templates/entity.py.j2 cli/tests/test_codegen_templates.py
git commit -m "feat(codegen): jinja2 engine + entity template with enums, money, relations"
```

---

## Task 6: Port + adapter templates

**Files:**
- Create: `cli/src/lich/codegen/templates/port.py.j2`, `cli/src/lich/codegen/templates/adapter.py.j2`
- Test: `cli/tests/test_codegen_templates.py` (append)

- [ ] **Step 1: Append failing tests**

Append to `cli/tests/test_codegen_templates.py`:

```python
class TestPortTemplate:
    def test_valid_python_and_interface(self, product):
        out = render_template("port.py.j2", entity=product)
        ast.parse(out)
        assert "class ProductPort(ABC):" in out
        assert "async def get_by_id" in out
        assert "async def list_all" in out
        assert "async def save" in out
        assert "async def delete" in out

    def test_unique_fields_get_finders(self, product):
        # product has no unique field; build one that does
        from lich.codegen.field_parser import parse_fields
        from lich.codegen.spec import EntitySpec
        f, r = parse_fields("email:str(unique), name:str")
        out = render_template("port.py.j2", entity=EntitySpec("Customer", f, r))
        assert "async def find_by_email" in out


class TestAdapterTemplate:
    def test_valid_python_sqlalchemy_model(self, product):
        out = render_template("adapter.py.j2", entity=product)
        ast.parse(out)
        assert "class ProductModel(Base):" in out
        assert '__tablename__ = "products"' in out
        assert "class ProductRepository(ProductPort):" in out
        assert "Numeric(10, 2)" in out          # money column
        assert "_model_to_entity" in out and "_entity_to_model" in out

    def test_fk_column(self, product):
        out = render_template("adapter.py.j2", entity=product)
        assert 'seller_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)' in out
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v -k "Port or Adapter"`
Expected: FAIL with `TemplateNotFound: port.py.j2`

- [ ] **Step 3: Write the port template**

Create `cli/src/lich/codegen/templates/port.py.j2`:

```jinja
"""
{{ entity.pascal }} port - Repository interface (hexagonal architecture).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from internal.entities.{{ entity.snake }} import {{ entity.pascal }}


class {{ entity.pascal }}Port(ABC):
    """{{ entity.pascal }} repository interface. Services depend on this, never on adapters."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[{{ entity.pascal }}]:
        ...

{% for f in entity.fields if f.unique %}
    @abstractmethod
    async def find_by_{{ f.name }}(self, {{ f.name }}: {{ TYPE_MAP[f.type].python }}) -> Optional[{{ entity.pascal }}]:
        ...

{% endfor %}
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[{{ entity.pascal }}]:
        ...

    @abstractmethod
    async def save(self, entity: {{ entity.pascal }}) -> {{ entity.pascal }}:
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        ...
```

- [ ] **Step 4: Write the adapter template**

Create `cli/src/lich/codegen/templates/adapter.py.j2`:

```jinja
"""
{{ entity.pascal }} repository - SQLAlchemy adapter implementing {{ entity.pascal }}Port.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, Numeric, String, Text, select
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession

from internal.adapters.db.connection import Base
from internal.entities.{{ entity.snake }} import {{ entity.pascal }}{% for f in entity.fields if f.type == "enum" %}, {{ entity.pascal }}{{ f.enum_class }}{% endfor %}

from internal.ports.{{ entity.snake }}_port import {{ entity.pascal }}Port


class {{ entity.pascal }}Model(Base):
    """SQLAlchemy model - persistence shape of {{ entity.pascal }}."""
    __tablename__ = "{{ entity.snake }}s"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
{% for f in entity.fields %}
    {{ f.name }} = Column({{ TYPE_MAP[f.type].sqlalchemy }}{% if f.unique %}, unique=True{% endif %}{% if f.index %}, index=True{% endif %}{% if f.nullable or f.type in ("datetime", "file") %}, nullable=True{% else %}, nullable=False{% endif %})
{% endfor %}
{% for r in entity.relations if r.kind == "fk" %}
    {{ r.name }}_id = Column(PGUUID(as_uuid=True), ForeignKey("{{ r.target_snake }}s.id"), nullable=True)
{% endfor %}


class {{ entity.pascal }}Repository({{ entity.pascal }}Port):
    """Database adapter for {{ entity.pascal }}."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_entity(self, m: "{{ entity.pascal }}Model") -> {{ entity.pascal }}:
        return {{ entity.pascal }}(
            id=m.id,
            created_at=m.created_at,
            updated_at=m.updated_at,
{% for f in entity.fields %}
{% if f.type == "enum" %}
            {{ f.name }}={{ entity.pascal }}{{ f.enum_class }}(m.{{ f.name }}),
{% else %}
            {{ f.name }}=m.{{ f.name }},
{% endif %}
{% endfor %}
{% for r in entity.relations if r.kind == "fk" %}
            {{ r.name }}_id=m.{{ r.name }}_id,
{% endfor %}
        )

    def _apply_entity(self, m: "{{ entity.pascal }}Model", e: {{ entity.pascal }}) -> None:
        m.created_at = e.created_at
        m.updated_at = e.updated_at
{% for f in entity.fields %}
{% if f.type == "enum" %}
        m.{{ f.name }} = e.{{ f.name }}.value
{% else %}
        m.{{ f.name }} = e.{{ f.name }}
{% endif %}
{% endfor %}
{% for r in entity.relations if r.kind == "fk" %}
        m.{{ r.name }}_id = e.{{ r.name }}_id
{% endfor %}

    async def get_by_id(self, id: UUID) -> Optional[{{ entity.pascal }}]:
        m = await self.session.get({{ entity.pascal }}Model, id)
        return self._model_to_entity(m) if m else None

{% for f in entity.fields if f.unique %}
    async def find_by_{{ f.name }}(self, {{ f.name }}: {{ TYPE_MAP[f.type].python }}) -> Optional[{{ entity.pascal }}]:
        result = await self.session.execute(
            select({{ entity.pascal }}Model).where({{ entity.pascal }}Model.{{ f.name }} == {{ f.name }}))
        m = result.scalar_one_or_none()
        return self._model_to_entity(m) if m else None

{% endfor %}
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[{{ entity.pascal }}]:
        result = await self.session.execute(
            select({{ entity.pascal }}Model).limit(limit).offset(offset))
        return [self._model_to_entity(m) for m in result.scalars().all()]

    async def save(self, entity: {{ entity.pascal }}) -> {{ entity.pascal }}:
        m = await self.session.get({{ entity.pascal }}Model, entity.id)
        if m is None:
            m = {{ entity.pascal }}Model(id=entity.id)
            self.session.add(m)
        self._apply_entity(m, entity)
        await self.session.flush()
        return entity

    async def delete(self, id: UUID) -> bool:
        m = await self.session.get({{ entity.pascal }}Model, id)
        if m is None:
            return False
        await self.session.delete(m)
        return True
```

- [ ] **Step 5: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v -k "Port or Adapter"`
Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add cli/src/lich/codegen/templates/port.py.j2 cli/src/lich/codegen/templates/adapter.py.j2 cli/tests/test_codegen_templates.py
git commit -m "feat(codegen): port and SQLAlchemy adapter templates"
```

---

## Task 7: DTO template

**Files:**
- Create: `cli/src/lich/codegen/templates/dto.py.j2`
- Test: `cli/tests/test_codegen_templates.py` (append)

- [ ] **Step 1: Append failing tests**

```python
class TestDtoTemplate:
    def test_valid_python_and_models(self, product):
        out = render_template("dto.py.j2", entity=product)
        ast.parse(out)
        for cls in ["ProductCreate", "ProductUpdate", "ProductResponse", "ProductListResponse"]:
            assert f"class {cls}(BaseModel):" in out

    def test_update_all_optional(self, product):
        out = render_template("dto.py.j2", entity=product)
        update_block = out.split("class ProductUpdate")[1].split("class ")[0]
        assert "Optional[str] = None" in update_block

    def test_response_has_id_and_timestamps(self, product):
        out = render_template("dto.py.j2", entity=product)
        resp = out.split("class ProductResponse")[1].split("class ")[0]
        assert "id: UUID" in resp and "created_at: datetime" in resp
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v -k Dto`
Expected: FAIL with `TemplateNotFound: dto.py.j2`

- [ ] **Step 3: Write the template**

Create `cli/src/lich/codegen/templates/dto.py.j2`:

```jinja
"""
{{ entity.pascal }} DTOs - request/response models (Pydantic).
Never expose domain entities directly through the API.
"""
from datetime import datetime
{% if entity.fields | selectattr("type", "equalto", "money") | list %}
from decimal import Decimal
{% endif %}
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from internal.entities.{{ entity.snake }} import {{ entity.pascal }}{% for f in entity.fields if f.type == "enum" %}, {{ entity.pascal }}{{ f.enum_class }}{% endfor %}


{% macro dto_type(f) -%}
{% if f.type == "enum" %}{{ entity.pascal }}{{ f.enum_class }}{% else %}{{ TYPE_MAP[f.type].pydantic }}{% endif %}
{%- endmacro %}
class {{ entity.pascal }}Create(BaseModel):
{% for f in entity.fields %}
    {{ f.name }}: {{ dto_type(f) }}{% if f.nullable or f.type in ("datetime", "file") %} = None{% endif %}

{% endfor %}
{% for r in entity.relations if r.kind == "fk" %}
    {{ r.name }}_id: Optional[UUID] = None
{% endfor %}
{% if not entity.fields and not entity.relations %}
    pass
{% endif %}


class {{ entity.pascal }}Update(BaseModel):
{% for f in entity.fields %}
    {{ f.name }}: Optional[{{ dto_type(f) }}] = None
{% endfor %}
{% for r in entity.relations if r.kind == "fk" %}
    {{ r.name }}_id: Optional[UUID] = None
{% endfor %}
{% if not entity.fields and not entity.relations %}
    pass
{% endif %}


class {{ entity.pascal }}Response(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
{% for f in entity.fields %}
    {{ f.name }}: {{ dto_type(f) }}{% if f.nullable or f.type in ("datetime", "file") %} = None{% endif %}

{% endfor %}
{% for r in entity.relations if r.kind == "fk" %}
    {{ r.name }}_id: Optional[UUID] = None
{% endfor %}

    @classmethod
    def from_entity(cls, e: {{ entity.pascal }}) -> "{{ entity.pascal }}Response":
        return cls(
            id=e.id,
            created_at=e.created_at,
            updated_at=e.updated_at,
{% for f in entity.fields %}
            {{ f.name }}=e.{{ f.name }},
{% endfor %}
{% for r in entity.relations if r.kind == "fk" %}
            {{ r.name }}_id=e.{{ r.name }}_id,
{% endfor %}
        )


class {{ entity.pascal }}ListResponse(BaseModel):
    items: List[{{ entity.pascal }}Response]
    total: int
    limit: int
    offset: int
```

- [ ] **Step 4: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v -k Dto`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/codegen/templates/dto.py.j2 cli/tests/test_codegen_templates.py
git commit -m "feat(codegen): DTO template (Create/Update/Response/List)"
```

---

## Task 8: Service template

**Files:**
- Create: `cli/src/lich/codegen/templates/service.py.j2`
- Test: `cli/tests/test_codegen_templates.py` (append)

- [ ] **Step 1: Append failing tests**

```python
class TestServiceTemplate:
    def test_valid_python_and_crud(self, product):
        out = render_template("service.py.j2", entity=product)
        ast.parse(out)
        assert "class ProductService:" in out
        for m in ["async def get_product", "async def list_products",
                  "async def create_product", "async def update_product",
                  "async def delete_product"]:
            assert m in out, f"missing {m}"

    def test_unique_conflict_check(self):
        from lich.codegen.field_parser import parse_fields
        from lich.codegen.spec import EntitySpec
        f, r = parse_fields("email:str(unique)")
        out = render_template("service.py.j2", entity=EntitySpec("Customer", f, r))
        assert "find_by_email" in out
        assert "ConflictError" in out
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v -k Service`
Expected: FAIL with `TemplateNotFound: service.py.j2`

- [ ] **Step 3: Write the template**

Create `cli/src/lich/codegen/templates/service.py.j2`:

```jinja
"""
{{ entity.pascal }}Service - Application service (use cases).
Depends on {{ entity.pascal }}Port (interface), never on the adapter.
"""
from typing import List, Optional
from uuid import UUID

from internal.dto.{{ entity.snake }}_dto import {{ entity.pascal }}Create, {{ entity.pascal }}Update
from internal.entities.{{ entity.snake }} import {{ entity.pascal }}
from internal.ports.{{ entity.snake }}_port import {{ entity.pascal }}Port


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class {{ entity.pascal }}Service:
    """CRUD + business logic for {{ entity.pascal }}."""

    def __init__(self, repository: {{ entity.pascal }}Port):
        self.repository = repository

    async def get_{{ entity.snake }}(self, id: UUID) -> {{ entity.pascal }}:
        entity = await self.repository.get_by_id(id)
        if entity is None:
            raise NotFoundError(f"{{ entity.pascal }} {id} not found")
        return entity

    async def list_{{ entity.snake }}s(self, limit: int = 100, offset: int = 0) -> List[{{ entity.pascal }}]:
        return await self.repository.list_all(limit=limit, offset=offset)

    async def create_{{ entity.snake }}(self, data: {{ entity.pascal }}Create) -> {{ entity.pascal }}:
{% for f in entity.fields if f.unique %}
        if await self.repository.find_by_{{ f.name }}(data.{{ f.name }}) is not None:
            raise ConflictError(f"{{ entity.pascal }} with {{ f.name }} '{data.{{ f.name }}}' already exists")
{% endfor %}
        entity = {{ entity.pascal }}(**data.model_dump())
        return await self.repository.save(entity)

    async def update_{{ entity.snake }}(self, id: UUID, data: {{ entity.pascal }}Update) -> {{ entity.pascal }}:
        entity = await self.get_{{ entity.snake }}(id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)
        entity.touch()
        return await self.repository.save(entity)

    async def delete_{{ entity.snake }}(self, id: UUID) -> None:
        deleted = await self.repository.delete(id)
        if not deleted:
            raise NotFoundError(f"{{ entity.pascal }} {id} not found")
```

- [ ] **Step 4: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v -k Service`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/codegen/templates/service.py.j2 cli/tests/test_codegen_templates.py
git commit -m "feat(codegen): service template with unique-conflict checks"
```

---

## Task 9: API routes template

**Files:**
- Create: `cli/src/lich/codegen/templates/api.py.j2`
- Test: `cli/tests/test_codegen_templates.py` (append)

- [ ] **Step 1: Append failing tests**

```python
class TestApiTemplate:
    def test_valid_python_and_routes(self, product):
        out = render_template("api.py.j2", entity=product)
        ast.parse(out)
        assert 'router = APIRouter(prefix="/products", tags=["products"])' in out
        assert '@router.get("/", response_model=ProductListResponse)' in out
        assert '@router.post("/", response_model=ProductResponse, status_code=201)' in out
        assert '@router.get("/{id}"' in out
        assert '@router.patch("/{id}"' in out
        assert '@router.delete("/{id}", status_code=204)' in out

    def test_error_mapping(self, product):
        out = render_template("api.py.j2", entity=product)
        assert "except NotFoundError" in out and "404" in out
        assert "except ConflictError" in out and "409" in out
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v -k Api`
Expected: FAIL with `TemplateNotFound: api.py.j2`

- [ ] **Step 3: Write the template**

Create `cli/src/lich/codegen/templates/api.py.j2`:

```jinja
"""
{{ entity.pascal }} API - FastAPI router (CRUD + pagination).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from internal.adapters.db.connection import get_session
from internal.adapters.db.{{ entity.snake }}_repo import {{ entity.pascal }}Repository
from internal.dto.{{ entity.snake }}_dto import (
    {{ entity.pascal }}Create,
    {{ entity.pascal }}ListResponse,
    {{ entity.pascal }}Response,
    {{ entity.pascal }}Update,
)
from internal.services.{{ entity.snake }}_service import ConflictError, NotFoundError, {{ entity.pascal }}Service

router = APIRouter(prefix="/{{ entity.snake }}s", tags=["{{ entity.snake }}s"])


def get_{{ entity.snake }}_service(session=Depends(get_session)) -> {{ entity.pascal }}Service:
    return {{ entity.pascal }}Service({{ entity.pascal }}Repository(session))


@router.get("/", response_model={{ entity.pascal }}ListResponse)
async def list_{{ entity.snake }}s(
    limit: int = 100,
    offset: int = 0,
    service: {{ entity.pascal }}Service = Depends(get_{{ entity.snake }}_service),
):
    items = await service.list_{{ entity.snake }}s(limit=limit, offset=offset)
    return {{ entity.pascal }}ListResponse(
        items=[{{ entity.pascal }}Response.from_entity(e) for e in items],
        total=len(items),
        limit=limit,
        offset=offset,
    )


@router.get("/{id}", response_model={{ entity.pascal }}Response)
async def get_{{ entity.snake }}(
    id: UUID,
    service: {{ entity.pascal }}Service = Depends(get_{{ entity.snake }}_service),
):
    try:
        return {{ entity.pascal }}Response.from_entity(await service.get_{{ entity.snake }}(id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model={{ entity.pascal }}Response, status_code=201)
async def create_{{ entity.snake }}(
    data: {{ entity.pascal }}Create,
    service: {{ entity.pascal }}Service = Depends(get_{{ entity.snake }}_service),
):
    try:
        return {{ entity.pascal }}Response.from_entity(await service.create_{{ entity.snake }}(data))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch("/{id}", response_model={{ entity.pascal }}Response)
async def update_{{ entity.snake }}(
    id: UUID,
    data: {{ entity.pascal }}Update,
    service: {{ entity.pascal }}Service = Depends(get_{{ entity.snake }}_service),
):
    try:
        return {{ entity.pascal }}Response.from_entity(await service.update_{{ entity.snake }}(id, data))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/{id}", status_code=204)
async def delete_{{ entity.snake }}(
    id: UUID,
    service: {{ entity.pascal }}Service = Depends(get_{{ entity.snake }}_service),
):
    try:
        await service.delete_{{ entity.snake }}(id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

- [ ] **Step 4: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v -k Api`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/codegen/templates/api.py.j2 cli/tests/test_codegen_templates.py
git commit -m "feat(codegen): FastAPI router template with error mapping"
```

---

## Task 10: Factory, test, and migration-hint templates

**Files:**
- Create: `cli/src/lich/codegen/templates/factory.py.j2`, `cli/src/lich/codegen/templates/test_service.py.j2`, `cli/src/lich/codegen/templates/migration_hint.py.j2`
- Test: `cli/tests/test_codegen_templates.py` (append)

- [ ] **Step 1: Append failing tests**

```python
class TestRemainingTemplates:
    def test_factory(self, product):
        out = render_template("factory.py.j2", entity=product)
        ast.parse(out)
        assert "class ProductFactory:" in out
        assert "def make(" in out and "def make_many(" in out
        assert "Faker" in out

    def test_test_template(self, product):
        out = render_template("test_service.py.j2", entity=product)
        ast.parse(out)
        assert "class TestProductService:" in out
        assert "AsyncMock" in out
        assert "pytest.mark.asyncio" in out

    def test_migration_hint(self, product):
        out = render_template("migration_hint.py.j2", entity=product)
        assert "op.create_table" in out
        assert '"products"' in out
        assert "sa.Numeric(10, 2)" in out
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v -k Remaining`
Expected: FAIL with `TemplateNotFound: factory.py.j2`

- [ ] **Step 3: Write factory template**

Create `cli/src/lich/codegen/templates/factory.py.j2`:

```jinja
"""
{{ entity.pascal }} test data factory (Faker-based).
"""
from typing import List

from faker import Faker

from internal.entities.{{ entity.snake }} import {{ entity.pascal }}{% for f in entity.fields if f.type == "enum" %}, {{ entity.pascal }}{{ f.enum_class }}{% endfor %}

{% if entity.fields | selectattr("type", "equalto", "money") | list %}
from decimal import Decimal
{% endif %}

fake = Faker()


class {{ entity.pascal }}Factory:
    """Build {{ entity.pascal }} instances with realistic fake data."""

    @staticmethod
    def make(**overrides) -> {{ entity.pascal }}:
        data = {
{% for f in entity.fields %}
{% if f.type == "enum" %}
            "{{ f.name }}": {{ entity.pascal }}{{ f.enum_class }}.{{ f.enum_values[0] | upper }},
{% else %}
            "{{ f.name }}": {{ TYPE_MAP[f.type].faker }},
{% endif %}
{% endfor %}
        }
        data.update(overrides)
        return {{ entity.pascal }}(**data)

    @staticmethod
    def make_many(count: int, **overrides) -> List[{{ entity.pascal }}]:
        return [{{ entity.pascal }}Factory.make(**overrides) for _ in range(count)]
```

- [ ] **Step 4: Write test template**

Create `cli/src/lich/codegen/templates/test_service.py.j2`:

```jinja
"""
{{ entity.pascal }}Service tests (generated starting point - extend with real business cases).
"""
from unittest.mock import AsyncMock

import pytest

from internal.services.{{ entity.snake }}_service import (
    ConflictError,
    NotFoundError,
    {{ entity.pascal }}Service,
)
from tests.factories.{{ entity.snake }}_factory import {{ entity.pascal }}Factory


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return {{ entity.pascal }}Service(repository=mock_repo)


class Test{{ entity.pascal }}Service:
    @pytest.mark.asyncio
    async def test_get_returns_entity(self, service, mock_repo):
        entity = {{ entity.pascal }}Factory.make()
        mock_repo.get_by_id.return_value = entity
        assert await service.get_{{ entity.snake }}(entity.id) is entity

    @pytest.mark.asyncio
    async def test_get_missing_raises(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        entity = {{ entity.pascal }}Factory.make()
        with pytest.raises(NotFoundError):
            await service.get_{{ entity.snake }}(entity.id)

    @pytest.mark.asyncio
    async def test_delete_missing_raises(self, service, mock_repo):
        mock_repo.delete.return_value = False
        entity = {{ entity.pascal }}Factory.make()
        with pytest.raises(NotFoundError):
            await service.delete_{{ entity.snake }}(entity.id)

    @pytest.mark.asyncio
    async def test_list_passes_pagination(self, service, mock_repo):
        mock_repo.list_all.return_value = []
        await service.list_{{ entity.snake }}s(limit=5, offset=10)
        mock_repo.list_all.assert_awaited_once_with(limit=5, offset=10)
```

- [ ] **Step 5: Write migration hint template**

Create `cli/src/lich/codegen/templates/migration_hint.py.j2`:

```jinja
# Migration hint for {{ entity.pascal }} - NOT an alembic revision file.
# Run:  lich migration create "create_{{ entity.snake }}s"
# Then paste this body into the generated revision's upgrade():

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


def upgrade_body():
    op.create_table(
        "{{ entity.snake }}s",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
{% for f in entity.fields %}
        sa.Column("{{ f.name }}", sa.{{ TYPE_MAP[f.type].sqlalchemy }}{% if f.unique %}, unique=True{% endif %}{% if f.index %}, index=True{% endif %}{% if f.nullable or f.type in ("datetime", "file") %}, nullable=True{% else %}, nullable=False{% endif %}),
{% endfor %}
{% for r in entity.relations if r.kind == "fk" %}
        sa.Column("{{ r.name }}_id", UUID(as_uuid=True), sa.ForeignKey("{{ r.target_snake }}s.id"), nullable=True),
{% endfor %}
    )


def downgrade_body():
    op.drop_table("{{ entity.snake }}s")
```

- [ ] **Step 6: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_codegen_templates.py -v`
Expected: all template tests pass (20 tests)

- [ ] **Step 7: Commit**

```bash
git add cli/src/lich/codegen/templates/ cli/tests/test_codegen_templates.py
git commit -m "feat(codegen): factory, generated-test, and migration-hint templates"
```

---

## Task 11: Generator orchestrator

**Files:**
- Create: `cli/src/lich/codegen/generator.py`
- Test: `cli/tests/test_generator.py`

- [ ] **Step 1: Write the failing test**

Create `cli/tests/test_generator.py`:

```python
"""Generator writes all 9 files into a lich project layout."""
from pathlib import Path

import pytest

from lich.codegen.generator import GeneratorError, generate_entity


@pytest.fixture
def project(tmp_path, monkeypatch):
    (tmp_path / ".lich").mkdir()
    base = tmp_path / "backend" / "internal" / "entities"
    base.mkdir(parents=True)
    (base / "base.py").write_text("class BaseEntity: pass\n")
    monkeypatch.chdir(tmp_path)
    return tmp_path


EXPECTED_FILES = [
    "backend/internal/entities/product.py",
    "backend/internal/ports/product_port.py",
    "backend/internal/adapters/db/product_repo.py",
    "backend/internal/services/product_service.py",
    "backend/internal/dto/product_dto.py",
    "backend/api/http/products.py",
    "backend/tests/factories/product_factory.py",
    "backend/tests/test_product_service.py",
    "backend/migrations/hints/create_products.py",
]


class TestGenerateEntity:
    def test_writes_all_files(self, project):
        written = generate_entity("Product", "name:str, price:money, status:enum(a,b)")
        assert sorted(str(p) for p in written) == sorted(EXPECTED_FILES)
        for f in EXPECTED_FILES:
            assert (project / f).exists(), f"missing {f}"

    def test_refuses_overwrite_without_force(self, project):
        generate_entity("Product", "name:str")
        with pytest.raises(GeneratorError, match="already exists"):
            generate_entity("Product", "name:str")

    def test_force_overwrites(self, project):
        generate_entity("Product", "name:str")
        written = generate_entity("Product", "name:str, extra:int", force=True)
        assert len(written) == 9
        content = (project / "backend/internal/entities/product.py").read_text()
        assert "extra: int" in content

    def test_requires_base_entity(self, project):
        (project / "backend/internal/entities/base.py").unlink()
        with pytest.raises(GeneratorError, match="base.py not found"):
            generate_entity("Product", "name:str")

    def test_invalid_entity_name(self, project):
        with pytest.raises(GeneratorError, match="Invalid entity name"):
            generate_entity("2Product", "name:str")
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_generator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lich.codegen.generator'`

- [ ] **Step 3: Implement the generator**

Create `cli/src/lich/codegen/generator.py`:

```python
"""
Orchestrates: parse --fields -> render 9 templates -> write into the project.
Deterministic. No AI. (Spec: Phase 4 of the 4-phase model.)
"""
import re
from pathlib import Path

from lich.codegen.engine import render_template
from lich.codegen.field_parser import parse_fields
from lich.codegen.spec import EntitySpec

ENTITY_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")


class GeneratorError(Exception):
    pass


def _targets(entity: EntitySpec) -> list[tuple[str, Path]]:
    s = entity.snake
    return [
        ("entity.py.j2", Path(f"backend/internal/entities/{s}.py")),
        ("port.py.j2", Path(f"backend/internal/ports/{s}_port.py")),
        ("adapter.py.j2", Path(f"backend/internal/adapters/db/{s}_repo.py")),
        ("service.py.j2", Path(f"backend/internal/services/{s}_service.py")),
        ("dto.py.j2", Path(f"backend/internal/dto/{s}_dto.py")),
        ("api.py.j2", Path(f"backend/api/http/{s}s.py")),
        ("factory.py.j2", Path(f"backend/tests/factories/{s}_factory.py")),
        ("test_service.py.j2", Path(f"backend/tests/test_{s}_service.py")),
        ("migration_hint.py.j2", Path(f"backend/migrations/hints/create_{s}s.py")),
    ]


def generate_entity(name: str, fields_source: str, force: bool = False) -> list[Path]:
    """Generate all files for one entity. Returns the written paths (relative)."""
    if not ENTITY_NAME_RE.match(name):
        raise GeneratorError(f"Invalid entity name '{name}' (letters/digits, must start with a letter)")
    if not Path(".lich").exists():
        raise GeneratorError("Not a Lich project (no .lich directory)")
    if not Path("backend/internal/entities/base.py").exists():
        raise GeneratorError(
            "backend/internal/entities/base.py not found - "
            "field-aware generation targets Lich-template projects")

    fields, relations = parse_fields(fields_source)
    entity = EntitySpec(name=name, fields=fields, relations=relations)

    targets = _targets(entity)
    if not force:
        existing = [str(p) for _, p in targets if p.exists()]
        if existing:
            raise GeneratorError(
                f"File already exists: {', '.join(existing)} (use --force to overwrite)")

    written: list[Path] = []
    for template_name, path in targets:
        content = render_template(template_name, entity=entity)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        written.append(path)
    return written
```

- [ ] **Step 4: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_generator.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/codegen/generator.py cli/tests/test_generator.py
git commit -m "feat(codegen): generator orchestrator writing all 9 entity files"
```

---

## Task 12: Wire `--fields` into `lich make entity` **[RE-VERIFY]**

**[RE-VERIFY]:** v1 hardening Phase 1 adds identifier validation to `make.py` and Phase 3 extracts `_check_lich_project` into `commands/common.py`. Re-read `cli/src/lich/commands/make.py` before this task; adapt import paths, keep both validations (they're compatible — `_validate.py` may already reject bad names before the generator does).

**Files:**
- Modify: `cli/src/lich/commands/make.py` (the `make_entity` function, currently at line 39)
- Test: `cli/tests/test_make_fields.py`

- [ ] **Step 1: Write the failing test**

Create `cli/tests/test_make_fields.py`:

```python
"""lich make entity --fields end-to-end through the CLI."""
from pathlib import Path

from typer.testing import CliRunner

from lich.cli import app

runner = CliRunner()


def _make_project(tmp_path, monkeypatch):
    (tmp_path / ".lich").mkdir()
    base = tmp_path / "backend" / "internal" / "entities"
    base.mkdir(parents=True)
    (base / "base.py").write_text("class BaseEntity: pass\n")
    monkeypatch.chdir(tmp_path)


class TestMakeEntityFields:
    def test_fields_generates_full_set(self, tmp_path, monkeypatch):
        _make_project(tmp_path, monkeypatch)
        result = runner.invoke(app, [
            "make", "entity", "Product",
            "--fields", "name:str, price:money, status:enum(draft,active)"])
        assert result.exit_code == 0, result.output
        assert Path("backend/internal/services/product_service.py").exists()
        assert Path("backend/api/http/products.py").exists()
        content = Path("backend/internal/entities/product.py").read_text()
        assert "price: Decimal" in content

    def test_bad_fields_message(self, tmp_path, monkeypatch):
        _make_project(tmp_path, monkeypatch)
        result = runner.invoke(app, ["make", "entity", "Product", "--fields", "name:strr"])
        assert result.exit_code == 1
        assert "Unknown type" in result.output

    def test_without_fields_legacy_path(self, tmp_path, monkeypatch):
        _make_project(tmp_path, monkeypatch)
        result = runner.invoke(app, ["make", "entity", "Product"])
        assert result.exit_code == 0
        # legacy path writes 3 files only
        assert Path("backend/internal/entities/product.py").exists()
        assert not Path("backend/internal/services/product_service.py").exists()
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_make_fields.py -v`
Expected: FAIL — `make entity` has no `--fields` option (`No such option`)

- [ ] **Step 3: Modify `make_entity`**

In `cli/src/lich/commands/make.py`, replace the `make_entity` signature and add the new branch at the top of the body (before `name_lower = ...`):

```python
@make_app.command("entity")
def make_entity(
    name: str = typer.Argument(..., help="Entity name (e.g., Product)"),
    fields: str = typer.Option(
        None, "--fields",
        help='Field spec, e.g. "name:str, price:money, status:enum(draft,active), seller:fk(User)"'),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
):
    """
    Generate a new entity.

    Without --fields: legacy 3-file skeleton (entity, port, adapter).
    With --fields: full 9-file set (entity, port, adapter, service, DTO,
    API router, factory, tests, migration hint) rendered from templates.
    """
    if not _check_lich_project():
        raise typer.Exit(1)

    if fields:
        from lich.codegen.field_parser import FieldParseError
        from lich.codegen.generator import GeneratorError, generate_entity
        from lich.codegen.relation_parser import RelationParseError

        try:
            written = generate_entity(name, fields, force=force)
        except (FieldParseError, RelationParseError, GeneratorError) as e:
            console.print(f"[red]❌ {e}[/red]")
            raise typer.Exit(1)
        console.print(f"\n🔨 [bold blue]Generated {name} ({len(written)} files):[/bold blue]")
        for path in written:
            console.print(f"   [green]✅ {path}[/green]")
        console.print("\nNext steps:")
        console.print(f"   1. Review the generated files")
        console.print(f"   2. Wire the router: include backend/api/http/{name.lower()}s.py in main.py")
        console.print(f"   3. Create the migration: see backend/migrations/hints/")
        return

    # legacy skeleton path (unchanged below)
```

Keep the rest of the existing function body exactly as it is.

- [ ] **Step 4: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_make_fields.py tests/test_make.py -v`
Expected: new tests pass AND all 21 existing `test_make.py` tests still pass (no regression on the legacy path)

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/commands/make.py cli/tests/test_make_fields.py
git commit -m "feat(make): --fields flag generates full 9-file entity set"
```

---

## Task 13: AI provider protocol + structured output

**Files:**
- Create: `cli/src/lich/ai/provider.py`, `cli/src/lich/ai/structured.py`
- Test: `cli/tests/test_ai_structured.py`

- [ ] **Step 1: Write the failing test**

Create `cli/tests/test_ai_structured.py`:

```python
"""JSON extraction from messy AI output + structured ask flow."""
import pytest

from lich.ai.provider import AIProviderError
from lich.ai.structured import StructuredOutputError, ask_structured, extract_json


class TestExtractJson:
    def test_plain_json(self):
        assert extract_json('{"a": 1}') == {"a": 1}

    def test_fenced_json(self):
        text = 'Here you go:\n```json\n{"a": 1}\n```\nHope that helps!'
        assert extract_json(text) == {"a": 1}

    def test_fence_without_lang(self):
        assert extract_json('```\n{"a": 1}\n```') == {"a": 1}

    def test_preamble_and_trailing(self):
        assert extract_json('Sure! {"a": [1, 2]} - done') == {"a": [1, 2]}

    def test_nested_braces(self):
        assert extract_json('x {"a": {"b": 2}} y') == {"a": {"b": 2}}

    def test_no_json_raises(self):
        with pytest.raises(StructuredOutputError, match="No JSON object"):
            extract_json("I cannot help with that.")

    def test_invalid_json_raises(self):
        with pytest.raises(StructuredOutputError, match="Invalid JSON"):
            extract_json('{"a": unquoted}')


class FakeProvider:
    """Scripted provider: returns queued responses."""
    name = "fake"

    def __init__(self, responses):
        self._responses = list(responses)
        self.prompts = []

    def is_available(self):
        return True

    async def ask(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._responses.pop(0)


class TestAskStructured:
    @pytest.mark.asyncio
    async def test_happy_path(self):
        p = FakeProvider(['{"entities": []}'])
        result = await ask_structured(p, "design an app", {"type": "object"})
        assert result == {"entities": []}
        assert "RESPOND ONLY WITH JSON" in p.prompts[0]

    @pytest.mark.asyncio
    async def test_retry_once_on_bad_json(self):
        p = FakeProvider(["not json at all", '{"ok": true}'])
        result = await ask_structured(p, "task", {})
        assert result == {"ok": True}
        assert len(p.prompts) == 2
        assert "was not valid JSON" in p.prompts[1]

    @pytest.mark.asyncio
    async def test_fails_after_retry(self):
        p = FakeProvider(["garbage", "more garbage"])
        with pytest.raises(StructuredOutputError):
            await ask_structured(p, "task", {})
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_ai_structured.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lich.ai.provider'`

- [ ] **Step 3: Write provider.py**

Create `cli/src/lich/ai/provider.py`:

```python
"""
AIProvider protocol - the BYOA contract (spec section 7).
Lich ships NO AI. Adapters wrap the user's own CLI/endpoint.
"""
from typing import Protocol, runtime_checkable


class AIProviderError(Exception):
    """Provider invocation failed (missing binary, timeout, non-zero exit)."""


@runtime_checkable
class AIProvider(Protocol):
    @property
    def name(self) -> str: ...

    def is_available(self) -> bool: ...

    async def ask(self, prompt: str) -> str: ...
```

- [ ] **Step 4: Write structured.py**

Create `cli/src/lich/ai/structured.py`:

```python
"""
Structured output: append schema instructions, extract JSON from messy
AI responses (markdown fences, preamble), retry once on invalid JSON.
"""
import json

from lich.ai.provider import AIProvider


class StructuredOutputError(Exception):
    pass


def extract_json(text: str) -> dict:
    """Pull the first JSON object out of an AI response."""
    candidate = text
    if "```" in text:
        # take the largest fenced block that contains a brace
        blocks = text.split("```")
        fenced = [b for b in blocks[1::2] if "{" in b]
        if fenced:
            candidate = max(fenced, key=len)
            if candidate.startswith("json"):
                candidate = candidate[4:]

    start = candidate.find("{")
    if start == -1:
        raise StructuredOutputError(f"No JSON object in response: {text[:200]!r}")

    depth = 0
    for i, ch in enumerate(candidate[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                raw = candidate[start:i + 1]
                try:
                    return json.loads(raw)
                except json.JSONDecodeError as e:
                    raise StructuredOutputError(f"Invalid JSON in response: {e}") from e
    raise StructuredOutputError("Unbalanced JSON braces in response")


SCHEMA_INSTRUCTION = """

RESPOND ONLY WITH JSON matching this schema. No prose, no markdown, no explanation:
{schema}
"""

RETRY_INSTRUCTION = """

Your previous response was not valid JSON ({error}).
Respond again with ONLY the JSON object, nothing else.
"""


async def ask_structured(provider: AIProvider, prompt: str, schema: dict) -> dict:
    """One-shot structured ask with a single retry on parse failure."""
    full = prompt + SCHEMA_INSTRUCTION.format(schema=json.dumps(schema, indent=2))
    response = await provider.ask(full)
    try:
        return extract_json(response)
    except StructuredOutputError as first_error:
        retry = full + RETRY_INSTRUCTION.format(error=first_error)
        response = await provider.ask(retry)
        return extract_json(response)
```

- [ ] **Step 5: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_ai_structured.py -v`
Expected: 10 passed

- [ ] **Step 6: Commit**

```bash
git add cli/src/lich/ai/provider.py cli/src/lich/ai/structured.py cli/tests/test_ai_structured.py
git commit -m "feat(ai): provider protocol + JSON extraction with one retry"
```

---

## Task 14: CLI adapters (Claude, Copilot, Gemini)

**Files:**
- Create: `cli/src/lich/ai/adapters/base.py`, `cli/src/lich/ai/adapters/claude_cli.py`, `cli/src/lich/ai/adapters/copilot_cli.py`, `cli/src/lich/ai/adapters/gemini_cli.py`
- Test: `cli/tests/test_ai_adapters.py`

- [ ] **Step 1: Write the failing test**

Create `cli/tests/test_ai_adapters.py`:

```python
"""Adapters build the right argv and never touch a shell."""
import asyncio
import json

import pytest

from lich.ai.adapters.claude_cli import ClaudeCLIAdapter
from lich.ai.adapters.copilot_cli import CopilotCLIAdapter
from lich.ai.adapters.gemini_cli import GeminiCLIAdapter
from lich.ai.provider import AIProviderError


class FakeProcess:
    def __init__(self, stdout=b"", stderr=b"", returncode=0):
        self._stdout, self._stderr = stdout, stderr
        self.returncode = returncode

    async def communicate(self):
        return self._stdout, self._stderr

    def kill(self):
        self.returncode = -9


@pytest.fixture
def spawn_recorder(monkeypatch):
    calls = {}

    def install(stdout=b"ok", returncode=0):
        async def fake_exec(*args, **kwargs):
            calls["argv"] = list(args)
            return FakeProcess(stdout=stdout, returncode=returncode)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
        return calls
    return install


class TestClaudeAdapter:
    @pytest.mark.asyncio
    async def test_argv_and_json_result(self, spawn_recorder):
        payload = json.dumps({"result": "hello from claude"}).encode()
        calls = spawn_recorder(stdout=payload)
        adapter = ClaudeCLIAdapter()
        out = await adapter.ask("hi")
        assert out == "hello from claude"
        assert calls["argv"][:2] == ["claude", "-p"]
        assert "--output-format" in calls["argv"] and "json" in calls["argv"]

    @pytest.mark.asyncio
    async def test_plain_text_fallback(self, spawn_recorder):
        spawn_recorder(stdout=b"not json")
        assert await ClaudeCLIAdapter().ask("hi") == "not json"

    @pytest.mark.asyncio
    async def test_nonzero_exit_raises(self, spawn_recorder):
        spawn_recorder(stdout=b"", returncode=1)
        with pytest.raises(AIProviderError, match="exit 1"):
            await ClaudeCLIAdapter().ask("hi")


class TestOtherAdapters:
    @pytest.mark.asyncio
    async def test_copilot_argv(self, spawn_recorder):
        calls = spawn_recorder(stdout=b"copilot says")
        assert await CopilotCLIAdapter().ask("hi") == "copilot says"
        assert calls["argv"][0] == "copilot"

    @pytest.mark.asyncio
    async def test_gemini_argv(self, spawn_recorder):
        calls = spawn_recorder(stdout=b"gemini says")
        assert await GeminiCLIAdapter().ask("hi") == "gemini says"
        assert calls["argv"][0] == "gemini"


class TestAvailability:
    def test_unavailable_when_binary_missing(self, monkeypatch):
        monkeypatch.setattr("shutil.which", lambda _: None)
        assert ClaudeCLIAdapter().is_available() is False

    def test_available_when_binary_found(self, monkeypatch):
        monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/claude")
        assert ClaudeCLIAdapter().is_available() is True
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_ai_adapters.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lich.ai.adapters.claude_cli'`

- [ ] **Step 3: Write the base adapter**

Create `cli/src/lich/ai/adapters/base.py`:

```python
"""
Base for CLI-wrapping adapters.
SAFETY: asyncio.create_subprocess_exec ONLY (argv list, no shell) - spec decision D11.
"""
import asyncio
import shutil

from lich.ai.provider import AIProviderError

DEFAULT_TIMEOUT = 300  # seconds; creative one-shot calls can be slow


class CLIAdapterBase:
    binary: str = ""

    @property
    def name(self) -> str:
        return self.binary

    def is_available(self) -> bool:
        return shutil.which(self.binary) is not None

    def build_argv(self, prompt: str) -> "list[str]":
        raise NotImplementedError

    def parse_output(self, stdout: str) -> str:
        return stdout.strip()

    async def ask(self, prompt: str) -> str:
        argv = self.build_argv(prompt)
        try:
            process = await asyncio.create_subprocess_exec(
                *argv,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            raise AIProviderError(
                f"'{self.binary}' not found. Install it or switch provider: "
                f"lich config set ai.provider <name>")
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=DEFAULT_TIMEOUT)
        except asyncio.TimeoutError:
            process.kill()
            raise AIProviderError(f"'{self.binary}' timed out after {DEFAULT_TIMEOUT}s")
        if process.returncode != 0:
            raise AIProviderError(
                f"'{self.binary}' failed (exit {process.returncode}): "
                f"{stderr.decode(errors='replace')[:500]}")
        return self.parse_output(stdout.decode(errors="replace"))
```

- [ ] **Step 4: Write the three adapters**

Create `cli/src/lich/ai/adapters/claude_cli.py`:

```python
"""Claude CLI adapter: claude -p <prompt> --output-format json."""
import json

from lich.ai.adapters.base import CLIAdapterBase


class ClaudeCLIAdapter(CLIAdapterBase):
    binary = "claude"

    def build_argv(self, prompt: str) -> list[str]:
        return ["claude", "-p", prompt, "--output-format", "json"]

    def parse_output(self, stdout: str) -> str:
        try:
            data = json.loads(stdout)
            return data.get("result", stdout).strip() if isinstance(data, dict) else stdout.strip()
        except json.JSONDecodeError:
            return stdout.strip()
```

Create `cli/src/lich/ai/adapters/copilot_cli.py`:

```python
"""GitHub Copilot CLI adapter: copilot -p <prompt>."""
from lich.ai.adapters.base import CLIAdapterBase


class CopilotCLIAdapter(CLIAdapterBase):
    binary = "copilot"

    def build_argv(self, prompt: str) -> list[str]:
        return ["copilot", "-p", prompt]
```

Create `cli/src/lich/ai/adapters/gemini_cli.py`:

```python
"""Gemini CLI adapter: gemini -p <prompt>."""
from lich.ai.adapters.base import CLIAdapterBase


class GeminiCLIAdapter(CLIAdapterBase):
    binary = "gemini"

    def build_argv(self, prompt: str) -> list[str]:
        return ["gemini", "-p", prompt]
```

- [ ] **Step 5: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_ai_adapters.py -v`
Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add cli/src/lich/ai/adapters/
git add cli/tests/test_ai_adapters.py
git commit -m "feat(ai): claude/copilot/gemini CLI adapters via create_subprocess_exec"
```

---

## Task 15: OpenAI-compatible adapter (local Qwen)

**Files:**
- Create: `cli/src/lich/ai/adapters/openai_compat.py`
- Test: `cli/tests/test_ai_adapters.py` (append)

- [ ] **Step 1: Append failing tests**

```python
class TestOpenAICompatAdapter:
    @pytest.mark.asyncio
    async def test_posts_chat_completion(self, monkeypatch):
        from lich.ai.adapters.openai_compat import OpenAICompatAdapter
        captured = {}

        class FakeResponse:
            status_code = 200

            def json(self):
                return {"choices": [{"message": {"content": "qwen says hi"}}]}

            def raise_for_status(self):
                pass

        def fake_post(url, json=None, timeout=None):
            captured["url"], captured["json"] = url, json
            return FakeResponse()

        monkeypatch.setattr("requests.post", fake_post)
        adapter = OpenAICompatAdapter(base_url="http://localhost:8080/v1", model="test-model")
        out = await adapter.ask("hello")
        assert out == "qwen says hi"
        assert captured["url"] == "http://localhost:8080/v1/chat/completions"
        assert captured["json"]["model"] == "test-model"
        assert captured["json"]["messages"][0]["content"] == "hello"

    def test_available_checks_models_endpoint(self, monkeypatch):
        from lich.ai.adapters.openai_compat import OpenAICompatAdapter

        class FakeResponse:
            status_code = 200

        monkeypatch.setattr("requests.get", lambda url, timeout=None: FakeResponse())
        assert OpenAICompatAdapter(base_url="http://localhost:8080/v1").is_available() is True

    def test_unavailable_on_connection_error(self, monkeypatch):
        import requests

        from lich.ai.adapters.openai_compat import OpenAICompatAdapter

        def raise_conn(url, timeout=None):
            raise requests.ConnectionError("refused")

        monkeypatch.setattr("requests.get", raise_conn)
        assert OpenAICompatAdapter(base_url="http://localhost:8080/v1").is_available() is False
```

- [ ] **Step 2: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_ai_adapters.py -v -k OpenAI`
Expected: FAIL with `ModuleNotFoundError: No module named 'lich.ai.adapters.openai_compat'`

- [ ] **Step 3: Implement**

Create `cli/src/lich/ai/adapters/openai_compat.py`:

```python
"""
OpenAI-compatible HTTP adapter for local models
(e.g. mlx_lm.server serving Qwen at http://localhost:8080/v1).
Uses requests (already a dependency) via asyncio.to_thread - no event-loop blocking.
"""
import asyncio

import requests

from lich.ai.provider import AIProviderError

DEFAULT_TIMEOUT = 300


class OpenAICompatAdapter:
    def __init__(self, base_url: str = "http://localhost:8080/v1",
                 model: str = "default", max_tokens: int = 4000):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = max_tokens

    @property
    def name(self) -> str:
        return f"local ({self.base_url})"

    def is_available(self) -> bool:
        try:
            return requests.get(f"{self.base_url}/models", timeout=3).status_code == 200
        except requests.RequestException:
            return False

    def _post(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.max_tokens,
            },
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    async def ask(self, prompt: str) -> str:
        try:
            return await asyncio.to_thread(self._post, prompt)
        except requests.RequestException as e:
            raise AIProviderError(f"Local model at {self.base_url} failed: {e}") from e
        except (KeyError, IndexError) as e:
            raise AIProviderError(f"Unexpected response shape from {self.base_url}: {e}") from e
```

- [ ] **Step 4: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_ai_adapters.py -v`
Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add cli/src/lich/ai/adapters/openai_compat.py cli/tests/test_ai_adapters.py
git commit -m "feat(ai): OpenAI-compatible adapter for local models (Qwen/mlx)"
```

---

## Task 16: Prompts, provider factory, `lich config` **[RE-VERIFY]**

**[RE-VERIFY]:** registers a new sub-app in `cli.py`; if v1 hardening reorganized command registration, match the new pattern.

**Files:**
- Create: `cli/src/lich/ai/prompts/extract_entities.j2`, `cli/src/lich/ai/prompts/plan_feature.j2`, `cli/src/lich/ai/factory.py`, `cli/src/lich/commands/config.py`
- Modify: `cli/src/lich/cli.py` (register `config_app`)
- Test: `cli/tests/test_config_cmd.py`

- [ ] **Step 1: Write the prompt templates (from spec Appendix A, verbatim structure)**

Create `cli/src/lich/ai/prompts/extract_entities.j2`:

```jinja
You are Lich, an AI-powered app architect. Analyze the description and extract a structured design.

## App Description
{{ description }}

## Project Context
{% if existing_entities %}
### Existing Entities (do not duplicate)
{% for entity in existing_entities %}
- {{ entity.name }}: {{ entity.fields | join(', ') }}
{% endfor %}
{% endif %}

## Architecture Rules
- Clean Architecture: entities are pure domain models (no DB annotations)
- Each entity: id (UUID), created_at, updated_at
- Enums for fixed-value fields
- Foreign keys for belongs-to
- M2M for tag-like relations

## Task
Extract entities, fields, relations, use cases.

RESPOND ONLY WITH JSON:
{
  "entities": [
    {
      "name": "EntityName",
      "description": "...",
      "fields": [{"name": "...", "type": "...", "constraints": []}],
      "relations": [{"name": "...", "type": "fk", "target": "...", "nullable": false}]
    }
  ],
  "use_cases": [
    {"actor": "User", "action": "create", "entity": "Product", "description": "..."}
  ],
  "rules": [{"entity": "Product", "rule": "Price must be positive"}],
  "suggestions": ["Consider adding a Review entity"]
}
```

Create `cli/src/lich/ai/prompts/plan_feature.j2`:

```jinja
You are Lich. A developer wants to add a feature to their existing app.

## Feature Request
{{ feature }}

## Current State
### Entities
{% for entity in entities %}
- {{ entity.name }}: {{ entity.fields | join(', ') }}
{% endfor %}
### Services
{% for service in services %}
- {{ service.name }}: {{ service.methods | join(', ') }}
{% endfor %}

## Task
Plan what to ADD and what to MODIFY.

RESPOND ONLY WITH JSON:
{
  "new_entities": [],
  "new_services": [],
  "new_apis": [],
  "modifications": [
    {"file": "...", "method": "...", "change": "...", "code_hint": "..."}
  ],
  "new_env_vars": [{"name": "...", "description": "..."}],
  "new_dependencies": ["package>=1.0.0"]
}
```

- [ ] **Step 2: Write the failing config test**

Create `cli/tests/test_config_cmd.py`:

```python
"""lich config set/get and the provider factory."""
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from lich.cli import app

runner = CliRunner()


@pytest.fixture
def project(tmp_path, monkeypatch):
    (tmp_path / ".lich").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestConfigCommand:
    def test_set_and_get(self, project):
        result = runner.invoke(app, ["config", "set", "ai.provider", "claude"])
        assert result.exit_code == 0, result.output
        data = yaml.safe_load((project / ".lich" / "config.yml").read_text())
        assert data["ai"]["provider"] == "claude"

        result = runner.invoke(app, ["config", "get", "ai.provider"])
        assert result.exit_code == 0
        assert "claude" in result.output

    def test_get_missing_key(self, project):
        result = runner.invoke(app, ["config", "get", "ai.nope"])
        assert result.exit_code == 1
        assert "not set" in result.output

    def test_set_invalid_provider(self, project):
        result = runner.invoke(app, ["config", "set", "ai.provider", "skynet"])
        assert result.exit_code == 1
        assert "Valid providers" in result.output

    def test_outside_project_fails(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["config", "set", "ai.provider", "claude"])
        assert result.exit_code == 1


class TestProviderFactory:
    def test_factory_returns_configured_adapter(self, project):
        from lich.ai.factory import get_provider
        runner.invoke(app, ["config", "set", "ai.provider", "claude"])
        provider = get_provider()
        assert provider is not None and provider.name == "claude"

    def test_factory_none_when_unconfigured(self, project):
        from lich.ai.factory import get_provider
        assert get_provider() is None

    def test_factory_local_reads_url_and_model(self, project):
        from lich.ai.factory import get_provider
        runner.invoke(app, ["config", "set", "ai.provider", "local"])
        runner.invoke(app, ["config", "set", "ai.base_url", "http://localhost:9999/v1"])
        runner.invoke(app, ["config", "set", "ai.model", "qwen3"])
        provider = get_provider()
        assert "9999" in provider.name
```

- [ ] **Step 3: Run to verify failure**

Run: `cd cli && python -m pytest tests/test_config_cmd.py -v`
Expected: FAIL — `config` command does not exist (`No such command 'config'`)

- [ ] **Step 4: Write the config command**

Create `cli/src/lich/commands/config.py`:

```python
"""
lich config - project configuration in .lich/config.yml (dot-notation keys).
"""
from pathlib import Path

import typer
import yaml
from rich.console import Console

console = Console()

config_app = typer.Typer(name="config", help="Get/set project configuration", no_args_is_help=True)

CONFIG_PATH = Path(".lich/config.yml")
VALID_PROVIDERS = ["claude", "copilot", "gemini", "local"]


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return yaml.safe_load(CONFIG_PATH.read_text()) or {}
    return {}


def _save(data: dict) -> None:
    CONFIG_PATH.write_text(yaml.safe_dump(data, default_flow_style=False))


def _require_project() -> None:
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        raise typer.Exit(1)


def _resolve(data: dict, dotted: str):
    node = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


@config_app.command("set")
def config_set(key: str = typer.Argument(..., help="Dot key, e.g. ai.provider"),
               value: str = typer.Argument(...)):
    """Set a config value."""
    _require_project()
    if key == "ai.provider" and value not in VALID_PROVIDERS:
        console.print(f"[red]❌ Unknown provider '{value}'. Valid providers: {', '.join(VALID_PROVIDERS)}[/red]")
        raise typer.Exit(1)
    data = load_config()
    node = data
    parts = key.split(".")
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value
    _save(data)
    console.print(f"[green]✅ {key} = {value}[/green]")


@config_app.command("get")
def config_get(key: str = typer.Argument(...)):
    """Read a config value."""
    _require_project()
    value = _resolve(load_config(), key)
    if value is None:
        console.print(f"[yellow]{key} is not set[/yellow]")
        raise typer.Exit(1)
    console.print(str(value))


@config_app.command("list")
def config_list():
    """Show the whole config."""
    _require_project()
    data = load_config()
    console.print(yaml.safe_dump(data, default_flow_style=False) if data else "[dim](empty)[/dim]")
```

- [ ] **Step 5: Write the provider factory**

Create `cli/src/lich/ai/factory.py`:

```python
"""Resolve the configured AI provider from .lich/config.yml (BYOA)."""
from lich.ai.provider import AIProvider
from lich.commands.config import load_config


def get_provider() -> "AIProvider | None":
    """Return the configured provider, or None (graceful degradation)."""
    ai_config = load_config().get("ai", {})
    name = ai_config.get("provider")
    if not name:
        return None
    if name == "claude":
        from lich.ai.adapters.claude_cli import ClaudeCLIAdapter
        return ClaudeCLIAdapter()
    if name == "copilot":
        from lich.ai.adapters.copilot_cli import CopilotCLIAdapter
        return CopilotCLIAdapter()
    if name == "gemini":
        from lich.ai.adapters.gemini_cli import GeminiCLIAdapter
        return GeminiCLIAdapter()
    if name == "local":
        from lich.ai.adapters.openai_compat import OpenAICompatAdapter
        return OpenAICompatAdapter(
            base_url=ai_config.get("base_url", "http://localhost:8080/v1"),
            model=ai_config.get("model", "default"))
    return None
```

- [ ] **Step 6: Register in cli.py [RE-VERIFY]**

In `cli/src/lich/cli.py`: add to the imports block:

```python
from lich.commands.config import config_app
```

and after the last `app.add_typer(...)` line:

```python
app.add_typer(config_app, name="config")
```

- [ ] **Step 7: Run to verify pass**

Run: `cd cli && python -m pytest tests/test_config_cmd.py -v`
Expected: 7 passed

- [ ] **Step 8: Commit**

```bash
git add cli/src/lich/ai/prompts/ cli/src/lich/ai/factory.py cli/src/lich/commands/config.py cli/src/lich/cli.py cli/tests/test_config_cmd.py
git commit -m "feat(ai): prompt templates, provider factory, lich config command"
```

---

## Task 17: Phase completion

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Full suite**

Run: `cd cli && python -m pytest -q`
Expected: all new tests green. Pre-existing failures: if the v1 hardening Phase 2 already shipped, the suite must be fully green; if executing before v1 Phase 2 (not recommended), the 5 known MCP/version failures are pre-existing — list them explicitly in the report, fix nothing else.

- [ ] **Step 2: Manual smoke (optional but encouraged)**

```bash
cd /tmp && rm -rf lich-smoke && mkdir lich-smoke && cd lich-smoke
mkdir -p .lich backend/internal/entities && printf 'class BaseEntity: pass\n' > backend/internal/entities/base.py
lich make entity Product --fields "name:str, price:money, seller:fk(User), status:enum(draft,active,sold)"
python -m ast backend/internal/entities/product.py && echo "entity parses OK"
```

Expected: 9 files created, `entity parses OK`

- [ ] **Step 3: Changelog**

Add at the top of `CHANGELOG.md` (create the section, keep existing content below):

```markdown
## [Unreleased - v2 Phase 1a]

### Added
- `lich make entity X --fields "..."` — full 9-file generation (entity, port, SQLAlchemy adapter, service, DTOs, FastAPI router, factory, tests, migration hint) with typed field system: str/int/float/bool/text/json/money/file/datetime/enum + fk/m2m/has_many relations
- AI adapter layer (BYOA): Claude CLI, Copilot CLI, Gemini CLI, and OpenAI-compatible local endpoints (Qwen/mlx); `asyncio.create_subprocess_exec` only
- Structured output: JSON extraction with single retry
- `lich config set/get/list` — `.lich/config.yml` (ai.provider, ai.base_url, ai.model)
```

Do NOT bump the version — Phase 1a ships together with Phase 1b (TUI) as v2.0.0-alpha1; versioning decision belongs to the human.

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: changelog for v2 phase 1a (codegen + AI adapter)"
```

- [ ] **Step 5: Report**

Report: commits list, test count before/after, any [RE-VERIFY] adaptations that were needed, and explicitly state that `lich tui`, the Concept Engine, and memory are NOT in this phase (they are Phase 1b).

---

## Spec coverage self-check (for the reviewer)

- Field type system (spec §5): Tasks 1–3 — all basic/constrained/special types; relations Task 4
- 9 generated backend files (spec §5 table): Tasks 5–11 (frontend files from the §5 table are Phase 1b, deliberately out of scope here)
- AI Provider protocol + adapters (spec §7): Tasks 13–15
- Structured output + graceful degradation (spec §7): Tasks 13, 16 (factory returns None → callers degrade)
- Config commands (spec §7): Task 16
- Prompt templates (spec Appendix A): Task 16
- D11 (no shell): Task 14 base adapter uses create_subprocess_exec exclusively

**Known scope cuts (intentional, YAGNI):**
- Frontend template files (page.tsx, Form, Table, api client) → Phase 1b with the TUI
- `--ai` enhancement flag on make → Phase 1b (needs TUI approval flow)
- Alembic auto-revision → migration hint file instead (revision IDs need alembic runtime; `lich migration create` remains the path)
- MongoDB adapter template → postgres-flavor only in Phase 1a
```
