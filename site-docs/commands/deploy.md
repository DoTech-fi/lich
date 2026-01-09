# lich deploy

The `lich deploy` command deploys components to staging or production.

## Setup

```bash
# Interactive setup (one time)
lich deploy setup
```

Setup asks:
- Environment (staging/production/both)
- Connection method (SSH config or manual)
- Deploy path on server
- Runtime (docker-compose or bare-metal)
- Git repository URL

## Usage

```bash
# Deploy to staging
lich deploy stage backend
lich deploy stage admin

# Deploy to production (with confirmation)
lich deploy prod backend
lich deploy prod admin --version v1.2.3

# Skip confirmation
lich deploy prod backend --force
```

## Commands

| Command | Description |
|---------|-------------|
| `lich deploy setup` | Interactive configuration |
| `lich deploy stage <component>` | Deploy to staging |
| `lich deploy prod <component>` | Deploy to production |
| `lich deploy status` | Show current configuration |

## Components

Valid components: `backend`, `web`, `admin`, `landing`

## Options

| Option | Description |
|--------|-------------|
| `--version, -v` | Specific version/tag to deploy |
| `--dry-run` | Preview without deploying |
| `--force, -f` | Skip confirmation (prod only) |

## Configuration

Saved to `.lich/deploy.yml`:

```yaml
staging:
  connection: ssh-config
  ssh_name: myserver-stage
  path: /opt/app
  runtime: docker-compose

production:
  connection: ssh-config
  ssh_name: myserver-prod
  path: /opt/app
  runtime: docker-compose

git_repo: git@github.com:user/repo.git
private_repo: true
```

## Secrets

For private repos, add to `.secrets`:

```
GITHUB_TOKEN=ghp_your_token_here
```

## Examples

```bash
# Deploy admin to staging
lich deploy stage admin

# Deploy backend v1.2.3 to production
lich deploy prod backend --version v1.2.3

# Preview deployment
lich deploy stage web --dry-run

# Check configuration
lich deploy status
```
