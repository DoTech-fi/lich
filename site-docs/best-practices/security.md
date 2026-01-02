# Security Guide

Security best practices for Lich applications.

## Quick Checklist

- [ ] Enable security headers middleware
- [ ] Use HTTPS in production
- [ ] Store secrets in environment variables
- [ ] Validate all input with Pydantic
- [ ] Enable rate limiting
- [ ] Use parameterized queries

## Enable Security Middleware

```bash
lich middleware enable security
lich middleware enable rate-limit
```

## Environment Variables

**Never** hardcode secrets:

```python
# ❌ Bad
JWT_SECRET = "my-secret-key"

# ✅ Good
import os
JWT_SECRET = os.environ.get("JWT_SECRET")
```

## Input Validation

Always use Pydantic DTOs:

```python
from pydantic import BaseModel, Field, EmailStr

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
```

## SQL Injection Prevention

Use ORM or parameterized queries:

```python
# ❌ Bad
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ Good
query = select(User).where(User.email == email)
```

## Authentication

Use the built-in auth or Keycloak:

```python
from api.middleware.auth import get_current_user

@router.get("/profile")
async def profile(user: User = Depends(get_current_user)):
    return user
```

## Authorization with Policies

```python
from internal.policies.article_policy import ArticlePolicy

if not ArticlePolicy().can_edit(user, article):
    raise HTTPException(403, "Forbidden")
```

## CORS Configuration

In `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```
