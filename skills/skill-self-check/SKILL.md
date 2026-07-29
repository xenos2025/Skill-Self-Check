---
name: skill-self-check
description: >-
  Runs a fast deterministic audit of a newly written or edited Agent Skill and
  returns ranked hard-gate fixes. Use when a user asks to audit, review,
  self-check, repair blockers, or explain what must change before a Skill is
  shared or used. Route explicit scorecard or growth-profile requests to the
  optional skill-growth-scorecard after this audit completes.
---

# Skill Self-Check

Fast static review of a target skill. Output deterministic gate status and
ranked fixes. Edit the target only when the user asks to apply fixes.

**Sources fused (plain-language checks):** Matt Pocock predictability levers, Addy Osmani skill anatomy / verification, Cursor `create-skill` hard rules, plus **PDCA** and **SMART** outcome contracts. Full items live in [CHECKLIST.md](CHECKLIST.md); mapping in [references/pdca-smart.md](references/pdca-smart.md).

**Authority split:** Deterministic gate status and script findings =
**script** ([scripts/hard_gates.py](scripts/hard_gates.py)); fix verification =
**script** ([scripts/verify_fix.py](scripts/verify_fix.py)). Numeric scores are
script-produced but informational only. Qualitative review (including
PDCA/SMART) is optional, model-owned, and cannot change `gate_verdict`, script
severity, or the process exit code.

## When to use

- User finished drafting a skill and wants a review
- User says "自检这个 skill" / "review my skill" / "skill self-check"
- User asks what blocks a Skill and wants paste-ready hard-gate fixes
- Before installing or sharing a personal/project skill

## When NOT to use

- Creating a skill from scratch (use create-skill)
- Asking for behavioral eval / multi-agent smoke tests (not in this skill yet)
- Generating a scorecard without first producing deterministic audit JSON

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
  (max attempts / timeout / escalate); open-ended refinement phrasing is
  flagged so a Skill cannot ship a runaway self-loop (script `EFF.*`)

## Inputs

1. Locate the target skill directory (must contain `SKILL.md`).
2. Prefer an explicit path from the user.
3. If missing: ask once, or use the skill they just created/opened in this conversation.

**Completion criterion:** You know the absolute path to the target skill directory.

## Process

### Default — fast hard-gate audit

Run the bundled checker directly. This Skill is independently installable and
must not require the other shipped Skills:

```bash
python scripts/hard_gates.py /absolute/path/to/target-skill --pretty
```

On Windows, `py -3` is fine if `python` is missing.

If there is any chance the user will say 「按意见改」, keep this run as the
**baseline** for Pass 7 — save the stdout JSON to a file outside the target:

```bash
python scripts/hard_gates.py /absolute/path/to/target-skill > /private/path/baseline.json
```

- Read **stdout JSON** as the source of truth for `gate_verdict`,
  `gate_reasons`, scores, and script findings.
- Stderr is a gate/count summary for humans.
- Exit code 1 means the deterministic gate did not pass — still report fixes.
- Read `package_health` before interpreting any score. Only
  `status=valid_skill_package` and `assessable=true` unlock maturity scoring.
  An invalid package keeps raw scores as partial file diagnostics only.
- Read `gate_verdict` before the deprecated compatibility alias
  `scores.ship_floor_met`. Numeric scores have
  `scoring_effect=informational_only`; the explicit gate alone controls exit.
- `scores.support_kit` describes materials / examples / memory / scripts.
  `kit_complete=false` is Should fix, not Critical.
- `operational_metrics.token_consumption` and
  `operational_metrics.runtime_duration` are informational dimensions. They do
  not change `gate_verdict` or the three source scores.

**Completion criterion:** JSON parsed; `package_health`, `gate_verdict`,
`gate_reasons`, and `findings` are available.

### Rank and explain deterministic findings

Map script `findings` with `severity: critical|should_fix|nice` into the report.  
You may **explain** and suggest rewrites; you may **not** mark a script Critical as passed.
Use [references/plain-language-response.md](references/plain-language-response.md)
to translate the source result without creating a second audit or scorecard.

`PKG.*` and `EFF.*` are mechanical: the fix does not depend on the user's
business, so write the rewrite yourself using
[references/fix-templates.md](references/fix-templates.md) instead of asking.

Default output:

1. Gate verdict and plain-language reasons.
2. Every script Critical, each with 问题 → 为什么 → 可直接采用的建议改法.
3. At most three highest-priority Should fix findings.
4. One next action: say 「按意见改」 to authorize edits, or explicitly ask for
   deep audit / scorecard.

**Fast-mode completion criterion:** Every script Critical is covered, no more
than three Should fix items are shown, and each displayed finding has an
actionable fix. Stop here unless the user explicitly requests another route.

### Optional route — deep qualitative audit

Run the following passes only when the user explicitly asks for a deep audit,
Predictability, Anatomy, PDCA, or SMART review. Label every model-owned item
with `source: model_review` and `priority: high|medium|low`. Model review is
advisory: it cannot add script Criticals, change `gate_verdict`, alter counts,
or change the exit code.

#### Predictability

Use [CHECKLIST.md](CHECKLIST.md) Pass 2. Incorporate script hints (no-op / negation density) but judge completion-criterion quality and leading words yourself.

**Completion criterion:** Each finding names the failure mode in plain language.

#### Anatomy

Use checklist Pass 3. If script already flagged missing Verification / When NOT / check axes, skip empty restatement — add paste-ready rewrites instead.

Split the gaps before writing rewrites:

- **Wording, structure, length, terminology** — infer and write the rewrite yourself.
- **Business decisions** (`1.7` triggers, `3.2` real scenarios, `3.3` exclusions, `3.5` acceptance evidence, `5.4` escalation) — only the user knows these. Ask instead of inventing; see [references/gap-questions.md](references/gap-questions.md).

**Completion criterion:** Contract gaps have concrete section text the user can paste, and every decision-owned gap is either answered by the user or marked `unknown — 待用户确认`.

#### Prune

Use checklist Pass 4. Trust script `line_count`, time-sensitive / path hints,
and the efficiency guards (`EFF.1` unguarded loop, `EFF.2` unbounded
refinement, `EFF.3` token budget). For every `EFF.*` finding, propose the
concrete stop condition or the exact material to move into `references/`;
[references/fix-templates.md](references/fix-templates.md) has the paste-ready
forms for each ID.

**Completion criterion:** Concrete cut-or-move suggestions listed; every
`EFF.*` finding has a paste-ready bound or split.

#### PDCA + SMART (+ 5W2H if interview skill)

Read [references/pdca-smart.md](references/pdca-smart.md). Use checklist Pass 5.

1. Map the target skill onto **Plan → Do → Check → Act** (quote evidence for each).
2. Judge the outcome contract against **SMART** (S/M/A/R/T as defined there; T = run-bound exit, not fake calendar dates).
3. Fill the PDCA×SMART matrix in the report. Assign advisory priority with
   paste-ready fixes while preserving the deterministic gate.
4. If the skill interviews clients / gathers requirements: also apply checklist **5.10–5.12 (5W2H)** — one clear question at a time; no slogan answers.

**Completion criterion:** Matrix filled; every `missing` cell has a finding or an explicit waiver note; interview skills have 5W2H coverage noted.

This self-check skill itself follows the loop: Plan (When + axes) → Do (passes 0–5) → Check (Verification) → Act (offer 「按意见改」, rationalizations).

### Optional route — scorecard

Only when the user explicitly asks for a score, scorecard, growth profile,
personal/project profile, printable HTML, or full report:

1. Finish the fast audit once and preserve its JSON.
2. If `skill-growth-scorecard` is installed, route that existing JSON to it.
   Do not rerun the same target checks.
3. Treat `skill-ship-safety`, `agent-work-readiness`, and behavior evidence as
   optional enhancements. This core audit remains valid when they are absent.
4. If `skill-growth-scorecard` is not installed, finish the core audit, save
   the reusable JSON outside the target/repository when an output was requested,
   and state that the optional scorecard route is unavailable. Do not
   auto-install anything; keep the missing scorecard state explicit.

The compatibility full runner remains available only as an explicit route:

```bash
python scripts/run_full_audit.py /absolute/path/to/target-skill \
  --out-dir /private/path/target-skill-audit \
  --pretty
```

Real scorecard output must stay outside the audited Skill and source
repository. [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md) remains a compatibility
reference for explicit deep/full technical reports; it is not a default
completion requirement.

## Pass 7 — 改完复检（only after fixes are applied）

Applies when the user said 「按意见改」 and you edited the target. A rewrite can
resolve four findings and quietly introduce a fifth, so the claim "已修复" has to
come from the script output below, not from memory.

```bash
python scripts/verify_fix.py /absolute/path/to/target-skill \
  --baseline /private/path/baseline.json \
  --pretty
```

Missing baseline? Say so, then run `hard_gates.py` once for a plain after-state
and report it as an after-state only — guessing the before-state is worse than
admitting you lack it.

Read the result:

| 字段 | 含义 | 动作 |
| --- | --- | --- |
| `verdict: improved` | 有改善，没有硬回退 | 交付，并列出 `introduced` 里新冒出来的项 |
| `verdict: unchanged` | 分数与 finding 都没动 | 改动没落盘，或没被任何检查覆盖——查清楚再说修好了 |
| `verdict: mixed` | 有改有坏 | 先处理 `new_critical`，本 Pass 最多再走一轮；第二轮仍是 `mixed` 就停下，把剩余项列成待办交给用户 |
| `verdict: regressed` | 新增 Critical 或 `gate_verdict` 回退 | 回滚这次改动 |
| `gates.gate_verdict` | 新旧确定性门禁 | 这是复检阻断状态的权威来源 |
| `findings.introduced` | 复检才出现的项 | 逐条说明；`newly_surfaced_non_critical` 常是新适用的检查，不是你改坏了 |
| `scores.*.direction` | 信息性分数变化 | 可解释趋势，但不能改变复检结论 |
| `scores.*.direction: not_comparable` | 该维度满分变了 | 说明适用范围变化，不要谎报涨跌 |

`introduced` 里的非 Critical 项不阻断交付，但必须出现在报告里。CI 想把它们也
当失败，加 `--strict`。

Then put a before/after table in the response: `gate_verdict`,
`package_health`、已解决数、新增数、剩余 Critical；三项分数放在可选信息区。

**Completion criterion:** `verify_fix.py` ran against the pre-fix baseline, the
report shows the before/after table, and any `introduced` finding is either
fixed or explicitly listed as remaining work. 改完就宣布完成、没有复检输出的，
本 Pass 未完成。

## Verification

- [ ] `hard_gates.py` was executed on the target directory
- [ ] `gate_verdict` and `gate_reasons` were read before deprecated score fields
- [ ] Every script Critical has a paste-ready fix
- [ ] No more than three Should fix items appear in the default response
- [ ] Token consumption states `estimated`, `observed`, or `not_assessed` with scope
- [ ] Runtime duration is `observed` only with trusted behavior evidence; otherwise `not_measured`
- [ ] No script Critical was overridden
- [ ] User was advised whether the deterministic gate passed
- [ ] 应用了修改时：`verify_fix.py` 跑过改前基线，报告含前后对照表
- [ ] 应用了修改时：复检新增的 finding 已逐条交代（修掉或列为剩余项）

Only for explicitly requested routes:

- [ ] Deep audit: model findings are advisory and labeled `source: model_review`
- [ ] Deep audit: PDCA×SMART matrix gaps map to advisory priorities
- [ ] Scorecard: existing audit JSON was consumed as-is; target check invocation count did not increase
- [ ] Scorecard/full output is outside the target and source repository
- [ ] Scorecard: source scores, counts, finding IDs, and gate conclusion remain unchanged

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I can judge frontmatter myself" | Deterministic gates are script-owned. Run the script. |
| "Script failed, I'll estimate the gate" | Report the error and mark `gate_verdict` unavailable. |
| "The score is high, so the gate passed" | Scores are informational. Read `gate_verdict` and Criticals. |
| "PDCA/SMART must run every time" | It is an explicit deep-audit route, not default completion work. |
| "Time-bound needs a calendar date" | For skills, T means run-bound exit (Verification / handoff), unless the domain is truly dated ops. |
| "User didn't say when NOT to use it — I'll write a sensible default" | Exclusions, triggers and acceptance evidence are the user's business decisions. Ask one question; a plausible invention scores well and still runs wrong. |
| "Asking is slower, I'll fill everything in" | Ask only decision-owned Critical / Should fix gaps, max three per round. The rest you still rewrite yourself. |
| "改完读一遍就知道修好了" | 分数和 finding 由脚本判定。跑 `verify_fix.py`，用前后对照说话。 |
| "复检冒出新 finding，说明脚本有问题" | 补上步骤之后，配套材料检查才开始适用。这是新暴露出来的检查范围，照常列进报告。 |
| "PKG/EFF 也得先问用户" | 这两类是机械问题，答案与业务无关。照 fix-templates 直接改。 |

## Red Flags

- Writing a gate verdict without running the script
- Re-scoring basic_usable after the script
- Skipping check-axes guidance when script severity is critical
- Running PDCA×SMART or scorecard generation without an explicit request
- Letting model review change `gate_verdict`, Critical counts, or exit status
- Calling a skill "done" with no Check (Verification) or Act (fix path)
- Inventing exclusions, triggers, or acceptance evidence
- Interrogating the user with a long question list instead of three at a time
- Claiming findings are fixed without a `verify_fix.py` before/after table
- Hiding findings that only appeared after the rewrite

## Out of scope

- Creating a skill from scratch
- Automated multi-case behavioral evals (v2)
- Editing the target unless the user explicitly asks
- Inventing quarterly OKRs for a skill that only needs a session exit criterion
