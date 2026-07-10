# Lich Roadmap — Master Execution Guide

> **Read this FIRST** before executing any plan in this directory. It tells you the order, the rules, the known traps, and what to double-check. Written 2026-07-10 by the planning session (Fable); execution is expected to run on Sonnet (implementer) with Opus (reviewer) — but any capable model can follow it.

## Current State (2026-07-10)

- Lich v1.12.15 on PyPI. Full code review scored it **6.5/10**: real hexagonal architecture, good DX, but shell injection in `deploy.py`, 5 failing tests, sync MCP tools, template bugs. Findings live in the specs below.
- **Nothing from these plans is implemented yet.** All documents are committed on `main`.
- Local test suite state: `cd cli && python3 -m pytest -q` → 75 passed, 5 failed (the 5 are fixed by v1 Phase 2).

## Document Map

| Document | Role |
|----------|------|
| `2026-07-10-CONTRACTS.md` | **FROZEN cross-plan interfaces — required reading before any v2 plan; contracts win over plan text** |
| `../specs/2026-07-10-lich-v1-hardening-design.md` | v1 spec — WHY and WHAT for phases 1–4 |
| `../specs/2026-04-14-lich-v2-design.md` | v2 spec — full vision, 12 features, Phase 0 + decisions log D1–D16 |
| `2026-07-10-v1-hardening-phase1-security.md` | v1.13.0 — EXECUTE FIRST |
| `2026-07-10-v1-hardening-phase2-correctness.md` | v1.13.1 |
| `2026-07-10-v1-hardening-phase3-quality.md` | v1.14.0 |
| `2026-07-10-v1-hardening-phase4-gates.md` | v1.15.0 |
| `2026-07-10-v2-phase0-lich-core.md` | DRAFT — lich-core runtime package |
| `2026-07-10-v2-phase1a-codegen-ai.md` | DRAFT — smart codegen + BYOA AI adapters |
| `2026-07-10-v2-phase1b-tui-concepts-memory.md` | DRAFT — TUI + concepts + memory write path |
| `2026-07-10-v2-phase2-4-quality-plugins-deploy.md` | DRAFT — self-validation, plugins, deploy |

## Execution Order

```
v1 P1 (security) → v1 P2 (correctness) → v1 P3 (quality) → v1 P4 (gates)
                                                              │
                     v2 P0 (lich-core) ←──────────────────────┘  (P0 tasks 13–14 need v1 P4's e2e harness)
                     v2 P1a (codegen+AI) — can start after v1 P3 (its make.py wiring assumes common.py exists)
                     v2 P1b (TUI+memory) — after P1a (Task 9 imports AIProvider from 1a)
                     v2 P2–4 — after P1b, with reconciliation (see Known Conflicts)
```

Strict rules:
1. **v1 phases run in order 1→2→3→4.** Each phase = its own branch + PR, ends with suite green + changelog + version bump.
2. **v2 Phase 0 tasks 1–12 are greenfield** and may run in parallel with late v1 phases if desired; tasks 13–14 are [RE-VERIFY] and blocked on v1 P4.
3. **Never publish to PyPI without Babak's explicit go.** Plans end at "commit + tag handoff", release is a human decision.

## Model Strategy (senior/junior)

- **Implementer:** Claude Sonnet, fresh session per phase. Use `superpowers:subagent-driven-development` (preferred) or `superpowers:executing-plans`.
- **Reviewer:** Opus (or better) between phases — see Opus Checklist below.
- Launch prompt template for a phase:
  > Execute the plan at `docs/superpowers/plans/<file>` task-by-task using the superpowers:subagent-driven-development skill. Follow TDD steps exactly. If a step's expected output doesn't match reality, STOP and report — do not force assertions to pass. Do not publish to PyPI.

## STOP Conditions (implementer must halt and report)

- A verification step's expected output doesn't match (plan may be stale — especially [RE-VERIFY] tasks).
- Coverage gate in v1 P4 fails because P3 didn't reach 80% — do NOT lower the gate.
- Any test that passed before a task fails after it in an unrelated area.
- A [RE-VERIFY] task's target file differs from the plan's snippet.

## Known Traps (discovered during planning)

1. **claude-mem PreToolUse:Read hook truncates repeat Reads to 1 line** in some sessions. If Read returns suspiciously little, use `cat`/`sed` via Bash instead. Two planning forks hit this.
2. **Session limits kill agents but files survive.** If an executing agent dies, check disk state before redoing work; batch-commit recovered files.
3. **5 pre-existing test failures** until v1 P2 lands — v1 P1's completion task documents this; don't "fix" them in P1.
4. **`.lich` is a FILE in v1 projects**, but the v2 memory vault wants `.lich/memory/` (directory). Phase 1b defines `_vault_dir()` with a `.lich-memory/` fallback — do not "simplify" it away.
5. **Dockerfile healthcheck in the template is broken** (curl not in slim image, wrong path) — fixed as v1 P4 Task 1; e2e cannot pass without it.

## Known Conflicts Between Plans (reconcile at execution time)

The v2 plans were written by parallel authors; these overlaps are REAL and must be reconciled:

1. **`cli/src/lich/memory/index.py`** — **RESOLVED 2026-07-10 via `2026-07-10-CONTRACTS.md` §C3** (option A, dual API): P1b's instance API is canonical; P2–4 Task 2.3 was rewritten to EXTEND it (`@classmethod build()`, `resolve_mentions()`, `walk()` returning note names; edges migrate `list`→`set`; no `@classmethod load(path)` — name-clash). Task 2.4's assembler was aligned (reads bodies via `notes.read_note`). Executors follow the contract file, not older drafts.
2. **`cli/src/lich/cli.py` wiring** — touched by v2 P1a Task 16 (`lich config`), P1b Task 4 (`lich memory`) and Task 11 (`lich tui`). Sequential execution is fine; each task adds one `add_typer` line. Conflict only if run out of order.
3. **`make.py`** — modified by v1 P1 (identifier validation), v1 P3 (common.py extraction), v2 P1a Task 12 (`--fields` wiring), v2 P1b Task 10 (TUI import). Execute in that order; each later task must re-read the file ([RE-VERIFY] marks say so).

## Opus Double-Check Checklist (before executing each v2 plan)

- [ ] Re-read every **[RE-VERIFY]** task against the file as it exists post-v1-hardening; update snippets/line refs.
- [ ] Verify every v2 plan task against `2026-07-10-CONTRACTS.md` — any task that contradicts a contract is wrong; fix the task, not the contract.
- [ ] ~~Open questions~~ — ALL FOUR resolved 2026-07-10: versioning (D17), marketplace home (D18), guardian fix scope (D19), FairBroker/Zenith deploy contract (D20 — FairBroker interface-only until it exposes a provisioning API; Zenith verified READY via REST API). Verify the resolutions still hold at execution time.
- [ ] Reconcile `memory/index.py` designs (Known Conflict 1).
- [ ] Sanity-check the 9 Jinja templates in P1a against the template backend as it exists after v1 P2's template fixes.
- [ ] Confirm lich-core extras/deps in P0 Task 1 still match template requirements after v1 changes.
- [ ] Spot-run 2–3 plan tasks' verification commands to confirm the plan's expected outputs are still accurate.

## Success Criteria (the finish line)

**v1 done (after P4):** CI green 3.10–3.12, coverage ≥80% enforced, bandit+pip-audit clean, golden-path e2e green (both matrix combos), MCP protocol smoke green, tool-count claims accurate. Target score on re-review: 9+/10.

**v2 Phase 0+1 done:** `pip install lich-core` works; generated project boots via `create_app()`; `lich make entity X --fields "..."` generates the full hexagonal slice; `lich tui` describe→review→generate flow works with at least Claude CLI and the local OpenAI-compat adapter (Qwen); `.lich/memory/` opens cleanly as an Obsidian vault with entity/decision notes.
