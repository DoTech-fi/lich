{%- if cookiecutter.use_structured_logging == 'yes' %}
"""
Structured logging setup using structlog.
Produces JSON logs in production, pretty logs in development.
"""
import logging
import structlog
from pkg.config.settings import settings


def setup_logging():
    """Configure structured logging."""
    
    # Determine if we're in development
    is_dev = settings.environment == "development"
    
    # Shared processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    
    if is_dev:
        # Development: pretty console output
        shared_processors.append(structlog.dev.ConsoleRenderer())
    else:
        # Production: JSON output
        shared_processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
{%- else %}
"""
Simple logging setup.
"""
import logging
from pkg.config.settings import settings


def setup_logging():
    """Configure basic logging."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
{%- endif %}
