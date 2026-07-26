# AGENTS.md

Guidance for coding agents working **on this repository**.

> Scope: this file configures agents editing the skill-self-check pack itself.
> End users install skills from `skills/`; they do not need to copy this file.

## Layout

| Path | Role |
| --- | --- |
| `skills/` | Installable product skills |
| `exp/` | Experiments — do not install by default; may be unstable |
| `tests/` | Stdlib regression tests for `hard_gates.py` and `ship_safety.py` (mirrors CI) |
| `docs/` | Human docs |
| `install.ps1` / `install.sh` | Copy `skills/skill-self-check` into Cursor skills dirs |

## Rules

1. Prefer editing `skills/skill-self-check/` for product behavior.
2. Put speculative PM / industry workflow work under `exp/`, not `skills/`.
3. Hard-gate scores come from `scripts/hard_gates.py` only — never invent scores in prose without running the script.
4. Keep Python stdlib-only unless CONTRIBUTING is updated.
5. Do not commit secrets or client PII.
6. After scoring logic changes, run `tests/test_hard_gates.py`, run the bad-commit-helper fixture, note before/after in the PR, and refresh `examples/smoke-report-before.md`.

## Quick commands

```bash
python tests/test_hard_gates.py
python tests/test_ship_safety.py
python skills/skill-self-check/scripts/hard_gates.py skills/skill-self-check --pretty
python skills/skill-self-check/scripts/hard_gates.py skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty
```
