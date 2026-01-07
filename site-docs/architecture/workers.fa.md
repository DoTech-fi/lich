# Background Workers

پروژه‌های لیچ شامل پشتیبانی داخلی برای پردازش تسک‌های پس‌زمینه با استفاده از Temporal یا Celery هستند.

## گزینه‌های Task Runner

هنگام `lich init`، می‌توانید task runner خود را انتخاب کنید:

| گزینه | بهترین برای | ویژگی‌ها |
|-------|-------------|----------|
| **Temporal** | گردش‌کارهای پیچیده | UI بصری، retry، تسک‌های طولانی |
| **Celery** | تسک‌های ساده | سبک، آشنا، عالی برای ایمیل/cron |
| **None** | اپ‌های ساده | بدون پردازش پس‌زمینه |

## Temporal

Temporal برای orchestration پیچیده توصیه می‌شود:

### راه‌اندازی Temporal

```bash
docker compose up temporal temporal-ui
```

### راه‌اندازی Workers

```bash
python -m internal.workers.main
```

### مثال Workflow

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

### فایل‌ها

| فایل | کاربرد |
|------|--------|
| `internal/workers/main.py` | نقطه ورود worker |
| `internal/workers/workflows.py` | تعریف workflow‌ها |
| `internal/workers/activities.py` | پیاده‌سازی activity‌ها |

## Celery

Celery برای job‌های پس‌زمینه ساده‌تر عالی است:

### راه‌اندازی Celery

```bash
# Worker
celery -A internal.celery_app worker -l INFO

# Beat (تسک‌های زمان‌بندی شده)
celery -A internal.celery_app beat -l INFO
```

### مثال تسک

```python
from celery import shared_task

@shared_task
def send_email(to: str, subject: str, body: str):
    # منطق ارسال ایمیل
    return True
```

### فایل‌ها

| فایل | کاربرد |
|------|--------|
| `internal/celery_app.py` | پیکربندی Celery |
| `internal/celery_tasks.py` | تعریف تسک‌ها |

## بهترین شیوه‌ها

1. **تسک‌ها را idempotent نگه دارید** - امن برای retry
2. **از heartbeat استفاده کنید** برای عملیات طولانی
3. **پیشرفت را لاگ کنید** برای دیباگ
4. **timeout مناسب تنظیم کنید**
5. **خطاها را با ظرافت مدیریت کنید**
