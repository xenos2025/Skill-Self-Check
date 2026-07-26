# Installation

## Requirements

- Cursor (or another agent that loads Agent Skills from a skills directory)
- Python **3.10+** on `PATH` (`python` or `py -3`)
- No `pip install` for core hard gates (stdlib only)

## Path A — Personal skill (recommended)

Available in all projects:

```powershell
# Windows
./install.ps1
# or
./install.ps1 -Force
```

```bash
# macOS / Linux
chmod +x install.sh
./install.sh
# or
./install.sh --force
```

Default destinations:

- `~/.cursor/skills/skill-self-check`
- `~/.cursor/skills/skill-ship-safety`
- `~/.cursor/skills/agent-work-readiness`
- `~/.cursor/skills/skill-growth-scorecard`

## Path B — Project skill

Shared with anyone using the repo:

```powershell
./install.ps1 -Project .
```

```bash
./install.sh --project .
```

Destinations:

- `<project>/.cursor/skills/skill-self-check`
- `<project>/.cursor/skills/skill-ship-safety`
- `<project>/.cursor/skills/agent-work-readiness`
- `<project>/.cursor/skills/skill-growth-scorecard`

## Path C — Manual copy

```bash
cp -R skills/skill-self-check ~/.cursor/skills/skill-self-check
cp -R skills/skill-ship-safety ~/.cursor/skills/skill-ship-safety
cp -R skills/agent-work-readiness ~/.cursor/skills/agent-work-readiness
cp -R skills/skill-growth-scorecard ~/.cursor/skills/skill-growth-scorecard
```

For another AI/Agent platform, copy each skill directory into that platform's
documented skill location. The static Python scripts are platform-neutral;
automatic discovery, invocation fields, and safe execution capabilities are
platform-specific.

## Do not install into

`~/.cursor/skills-cursor/` — reserved for Cursor built-ins.

## Verify

Run the full read-only audit and create both scorecards:

```bash
python ~/.cursor/skills/skill-self-check/scripts/run_full_audit.py \
  path/to/any-skill \
  --out-dir "$HOME/Documents/skill-audits/first-run" \
  --pretty
```

The output directory must be outside the audited Skill and its source
repository. The result includes `audit-manifest.json`,
`personal-scorecard.html`, and `project-scorecard.html`.

To run only the structure gate:

```bash
python ~/.cursor/skills/skill-self-check/scripts/hard_gates.py \
  path/to/any-skill --pretty
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

Assess one business work package, then optionally generate an offline scorecard:

```bash
python skills/agent-work-readiness/scripts/readiness_gates.py \
  path/to/work-package --out readiness.json --pretty

python skills/skill-growth-scorecard/scripts/profile_engine.py \
  --readiness readiness.json \
  --hard-gates hard-gates.json \
  --ship-safety ship-safety.json \
  --out-json profile.json \
  --out-html scorecard.html
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
