"""
Request Logging Middleware - Log all incoming requests.

To enable, add to main.py:
    from api.middleware.logging import RequestLoggingMiddleware
    app.add_middleware(RequestLoggingMiddleware)
"""
import time
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
{%- if cookiecutter.use_structured_logging == 'yes' %}
from pkg.logger.setup import get_logger

logger = get_logger(__name__)
{%- else %}
import logging

logger = logging.getLogger(__name__)
{%- endif %}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all incoming HTTP requests with timing.
    
    Logs:
        - Request ID
        - Method and path
        - Client IP
        - Response status code
        - Response time in ms
        
    Usage:
        app.add_middleware(RequestLoggingMiddleware)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Start timer
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"[{request_id}] {method} {path} - ERROR after {process_time:.2f}ms",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "client_ip": client_ip,
                    "error": str(e),
                    "duration_ms": process_time,
                }
            )
            raise
        
        # Calculate response time
        process_time = (time.time() - start_time) * 1000
        
        # Log request
        log_message = f"[{request_id}] {method} {path} - {response.status_code} ({process_time:.2f}ms)"
        
        if response.status_code >= 500:
            logger.error(log_message)
        elif response.status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
