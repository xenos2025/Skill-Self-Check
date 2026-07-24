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

## [0.1.0] — 2026-07-25

### Added

- `skill-self-check` skill: four-pass review, checklist, report template
- `scripts/hard_gates.py`: deterministic scores (`basic_usable`,
  `contract_clarity`, `ship_floor_met`) and Critical/Should/Nice findings
- Fixture `examples/fixtures/bad-commit-helper` for smoke testing
