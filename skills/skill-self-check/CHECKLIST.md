# Skill Self-Check Checklist

Plain-language items for auditing a target skill. Optional Matt-style terms appear in parentheses. Use with [SKILL.md](SKILL.md).

**Who decides**

| Kind | Owner | Notes |
|------|-------|-------|
| Hard gates, scores, regex hints | `scripts/hard_gates.py` | Model must not override |
| Qualitative predictability / anatomy / PDCA+SMART | Model | After script JSON is in hand |

**Scores (script)**

- `basic_usable` /5 — file+frontmatter, name match, description voice/triggers, actionable body, verification or Done-when
- `contract_clarity` /5 — When to Use, When NOT, named check axes, verification checkboxes, rationalizations/red flags
- `support_kit` n/applicable — references (资料), examples (案例), memory (落地记忆), scripts (脚本); explicit `N/A` / `不适用` does not dock; **does not** affect ship floor
- `ship_floor_met` — `basic_usable >= 4` and zero script Critical

**Severity**

| Level | When |
|-------|------|
| Critical | Hard gate fail, or review skill missing named check axes |
| Should fix | Predictability or verification gap that will cause inconsistent runs |
| Nice | Polish, token trim, optional anatomy sections for reference-only skills |

---

## Pass 1 — Hard gates (script-owned)

| # | Check (plain) | Fail if | Sev |
|---|----------------|---------|-----|
| 1.1 | Skill folder has `SKILL.md` | Missing file | Critical |
| 1.2 | YAML frontmatter has `name` and `description` | Missing either | Critical |
| 1.3 | `name` is lowercase letters/numbers/hyphens only, ≤64 chars | Invalid chars, spaces, or too long | Critical |
| 1.4 | `name` matches directory name | Mismatch | Critical |
| 1.5 | `description` non-empty, ≤1024 chars | Empty or over limit | Critical |
| 1.6 | Description is third person (not "I can…" / "You can…") | First/second person as the main voice | Critical |
| 1.7 | Description states WHAT and WHEN (capabilities + triggers) | Only vague help text; no triggers | Critical |
| 1.8 | Body is actionable: ordered steps and/or clear review/reference rules | Narrative diary, slogans only, no procedure | Critical |
| 1.9 | If `disable-model-invocation: true`, description may be human-facing one-liner; if omitted/false, description must be model-facing triggers | Model-invoked skill with empty trigger list | Critical |
| 1.10 | Verification section or Done-when markers | Neither detected | Should fix |
| 1.11 | `SKILL.md` is saved as UTF-8 | Decodes only as GBK / Big5 / CP1252 | Should fix |
| 3.10 | Named check axes (color / composition / copy / …) | Review/audit skill with no axis list | Critical if review-like |

**Bilingual detection:** 1.7 accepts Chinese triggers (`用于` / `适用` / `当用户` / `使用场景`) and Chinese WHAT verbs (`生成` / `审查` / `检查` / `编排`). Chinese headings count too: `何时使用`, `何时不用` / `不适用`, `检查轴` / `维度`, `验收` / `校验`, `常见借口` / `危险信号`.

---

## Pass 2 — Predictability (Matt)

| # | Check (plain) | Fail if | Sev |
|---|----------------|---------|-----|
| 2.1 | Invocation choice fits use (model- vs user-invoked) | Always-on skill that only runs by hand still burns context; or auto skill with no discoverable triggers | Should fix |
| 2.2 | Model-invoked description is pruned: front-load job, one trigger per branch, no body dump (description pruning) | Synonym duplication; workflow summary that agents may follow instead of the body | Should fix |
| 2.3 | Each step ends with a checkable done condition (completion criterion) | "Understand / polish / improve" with no observable bar | Should fix |
| 2.4 | Done conditions are demanding enough where it matters (legwork) | "Make a list" when the job needs "every X accounted for" | Nice / Should fix if high-stakes |
| 2.5 | Prefer positive target behavior over bans (negation) | Many "don't…" without "do…" alternative | Should fix |
| 2.6 | No lines that only restate the model default (no-op) | "Be careful", "think step by step", "write good code" with no new constraint | Should fix |
| 2.7 | One meaning, one place (duplication / single source of truth) | Same rule restated in 2+ places with drift risk | Should fix |
| 2.8 | Long or branch-only material is linked out (progressive disclosure / sprawl) | `SKILL.md` buries steps under optional reference | Should fix if steps hard to find |
| 2.9 | A compact pretrained concept could replace repeated phrases (leading word) | Same triad restated three times; no anchor word | Nice |
| 2.10 | Later steps do not tempt rushing the current one (premature completion) | Vague current step + highly visible next phase in same breath | Nice / Should fix if observed pattern |

---

## Pass 3 — Anatomy and verification (Addy)

| # | Check (plain) | Fail if | Sev |
|---|----------------|---------|-----|
| 3.1 | Short Overview: what + why | Missing or essay-length with no pitch | Nice / Should fix if purpose unclear |
| 3.2 | When to Use includes positive triggers | No trigger list | Should fix |
| 3.3 | When NOT to use (exclusions) present for non-trivial skills | Easy to over-apply; no exclusions | Should fix |
| 3.4 | Core Process is specific ("Run X and verify Y"), not vibes | "Ensure quality", "handle appropriately" | Should fix |
| 3.5 | Exit Verification checklist with evidence (verification) | No verification section, or checkboxes with no proof | Should fix (Critical if skill claims a quality gate) |
| 3.6 | Workflow/discipline skills have Common Rationalizations table | Process skill with skip-prone steps and no rebuttals | Should fix |
| 3.7 | Workflow/discipline skills have Red Flags | No observable "you're doing it wrong" list | Nice / Should fix for discipline skills |
| 3.8 | Skill is a workflow (process over knowledge dump) | Encyclopedia with no steps for a how-to skill | Should fix |
| 3.9 | Reference-only skills are allowed flat rules — but still need clear apply-all bar | Review skill with no "every rule applied" style demand | Should fix |

**Skill type hint**

- **Workflow / discipline** (TDD, review gates, shipping): 3.5–3.7 expected.
- **Reference** (API/rules list): Overview + When + exhaustive apply bar; rationalizations optional.

---

## Pass 4 — Prune and tokens (Cursor + Matt pruning)

| # | Check (plain) | Fail if | Sev |
|---|----------------|---------|-----|
| 4.1 | `SKILL.md` under ~500 lines | Far over; no split plan | Should fix |
| 4.2 | Links are one level deep from `SKILL.md` | Chain A→B→C for must-have material | Should fix |
| 4.3 | Terminology consistent | Mixes "endpoint/URL/route" for the same thing | Nice |
| 4.4 | No time-sensitive "before August 20XX use old API" without an Old patterns fold | Dated instructions that will rot | Should fix |
| 4.5 | Stale or irrelevant lines removed (sediment / relevance) | History of abandoned approaches left as main path | Should fix |
| 4.6 | Windows-style paths avoided in instructions | `scripts\foo.py` instead of `scripts/foo.py` | Nice |
| 4.7 | Default tool/approach given; escape hatch only when needed | Laundry list of five equivalent libraries | Should fix |
| 4.8 | Scripts (if any) documented: when to run, expected output | Scripts present with no usage | Should fix |

---

## Pass 6 — Support kit (script-owned; blue light)

Four modules beyond `SKILL.md`. Workflow skills are expected to pack what they need; mark `资料/案例/落地记忆/脚本: N/A` when a module truly does not apply.

| # | Check (plain) | Fail if | Sev |
|---|----------------|---------|-----|
| 6.1 | **资料** — `references/` present (link from SKILL.md recommended) | Workflow has steps but no materials pack and no N/A | Should fix |
| 6.2 | **案例** — `examples/` or a substantive `## 案例` / Example section | Workflow with no worked example and no N/A | Should fix |
| 6.3 | **落地记忆** — if the skill writes/reads cross-run state, path + fields are named | Mentions 回写/发送记录/冷却/落表 but no schema (`sent_at`, JSON shape, …) | Should fix |
| 6.4 | **脚本** — `scripts/` present and named in SKILL.md when automation is claimed | `scripts/` undocumented, or body claims automation with no `scripts/` | Should fix |

N/A markers recognised: table rows or `资料: N/A` / `案例: 不适用` style lines in `SKILL.md`.

---

## Pass 5 — PDCA + SMART (model)

Full mapping: [references/pdca-smart.md](references/pdca-smart.md).

### PDCA

| # | Check (plain) | Fail if | Sev |
|---|----------------|---------|-----|
| 5.1 | **Plan** — When / When NOT + check axes + success shape before work | No scope; tips without triggers | Should fix |
| 5.2 | **Do** — Ordered steps or apply-all rules with Done when | Vibes-only; no observable progress | Should fix |
| 5.3 | **Check** — Verification with evidence | "Looks good"; no proof | Should fix (Critical if quality-gate skill) |
| 5.4 | **Act** — Red Flags / Rationalizations / retry or escalate path | One-shot prose; failure has nowhere to go | Should fix for workflow skills |

### SMART (outcome contract)

| # | Check (plain) | Fail if | Sev |
|---|----------------|---------|-----|
| 5.5 | **S**pecific — WHAT + named axes / deliverable shape | Vague "help with X" | Should fix |
| 5.6 | **M**easurable — Done when + Verification evidence | "Improve quality" only | Should fix |
| 5.7 | **A**chievable — When NOT + one-skill scope | Boils the ocean | Should fix |
| 5.8 | **R**elevant — triggers match steps and user job | Body drifts off the job | Should fix |
| 5.9 | **T**ime-bound as **run-bound exit** — invocation has a finish line | Endless refine; no stop | Should fix |

### Interview / discovery skills (optional band)

If the skill interviews humans or gathers requirements (PM intake, client ops discovery):

| # | Check (plain) | Fail if | Sev |
|---|----------------|---------|-----|
| 5.10 | Uses **5W2H** (What/Why/Who/When/Where/How/How much) | Random questions; no coverage map | Should fix |
| 5.11 | One clear question at a time; vague answers get follow-ups | Multi-ask dumps; accepts slogans | Should fix |
| 5.12 | Capture table or equivalent before proposing solutions | Jumps to skill/build advice mid-interview | Should fix |

Canonical guide for this pack's PM experiment: `exp/pm-workflow-planning/INTERVIEW.md`.

5.10–5.12 score **the target skill** when it happens to be an interview skill.
They are not the path for interviewing *your own user* about report gaps — that
is [references/gap-questions.md](references/gap-questions.md).

---

## Mini glossary (optional)

| Term | Meaning |
|------|---------|
| Predictability | Same *process* each run, not same output |
| Model-invoked | Agent can discover via description (pays context load) |
| User-invoked | `disable-model-invocation: true`; human must name it |
| Completion criterion | Checkable "done" for a step |
| No-op | Instruction that does not change default behavior |
| Negation | Steering by "don't…" that can backfire |
| Progressive disclosure | Heavy reference behind a link |
| Leading word | Short pretrained concept that anchors behavior |
| Verification | Exit checklist with evidence |
| Rationalizations | Excuses agents use to skip steps, plus rebuttals |
| PDCA | Plan → Do → Check → Act closed loop inside the skill |
| SMART | Specific / Measurable / Achievable / Relevant / run-bound exit for outcomes |
| 5W2H | What / Why / Who / When / Where / How / How much — interview clarity |
