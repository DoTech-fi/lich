# lich make middleware

ساخت HTTP middleware سفارشی.

## استفاده

```bash
lich make middleware <Name>
```

## مثال

```bash
$ lich make middleware RequestTimer

✅ Middleware RequestTimerMiddleware ساخته شد!
```

## کد تولید شده

```python
class RequestTimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # قبل از درخواست
        start_time = time.time()
        
        # پردازش درخواست
        response = await call_next(request)
        
        # بعد از درخواست
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

## ثبت Middleware

در `backend/main.py`:

```python
from api.middleware.request_timer import RequestTimerMiddleware

app.add_middleware(RequestTimerMiddleware)
```
