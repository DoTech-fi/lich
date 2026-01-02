# 🔐 Authentication vs Authorization - Complete Guide

> **فرق Authentication و Authorization چیه و Policy کجا قرار می‌گیره؟**

---

## 📚 مفاهیم پایه

| | Authentication (احراز هویت) | Authorization (مجوز دسترسی) |
|---|---|---|
| **سوال** | تو کی هستی؟ | تو چیکار می‌تونی بکنی؟ |
| **مثال** | Login با JWT/Keycloak | آیا می‌تونی این پست رو Edit کنی؟ |
| **مسئول در Lich** | `jwt_builtin` یا `keycloak` | **Policy** |
| **زمان اجرا** | اول Request | بعد از Authentication |

---

## 🔄 Request Flow

```
┌─────────────────────────────────────────────────────────┐
│                      Request Flow                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Request Incoming                                     │
│         ↓                                                │
│  2. [Middleware] ← RateLimitMiddleware, LoggingMiddleware│
│         ↓                                                │
│  3. [Authentication] ← JWT یا Keycloak                   │
│      └─→ get_current_user() → User object                │
│         ↓                                                │
│  4. [API Endpoint]                                       │
│      └─→ Policy.can_edit(user, resource) ← 🎯 اینجا!    │
│         ↓                                                │
│  5. [Service Layer]                                      │
│         ↓                                                │
│  6. [Database]                                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 Authentication Options در Lich

| Option | توضیح | Use Case |
|--------|-------|----------|
| `jwt_builtin` | JWT با FastAPI (python-jose + bcrypt) | پروژه‌های ساده، استارتاپ |
| `keycloak` | Keycloak Server - OAuth2, OIDC | Enterprise، SSO، Multi-tenant |
| `auth_proxy` | Auth از طریق Reverse Proxy | زیرساخت موجود |
| `none` | بدون Authentication | Public API |

### jwt_builtin چی داره؟
```
✅ Login/Register endpoints
✅ JWT Access + Refresh tokens
✅ Password hashing (bcrypt)
✅ get_current_user() dependency
✅ Frontend AuthContext
```

### keycloak چی داره؟
```
✅ Keycloak Docker setup
✅ setup-keycloak.sh script
✅ OIDC integration
✅ Frontend redirect to Keycloak
✅ Token validation در backend
```

---

## 🎯 Policy چیه؟

**فقط یه کلاس ساده Python!** نه Middleware، نه بخشی از Keycloak.

```python
# backend/internal/policies/post_policy.py
class PostPolicy:
    def can_view(self, user, post) -> bool:
        return post.is_published or self.can_edit(user, post)
    
    def can_edit(self, user, post) -> bool:
        return user.id == post.author_id or user.is_admin
    
    def can_delete(self, user, post) -> bool:
        return self.can_edit(user, post)
```

---

## 🧩 Policy کجا استفاده می‌شه؟

### Option 1: توی API Endpoint (رایج‌ترین)

```python
# backend/api/http/posts.py
from internal.policies.post_policy import PostPolicy

@router.put("/{post_id}")
async def update_post(
    post_id: UUID,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),  # ← Auth
):
    post = await post_service.get(post_id)
    
    # 🎯 Policy check
    if not PostPolicy().can_edit(current_user, post):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return await post_service.update(post_id, data)
```

### Option 2: توی Service Layer

```python
# backend/internal/services/post_service.py
from internal.policies.post_policy import PostPolicy

class PostService:
    async def update(self, user: User, post_id: UUID, data: dict):
        post = await self.repo.get(post_id)
        
        # 🎯 Policy check
        if not PostPolicy().can_edit(user, post):
            raise ForbiddenError("Cannot edit this post")
        
        return await self.repo.update(post_id, data)
```

---

## 🔗 رابطه Auth و Policy

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Keycloak   │     │ JWT Builtin │     │   Policy    │
│      یا     │ OR  │             │  →  │             │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ Who is      │     │ Who is      │     │ Can this    │
│ this user?  │     │ this user?  │     │ user do X?  │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ Returns:    │     │ Returns:    │     │ Returns:    │
│ User object │     │ User object │     │ True/False  │
└─────────────┘     └─────────────┘     └─────────────┘
        │                  │                   ▲
        └──────────────────┴───────────────────┘
                    User object
                    is passed to
                    Policy methods
```

---

## 📋 کجا چی انجام می‌ده؟

| Layer | جا | مسئولیت | مثال |
|-------|---|---------|------|
| **Middleware** | قبل از همه چیز | Rate limit, Logging, CORS | `RateLimitMiddleware` |
| **Auth (JWT/Keycloak)** | بعد از Middleware | کیه؟ | `get_current_user()` |
| **Policy** | توی Endpoint/Service | می‌تونه؟ | `PostPolicy().can_edit()` |

---

## ❓ سوالات متداول

### Q: Policy با Keycloak کار می‌کنه؟
**A: آره!** Keycloak فقط میگه این User کیه. Policy میگه این User می‌تونه این کار رو بکنه یا نه.

### Q: اگه Keycloak Roles داشته باشیم چی؟
**A:** می‌تونی Role رو توی Policy چک کنی:

```python
def can_edit(self, user, post) -> bool:
    # Check Keycloak role
    if "admin" in user.roles:
        return True
    # Check ownership
    return user.id == post.author_id
```

### Q: Policy چرا Middleware نیست؟
**A:** چون Middleware به Resource دسترسی نداره. مثلاً نمی‌دونه "این Post مال کیه؟"

```python
# Middleware فقط می‌دونه:
- Request headers
- User token

# Policy می‌دونه:
- User object
- Resource object (Post, Comment, etc.)
- Relationship between them
```

### Q: هر Auth Strategy نیاز به Policy داره؟

| Auth Strategy | نیاز به Policy |
|---------------|----------------|
| `jwt_builtin` | ✅ آره |
| `keycloak` | ✅ آره |
| `auth_proxy` | ✅ آره |
| `none` | ❌ نه (همه چیز public) |

---

## 🛠️ Quick Commands

```bash
# Generate a policy
lich make policy Post

# Generate auth middleware
lich make middleware Auth

# Files created:
# - backend/internal/policies/post_policy.py
# - backend/api/middleware/auth_middleware.py
```

---

## 📁 File Locations

```
backend/
├── api/
│   ├── http/
│   │   └── posts.py          ← Uses Policy here
│   └── middleware/
│       └── auth_middleware.py ← Authentication
├── internal/
│   ├── policies/
│   │   └── post_policy.py    ← Policy definition
│   └── services/
│       └── auth_deps.py      ← get_current_user()
```

---

**حالا می‌دونی Auth و Policy چطور با هم کار می‌کنن!** 🔐✅
