# lich make listener

ساخت event listener برای واکنش به events.

## استفاده

```bash
lich make listener <Name>
```

## مثال

```bash
$ lich make listener SendOrderConfirmation

✅ Listener SendOrderConfirmationListener ساخته شد!
```

## کد تولید شده

```python
class SendOrderConfirmationListener:
    async def handle(self, event: OrderPlacedEvent) -> None:
        # ارسال ایمیل تایید
        print(f"Order {event.order_id} confirmed!")
```

## ثبت Listeners

```python
event_bus.subscribe(OrderPlacedEvent, SendOrderConfirmationListener())
```
