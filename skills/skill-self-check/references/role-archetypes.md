# Functional Role Archetypes

Use this compact library only after inventorying target work units. These are
selection aids, not personas to paste unchanged. Target evidence owns final
wording, authority, outputs, and handoff.

| Archetype | Select when evidence shows | Authority boundary | Typical output | Common misuse |
| --- | --- | --- | --- | --- |
| Evidence and requirements analyst | sources must be collected, normalized, or gaps labeled before decisions | may classify evidence; cannot invent facts or approve downstream action | evidence map, requirements record, missing-data list | renamed “research expert” with no trust rules |
| Policy, compliance, and Claims Gate | claims or actions require policy/evidence approval | may approve, reject, or escalate named claims only | approved/pending/rejected claim ledger | writes marketing copy and self-approves it |
| Content and communication producer | approved evidence must become audience-facing language | may choose expression within approved claims; cannot create new claims | page copy, brief, message draft | given compliance authority merely for writing |
| Visual and system designer | approved content must become layout, interaction, or visual rules | may decide hierarchy and presentation; cannot change approved facts | visual specification, layout, design tokens | used as a vague creativity persona |
| Implementation and execution specialist | an approved specification must become code or another concrete artifact | may implement within the approved specification; external actions stay separately authorized | code, configured artifact, render | allowed to redesign requirements while implementing |
| QA and acceptance verifier | outputs need checks independent from production | may pass, fail, or report defects against named tests; cannot silently repair scope | test report, defect list, acceptance status | producer declares its own work accepted |
| Router / gatekeeper | work must be assigned or stopped based on explicit conditions | may select one named owner/path; cannot absorb specialist work or invent approvals | routing decision, bounded context packet | creates many roles without runtime evidence |
| External-action operator | an approved artifact must be sent, published, written, or otherwise mutate a real system | may perform only the explicitly authorized action and must record the result | send/write receipt, external ID, failure record | treated as approval owner or allowed implicit retries |
| Data and measurement analyst | trusted observations must become metrics, comparisons, or diagnostics | may compute and interpret named measures; cannot fabricate unavailable data or claim causality without evidence | metric table, diagnostic summary, measurement gaps | turns missing data into estimates presented as facts |

Reject generic labels such as “expert”, “senior consultant”, or “professional”
when they do not change evidence handling, decisions, outputs, permissions, or
handoff. Prefer one functional role unless real work-unit boundaries require a
split.

## E-commerce high-coupling example

Commerce image production usually couples product evidence, asset selection,
copy density, visual hierarchy, and the final buyer-facing story. Default to one
end-to-end functional role:

`E-commerce creative production owner` — retains the original brief and full
asset inventory, plans copy and visuals together, applies the Claims Gate only
to controlled claims, and owns the integrated render and QA result.

Internal checkpoints:

`global brief → evidence/Claims Gate → content and visual plan → render → integrated QA`

Represent this as `runtime_mode: single_context` plus `role_mode: single_role`.
The checkpoints are not subagents or separate model-call nodes. Missing claim
evidence removes or marks only the affected claim; it does not erase supported
product facts, visual context, or the overall commercial objective.

Use `sequential_roles` only when medium coupling and a real internal handoff are
both evidenced, while the same Agent retains the global brief and a named
end-to-end owner. Use workflow nodes only when the runtime actually invokes the
model separately and the final integrator receives the shared context needed to
reconcile the outputs.
