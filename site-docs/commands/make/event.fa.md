# lich make event

ساخت کلاس‌های event برای معماری event-driven.

## استفاده

```bash
lich make event <Name>
```

## مثال

```bash
$ lich make event OrderPlaced

✅ Event OrderPlaced ساخته شد!
```

## کد تولید شده

```python
@dataclass
class OrderPlacedEvent:
    """Event منتشر شده وقتی سفارش ثبت می‌شود."""
    
    order_id: UUID
    user_id: UUID
    total: float
    timestamp: datetime = None
```

## انتشار Event

```python
event = OrderPlacedEvent(
    order_id=order.id,
    user_id=order.user_id,
    total=order.total
)

await event_bus.publish(event)
```

## همچنین ببینید

- [`make listener`](listener.md) - واکنش به events
