# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.15.x  | ✅                 |
| 1.13.x – 1.14.x | ✅ security fixes only |
| < 1.13  | ❌ (upgrade — versions before 1.13.0 contain known vulnerabilities fixed in the 2026-07 hardening releases) |

## Reporting a Vulnerability

Please **do not open a public GitHub issue** for security vulnerabilities.

Email **babak@dotech.fi** with:
- A description of the vulnerability and its impact
- Steps to reproduce (a minimal PoC helps)
- The version you tested (`lich version`)

You will get an acknowledgement within **72 hours** and a status update within
**14 days**. Once a fix ships, we credit reporters in the changelog unless you
prefer to stay anonymous.

## Scope

- `lich` CLI (PyPI package, `cli/`)
- The Lich MCP server (`lich serve`)
- The project template (`template/`) — vulnerabilities in freshly generated
  projects count; vulnerabilities you introduce after generation do not.

## Hardening Baseline

Since v1.13.0, all subprocess calls use list arguments (no `shell=True`),
user input is validated at CLI/MCP boundaries, and generated projects refuse
to start in production with placeholder secrets. CI runs bandit and pip-audit
on every PR.
