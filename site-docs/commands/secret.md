# lich secret

The `lich secret` command manages secrets and secure credentials.

## Usage

```bash
# Generate a new secret key
lich secret generate

# Generate with specific length
lich secret generate --length 64

# Rotate existing secrets
lich secret rotate

# Check secret strength
lich secret check
```

## Subcommands

### `lich secret generate`
Generate cryptographically secure secrets.

```bash
# Default (32 chars)
lich secret generate

# Custom length
lich secret generate --length 64

# Hex format
lich secret generate --format hex

# Copy to clipboard
lich secret generate --copy
```

### `lich secret rotate`
Rotate secrets in `.env` file.

```bash
# Rotate all secrets
lich secret rotate

# Rotate specific key
lich secret rotate --key SECRET_KEY

# Preview without applying
lich secret rotate --dry-run
```

### `lich secret check`
Audit secrets for security issues.

```bash
lich secret check
```

Checks for:
- Weak passwords
- Default/placeholder values
- Short secrets (< 32 chars)

## Options

| Option | Description |
|--------|-------------|
| `--length, -l` | Secret length (default: 32) |
| `--format, -f` | Format: `base64`, `hex`, `alphanumeric` |
| `--copy, -c` | Copy to clipboard |
| `--dry-run` | Preview changes |
