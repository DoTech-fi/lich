# lich make listener

Create event listeners to react to events.

## What are Listeners?

**Listeners** react to events:

- Send welcome email when `UserRegistered`
- Update inventory when `OrderPlaced`
- Send notification when `PaymentCompleted`

## Usage

```bash
lich make listener <Name>
```

## Example

```bash
$ lich make listener SendOrderConfirmation

✅ Listener SendOrderConfirmationListener created!

Files created:
  backend/internal/listeners/send_order_confirmation.py
```

## Generated Code

```python
"""
SendOrderConfirmation listener.
"""
from internal.events.order_placed import OrderPlacedEvent


class SendOrderConfirmationListener:
    """
    Listener that sends order confirmation email.
    """
    
    async def handle(self, event: OrderPlacedEvent) -> None:
        """
        Handle the OrderPlaced event.
        
        Args:
            event: The event data
        """
        # TODO: Implement logic
        # - Send confirmation email
        # - Log the order
        # - Update analytics
        print(f"Order {event.order_id} confirmed!")
```

## Registering Listeners

```python
event_bus.subscribe(OrderPlacedEvent, SendOrderConfirmationListener())
event_bus.subscribe(OrderPlacedEvent, UpdateInventoryListener())
```

## See Also

- [`make event`](event.md) - Create events first
