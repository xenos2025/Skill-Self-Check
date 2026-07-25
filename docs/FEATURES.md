# Features

| Capability | Input | Output | Writes target skill? |
| --- | --- | --- | --- |
| Hard-gate script | Skill directory | JSON scores + findings | No |
| Agent self-check skill | Skill path + chat | Ranked fix report | Only if user says apply |
| Three-light scores | Script | `basic_usable`, `contract_clarity`, `support_kit`, `ship_floor_met` | No |
| Checklist (Matt/Addy/Cursor fusion) | Loaded with skill | Guidance for Pass 2–4 | No |
| PDCA + SMART audit (Pass 5) | Target SKILL.md | Matrix + findings | No |
| Bad fixture smoke | Bundled example | Known Criticals | No |
| Bilingual gates | EN or 中文 `SKILL.md` | Same scores either language | No |
| Encoding tolerance | Non-UTF-8 file | Scores + finding `1.11` (no crash) | No |
| Regression suite + CI | `tests/test_hard_gates.py` | Pass/fail per scoring rule | No |
| Installers | This repo | Copy into Cursor skills dir | N/A |
| `exp/` PM hook | Manual | Drafts only | N/A |

## Scores

| Score | Max | Meaning |
| --- | --- | --- |
| `basic_usable` | 5 | Structure + description + actionable body + verification markers |
| `contract_clarity` | 5 | When / When-NOT / check axes / verification checkboxes / rationalizations |
| `support_kit` | applicable count | references / examples / memory / scripts; N/A skipped; not in ship floor |
| `ship_floor_met` | bool | `basic_usable >= 4` and zero script Critical |
