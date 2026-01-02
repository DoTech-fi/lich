# AI Integration

How to use AI coding assistants effectively with Lich projects.

## Built-in AI Rules

Every Lich project includes AI rules in `.lich/rules/`:

```
.lich/rules/
├── backend.md       # Backend patterns
├── frontend.md      # Frontend patterns
├── lich-cli.md      # CLI commands
└── master-prompt.md # Combined rules
```

## Why AI Rules?

| Problem | Solution |
|---------|----------|
| AI creates wrong structure | Rules define correct locations |
| AI uses wrong patterns | Rules enforce architecture |
| AI forgets conventions | Rules remind every time |

## Using with Claude

Add to system prompt or CLAUDE.md:

```markdown
You are working on a Lich Framework project.
Read `.lich/rules/master-prompt.md` before making changes.
```

## Using with Cursor

Create `.cursorrules`:

```
When working on this project:
1. Follow Clean Architecture
2. Entities go in backend/internal/entities/
3. Services go in backend/internal/services/
4. Use `lich make` commands for new files
```

## Using with Copilot

Add inline comments to guide:

```python
# This file follows Lich architecture patterns
# Entities must not import framework code
# Domain logic goes in entity methods

@dataclass
class Order:
    ...
```

## Common AI Mistakes

| Mistake | Rule to Prevent |
|---------|-----------------|
| Import SQLAlchemy in entities | "Entities must be pure Python" |
| Business logic in router | "Routers call services, not logic" |
| Direct database access | "Use repository ports" |

## Example AI Prompt

> "Create a new Product feature with entity, service, API, and DTOs following the Lich architecture in `.lich/rules/`."
