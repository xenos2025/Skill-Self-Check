# Changelog

All notable changes to this project are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- Added opt-in `--repo-root` resource resolution to `hard_gates.py` and the
  full static runner for intentional multi-Skill source packs. The default
  remains target-local; every resolved resource reports `target` or `repo`
  scope, and absolute or repository-escaping paths remain Critical.
- Optimized the `skill-self-check` prompt contract: frontmatter now carries
  positive triggers and exclusions, script/model authority uses one explicit
  semantic boundary, and optional deep audit, full static audit, and
  fix-verification procedures load from dedicated references only when
  requested. An evidence-bounded prompt-optimization route now checks trigger
  precision, default-path economy, progressive disclosure, authority, output
  contracts, and behavior-preservation claims. The default fast path remains
  in `SKILL.md`; its current static input estimate is 2,413 tokens, down 1,631
  (about 40%) from 4,044, while the deterministic gate stays `pass` with no
  introduced findings.
- Tightened portable-path detection so a placeholder-prefixed path no longer
  hides a separate machine-specific absolute path on the same line.
- Expanded `skill-ship-safety` Shopify Admin GraphQL inventory to preserve
  distinct Store/App execute commands, resolve query files, respect Store's
  default mutation guard, and treat unreferenced mutation definitions as
  inventory rather than automatic stop-ship actions. Repository-level
  `skills/...` commands now resolve exactly and cannot fall back to a target
  script with the same basename.
- Separated external suite facts from auditor facts: auditor tests no longer
  unlock target behavior levels or runtime evidence, external target Git
  commands are disabled, conclusions are derived from current target results,
  and same-repository `--allow-repo-output` compatibility remains available.
- Narrowed the shipped pack to three check modules: `skill-self-check`,
  `skill-ship-safety`, and `agent-work-readiness`. The offline growth scorecard
  is no longer installed, documented, or required by the full static runner.

### Added

- Explicit deterministic gate contract in `hard_gates.py` schema 1.4:
  `gate_verdict`, structured `gate_reasons`, and named required checks replace
  numeric score thresholds as the blocking source of truth. Scores carry
  `scoring_effect=informational_only`; `scores.ship_floor_met` remains a
  deprecated one-generation compatibility alias.
- `hard_gates.py --out-json` writes the same report as explicit UTF-8 JSON,
  creates its parent directory, and refuses to write inside the audited Skill.
  This makes JSON reuse reliable across PowerShell versions without shell
  redirection encoding differences.
- One-way optional routing: `skill-self-check` now completes a standalone fast
  audit first and routes deep model review only on an explicit request. The
  other two shipped Skills are optional
  enhancements and are never required for the core audit.
- The former root-level business report template is now the focused
  `references/plain-language-response.md` contract. It translates the core
  gate and ranked findings without pulling safety, readiness, token,
  or runtime fields into the default route.
- Closed-loop fix verification: `skill-self-check/scripts/verify_fix.py` compares
  a Skill against the `hard_gates.py` JSON captured before the edits and reports
  score movement, resolved / introduced / persisting findings, gate and
  package-health transitions, and estimated token savings. Findings that only
  disappear because a check stopped applying no longer read as progress, and
  dimensions whose maximum changed are marked `not_comparable` instead of being
  reported as a gain or a drop. Exit code 1 on a hard regression (new Critical,
  severity escalation, or `gate_verdict` regression); score movement is
  informational. `--strict` also fails
  on newly surfaced non-critical findings. UTF-16 baselines produced by
  PowerShell redirection are accepted.
- `skill-self-check` Pass 7 (fix verification) wired into `SKILL.md`,
  `CHECKLIST.md` (checks 7.1–7.5), the technical report, and the plain-language
  response contract, so "已修复" has to come from a re-run rather than from
  memory.
- `skill-self-check/references/fix-templates.md`: paste-ready rewrites for every
  mechanical finding (`EFF.1`–`EFF.3`, `PKG.1`–`PKG.7`), including which fixes
  the model writes itself and which need the user to move or delete files.
- Efficiency guards in `hard_gates.py` (schema 1.3): `EFF.1` flags loop/retry
  instructions without a nearby stop condition (max attempts / timeout /
  escalate), `EFF.2` flags unbounded "until perfect" / 直到满意 refinement
  phrasing, and `EFF.3` flags static instruction text above the recommended
  input-token budget. Anti-loop instructions count as guards; results surface
  as a `loop_guard` metric and a token `budget` block, wired into both report
  templates and the checklist.
- Maintainer platform matrix in `docs/PLATFORM-COMPATIBILITY.md` and README:
  Cursor in active use, Codex as the next comparable second platform; Claude
  Code, WorkBuddy, and Coze listed as not tested yet (not a certification).
- Red Flags section on `agent-work-readiness` so skip-prone discipline steps
  have explicit observable failure signals.
- `skill-self-check/scripts/run_full_audit.py`: an explicit read-only full route
  produces checker source JSON and a before/after target fingerprint manifest;
  real reports are refused inside the target or its source repository.
- `agent-work-readiness`: deterministic B0–B6 gates for turning one oral,
  repeated business process into a goal, workflow, role/handoff, metric,
  delegation-control, and learning-evidence work package.
- Regression coverage for readiness evidence boundaries, hard gates, static
  ship safety, and the JSON-only full static runner.
- `skill-ship-safety` skill: static preflight audit for external-action skills
  complements the static self-check. `scripts/ship_safety.py` (stdlib-only)
  inventories documented commands, flags promises without implementation
  (`CMD.*`), scans send-capable scripts for dry-run guards (`EXT.*`), and
  emits `static_pass`, `stop_ship`, or `execution_unverified`. Target code is
  never executed by the built-in script; trusted isolated gate-bypass tests
  and compliance wording stay separately owned
  (`references/gate-bypass.md`). Fixture `examples/fixtures/promise-gap`
  plus `tests/test_ship_safety.py` wired into CI.

- Open-source packaging: LICENSE (MIT), NOTICE, CONTRIBUTING, CODE_OF_CONDUCT,
  SECURITY, SUPPORT, PRIVACY, AGENTS, plugin.json, installers, GitHub templates
- Repository layout: `skills/` product root + `exp/` experiment hook for future
  PM / workflow-planning productization
- Docs: ARCHITECTURE, INSTALLATION, AUDIENCE, DESIGN, FEATURES, TROUBLESHOOTING
- PDCA + SMART as Pass 5: `references/pdca-smart.md`, checklist items, report
  matrix; T = run-bound exit (not fake calendar OKRs)
- Client interview 5W2H guide under `exp/pm-workflow-planning/INTERVIEW.md`
  (one question at a time; required source table on skill proposals)
- Boss-friendly SVG diagrams (`assets/diagrams/` + `zh/`) via
  `branding/generate_diagrams.py`: how-to-use, PDCA, SMART, 5W2H, three lights;
  README leads with Chinese visuals
- Bilingual hard gates: Chinese WHEN triggers, WHAT verbs and headings
  (`何时使用`, `何时不用` / `不适用`, `检查轴`, `验收`, `常见借口`) now score
- Finding `1.11` for non-UTF-8 `SKILL.md`
- `tests/test_hard_gates.py` regression suite and `hard-gates` CI workflow
  (tests, ship floor for every `skills/*`, fixture still fails, diagrams reproducible)

- Fix-loop SVG (`06-fix-loop.svg` + `zh/`): write → check → report →
  fix & retry or ready to use; wired into README for beginners
- Experimental `pm-workflow-planning` skill for turning tacit business
  experience into a reviewable workflow through one-question-at-a-time,
  recommendation-led interviews
- Conditional L/S/V/R operating modules for measurable decisions, source
  provenance, evidence strength, and repeatable run records; non-applicable
  modules are recorded as `N/A` instead of becoming universal self-check gates
- Browser evidence contract for Google discovery, public LinkedIn access, and
  screenshot-backed official-site claims with explicit blocked/unverified states
- Customer background investigation example with workflow/proposal artifacts
  plus linked `score-rules`, `source-register`, `evidence-log`, and `run-log`
  CSV templates
- Gap-question loop inside `skill-self-check`: `references/gap-questions.md`
  maps decision-owned findings (`1.7` `3.2` `3.3` `3.5` `5.3` `5.4`) to one
  plain-Chinese question each, a paste-ready section, and a `unknown — 待用户确认`
  fallback; report gains a 「还需你确认」 section and a 「帮我补」 exit
- `support_kit` score in `hard_gates.py`: detects references/, examples/,
  cross-run memory contracts, and scripts/; findings `6.1`–`6.4`; explicit
  `资料/案例/落地记忆/脚本: N/A` clears the module without docking
- Business and technical report templates for both shipped skills. Both views
  share one finding set; the business view translates technical severities and
  avoids raw JSON/exit-code language.
- Plain-language companion for the bundled bad-skill worked report.
- Versioned audit metadata (`schema_version`, `audit_level`,
  `target_platform`, `limitations`) in script JSON.
- Platform capability guide covering chat-only, local static, native skill, and
  trusted isolated-runner levels.

### Changed

- Default self-check output is now focused: gate verdict and reasons, every
  deterministic Critical, at most three Should-fix items, and paste-ready
  changes. PDCA×SMART remains explicit deep-review work.
- README: beginner path now includes fix verification (`verify_fix.py`) and
  separates the fast gate from optional deep review; not a full rewrite.
- `skill-self-check` now bounds its own retry instructions and states the
  package-health rule positively, clearing the `EFF.1` and `2.5` findings it
  raised against itself.
- `CONTRIBUTING.md` and `AGENTS.md` updated for the three-checker pack: full
  unittest discovery, private-output rules, and script ownership map.
- Default installers and plugin metadata now expose three stable skills:
  readiness, self-check, and ship-safety.
- `ship_safety.py --exec` is now a safe compatibility refusal: it does not run
  target code and returns `execution_unverified` until a trusted isolation
  runner supplies behavioral evidence.
- Installers reject drive/filesystem roots, the user home, the repository
  root, and destinations whose final directory name does not match the skill.
- Static core-gate wording means "ready for controlled trial", not proof
  of behavioral safety or permission to send.
- Pass 3 now splits gaps: wording/structure are rewritten by the model, while
  triggers, exclusions, acceptance evidence and escalation are asked (one
  question at a time, max three per round) instead of invented
- Report template’s closing sections are Chinese, matching the rest of the report
- Boss-facing scores are now **three lights**: green `basic_usable`, amber
  `contract_clarity`, blue `support_kit` (资料/案例/落地记忆/脚本; N/A allowed;
  all informational and unable to override `gate_verdict`). Diagram
  `05-three-lights.svg` explains the gate-first reading order.

### Fixed

- Ship-safety no longer treats comments as implemented subcommands, scans its
  intentionally unsafe fixtures as shipped code, or treats placeholder paths
  such as `scripts/<sender>.py` as missing production commands.
- Check-axis labels preserve hyphens; weak `run after` / `after you` phrases no
  longer satisfy model-trigger rules; `routes` / `orchestrates` count as WHAT
  verbs; user-invoked skills now receive a finding when a usage section is
  missing; "automation boundary" no longer claims a scripts package.
- Non-UTF-8 `SKILL.md` crashed with `UnicodeDecodeError` and emitted no JSON,
  leaving the model with nothing to review; the reader now falls back to
  GBK / Big5 / CP1252 and reports the encoding instead
- Chinese descriptions were failing Critical `1.7` (missing WHEN triggers) and
  Chinese `何时不用` headings failed `3.3`, so valid Chinese skills were wrongly
  denied the ship floor
- JSON and the stderr summary are now written as UTF-8 even on legacy consoles
  (cp936), which previously garbled every Chinese evidence string

## [0.1.0] — 2026-07-25

### Added

- `skill-self-check` skill: four-pass review, checklist, report template
- `scripts/hard_gates.py`: deterministic scores (`basic_usable`,
  `contract_clarity`, `ship_floor_met`) and Critical/Should/Nice findings
- Fixture `examples/fixtures/bad-commit-helper` for smoke testing
