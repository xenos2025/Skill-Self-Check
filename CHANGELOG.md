# Changelog

All notable changes to this project are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `skill-ship-safety` skill: behavioral "safe to actually send" audit that
  complements the static self-check. `scripts/ship_safety.py` (stdlib-only)
  inventories documented commands, flags promises without implementation
  (`CMD.*`), scans send-capable scripts for dry-run guards (`EXT.*`), and
  emits a ship / stop-ship verdict; optional `--exec` probes run in a
  sandboxed copy of the target so nothing touches real files. Gate-bypass
  sandbox tests and compliance wording stay model-owned
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

### Changed

- Pass 3 now splits gaps: wording/structure are rewritten by the model, while
  triggers, exclusions, acceptance evidence and escalation are asked (one
  question at a time, max three per round) instead of invented
- Report template’s closing sections are Chinese, matching the rest of the report
- Boss-facing scores are now **three lights**: green `basic_usable`, amber
  `contract_clarity`, blue `support_kit` (资料/案例/落地记忆/脚本; N/A allowed;
  does not block ship floor). Diagram `05-three-lights.svg` replaces two-lights.

### Fixed

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
