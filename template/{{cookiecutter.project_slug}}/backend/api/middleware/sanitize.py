"""
Input Sanitization Middleware - Sanitize user input to prevent XSS attacks.

To enable, add to main.py:
    from api.middleware.sanitize import SanitizeMiddleware
    app.add_middleware(SanitizeMiddleware)
"""
import re
import html
from typing import Any, Callable, Dict, List, Union
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SanitizeMiddleware(BaseHTTPMiddleware):
    """
    Input Sanitization Middleware.
    
    Sanitizes request body JSON to prevent XSS attacks:
    - Removes script tags and event handlers
    - Escapes HTML entities
    - Recursively sanitizes nested objects
    
    Usage:
        app.add_middleware(SanitizeMiddleware)
        
        # Custom patterns:
        app.add_middleware(SanitizeMiddleware, extra_patterns=[r"custom-pattern"])
    """
    
    # XSS attack patterns to remove
    XSS_PATTERNS = [
        # Script tags
        re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL),
        re.compile(r"<\s*script[^>]*>", re.IGNORECASE),
        re.compile(r"<\s*/\s*script\s*>", re.IGNORECASE),
        
        # Event handlers
        re.compile(r"\bon\w+\s*=\s*['\"]?[^'\"]*['\"]?", re.IGNORECASE),
        
        # JavaScript URLs
        re.compile(r"javascript\s*:", re.IGNORECASE),
        re.compile(r"vbscript\s*:", re.IGNORECASE),
        re.compile(r"data\s*:[^,]*;base64", re.IGNORECASE),
        
        # Expression/behavior (IE specific)
        re.compile(r"expression\s*\(", re.IGNORECASE),
        re.compile(r"behavior\s*:", re.IGNORECASE),
        
        # Style tag with expression
        re.compile(r"<\s*style[^>]*>.*?<\s*/\s*style\s*>", re.IGNORECASE | re.DOTALL),
        
        # Iframe/embed/object
        re.compile(r"<\s*iframe[^>]*>", re.IGNORECASE),
        re.compile(r"<\s*embed[^>]*>", re.IGNORECASE),
        re.compile(r"<\s*object[^>]*>", re.IGNORECASE),
    ]
    
    def __init__(
        self,
        app,
        escape_html: bool = True,
        extra_patterns: List[str] = None,
        exclude_paths: List[str] = None,
        exclude_fields: List[str] = None,
    ):
        super().__init__(app)
        self.escape_html = escape_html
        self.exclude_paths = exclude_paths or ["/api/docs", "/api/openapi.json"]
        self.exclude_fields = exclude_fields or ["password", "token", "secret"]
        
        # Compile extra patterns
        self.patterns = self.XSS_PATTERNS.copy()
        if extra_patterns:
            for pattern in extra_patterns:
                self.patterns.append(re.compile(pattern, re.IGNORECASE))
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize a single string value."""
        if not value:
            return value
        
        result = value
        
        # Remove XSS patterns
        for pattern in self.patterns:
            result = pattern.sub("", result)
        
        # Optionally escape HTML entities
        if self.escape_html:
            # Only escape < > & " to prevent HTML injection
            # but allow other characters for usability
            result = (result
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))
        
        return result.strip()
    
    def _sanitize_value(self, value: Any, key: str = None) -> Any:
        """Recursively sanitize a value."""
        # Skip excluded fields
        if key and key.lower() in [f.lower() for f in self.exclude_fields]:
            return value
        
        if isinstance(value, str):
            return self._sanitize_string(value)
        elif isinstance(value, dict):
            return {k: self._sanitize_value(v, k) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._sanitize_value(item) for item in value]
        else:
            return value
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Only process requests with JSON body
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            return await call_next(request)
        
        # Read and sanitize body
        try:
            body = await request.body()
            if body:
                import json
                data = json.loads(body)
                sanitized_data = self._sanitize_value(data)
                
                # Create new request with sanitized body
                # Note: This is a simplified approach
                # For production, consider using a custom Request class
                request._body = json.dumps(sanitized_data).encode()
        except (json.JSONDecodeError, UnicodeDecodeError):
            # If body is not valid JSON, let it through
            # Validation will catch it later
            pass
        
        return await call_next(request)


def sanitize_input(value: Any, escape_html: bool = True) -> Any:
    """
    Utility function to sanitize input outside of middleware.
    
    Usage:
        from api.middleware.sanitize import sanitize_input
        
        clean_name = sanitize_input(user_input)
    """
    middleware = SanitizeMiddleware(None, escape_html=escape_html)
    return middleware._sanitize_value(value)
