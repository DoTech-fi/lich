# Infrastructure Architecture Rules

> As an Infra Architect for Terraform + Ansible, follow these rules.

## Core Principles

```
📝 INFRASTRUCTURE AS CODE
🔒 SECURE BY DEFAULT
🔄 IDEMPOTENT OPERATIONS
🌍 ENVIRONMENT-AWARE
```

---

## 1. Folder Structure

```
infra/
├── terraform/
│   ├── envs/
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── backend.tf
│   │   ├── stage/
│   │   └── prod/
│   ├── modules/
│   │   ├── network/
│   │   ├── compute/
│   │   ├── database/
│   │   └── security/
│   └── README.md
└── ansible/
    ├── inventories/
    │   ├── dev/
    │   ├── stage/
    │   └── prod/
    ├── roles/
    │   ├── common/
    │   ├── backend/
    │   ├── frontend/
    │   └── monitoring/
    ├── playbooks/
    │   └── site.yml
    └── group_vars/
```

---

## 2. Terraform Rules

### DO ✅
- Remote backend for state (S3/GCS + lock)
- Separate directories per environment
- Use modules with clear purpose
- Minimal, clean variable interface
- Tag all resources (project, env, owner)

### DON'T ❌
- No secrets in Terraform code
- No hardcoded environment values in modules
- No public access by default

### Module Structure
```hcl
# modules/network/main.tf
variable "vpc_cidr" {}
variable "environment" {}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "${var.environment}-vpc"
    Environment = var.environment
  }
}

output "vpc_id" {
  value = aws_vpc.main.id
}
```

---

## 3. Ansible Rules

### DO ✅
- Focused roles (common, backend, frontend, db)
- Idempotent tasks always
- Use ansible-vault for secrets
- Separate inventory per environment
- Key-based SSH auth

### DON'T ❌
- No raw passwords in code
- No password SSH auth
- No shared state between runs

### Role Structure
```
roles/backend/
├── tasks/
│   └── main.yml
├── handlers/
│   └── main.yml
├── templates/
│   └── app.service.j2
├── defaults/
│   └── main.yml
└── vars/
    └── main.yml
```

---

## 4. Security

### DO ✅
- Private subnets for sensitive resources
- Security groups: least privilege
- Use secret managers
- Encrypt data at rest and in transit

### DON'T ❌
- No public IPs for databases
- No 0.0.0.0/0 ingress rules
- No hardcoded credentials

---

## 5. Integration

Terraform provisions → Ansible configures → App runs

```
Terraform outputs (IPs, endpoints)
       ↓
Ansible inventory (uses outputs)
       ↓
Application config (env variables)
```

---

> **Mantra**: Simple → Modular → Secure
