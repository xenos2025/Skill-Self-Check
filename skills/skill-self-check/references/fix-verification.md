# Fix Verification

Read this reference only after the user explicitly authorizes edits.

## Before editing

Save `hard_gates.py` stdout JSON outside the target Skill and source
repository. This is the baseline.

## After editing

```bash
python scripts/verify_fix.py /absolute/path/to/target-skill \
  --baseline /private/path/baseline.json \
  --pretty
```

If the baseline is missing, say so. Run `hard_gates.py` once and report a plain
after-state only; never invent the before-state.

## Interpret the result

| Field | Meaning | Required action |
| --- | --- | --- |
| `verdict: improved` | Improvement with no hard regression | Deliver and list every introduced finding |
| `verdict: unchanged` | Scores and findings did not move | Confirm the edit landed and the checks cover it |
| `verdict: mixed` | Some improvement and some regression | Fix `new_critical`; retry at most once, then stop and report remaining work |
| `verdict: regressed` | New Critical or gate regression | Revert the current edit |
| `gates.gate_verdict` | Authoritative before/after gate | Report this before informational scores |
| `findings.introduced` | Findings visible only after the edit | Fix or explicitly list each item |
| `scores.*.direction` | Informational score movement | Explain only; never change the verdict |
| `direction: not_comparable` | The dimension maximum changed | Report changed applicability, not gain/loss |

Non-Critical introduced findings do not block delivery, but they must be
reported. Use `--strict` only when CI should fail on them.

## Output contract

Include a before/after table with:

- `gate_verdict`;
- `package_health`;
- resolved finding count;
- introduced finding count;
- remaining Critical count.

Keep scores in an optional informational section.

## Completion

Done when `verify_fix.py` ran against the pre-edit baseline and every introduced
finding is fixed or explicitly listed as remaining work. Never claim “fixed”
from memory alone.
