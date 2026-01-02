# Entities

Entities are the core of your domain - they represent business concepts.

## Location

```
backend/internal/entities/
├── user.py
├── user_repository.py
├── product.py
└── product_repository.py
```

## What An Entity Contains

```python
@dataclass
class Order:
    """Order domain entity."""
    
    # Identity
    id: UUID
    
    # Properties
    user_id: UUID
    items: List[OrderItem]
    total: float
    status: str
    
    # Timestamps
    created_at: datetime
    
    # Domain Methods
    def calculate_total(self) -> float:
        """Business logic lives here."""
        return sum(item.price * item.quantity for item in self.items)
    
    def can_cancel(self) -> bool:
        """Domain rules."""
        return self.status in ['pending', 'processing']
```

## Rules

1. **No framework imports** - Pure Python only
2. **Domain logic inside** - Validation, calculations
3. **Paired with Repository** - Interface for data access

## Create with CLI

```bash
lich make entity Order
```
