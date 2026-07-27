---
name: skill-self-check
description: >-
  Reviews a newly written or edited Agent Skill and returns ranked fix suggestions.
  Use when a user asks to audit, review, self-check, score, or explain what must
  change in a drafted Skill before it is shared or used.
---

# Skill Self-Check

Static review of a target skill. Output a ranked fix report. Edit the target only when the user asks to apply fixes.

**Sources fused (plain-language checks):** Matt Pocock predictability levers, Addy Osmani skill anatomy / verification, Cursor `create-skill` hard rules, plus **PDCA** and **SMART** outcome contracts. Full items live in [CHECKLIST.md](CHECKLIST.md); mapping in [references/pdca-smart.md](references/pdca-smart.md).

**Authority split:** Hard gates + scores = **script** ([scripts/hard_gates.py](scripts/hard_gates.py)); fix verification = **script** ([scripts/verify_fix.py](scripts/verify_fix.py)). Qualitative judgment (including PDCA/SMART) = model. Script Critical pass/fail, numeric scores, and before/after deltas stay authoritative.

## When to use

- User finished drafting a skill and wants a review
- User says "自检这个 skill" / "review my skill" / "skill self-check"
- Before installing or sharing a personal/project skill

## When NOT to use

- Creating a skill from scratch (use create-skill)
- Asking for behavioral eval / multi-agent smoke tests (not in this skill yet)

## Check axes

This audit always reports on:

- **Package health preflight** — one installable root, name/root alignment,
  standard top-level directories, portable paths, valid resource references,
  filename/residue hygiene, duplicate resources, and static installability
  (script; blocks maturity assessment)
- **Hard structure** — frontmatter, name, description shape (script)
- **Basic usable score** — 0–5 ship floor (script)
- **Contract clarity score** — 0–5 including named check axes / when-not / verification (script)
- **Support kit score** — references / examples / memory / scripts; N/A allowed (script; does not block ship floor)
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

### 新手入口 — 一次生成两份成绩单（推荐）

四个正式 Skill 已一起安装时，优先运行：

```bash
python scripts/run_full_audit.py /absolute/path/to/target-skill \
  --out-dir /private/path/target-skill-audit \
  --pretty
```

Windows 可以使用 `py -3`。真实输出目录必须在被检查 Skill 和其源码仓库
之外；脚本会拒绝把报告放进可能同步到 GitHub 的目录。它只读取目标，不执行
目标 Skill，也不联网，并生成：

- `personal-scorecard.html`：个人能力、等级、优势和下一项练习；
- `project-scorecard.html`：项目分数、风险、证据和整改优先级；
- 两份成绩单共用的 JSON 来源，以及证明审计前后目标未变化的
  `audit-manifest.json`。

一键入口先读取 `hard-gates.json.package_health`。如果状态为
`invalid_skill_package`，仍生成完整问题清单和原始局部诊断，但必须停止
Lv0–Lv5、能力类型、徽章和“可交付”结论；两份 HTML 都要明确显示
“不是标准 Skill 包 · 暂停成熟度评分”。

可选加上 `--work-package 工作包.json`。

**高级审计（可选，作者轨道）：** 另加 `--behavior 可信行为证据.json` 才会解锁
成长成绩单 Lv3+ / 跨平台指纹。企业默认认证**不要求**这份文件：Ship floor
已过且无 Critical 时，成绩单主结论仍是「可受控试用」；缺行为证据只记在
`advanced_audit` 旁注里。

目标未变化只证明**本次审计只读**，不能替代目标 Skill 在真实业务里的试跑验收。

**完成标准：** 两份 HTML 指向同一个 Skill，项目成绩单保留原始分数，
`audit-manifest.json` 中 `target.unchanged=true`。

### Pass 0 — Run hard-gate script (required)

From this skill's directory (or via absolute path to the script):

```bash
python scripts/hard_gates.py /absolute/path/to/target-skill --pretty
```

On Windows, `py -3` is fine if `python` is missing.

If there is any chance the user will say 「按意见改」, keep this run as the
**baseline** for Pass 7 — save the stdout JSON to a file outside the target:

```bash
python scripts/hard_gates.py /absolute/path/to/target-skill > /private/path/baseline.json
```

如果已经使用上面的新手入口，直接读取其 `hard-gates.json`，不要为了相同证据
重复运行。

- Read **stdout JSON** as the source of truth for scores and script findings.
- Stderr one-liner is for humans; parse scores from stdout JSON only.
- Exit code 1 means ship floor not met — still continue the review.
- Read `package_health` before interpreting any score. Only
  `status=valid_skill_package` and `assessable=true` unlock maturity scoring.
  An invalid package keeps raw scores as partial file diagnostics only.
- `scores.support_kit` is the blue light: materials / examples / memory / scripts. `kit_complete=false` is Should fix, not Critical.
- `operational_metrics.token_consumption` and
  `operational_metrics.runtime_duration` are informational dimensions. They do
  not change `ship_floor_met` or the three source scores.

**Completion criterion:** JSON parsed; `package_health`,
`scores.basic_usable`, `scores.contract_clarity`, `scores.support_kit`, and
`findings` are available. Leave numeric scores exactly as the script emitted
them, and translate them into maturity only when package health is valid.

### Pass 1 — Hard gates (script-owned)

Map script `findings` with `severity: critical|should_fix|nice` into the report.  
You may **explain** and suggest rewrites; you may **not** mark a script Critical as passed.

`PKG.*` and `EFF.*` are mechanical: the fix does not depend on the user's
business, so write the rewrite yourself using
[references/fix-templates.md](references/fix-templates.md) instead of asking.

**Completion criterion:** Every script Critical appears under Critical with 建议改法.

### Pass 2 — Predictability (model)

Use [CHECKLIST.md](CHECKLIST.md) Pass 2. Incorporate script hints (no-op / negation density) but judge completion-criterion quality and leading words yourself.

**Completion criterion:** Each finding names the failure mode in plain language.

### Pass 3 — Anatomy (model)

Use checklist Pass 3. If script already flagged missing Verification / When NOT / check axes, skip empty restatement — add paste-ready rewrites instead.

Split the gaps before writing rewrites:

- **Wording, structure, length, terminology** — infer and write the rewrite yourself.
- **Business decisions** (`1.7` triggers, `3.2` real scenarios, `3.3` exclusions, `3.5` acceptance evidence, `5.4` escalation) — only the user knows these. Ask instead of inventing; see [references/gap-questions.md](references/gap-questions.md).

**Completion criterion:** Contract gaps have concrete section text the user can paste, and every decision-owned gap is either answered by the user or marked `unknown — 待用户确认`.

### Pass 4 — Prune (model)

Use checklist Pass 4. Trust script `line_count`, time-sensitive / path hints,
and the efficiency guards (`EFF.1` unguarded loop, `EFF.2` unbounded
refinement, `EFF.3` token budget). For every `EFF.*` finding, propose the
concrete stop condition or the exact material to move into `references/`;
[references/fix-templates.md](references/fix-templates.md) has the paste-ready
forms for each ID.

**Completion criterion:** Concrete cut-or-move suggestions listed; every
`EFF.*` finding has a paste-ready bound or split.

### Pass 5 — PDCA + SMART (+ 5W2H if interview skill)

Read [references/pdca-smart.md](references/pdca-smart.md). Use checklist Pass 5.

1. Map the target skill onto **Plan → Do → Check → Act** (quote evidence for each).
2. Judge the outcome contract against **SMART** (S/M/A/R/T as defined there; T = run-bound exit, not fake calendar dates).
3. Fill the PDCA×SMART matrix in the report. Promote gaps to Critical / Should fix / Nice with paste-ready fixes.
4. If the skill interviews clients / gathers requirements: also apply checklist **5.10–5.12 (5W2H)** — one clear question at a time; no slogan answers.

**Completion criterion:** Matrix filled; every `missing` cell has a finding or an explicit waiver note; interview skills have 5W2H coverage noted.

This self-check skill itself follows the loop: Plan (When + axes) → Do (passes 0–5) → Check (Verification) → Act (offer 「按意见改」, rationalizations).

## Write both reports

Create both views from the same script result and qualitative findings:

- [REPORT-BUSINESS-TEMPLATE.md](REPORT-BUSINESS-TEMPLATE.md) — plain-language
  version for owners, operators, and other non-technical readers.
- [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md) — technical version with finding
  IDs, script fields, evidence, and reproduction details.

Rules:

- Keep scores, finding counts, finding IDs, and pass/fail conclusion identical
  across both reports
- Put **script scores** in the technical 分数表 verbatim from JSON
- Translate technical terms in the business report: Critical → 必须先解决,
  Should fix → 建议尽快改进, ship floor → 基础使用门槛
- Keep raw JSON and bare exit codes out of the business report; say what they mean instead
- Fill **PDCA×SMART** matrix (Pass 5) — model-owned, not inventing script scores
- Rank findings: Critical → Should fix → Nice
- Each finding: **问题** → **为什么** → **建议改法** (paste-ready when helpful)
- Label source: `script` vs `model` on each finding
- Default: report only. Offer: "说「按意见改」我可以代改 Critical / Should fix"
- If decision-owned gaps remain, also offer: "说「帮我补」我一次问你一个问题，把这些补齐" — follow [references/gap-questions.md](references/gap-questions.md): one question at a time, max three per round, recommended answer first
- Answers become **待确认文本 in the report**. Write them into the target `SKILL.md` only under the same gate as 「按意见改」
- If `ship_floor_met` is false: tell the user to fix Critical before relying on real-world observation to polish
- If ship floor is true but PDCA **Check** or **Act** is missing: say so — usable ≠ closed-loop

**Completion criterion (skill done):** Both reports share one conclusion and
finding set; the business report gives one plain-language next action; the
technical report includes script scores, PDCA×SMART, all script Criticals with
rewrites, Pass 2–5 coverage, and an offer to apply fixes or interview for
decision-owned gaps.

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
| `verdict: regressed` | 新增 Critical 或分数下降 | 回滚这次改动 |
| `findings.introduced` | 复检才出现的项 | 逐条说明；`newly_surfaced_non_critical` 常是新适用的检查，不是你改坏了 |
| `scores.*.direction: not_comparable` | 该维度满分变了 | 说明适用范围变化，不要谎报涨跌 |

`introduced` 里的非 Critical 项不阻断交付，但必须出现在报告里。CI 想把它们也
当失败，加 `--strict`。

Then put a before/after table in both reports: 三项分数、ship floor、
`package_health`、已解决数、新增数、剩余 Critical。

**Completion criterion:** `verify_fix.py` ran against the pre-fix baseline, the
report shows the before/after table, and any `introduced` finding is either
fixed or explicitly listed as remaining work. 改完就宣布完成、没有复检输出的，
本 Pass 未完成。

## Verification

- [ ] `hard_gates.py` was executed on the target directory
- [ ] 新手入口生成的真实报告位于目标和源码仓库之外
- [ ] `audit-manifest.json` 证明审计前后目标未变化
- [ ] Both reports share the same scores, counts, finding IDs, and conclusion
- [ ] Technical report scores match JSON exactly
- [ ] Token consumption states `estimated`, `observed`, or `not_assessed` with scope
- [ ] Runtime duration is `observed` only with trusted behavior evidence; otherwise `not_measured`
- [ ] Business report contains no unexplained technical terms
- [ ] No script Critical was overridden
- [ ] User was advised whether ship floor is met
- [ ] PDCA×SMART matrix filled (Plan/Do/Check/Act × S/M/A/R/T notes)
- [ ] Every PDCA `missing` cell mapped to a finding or dated waiver
- [ ] Decision-owned gaps were asked, not invented (or left as `unknown — 待用户确认`)
- [ ] 应用了修改时：`verify_fix.py` 跑过改前基线，报告含前后对照表
- [ ] 应用了修改时：复检新增的 finding 已逐条交代（修掉或列为剩余项）

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I can judge frontmatter myself" | Numbers and regex gates are script-owned. Run the script. |
| "Script failed, I'll skip scores" | Still report the error; leave score cells as "script failed". |
| "Ship floor failed but skill looks fine" | Floor is the rule for 'basic usable'. List Criticals first. |
| "PDCA/SMART is enterprise fluff" | Here they are evidence mappings (When→Plan, Done when→Measurable, Verification→Check). Empty cells are defects. |
| "Time-bound needs a calendar date" | For skills, T means run-bound exit (Verification / handoff), unless the domain is truly dated ops. |
| "User didn't say when NOT to use it — I'll write a sensible default" | Exclusions, triggers and acceptance evidence are the user's business decisions. Ask one question; a plausible invention scores well and still runs wrong. |
| "Asking is slower, I'll fill everything in" | Ask only decision-owned Critical / Should fix gaps, max three per round. The rest you still rewrite yourself. |
| "改完读一遍就知道修好了" | 分数和 finding 由脚本判定。跑 `verify_fix.py`，用前后对照说话。 |
| "复检冒出新 finding，说明脚本有问题" | 补上步骤之后，配套材料检查才开始适用。这是新暴露出来的检查范围，照常列进报告。 |
| "PKG/EFF 也得先问用户" | 这两类是机械问题，答案与业务无关。照 fix-templates 直接改。 |

## Red Flags

- Writing a score without running the script
- Re-scoring basic_usable after the script
- Skipping check-axes guidance when script severity is critical
- Report without PDCA×SMART matrix
- Calling a skill "done" with no Check (Verification) or Act (fix path)
- Writing exclusions, triggers or acceptance evidence the user never stated
- Interrogating the user with a long question list instead of three at a time
- Claiming findings are fixed without a `verify_fix.py` before/after table
- Hiding findings that only appeared after the rewrite

## Out of scope

- Creating a skill from scratch
- Automated multi-case behavioral evals (v2)
- Editing the target unless the user explicitly asks
- Inventing quarterly OKRs for a skill that only needs a session exit criterion
