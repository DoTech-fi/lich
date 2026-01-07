# Celery Application Configuration
# =================================
# This module configures Celery for background task processing.
#
# Quick start:
#   1. Start Redis: docker compose up redis
#   2. Start worker: celery -A internal.celery_app worker -l INFO
#   3. Start beat (for scheduled tasks): celery -A internal.celery_app beat -l INFO
#
# Environment variables:
#   CELERY_BROKER_URL: Redis URL for message broker
#   CELERY_RESULT_BACKEND: Redis URL for result storage

import os
from celery import Celery
from celery.schedules import crontab

# Get configuration from environment
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# Create Celery app
app = Celery(
    "{{ cookiecutter.project_slug }}",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=[
        "internal.celery_tasks",
    ],
)

# Celery configuration
app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task result settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Task execution settings
    task_acks_late=True,  # Acknowledge after task completion
    task_reject_on_worker_lost=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_concurrency=4,  # Number of concurrent workers
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Daily cleanup at midnight
    "cleanup-old-data": {
        "task": "internal.celery_tasks.cleanup_old_data",
        "schedule": crontab(hour=0, minute=0),
        "args": (30,),  # Keep last 30 days
    },
    
    # Weekly report every Monday at 9 AM
    "weekly-report": {
        "task": "internal.celery_tasks.generate_weekly_report",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
    },
    
    # Health check every 5 minutes
    "health-check": {
        "task": "internal.celery_tasks.health_check",
        "schedule": 300.0,  # 5 minutes in seconds
    },
    
    # Sync data every hour
    "sync-external-data": {
        "task": "internal.celery_tasks.sync_external_data",
        "schedule": crontab(minute=0),  # Every hour at :00
    },
}

# Optional: Custom task base class
class BaseTask:
    """Base task with common functionality."""
    
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes max
    retry_jitter = True


if __name__ == "__main__":
    app.start()
