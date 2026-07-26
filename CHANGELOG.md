# Changelog

All notable changes to this project are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- README scorecard gallery: personal Growth and project Detection screenshots
  under `assets/scorecards/`, plus CN/EN copy explaining the two offline HTML
  views and how to regenerate a suite demo.
- Maintainer platform matrix in `docs/PLATFORM-COMPATIBILITY.md` and README:
  Cursor in active use, Codex as the next comparable second platform; Claude
  Code, WorkBuddy, and Coze listed as not tested yet (not a certification).
- Red Flags sections on `agent-work-readiness` and `skill-growth-scorecard` so
  skip-prone discipline steps have explicit observable failure signals.
- `skill-self-check/scripts/run_full_audit.py`: one read-only command produces
  matched personal/project offline scorecards, source JSON, and a before/after
  target fingerprint manifest; real reports are refused inside the target or
  its source repository.
- Comparable cross-platform evidence contract requiring two distinct platforms
  to share the same contract and sanitized-fixture SHA-256 identifiers, plus
  `platform_record.py` for generating review-gated records.
- `agent-work-readiness`: deterministic B0–B6 gates for turning one oral,
  repeated business process into a goal, workflow, role/handoff, metric,
  delegation-control, and learning-evidence work package.
- `skill-growth-scorecard`: combines readiness, hard-gate, ship-safety, and
  optional behavior JSON into one rules-based growth profile plus a
  single-file offline HTML with growth, detection, and technical-evidence views.
- Regression coverage for readiness evidence boundaries, static-vs-behavior
  level caps, stop-ship suppression, cross-platform evidence, and offline HTML.
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

- `CONTRIBUTING.md` and `AGENTS.md` updated for the four-skill pack: full
  unittest discover, scorecard private-output rules, script ownership map, and
  platform-evidence pointers.
- `skill-growth-scorecard` description and check axes tightened for clearer
  triggers and named review axes (business readiness, maturity, type, next
  quest, privacy, browser behavior).
- Growth ruleset 0.2 makes external-action and write-back applicability
  evidence-based: verified N/A can satisfy a control, but omission or an
  absolute local evidence path cannot. Write-back N/A also requires a trusted
  unchanged-target record.
- Default installers and plugin metadata now expose four stable skills:
  readiness, self-check, ship-safety, and growth scorecard.
- Growth scorecards now identify the analyzed Skill or work process in the
  header, detection view, technical evidence, document title, and profile JSON.
- The growth view now presents an original Skill navigator character, a
  type-first declaration, and six single-direction evidence-coverage axes.
  Percentages are deterministic 0–4 state translations, not personality
  probabilities or complementary gap scores. Each axis states its 100%
  full-evidence condition; detection and technical views remain available from
  the same fact set.
- The growth view now frames type and level as personal Skill-building
  capability demonstrated by the analyzed work sample. Project delivery
  verdicts remain unchanged in detection and technical evidence, but no longer
  appear as personal badges.
- Personal capability cards now use a deterministic evidence-based assessment:
  one concrete capability headline, the current stage, and up to three growth
  priorities. Product-explanation meta copy is no longer shown as if it were a
  personal evaluation; the same fields are preserved in profile JSON.
- Growth “next quest” cards now teach personal capability development by level,
  including measurable goals, scenario judgment, reusable components or
  scripts, Harness placement, testing, safety, recovery, and portability.
  Finding-specific remediation remains separately visible in Detection Results.
- `ship_safety.py --exec` is now a safe compatibility refusal: it does not run
  target code and returns `execution_unverified` until a trusted isolation
  runner supplies behavioral evidence.
- Installers reject drive/filesystem roots, the user home, the repository
  root, and destinations whose final directory name does not match the skill.
- Static ship-floor wording now means "ready for controlled trial", not proof
  of behavioral safety or permission to send.
- Pass 3 now splits gaps: wording/structure are rewritten by the model, while
  triggers, exclusions, acceptance evidence and escalation are asked (one
  question at a time, max three per round) instead of invented
- Report template’s closing sections are Chinese, matching the rest of the report
- Boss-facing scores are now **three lights**: green `basic_usable`, amber
  `contract_clarity`, blue `support_kit` (资料/案例/落地记忆/脚本; N/A allowed;
  does not block ship floor). Diagram `05-three-lights.svg` replaces two-lights.

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
