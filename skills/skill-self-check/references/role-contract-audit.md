# Conditional Role Contract Audit

Use this deterministic route after workflow applicability is declared. It
selects the role layer from the Skill's real model-call shape instead of adding
a profession to every Prompt.

## Scope selection

1. When `references/workflow-prompts.json` exists, role scope is
   `workflow_nodes`. Schema 1.1 node `role_contract` values are checked through
   the workflow Prompt audit.
2. When the Skill declares `Workflow prompt audit: N/A — <reason>`, role scope
   is `single_context`. The checker reads `references/role-contract.json` and
   verifies that its functional-role contract text is present in `SKILL.md`.
   One runtime context may use either one functional role or a declared
   sequence of roles; this does not create extra model-call nodes.
3. When model-call applicability is undeclared, status is `not_assessed`.
4. A single-context Skill may declare `Role contract audit: N/A — <reason>`
   only when role wording would not change decisions, evidence handling,
   output, permissions, or handoff. A contract takes precedence over N/A.

Do not treat workflow sections, checklist passes, or reasoning stages as
separate model-call nodes unless the runtime actually invokes them separately.
`agents/openai.yaml` `default_prompt` is normally an invocation prompt, not a
second business Prompt.

For `single_context`, functional roles are responsibility lenses inside one
Agent and shared context. `roles`, `next`, headings, or review passes never
authorize subagent dispatch. Static contract validity does not prove that the
role split preserves the global objective.

## Single-context contract

Copy [role-contract.example.json](../examples/role-contract.example.json) to
`references/role-contract.json`, then write the same contract text into
`SKILL.md`.

Legacy schema 1.0 remains valid:

- `schema_version`: `"1.0"`;
- `role`, `purpose`: non-empty strings;
- `responsibilities`, `out_of_scope`, `decision_authority`: non-empty string
  lists;
- `handoff_to`: a string list; terminal roles may use an empty list.

Schema 1.1 separates runtime topology from functional-role topology:

- `schema_version`: `"1.1"`;
- `runtime_mode`: `"single_context"`;
- `role_mode`: `"single_role"` or `"sequential_roles"`;
- `entry_role`: the first functional-role ID;
- `roles`: one or more role objects.

Every schema 1.1 role declares `id`, `role`, `purpose`, `inputs`,
`responsibilities`, `out_of_scope`, `decision_authority`, `outputs`,
`acceptance_tests`, `stop_conditions`, `next`, and `handoff_to`.
`next` names the next internal functional role in the same model invocation;
`handoff_to` names external downstream Skills, processes, or delivery steps.

`single_role` requires exactly one role and `next=[]`. `sequential_roles`
requires two or more roles forming one connected, reachable, acyclic chain
with one terminal role. Every non-entry role has exactly one incoming internal
handoff. Do not use this schema to represent branching model calls; use the
workflow manifest for actual model-call nodes.

The deterministic checker validates declaration shape and text linkage. It
does not decide whether the chosen role is useful or well designed.

## Run

```bash
python scripts/role_contract_audit.py /absolute/path/to/target-skill --pretty
```

Optional overrides:

```bash
python scripts/role_contract_audit.py /absolute/path/to/target-skill \
  --manifest /absolute/path/to/workflow-prompts.json \
  --role-contract /absolute/path/to/role-contract.json --pretty
```

Read stdout JSON. Exit `0` means `pass` or reasoned `not_applicable`; exit `1`
means `needs_work` or `not_assessed`.

## Findings

- `RCA.0`: applicability or required role declaration is unavailable;
- `RCA.1`: single-context role contract JSON is malformed or incomplete;
- `RCA.2`: declared role Prompt text is absent from `SKILL.md`;
- `RCA.3`: role IDs, entry, cardinality, or internal role chain are invalid;
- `RCA.4`: `SKILL.md` gives an unqualified delegation directive while the
  declaration is single-context.

`RCA.4` compares the declared topology against the instruction text the Agent
actually receives. A single-context Skill routinely *names* subagents,
dispatching, or parallel workers in order to forbid them, so a directive counts
as a leak only when neither its own line nor its section negates it. Prohibitive
sections (`When NOT to use`, `Out of scope`, `Red Flags`,
`Common Rationalizations`, `不可违背`, `禁止`) and fenced code blocks are
excluded. Evidence reports the line number, the matched directive, and the line
text so the fix target is unambiguous.

Report schema 1.1 preserves `mode`, `role`, and `nodes` for compatibility and
adds `runtime_mode`, `role_mode`, `entry_role`, `role_count`, and `roles`.
For schema 1.0, `roles` contains one normalized legacy record. For schema 1.1
sequential roles, `roles` is authoritative and singular `role` is `null`.

For workflow-node mode, relevant `WPA.*` findings remain unchanged and retain
their node evidence. Role results remain separate from package
`gate_verdict`.

## Limitations

A static pass proves declaration consistency only. Use
[role-prompt-review.md](role-prompt-review.md) for advisory necessity, overlap,
authority, and rewrite review. Accuracy, token use, latency, and retry reduction
require before/after behavior evaluation on the same fixtures. Validate supplied
comparison evidence with
[role-prompt-behavior-eval.md](role-prompt-behavior-eval.md); its verdict remains
separate from this audit and `gate_verdict`.
