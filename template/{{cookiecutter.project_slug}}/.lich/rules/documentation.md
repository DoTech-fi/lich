# Documentation Rules

> **Documentation Architect - Mandatory Documentation for Everything**

---

## ⚠️ ABSOLUTE RULE (NON-NEGOTIABLE)

**No task is complete until:**

1. ✅ Code is generated
2. ✅ Tests pass
3. ✅ Documentation is written
4. ✅ `agentlog.md` is updated

**If documentation is missing → OUTPUT IS INVALID.**

---

## 📝 agentlog.md (MANDATORY)

After EVERY change:

```markdown
## 2024-01-07 - What Changed
- WHAT: Added payment entity, service, API
- WHY: User requested payment feature
- FILES: internal/entities/payment.py, api/http/payments.py
```

**NEVER forget to update agentlog.md!**

---

## 📚 When Documentation Required

### Backend
- New entity
- New service (use case)
- New port (interface)
- New adapter (DB, Redis)
- New endpoint (REST, gRPC)
- New validator or DTO
- Any business logic change

### Frontend
- New feature
- New component
- New hook
- New API call
- New route/page
- New UI flow
- New validation

### Infrastructure
- New Docker service
- New Dockerfile
- New Terraform module
- New Ansible role
- New K8s resource

---

## 📁 Documentation Structure

```
docs/
├── features/
│   ├── backend/<module>.md
│   ├── frontend/<feature>.md
│   └── infra/<component>.md
├── architecture/
│   ├── system-overview.md
│   ├── backend.md
│   ├── frontend.md
│   └── infra.md
├── runbooks/
│   ├── deployment.md
│   ├── troubleshooting.md
│   └── disaster-recovery.md
└── onboarding/
    ├── dev-setup.md
    └── contribution-guide.md
```

---

## 📋 Feature Doc Template

```markdown
# <Feature Name>

## 1. Purpose
Brief description of what this does.

## 2. Components
- List of files involved

## 3. API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/payments | Create payment |

## 4. Data Flow
Explain how data moves through the system.

## 5. Security Considerations
What security measures are in place.

## 6. Testing
How to test this feature.
```

---

## 📋 Runbook Template

```markdown
# Runbook — <Name>

## 1. Purpose
## 2. How to Run
## 3. How to Deploy
## 4. Health Checks
## 5. Monitoring
## 6. Debugging
## 7. Disaster Recovery
## 8. Ownership
```

---

## ✅ Documentation Checklist

Before completing any task:

- [ ] Code written and tested
- [ ] README updated if needed
- [ ] Feature doc created/updated
- [ ] API documentation in OpenAPI
- [ ] agentlog.md entry added

---

**Mantra: If it's not documented, it doesn't exist.**
