# lich deploy

The `lich deploy` command deploys your project using Ansible.

## Usage

```bash
# Deploy to staging
lich deploy --env staging

# Deploy to production
lich deploy --env production

# Deploy with specific host
lich deploy --host user@server.com

# Dry run (show what would happen)
lich deploy --dry-run
```

## Requirements

- **Ansible** installed locally
- SSH access to target servers
- Configured inventory in `infra/ansible/inventory/`

## Options

| Option | Description |
|--------|-------------|
| `--env, -e` | Environment: `staging`, `production` |
| `--host, -h` | Target host (user@hostname) |
| `--key, -k` | SSH private key path |
| `--dry-run` | Show what would happen without executing |
| `--playbook, -p` | Specific playbook to run |

## Playbooks

| Playbook | Description |
|----------|-------------|
| `site.yml` | Full server setup |
| `update.yml` | Deploy code updates |
| `backup.yml` | Create backup |
| `rollback.yml` | Rollback to previous version |

## Examples

```bash
# Full deployment
lich deploy --env production

# Update only
lich deploy --env production --playbook update.yml

# Test without executing
lich deploy --env staging --dry-run
```

## Configuration

Edit `infra/ansible/group_vars/all.yml`:

```yaml
project_name: myproject
app_domain: example.com
db_name: myproject_db
ssl_enabled: true
```
