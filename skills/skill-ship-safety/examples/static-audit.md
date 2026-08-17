# Static audit example

Use this Skill before the first real external action. The audit inspects the
target package but does not run its sender.

```bash
python scripts/ship_safety.py path/to/target-skill --pretty
```

Interpret the result conservatively:

- `static_pass` means the documented static gates were found.
- `stop` means a blocking static defect was found.
- `not_safely_verified` means isolated behavior evidence is still missing.

Do not convert a static pass into authorization for a live send. Complete the
trusted isolated behavior test and obtain the required human approval first.
