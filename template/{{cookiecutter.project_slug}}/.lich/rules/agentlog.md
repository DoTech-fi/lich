# Agent Log Rules

> **MANDATORY**: Always update `agentlog.md` - no exceptions.

## Purpose

`agentlog.md` is the canonical, human-readable change log that documents project evolution.

## Location

Always create/update `agentlog.md` in the project root.

## When to Update

Update `agentlog.md` EVERY time you:

- ✅ Add new code (entity, service, component, etc.)
- ✅ Modify existing code
- ✅ Change architecture
- ✅ Update configuration
- ✅ Modify infrastructure
- ✅ Add/update tests
- ✅ Update documentation

## Entry Format

```markdown
## YYYY-MM-DDTHH:MM:SS - Brief Title

**What**: What was changed (files, features, fixes)
**Why**: Why the change was needed
**Mode**: backend/frontend/infra/fullstack
```

## Example Entries

```markdown
## 2024-01-15T14:30:00 - Added User Profile Feature

**What**: Created Profile entity, service, API endpoints, and frontend page
**Why**: User requested profile editing capability
**Mode**: fullstack

---

## 2024-01-15T10:00:00 - Fixed Authentication Bug

**What**: Fixed token refresh logic in auth_deps.py
**Why**: Users were getting logged out unexpectedly
**Mode**: backend
```

## Rules

### DO ✅
- Be concise but complete
- Include timestamp
- Mention affected files/areas
- Explain the reasoning ("why")

### DON'T ❌
- Skip entries (every change needs logging)
- Write vague descriptions
- Forget timestamps
- Leave out the "why"

## Task Completion Rule

**No task is complete until:**
1. Code is generated
2. Documentation is updated
3. `agentlog.md` is updated

If agentlog is missing → Output is invalid.

---

> **Mantra**: Document every change, always.
