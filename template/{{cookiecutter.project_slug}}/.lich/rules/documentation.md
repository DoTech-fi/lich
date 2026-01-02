# Documentation Architecture Rules

> **MANDATORY**: Documentation is required for ALL new code. No exceptions.

## Core Principles

```
📝 DOCUMENT AS YOU CODE
🎯 AUDIENCE-FOCUSED  
🔄 KEEP IT UPDATED
📖 EXAMPLES OVER THEORY
```

---

## 1. Documentation is ALWAYS Required For

### Frontend
- New feature, component, hook
- New service/API call
- New route or page
- New UI flow, state logic
- New validation rules

### Backend
- New entity, service (use case)
- New port (interface), adapter
- New endpoint (REST, gRPC)
- New validator or DTO
- Any business logic change

### Infrastructure
- New Terraform module/variable/output
- New Ansible role/task
- New Docker service/Dockerfile
- New Kubernetes resource
- New secret or config

---

## 2. Documentation Folder Structure

```
docs/
├── runbooks/
│   ├── frontend/
│   ├── backend/
│   └── infra/
├── features/
│   ├── frontend/<feature>.md
│   ├── backend/<module>.md
│   └── infra/<component>.md
├── architecture/
│   ├── system-overview.md
│   ├── frontend-architecture.md
│   ├── backend-architecture.md
│   └── infra-architecture.md
├── troubleshooting/
│   ├── frontend.md
│   ├── backend.md
│   └── infra.md
└── onboarding/
    ├── dev-setup.md
    ├── contribution-guide.md
    └── workflows.md
```

---

## 3. Runbook Template

Every feature/module MUST have a runbook:

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
## 9. Change History
```

---

## 4. Frontend Feature Doc Template

```markdown
# <Feature Name> (Frontend Feature Doc)

## 1. Overview
## 2. UI/UX Flow
## 3. Data Flow
## 4. Components
## 5. Services/API
## 6. Hooks
## 7. State Logic
## 8. Edge Cases
## 9. Security Considerations
## 10. Testing Strategy
## 11. Future Improvements
```

---

## 5. Backend Module Doc Template

```markdown
# <Module Name> (Backend Module Doc)

## 1. Purpose
## 2. Entities
## 3. Services (Use Cases)
## 4. Ports
## 5. Adapters
## 6. API Endpoints
## 7. Validation Rules
## 8. Security Model
## 9. Testing Strategy
## 10. Future Improvements
```

---

## 6. Infra Module Doc Template

```markdown
# <Infra Component>

## 1. Purpose
## 2. Architecture
## 3. Inputs (Variables)
## 4. Outputs
## 5. Security Rules
## 6. Deployment Steps
## 7. Rollback
## 8. Monitoring & Alerts
## 9. Change History
```

---

## 7. agentlog.md (Required!)

Always update `agentlog.md` with:
- **WHAT** changed
- **WHY** it changed  
- **WHEN** (timestamp)

---

## 8. Completion Rule

**No task is complete until:**
1. Code is generated
2. Documentation is generated
3. `agentlog.md` is updated

If documentation is missing → Output is INVALID.

---

> **Mantra**: Simple → Clear → Current
