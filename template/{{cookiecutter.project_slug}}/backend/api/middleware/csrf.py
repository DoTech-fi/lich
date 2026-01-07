"""
CSRF Protection Middleware - Protect against Cross-Site Request Forgery.

To enable, add to main.py:
    from api.middleware.csrf import CSRFMiddleware
    app.add_middleware(CSRFMiddleware, secret_key=settings.secret_key)
"""
import secrets
import hashlib
import hmac
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware.
    
    Generates and validates CSRF tokens for state-changing requests.
    Tokens are passed via X-CSRF-Token header or _csrf_token form field.
    
    Safe methods (GET, HEAD, OPTIONS) are exempt from CSRF validation.
    
    Usage:
        app.add_middleware(CSRFMiddleware, secret_key="your-secret-key")
        
    Client-side:
        1. Get token from /api/csrf-token endpoint
        2. Include X-CSRF-Token header in POST/PUT/DELETE requests
    """
    
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    TOKEN_LENGTH = 32
    
    def __init__(
        self,
        app,
        secret_key: str,
        header_name: str = "X-CSRF-Token",
        cookie_name: str = "csrf_token",
        exempt_paths: list = None,
    ):
        super().__init__(app)
        self.secret_key = secret_key.encode()
        self.header_name = header_name
        self.cookie_name = cookie_name
        self.exempt_paths = exempt_paths or ["/health", "/api/health", "/api/docs"]
    
    def _generate_token(self) -> str:
        """Generate a new CSRF token."""
        random_bytes = secrets.token_bytes(self.TOKEN_LENGTH)
        signature = hmac.new(self.secret_key, random_bytes, hashlib.sha256).hexdigest()
        return f"{random_bytes.hex()}.{signature}"
    
    def _validate_token(self, token: str) -> bool:
        """Validate a CSRF token."""
        try:
            token_data, signature = token.rsplit(".", 1)
            random_bytes = bytes.fromhex(token_data)
            expected_signature = hmac.new(self.secret_key, random_bytes, hashlib.sha256).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        except (ValueError, AttributeError):
            return False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip for safe methods
        if request.method in self.SAFE_METHODS:
            response = await call_next(request)
            return response
        
        # Skip for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            response = await call_next(request)
            return response
        
        # Get token from header or form data
        token = request.headers.get(self.header_name)
        
        if not token:
            # Try to get from form data
            content_type = request.headers.get("content-type", "")
            if "application/x-www-form-urlencoded" in content_type:
                form = await request.form()
                token = form.get("_csrf_token")
        
        # Validate token
        if not token or not self._validate_token(token):
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token missing or invalid"}
            )
        
        response = await call_next(request)
        return response


# Endpoint to get CSRF token - add to your routes
def get_csrf_router(secret_key: str):
    """Get a router with CSRF token endpoint."""
    from fastapi import APIRouter
    
    router = APIRouter(tags=["Security"])
    middleware = CSRFMiddleware(None, secret_key)
    
    @router.get("/csrf-token")
    async def get_csrf_token():
        """Get a new CSRF token for form submissions."""
        return {"csrf_token": middleware._generate_token()}
    
    return router
