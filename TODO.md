# Roadmap / TODO

Open an issue with the `roadmap` label to propose items.

## Near term

- [x] PDCA + SMART Pass 5 (matrix in report; T = run-bound exit)
- [x] Recognize Chinese WHEN triggers, headings and WHAT verbs in `hard_gates.py`
- [x] Survive non-UTF-8 `SKILL.md` (finding `1.11`) and force UTF-8 stdout
- [ ] Fix check-axis label parsing so hyphens are not truncated (`Per-role …` → `Per`)
- [ ] Tighten `WHEN_TRIGGER_RE`: `run after` / `after you` are weak signals that
      let trigger-free descriptions pass 1.7
- [ ] Emit a finding when `contract_clarity.when_to_use` is docked for
      user-invoked skills (score drops today with nothing in `findings`)
- [ ] Expand WHAT-verb list (`routes`, `orchestrates`, …)
- [ ] Optional script hints for PDCA section headings (Plan/Do/Check/Act aliases)
- [ ] `npx skills add` / marketplace install notes once the public repo URL is set
- [x] Boss-friendly SVGs under `assets/diagrams/` (+ `zh/`)

## Productization hook (`exp/`)

Reserved for a future **PM / ops workflow planner** that helps foreign trade,
factory, and ecommerce teams:

- [ ] Interview → workflow map → skill gap proposal (draft under `exp/pm-workflow-planning/`)
- [ ] Industry packs (B2B inquiry, DTC Shopify, factory OEM) as experiment folders
- [ ] Promote only after self-check ship floor + real-client pilot notes

## Later

- [ ] Lightweight behavioral evals (trigger / non-trigger cases)
- [x] CI job: regression tests + `hard_gates.py` on all `skills/*` + diagram reproducibility
- [ ] Optional uninstall.ps1 / uninstall.sh for Cursor skills dir
