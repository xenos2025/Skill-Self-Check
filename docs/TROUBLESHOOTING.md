# Troubleshooting

## `python` not found

Try `py -3` on Windows, or install Python 3.10+.

```powershell
py -3 skills/skill-self-check/scripts/hard_gates.py path\to\skill --pretty
```

## Skill not showing up in Cursor

- Confirm install path is `~/.cursor/skills/skill-self-check` or
  `<project>/.cursor/skills/skill-self-check`
- Restart the agent session after install
- Do not install under `~/.cursor/skills-cursor/`

## Scores look wrong

1. Re-run the script; do not trust remembered numbers.
2. Confirm you pointed at the **skill directory** (folder containing `SKILL.md`),
   not a parent monorepo root.
3. Chinese-only descriptions may fail WHEN detection today — add `Use when...`
   or track the Chinese-trigger TODO in [TODO.md](../TODO.md).

## `ship_floor_met: false` but the skill “feels fine”

Ship floor is intentionally strict. Fix script Criticals first; qualitative
polish comes after.

## Installer says destination exists

Pass `-Force` / `--force`, or remove the old copy manually.
