# Deep Qualitative Audit

Read this reference only when the user explicitly requests a deep audit,
Predictability, Anatomy, PDCA, SMART, or interview-skill review.

## Authority

Label every qualitative item with `source: model_review` and
`priority: high|medium|low`. Model review is advisory. It cannot add script
Criticals or change `gate_verdict`, counts, severity, scores, or exit code.

Use [../CHECKLIST.md](../CHECKLIST.md) for the complete pass definitions.

## Predictability

Use checklist Pass 2. Incorporate script hints such as no-op and negation
density, then judge completion-criterion quality and leading words.

Done when each finding names the failure mode in plain language.

## Anatomy

Use checklist Pass 3. When the script already flagged a missing Verification,
When NOT, or check-axis section, do not restate the gap; provide paste-ready
text.

Split gaps by ownership:

- Wording, structure, length, and terminology: write the rewrite.
- Business decisions (`1.7`, `3.2`, `3.3`, `3.5`, `5.4`): ask rather than
  invent. Use [gap-questions.md](gap-questions.md).

Done when contract gaps have paste-ready text and every decision-owned gap is
answered or marked `unknown — 待用户确认`.

## Prune

Use checklist Pass 4. Trust script `line_count`, time-sensitive/path hints, and
`EFF.1`–`EFF.3`. For every `EFF.*` finding, provide a concrete stop condition
or name the exact material to move into `references/`. Use
[fix-templates.md](fix-templates.md).

Done when every `EFF.*` finding has a paste-ready bound or split.

## PDCA and SMART

Read [pdca-smart.md](pdca-smart.md), then use checklist Pass 5.

1. Map Plan, Do, Check, and Act with evidence.
2. Judge Specific, Measurable, Achievable, Relevant, and run-bound exit.
3. Fill the PDCA×SMART matrix without altering the deterministic gate.
4. For interview or requirements-gathering Skills, also apply checklist
   `5.10`–`5.12` and ask one clear question at a time.

Done when every `missing` cell has an advisory finding or explicit waiver, and
interview Skills state their 5W2H coverage.

## Deep-route completion

- Every model finding is labeled advisory.
- Script and model findings remain separate.
- Decision-owned gaps are asked, not invented.
- The final report preserves the original deterministic gate.
