# 🎯 Events & Listeners - Complete Guide

> **یادگیری Event-Driven Architecture برای Junior ها**

---

## 📚 مفاهیم پایه

### Event چیست؟
یه چیزی که اتفاق افتاده. گذشته. نه آینده.

```
❌ "UserWillRegister"   ← این اشتباهه
✅ "UserRegistered"     ← این درسته
```

### Listener چیست؟
یه کلاسی که وقتی Event اتفاق می‌افته، یه کاری انجام می‌ده.

---

## 🛠️ چطور استفاده کنیم؟

### Step 1: Event بساز

```bash
lich make event UserRegistered
```

```python
# backend/internal/events/userregistered.py
@dataclass
class UserRegistered:
    user_id: UUID
    email: str
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
```

### Step 2: Listener(s) بساز

```bash
lich make listener SendWelcomeEmail --event UserRegistered
lich make listener CreateDefaultSettings --event UserRegistered
lich make listener TrackAnalytics --event UserRegistered
```

### Step 3: Event رو Fire کن

```python
# In your service
from internal.events.userregistered import UserRegistered

class UserService:
    def __init__(self, repo, event_bus):
        self.repo = repo
        self.event_bus = event_bus
    
    async def register(self, email: str, password: str):
        # 1. Create user
        user = await self.repo.create(email=email, password=hash(password))
        
        # 2. Fire event
        event = UserRegistered(user_id=user.id, email=email)
        await self.event_bus.publish(event)
        
        return user
```

---

## 🎬 سناریوهای واقعی

### Scenario 1: ثبت نام کاربر

```
UserRegistered Event
    │
    ├── SendWelcomeEmail Listener
    │   └── Email welcome message
    │
    ├── CreateDefaultSettings Listener
    │   └── Create user preferences
    │
    └── TrackAnalytics Listener
        └── Log to analytics
```

```bash
lich make event UserRegistered
lich make listener SendWelcomeEmail
lich make listener CreateDefaultSettings
lich make listener TrackAnalytics
```

---

### Scenario 2: سفارش آنلاین

```
OrderPlaced Event
    │
    ├── SendOrderConfirmation Listener
    │   └── Email to customer
    │
    ├── NotifyWarehouse Listener
    │   └── Send to ERP
    │
    ├── DeductInventory Listener
    │   └── Update stock
    │
    └── CreateShippingLabel Listener
        └── Generate label
```

```bash
lich make event OrderPlaced
lich make listener SendOrderConfirmation
lich make listener NotifyWarehouse
lich make listener DeductInventory
lich make listener CreateShippingLabel
```

---

### Scenario 3: پرداخت موفق

```
PaymentReceived Event
    │
    ├── ActivateSubscription Listener
    │   └── Enable features
    │
    ├── SendReceipt Listener
    │   └── Email invoice
    │
    └── NotifyAccountant Listener
        └── Webhook to accounting
```

```bash
lich make event PaymentReceived
lich make listener ActivateSubscription
lich make listener SendReceipt
lich make listener NotifyAccountant
```

---

## 💡 Event Bus - ساده‌ترین پیاده‌سازی

```python
# pkg/events/bus.py
from typing import Dict, List, Type
import asyncio

class EventBus:
    def __init__(self):
        self._listeners: Dict[Type, List] = {}
    
    def subscribe(self, event_type: Type, listener):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
    
    async def publish(self, event):
        event_type = type(event)
        for listener in self._listeners.get(event_type, []):
            await listener.handle(event)
```

### استفاده:

```python
# main.py
from pkg.events.bus import EventBus
from internal.events.userregistered import UserRegistered
from internal.listeners.sendwelcomeemail import SendWelcomeEmail
from internal.listeners.createdefaultsettings import CreateDefaultSettings

# Setup
event_bus = EventBus()
event_bus.subscribe(UserRegistered, SendWelcomeEmail())
event_bus.subscribe(UserRegistered, CreateDefaultSettings())
```

---

## 🔄 Async Event Processing

برای کارهای سنگین از **Job** استفاده کن:

```python
class SendWelcomeEmail:
    async def handle(self, event: UserRegistered):
        # Don't do heavy work here!
        # Dispatch to background job
        send_email_job.delay({
            "email": event.email,
            "template": "welcome"
        })
```

---

## ✅ Best Practices

### 1. Event ها باید immutable باشن
```python
@dataclass(frozen=True)  # ← frozen!
class UserRegistered:
    user_id: UUID
    email: str
```

### 2. Event ها باید کوچیک باشن
```python
# ❌ Bad - too much data
@dataclass
class OrderPlaced:
    order: Order  # Full object!
    products: List[Product]
    customer: Customer

# ✅ Good - just IDs
@dataclass
class OrderPlaced:
    order_id: UUID
    customer_id: UUID
```

### 3. Listener ها باید یه کار انجام بدن
```python
# ❌ Bad - does too much
class DoEverything:
    async def handle(self, event):
        await send_email()
        await update_analytics()
        await notify_slack()

# ✅ Good - single responsibility
class SendEmail:
    async def handle(self, event):
        await send_email()

class UpdateAnalytics:
    async def handle(self, event):
        await analytics.track()
```

---

## 🧪 تست نوشتن

```python
import pytest
from internal.events.userregistered import UserRegistered
from internal.listeners.sendwelcomeemail import SendWelcomeEmail

@pytest.mark.asyncio
async def test_send_welcome_email_on_user_registered():
    # Arrange
    event = UserRegistered(
        user_id=uuid4(),
        email="test@test.com"
    )
    listener = SendWelcomeEmail(email_service=MockEmailService())
    
    # Act
    await listener.handle(event)
    
    # Assert
    assert listener.email_service.sent_to == "test@test.com"
```

---

## 📋 Cheat Sheet

| کار | دستور |
|-----|--------|
| Event بساز | `lich make event OrderPlaced` |
| Listener بساز | `lich make listener SendConfirmation` |
| Event منتشر کن | `await event_bus.publish(event)` |

---

**حالا برو Event-Driven Architecture بزن! 🚀**
