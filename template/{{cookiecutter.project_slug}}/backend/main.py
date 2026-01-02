"""
{{ cookiecutter.project_name }} - Backend API
FastAPI application with Lich Architecture
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
{%- if cookiecutter.use_structured_logging == 'yes' %}
from pkg.logger.setup import setup_logging, get_logger
{%- endif %}
from pkg.config.settings import settings
from api.http import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    {%- if cookiecutter.use_structured_logging == 'yes' %}
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting {{ cookiecutter.project_name }} API")
    {%- else %}
    print("🚀 Starting {{ cookiecutter.project_name }} API")
    {%- endif %}
    
    # Initialize database connection
    from internal.adapters.db.connection import init_db
    await init_db()
    
    {%- if cookiecutter.use_redis == 'yes' %}
    # Initialize Redis connection
    from internal.adapters.cache.redis_cache import init_redis
    await init_redis()
    {%- endif %}
    
    yield
    
    # Cleanup
    {%- if cookiecutter.use_structured_logging == 'yes' %}
    logger.info("Shutting down {{ cookiecutter.project_name }} API")
    {%- else %}
    print("👋 Shutting down {{ cookiecutter.project_name }} API")
    {%- endif %}


app = FastAPI(
    title="{{ cookiecutter.project_name }} API",
    description="{{ cookiecutter.project_description }}",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# OPTIONAL MIDDLEWARES - Uncomment to enable
# ============================================================

# --- Timing: Add response time headers ---
# from api.middleware.timing import TimingMiddleware
# app.add_middleware(TimingMiddleware)

# --- Security Headers: OWASP security headers ---
# from api.middleware.security import SecurityHeadersMiddleware
# app.add_middleware(SecurityHeadersMiddleware)

# --- Request Logging: Log all requests with timing ---
# from api.middleware.logging import RequestLoggingMiddleware
# app.add_middleware(RequestLoggingMiddleware)

# --- Rate Limiting: Prevent API abuse ---
# from api.middleware.rate_limit import RateLimitMiddleware
# app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# ============================================================

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "{{ cookiecutter.project_slug }}-api"}


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint."""
    return {"status": "healthy", "service": "{{ cookiecutter.project_slug }}-api"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
