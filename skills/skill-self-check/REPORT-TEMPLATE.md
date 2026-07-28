# Skill Self-Check Technical Report（技术版）

**Target:** `<path/to/skill>/SKILL.md`  
**Date:** `<YYYY-MM-DD>`  
**Script:** `python scripts/hard_gates.py <skill-dir>`  
**Passes covered:** 0 Script · 1 Hard gates · 2 Predictability · 3 Anatomy · 4 Prune · 5 PDCA+SMART · 7 Fix verification（改过才有）
**Schema:** `<schema_version>` · **Audit level:** `<audit_level>`

> 本报告面向开发、测试和技能维护者。面向业务读者的结论使用
> `REPORT-BUSINESS-TEMPLATE.md`，两份报告必须共享相同分数、问题编号和结论。

## Skill 包结构检查

**状态：** `valid_skill_package / invalid_skill_package`

**可进入成熟度评分：** `true / false`

| 检查 | 状态 | 证据 |
|------|------|------|
| 唯一 Skill 根 | `pass/fail` | … |
| 名称与根目录一致 | `pass/fail` | … |
| 标准顶层目录 | `pass/warn/fail` | … |
| 路径可移植 | `pass/fail` | … |
| 资源引用有效 | `pass/fail` | … |
| 文件名与残留健康 | `pass/warn` | … |
| 资源无重复歧义 | `pass/warn` | … |

`<如果 invalid：明确写“以下分数只用于局部文件诊断；不生成成熟度等级、能力类型或交付通过结论”。>`

## 分数（脚本，禁止手改）

| 维度 | 得分 | 含义 |
|------|------|------|
| 基础可用 `basic_usable` | `<n>/5` | ≥4 且无 Critical → 达到静态基础门槛，不代表行为已验证 |
| 契约清晰 `contract_clarity` | `<n>/5` | 使用时机 / 不适用情况 / 检查项 / 验收方式 / 常见借口 |
| 配套齐备 `support_kit` | `<n>/<max>` 或 `n/a` | 资料 / 案例 / 运行记录 / 脚本；N/A 不扣分；不挡 ship floor |
| Ship floor | `yes/no` | 来自 `scores.ship_floor_met`（只看绿灯+Critical） |

`<One sentence: 是否达到 ship floor；蓝灯是否 kit_complete；若否先改 Critical 再补配套。>`

## 运行指标（不参与评分）

| 维度 | 状态 | 数值 | 范围与证据 |
|------|------|------|------------|
| Token 消耗 | `estimated/observed/not_assessed` | `≈n tokens` 或 `input/output/total` | 静态估算方法或行为证据引用 |
| Token 预算 | `within/exceeded/not_assessed` | 上限 `<max_recommended_input_tokens>` | 超出时对应 `EFF.3` |
| 运行时长 | `observed/not_measured` | `<duration_ms> ms` 或 `未测量` | 实际运行证据里的目标运行时长；不得用审计器自身耗时代替 |
| 重试限制 | `pass/warn/not_applicable` | 重试指令数 / 已设停止条件数 | 未设停止条件的行号；对应 `EFF.1` / `EFF.2` |
| 检查类型 | `enterprise` / `advanced_audit` | 日常检查 / 高级审计 | Ship floor 已过 → 可受控试用；行为 JSON / 跨平台只在高级审计 |

`<明确说明这些值不改变 basic_usable、contract_clarity、support_kit 或 ship floor；EFF.* 以 Should fix 形式列入问题清单。>`
`<不要把「未附 --behavior」写成「没有运行检查」：一键审计已经完成日常检查，只是没有附加实际运行证据。>`

配套模块明细（抄自 JSON `scores.support_kit.modules`）：

| 模块 | 状态 | 说明 |
|------|------|------|
| 资料 references | `pass/fail/na` | … |
| 案例 examples | `pass/fail/na` | … |
| 运行记录 memory | `pass/fail/na` | … |
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

## 修改前后对照（仅在应用了修改时填）

**Script:** `python scripts/verify_fix.py <skill-dir> --baseline <pre-fix hard-gates.json>`
**Verdict:** `improved / unchanged / mixed / regressed` · **硬回退:** `true/false`

| 指标 | 改之前 | 改之后 | 方向 |
|------|--------|--------|------|
| 基础可用 `basic_usable` | `<n>/5` | `<n>/5` | `improved/unchanged/regressed/not_comparable` |
| 契约清晰 `contract_clarity` | `<n>/5` | `<n>/5` | … |
| 配套齐备 `support_kit` | `<n>/<max>` | `<n>/<max>` | … |
| Ship floor | `yes/no` | `yes/no` | … |
| 包健康 `package_health` | `<status>` | `<status>` | … |
| 静态 token 估算 | `<n>` | `<n>` | 省下 `<saved>` |

| 问题变化 | 数量 | 编号 |
|----------|------|------|
| 已解决 | `<resolved>`（其中 Critical `<resolved_critical>`） | … |
| 新增 | `<introduced>`（其中 Critical `<new_critical>`） | … |
| 仍存在 | `<persisting>` | … |
| 剩余 Critical | `<remaining_critical>` | … |

`<逐条交代「新增」里的每一项：这轮修掉了，还是列为剩余工作。>`
`<方向为 not_comparable 时说明满分变化原因（例如补上步骤后配套模块才开始适用），不要报成涨跌。>`

## 各 Pass 覆盖情况

| Pass | 结果 |
|------|------|
| 0 脚本 | 已运行 / 运行失败 |
| 1 硬门禁 | 取自脚本计数 |
| 2 可预测性 | … |
| 3 结构解剖 | … |
| 4 修剪 | … |
| 5 PDCA+SMART | 矩阵已填 / 有缺口 |
| 7 改后复检 | 已复检 / 本次未改动，不适用 |

## 下一步

- Ship floor **未过**：先改 Critical，别急着靠实战观察去打磨。
- Ship floor **过了**但 PDCA 的 Check / Act **缺失**：补上验收和出错处理，才算闭环。
- Ship floor **过了**且 PDCA 正常：进入受控试用或行为验证；不要把静态通过当成安全执行证明。
- 说 **「按意见改」** —— 我来改 Critical / Should fix。
- 说 **「帮我补」** —— 我一次问你一个问题，把上面「还需你确认」的空缺补齐；你点头之后才写进文件。
