# lich make job

Create background jobs for async processing.

## What are Jobs?

**Jobs** run in the background:

- Send emails
- Process images
- Generate reports
- Sync external APIs

## Usage

```bash
lich make job <Name> [--type=celery|temporal]
```

## Example

```bash
$ lich make job SendWelcomeEmail

✅ Job SendWelcomeEmailJob created!

Files created:
  backend/internal/jobs/send_welcome_email.py
```

## Celery Job (Default)

```python
"""
SendWelcomeEmail Celery job.
"""
from celery import shared_task


@shared_task(bind=True, max_retries=3)
def send_welcome_email_job(self, user_id: str, email: str):
    """
    Send welcome email to new user.
    
    Args:
        user_id: User ID
        email: User email
    """
    try:
        # TODO: Implement email sending
        print(f"Sending welcome email to {email}")
        
    except Exception as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```

## Temporal Workflow

```bash
lich make job ProcessOrder --type=temporal
```

```python
"""
ProcessOrder Temporal workflow.
"""
from temporalio import workflow, activity
from datetime import timedelta


@activity.defn
async def validate_order(order_id: str) -> bool:
    """Validate order activity."""
    return True


@workflow.defn
class ProcessOrderWorkflow:
    """Process order workflow."""
    
    @workflow.run
    async def run(self, order_id: str) -> dict:
        # Run activities
        is_valid = await workflow.execute_activity(
            validate_order,
            order_id,
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        if not is_valid:
            return {"status": "invalid"}
        
        return {"status": "processed", "order_id": order_id}
```

## When to Use Each

| Use Celery | Use Temporal |
|------------|--------------|
| Simple tasks | Complex workflows |
| Fire-and-forget | Long-running processes |
| Quick setup | Needs retries & state |

## See Also

- [Background Jobs Guide](../../best-practices/testing.md)
