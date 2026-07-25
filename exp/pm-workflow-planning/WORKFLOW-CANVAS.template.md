# Workflow canvas

## Scope

- Process:
- Company/industry:
- Intended decision or deliverable:
- Trigger:
- Owner:
- Approver:
- Explicitly out of scope:

## Business-experience module selection

Judge from context. If unclear, ask one question with a recommendation.

| Module | Apply? (Y/N/Ask user) | Reason | Artifact or N/A |
| --- | --- | --- | --- |
| L — numeric value/score | | | |
| S — source provenance | | | |
| V — verification strength | | | |
| R — run/history record | | | |

## Measurable goal and value levels

Complete only when L is selected. Otherwise write `N/A — <reason>`.

| Metric ID | Name | Formula | Unit | Direction | Weight | Baseline | Owner | Score rule version |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |

| Level | Numeric rule | Required V level | Allowed action |
| --- | --- | --- | --- |
| L1 | | | |
| L2 | | | |
| L3 | | | |

## Source register

Complete only when S is selected. Otherwise write `N/A — <reason>`.

| Source ID | Source | Claim scope | S grade | Access method | Runtime status | Last tested | Fallback | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |

## Verification policy

Complete only when V is selected. Otherwise write `N/A — <reason>`.

| Claim / metric | Required source grade | Required V level | Artifact | Pass rule | Human escalation |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Workflow

| Step | Trigger / input | Role | Action | Metric | Source ID | Evidence / V level | Record written | Done when | Exception / escalation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | | | | |

## Decision points

| Decision | Recommended default | User/role who decides | Evidence needed | Alternative |
| --- | --- | --- | --- | --- |
| | | | | |

## Recording contract

Complete only when R is selected. Reuse an existing approved system when it
already supplies the required fields.

| Table | One row per | Required? | Storage path | Owner | Retention / sensitivity rule |
| --- | --- | --- | --- | --- | --- |
| `score-rules.csv` | metric-level rule and level | L selected? | | | |
| `source-register.csv` | source/capability | S selected? | | | |
| `evidence-log.csv` | claim-source observation | V selected? | | | |
| `run-log.csv` or existing system | workflow run | R selected? | | | |

Join key: `run_id`. Timestamp format: ISO 8601 with timezone.

## Open blockers

| Blocker | Impact | Owner | Next action | Due/trigger |
| --- | --- | --- | --- | --- |
| | | | | |

## Confirmation

- Workflow read back to user:
- Confirmed by:
- Confirmation date:
- Approved next step: proposal only / draft Skill / other
