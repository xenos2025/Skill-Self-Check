# Contributing

Thanks for helping improve Skill Self-Check.

## Getting started

1. Fork and clone `https://github.com/xenos2025/Skill-Self-Check.git`.
2. Use **Python 3.10+**. Core scripts are **stdlib only** (no `pip install` for
   product paths under `skills/`).
3. Install the three shipped skills locally:

```powershell
./install.ps1 -Force
```

```bash
chmod +x install.sh && ./install.sh --force
```

4. Smoke the structure gates against the bundled bad fixture:

```bash
python skills/skill-self-check/scripts/hard_gates.py \
  skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty
```

Expect `basic_usable 2/5`, `contract_clarity 0/5`, `ship_floor_met: false`, and
Critical findings (the fixture must keep failing).

5. Run the full regression suite (mirrors CI intent; prefer this locally):

```bash
python -m unittest discover tests -v
```

Individual entry points when you touch one area:

```bash
python tests/test_hard_gates.py
python tests/test_ship_safety.py
python tests/test_readiness_gates.py
python tests/test_full_audit_runner.py
python tests/test_verify_fix.py
```

6. When a change edits a shipped `SKILL.md`, show the delta instead of claiming
   the findings are gone. Capture the baseline **before** editing:

```bash
python skills/skill-self-check/scripts/hard_gates.py \
  skills/<edited-skill> > "$HOME/skill-audits/baseline.json"

# ... make the edits ...

python skills/skill-self-check/scripts/verify_fix.py \
  skills/<edited-skill> \
  --baseline "$HOME/skill-audits/baseline.json" --pretty
```

Exit code 1 means a hard regression (new Critical, severity escalation, lost
ship floor, or a score drop). Paste the `verdict`, resolved / introduced counts,
and `remaining_critical` into the PR. Add `--strict` to also fail on newly
surfaced non-critical findings.

7. Optional: run the full static audit pack (output **must** stay outside the
   repository):

```bash
python skills/skill-self-check/scripts/run_full_audit.py \
  skills/skill-self-check \
  --out-dir "$HOME/Documents/skill-audits/contrib-demo" --pretty
```

## Project structure

```text
skills/                      # product skills (installable)
  agent-work-readiness/      # oral process → B0–B6 work package
  skill-self-check/          # static structure / contract audit + run_full_audit
  skill-ship-safety/         # static external-action preflight
exp/                         # experiments — NOT installed by default
  pm-workflow-planning/      # PM / interview → workflow hook
tests/                       # stdlib regression suite
assets/diagrams/             # README SVGs (zh/ for Chinese)
docs/                        # architecture, installation, platform matrix, …
install.ps1 / install.sh
plugin.json                  # lists the three shipped skill folder names
```

Shipped skill names are the source of truth in `plugin.json` → `skills`.

## Making changes

- **Stable product** lives under `skills/`. Keep each `SKILL.md` short; put long
  contracts, fixtures, and templates in sibling files.
- **Experiments** live under `exp/`. Do not promote an experiment into `skills/`
  without a ship-floor self-check pass and a CHANGELOG note.
- **Scores and verdicts are script-owned.**
  - Structure scores → `skill-self-check/scripts/hard_gates.py`
  - Safety verdict → `skill-ship-safety/scripts/ship_safety.py`
  - Business readiness B0–B6 → `agent-work-readiness/scripts/readiness_gates.py`
  - Before/after fix deltas → `skill-self-check/scripts/verify_fix.py`
  - Never invent numeric scores or soften a stricter script verdict in prose.
- Built-in audit scripts are **read-only** toward the target Skill: they must not
  execute target code or send external messages. Real audit and client
  reports stay in a private directory outside this repository.
- Scoring / gate changes need green tests, fixture updates when behavior
  changes, and refreshed smoke numbers in
  `skills/skill-self-check/examples/smoke-report-before.md` (and the business
  twin when that report’s numbers move).
- Update `CHANGELOG.md` under `[Unreleased]` for user-visible behavior or docs.
- Never commit secrets, client PII, store tokens, filled export CSVs, or private
  audit JSON from real engagements.

## Platform notes

Portable Level B assumes local files + Python 3.10+. Maintainer evidence and the
Cursor / Codex / other platform matrix live in
[docs/PLATFORM-COMPATIBILITY.md](docs/PLATFORM-COMPATIBILITY.md). Cross-platform
“verified” claims need two distinct platforms sharing the same contract and
fixture SHA-256 identifiers — do not treat “ran once on my machine” as enough.

## Python style

- `from __future__ import annotations` in new scripts
- stdlib only unless a dependency is strongly justified **and** this file plus
  `plugin.json` / docs are updated
- `argparse` CLIs; meaningful non-zero exit codes on failure
- Prefer `pathlib.Path`
- Force UTF-8 on stdout/stderr when emitting Chinese JSON for agents

## Pull requests

1. Branch from `main`.
2. Keep the PR focused (one concern when possible).
3. Describe **why** the change is needed; link issues if any.
4. For scoring or gate changes, paste before/after script JSON (or a short
   excerpt) on a fixture.
5. Confirm `python -m unittest discover tests -v` is green.
6. Follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Report vulnerabilities privately per [SECURITY.md](SECURITY.md). Do not open
public issues for security findings.
