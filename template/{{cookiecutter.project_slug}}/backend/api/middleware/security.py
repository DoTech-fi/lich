"""
Security Headers Middleware - Add security headers to responses.

To enable, add to main.py:
    from api.middleware.security import SecurityHeadersMiddleware
    app.add_middleware(SecurityHeadersMiddleware)
"""
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    
    Headers added:
        - X-Content-Type-Options: nosniff
        - X-Frame-Options: DENY
        - X-XSS-Protection: 1; mode=block
        - Strict-Transport-Security (HTTPS only)
        - Content-Security-Policy (optional)
        
    Usage:
        app.add_middleware(SecurityHeadersMiddleware)
        
        # Or with custom CSP:
        app.add_middleware(
            SecurityHeadersMiddleware,
            content_security_policy="default-src 'self'"
        )
    """
    
    def __init__(
        self,
        app,
        content_security_policy: str = None,
        hsts_max_age: int = 31536000,  # 1 year
    ):
        super().__init__(app)
        self.csp = content_security_policy
        self.hsts_max_age = hsts_max_age
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection (legacy, but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS - only add for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains"
            )
        
        # Content Security Policy (optional)
        if self.csp:
            response.headers["Content-Security-Policy"] = self.csp
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        
        return response
