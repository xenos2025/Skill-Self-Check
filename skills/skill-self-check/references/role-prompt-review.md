# Role Discovery and Prompt Synthesis

Use after `workflow_prompt_audit.py` and `role_contract_audit.py` when the user
asks whether roles fit the Skill, how many roles it needs, or requests
role-based Prompt enhancement. This model review is advisory and cannot change
script status, findings, counts, severity, exit code, or `gate_verdict`.

## Preserve the global mission first

Before inventorying roles, write one shared mission block from target evidence:

- `global_objective` — the end-to-end user outcome, not a local gate result;
- `global_success_criteria` — observable business and artifact outcomes;
- `shared_context` — original brief, source evidence, assets, constraints, and
  unresolved items that the end-to-end owner must retain;
- `end_to_end_owner` — the one role or real workflow node responsible for the
  integrated deliverable; and
- `integration_acceptance_tests` — checks that local outputs form a coherent
  whole and still satisfy the original request.

Do not optimize a role independently before this block exists. A compliance,
QA, or evidence gate may constrain part of the work but must not replace the
global objective. Missing evidence blocks only the affected claim, action, or
deliverable unless target policy explicitly requires the entire workflow to
stop.

## Select two topologies independently

First determine runtime topology from actual invocation evidence:

- `workflow_nodes`: the runtime separately invokes two or more model-call
  nodes; review one role contract per declared node.
- `single_context`: one Agent instruction context performs the work; it may use
  `single_role` or `sequential_roles` without creating extra model calls.
- `not_assessed`: evidence does not establish the call shape. Return
  `needs_confirmation`; do not invent nodes or roles.
- `not_applicable`: accept only a reason showing role wording would not change
  decisions, evidence handling, output, permissions, or handoff.

Headings, review passes, ordinary steps, and `agents/openai.yaml`
`default_prompt` are not separate model calls. Recommend `workflow_nodes` only
when isolation, permissions, retry ownership, or context boundaries require
separate invocations.

`single_context` means one Agent with one shared context. Never translate its
`roles`, `next`, headings, or review passes into subagents, parallel workers, or
separate tasks. If the runtime can express functional roles only by delegation,
keep `single_role` and encode the other responsibilities as internal checkpoints.

## Required evidence

- Role-contract and workflow-Prompt audit JSON.
- `SKILL.md` plus the applicable role contract or workflow manifest.
- Inputs and trusted evidence, decisions and approval boundaries, outputs,
  acceptance tests, stop conditions, and downstream consumers.
- Referenced Prompts for real workflow nodes.

Use [role-archetypes.md](role-archetypes.md) only after reading target evidence.
If a required boundary is missing, mark it `needs_confirmation`. Never invent a
persona, authority, business rule, claim, or handoff.

## Work-unit inventory

Before naming a role, inventory each coherent unit of work:

1. `inputs_and_evidence` — what it receives and which sources are trusted.
2. `decisions_and_approval` — what it may decide, recommend, or must escalate.
3. `outputs` — machine keys, files, statuses, or downstream artifacts.
4. `acceptance_tests` — observable conditions that make the output usable.
5. `prohibitions_and_stop` — unsupported claims, forbidden actions, and exit
   conditions.
6. `downstream_consumer` — the next internal role, Skill, person, system, or
   delivery step.

Do not use occupations as evidence. A role exists only when its work unit
changes decisions, evidence treatment, output, authority, or handoff.

## Integration coupling and split decision

Assess integration coupling before counting role boundaries:

- `high`: copy, evidence, assets, layout, or implementation must be revised
  together to satisfy one outcome; context loss would change the result;
- `medium`: outputs have clear handoffs but need an end-to-end owner to reconcile
  tradeoffs; or
- `low`: artifacts, authority, retries, and acceptance can be isolated without
  losing the original objective.

High coupling is a split veto for execution. Default to `single_role` with
internal gates. Medium coupling may use `sequential_roles` only inside one
shared context, with a named end-to-end owner and integration tests. Low
coupling may support real workflow nodes when runtime evidence also proves
separate model calls.

Record a functional boundary when any hard boundary exists:

- different approval or decision authority;
- evidence or trust isolation;
- a rule forbids the producer from approving its own result.

Hard boundaries require an explicit gate or authority rule, but do not by
themselves authorize a new worker or model call. Otherwise consider a role
split only when at least two soft boundaries materially differ: input evidence,
output artifact, acceptance tests, downstream consumer, or work objective. If
only responsibilities differ while authority and the delivery chain stay the
same, keep one role and list those responsibilities.

State the evidence for every split and merge. Prefer the fewest roles that
preserve real boundaries; never add a decorative “expert” role.

## Build the role contract

For `single_context`, propose schema 1.1 from
[role-contract-audit.md](role-contract-audit.md):

- `single_role`: exactly one role, matching `entry_role`, with `next=[]`.
- `sequential_roles`: two or more roles in one connected, reachable, acyclic
  chain. `next` is the next internal role in the same invocation.
- `handoff_to` is reserved for external downstream destinations.

The contract describes functional responsibility, not worker allocation. For
`single_context`, set `execution_mapping: single_agent_shared_context` in the
model review and reject any proposed dispatch, spawn, delegation, or parallel
worker instruction.

For `workflow_nodes`, keep manifest schema 1.1 and one role contract per actual
model-call node. Do not collapse real nodes into a single-context role chain.

## Synthesize the Prompt

Start the paste-ready patch with the shared mission block. Then add a Prompt
section for every proposed role. Every role receives the global objective and
the shared context it needs; authority restrictions limit decisions, not access
to relevant evidence. Keep role controls near the task and output contract.
Preserve exact machine-consumed keys and keep untrusted material inside its
data boundary.

`paste-ready` means the patch contains no “insert existing value”, TODO,
ellipsis, invented schema, or other unresolved placeholder. When exact Prompt,
manifest, schema, acceptance, stop, or source-isolation text is required but
missing, do not present a partial role patch as paste-ready. Return a
paste-ready blocking intake patch that names the missing evidence and stops the
rewrite until it is supplied.

Each role section must contain:

1. **Role** — precise functional ownership, not seniority or style.
2. **Purpose** — one outcome.
3. **Inputs and trusted evidence** — required data and trust boundary.
4. **Responsibilities** — work needed for the outcome.
5. **Out of scope** — prohibited decisions and unsupported claims.
6. **Decision authority** — statuses or decisions the role may emit.
7. **Output contract** — files, keys, artifacts, and unresolved items.
8. **Acceptance tests** — observable checks.
9. **Stop conditions** — when to stop or escalate.
10. **Handoff** — internal `next` role or external `handoff_to` destination.

For every prohibition, provide the allowed fallback when one exists. Do not
write broad stops such as “missing evidence stops the task” when the safe
behavior is to omit one claim, label one item pending, or ask for one missing
input. The end-to-end owner may revise coupled copy, asset selection, and layout
until the integrated acceptance tests pass, without crossing approval bounds.

After role boundaries are correct, apply context pruning and progressive
disclosure from [prompt-optimization.md](prompt-optimization.md). Do not optimize
a faulty one-role design merely by making it shorter.

## Output contract

Return one review object or clearly equivalent structured sections containing:

- `mode: role_prompt_enhancement`;
- `source: model_review`;
- `runtime_mode`, `role_mode`, and evidence for both;
- `global_mission`: objective, success criteria, shared context, end-to-end
  owner, and integration acceptance tests;
- `work_unit_inventory`;
- `split_decision`: integration coupling, coupling evidence, hard boundaries,
  soft-boundary count, recommendation, and evidence;
- `execution_mapping`, which must be `single_agent_shared_context` for
  `single_context`;
- `proposed_role_count` and ordered topology;
- paste-ready schema 1.1 role-contract JSON or workflow-node patch;
- paste-ready Prompt patch containing all ten role sections, or a blocking
  intake patch when exact required evidence is unavailable;
- `confidence: high|medium|low`;
- `needs_confirmation` items;
- `behavior_eval_required: true|false` and the claim it would verify.
- a same-fixture behavior test plan following
  [role-prompt-behavior-eval.md](role-prompt-behavior-eval.md) when a rewrite
  changes role count, runtime mapping, authority, shared context, or deliverables.

Separate these claims:

- static consistency comes only from the deterministic scripts;
- role quality is advisory model judgment;
- runtime improvement requires before/after behavior evaluation on the same
  representative fixtures.

Never claim improved accuracy, safety, token use, latency, or retry rate from a
static rewrite alone. Do not edit the target until the user authorizes the
rewrite; after edits, verify against the saved hard-gate baseline.
