# lich migration

Database migration commands using Alembic.

## Commands

| Command | Description |
|---------|-------------|
| `lich migration init` | Initialize Alembic |
| `lich migration create "message"` | Create new migration |
| `lich migration up` | Apply all migrations |
| `lich migration down` | Rollback one migration |
| `lich migration status` | Show migration status |

## Initialize Migrations

```bash
lich migration init
```

Creates `backend/alembic/` folder with configuration.

## Create Migration

```bash
lich migration create "add users table"
```

Creates migration file in `backend/alembic/versions/`.

## Apply Migrations

```bash
# Apply all pending
lich migration up

# Apply specific revision
lich migration up abc123
```

## Rollback

```bash
# Rollback one
lich migration down

# Rollback to specific
lich migration down abc123
```

## Check Status

```bash
lich migration status
```

Shows current revision and pending migrations.

## Example Workflow

```bash
# 1. Create entity
lich make entity Product

# 2. Create migration for the table
lich migration create "add products table"

# 3. Edit the migration file
# 4. Apply it
lich migration up
```
