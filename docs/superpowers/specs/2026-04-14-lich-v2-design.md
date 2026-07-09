# Lich v2 — AI-Powered Full-Stack App Builder

> "Lovable for code — but with real engineering behind it"

**Status:** Design approved, ready for implementation
**Version:** 2.0.0
**Date:** 2026-04-14
**Author:** Babak (DoTech)

> **Sequencing note (2026-07-10):** The v1 hardening spec (`docs/superpowers/specs/2026-07-10-lich-v1-hardening-design.md`) ships **before/parallel to** v2 Phase 0. v1 security fixes are not blocked by any v2 work.

---

## Table of Contents

1. [Vision](#1-vision)
2. [Ecosystem Context](#2-ecosystem-context)
3. [Architecture Overview](#3-architecture-overview)
4. [Phase Model: How Lich Builds Apps](#4-phase-model-how-lich-builds-apps)
5. [Feature 1: Smart Code Gen](#5-feature-1-smart-code-gen)
6. [Feature 2: TUI App](#6-feature-2-tui-app)
7. [Feature 3: AI Adapter (BYOA)](#7-feature-3-ai-adapter-byoa)
8. [Feature 4: Concept Engine](#8-feature-4-concept-engine)
9. [Feature 5: Self-Validating Generation](#9-feature-5-self-validating-generation)
10. [Feature 6: Continuous Mode](#10-feature-6-continuous-mode)
11. [Feature 7: Plugin System](#11-feature-7-plugin-system)
12. [Feature 8: Architecture Guardian](#12-feature-8-architecture-guardian)
13. [Feature 9: Zenith/FairBroker Deploy](#13-feature-9-zenithfairbroker-deploy)
14. [Feature 10: Spec Marketplace](#14-feature-10-spec-marketplace)
15. [Feature 11: Project Insights](#15-feature-11-project-insights)
16. [Feature 12: Knowledge Graph Memory](#16-feature-12-knowledge-graph-memory-obsidian-compatible)
17. [Implementation Phases](#17-implementation-phases)
18. [File Structure](#18-file-structure)
19. [Decisions Log](#19-decisions-log)
20. [Checklist](#20-checklist)

---

## 1. Vision

### What is Lich v2?

Lich v2 is a TUI-based full-stack app builder that lets developers describe what they want in natural language, then generates production-quality code with Clean Architecture — entities, services, ports, adapters, APIs, DTOs, tests, migrations, and frontend pages.

### How is it different from Lovable/Bolt/v0?

| | Lovable/Bolt/v0 | Lich v2 |
|---|---|---|
| Input | "Build me X" | "Build me X" |
| Architecture | Random, AI decides | Clean Architecture enforced |
| Code quality | AI spaghetti | Structured: entities, services, ports, adapters |
| Continuity | Starts fresh each time | Remembers project, builds on it |
| AI | Built-in, vendor locked | BYOA — user chooses their AI |
| Deploy | Vercel only | Zenith, FairBroker, or anywhere |
| Tests | Usually none | Generated and validated |
| Cost | Per-message pricing | Free tool, user pays their AI directly |

### Core Principle

Lich is NOT an AI. Lich is an orchestrator that:
1. Gathers context (deterministic)
2. Asks AI for creative decisions (one-shot)
3. Lets user approve/edit (human in the loop)
4. Generates code (deterministic, template-based)
5. Validates output (deterministic)

AI is used for understanding intent and suggesting design — NOT for writing code directly. Lich's code generators write the actual code.

---

## 2. Ecosystem Context

```
User Journey:
  pip install lich-toolkit
  lich tui  ->  Describe app  ->  Approve spec  ->  Code
  lich dev  ->  Iterate  ->  Add features  ->  Test
  lich deploy zenith  ->  Live at myapp.freezenith.com
```

### DoTech Products

| Product | Role | Tech |
|---------|------|------|
| Lich | Framework + Builder (free, open source) | Python CLI + TUI |
| Zenith (freezenith.com) | PaaS on Hetzner | Go + k8s |
| FairBroker (fairbroker.net) | VPS/Container broker | Python + FastAPI (built with Lich) |

Lich recommends Zenith for hosting but works anywhere. No vendor lock-in.

---

## 3. Architecture Overview

### System Diagram

```
                    LICH TUI (Textual)
                  Chat, entity viewer, spec approval
                           |
                    LICH CORE ENGINE
          /                |                \
   Concept Engine    Code Generator    Project Context
   (YAML workflows)  (Jinja2 templates) (Reader)
          |                |                |
   AI Adapter         Validator       Plugin Manager
   (BYOA)            (test/lint)
          |
    /     |      \
Claude  Copilot  Gemini
CLI     CLI      CLI
```

### New Module Map

```
cli/src/lich/
|-- cli.py                    # Existing -- add tui, plugin, guardian commands
|-- commands/                 # Existing commands (keep all)
|-- mcp/                      # Existing MCP server (keep all)
|
|-- tui/                      # NEW -- Textual TUI app
|   |-- app.py                # Main TUI application
|   |-- builder.py            # Backend brain (like Jarvis advisor.py)
|   |-- screens/              # TUI screens
|   +-- widgets/              # Custom widgets
|
|-- ai/                       # NEW -- AI adapter layer
|   |-- provider.py           # AIProvider protocol + factory
|   |-- adapters/
|   |   |-- claude_cli.py     # Claude CLI adapter
|   |   |-- copilot_cli.py    # Copilot CLI adapter
|   |   +-- gemini_cli.py     # Gemini CLI adapter
|   |-- prompts/              # Jinja2 prompt templates
|   +-- parser.py             # Structured output parser (JSON extraction)
|
|-- concepts/                 # NEW -- Concept engine (Jarvis pattern)
|   |-- loader.py             # Load + match concepts from YAML
|   |-- executor.py           # Execute workflow steps
|   |-- schema.py             # Concept dataclass definitions
|   +-- workflows/            # YAML concept definitions
|       |-- create_app.yaml
|       |-- add_entity.yaml
|       |-- add_feature.yaml
|       +-- deploy.yaml
|
|-- spec/                     # NEW -- Spec generator/parser
|   |-- generator.py          # Generate DDD spec from AI output
|   |-- parser.py             # Parse spec back to entities/use-cases
|   +-- schema.py             # Spec data structures
|
|-- codegen/                  # NEW -- Enhanced code generation
|   |-- engine.py             # Orchestrator: spec -> all files
|   |-- field_parser.py       # Parse field definitions
|   |-- relation_parser.py    # Parse relation definitions
|   |-- templates/            # Jinja2 code templates
|   |   |-- entity.py.j2
|   |   |-- port.py.j2
|   |   |-- adapter.py.j2
|   |   |-- service.py.j2
|   |   |-- api.py.j2
|   |   |-- dto.py.j2
|   |   |-- migration.py.j2
|   |   |-- test.py.j2
|   |   +-- frontend/
|   |       |-- page.tsx.j2
|   |       |-- form.tsx.j2
|   |       +-- table.tsx.j2
|   +-- validators/
|       |-- architecture.py   # Clean Architecture compliance
|       |-- imports.py        # Import validation
|       +-- tests.py          # Test runner
|
|-- memory/                   # NEW -- Knowledge graph memory (Feature 12)
|   |-- notes.py              # Note read/write (frontmatter + [[wikilinks]])
|   |-- index.py              # Link/frontmatter index (.lich/memory/.index.json)
|   +-- assembler.py          # Context Assembler (graph walk within token budget)
|
|-- plugins/                  # NEW -- Plugin system
|   |-- manager.py            # Install, load, list plugins
|   |-- registry.py           # Plugin discovery (PyPI entry points)
|   |-- schema.py             # lich-plugin.yaml schema
|   +-- interface.py          # LichPlugin protocol
|
+-- deploy/                   # ENHANCED -- Add Zenith + FairBroker
    |-- zenith.py             # Zenith deployment adapter
    +-- fairbroker.py         # FairBroker deployment adapter
```

### lich-core Runtime Package (Phase 0)

v2 turns Lich from a pure copy-in generator into a real framework: shared runtime code moves out of the template and into a versioned pip package.

```
core/src/lich_core/           # NEW PACKAGE -- runtime library (separate from CLI)
|-- app.py                    # create_app() factory -- inversion of control
|-- container.py              # Lightweight DI container (app-level singletons for repos/services)
|-- entities/
|   +-- base.py               # BaseEntity (id, created_at, updated_at, touch())
|-- ports/
|   +-- repository.py         # Repository port protocols
|-- services/
|   +-- base.py               # Service base class
|-- middleware/
|   |-- rate_limit.py         # Redis-backed rate limiting (fixes in-memory leak for all projects)
|   |-- security_headers.py   # OWASP headers
|   +-- csrf.py               # HMAC CSRF
|-- auth/
|   |-- jwt.py                # JWT adapter (access/refresh)
|   +-- keycloak.py           # Keycloak adapter (JWKS cached)
+-- config/
    +-- settings.py           # Pydantic settings + startup secret validation ("change-me" guard)
```

**What changes for the template:** it shrinks to a project skeleton + domain code. Generated `main.py` becomes:

```python
from lich_core import create_app

app = create_app()  # discovers routers, entities, plugins; wires DI container
```

**Why (rationale):**
- **Fixes ship to everyone at once.** Precedent: the in-memory rate-limiter leak existed independently in every copy-in project with no upgrade path. As a library, `pip install -U lich-core` fixes all of them.
- **Cheaper, safer AI codegen.** The AI (Feature 1/3) generates only thin domain-specific code instead of ~200 lines of boilerplate per entity — fewer generated lines means fewer bugs and simpler self-validation (Feature 5).
- **Real upgrade story.** The TUI can say "lich-core 2.1 available — update?", which is only possible with a runtime dependency.

**Plugin integration:** `create_app()` consumes the same `lich.plugins` entry-points group defined in Feature 7 — runtime plugin parts (middleware, startup hooks) register through lich-core, scaffold parts stay copy-in.

**API stability:** lich-core public API follows semver with a documented deprecation policy (warn one minor version before removal).

> **Decision (2026-07-10): v1 projects are grandfathered.** Existing copy-in projects (FairBroker, BabakAcademy) keep working untouched. `lich adopt --core` arrives as an *optional* migration post-v2.1. lich-core's API is designed free of v1 constraints.

---

## 4. Phase Model: How Lich Builds Apps

Inspired by Jarvis Concept-First pattern, adapted for app building.

### The 4 Phases

```
PHASE 1: Context Gathering (Deterministic, NO AI)
  - Read .lich/PROJECT_CONFIG.yaml
  - Read existing entities, services, APIs
  - Read architecture rules (.lich/rules/)
  - Read knowledge graph memory (.lich/memory/ -- Feature 12)
  - Read installed plugins
  - Package as structured context dict
         |
PHASE 2: AI Creative Work (ONE call)
  Send: user description + all context + prompt template
  AI returns STRUCTURED JSON:
    - entities: [{name, fields, relations}]
    - use_cases: [{actor, action, entity}]
    - rules: [{entity, rule}]
    - suggestions: [str]
         |
PHASE 3: Human Approval (TUI)
  - Show entities with fields -> Accept/Edit/Remove
  - Show use cases -> Accept/Edit/Remove
  - Show full spec preview
  - Final confirm
         |
PHASE 4: Code Generation (Deterministic, NO AI)
  For each entity:
    1. entity.py (dataclass + fields)
    2. port.py (repository interface)
    3. adapter.py (DB implementation)
    4. service.py (business logic + use cases)
    5. api.py (FastAPI router + CRUD)
    6. dto.py (Pydantic schemas)
    7. migration (Alembic)
    8. test.py (pytest)
    9. frontend page (Next.js)
    10. frontend form component
    11. frontend table component
  Then self-validate: lint -> test -> architecture check
```

### Token Efficiency

| Phase | AI Needed? | Deterministic? | Token Cost |
|-------|-----------|----------------|------------|
| 1. Context | No | Yes | 0 |
| 2. Creative | Yes (one-shot) | No | ~2K-5K tokens |
| 3. Approval | No | Yes (user input) | 0 |
| 4. Generation | No | Yes | 0 |

ONE AI call per operation. Jarvis pattern applied to app building.

---

## 5. Feature 1: Smart Code Gen

### Current State

`lich make entity User` generates skeleton with only id, created_at, updated_at. User must add all fields manually. Each part is a separate command.

### Target State

```bash
# Direct field specification (no AI needed)
lich make entity User --fields "name:str, email:str(unique), role:enum(admin,user)"

# AI-assisted (via TUI)
lich tui
> "create a User entity with name, email, role, and avatar"
```

### Field Type System

```
# Basic types
name:str                    -> str
age:int                     -> int
price:float                 -> float (Decimal for money)
is_active:bool              -> bool
bio:text                    -> str (Text in DB)
data:json                   -> dict

# Constrained types
email:str(unique)           -> str + unique constraint + email validation
slug:str(unique,index)      -> str + unique + index
status:enum(active,banned)  -> Enum class auto-generated
priority:enum(low,med,high) -> Enum class auto-generated

# Special types
avatar:file                 -> str (file path) + upload handler
price:money                 -> Decimal(10,2)
published_at:datetime       -> datetime (nullable)
metadata:json               -> dict (JSONB in Postgres)

# Relations
author:fk(User)             -> Foreign key to User
tags:m2m(Tag)               -> Many-to-many through table
category:fk(Category,null)  -> Nullable foreign key
comments:has_many(Comment)  -> Reverse relation (no DB column)
```

### What Gets Generated (per entity)

For `lich make entity Product --fields "name:str, price:money, seller:fk(User), tags:m2m(Tag), status:enum(draft,active,sold)"`:

| File | What |
|------|------|
| backend/internal/entities/product.py | Dataclass with all fields, enum, factory |
| backend/internal/ports/product_port.py | Repository interface with typed methods |
| backend/internal/adapters/db/product_repo.py | SQLAlchemy implementation with joins |
| backend/internal/services/product_service.py | CRUD + business logic + validation |
| backend/api/http/products.py | FastAPI router: CRUD + filter + pagination |
| backend/internal/dto/product_dto.py | Pydantic: Create, Update, Response, List |
| backend/migrations/versions/xxx_create_product.py | Alembic migration |
| backend/tests/test_product_service.py | pytest with assertions |
| backend/tests/factories/product_factory.py | Faker-based test data factory |
| apps/web/app/products/page.tsx | Next.js page with table |
| apps/web/components/products/ProductForm.tsx | Form component |
| apps/web/components/products/ProductTable.tsx | Table with sort/filter |
| apps/web/lib/api/products.ts | TypeScript API client |

### AI Enhancement (with --ai flag or in TUI)

When AI is available:
- Infers validation rules from field names (email -> email format, price -> positive)
- Suggests missing fields ("Product usually has description and image")
- Generates meaningful test assertions
- Adds field-level documentation

---

## 6. Feature 2: TUI App

### Framework: Textual (proven by Jarvis)

### TUI Screens

1. Welcome / Init Screen - description input
2. Entity Review Screen - show/edit entities with fields
3. Use Case Review Screen - show/edit behaviors
4. Spec Review Screen - full markdown preview
5. Generation Progress Screen - progress bar per file
6. Continuous Mode Screen - add features to existing project

### TUI Architecture (Builder Pattern from Jarvis)

```python
# lich/tui/builder.py -- Backend brain (no Textual dependency)

class Builder:
    """Executes concepts and orchestrates AI for app building."""

    def __init__(self, ai_provider: AIProvider):
        self.ai = ai_provider
        self.context = ProjectContext()
        self.concept_engine = ConceptEngine()

    async def create_app(self, description: str, progress_cb) -> AppSpec:
        # Phase 1: Gather context
        context = self.context.gather()
        # Phase 2: AI creative work (one-shot)
        prompt = self.build_prompt("create_app", description, context)
        ai_response = await self.ai.ask(prompt)
        spec = self.parse_spec(ai_response)
        return spec  # TUI shows this for Phase 3 approval

    async def generate_from_spec(self, spec: AppSpec, progress_cb):
        # Phase 4: Generate code from approved spec
        engine = CodeGenEngine()
        result = engine.generate(spec)
        # Self-validate
        validation = await self.validate(result)
        if not validation.passed:
            result = await self.auto_fix(result, validation)
        return result
```

---

## 7. Feature 3: AI Adapter (BYOA)

### Principle: Bring Your Own AI

Lich does not include AI. User installs their preferred AI CLI and configures Lich to use it.

### Configuration

```bash
lich config set ai.provider claude-cli    # or copilot-cli, gemini-cli
lich config set ai.model opus             # optional
```

### AI Provider Protocol

```python
class AIProvider(Protocol):
    async def ask(self, prompt: str) -> str: ...
    async def ask_structured(self, prompt: str, schema: dict) -> dict: ...
    def is_available(self) -> bool: ...
    @property
    def name(self) -> str: ...
```

### Adapters

Each adapter wraps a CLI binary:
- ClaudeCLIAdapter: calls `claude` with `-p` flag
- CopilotCLIAdapter: calls `copilot` with `-p` flag
- GeminiCLIAdapter: calls `gemini` with appropriate flags

All use `asyncio.create_subprocess_exec` (not shell exec) for safety.

### Structured Output

`ask_structured()` appends JSON schema to prompt and instructs AI to respond only with JSON. Parser extracts JSON from response (handles markdown code blocks, preamble text, etc).

### Graceful Degradation

Without AI configured:
- `lich make entity X --fields "..."` still works (deterministic)
- `lich tui` shows warning and disables AI features
- Everything else (test, deploy, lint) works normally

### Recommendation

```
For the best experience, install Claude CLI and run:
  lich config set ai.provider claude-cli
Lich works with: Claude CLI, GitHub Copilot CLI, Gemini CLI
```

---

## 8. Feature 4: Concept Engine

### Adapted from Jarvis

Jarvis: YAML concepts for diagnostic workflows.
Lich: YAML concepts for app-building workflows.

### Key Difference

| | Jarvis | Lich |
|---|---|---|
| Steps | Tool calls (gather data) | Context readers + AI call |
| AI role | Analysis (end) | Creative (middle) |
| Output | Markdown report | Spec + generated code |
| User input | None during execution | Approval between phases |

### Example: create_app.yaml

```yaml
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

### Tool Registry

```python
tool_registry = {
    # Context readers (Phase 1)
    "read_project_config": context.read_project_config,
    "read_existing_entities": context.read_existing_entities,
    "read_existing_services": context.read_existing_services,
    "read_existing_apis": context.read_existing_apis,
    "read_architecture_rules": context.read_architecture_rules,
    "list_installed_plugins": plugins.list_installed,
    # AI tools (Phase 2)
    "ai_extract_design": ai.extract_design,
    "ai_plan_feature": ai.plan_feature,
    # Code gen tools (Phase 4)
    "generate_entity": codegen.generate_entity,
    "generate_service": codegen.generate_service,
    # ...etc
}
```

---

## 9. Feature 5: Self-Validating Generation

### Flow

```
Code generated
  -> Run: lich lint (Ruff)        -> pass?
  -> Run: lich test (pytest)      -> pass?
  -> Run: architecture check      -> pass?
  -> Show to user

If ANY fails:
  -> Auto-fix attempt (max 3 rounds)
  -> If still fails -> show user with warnings
```

### Architecture Compliance Checks

1. Entities must not import from adapters
2. Services must import from ports, not adapters
3. Every entity must have a port
4. Every port must have at least one adapter
5. APIs must use DTOs, not entities directly
6. No circular imports
7. Tests must exist for every service

### Auto-Fix Strategy

1. Lint errors: `ruff --fix` (deterministic)
2. Import errors: fix based on rules (deterministic)
3. Test failures: send to AI for fix (one AI call)
4. Architecture violations: restructure (deterministic)

---

## 10. Feature 6: Continuous Mode

After init, user keeps TUI open and adds features incrementally.

```
lich tui   # Opens TUI, loads existing project

> "add email notifications when order is placed"

Phase 1: Read ALL existing code
Phase 2: AI plans additions + modifications
Phase 3: Show plan: new files, modified files
Phase 4: Generate new + patch existing
Phase 5: Self-validate
```

### Diff-Based Modifications

When modifying existing files:
- Read current file
- Generate modification as diff
- Show diff to user for approval
- Apply via AST-aware patching

---

## 11. Feature 7: Plugin System

### Plugin Structure (lich-plugin.yaml)

```yaml
name: lich-plugin-payments
version: 1.0.0
description: Stripe payment integration

provides:
  scaffold:  # Copied to project, user owns the code
    entities:
      - name: PaymentIntent
        fields: "amount:money, currency:str, status:enum(pending,succeeded,failed)"
    services:
      - name: PaymentService
        template: templates/payment_service.py.j2
    apis:
      - name: payments
        template: templates/payments_api.py.j2
    frontend:
      - type: page
        path: app/payments/page.tsx
    migrations:
      - template: templates/create_payments.py.j2

  runtime:  # Stays in package, auto-updates
    middleware:
      - name: StripeWebhookVerification
        class: lich_plugin_payments.middleware.StripeWebhookMiddleware
    cli_commands:
      - name: payments
        module: lich_plugin_payments.commands
    ai_rules:
      - path: rules/payments.md
    env_vars:
      - name: STRIPE_SECRET_KEY
        required: true

requires:
  python: ["stripe>=7.0.0"]
```

### Plugin Commands

```bash
lich plugin add payments          # Install from PyPI
lich plugin add ./my-plugin       # Install from local
lich plugin remove payments
lich plugin list
lich plugin info payments
```

### Discovery: Python entry points (standard)

```toml
# plugin pyproject.toml
[project.entry-points."lich.plugins"]
payments = "lich_plugin_payments:plugin"
```

Runtime plugin parts (middleware, startup hooks) register through `lich_core.create_app()` (see lich-core in §3); scaffold parts remain copy-in and user-owned.

---

## 12. Feature 8: Architecture Guardian

### Commands

```bash
lich guardian install    # Install pre-commit hook
lich guardian check      # Manual check
lich guardian fix        # Auto-fix violations
```

### Checks

1. Entity isolation (no adapter imports)
2. Port compliance (services use ports)
3. DTO boundary (APIs use DTOs)
4. Test coverage (new services have tests)
5. Import direction (dependencies flow inward)
6. No hardcoded secrets

---

## 13. Feature 9: Zenith/FairBroker Deploy

### Zenith

```bash
lich deploy zenith
# Check zenith CLI -> Login -> Build Docker -> Push -> Deploy -> Health check
# Output: https://myapp.freezenith.com
```

### FairBroker

```bash
lich deploy fairbroker
# Check account -> Provision container -> Deploy -> Output URL
```

---

## 14. Feature 10: Spec Marketplace

```bash
lich marketplace browse
lich marketplace search "ecom"
lich marketplace fork marketplace-pro
lich marketplace publish
```

Initially GitHub-based. Later dedicated website on freezenith.com.

---

## 15. Feature 11: Project Insights

```bash
lich insights
# Entity count, API endpoint count
# Test coverage %
# Architecture compliance score
# Dead code detection
# Security warnings
# Last deploy info
```

---

## 16. Feature 12: Knowledge Graph Memory (Obsidian-Compatible)

> "Your project's brain is an Obsidian vault."

`.lich/memory/` is a plain-markdown, Obsidian-compatible vault: notes with YAML frontmatter + `[[wikilinks]]`. No database, no embeddings, no external infra — just files that both humans and AIs can read.

### Note Types

| Type | Created by | Content |
|------|-----------|---------|
| `entity` | Auto, after every generation | Fields, relations (as wikilinks), invariants |
| `decision` | `lich memory decide "..."` or TUI | ADR-style: context, decision, consequences |
| `gotcha` | User or AI session | Discovered constraints, bugs, workarounds |
| `session` | Auto, at end of each AI work session | What was asked, what was generated/changed, why |

### Example Note

```markdown
---
type: entity
name: Product
created: 2026-07-10
fields: [name, price, status]
relations: [seller, tags]
---

# Product

Marketplace listing. Belongs to [[User]] via `seller`, tagged via [[Tag]] (m2m).
Status: draft -> active -> sold (enum).

## Invariants
- Price must be positive ([[decision-positive-prices]])

## Gotchas
- Bulk import skips validation — see [[gotcha-bulk-import]]
```

### Write Path

- Lich auto-creates/updates `entity` notes after every generation (Phase 4 of the build loop).
- `session` notes are written at the end of each TUI/AI session.
- Decisions are appended via `lich memory decide "..."` or from the TUI.

### Index

Lightweight link + frontmatter index at `.lich/memory/.index.json`, rebuilt incrementally on write. The graph = nodes (notes) + edges (wikilinks + frontmatter relations). Parsing needs only pyyaml (already a dependency) + regex for wikilinks.

### Context Assembler (the killer feature)

When the AI adapter (Feature 3) needs context for a task, it does NOT read the whole codebase. It resolves start nodes (entity names mentioned in the request), walks the graph 1–2 hops, and assembles ONLY those notes into the prompt — within a configurable token budget (default ~8K).

```python
# lich/memory/assembler.py

class ContextAssembler:
    """Graph-walk note retrieval within a token budget."""

    def __init__(self, index: MemoryIndex):
        self.index = index

    def assemble(self, task: str, budget_tokens: int = 8_000) -> str:
        start_nodes = self.index.resolve_mentions(task)   # "add reviews to Product" -> [Product]
        notes = self.index.walk(start_nodes, max_hops=2)  # Product -> User, Tag, decisions
        return self.pack(notes, budget_tokens)            # highest-relevance first, stop at budget
```

This is what makes BYOA work with small-context local models (e.g. Qwen3-32B with a 32K window): one graph walk replaces reading dozens of source files.

### Human-Facing Bonus

Open `.lich/memory/` directly in Obsidian: the project's entities, decisions, and history appear as a browsable graph. No competitor has this.

### Integration

- **Concept Engine (Feature 4):** workflow steps can reference memory notes as context sources (`read_memory` tool in the registry).
- **TUI (Feature 2):** Memory screen — browse/search notes.
- **CLI:** `lich memory show <note>`, `lich memory search <term>`, `lich memory decide "<text>"`, `lich memory rebuild-index`.

### YAGNI Boundaries

- **No embeddings/vector search in v2** — link-graph traversal is deterministic, free, and sufficient for structured project knowledge. Revisit for v3 if fuzzy recall is needed.
- **No cross-project shared memory in v2** — BabakOS-style shared layer is a v3 candidate.

---

## 17. Implementation Phases

### Phase 0: lich-core Extraction

Goal: shared runtime moves from template copy-in to a versioned `lich-core` pip package (see §3). Runs after/parallel to the v1 hardening plan — v1 security fixes ship first.

| # | Task | Priority | Depends On |
|---|------|----------|------------|
| 0.1 | Create `core/` package skeleton (lich-core: pyproject, src layout, publish workflow) | P0 | - |
| 0.2 | Extract BaseEntity + entity helpers from template | P0 | 0.1 |
| 0.3 | Extract repository ports + service base | P0 | 0.2 |
| 0.4 | Extract middleware collection (Redis-backed rate limit, security headers, CSRF) | P0 | 0.1 |
| 0.5 | Extract pydantic settings + startup secret validation ("change-me" guard) | P0 | 0.1 |
| 0.6 | Extract JWT + Keycloak auth adapters | P0 | 0.3, 0.5 |
| 0.7 | `create_app()` factory + DI container (app-level singletons for repos/services) | P0 | 0.3–0.6 |
| 0.8 | Plugin hooks: `create_app()` consumes `lich.plugins` entry points (Feature 7) | P1 | 0.7 |
| 0.9 | Template shrink: skeleton + `from lich_core import create_app` + domain code only | P0 | 0.7 |
| 0.10 | Golden-path e2e green with lich-core template (reuse v1 Phase 4 harness) | P0 | 0.9 |
| 0.11 | Semver + deprecation policy doc for lich-core public API | P1 | 0.1 |

Acceptance Criteria Phase 0:
- [ ] `pip install lich-core` works; template's generated project boots via `create_app()`
- [ ] Generated project contains zero copied middleware/auth/config boilerplate
- [ ] Golden-path e2e passes with the shrunken template
- [ ] v1 copy-in projects untouched and still working (grandfathered — see Decisions Log)

### Phase 1: Foundation (Current Sprint)

Goal: Smart code gen + basic TUI + AI adapter

| # | Task | Priority | Depends On |
|---|------|----------|------------|
| 1.1 | Field parser (name:str, email:str(unique) syntax) | P0 | - |
| 1.2 | Relation parser (author:fk(User), tags:m2m(Tag)) | P0 | 1.1 |
| 1.3 | Jinja2 code templates (entity, port, adapter, service, API, DTO, test) | P0 | 1.1 |
| 1.4 | CodeGen engine (orchestrate template rendering) | P0 | 1.3 |
| 1.5 | Upgrade lich make entity to accept --fields | P0 | 1.4 |
| 1.6 | Upgrade lich make entity to generate ALL files | P0 | 1.4 |
| 1.7 | AI Provider protocol + Claude CLI adapter | P0 | - |
| 1.8 | AI Provider: Copilot CLI adapter | P1 | 1.7 |
| 1.9 | AI Provider: Gemini CLI adapter | P2 | 1.7 |
| 1.10 | Structured output parser (JSON from AI response) | P0 | 1.7 |
| 1.11 | Basic TUI: welcome screen + description input | P0 | - |
| 1.12 | TUI: entity review screen | P0 | 1.11 |
| 1.13 | TUI: spec review screen | P1 | 1.12 |
| 1.14 | TUI: generation progress screen | P1 | 1.13 |
| 1.15 | Concept engine: YAML loader + executor | P0 | - |
| 1.16 | Concept: create_app workflow | P0 | 1.15, 1.7 |
| 1.17 | Prompt templates (Jinja2) for AI | P0 | 1.7 |
| 1.18 | Frontend code templates (Next.js) | P1 | 1.3 |
| 1.19 | Migration template generation | P1 | 1.1 |
| 1.20 | lich config set ai.provider command | P0 | 1.7 |
| 1.21 | Memory: note writer (frontmatter + wikilinks) + `.lich/memory/` layout | P1 | - |
| 1.22 | Memory: auto-generate entity notes after codegen | P1 | 1.21, 1.4 |
| 1.23 | Memory: `lich memory` CLI (show, search, decide, rebuild-index) | P1 | 1.21 |

Acceptance Criteria Phase 1:
- [ ] `lich make entity User --fields "name:str, email:str(unique)"` generates ALL 9+ backend files
- [ ] `lich tui` opens, user describes app, entities shown, user approves, code generated
- [ ] Works with Claude CLI, Copilot CLI, or no AI (graceful degradation)
- [ ] Generated code passes `lich lint` and `lich test`
- [ ] After generation, `.lich/memory/` contains entity notes and opens cleanly as an Obsidian vault

### Phase 2: Quality + Continuous

Goal: Self-validation, continuous mode, architecture guardian

| # | Task | Priority | Depends On |
|---|------|----------|------------|
| 2.1 | Architecture validator (import direction checker) | P0 | Phase 1 |
| 2.2 | Self-validation loop (lint, test, arch check) | P0 | 2.1 |
| 2.3 | Auto-fix: lint errors (ruff --fix) | P0 | 2.2 |
| 2.4 | Auto-fix: import errors (rule-based) | P1 | 2.2 |
| 2.5 | Continuous mode: TUI stays open, add features | P0 | Phase 1 |
| 2.6 | Concept: add_feature workflow | P0 | 2.5 |
| 2.7 | Concept: add_entity workflow | P0 | 2.5 |
| 2.8 | Diff-based file modification | P0 | 2.5 |
| 2.9 | Architecture guardian pre-commit hook | P1 | 2.1 |
| 2.10 | Project insights command | P2 | 2.1 |
| 2.11 | Memory: link/frontmatter index (`.index.json`, incremental rebuild) | P0 | Phase 1 |
| 2.12 | Memory: Context Assembler (graph walk, token budget) wired into AI adapter | P0 | 2.11 |
| 2.13 | Memory: session notes written at end of each AI session | P1 | 2.11 |
| 2.14 | TUI: Memory screen (browse/search notes) | P2 | 2.11 |

Acceptance Criteria Phase 2:
- [ ] Generated code always passes validation before showing to user
- [ ] User can say "add payments" to existing project and it works
- [ ] Pre-commit hook catches architecture violations
- [ ] `lich insights` shows project health
- [ ] `add_feature` context is assembled from the memory graph within the token budget (no whole-codebase reads)

### Phase 3: Plugin System

Goal: Plugin infrastructure + first plugins

| # | Task | Priority | Depends On |
|---|------|----------|------------|
| 3.1 | Plugin interface (LichPlugin protocol) | P0 | - |
| 3.2 | Plugin discovery (entry points) | P0 | 3.1 |
| 3.3 | Plugin manager (install, remove, list) | P0 | 3.2 |
| 3.4 | Scaffold injection | P0 | 3.3 |
| 3.5 | Runtime injection (middleware, CLI) | P0 | 3.3 |
| 3.6 | lich-plugin.yaml schema + validation | P0 | 3.1 |
| 3.7 | First plugin: lich-plugin-auth | P1 | 3.6 |
| 3.8 | Second plugin: lich-plugin-notifications | P2 | 3.6 |
| 3.9 | Plugin template: lich make plugin | P1 | 3.6 |
| 3.10 | Concept: add_plugin workflow | P1 | 3.3 |

Acceptance Criteria Phase 3:
- [ ] `lich plugin add auth` installs and scaffolds
- [ ] Plugin CLI commands auto-register
- [ ] Plugin middleware auto-activates
- [ ] `lich make plugin my-plugin` creates scaffold

### Phase 4: Deploy + Marketplace

Goal: Zenith/FairBroker deploy + spec sharing

| # | Task | Priority | Depends On |
|---|------|----------|------------|
| 4.1 | Zenith deploy adapter | P0 | - |
| 4.2 | FairBroker deploy adapter | P1 | - |
| 4.3 | lich deploy zenith command | P0 | 4.1 |
| 4.4 | lich deploy fairbroker command | P1 | 4.2 |
| 4.5 | Spec export (lich spec export) | P1 | - |
| 4.6 | Spec import (lich spec import) | P1 | 4.5 |
| 4.7 | Marketplace browse/search | P2 | 4.5 |
| 4.8 | Marketplace publish | P2 | 4.7 |

Acceptance Criteria Phase 4:
- [ ] `lich deploy zenith` deploys to freezenith.com
- [ ] `lich spec export` creates shareable spec
- [ ] `lich marketplace browse` shows community specs

---

## 17. File Structure

### New Dependencies (add to pyproject.toml)

```toml
dependencies = [
    # Existing
    "typer>=0.9.0",
    "cookiecutter>=2.5.0",
    "rich>=13.0.0",
    "pyyaml>=6.0",
    "requests>=2.28.0",
    "mcp>=0.1.0",
    # New
    "textual>=0.50.0",      # TUI framework
    "jinja2>=3.1.0",        # Code templates
]
```

### New CLI Commands

```python
# cli.py additions:
app.command(name="tui")(tui.launch_tui)
app.add_typer(plugin_app, name="plugin")
app.add_typer(guardian_app, name="guardian")
app.command(name="insights")(insights.show_insights)
```

---

## 18. Decisions Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| D1 | BYOA (no built-in AI) | No vendor lock-in, user uses own subscription | 2026-04-14 |
| D2 | Concept-First from Jarvis | Proven: deterministic + one-shot AI = 90% token savings | 2026-04-14 |
| D3 | Textual for TUI | Proven by Jarvis, Python-native | 2026-04-14 |
| D4 | Hybrid plugin (scaffold + runtime) | Scaffold for customizable code, runtime for internals | 2026-04-14 |
| D5 | 4-Phase model | Separates deterministic from creative, minimizes AI calls | 2026-04-14 |
| D6 | AI returns structured JSON | Prevents parsing fragility | 2026-04-14 |
| D7 | PyPI entry points for plugins | Standard Python mechanism | 2026-04-14 |
| D8 | Recommend Claude Opus | Best structured output, but support all CLIs | 2026-04-14 |
| D9 | Jinja2 for code templates | Industry standard, clean separation | 2026-04-14 |
| D10 | Phase 1: Smart Code Gen + TUI | Highest daily-use impact | 2026-04-14 |
| D11 | asyncio.create_subprocess_exec for AI calls | Safe from shell injection (no shell=True) | 2026-04-14 |
| D12 | Phase 0: extract `lich-core` runtime package before v2 features | Fixes ship to all projects at once; AI generates less boilerplate; enables real upgrade story | 2026-07-10 |
| D13 | v1 copy-in projects grandfathered; `lich adopt --core` optional, post-v2.1 | lich-core API designed free of v1 constraints; FairBroker/BabakAcademy untouched | 2026-07-10 |
| D14 | Knowledge graph memory scope = project + session (Feature 12) | Structural knowledge AND session history make any BYOA model instantly productive | 2026-07-10 |
| D15 | Memory = plain markdown + wikilinks, Obsidian-compatible; no embeddings in v2 | Zero infra, deterministic retrieval, git-diffable, human-usable as a vault; vector search deferred to v3 | 2026-07-10 |
| D16 | v1 hardening (separate spec) ships before/parallel to Phase 0 | Public PyPI security holes can't wait on v2 | 2026-07-10 |

---

## 19. Checklist

### Per-Phase Completion Criteria

#### Phase 1 Readiness
- [ ] Field parser handles: str, int, float, bool, text, json, money, file, datetime, enum
- [ ] Relation parser handles: fk(), m2m(), has_many()
- [ ] All 9 backend Jinja2 templates render correctly
- [ ] All 3 frontend Jinja2 templates render correctly
- [ ] `lich make entity X --fields "..."` generates all files in one command
- [ ] AI Provider protocol defined with ask() and ask_structured()
- [ ] Claude CLI adapter works (tested with real CLI)
- [ ] Copilot CLI adapter works
- [ ] Structured output parser extracts JSON from AI response
- [ ] TUI launches with `lich tui`
- [ ] TUI: description input -> entity review -> approve -> generate
- [ ] Concept engine loads YAML and executes workflows
- [ ] create_app concept works end-to-end
- [ ] `lich config set ai.provider` works
- [ ] Generated code passes `lich lint`
- [ ] Generated code passes `lich test`
- [ ] Works without AI (graceful degradation with --fields flag)
- [ ] All existing CLI commands still work (no regression)

#### Phase 2 Readiness
- [ ] Architecture validator catches: wrong imports, missing ports, entity in API
- [ ] Self-validation loop runs after every generation
- [ ] Auto-fix resolves lint errors automatically
- [ ] Continuous mode: TUI opens existing project
- [ ] add_feature concept works (generates new + modifies existing)
- [ ] Diff-based modification shows changes before applying
- [ ] Pre-commit hook installable via `lich guardian install`

#### Phase 3 Readiness
- [ ] `lich plugin add X` installs from PyPI
- [ ] `lich plugin add ./local` installs from directory
- [ ] Scaffold files copied correctly
- [ ] Runtime middleware/commands register automatically
- [ ] At least 1 plugin published
- [ ] `lich make plugin` scaffolds plugin project

#### Phase 4 Readiness
- [ ] `lich deploy zenith` works end-to-end
- [ ] `lich spec export/import` round-trips correctly
- [ ] Marketplace browse shows community specs

### Cross-Phase Invariants (ALWAYS TRUE)
- [ ] All existing `lich` commands work (no regression)
- [ ] `lich make entity X` (without --fields) still works as before
- [ ] MCP server still works (backward compatible)
- [ ] No AI required for basic operations
- [ ] Generated code follows Clean Architecture
- [ ] All tests pass: `cd cli && pytest`

---

## Appendix A: Prompt Templates

### extract_entities.j2

```
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
      "fields": [{"name": "...", "type": "...", "constraints": [...]}],
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

### plan_feature.j2

```
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
  "new_entities": [...],
  "new_services": [...],
  "new_apis": [...],
  "modifications": [
    {"file": "...", "method": "...", "change": "...", "code_hint": "..."}
  ],
  "new_env_vars": [{"name": "...", "description": "..."}],
  "new_dependencies": ["package>=1.0.0"]
}
```

---

## Appendix B: Reference Implementation (Jarvis)

Jarvis at `/Users/babak/codes/DoTech/jarvis/kubeManager/kubemanager/` provides proven patterns:

| Pattern | Jarvis File | Lich Equivalent |
|---------|-------------|-----------------|
| TUI app | src/jarvis/tui/app.py | lich/tui/app.py |
| Backend brain | src/jarvis/tui/advisor.py | lich/tui/builder.py |
| Concept loading | src/jarvis/internal/concepts/concept_loader.py | lich/concepts/loader.py |
| AI invocation | advisor.py:_invoke_copilot() | ai/adapters/claude_cli.py |
| Tool registry | advisor.py:_get_tool_registry() | concepts/executor.py |
| Prompt building | advisor.py:_build_prompt() | ai/prompts/*.j2 |
| Workflow execution | advisor.py:execute_concept() | concepts/executor.py |
