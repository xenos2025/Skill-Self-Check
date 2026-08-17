# Prompt Optimization Audit

Read this reference only when the user explicitly requests prompt optimization,
context-efficiency review, instruction pruning, or before/after prompt analysis.

## Authority

- Run `hard_gates.py` first. The script exclusively owns package health,
  `gate_verdict`, findings, severity, counts, estimated static tokens, and exit
  code.
- Label qualitative findings `source: model_review`. They are advisory and
  cannot change the script result.
- Treat fewer tokens as an efficiency result, not proof of better quality.
- Claim behavioral equivalence only when representative behavior evidence
  supports it. Static gates and unit tests alone do not establish it.
- Edit the target only after explicit user authorization.

## Evidence baseline

Record the audit date, timezone, exact target, and inputs. State whether the
basis is live files, a Git diff, saved script JSON, tests, or behavior traces.

Before comparative edits, save `hard_gates.py --out-json` outside the audited
Skill and source repository. Record the baseline path or durable artifact ID
without embedding credentials or sensitive data. If the baseline is missing,
report the current state only; do not reconstruct before-state numbers.

Define measurement scope explicitly:

- `SKILL.md` static estimate covers instruction text only.
- On-demand references add context only when their route is selected.
- Observed model or platform tokens require trusted runtime evidence.
- Dirty scripts or tests prove the current worktree result, not isolated
  causality for one prompt edit.

## Review axes

1. **Trigger precision** — positive triggers, exclusions, and neighboring
   workflow boundaries are explicit in frontmatter.
2. **Default-path economy** — the common path contains only instructions needed
   on most runs while retaining required safety, authority, and completion
   steps.
3. **Progressive disclosure** — low-frequency variants, examples, and detailed
   procedures move to directly linked references with clear load conditions.
4. **Authority and output contracts** — scripts, model judgment, user decisions,
   and final report fields each have one owner.
5. **Instruction quality** — remove duplication and low-value explanation;
   preserve exact commands, stop conditions, permissions, and failure handling.
6. **Behavior preservation** — compare representative triggers, exclusions,
   outputs, authorization boundaries, and failure paths before claiming
   equivalence.

For every finding, include `source`, `scope`, `evidence`, `severity`,
`confidence`, and `verification status`. Use `severity: high|medium|low` for
model review so it cannot be confused with script-owned Critical findings.

## Workflow

1. Run the fast hard-gate audit and preserve its JSON when edits may follow.
2. Map what loads by default and what loads only for explicit routes.
3. Separate measured facts, model inferences, and items needing behavior or
   platform confirmation.
4. Propose the smallest cuts, moves, or contract rewrites that preserve the
   common path.
5. Apply edits only when authorized.
6. Run `verify_fix.py` against the saved baseline. Then run representative
   behavior cases when the claim includes output quality or equivalence.

Stop after one verified edit cycle. If validation is mixed, follow
[fix-verification.md](fix-verification.md): address new Critical findings once,
then report remaining work.

## Output contract

Report:

1. Audit scope, date/timezone, exact inputs, and evidence basis.
2. Current deterministic gate and static token estimate.
3. Ranked findings with `source`, `scope`, `evidence`, `severity`, `confidence`,
   `verification status`, and a concrete change.
4. A before/after table only when a saved baseline exists.
5. Separate conclusions for static efficiency, contract quality, and behavior.
6. One next action: apply authorized edits, run behavior cases, or stop.

Allowed claim: “Static `SKILL.md` input fell by 43%; the deterministic gate and
covered regression tests did not regress.”

Disallowed claim without behavior evidence: “Prompt quality improved by 43%”
or “behavioral equivalence is proven.”

## Verified case study

Historical project case, verified 2026-08-18 (Asia/Shanghai), based on live
files, saved `hard_gates.py` JSON, `verify_fix.py`, and the 32 related unit
tests:

| Metric | Before | After compression |
| --- | ---: | ---: |
| `SKILL.md` lines | 308 | 196 |
| Estimated static input tokens | 4,044 | 2,306 |
| `gate_verdict` | pass | pass |
| Introduced findings | 0 | 0 |

The compression saved 1,738 estimated tokens, about 43%. This is a historical
compression-stage result; rerun current metrics after later edits. Verification
status: static contract and related regression coverage passed. Behavioral
equivalence still needs representative model/platform evidence.
