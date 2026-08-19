# Role and Prompt Behavior Evidence

Use this route after an authorized role or Prompt rewrite changes role count,
runtime mapping, authority, shared context, or deliverables. It is independent
from static role-contract status and never changes `gate_verdict`.

## What this module does

Run the same representative fixture against the saved baseline and candidate.
Use an independent evaluator context that receives the original request,
artifacts, and success criteria, but not the expected verdict or suspected bug.
Record the comparison with
[role-prompt-behavior.example.json](../examples/role-prompt-behavior.example.json),
then validate it:

```bash
python scripts/role_prompt_behavior_check.py /private/path/role-prompt-behavior.json --pretty
```

The checker validates supplied evidence only. It does not invoke the target
Skill, a model, subagents, or external systems.

## Required checks

- `global_objective` — the candidate still optimizes the original end-to-end
  outcome rather than a local gate.
- `required_business_outcomes` — all required user-facing outcomes remain.
- `shared_context` — the final owner can use the original brief, relevant
  evidence, assets, constraints, and unresolved items.
- `end_to_end_ownership` — one named owner integrates and revises coupled work.
- `authority_boundaries` — claims, approvals, and external actions remain
  bounded without blocking unrelated safe work.
- `integration_quality` — local outputs form a coherent accepted deliverable.

Each check needs artifact evidence and a baseline/candidate status. Missing
checks, changed inputs, changed success criteria, non-independent evaluation,
or `not_assessed` comparison fields produce `behavior_verdict: not_assessed`.

## Topology invariant

When the candidate declares `runtime_mode: single_context`, `agent_count` must
remain `1` and `implicit_delegation` must be `false`. Functional roles, Prompt
headings, review passes, and `next` do not authorize subagents. Violations are
`RPB.1` and the candidate is `regressed`.

## Verdicts

- `improved`: at least one check improved and none regressed;
- `unchanged`: no check changed; eligible, but do not claim improvement;
- `mixed`: gains and regressions coexist; block release;
- `regressed`: topology, global purpose, or another behavior check regressed;
- `not_assessed`: comparative evidence is incomplete or invalid.

`RPB.2` identifies loss of global purpose, shared context, ownership, required
outcomes, or integration quality. This module stays separate from
`role_contract_audit.py`: one proves evidence-record consistency; the other
proves only static contract consistency.
