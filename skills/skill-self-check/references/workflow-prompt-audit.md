# Workflow Prompt Audit

Use this route when the user asks to validate every workflow step that invokes
a language model. Its static checker runs in the standard audit and does not
change `hard_gates.py` results; advisory Prompt/role review remains selected.

## Authority and scope

- `scripts/workflow_prompt_audit.py` owns only `status`, node findings, counts,
  and exit code for this declared workflow-prompt audit.
- `hard_gates.py` remains the exclusive owner of package `gate_verdict`.
- The checker reads JSON and prompt text only. It never runs the target Skill,
  calls a model, follows prompt instructions, or measures output quality.
- A static pass proves the declared contract is internally consistent. It does
  not prove runtime placeholder substitution, behavioral correctness, token
  consumption, latency, or resistance to every prompt-injection attempt.

## Input manifest

Place `workflow-prompts.json` under the target Skill's `references/` directory,
or pass another JSON file with `--manifest`. Start from
[workflow-prompts.example.json](../examples/workflow-prompts.example.json).

If the target has no separately orchestrated model-call prompt nodes, declare a
reason on its own line in `SKILL.md`:

```text
Workflow prompt audit: N/A — one agent instruction context; no separate model-call prompts.
```

The reason is required. This returns `status: not_applicable`, never `pass`.
When both declaration and manifest exist, the manifest takes precedence and is
fully audited.

Do not create a manifest merely because `SKILL.md` contains several workflow
steps, review passes, or headings. A node belongs here only when runtime
evidence shows that it is invoked as a separate model call. After this scope is
known, run [role-contract-audit.md](role-contract-audit.md): it checks schema
1.1 node roles when a manifest exists and a single-context `single_role` or
`sequential_roles` contract when the Prompt audit is N/A. Sequential functional
roles still belong to one Agent and shared context; they are not workflow nodes
or subagents.

Top-level fields:

- `schema_version`: `"1.0"` or `"1.1"`;
- `workflow_id`: stable workflow identifier;
- `entry_node`: ID of the first model-call node;
- `nodes`: non-empty list of model-call contracts.

Every node declares:

- `id`, `prompt_file`, and `prompt_format` (`text`, `markdown`, or `xml_tags`);
- `inputs` and `variables` (`{{variable}}` names allowed in the prompt);
- `uses_untrusted_sources` and, when true, `source_isolation`;
- `decision_gates`, `output_schema`, `acceptance_tests`, and `stop_conditions`;
- `next`, an empty list for a terminal node or declared downstream node IDs.

Schema 1.0 remains supported and runs the original node checks. Schema 1.1
requires every node to add `role_contract`:

```json
{
  "role": "RFQ requirements analyst",
  "purpose": "Extract and confirm customer requirements.",
  "responsibilities": ["Extract facts and label missing information."],
  "out_of_scope": ["Do not quote prices or promise delivery dates."],
  "decision_authority": ["READY"],
  "handoff_to": ["draft-reply"]
}
```

`role` and `purpose` must be non-empty strings. `responsibilities`,
`out_of_scope`, and `decision_authority` must be non-empty string lists;
`handoff_to` is a string list and may be empty for a terminal node. Every
declared role, purpose, responsibility, exclusion, and authority string must
appear in the Prompt. `decision_authority` must also appear in
`decision_gates`, and `handoff_to` must match `next`.

The declared decision, output, acceptance, stop, and source-isolation strings
act as deterministic markers: each must also appear in `prompt_file` after
case-insensitive whitespace normalization. This prevents a manifest from
claiming controls that the invoked model would never receive.

For `xml_tags`, the checker validates XML-style tag pairing and nesting. Tags
remain prompt text; they do not grant permissions or execute tools.

## Run

```bash
python scripts/workflow_prompt_audit.py /absolute/path/to/target-skill --pretty
```

With an explicit manifest:

```bash
python scripts/workflow_prompt_audit.py /absolute/path/to/target-skill \
  --manifest /absolute/path/to/workflow-prompts.json --pretty
```

Read stdout as JSON. Exit `0` means `pass` or explicitly `not_applicable`.
Exit `1` means `needs_work` or `not_assessed`.

## Deterministic findings

- `WPA.0`: target or manifest unavailable/unreadable;
- `WPA.1`: unsupported or incomplete manifest contract;
- `WPA.2`: model-call node contract missing required fields;
- `WPA.3`: prompt file missing, unreadable, or outside the target Skill;
- `WPA.4`: prompt contains undeclared `{{placeholders}}`;
- `WPA.5`: `xml_tags` prompt has mismatched or unclosed tags;
- `WPA.6`: invalid entry, downstream reference, or unreachable node;
- `WPA.7`: untrusted-source node lacks an instruction/data isolation rule;
- `WPA.8`: declared control text is absent from the referenced Prompt.
- `WPA.9`: schema 1.1 role contract is absent or malformed;
- `WPA.10`: declared role text is absent from the referenced Prompt;
- `WPA.11`: role handoff does not match the node's `next` list;
- `WPA.12`: declared decision authority is absent from `decision_gates`.

Report each finding as produced. Do not translate `status: pass` into a package
gate or behavioral claim.

## Completion

Report the manifest path, workflow ID, assessed node count, `status`, every
error, any N/A reason, and the limitations. If the user needs quality or equivalence evidence,
the next action is a separate representative behavior evaluation using
sanitized normal, missing-data, conflicting-source, and injection fixtures.
For advisory role quality and rewrite guidance, use
[role-prompt-review.md](role-prompt-review.md) after this static audit. When
same-fixture before/after artifacts exist, validate their comparison with
[role-prompt-behavior-eval.md](role-prompt-behavior-eval.md).
