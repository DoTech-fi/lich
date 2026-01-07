"""
Audit Logging Middleware - Log all state-changing API requests.

To enable, add to main.py:
    from api.middleware.audit import AuditMiddleware
    app.add_middleware(AuditMiddleware)
"""
import json
import logging
from datetime import datetime
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("audit")


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Audit Logging Middleware.
    
    Logs POST, PUT, PATCH, DELETE operations with:
    - Timestamp
    - User ID (from request state or JWT)
    - Request path and method
    - Response status code
    - Client IP address
    - Request duration
    
    Usage:
        app.add_middleware(AuditMiddleware)
        
        # With DB persistence:
        app.add_middleware(AuditMiddleware, persist_to_db=True)
    """
    
    AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    
    def __init__(
        self,
        app,
        persist_to_db: bool = False,
        exclude_paths: list = None,
    ):
        super().__init__(app)
        self.persist_to_db = persist_to_db
        self.exclude_paths = exclude_paths or [
            "/health", "/api/health", "/api/docs", 
            "/api/openapi.json", "/metrics"
        ]
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, handling proxies."""
        # Check X-Forwarded-For header (from reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request state or JWT."""
        # Try request.state.user (set by auth middleware)
        if hasattr(request.state, "user"):
            user = request.state.user
            if hasattr(user, "id"):
                return str(user.id)
            elif isinstance(user, dict):
                return str(user.get("id", user.get("sub", "unknown")))
        
        # Try to decode from Authorization header (basic extraction)
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            # Just log that there was a token, don't decode here
            return "authenticated"
        
        return "anonymous"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip non-audited methods
        if request.method not in self.AUDITED_METHODS:
            return await call_next(request)
        
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        start_time = datetime.utcnow()
        
        # Process request
        response = await call_next(request)
        
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Build audit entry
        audit_entry = {
            "timestamp": start_time.isoformat() + "Z",
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params) or None,
            "user_id": self._get_user_id(request),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", "unknown")[:200],
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }
        
        # Log the audit entry
        logger.info(json.dumps(audit_entry))
        
        # Optionally persist to database
        if self.persist_to_db:
            await self._persist_audit_log(audit_entry)
        
        return response
    
    async def _persist_audit_log(self, entry: dict):
        """Persist audit log to database. Override this method for custom storage."""
        # This is a placeholder - implement based on your DB setup
        # Example with SQLAlchemy:
        # async with get_session() as session:
        #     audit_log = AuditLog(**entry)
        #     session.add(audit_log)
        #     await session.commit()
        pass


# Optional: AuditLog entity for DB persistence
"""
To use DB persistence, create this entity:

# internal/entities/audit_log.py
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from internal.adapters.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    method = Column(String(10))
    path = Column(String(500))
    query = Column(String(1000), nullable=True)
    user_id = Column(String(100))
    client_ip = Column(String(50))
    user_agent = Column(String(200))
    status_code = Column(Integer)
    duration_ms = Column(Integer)
"""
