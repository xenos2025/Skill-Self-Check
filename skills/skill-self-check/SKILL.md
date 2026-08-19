---
name: skill-self-check
description: >-
  Deterministically audits an Agent Skill package, reports gate_verdict and
  paste-ready fixes, then verifies authorized repairs against a baseline. Use
  when users request audit, review, self-check, blocker diagnosis, prompt optimization,
  context efficiency, workflow Prompt validation, or pre-share validation. Do not use to create
  Skills, execute behavioral evaluations, make visual scorecards, or edit
  without approval.
---

# Skill Self-Check

Run a fast static review with deterministic gate status and ranked fixes.
Full checks: [CHECKLIST.md](CHECKLIST.md).

Workflow prompt audit: N/A — one agent instruction context; no separate model calls.

## Role contract

- **Role:** Skill audit verifier
- **Purpose:** Report script gates and verify approved fixes.
- **Responsibilities:** Run the standard static checkers before reporting.
- **Responsibilities:** Separate model advice from script results.
- **Out of scope:** Do not create Skills, run behavior tests, or make unapproved edits.
- **Decision authority:** Report only the script gate_verdict.
- **Decision authority:** Verify approved fixes against a baseline.
- **Handoff to:** Send business-readiness gaps to agent-work-readiness.
- **Handoff to:** Send external-action safety to skill-ship-safety.

Machine contract: [references/role-contract.json](references/role-contract.json).

<authority_contract>

- [hard_gates.py](scripts/hard_gates.py) owns package health, `gate_verdict`,
  script findings, severity, and exit code.
- [verify_fix.py](scripts/verify_fix.py) owns saved-baseline verification.
- Script scores are informational only.
- Model review cannot change script status, counts, severity, or exit code.
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

[CHECKLIST.md](CHECKLIST.md) owns four result families:

- **Gate:** package health and `gate_verdict` (script; blocking);
- **Diagnostics:** structure, contract, support, token, and loops (script);
- **Qualitative:** Predictability, Anatomy, PDCA, SMART (explicit advisory route);
- **Role/Prompt:** workflow applicability and role contract (standard static
  status), plus explicit model-owned optimization.

## Inputs

1. Locate the target skill directory (must contain `SKILL.md`).
2. Prefer an explicit path from the user.
3. If missing: ask once, or use the skill they just created/opened in this conversation.

**Completion criterion:** You know the absolute path to the target skill directory.

## Process

### Standard audit — three static statuses

For every general audit, review, or self-check, run all three bundled checkers:

```bash
python scripts/hard_gates.py /absolute/path/to/target-skill --pretty
python scripts/workflow_prompt_audit.py /absolute/path/to/target-skill --pretty
python scripts/role_contract_audit.py /absolute/path/to/target-skill --pretty
```

`hard_gates.py` alone owns `gate_verdict`; workflow and role statuses remain
separate. Run only `hard_gates.py` when the user explicitly asks for a fast or
gate-only check.

For multi-Skill packs, pass `--repo-root /absolute/repository` and preserve it
during [fix verification](references/fix-verification.md). Escaping paths stay Critical.

If fixes may follow, save the same run as a baseline outside the target and
source repository:

```bash
python scripts/hard_gates.py /absolute/path/to/target-skill \
  --out-json /private/path/baseline.json --pretty
```

- Parse stdout JSON; stderr is a human summary.
- Read `package_health`, `gate_verdict`, `gate_reasons`, and `findings` first.
- Exit 1 means the gate failed; report fixes normally.
- Scores/metrics are informational. Show maturity only for an assessable package.

**Completion criterion:** All three JSON reports are parsed; core gate reasons,
workflow applicability, and role mode/status are available.

### Rank and explain deterministic findings

Map script `findings` into [plain-language response](references/plain-language-response.md)
without changing any Critical or creating a second audit.

For mechanical `PKG.*`/`EFF.*`, write the rewrite from
[fix-templates.md](references/fix-templates.md) instead of asking.

<output_contract>

1. Gate verdict plus workflow Prompt and role-contract statuses.
2. Every script Critical, each with 问题 → 为什么 → 可直接采用的建议改法.
3. At most three highest-priority Should fix findings.
4. One next action: 「按意见改」, or request a named advisory/full route.

</output_contract>

## Selected routes

Load only selected references. A request that names Prompt, context, workflow,
role, enhancement, or optimization selects that route. “Did you review X?” also
means run the read-only X route now unless the user explicitly asks for status
only; execute it instead of returning `not_run`. Run every named row; “role and Prompt enhancement”
selects both Prompt optimization and workflow/role review.

| User request | Required reference | Route result |
| --- | --- | --- |
| Deep review, Predictability, Anatomy, PDCA, or SMART | [references/deep-qualitative-audit.md](references/deep-qualitative-audit.md) | Advisory; script gate unchanged |
| Prompt optimization or context efficiency | [references/prompt-optimization.md](references/prompt-optimization.md) | Evidence-bounded; token cuts do not prove quality |
| Workflow Prompt, roles, enhancement, or regression comparison | [workflow](references/workflow-prompt-audit.md) + [role contract](references/role-contract-audit.md) + [role synthesis](references/role-prompt-review.md) + [behavior evidence](references/role-prompt-behavior-eval.md) | Select named routes; validate supplied comparisons with `scripts/role_prompt_behavior_check.py`; gate unchanged |
| Complete installed check pack or saved source reports | [references/full-static-audit.md](references/full-static-audit.md) | Read-only JSON outside target/repo |
| Apply fixes / 「按意见改」 | [references/fix-verification.md](references/fix-verification.md) | Authorized edits + baseline verification |

For an explicitly requested deep/full technical report, use
[REPORT-TEMPLATE.md](REPORT-TEMPLATE.md) only for that explicit route.

## Verification

- [ ] `hard_gates.py` was executed on the target directory
- [ ] `workflow_prompt_audit.py` and `role_contract_audit.py` were executed
- [ ] `gate_verdict` and `gate_reasons` were read before deprecated score fields
- [ ] Every script Critical has a paste-ready fix
- [ ] No more than three Should fix items appear in the default response
- [ ] Token consumption states `estimated`, `observed`, or `not_assessed` with scope
- [ ] Runtime duration is `observed` only with trusted behavior evidence; otherwise `not_measured`
- [ ] No script Critical was overridden
- [ ] User was advised whether the deterministic gate passed

Only for selected advisory/full/fix routes:

- [ ] Deep audit: model findings are advisory and labeled `source: model_review`
- [ ] Deep audit: PDCA×SMART matrix gaps map to advisory priorities
- [ ] Prompt optimization: static reduction, quality, and behavior claims remain separate
- [ ] Prompt optimization: comparative claims use a saved pre-edit baseline
- [ ] Workflow Prompt audit: node/role findings remain separate from `gate_verdict`
- [ ] Role optimization: actual runtime evidence selected `workflow_nodes` or
      `single_context`; single-context review selected `single_role` or
      `sequential_roles`, preserved one Agent, and produced a bounded Prompt patch
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
| "They only asked whether the role/Prompt audit ran" | Run the named read-only route now unless they explicitly requested status only. |
| "User didn't say when NOT to use it — I'll write a sensible default" | Exclusions, triggers and acceptance evidence are the user's business decisions. Ask one question; a plausible invention scores well and still runs wrong. |
| "改完读一遍就知道修好了" | 分数和 finding 由脚本判定。跑 `verify_fix.py`，用前后对照说话。 |
| "PKG/EFF 也得先问用户" | 这两类是机械问题，答案与业务无关。照 fix-templates 直接改。 |

## Red Flags

- Writing a gate verdict without running the script
- Reporting a named read-only route as `not_run` instead of executing it
- Running PDCA×SMART or the full static audit without an explicit request
- Letting model review change `gate_verdict`, Critical counts, or exit status
- Inventing exclusions, triggers, or acceptance evidence
- Claiming findings are fixed without a `verify_fix.py` before/after table
- Editing the target before the user explicitly authorizes it

## Out of scope

- Creating a skill from scratch
- Executing target or model behavior tests; supplied evidence validation only
- Editing the target unless the user explicitly asks
- Inventing quarterly OKRs for a skill that only needs a session exit criterion
