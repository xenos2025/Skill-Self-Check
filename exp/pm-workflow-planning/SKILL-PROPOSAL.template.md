# Skill proposal template (experiment)

> Copy into a private workspace. Do not fill with real customer secrets in a
> public fork.

## Context

- Company type: foreign trade / factory / ecommerce / other
- Primary KPI:
- Systems in use:
- Pain (current failure mode):
- Interview date / process name:

## 5W2H source (required — from INTERVIEW.md)

Paste the cleared table. Do not propose a skill while any cell is still slogan-level.

| 5W2H | Answer | Clear? | Evidence / system |
| --- | --- | --- | --- |
| What | | Y/N | |
| Why | | Y/N | |
| Who | | Y/N | |
| When | | Y/N | |
| Where | | Y/N | |
| How | | Y/N | |
| How much | | Y/N | |

Blockers still open:

## Proposed skill

- Working name (`kebab-case`):
- User-invoked or model-invoked:
- One-line WHAT:
- WHEN triggers:
- When NOT:

## Check axes

- …
- …
- …

## PDCA (required for promotion)

| Phase | What we will write into the skill |
| --- | --- |
| Plan | When / When NOT / check axes / success shape |
| Do | Steps + Done when |
| Check | Verification evidence |
| Act | Red Flags / Rationalizations / retry |

## SMART outcome (required)

| Letter | Draft |
| --- | --- |
| Specific | |
| Measurable | |
| Achievable | |
| Relevant | |
| Time / run-bound exit | |

## Workflow outline

1. …
   - Done when:
2. …
   - Done when:

## Evidence / verification

- [ ] …
- [ ] …

## Build vs reuse

| Need | Build new | Reuse existing skill | Buy/partner pack |
| --- | --- | --- | --- |
| … | | | |

## Self-check gate

After a draft `SKILL.md` exists:

```bash
python skills/skill-self-check/scripts/hard_gates.py path/to/draft-skill --pretty
```

Promote only if `ship_floor_met` is true (or Criticals are explicitly waived
with a dated reason).
