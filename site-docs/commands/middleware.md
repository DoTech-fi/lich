# lich middleware

Enable or disable pre-built middlewares.

## Available Middlewares

| Middleware | Description |
|------------|-------------|
| `rate-limit` | Prevent API abuse |
| `logging` | Log all requests |
| `security` | Add security headers |
| `timing` | Add response time headers |

## Commands

```bash
# List all middlewares
lich middleware list

# Enable a middleware  
lich middleware enable rate-limit

# Disable a middleware
lich middleware disable rate-limit

# Enable all
lich middleware enable-all

# Disable all
lich middleware disable-all
```

## Example

```bash
$ lich middleware list

🛡️ Available Middlewares:

  ❌ rate-limit   - Rate limiting (60 req/min)
  ❌ logging      - Request logging
  ❌ security     - Security headers
  ❌ timing       - Response timing

$ lich middleware enable security
✅ Security headers middleware enabled!
```

## What Each Does

### rate-limit
Limits requests per minute per IP. Protects against abuse.

### logging
Logs every request with timing, status code, and user info.

### security
Adds OWASP security headers:
- X-Content-Type-Options
- X-Frame-Options
- Strict-Transport-Security

### timing
Adds `X-Response-Time` header to responses.
