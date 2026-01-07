# Background Workers

Lich projects include built-in support for background task processing using Temporal or Celery.

## Task Runner Options

During `lich init`, you can choose your task runner:

| Option | Best For | Features |
|--------|----------|----------|
| **Temporal** | Complex workflows | Visual UI, retries, long-running tasks |
| **Celery** | Simple tasks | Lightweight, familiar, great for email/cron |
| **None** | Simple apps | No background processing |

## Temporal

Temporal is recommended for complex orchestration:

### Starting Temporal

```bash
docker compose up temporal temporal-ui
```

### Starting Workers

```bash
python -m internal.workers.main
```

### Example Workflow

```python
from temporalio import workflow

@workflow.defn
class EmailNotificationWorkflow:
    @workflow.run
    async def run(self, email: str, subject: str) -> bool:
        return await workflow.execute_activity(
            "send_email_activity",
            args=[email, subject],
            start_to_close_timeout=timedelta(seconds=30),
        )
```

### Files

| File | Purpose |
|------|---------|
| `internal/workers/main.py` | Worker entry point |
| `internal/workers/workflows.py` | Workflow definitions |
| `internal/workers/activities.py` | Activity implementations |

## Celery

Celery is great for simpler background jobs:

### Starting Celery

```bash
# Worker
celery -A internal.celery_app worker -l INFO

# Beat (scheduled tasks)
celery -A internal.celery_app beat -l INFO
```

### Example Task

```python
from celery import shared_task

@shared_task
def send_email(to: str, subject: str, body: str):
    # Send email logic
    return True
```

### Files

| File | Purpose |
|------|---------|
| `internal/celery_app.py` | Celery configuration |
| `internal/celery_tasks.py` | Task definitions |

## Best Practices

1. **Keep tasks idempotent** - Safe to retry
2. **Use heartbeats** for long operations
3. **Log progress** for debugging
4. **Set timeouts** appropriately
5. **Handle failures** gracefully
