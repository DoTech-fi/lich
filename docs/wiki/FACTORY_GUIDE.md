# 🏭 Factory Guide - Test Data Generation

> **چطور از Factory ها برای تست استفاده کنیم**

---

## 🎯 Factory چیه؟

Factory یه کلاس کمکی هست که **داده‌های تستی** می‌سازه. به جای اینکه هر بار دستی User یا Product بسازی،
Factory با یه خط کد همه فیلدها رو با داده‌های واقعی پر می‌کنه.

---

## 🚀 Quick Start

### 1. ساختن Factory

```bash
lich make factory User
```

فایل ساخته می‌شه در: `backend/tests/factories/user_factory.py`

### 2. محتوای Factory

```python
"""
UserFactory - Generate test data for User entity.
"""
from faker import Faker
from internal.entities.user import User

fake = Faker()


class UserFactory:
    """Factory for creating User test instances."""
    
    @classmethod
    def build(cls, **kwargs) -> User:
        """Build a User instance without saving."""
        defaults = {
            "id": fake.uuid4(),
            "email": fake.email(),
            "name": fake.name(),
            "is_active": True,
        }
        defaults.update(kwargs)
        return User(**defaults)
    
    @classmethod
    def build_batch(cls, count: int, **kwargs) -> list[User]:
        """Build multiple User instances."""
        return [cls.build(**kwargs) for _ in range(count)]
```

---

## 📋 استفاده در تست‌ها

### مثال ساده

```python
from tests.factories.user_factory import UserFactory

def test_user_creation():
    # یه User با داده‌های رندوم
    user = UserFactory.build()
    
    assert user.email is not None
    assert user.name is not None
```

### Override کردن فیلدها

```python
def test_specific_email():
    # Email خاص، بقیه رندوم
    user = UserFactory.build(email="test@example.com")
    
    assert user.email == "test@example.com"
```

### ساختن چند تا

```python
def test_list_users():
    users = UserFactory.build_batch(10)
    
    assert len(users) == 10
```

---

## 🔧 Factory Patterns

### Basic Factory

```python
class ProductFactory:
    @classmethod
    def build(cls, **kwargs) -> Product:
        defaults = {
            "id": fake.uuid4(),
            "name": fake.word(),
            "price": fake.pydecimal(min_value=1, max_value=1000),
            "stock": fake.random_int(min=0, max=100),
        }
        defaults.update(kwargs)
        return Product(**defaults)
```

### Factory با Relationship

```python
class OrderFactory:
    @classmethod
    def build(cls, user: User = None, **kwargs) -> Order:
        if user is None:
            user = UserFactory.build()
        
        defaults = {
            "id": fake.uuid4(),
            "user_id": user.id,
            "user": user,
            "total": fake.pydecimal(min_value=10, max_value=500),
            "status": "pending",
        }
        defaults.update(kwargs)
        return Order(**defaults)
```

### Factory با States

```python
class UserFactory:
    @classmethod
    def build(cls, **kwargs) -> User:
        # Default active user
        defaults = {
            "id": fake.uuid4(),
            "email": fake.email(),
            "is_active": True,
            "is_admin": False,
        }
        defaults.update(kwargs)
        return User(**defaults)
    
    @classmethod
    def admin(cls, **kwargs) -> User:
        """Build an admin user."""
        return cls.build(is_admin=True, **kwargs)
    
    @classmethod
    def inactive(cls, **kwargs) -> User:
        """Build an inactive user."""
        return cls.build(is_active=False, **kwargs)
```

استفاده:
```python
admin = UserFactory.admin()
inactive = UserFactory.inactive()
```

---

## 🗄️ Factory با Database (Integration Tests)

```python
class UserFactory:
    @classmethod
    def build(cls, **kwargs) -> User:
        """Build without saving."""
        ...
    
    @classmethod
    async def create(cls, db_session, **kwargs) -> User:
        """Create and save to database."""
        user = cls.build(**kwargs)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
```

استفاده:
```python
async def test_get_user(db_session):
    user = await UserFactory.create(db_session)
    
    result = await user_service.get(user.id)
    assert result.id == user.id
```

---

## 📁 فایل‌ها کجان؟

```
backend/
└── tests/
    └── factories/
        ├── __init__.py
        ├── user_factory.py
        ├── product_factory.py
        └── order_factory.py
```

---

## ❓ FAQ

### Q: چرا Factory بهتر از دستی ساختنه؟
**A:**
- کد تست تمیزتر
- DRY (Don't Repeat Yourself)
- داده‌های واقعی‌تر با Faker
- تغییرات Entity فقط یه جا fix می‌شه

### Q: Faker چیه؟
**A:** کتابخانه‌ای که داده‌های fake ولی واقعی می‌سازه:
```python
fake.name()      # "John Smith"
fake.email()     # "john@example.com"
fake.address()   # "123 Main St, City, Country"
fake.uuid4()     # UUID رندوم
```

### Q: Factory vs Fixture?
**A:**
- **Factory**: داده می‌سازه، هر بار جدید
- **Fixture**: setup/teardown روی تست‌ها

کنار هم استفاده می‌شن:
```python
@pytest.fixture
def user():
    return UserFactory.build()
```

---

## 🛠️ CLI Commands

```bash
# ساختن Factory جدید
lich make factory User

# ساختن Entity + Factory با هم
lich make entity User
lich make factory User
```

---

**حالا تست نوشتن سریع‌تر و تمیزتره!** 🏭✅
