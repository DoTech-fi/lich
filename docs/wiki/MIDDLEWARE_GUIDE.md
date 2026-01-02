# 🔧 Middleware Guide - Complete Reference

> **Pre-built middlewares در Lich که می‌تونی enable کنی**

---

## 📦 Available Middlewares

| Middleware | کاربرد | فایل |
|------------|--------|------|
| **RateLimitMiddleware** | جلوگیری از حملات DoS | `api/middleware/rate_limit.py` |
| **RequestLoggingMiddleware** | Log همه requests | `api/middleware/logging.py` |
| **SecurityHeadersMiddleware** | OWASP security headers | `api/middleware/security.py` |
| **TimingMiddleware** | Response time headers | `api/middleware/timing.py` |

---

## 🚀 How to Enable

توی `backend/main.py`، کامنت‌ها رو بردار:

```python
# ============================================================
# OPTIONAL MIDDLEWARES - Uncomment to enable
# ============================================================

# --- Timing: Add response time headers ---
from api.middleware.timing import TimingMiddleware
app.add_middleware(TimingMiddleware)

# --- Security Headers: OWASP security headers ---
from api.middleware.security import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)

# --- Request Logging: Log all requests with timing ---
from api.middleware.logging import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)

# --- Rate Limiting: Prevent API abuse ---
from api.middleware.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

> ⚠️ **ترتیب مهمه!** اولین middleware که add می‌کنی = آخرین که اجرا می‌شه

---

## 📋 Middleware Details

### 1. RateLimitMiddleware

**کاربرد:** جلوگیری از حملات DoS و API abuse

```python
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60  # 60 request در دقیقه
)
```

**Headers اضافه می‌کنه:**
- `X-RateLimit-Limit`: حداکثر request‌ها
- `X-RateLimit-Remaining`: request‌های باقی‌مانده
- `Retry-After`: زمان انتظار (اگه limit شد)

**Response وقتی limit می‌شه:**
```json
{
    "detail": "Too many requests",
    "retry_after": 60
}
```

> ⚠️ **Production:** برای production از Redis-based rate limiting استفاده کن

---

### 2. RequestLoggingMiddleware

**کاربرد:** Log همه incoming requests با timing

```python
app.add_middleware(RequestLoggingMiddleware)
```

**Log format:**
```
[abc123de] GET /api/users - 200 (45.23ms)
[abc123de] POST /api/orders - 201 (123.45ms)
[abc123de] GET /api/products/999 - 404 (12.34ms)
```

**Headers اضافه می‌کنه:**
- `X-Request-ID`: شناسه یکتا برای هر request

**Log levels:**
- `INFO`: Status 2xx, 3xx
- `WARNING`: Status 4xx
- `ERROR`: Status 5xx

---

### 3. SecurityHeadersMiddleware

**کاربرد:** OWASP security headers

```python
app.add_middleware(SecurityHeadersMiddleware)

# Or with custom CSP:
app.add_middleware(
    SecurityHeadersMiddleware,
    content_security_policy="default-src 'self'"
)
```

**Headers اضافه می‌کنه:**
| Header | مقدار | کاربرد |
|--------|-------|--------|
| X-Content-Type-Options | nosniff | جلوگیری از MIME sniffing |
| X-Frame-Options | DENY | جلوگیری از clickjacking |
| X-XSS-Protection | 1; mode=block | محافظت XSS |
| Referrer-Policy | strict-origin-when-cross-origin | کنترل referrer |
| Strict-Transport-Security | max-age=31536000 | Force HTTPS |
| Permissions-Policy | geolocation=(), ... | محدود کردن دسترسی‌ها |

---

### 4. TimingMiddleware

**کاربرد:** Response time headers (برای monitoring)

```python
app.add_middleware(TimingMiddleware)
```

**Headers اضافه می‌کنه:**
- `X-Response-Time`: 45.23ms
- `Server-Timing`: app;dur=45.23

---

## 🔄 Middleware Order

ترتیب اجرا (از بیرون به داخل):

```
Request → Rate Limit → Logging → Security → Timing → CORS → Handler
Response ← Rate Limit ← Logging ← Security ← Timing ← CORS ← Handler
```

**پیشنهاد ترتیب در main.py:**
```python
# Add in this order (last added = first executed)
app.add_middleware(TimingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

---

## 🛠️ CLI Command

اگه Middleware custom می‌خوای:

```bash
lich make middleware MyCustom
```

فایل توی `backend/api/middleware/my_custom_middleware.py` ساخته می‌شه.

---

## 📁 File Locations

```
backend/
├── api/
│   └── middleware/
│       ├── __init__.py          ← Package docs
│       ├── rate_limit.py        ← Rate limiting
│       ├── logging.py           ← Request logging
│       ├── security.py          ← Security headers
│       └── timing.py            ← Response timing
└── main.py                      ← Enable middlewares here
```

---

## ❓ FAQ

### Q: کدوم‌ها رو برای Production فعال کنم؟
**A:** همه‌شون! ولی برای rate limiting از Redis استفاده کن:

```python
# For production, use Redis-based rate limiting:
# pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

### Q: چرا Timing رو آخر میذاریم؟
**A:** چون می‌خوایم زمان واقعی Handler رو بگیریم، نه زمان کل middlewares.

### Q: آیا Logging performance impact داره؟
**A:** بله، ولی خیلی کم. برای production می‌تونی log level رو WARNING بذاری.

---

**حالا middleware‌ها آماده استفاده‌ان!** 🔧✅
