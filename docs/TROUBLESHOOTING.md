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
3. Chinese descriptions are supported: `用于` / `适用` / `当用户` / `使用场景`
   count as WHEN triggers, and `何时不用` / `不适用` count as exclusions. If a
   Chinese skill still fails 1.7, the description likely states only a topic
   with no trigger phrase at all.

## Chinese text comes out as garbage (`���ɫ`)

The script forces UTF-8 on stdout, so garbled text means something downstream
re-decoded it. Write the JSON to a file instead of scraping a legacy console —
and note that PowerShell 5.1 `>` writes **UTF-16**, which breaks JSON readers:

```powershell
py -3 skills/skill-self-check/scripts/hard_gates.py path/to/skill --pretty |
  Out-File -Encoding utf8 report.json
```

## Finding `1.11` — SKILL.md is not UTF-8

The file decoded as GBK/Big5/CP1252 rather than UTF-8. Scoring still runs (the
script falls back instead of crashing), but re-save the file as UTF-8: other
agent tooling assumes it.

## `ship_floor_met: false` but the skill “feels fine”

Ship floor is intentionally strict. Fix script Criticals first; qualitative
polish comes after.

## Installer says destination exists

Pass `-Force` / `--force`, or remove the old copy manually.
