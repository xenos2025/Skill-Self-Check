---
name: skill-self-check
description: >-
  Reviews a newly written or edited Agent Skill and returns ranked fix suggestions.
  Human-facing summary: run after you draft a skill to get a beginner-friendly audit.
disable-model-invocation: true
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

### Pass 0 — Run hard-gate script (required)

From this skill's directory (or via absolute path to the script):

```bash
python scripts/hard_gates.py /absolute/path/to/target-skill --pretty
```

On Windows, `py -3` is fine if `python` is missing.

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

## Write the report

Copy [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md). Fill every section.

Rules:

- Put **script scores** in the 分数表 verbatim from JSON
- Fill **PDCA×SMART** matrix (Pass 5) — model-owned, not inventing script scores
- Rank findings: Critical → Should fix → Nice
- Each finding: **问题** → **为什么** → **建议改法** (paste-ready when helpful)
- Label source: `script` vs `model` on each finding
- Default: report only. Offer: "说「按意见改」我可以代改 Critical / Should fix"
- If decision-owned gaps remain, also offer: "说「帮我补」我一次问你一个问题，把这些补齐" — follow [references/gap-questions.md](references/gap-questions.md): one question at a time, max three per round, recommended answer first
- Answers become **待确认文本 in the report**. Write them into the target `SKILL.md` only under the same gate as 「按意见改」
- If `ship_floor_met` is false: tell the user to fix Critical before relying on real-world observation to polish
- If ship floor is true but PDCA **Check** or **Act** is missing: say so — usable ≠ closed-loop

**Completion criterion (skill done):** Report includes script scores, PDCA×SMART matrix, all script Criticals with rewrites, Pass 2–5 coverage, and an offer to apply fixes or to interview for decision-owned gaps (neither applied yet).

## Verification

- [ ] `hard_gates.py` was executed on the target directory
- [ ] Report scores match JSON exactly
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
