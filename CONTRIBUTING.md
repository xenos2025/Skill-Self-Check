# Contributing

Thanks for helping improve Skill Self-Check.

## Getting started

1. Fork and clone `https://github.com/xenos2025/Skill-Self-Check.git`.
2. Use **Python 3.10+** (stdlib only for `hard_gates.py`; no `pip install` for core paths).
3. Install locally:

```powershell
./install.ps1 -Force
```

```bash
chmod +x install.sh && ./install.sh --force
```

4. Smoke the script against the bundled fixture:

```bash
python skills/skill-self-check/scripts/hard_gates.py \
  skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty
```

Expect `ship_floor_met: false` and Critical findings on name/description.

## Project structure

```text
skills/                 # product skills (installable)
  skill-self-check/     # stable self-check skill
exp/                    # experiments — NOT installed by default
  pm-workflow-planning/ # future PM / workflow productization hook
docs/                   # architecture, installation, audience, design
install.ps1 / install.sh
plugin.json
```

## Making changes

- **Stable product** lives under `skills/`. Keep `SKILL.md` short; put long checklists in sibling files.
- **Experiments** live under `exp/`. Do not promote an experiment into `skills/` without a ship-floor self-check pass and a CHANGELOG note.
- **Hard gates and scores are script-owned.** Change scoring only in `scripts/hard_gates.py` with a fixture update; do not ask the model to invent numbers.
- Update `CHANGELOG.md` under `[Unreleased]` for user-visible behavior or docs changes.
- Never commit secrets, client PII, store tokens, or filled export CSVs.

## Python style

- `from __future__ import annotations` in new scripts
- stdlib only unless a dependency is strongly justified
- `argparse` CLIs; meaningful non-zero exit codes on failure
- Prefer `pathlib.Path`

## Pull requests

1. Branch from `main`.
2. Keep the PR focused (one concern when possible).
3. Describe **why** the change is needed; link issues if any.
4. Include script output for scoring changes (before/after on a fixture).
5. Follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Report vulnerabilities privately per [SECURITY.md](SECURITY.md). Do not open public issues for security findings.
