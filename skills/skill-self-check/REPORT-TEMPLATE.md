# Skill Self-Check Technical Report（技术版）

**Target:** `<path/to/skill>/SKILL.md`  
**Date:** `<YYYY-MM-DD>`  
**Script:** `python scripts/hard_gates.py <skill-dir>`  
**Route:** `explicit deep/full report`
**Passes covered:** 0 Script · 1 Hard gates · optional 2–5 model review · 7 Fix verification（改过才有）
**Schema:** `<schema_version>` · **Audit level:** `<audit_level>`

> 本报告面向开发、测试和技能维护者。需要白话摘要时，按
> `references/plain-language-response.md` 翻译同一份门禁结果；不得重算或
> 改写问题数量、编号和结论。

## Skill 包健康前置门

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

## 确定性门禁（脚本，禁止手改）

**`gate_verdict`:** `pass / fail / invalid_skill_package`

| 必备检查 | 状态 | 证据 |
| --- | --- | --- |
| `file_and_frontmatter` | `pass/fail` | `gate_policy.required_checks` |
| `name_valid_and_matched` | `pass/fail` | `gate_policy.required_checks` |
| `description_voice_and_triggers` | `pass/fail` | `gate_policy.required_checks` |
| `body_actionable` | `pass/fail` | `gate_policy.required_checks` |

`gate_reasons`: `<逐条抄录>`。只有此门禁、包健康和脚本 Critical 决定阻断状态。

## 信息性分数（脚本，禁止手改）

| 维度 | 得分 | 含义 |
|------|------|------|
| 基础可用 `basic_usable` | `<n>/5` | 结构成熟度提示，不决定门禁 |
| 契约清晰 `contract_clarity` | `<n>/5` | When/When-NOT/检查轴/Verification/反合理化 |
| 配套齐备 `support_kit` | `<n>/<max>` 或 `n/a` | 资料/案例/落地记忆/脚本；N/A 不扣分 |
| Legacy ship floor | `yes/no` | 已弃用的 `scores.ship_floor_met`；新报告看 `gate_verdict` |

`<One sentence: gate 是否通过；若否先处理 gate_reasons / Critical；分数只解释成熟度。>`

## 运行指标（不参与评分）

| 维度 | 状态 | 数值 | 范围与证据 |
|------|------|------|------------|
| Token 消耗 | `estimated/observed/not_assessed` | `≈n tokens` 或 `input/output/total` | 静态估算方法或行为证据引用 |
| Token 预算 | `within/exceeded/not_assessed` | 上限 `<max_recommended_input_tokens>` | 超出时对应 `EFF.3` |
| 运行时长 | `observed/not_measured` | `<duration_ms> ms` 或 `未测量` | 作者进阶行为证据里的目标运行时长；不得用审计器自身耗时代替 |
| 循环护栏 | `pass/warn/not_applicable` | 指令数 / 有护栏数 | 未设停止条件的行号；对应 `EFF.1` / `EFF.2` |
| 成绩单轨道 | `enterprise` / `advanced_audit` | 主结论 / 旁注 | 核心 gate 与可选安全证据保持分栏；行为 JSON / 跨平台只在高级审计 |

`<明确说明这些值和数字分数都不改变 gate_verdict；EFF.* 以 Should fix 形式列入问题清单。>`
`<不要把「未附 --behavior」写成核心 gate 失败；behavior 只属于显式高级审计。>`

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

- 核心门禁 **未过**：先处理 `gate_reasons` 和 Critical，别急着靠实战观察去打磨。
- 核心门禁 **过了**但 PDCA 的 Check / Act **缺失**：补上验收和出错处理，才算闭环。
- 核心门禁 **过了**且 PDCA 正常：进入受控试用或行为验证；不要把静态通过当成安全执行证明。
- 说 **「按意见改」** —— 我来改 Critical / Should fix。
- 说 **「帮我补」** —— 我一次问你一个问题，把上面「还需你确认」的空缺补齐；你点头之后才写进文件。
