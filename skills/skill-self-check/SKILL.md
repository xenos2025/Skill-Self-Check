---
name: skill-self-check
description: >-
  Deterministically audits an existing Agent Skill package, reports package
  health, gate_verdict, and ranked paste-ready fixes, and verifies
  user-authorized repairs against a saved baseline. Use when a user requests
  an audit, review, self-check, blocker diagnosis, prompt optimization, context
  efficiency review, or pre-share validation. For Skill creation, behavioral
  evaluation, visual scorecards, or edits lacking explicit authorization, use
  another workflow.
---

# Skill Self-Check

Fast static review of a target skill. Output deterministic gate status and
ranked fixes. Edit the target only when the user asks to apply fixes.

Sources fused: predictability, Skill anatomy/verification, Cursor hard rules,
PDCA, and SMART. Full checks live in [CHECKLIST.md](CHECKLIST.md).

<authority_contract>

- [scripts/hard_gates.py](scripts/hard_gates.py) exclusively owns
  `package_health`, `gate_verdict`, script findings, severity, and exit code.
- [scripts/verify_fix.py](scripts/verify_fix.py) exclusively owns fix
  verification against a saved baseline.
- Numeric scores are script-produced and informational only.
- Qualitative review is optional and model-owned; script findings, gate status,
  counts, severity, and exit code remain unchanged.
- Edit the target only after explicit user authorization.

</authority_contract>

## When to use

- Review an existing Skill before controlled use, installation, or sharing.
- Diagnose deterministic blockers and provide paste-ready fixes.
- Recheck user-authorized repairs against a saved baseline.

## When NOT to use

- Create a Skill from scratch.
- Run behavioral evaluations or multi-agent smoke tests.
- Generate profiles, presentations, or visual scorecards.

## Check axes

This audit always reports on:

- **Package health preflight** — one installable root, name/root alignment,
  standard top-level directories, portable paths, valid resource references,
  filename/residue hygiene, duplicate resources, and static installability
  (script; blocks maturity assessment)
- **Hard structure** — frontmatter, name, description shape (script)
- **Explicit gate** — valid package, named required checks, and no script
  Criticals; independent of numeric scores (script; blocking)
- **Basic usable score** — 0–5 informational diagnostic (script)
- **Contract clarity score** — 0–5 informational diagnostic (script)
- **Support kit score** — references / examples / memory / scripts; N/A
  allowed; informational only (script)
- **Predictability** — completion criteria, no-op, negation, sprawl (model + script hints)
- **Anatomy** — workflow quality, rationalizations (model + script hints)
- **PDCA loop** — Plan / Do / Check / Act all explicit (model; see references)
- **SMART outcomes** — Specific, Measurable, Achievable, Relevant, run-bound exit (model)
- **Token consumption** — static `SKILL.md` input estimate with a recommended
  budget ceiling, replaced by trusted input/output/total usage when behavior
  evidence supplies it (script)
- **Runtime duration** — target execution time only from trusted behavior
  evidence; otherwise `not_measured` (script)
- **Loop guard** — every loop/retry instruction carries a stop condition
  (max attempts / timeout / escalate); open-ended refinement requires a guard
  before the Skill ships (script `EFF.*`)

## Inputs

1. Locate the target skill directory (must contain `SKILL.md`).
2. Prefer an explicit path from the user.
3. If missing: ask once, or use the skill they just created/opened in this conversation.

**Completion criterion:** You know the absolute path to the target skill directory.

## Process

### Default — fast hard-gate audit

Run the bundled checker directly. This Skill operates independently of the
other shipped Skills:

```bash
python scripts/hard_gates.py /absolute/path/to/target-skill --pretty
```

On Windows, `py -3` is fine if `python` is missing.

For a multi-Skill source pack, add `--repo-root /absolute/path/to/repository`.
Omitting it keeps resolution target-local; supplying it permits only relative
links inside that root. Absolute/escaping paths remain Critical, and each link
reports `resolution_scope: target|repo`.

If fixes may follow, save the same run as a baseline outside the target and
source repository:

```bash
python scripts/hard_gates.py /absolute/path/to/target-skill \
  --out-json /private/path/baseline.json --pretty
```

- Parse stdout JSON. Treat stderr as a human summary only.
- Read `package_health`, `gate_verdict`, `gate_reasons`, and `findings` first.
- Exit code 1 means the gate did not pass; report the fixes normally.
- Treat scores and operational metrics as informational. Use `gate_verdict` as
  the exclusive gate authority instead of `scores.ship_floor_met`.
- Present maturity scores as a package assessment only when package health is
  valid and assessable.

**Completion criterion:** JSON parsed; `package_health`, `gate_verdict`,
`gate_reasons`, and `findings` are available.

### Rank and explain deterministic findings

Map script `findings` with `severity: critical|should_fix|nice` into the report.  
Explain and suggest rewrites; keep every script Critical in failed status.
Use [references/plain-language-response.md](references/plain-language-response.md)
to translate the source result without creating a second audit.

`PKG.*` and `EFF.*` are mechanical: the fix does not depend on the user's
business, so write the rewrite yourself using
[references/fix-templates.md](references/fix-templates.md) instead of asking.

<output_contract>

1. Gate verdict and plain-language reasons.
2. Every script Critical, each with 问题 → 为什么 → 可直接采用的建议改法.
3. At most three highest-priority Should fix findings.
4. One next action: say 「按意见改」 to authorize edits, or explicitly ask for
   deep audit / full static audit.

</output_contract>

**Fast-mode completion criterion:** Every script Critical is covered, no more
than three Should fix items are shown, and each displayed finding has an
actionable fix. Stop here unless the user explicitly requests another route.

## Optional routes

Load only the reference selected by the user's explicit request:

| User request | Required reference | Route result |
| --- | --- | --- |
| Deep review, Predictability, Anatomy, PDCA, or SMART | [references/deep-qualitative-audit.md](references/deep-qualitative-audit.md) | Advisory model findings layered onto the unchanged script gate |
| Prompt optimization or context efficiency | [references/prompt-optimization.md](references/prompt-optimization.md) | Evidence-bounded optimization findings without treating token reduction as quality gain |
| Complete installed check pack or saved source reports | [references/full-static-audit.md](references/full-static-audit.md) | Read-only JSON reports outside the target and source repository |
| Apply fixes / 「按意见改」 | [references/fix-verification.md](references/fix-verification.md) | Authorized edits followed by baseline verification |

For an explicitly requested deep/full technical report, use
[REPORT-TEMPLATE.md](REPORT-TEMPLATE.md) only for that explicit route.

## Verification

- [ ] `hard_gates.py` was executed on the target directory
- [ ] `gate_verdict` and `gate_reasons` were read before deprecated score fields
- [ ] Every script Critical has a paste-ready fix
- [ ] No more than three Should fix items appear in the default response
- [ ] Token consumption states `estimated`, `observed`, or `not_assessed` with scope
- [ ] Runtime duration is `observed` only with trusted behavior evidence; otherwise `not_measured`
- [ ] No script Critical was overridden
- [ ] User was advised whether the deterministic gate passed

Only for explicitly requested routes:

- [ ] Deep audit: model findings are advisory and labeled `source: model_review`
- [ ] Deep audit: PDCA×SMART matrix gaps map to advisory priorities
- [ ] Prompt optimization: static reduction, quality, and behavior claims remain separate
- [ ] Prompt optimization: comparative claims use a saved pre-edit baseline
- [ ] Full static audit: source JSON is outside the target and source repository
- [ ] Full static audit: target fingerprint is unchanged
- [ ] Applied fixes: `verify_fix.py` ran against the pre-fix baseline
- [ ] Applied fixes: every introduced finding is fixed or explicitly reported

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I can judge frontmatter myself" | Deterministic gates are script-owned. Run the script. |
| "Script failed, I'll estimate the gate" | Report the error and mark `gate_verdict` unavailable. |
| "The score is high, so the gate passed" | Scores are informational. Read `gate_verdict` and Criticals. |
| "User didn't say when NOT to use it — I'll write a sensible default" | Exclusions, triggers and acceptance evidence are the user's business decisions. Ask one question; a plausible invention scores well and still runs wrong. |
| "改完读一遍就知道修好了" | 分数和 finding 由脚本判定。跑 `verify_fix.py`，用前后对照说话。 |
| "PKG/EFF 也得先问用户" | 这两类是机械问题，答案与业务无关。照 fix-templates 直接改。 |

## Red Flags

- Writing a gate verdict without running the script
- Running PDCA×SMART or the full static audit without an explicit request
- Letting model review change `gate_verdict`, Critical counts, or exit status
- Inventing exclusions, triggers, or acceptance evidence
- Claiming findings are fixed without a `verify_fix.py` before/after table
- Editing the target before the user explicitly authorizes it

## Out of scope

- Creating a skill from scratch
- Automated multi-case behavioral evals (v2)
- Editing the target unless the user explicitly asks
- Inventing quarterly OKRs for a skill that only needs a session exit criterion
