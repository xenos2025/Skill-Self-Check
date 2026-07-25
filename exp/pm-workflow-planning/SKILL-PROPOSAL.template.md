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

## Operational data contract

Read [references/operational-data-contract.md](references/operational-data-contract.md).

### Module selection

| Module | Apply? (Y/N/Ask user) | Reason | Artifact or N/A |
| --- | --- | --- | --- |
| L — numeric value/score | | | |
| S — source provenance | | | |
| V — verification strength | | | |
| R — run/history record | | | |

Complete only the selected sections below. A justified N/A is not a defect and
does not lower the general self-check score.

### Measurable goal

Complete only when L is selected.

| Metric ID | Formula | Unit | Direction | Weight | Owner | Score rule version |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

| Level | Numeric rule | Required V level | Action |
| --- | --- | --- | --- |
| L1 | | | |
| L2 | | | |
| L3 | | | |

### Source module

Complete only when S is selected.

| Source ID | Claim scope | S grade | Access test | Fallback |
| --- | --- | --- | --- | --- |
| | | | | |

### Verification module

Complete only when V is selected.

| Claim / metric | Required S grade | Required V level | Evidence artifact | Pass rule |
| --- | --- | --- | --- | --- |
| | | | | |

### Record module

Complete only when R is selected; prefer an existing approved system when it
already satisfies the fields.

- `score-rules.csv` path / owner:
- `source-register.csv` path / owner:
- `evidence-log.csv` path / owner:
- `run-log.csv` path / owner:
- `run_id` format:
- timestamp/timezone:
- schema version:
- sensitive-data exclusions:

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
| Do | Steps + Done when + selected module actions |
| Check | Applicable verification / deterministic completion evidence |
| Act | Applicable record, human override, retry, or handoff |

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
