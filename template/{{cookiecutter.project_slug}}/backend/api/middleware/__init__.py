"""
API Middleware Package

Available middlewares (opt-in):
    - RateLimitMiddleware: Prevent API abuse
    - RequestLoggingMiddleware: Log all requests
    - SecurityHeadersMiddleware: Add security headers
    - TimingMiddleware: Add response timing

To enable, add to main.py:
    from api.middleware.rate_limit import RateLimitMiddleware
    from api.middleware.logging import RequestLoggingMiddleware
    from api.middleware.security import SecurityHeadersMiddleware
    from api.middleware.timing import TimingMiddleware
    
    # Add middlewares (order matters - first added = outermost)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
"""
