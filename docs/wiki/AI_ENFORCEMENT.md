# 🤖 AI Enforcement Guide - How to Make AI Follow Lich Rules

> **این فایل توضیح می‌ده چطور AI رو مجبور کنی همیشه rules فریمورک رو رعایت کنه**

---

## 🎯 روش‌های Enforce کردن Rules

### 1️⃣ System Prompt (توصیه شده)

در شروع هر session با AI، این متن رو بده:

```
You are working on a Lich Framework project. 

CRITICAL RULES:
1. Read .lich/rules/*.md files before any code generation
2. Use `lich make` commands for scaffolding
3. Follow Clean Architecture (entities → ports → adapters)
4. Never import adapters in services (use ports + DI)
5. Always update agentlog.md after changes

BEFORE generating code, ask yourself:
- Is this following Lich Architecture?
- Should I use a `lich make` command instead?
- Am I breaking dependency rules?
```

---

### 2️⃣ CLAUDE.md File (برای Cursor/Claude)

هر پروژه Lich یه `CLAUDE.md` داره که Cursor/Claude خودکار می‌خونه:

```markdown
# Project: {{ cookiecutter.project_name }}

## Tech Stack
- Backend: FastAPI with Python 3.12
- Frontend: Next.js 14 with TypeScript
- Auth: {{ cookiecutter.auth_strategy }}

## CRITICAL RULES
1. Follow Lich Architecture in .lich/rules/
2. Use `lich make <type> <Name>` for code generation
3. Never put business logic in API layer
4. Always use dependency injection

## Quick Commands
lich make entity User      # Create entity + port + adapter
lich make service User     # Create service
lich make api users        # Create API router
```

---

### 3️⃣ فولدر .lich/rules/ (در هر پروژه)

```
.lich/
└── rules/
    ├── master-prompt.md     ← Identity + role switching
    ├── backend.md           ← Architecture rules
    ├── frontend.md          ← Next.js rules
    ├── security.md          ← Security rules
    ├── lich-cli.md          ← CLI commands reference
    └── docker.md            ← Infrastructure rules
```

AI باید اول این فایل‌ها رو بخونه!

---

### 4️⃣ Inline Comments در کد

```python
# 🧙 LICH: This is an entity - NO external dependencies allowed
@dataclass
class User:
    id: UUID
    email: str
```

```python
# 🧙 LICH: Use policy for authorization, not here
@router.put("/{id}")
async def update(id: UUID, user = Depends(get_current_user)):
    # Authorization logic should be in Policy
    ...
```

---

## 📋 Checklist برای AI

هر بار که AI کد generate می‌کنه، باید این‌ها رو چک کنه:

- [ ] آیا از `lich make` استفاده کردم؟
- [ ] آیا dependency rules رعایت شده؟
- [ ] آیا entity پاک مونده (بدون framework import)؟
- [ ] آیا business logic توی service هست نه API؟
- [ ] آیا validation با Pydantic انجام شده؟
- [ ] آیا agentlog.md update شده؟

---

## 🔒 Enforcement در Different AI Tools

### Cursor (با Claude)
```
Settings → Rules for AI → Add:

Read .lich/rules/ before generating code.
Use lich make commands for scaffolding.
```

### GitHub Copilot
فایل `.github/copilot-instructions.md`:
```markdown
## Lich Framework Rules
- Use lich make for scaffolding
- Follow Clean Architecture
- Keep entities pure
```

### ChatGPT / Claude Direct
در شروع chat:
```
I'm using Lich Framework. Rules are in:
- docs/AI_RULES.md
- .lich/rules/*.md

Please read them first.
```

### Windsurf
در `.windsurfrules`:
```yaml
rules:
  - read: .lich/rules/*.md
  - use: lich make commands
```

---

## 🚨 Common AI Mistakes to Prevent

### ❌ Wrong: Import adapter in service
```python
# BAD - AI might do this
from internal.adapters.db.user_repo import UserRepository

class UserService:
    def __init__(self):
        self.repo = UserRepository()  # ❌ Direct dependency
```

### ✅ Correct: Use port injection
```python
# GOOD - What we want
from internal.ports.user_port import UserPort

class UserService:
    def __init__(self, user_port: UserPort):  # ✅ Injected
        self.user_port = user_port
```

---

### ❌ Wrong: Business logic in API
```python
# BAD
@router.post("/orders")
async def create_order(data: OrderCreate):
    # Calculate total, validate stock, create order... ❌
    total = sum(item.price * item.qty for item in data.items)
    if total < 0:
        raise HTTPException(400)
```

### ✅ Correct: Delegate to service
```python
# GOOD
@router.post("/orders")
async def create_order(data: OrderCreate):
    return await order_service.create(data)  # ✅ Delegate
```

---

## 📝 Template Prompt برای AI

این prompt رو هر بار به AI بده:

```
You are an expert in Lich Framework. Follow these rules:

## Architecture
- Entities: Pure Python, no frameworks
- Services: Business logic, use ports
- Ports: Interfaces only
- Adapters: Implement ports
- API: Thin layer, delegate to services

## CLI Commands
- lich make entity <Name>
- lich make service <Name>
- lich make api <name>
- lich make dto <Name>
- lich make factory <Name>
- lich make middleware <Name>
- lich make event <Name>
- lich make listener <Name>
- lich make job <Name>
- lich make policy <Name>

## Always
1. Use lich make for scaffolding
2. Keep entities pure
3. Use dependency injection
4. Validate with Pydantic
5. Update agentlog.md

## Never
1. Import adapters in services
2. Put business logic in API
3. Hardcode secrets
4. Skip validation
```

---

**با این روش‌ها AI همیشه rules رو رعایت می‌کنه!** 🧙✅
