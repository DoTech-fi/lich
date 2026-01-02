# lich make factory

Create test factories for generating test data.

## What is a Factory?

A **factory** creates test data with:

- **Fake data** - Realistic random values
- **Defaults** - Sensible pre-filled values
- **Overrides** - Customize specific fields

## Usage

```bash
lich make factory <Name>
```

## Example

```bash
$ lich make factory User

✅ Factory UserFactory created!

Files created:
  backend/tests/factories/user_factory.py
```

## Generated Code

```python
"""
User factory for test data generation.
"""
from uuid import uuid4
from datetime import datetime
from typing import Optional
from faker import Faker

from internal.entities.user import User

fake = Faker()


class UserFactory:
    """Factory for creating User test instances."""
    
    @staticmethod
    def create(
        id: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        **overrides
    ) -> User:
        """
        Create a User instance with fake data.
        
        Args:
            id: Override ID
            name: Override name
            email: Override email
            **overrides: Any other field overrides
        """
        return User(
            id=id or uuid4(),
            name=name or fake.name(),
            email=email or fake.email(),
            created_at=datetime.utcnow(),
            **overrides
        )
    
    @staticmethod
    def create_batch(count: int, **overrides) -> list:
        """Create multiple User instances."""
        return [UserFactory.create(**overrides) for _ in range(count)]
```

## Use in Tests

```python
from tests.factories.user_factory import UserFactory

def test_user_registration():
    # Create test user
    user = UserFactory.create(
        email="test@example.com"
    )
    
    assert user.email == "test@example.com"
    assert user.name  # Random name

def test_list_users():
    # Create 10 test users
    users = UserFactory.create_batch(10)
    
    assert len(users) == 10
```

## Why Use Factories?

| Benefit | Description |
|---------|-------------|
| 🎲 **Realistic Data** | Faker generates real-looking data |
| ⚡ **Speed** | Create test data quickly |
| 🔧 **Flexible** | Override only what you need |
| 🧹 **Clean Tests** | No verbose setup code |

## See Also

- [Testing Guide](../../best-practices/testing.md)
- [`lich test`](../test.md) - Run tests
