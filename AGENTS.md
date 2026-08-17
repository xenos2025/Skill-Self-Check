# AGENTS.md

Guidance for coding agents working **on this repository**.

> Scope: this file configures agents editing the skill-self-check pack itself.
> End users install skills from `skills/`; they do not need to copy this file.

## Layout

| Path | Role |
| --- | --- |
| `skills/` | Installable product skills (three shipped names in `plugin.json`) |
| `skills/agent-work-readiness/` | Oral process → B0–B6 work package |
| `skills/skill-self-check/` | Structure/contract audit + `run_full_audit.py` |
| `skills/skill-ship-safety/` | Static external-action preflight |
| `exp/` | Experiments — do not install by default; may be unstable |
| `tests/` | Stdlib regression suite (mirrors CI intent) |
| `docs/` | Human docs including platform compatibility |
| `install.ps1` / `install.sh` | Copy shipped skills into Cursor skills dirs |

## Rules

1. Prefer editing the relevant skill under `skills/` for product behavior.
2. Put speculative PM / industry workflow work under `exp/`, not `skills/`.
3. Hard-gate, ship-safety, and readiness results come from their scripts
   only — never invent scores in prose without running the script.
4. Keep Python stdlib-only unless CONTRIBUTING is updated.
5. Do not commit secrets, client PII, or real audit reports inside this repo.
6. After scoring logic changes, run the matching tests (or
 `python -m unittest discover tests -v`), note before/after in the PR, and
 refresh smoke reports when hard-gate numbers move.
7. After editing a shipped Skill's `SKILL.md`, capture a `hard_gates.py`
 baseline first and report the `verify_fix.py` delta instead of asserting the
 findings are fixed.
8. Real audit `--out-dir` values must stay outside the audited Skill and
   this source repository.

## Quick commands

```bash
python -m unittest discover tests -v
python skills/skill-self-check/scripts/hard_gates.py skills/skill-self-check --pretty
python skills/skill-self-check/scripts/hard_gates.py \
  skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty
python skills/skill-ship-safety/scripts/ship_safety.py skills/skill-self-check --pretty
python skills/skill-self-check/scripts/hard_gates.py skills/skill-self-check \
 > "$HOME/Documents/skill-audits/baseline.json"
python skills/skill-self-check/scripts/verify_fix.py skills/skill-self-check \
 --baseline "$HOME/Documents/skill-audits/baseline.json" --pretty
python skills/skill-self-check/scripts/run_full_audit.py skills/skill-self-check \
  --out-dir "$HOME/Documents/skill-audits/agent-demo" --pretty
```
