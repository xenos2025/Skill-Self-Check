# Features

| Capability | Input | Output | Writes target skill? |
| --- | --- | --- | --- |
| Hard-gate script | Skill directory | JSON scores + findings | No |
| Agent self-check skill | Skill path + chat | Business + technical reports from one result | Only if user says apply |
| One-command full audit | Skill path; optional work package / trusted behavior JSON | Read-only manifest + personal/project JSON and offline HTML | No |
| Static ship-safety scan | Skill directory | Promise inventory, external-action hints, execution status | No |
| Work-readiness gates | One structured work package | B0–B6 business readiness, missing fields, one next quest | No |
| Growth scorecard | Readiness / audit / safety / behavior JSON | One JSON fact set + offline HTML | No |
| Whole-suite scorecards | Repository `skills/` + local regression suite | Private audit JSON + separate personal/project HTML | No |
| Three-light scores | Script | `basic_usable`, `contract_clarity`, `support_kit`, `ship_floor_met` | No |
| Checklist (Matt/Addy/Cursor fusion) | Loaded with skill | Guidance for Pass 2–4 | No |
| PDCA + SMART audit (Pass 5) | Target SKILL.md | Matrix + findings | No |
| Bad fixture smoke | Bundled example | Known Criticals | No |
| Bilingual gates | EN or 中文 `SKILL.md` | Same scores either language | No |
| Encoding tolerance | Non-UTF-8 file | Scores + finding `1.11` (no crash) | No |
| Regression suite + CI | `tests/test_*.py` | Pass/fail per scoring rule | No |
| Installers | This repo | Copy into Cursor skills dir | N/A |
| `exp/` PM hook | Manual | Drafts only | N/A |

## Scores

| Score | Max | Meaning |
| --- | --- | --- |
| `basic_usable` | 5 | Structure + description + actionable body + verification markers |
| `contract_clarity` | 5 | When / When-NOT / check axes / verification checkboxes / rationalizations |
| `support_kit` | applicable count | references / examples / memory / scripts; N/A skipped; not in ship floor |
| `ship_floor_met` | bool | `basic_usable >= 4` and zero script Critical; static floor only |

`ship_floor_met` does not certify behavioral correctness, platform
compatibility, or safe external execution. `skill-ship-safety` never executes
target code; trusted isolated behavior evidence is a separate requirement.

## Growth levels

The product deliberately keeps two independent progress lines:

| Line | Levels | What it measures |
| --- | --- | --- |
| Business readiness | B0–B6 | From oral experience to a measurable, delegable, reviewed workflow |
| Skill engineering | Lv0–Lv5 | From a draft to static quality, behavior closure, safety, and cross-platform evidence |

The HTML scorecard is a view, not a second scoring system. Its three tabs reuse
the same JSON: `成长画像`, `检测结果`, and `技术证据`.

Lv4 treats applicability as evidence, not a checkbox: an inapplicable write-back
gate needs a trusted unchanged-target record, and an inapplicable external-action
gate needs a clean static safety scope plus a shareable evidence reference. Lv5
counts two platforms only when both use the same contract and fixture SHA-256
identifiers.
