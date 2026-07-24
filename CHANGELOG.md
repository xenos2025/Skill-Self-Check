# Changelog

All notable changes to this project are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

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
  `branding/generate_diagrams.py`: how-to-use, PDCA, SMART, 5W2H, two lights;
  README leads with Chinese visuals
- Bilingual hard gates: Chinese WHEN triggers, WHAT verbs and headings
  (`何时使用`, `何时不用` / `不适用`, `检查轴`, `验收`, `常见借口`) now score
- Finding `1.11` for non-UTF-8 `SKILL.md`
- `tests/test_hard_gates.py` regression suite and `hard-gates` CI workflow
  (tests, ship floor for every `skills/*`, fixture still fails, diagrams reproducible)

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
