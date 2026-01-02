# راهنمای امنیت

بهترین شیوه‌های امنیتی برای اپلیکیشن‌های لیچ.

## چک‌لیست سریع

- [ ] فعال کردن middleware هدرهای امنیتی
- [ ] استفاده از HTTPS در تولید
- [ ] ذخیره secrets در متغیرهای محیطی
- [ ] اعتبارسنجی همه ورودی‌ها با Pydantic
- [ ] فعال کردن rate limiting
- [ ] استفاده از کوئری‌های parameterized

## فعال کردن Middleware امنیتی

```bash
lich middleware enable security
lich middleware enable rate-limit
```

## متغیرهای محیطی

**هرگز** secrets را hardcode نکنید:

```python
# ❌ بد
JWT_SECRET = "my-secret-key"

# ✅ خوب
import os
JWT_SECRET = os.environ.get("JWT_SECRET")
```

## اعتبارسنجی ورودی

همیشه از DTOهای Pydantic استفاده کنید:

```python
from pydantic import BaseModel, Field, EmailStr

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
```

## جلوگیری از SQL Injection

از ORM یا کوئری‌های parameterized استفاده کنید:

```python
# ❌ بد
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ خوب
query = select(User).where(User.email == email)
```

## Authorization با Policies

```python
from internal.policies.article_policy import ArticlePolicy

if not ArticlePolicy().can_edit(user, article):
    raise HTTPException(403, "Forbidden")
```

## تنظیم CORS

در `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # نه "*"
    allow_credentials=True,
)
```
