# v2 Cross-Plan Interface Contracts (FROZEN)

> **Any plan task that contradicts this file is WRONG — fix the task, not the contract.**
> **Changes to this file require explicit human approval (Babak).**
>
> Purpose: the four v2 plans were authored in parallel. Every interface that crosses a plan
> boundary is pinned here so executors never have to guess which version wins.
> Source of each contract is noted as (plan, task).

## C1. `AIProvider` protocol — `cli/src/lich/ai/provider.py`
Source: P1a Task 13. Consumers: P1a adapters/factory, P1b Task 9 (tool registry), P2–4 Task 2.4 Step 5.

```python
class AIProviderError(Exception): ...

@runtime_checkable
class AIProvider(Protocol):
    @property
    def name(self) -> str: ...
    def is_available(self) -> bool: ...
    async def ask(self, prompt: str) -> str: ...
```

Structured output is a FREE FUNCTION, not a protocol method (P1a Task 13, `ai/structured.py`):

```python
async def ask_structured(provider: AIProvider, prompt: str, schema: dict) -> dict
```

All subprocess invocations inside adapters: `asyncio.create_subprocess_exec` only (spec D11).

## C2. `Note` model + vault layout — `cli/src/lich/memory/notes.py`
Source: P1b Task 1. Consumers: P1b index/writer/CLI, P2–4 Tasks 2.3/2.4/2.6.

```python
NOTE_TYPES = ("entity", "decision", "gotcha", "session")

@dataclass
class Note:
    name: str
    type: str          # must be in NOTE_TYPES
    body: str
    meta: dict = field(default_factory=dict)   # extra frontmatter keys
    # properties: links -> list[str] (parsed [[wikilinks]]), filename -> f"{name}.md"

def read_note(path: Path) -> Note          # raises ValueError on bad frontmatter
def write_note(note: Note, directory: Path) -> Path
```

**There is exactly ONE Note class in the codebase — this one.** (P2–4 Task 2.3's original
draft defined a second local `Note` in index.py; that is superseded — see C3.)

Vault location — `_vault_dir(root)` (P1b Task 4, `commands/memory.py`):
- `.lich` is a directory → vault = `.lich/memory/`
- `.lich` is a legacy file marker → vault = `.lich-memory/`

## C3. `MemoryIndex` — `cli/src/lich/memory/index.py` (RECONCILED)
Source: P1b Task 2 (canonical base, ships first) + P2–4 Task 2.3 (extends). This section
resolves EXECUTION-GUIDE Known Conflict 1.

```python
INDEX_FILENAME = ".index.json"

class MemoryIndex:
    def __init__(self, vault_dir: Path): ...
    vault_dir: Path
    nodes: dict[str, dict]            # name -> {"type": str, "path": str, "links": list[str]}
    edges: set[tuple[str, str]]       # NORMALIZED TO set (P1b ships list; P2-4 Task 2.3 migrates to set)

    @property
    def path(self) -> Path            # vault_dir / INDEX_FILENAME

    # P1b (canonical, ships in Phase 1b):
    def rebuild(self) -> None         # full re-index + save()
    def update_note(self, name: str) -> None
    def neighbors(self, name: str) -> set[str]
    def save(self) -> None            # writes self.path; edges serialized as sorted lists
    def load(self) -> None            # instance method, reloads self from self.path

    # P2-4 Task 2.3 ADDS (extends the file, never recreates it):
    @classmethod
    def build(cls, vault_dir: Path) -> "MemoryIndex"    # = cls(vault_dir) + rebuild()
    def resolve_mentions(self, task: str) -> list[str]  # sorted note names mentioned in task text
    def walk(self, start: list[str], max_hops: int = 2) -> list[str]  # note NAMES, BFS order, start first
```

Resolution decisions (binding):
1. **No `@classmethod load(path)`** — it would name-clash with P1b's instance `load()`.
   Factory pattern for loading: `idx = MemoryIndex(vault_dir); idx.load()`.
2. **`walk()` returns note NAMES** (`list[str]`), not Note objects. Callers needing bodies do:
   `read_note(idx.vault_dir / idx.nodes[name]["path"])` (see C2).
3. **`edges` is `set[tuple[str, str]]`** after P2–4 Task 2.3; `save()` keeps the on-disk
   format deterministic (sorted). P1b's `.index.json` schema is unchanged and remains readable.
4. `save(path)` / positional-path variants are dropped; the index is always vault-anchored.

## C4. Codegen specs — `cli/src/lich/codegen/spec.py`
Source: P1a Task 1. Consumers: P1a parsers/templates/generator, P2–4 Task 2.2 pipeline.

```python
@dataclass
class FieldSpec:
    name: str
    type: str                          # key into TYPE_MAP ("enum" uses enum_values)
    unique: bool = False
    index: bool = False
    nullable: bool = False
    enum_values: list[str] = field(default_factory=list)
    # property: enum_class -> str  (e.g. "status" -> "Status")

@dataclass
class RelationSpec:
    name: str                          # e.g. "seller"
    kind: str                          # "fk" | "m2m" | "has_many"
    target: str                        # e.g. "User"
    nullable: bool = False
    # property: target_snake -> str

@dataclass
class EntitySpec:
    name: str
    fields: list[FieldSpec]
    relations: list[RelationSpec]
    # properties: pascal -> str, snake -> str

TYPE_MAP: dict[str, TypeInfo]  # keys: str,int,float,bool,text,json,money,file,datetime,enum
# TypeInfo fields: python, default, sqlalchemy, pydantic, faker
```

Generator entry point (P1a Task 11, `codegen/generator.py`):

```python
class GeneratorError(Exception): ...
def generate_entity(name: str, fields_source: str, force: bool = False) -> list[Path]
```

P2–4 Task 2.2's `ValidationPipeline` wraps `generate_entity` — it must not change this signature.

## C5. lich-core — `core/src/lich_core/`
Source: P0 Tasks 2–12. Consumers: template (P0 Task 13), future `lich adopt --core`.

```python
# lich_core.errors
class LichConfigError(RuntimeError): ...      # NOT an AppException subclass

# lich_core.config
class LichSettings(BaseSettings):
    def validate_secrets(self) -> None        # raises LichConfigError in production if any
                                              # secret contains "change-me"

# lich_core.container
class Container:
    def register(self, key: Type[T], instance: T) -> None
    def register_factory(self, key: Type[T], factory: Callable[[], T]) -> None
    def resolve(self, key: Type[T]) -> T

# lich_core.app
def create_app(
    settings: Optional[LichSettings] = None,
    *,
    routers: Sequence = (),
    container: Optional[Container] = None,
    on_startup: Sequence[StartupHook] = (),
    on_shutdown: Sequence[StartupHook] = (),
    middleware: Optional[MiddlewareConfig] = None,
    discover_plugins: bool = True,
    title: Optional[str] = None,
) -> FastAPI
# create_app calls settings.validate_secrets() at lifespan startup (crash-at-boot, never per-request)

# lich_core.plugins — entry-points group "lich.plugins"
class LichPlugin(Protocol):
    def register(self, app: FastAPI, container: Container) -> None
# broken plugin = logged + skipped, never fatal
```

Versioning (decision 2026-07-10): **lich-core starts at `0.1.0`** and reaches `1.0.0` at v2 GA.
The lich CLI v2 releases as `2.0.0-alpha.N`. (See spec Decisions Log D17.)

## C6. Concepts — `cli/src/lich/concepts/`
Source: P1b Tasks 6–9. Consumers: P2–4 Task 2.5 (`add_feature.yaml`, `add_entity.yaml`).

```python
# registry (P1b Task 9)
def build_tool_registry(project_root: Path, ai_provider: AIProvider | None = None) -> dict[str, Any]
# registry keys are step tool names; ai steps degrade gracefully when ai_provider is None

# executor context: step outputs stored under their step name; ${step.key} resolution
# supports nested dict access (P1b Task 8). New workflow YAMLs MUST follow the
# create_app.yaml step schema fixture from P1b Task 6 exactly.
```

## C7. Patcher — `cli/src/lich/codegen/patcher.py`
Source: P2–4 Task 2.5 (binding interface declared in-plan):

```python
class PatchError(Exception): ...
def preview(path: Path, diff: str) -> str      # patched text, no write
def apply(path: Path, diff: str) -> None       # atomic write or PatchError
```
