# lich seed

Database seeding commands.

## Usage

```bash
lich seed [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--fresh` | Reset DB before seeding |
| `--list` | List available seeders |
| `--only NAME` | Run specific seeder |

## Examples

```bash
# Run all seeders
lich seed

# List available seeders
lich seed --list

# Run specific seeder
lich seed --only users

# Fresh database + seed
lich seed --fresh
```

## Creating Seeders

Create seeders in `backend/seeds/`:

```python
# backend/seeds/users_seeder.py

from internal.entities.user import User

async def run(session):
    """Seed users table."""
    users = [
        User(name="Admin", email="admin@example.com", is_admin=True),
        User(name="Test User", email="user@example.com"),
    ]
    
    for user in users:
        session.add(user)
    
    await session.commit()
    print(f"Seeded {len(users)} users")
```

## Example Output

```bash
$ lich seed

🌱 Running Database Seeders

  ✅ users_seeder - 10 records
  ✅ products_seeder - 50 records
  ✅ orders_seeder - 25 records

Done! Seeded 85 total records.
```
