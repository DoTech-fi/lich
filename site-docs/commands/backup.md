# lich backup

The `lich backup` command creates and restores database backups.

## Usage

```bash
# Create backup
lich backup

# Create backup for specific database
lich backup --database postgres

# Upload to S3
lich backup --s3 my-bucket

# Restore from backup
lich backup restore backup_2024.sql.gz

# List available backups
lich backup list
```

## Supported Databases

| Database | Detection |
|----------|-----------|
| PostgreSQL | Auto-detected from docker-compose |
| MySQL | Auto-detected from docker-compose |
| MongoDB | Auto-detected from docker-compose |
| Redis | RDB dump |

## Options

| Option | Description |
|--------|-------------|
| `--database, -d` | Database type |
| `--s3` | S3 bucket for upload |
| `--output, -o` | Output directory |

## Subcommands

### `lich backup list`
List available local backups.

### `lich backup restore <file>`
Restore database from backup file.

### `lich backup clean`
Remove old backups (keeps last 5).

## Examples

```bash
# Create and upload to S3
lich backup --s3 my-backups

# Restore specific backup
lich backup restore backups/db_2024-01-07.sql.gz

# Interactive restore
lich backup restore
```

## Storage

Backups are stored in:
- Local: `./backups/db/`
- S3: `s3://<bucket>/backups/`
