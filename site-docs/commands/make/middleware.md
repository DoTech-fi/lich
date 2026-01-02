# lich make middleware

Create custom HTTP middleware.

## What is Middleware?

**Middleware** runs before/after every request:

- **Authentication** - Verify tokens
- **Logging** - Log requests
- **Rate limiting** - Prevent abuse
- **CORS** - Cross-origin handling

## Usage

```bash
lich make middleware <Name>
```

## Example

```bash
$ lich make middleware RequestTimer

✅ Middleware RequestTimerMiddleware created!

Files created:
  backend/api/middleware/request_timer.py
```

## Generated Code

```python
"""
RequestTimer middleware.
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestTimerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request timing.
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Before request
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # After request
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

## Register Middleware

In `backend/main.py`:

```python
from api.middleware.request_timer import RequestTimerMiddleware

app.add_middleware(RequestTimerMiddleware)
```

## Built-in Middlewares

Lich includes pre-built middlewares. Enable with:

```bash
lich middleware enable rate-limit
lich middleware enable logging
lich middleware enable security
```

## See Also

- [`lich middleware`](../middleware.md) - Enable/disable middlewares
- [Security Guide](../../best-practices/security.md)
