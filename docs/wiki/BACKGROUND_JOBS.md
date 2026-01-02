# ⚙️ Background Jobs - Celery vs Temporal

> **انتخاب Queue System مناسب**

---

## 🤔 کدوم رو انتخاب کنم؟

| | Celery | Temporal |
|---|--------|----------|
| **پیچیدگی** | ساده | پیچیده‌تر |
| **Use Case** | ارسال ایمیل، پردازش فایل | Workflow های پیچیده |
| **Infrastructure** | Redis | Temporal Server |
| **Retry Logic** | ساده | پیشرفته |
| **Observability** | ساده | UI داخلی |
| **Learning Curve** | کم | زیاد |

---

## 🟢 Celery - ساده و سریع

### کِی استفاده کنیم؟
- ارسال ایمیل
- پردازش تصویر/ویدیو
- Sync کردن با سرویس خارجی
- کارهای ساده و یکباره

### چطور بسازیم؟

```bash
lich make job SendEmail --queue celery
```

```python
# backend/internal/jobs/sendemail_job.py
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def send_email_job(self, data: dict):
    """
    Send email background job.
    
    Usage:
        send_email_job.delay({"email": "test@test.com", "template": "welcome"})
    """
    try:
        email = data["email"]
        template = data["template"]
        
        # Send email logic
        send_email(email, template)
        
        return {"status": "sent", "email": email}
    
    except Exception as exc:
        # Retry with exponential backoff
        self.retry(exc=exc, countdown=2 ** self.request.retries)
```

### استفاده:

```python
# In your service
from internal.jobs.sendemail_job import send_email_job

class UserService:
    async def register(self, email: str):
        user = await self.repo.create(email=email)
        
        # 👇 Dispatch to background
        send_email_job.delay({
            "email": email,
            "template": "welcome"
        })
        
        return user
```

### Setup Celery:

```python
# backend/celery_app.py
from celery import Celery

app = Celery(
    'lich',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
)
```

---

## 🔵 Temporal - Workflow های پیچیده

### کِی استفاده کنیم؟
- Workflow های چند مرحله‌ای
- کارهایی که ممکنه ساعت‌ها طول بکشن
- نیاز به Rollback
- Saga Pattern
- Human-in-the-loop

### چطور بسازیم؟

```bash
lich make job ProcessOrder --queue temporal
```

```python
# backend/internal/jobs/processorder_job.py
from datetime import timedelta
from temporalio import activity, workflow

@activity.defn
async def validate_order_activity(order_id: str) -> dict:
    """Validate the order."""
    # Validation logic
    return {"valid": True}

@activity.defn
async def charge_payment_activity(order_id: str) -> dict:
    """Charge the payment."""
    # Payment logic
    return {"charged": True}

@activity.defn
async def reserve_inventory_activity(order_id: str) -> dict:
    """Reserve inventory."""
    # Inventory logic
    return {"reserved": True}

@activity.defn
async def send_confirmation_activity(order_id: str) -> dict:
    """Send order confirmation."""
    # Email logic
    return {"sent": True}


@workflow.defn
class ProcessOrderWorkflow:
    """
    Order processing workflow.
    
    Steps:
    1. Validate order
    2. Charge payment
    3. Reserve inventory
    4. Send confirmation
    """
    
    @workflow.run
    async def run(self, order_id: str) -> dict:
        # Step 1: Validate
        validation = await workflow.execute_activity(
            validate_order_activity,
            order_id,
            start_to_close_timeout=timedelta(minutes=1),
        )
        
        if not validation["valid"]:
            return {"status": "failed", "reason": "validation"}
        
        # Step 2: Charge payment
        payment = await workflow.execute_activity(
            charge_payment_activity,
            order_id,
            start_to_close_timeout=timedelta(minutes=5),
        )
        
        # Step 3: Reserve inventory
        inventory = await workflow.execute_activity(
            reserve_inventory_activity,
            order_id,
            start_to_close_timeout=timedelta(minutes=2),
        )
        
        # Step 4: Send confirmation
        await workflow.execute_activity(
            send_confirmation_activity,
            order_id,
            start_to_close_timeout=timedelta(minutes=1),
        )
        
        return {"status": "completed", "order_id": order_id}
```

### استفاده:

```python
from temporalio.client import Client

async def start_order_processing(order_id: str):
    client = await Client.connect("localhost:7233")
    
    result = await client.execute_workflow(
        ProcessOrderWorkflow.run,
        order_id,
        id=f"order-{order_id}",
        task_queue="orders",
    )
    
    return result
```

---

## 📊 مقایسه سناریوها

### Scenario 1: ارسال ایمیل خوش‌آمدگویی
**انتخاب: Celery** ← ساده، یه بار اجرا

```bash
lich make job SendWelcomeEmail --queue celery
```

---

### Scenario 2: پردازش سفارش
**انتخاب: Temporal** ← چند مرحله، نیاز به Rollback

```bash
lich make job ProcessOrder --queue temporal
```

---

### Scenario 3: Resize کردن عکس
**انتخاب: Celery** ← ساده، CPU-bound

```bash
lich make job ResizeImage --queue celery
```

---

### Scenario 4: Onboarding کاربر جدید
**انتخاب: Temporal** ← چند روزه، نیاز به track

```bash
lich make job UserOnboarding --queue temporal
```

---

## 🔧 Docker Setup

### Celery (با Redis):

```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"

celery_worker:
  build: ./backend
  command: celery -A celery_app worker -l info
  depends_on:
    - redis
  environment:
    CELERY_BROKER_URL: redis://redis:6379/0
```

### Temporal:

```yaml
# docker-compose.yml
temporal:
  image: temporalio/auto-setup:1.22
  ports:
    - "7233:7233"
  environment:
    - DB=postgresql
    - POSTGRES_SEEDS=postgres

temporal-ui:
  image: temporalio/ui:2.22.1
  ports:
    - "8088:8080"
  environment:
    - TEMPORAL_ADDRESS=temporal:7233
```

---

## ✅ Best Practices

### 1. Job ها باید Idempotent باشن
```python
# ❌ Bad - can double-charge
@shared_task
def charge_user(user_id, amount):
    charge(user_id, amount)

# ✅ Good - check before charge
@shared_task
def charge_user(user_id, amount, payment_id):
    if already_charged(payment_id):
        return
    charge(user_id, amount, payment_id)
```

### 2. Retry با Backoff
```python
@shared_task(
    bind=True,
    max_retries=5,
    retry_backoff=2,      # 2, 4, 8, 16, 32 seconds
    retry_backoff_max=60  # Max 60 seconds
)
def my_task(self):
    ...
```

### 3. Dead Letter Queue
```python
@shared_task(
    bind=True,
    max_retries=3,
    on_failure=send_to_dlq
)
def critical_task(self):
    ...
```

---

## 📋 Cheat Sheet

```bash
# Celery job
lich make job SendEmail --queue celery

# Temporal workflow
lich make job ProcessOrder --queue temporal

# Run Celery worker
celery -A celery_app worker -l info

# Run Temporal worker
python worker.py
```

---

**حالا برو Background Processing بزن! 🚀**
