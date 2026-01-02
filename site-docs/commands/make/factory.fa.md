# lich make factory

ساخت factory تست برای تولید داده‌های تست.

## استفاده

```bash
lich make factory <Name>
```

## مثال

```bash
$ lich make factory User

✅ Factory UserFactory ساخته شد!
```

## کد تولید شده

```python
from faker import Faker

fake = Faker()

class UserFactory:
    @staticmethod
    def create(**overrides) -> User:
        return User(
            id=uuid4(),
            name=fake.name(),
            email=fake.email(),
            **overrides
        )
    
    @staticmethod
    def create_batch(count: int, **overrides) -> list:
        return [UserFactory.create(**overrides) for _ in range(count)]
```

## استفاده در تست‌ها

```python
def test_user_registration():
    user = UserFactory.create(email="test@example.com")
    assert user.email == "test@example.com"

def test_list_users():
    users = UserFactory.create_batch(10)
    assert len(users) == 10
```
