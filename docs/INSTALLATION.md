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

Default destination: `~/.cursor/skills/skill-self-check`.

## Path B — Project skill

Shared with anyone using the repo:

```powershell
./install.ps1 -Project .
```

```bash
./install.sh --project .
```

Destination: `<project>/.cursor/skills/skill-self-check`.

## Path C — Manual copy

```bash
cp -R skills/skill-self-check ~/.cursor/skills/skill-self-check
```

## Do not install into

`~/.cursor/skills-cursor/` — reserved for Cursor built-ins.

## Verify

```bash
python ~/.cursor/skills/skill-self-check/scripts/hard_gates.py \
  path/to/any-skill --pretty
```

Or against the bundled fixture from this repo:

```bash
python skills/skill-self-check/scripts/hard_gates.py \
  skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty
```

## Experiments

Folders under `exp/` are **not** installed by `install.*`. Copy them manually
only if you are piloting PM workflow drafts.
