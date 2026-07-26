# Skill Self-Check Technical Report（技术版）

**Target:** `<path/to/skill>/SKILL.md`  
**Date:** `<YYYY-MM-DD>`  
**Script:** `python scripts/hard_gates.py <skill-dir>`  
**Passes covered:** 0 Script · 1 Hard gates · 2 Predictability · 3 Anatomy · 4 Prune · 5 PDCA+SMART
**Schema:** `<schema_version>` · **Audit level:** `<audit_level>`

> 本报告面向开发、测试和技能维护者。面向业务读者的结论使用
> `REPORT-BUSINESS-TEMPLATE.md`，两份报告必须共享相同分数、问题编号和结论。

## 分数（脚本，禁止手改）

| 维度 | 得分 | 含义 |
|------|------|------|
| 基础可用 `basic_usable` | `<n>/5` | ≥4 且无 Critical → 达到静态基础门槛，不代表行为已验证 |
| 契约清晰 `contract_clarity` | `<n>/5` | When/When-NOT/检查轴/Verification/反合理化 |
| 配套齐备 `support_kit` | `<n>/<max>` 或 `n/a` | 资料/案例/落地记忆/脚本；N/A 不扣分；不挡 ship floor |
| Ship floor | `yes/no` | 来自 `scores.ship_floor_met`（只看绿灯+Critical） |

`<One sentence: 是否达到 ship floor；蓝灯是否 kit_complete；若否先改 Critical 再补配套。>`

配套模块明细（抄自 JSON `scores.support_kit.modules`）：

| 模块 | 状态 | 说明 |
|------|------|------|
| 资料 references | `pass/fail/na` | … |
| 案例 examples | `pass/fail/na` | … |
| 落地记忆 memory | `pass/fail/na` | … |
| 脚本 scripts | `pass/fail/na` | … |

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

## 还需你确认（只有你知道的空缺）

只列 Critical / Should fix 里属于业务决策的项。一次问一个，一轮最多三个；其余留在这张表里。
问法与可粘贴模板见 [references/gap-questions.md](references/gap-questions.md)。

| # | 对应 finding | 要问你的一句话 | 我建议的答案（可直接改） | 状态 |
|---|--------------|----------------|--------------------------|------|
| Q1 | `<3.3>` | … | … | 待回答 / 已答 / `unknown — 待用户确认` |

`<若无此类空缺，写：本次没有需要你决策的空缺。>`

## 各 Pass 覆盖情况

| Pass | 结果 |
|------|------|
| 0 脚本 | 已运行 / 运行失败 |
| 1 硬门禁 | 取自脚本计数 |
| 2 可预测性 | … |
| 3 结构解剖 | … |
| 4 修剪 | … |
| 5 PDCA+SMART | 矩阵已填 / 有缺口 |

## 下一步

- Ship floor **未过**：先改 Critical，别急着靠实战观察去打磨。
- Ship floor **过了**但 PDCA 的 Check / Act **缺失**：补上验收和出错处理，才算闭环。
- Ship floor **过了**且 PDCA 正常：进入受控试用或行为验证；不要把静态通过当成安全执行证明。
- 说 **「按意见改」** —— 我来改 Critical / Should fix。
- 说 **「帮我补」** —— 我一次问你一个问题，把上面「还需你确认」的空缺补齐；你点头之后才写进文件。
