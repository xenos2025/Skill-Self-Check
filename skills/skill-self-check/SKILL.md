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

**Authority split:** Hard gates + scores = **script** ([scripts/hard_gates.py](scripts/hard_gates.py)). Qualitative judgment (including PDCA/SMART) = model. Script Critical pass/fail and numeric scores stay authoritative.

## When to use

- User finished drafting a skill and wants a review
- User says "自检这个 skill" / "review my skill" / "skill self-check"
- Before installing or sharing a personal/project skill

## When NOT to use

- Creating a skill from scratch (use create-skill)
- Asking for behavioral eval / multi-agent smoke tests (not in this skill yet)

## Check axes

This audit always reports on:

- **Hard structure** — frontmatter, name, description shape (script)
- **Basic usable score** — 0–5 ship floor (script)
- **Contract clarity score** — 0–5 including named check axes / when-not / verification (script)
- **Support kit score** — references / examples / memory / scripts; N/A allowed (script; does not block ship floor)
- **Predictability** — completion criteria, no-op, negation, sprawl (model + script hints)
- **Anatomy** — workflow quality, rationalizations (model + script hints)
- **PDCA loop** — Plan / Do / Check / Act all explicit (model; see references)
- **SMART outcomes** — Specific, Measurable, Achievable, Relevant, run-bound exit (model)

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

可选加上 `--work-package 工作包.json` 和 `--behavior 可信行为证据.json`。
没有行为证据时，等级不会越过静态证据上限。目标未变化只证明**本次审计只读**，
不能替代目标 Skill 自身的运行与安全验证。

**完成标准：** 两份 HTML 指向同一个 Skill，项目成绩单保留原始分数，
`audit-manifest.json` 中 `target.unchanged=true`。

### Pass 0 — Run hard-gate script (required)

From this skill's directory (or via absolute path to the script):

```bash
python scripts/hard_gates.py /absolute/path/to/target-skill --pretty
```

On Windows, `py -3` is fine if `python` is missing.

如果已经使用上面的新手入口，直接读取其 `hard-gates.json`，不要为了相同证据
重复运行。

- Read **stdout JSON** as the source of truth for scores and script findings.
- Stderr one-liner is for humans; parse scores from stdout JSON only.
- Exit code 1 means ship floor not met — still continue the review.
- `scores.support_kit` is the blue light: materials / examples / memory / scripts. `kit_complete=false` is Should fix, not Critical.

**Completion criterion:** JSON parsed; `scores.basic_usable`, `scores.contract_clarity`, `scores.support_kit`, and `findings` available. Leave numeric scores exactly as the script emitted them.

### Pass 1 — Hard gates (script-owned)

Map script `findings` with `severity: critical|should_fix|nice` into the report.  
You may **explain** and suggest rewrites; you may **not** mark a script Critical as passed.

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

Use checklist Pass 4. Trust script `line_count` and time-sensitive / path hints.

**Completion criterion:** Concrete cut-or-move suggestions listed.

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
- Do not expose raw JSON or unexplained exit codes in the business report
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

## Verification

- [ ] `hard_gates.py` was executed on the target directory
- [ ] 新手入口生成的真实报告位于目标和源码仓库之外
- [ ] `audit-manifest.json` 证明审计前后目标未变化
- [ ] Both reports share the same scores, counts, finding IDs, and conclusion
- [ ] Technical report scores match JSON exactly
- [ ] Business report contains no unexplained technical terms
- [ ] No script Critical was overridden
- [ ] User was advised whether ship floor is met
- [ ] PDCA×SMART matrix filled (Plan/Do/Check/Act × S/M/A/R/T notes)
- [ ] Every PDCA `missing` cell mapped to a finding or dated waiver
- [ ] Decision-owned gaps were asked, not invented (or left as `unknown — 待用户确认`)

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

## Red Flags

- Writing a score without running the script
- Re-scoring basic_usable after the script
- Skipping check-axes guidance when script severity is critical
- Report without PDCA×SMART matrix
- Calling a skill "done" with no Check (Verification) or Act (fix path)
- Writing exclusions, triggers or acceptance evidence the user never stated
- Interrogating the user with a long question list instead of three at a time

## Out of scope

- Creating a skill from scratch
- Automated multi-case behavioral evals (v2)
- Editing the target unless the user explicitly asks
- Inventing quarterly OKRs for a skill that only needs a session exit criterion
