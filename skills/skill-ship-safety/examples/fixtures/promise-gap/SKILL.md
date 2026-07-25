---
name: promise-gap
description: Bad fixture for ship-safety audits. Documents commands its script does not implement and ships a sender with no dry-run guard. Use when smoke-testing scripts/ship_safety.py.
---

# Promise Gap (bad fixture)

A deliberately broken skill: the docs promise more than the code delivers.

## Commands

```bash
python3 scripts/ops.py check_lead <email>
python3 scripts/ops.py confirm_win <email>
python3 scripts/missing_tool.py sync
```

Expected ship-safety findings:

- `CMD.2` — `confirm_win` is documented but not implemented in `ops.py`
- `CMD.1` — `scripts/missing_tool.py` does not exist
- `EXT.1` — `ops.py` imports smtplib with no dry-run guard
- Verdict: `stop_ship`
