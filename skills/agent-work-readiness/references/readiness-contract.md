# Work readiness contract

## Contents

1. [Purpose](#purpose)
2. [Canonical file](#canonical-file)
3. [B0–B6 gates](#b0b6-gates)
4. [Field rules](#field-rules)
5. [Privacy and evidence](#privacy-and-evidence)

## Purpose

Assess whether one business process is clear enough to delegate to an Agent.
This contract does not score the engineering quality of a finished Skill.

The assessment is sequential. A later gate cannot compensate for an earlier
missing gate.

## Canonical file

The canonical input is `work-readiness.json`. Copy
`../assets/work-readiness.template.json` into an approved private workspace.

Required top-level objects:

| Field | Purpose |
| --- | --- |
| `process` | Scope, outcome, trigger, owner, approver, and boundary |
| `steps` | Ordered workflow with input, action, output, role, Done when, exception |
| `roles` | Role ownership and explicit non-ownership |
| `handoffs` | Cross-role deliverable and acceptance |
| `metrics` | Reproducible completion or performance standards |
| `agent_boundary` | Allowed, forbidden, approval, and escalation |
| `evidence` | Versioned pilot records and retrospective |

## B0–B6 gates

| Level | Name | Gate |
| --- | --- | --- |
| B0 | 口头经验 | A valid work package is not yet available |
| B1 | 目标澄清 | Name, outcome, reason, trigger, and out-of-scope are present |
| B2 | 流程成形 | Every step has ID, input, action, output, and Done when |
| B3 | 职责分清 | Process owner/approver, step roles, role ownership, and handoffs are clear |
| B4 | 标准量化 | At least one metric has formula, unit, direction, threshold, and owner |
| B5 | Agent 可委派 | Allowed/forbidden actions, human approval, exceptions, and escalation exist |
| B6 | Agent 可运营 | Two local pilot artifacts, a retrospective, and a version exist |

Levels are maturity gates, not an average. B5 requires B1–B4 to pass first.

## Field rules

### `process`

```json
{
  "name": "one narrowly named process",
  "intended_outcome": "visible result",
  "why": "business reason or failure prevented",
  "trigger": "event or schedule",
  "owner": "one responsible role",
  "approver": "one approving role",
  "out_of_scope": "what this package will not do"
}
```

### `steps`

Every step needs:

- unique `id`;
- `input`;
- `action`;
- `output`;
- one declared `role`;
- `done_when`;
- `exception`.

### `roles` and `handoffs`

Each role has an `owns` list. Exact duplicate ownership across roles blocks B3
until the boundary is resolved. When more than one step role exists, at least
one handoff must name `from`, `to`, `deliverable`, and `acceptance`.

### `metrics`

Each metric needs:

- `id` and `name`;
- reproducible `formula`;
- `unit`;
- `direction` such as `higher_is_better`, `lower_is_better`, or `must_equal`;
- exact `threshold`;
- one `owner`.

### `agent_boundary`

Use separate lists for:

- `allowed_actions`;
- `forbidden_actions`;
- `human_approval`.

Also provide one `escalation` rule. Every workflow step has its own common
exception.

### `evidence`

B6 requires:

- a non-empty `version`;
- at least two pilot records with `run_id`, `artifact`, `outcome`, and
  `reviewed_by`;
- one `retrospective` file.

Artifact paths must be relative, remain inside the work package, and exist.
Absolute paths and `..` traversal do not count.

## Privacy and evidence

- Keep real work packages outside this public repository.
- Do not store credentials, customer contact data, raw private chat, or secrets.
- Prefer structured summaries over full transcripts.
- A file's existence proves only that evidence was supplied, not that the
  business claim is true.
- Use a trusted human review before real Agent delegation.

