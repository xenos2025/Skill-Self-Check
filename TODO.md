# Roadmap / TODO

Open an issue with the `roadmap` label to propose items.

## Near term

- [x] PDCA + SMART Pass 5 (matrix in report; T = run-bound exit)
- [x] Recognize Chinese WHEN triggers, headings and WHAT verbs in `hard_gates.py`
- [x] Survive non-UTF-8 `SKILL.md` (finding `1.11`) and force UTF-8 stdout
- [x] Fix check-axis label parsing so hyphens are not truncated (`Per-role …` → `Per`)
- [x] Tighten `WHEN_TRIGGER_RE`: `run after` / `after you` are weak signals that
      let trigger-free descriptions pass 1.7
- [x] Emit a finding when `contract_clarity.when_to_use` is docked for
      user-invoked skills (score drops today with nothing in `findings`)
- [x] Expand WHAT-verb list (`routes`, `orchestrates`, …)
- [ ] Optional script hints for PDCA section headings (Plan/Do/Check/Act aliases)
- [ ] `npx skills add` / marketplace install notes once the public repo URL is set
- [x] Boss-friendly SVGs under `assets/diagrams/` (+ `zh/`)
- [x] Third light `support_kit` (资料/案例/落地记忆/脚本; N/A; not ship floor)
- [x] Generic B0–B6 work-readiness gates promoted to `skills/agent-work-readiness`
- [x] Offline dual-line growth scorecard with preserved audit and evidence views

## Productization hook (`exp/`)

Reserved for a future **PM / ops workflow planner** that helps foreign trade,
factory, and ecommerce teams:

- [x] Interview → workflow map → skill gap proposal (draft under `exp/pm-workflow-planning/`)
- [x] Conditional operational data contract: judge/ask before selecting L value, S source, V verification, and R record modules
- [x] First industry example: B2B customer background investigation with browser evidence gates
- [ ] Additional industry packs (DTC Shopify, factory OEM) as experiment folders
- [ ] Promote only after self-check ship floor + real-client pilot notes

## Later

- [x] Ship-safety static preflight (`skills/skill-ship-safety`): promise
      inventory, send-gate scan, and explicit execution-unverified boundary
- [ ] Trusted-runner adapter for isolated gate-bypass behavior tests
- [ ] Lightweight behavioral evals (trigger / non-trigger cases)
- [ ] User research for whether beginners understand B0–B6, Lv0–Lv5, and the
      single “next quest” without facilitator explanation
- [x] CI job: regression tests + `hard_gates.py` on all `skills/*` + diagram reproducibility
- [ ] Optional uninstall.ps1 / uninstall.sh for Cursor skills dir
