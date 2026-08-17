# Features

| Capability | Input | Output | Writes target skill? |
| --- | --- | --- | --- |
| Hard-gate script | Skill directory | Explicit `gate_verdict`, ranked findings, informational scores | No |
| Agent self-check skill | Skill path + chat | Fast gate result + all Criticals + up to three Should-fix items | Only if user says apply |
| Explicit full audit | Skill path; optional work package | Read-only manifest + checker source JSON | No |
| Static ship-safety scan | Skill directory | Promise inventory, external-action hints, execution status | No |
| Work-readiness gates | One structured work package | B0–B6 business readiness, missing fields, one next quest | No |
| Deterministic gate | Script | `gate_verdict`, `gate_reasons`, named required checks | No |
| Three-light scores | Script | Informational `basic_usable`, `contract_clarity`, `support_kit` | No |
| Optional deep checklist | Explicit user request | Advisory model-review priorities | No |
| Optional PDCA + SMART audit | Explicit user request | Advisory matrix + fixes | No |
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
| `support_kit` | applicable count | references / examples / memory / scripts; N/A skipped |

All numeric scores have `scoring_effect=informational_only`. The blocking
result is `gate_verdict`: package health must be valid, every named required
check must pass, and script Critical count must be zero.
`scores.ship_floor_met` remains a deprecated compatibility alias for one
schema generation; new consumers must read `gate_verdict`.

The deterministic gate does not certify behavioral correctness, platform
compatibility, or safe external execution. `skill-ship-safety` never executes
target code; trusted isolated behavior evidence is a separate requirement.

## Readiness levels

`agent-work-readiness` reports B0–B6, from oral experience to a measurable,
delegable, reviewed workflow. These levels describe the supplied work package;
they do not change `skill-self-check` gate results.
