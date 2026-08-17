# Installation

## Requirements

- Cursor (or another agent that loads Agent Skills from a skills directory)
- Python **3.10+** on `PATH` (`python` or `py -3`)
- No `pip install` for core hard gates (stdlib only)

## Path A — Personal skill (recommended)

Install the standalone core in all projects:

```powershell
# Windows
./install.ps1 -Skills skill-self-check
# or
./install.ps1 -Skills skill-self-check -Force
```

```bash
# macOS / Linux
chmod +x install.sh
./install.sh --skills skill-self-check
# or
./install.sh --skills skill-self-check --force
```

Omit `-Skills` / `--skills` only when you want the complete optional suite.
The default all-suite destinations are:

- `~/.cursor/skills/skill-self-check`
- `~/.cursor/skills/skill-ship-safety`
- `~/.cursor/skills/agent-work-readiness`

## Path B — Project skill

Shared with anyone using the repo:

```powershell
./install.ps1 -Project . -Skills skill-self-check
```

```bash
./install.sh --project . --skills skill-self-check
```

The core destination is `<project>/.cursor/skills/skill-self-check`. Omit the
skill selector to install all three destinations:

- `<project>/.cursor/skills/skill-self-check`
- `<project>/.cursor/skills/skill-ship-safety`
- `<project>/.cursor/skills/agent-work-readiness`

## Path C — Manual copy

```bash
cp -R skills/skill-self-check ~/.cursor/skills/skill-self-check
```

Optional enhancements:

```bash
cp -R skills/skill-ship-safety ~/.cursor/skills/skill-ship-safety
cp -R skills/agent-work-readiness ~/.cursor/skills/agent-work-readiness
```

For another AI/Agent platform, copy each skill directory into that platform's
documented skill location. The static Python scripts are platform-neutral;
automatic discovery, invocation fields, and safe execution capabilities are
platform-specific.

## Do not install into

`~/.cursor/skills-cursor/` — reserved for Cursor built-ins.

## Verify

Run the standalone fast deterministic gate:

```bash
python ~/.cursor/skills/skill-self-check/scripts/hard_gates.py \
  path/to/any-skill \
  --out-json "$HOME/Documents/skill-audits/first-run/hard-gates.json" \
  --pretty
```

Read `gate_verdict`, `gate_reasons`, every Critical, and the highest-priority
Should-fix items. Numeric scores are informational only.

The output directory must be outside the audited Skill and its source
repository.

The full runner remains available when an explicit request requires structure
and static safety checks in one JSON-only report set:

```bash
python ~/.cursor/skills/skill-self-check/scripts/run_full_audit.py \
  path/to/any-skill \
  --out-dir "$HOME/Documents/skill-audits/full-report" \
  --pretty
```

Or against the bundled fixture from this repo:

```bash
python skills/skill-self-check/scripts/hard_gates.py \
  skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty
```

`skill-ship-safety` performs static safety checks only:

```bash
python skills/skill-ship-safety/scripts/ship_safety.py \
  path/to/any-skill --pretty
```

The compatibility flag `--exec` does not execute target code. It reports that
trusted isolated behavior evidence is still required.

Assess one business work package:

```bash
python skills/agent-work-readiness/scripts/readiness_gates.py \
  path/to/work-package --out readiness.json --pretty
```

Real reports should be written outside the public repository. Do not commit
client names, full local paths, raw evidence, or credentials.

## Force-install safety

`-Force` / `--force` only accepts a target whose final directory name matches
the skill being installed. Drive roots, filesystem roots, the user home, and
the repository root are rejected.

## Experiments

Folders under `exp/` are **not** installed by `install.*`. Copy them manually
only if you are piloting PM workflow drafts.
