"""
Timing Middleware - Add response timing headers.

To enable, add to main.py:
    from api.middleware.timing import TimingMiddleware
    app.add_middleware(TimingMiddleware)
"""
import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Add response timing information to headers.
    
    Headers added:
        - X-Response-Time: {time}ms
        - Server-Timing: app;dur={time}
        
    Usage:
        app.add_middleware(TimingMiddleware)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        
        # Add timing headers
        response.headers["X-Response-Time"] = f"{process_time:.2f}ms"
        response.headers["Server-Timing"] = f"app;dur={process_time:.2f}"
        
        return response
