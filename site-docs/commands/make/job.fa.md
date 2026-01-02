# lich make job

ساخت background job برای پردازش async.

## استفاده

```bash
lich make job <Name> [--type=celery|temporal]
```

## مثال

```bash
$ lich make job SendWelcomeEmail

✅ Job SendWelcomeEmailJob ساخته شد!
```

## Celery Job (پیش‌فرض)

```python
@shared_task(bind=True, max_retries=3)
def send_welcome_email_job(self, user_id: str, email: str):
    try:
        print(f"Sending welcome email to {email}")
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
```

## Temporal Workflow

```bash
lich make job ProcessOrder --type=temporal
```

## چه زمانی از کدام استفاده کنیم

| از Celery استفاده کنید | از Temporal استفاده کنید |
|------------|--------------|
| کارهای ساده | workflowهای پیچیده |
| Fire-and-forget | پردازش‌های طولانی‌مدت |
| راه‌اندازی سریع | نیاز به retry و state |
