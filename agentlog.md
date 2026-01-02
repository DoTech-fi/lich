# Lich Toolkit - Agent Log

## 2026-01-02T14:45:00 - v1.3.0 Complete Update

**What Changed**:
- CLI v1.3.0: Added `lich make factory/middleware/event/listener/job/policy`
- Pre-built middlewares: RateLimit, Logging, Security, Timing (opt-in)
- Comprehensive test suite: 39 tests for all CLI commands
- Wiki documentation: CLI_REFERENCE, AUTH_AND_POLICY, MIDDLEWARE_GUIDE, EVENTS_LISTENERS, BACKGROUND_JOBS, AUTHORIZATION_POLICIES
- AI_RULES.md: Complete rules for AI agents
- AI_ENFORCEMENT.md: Guide on forcing AI to follow rules
- Template rules updated: lich-cli.md, backend.md, master-prompt.md

**Why Changed**:
User requested complete CLI expansion with documentation for juniors and AI agents

---

## 2026-01-02T01:00:00 - Comprehensive QA & Enhancements

**What Changed**: 
- Added TLS/Let's Encrypt support (`use_tls` option)
- Created QUICK_START.md with dynamic service URLs
- Updated post_gen hook to show all service URLs
- Fixed docker-compose.yml (proper YAML quoting)
- Fixed tsconfig.json (moduleResolution: node)
- Added unit tests (test_user_entity, test_user_service, test_dto_validation)
- Added integration tests (test_api_integration)
- Added pytest.ini configuration
- Cleaned cookiecutter.json (English only)
- Changed default_language to 'en' first

**Why Changed**:
User requested comprehensive QA check and test coverage

---

## 2026-01-01T21:09:00 - Added Auth Pages

**What Changed**: 
- Login, Register, Forgot Password, Dashboard, Profile, Settings pages

---

## 2026-01-01T20:01:00 - Enhanced with Additional Features

**What Changed**: 
- API client, AuthContext, CI/CD, Dockerfile, Sidebar/Header components

---

## 2026-01-01T19:36:00 - Initial Creation

**What Changed**: 
- Complete Cookiecutter template for Lich Toolkit
