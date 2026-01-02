# lich make event

Create event classes for event-driven architecture.

## What are Events?

**Events** represent things that happened:

- `UserRegistered`
- `OrderPlaced`
- `PaymentCompleted`

Events are published and listeners react to them.

## Usage

```bash
lich make event <Name>
```

## Example

```bash
$ lich make event OrderPlaced

✅ Event OrderPlaced created!

Files created:
  backend/internal/events/order_placed.py
```

## Generated Code

```python
"""
OrderPlaced event.
"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class OrderPlacedEvent:
    """
    Event emitted when an order is placed.
    """
    
    order_id: UUID
    user_id: UUID
    total: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
```

## Publishing Events

```python
from internal.events.order_placed import OrderPlacedEvent

# In your service
event = OrderPlacedEvent(
    order_id=order.id,
    user_id=order.user_id,
    total=order.total
)

await event_bus.publish(event)
```

## Why Events?

| Benefit | Description |
|---------|-------------|
| 🔌 **Decoupling** | Services don't know about each other |
| 📬 **Async** | Non-blocking operations |
| 🔄 **Scalable** | Add listeners without changing code |

## See Also

- [`make listener`](listener.md) - React to events
