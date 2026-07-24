# Skill Self-Check Report

**Target:** `<path/to/skill>/SKILL.md`  
**Date:** `<YYYY-MM-DD>`  
**Script:** `python scripts/hard_gates.py <skill-dir>`  
**Passes covered:** 0 Script · 1 Hard gates · 2 Predictability · 3 Anatomy · 4 Prune · 5 PDCA+SMART

## 分数（脚本，禁止手改）

| 维度 | 得分 | 含义 |
|------|------|------|
| 基础可用 `basic_usable` | `<n>/5` | ≥4 且无 Critical → 可先真用再观察优化 |
| 契约清晰 `contract_clarity` | `<n>/5` | When/When-NOT/检查轴/Verification/反合理化 |
| Ship floor | `yes/no` | 来自 `scores.ship_floor_met` |

`<One sentence: 是否达到 ship floor；若否先改 Critical。>`

| Severity | Count (script + model) |
|----------|------:|
| Critical | 0 |
| Should fix | 0 |
| Nice | 0 |

---

## PDCA × SMART（模型，须填）

Mark each PDCA cell `ok` / `weak` / `missing` and cite a short evidence quote.  
SMART: one line each — `ok` / `weak` / `missing` + why.  
T = **run-bound exit** (Verification / handoff), not a fake calendar date unless the skill is dated ops.

| PDCA | Status | Evidence (quote / section) |
|------|--------|----------------------------|
| Plan | | When / When NOT / check axes / success shape |
| Do | | Steps + Done when |
| Check | | Verification + evidence |
| Act | | Red Flags / Rationalizations / retry path |

| SMART | Status | Note |
|-------|--------|------|
| Specific | | |
| Measurable | | |
| Achievable | | |
| Relevant | | |
| Time / run-bound | | |

`<One sentence: closed-loop? usable but missing Check/Act?>`

---

## Critical

### C1. `<short title>` · source: `script|model`

- **问题:** …
- **为什么:** …
- **建议改法:**

```markdown
<paste-ready rewrite or concrete edit>
```

---

## Should fix

### S1. `<short title>` · source: `script|model`

- **问题:** …
- **为什么:** …
- **建议改法:** …

---

## Nice

### N1. `<short title>` · source: `script|model`

- **问题:** …
- **为什么:** …
- **建议改法:** …

---

## Pass coverage notes

| Pass | Result |
|------|--------|
| 0 Script | ran / failed to run |
| 1 Hard gates | from script counts |
| 2 Predictability | … |
| 3 Anatomy | … |
| 4 Prune | … |
| 5 PDCA+SMART | matrix filled / gaps |

## Next step

- If ship floor **no**: fix Critical before relying on real-world observation.
- If ship floor **yes** but PDCA Check/Act **missing**: add Verification + fix path before calling the skill closed-loop.
- If ship floor **yes** and PDCA ok: use in real tasks; watch misses; raise SMART Measurable next.
- Say **「按意见改」** to apply Critical / Should fix.
