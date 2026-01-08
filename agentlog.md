# Agent Log

## 2026-01-08

- Started debugging Lich MCP setup issue.
- Fixed `lich setup antigravity` config path to point to `~/.gemini/antigravity/mcp_config.json` instead of `settings.json`.
- Updated documentation and prepared release v1.7.9.
- Added `--no-cache-dir` to `lich upgrade` to prevent "distribution not found" errors.
- **UX Improvement**: `lich upgrade` now automatically restarts itself after updating the CLI.
- **UX Improvement**: Added a prominent reminder to run `lich setup` after upgrading.
- Released v1.8.0 containing these UX improvements.
- Released v1.8.1 to fix CI/CD pipeline issues (lint and tests).
