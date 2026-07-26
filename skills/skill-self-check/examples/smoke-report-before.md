# Skill Self-Check Report

> Technical companion to
> [smoke-report-before-business.md](smoke-report-before-business.md).

**Target:** `examples/fixtures/bad-commit-helper/SKILL.md`  
**Date:** 2026-07-27
**Script:** `python skills/skill-self-check/scripts/hard_gates.py skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty`  
**Passes covered:** 0 Script · 1 Hard gates · 2 Predictability · 3 Anatomy · 4 Prune · 5 PDCA+SMART

> Worked example. Regenerate after changing scoring logic — CI (`.github/workflows/hard-gates.yml`) keeps the fixture failing, but the numbers below are maintained by hand.
> Revalidated on 2026-07-27 after the one-command audit and growth ruleset
> 0.2 changes: hard-gate scores and counts remain unchanged.

## 分数（脚本，禁止手改）

| 维度 | 得分 | 含义 |
|------|------|------|
| 基础可用 `basic_usable` | `2/5` | 只拿到「有 frontmatter」「正文有编号步骤」两分 |
| 契约清晰 `contract_clarity` | `0/5` | When / When-NOT / 检查轴 / Verification / 反合理化 全缺 |
| 配套齐备 `support_kit` | `0/2` | 工作流缺资料包与案例包（记忆/脚本 N/A） |
| Ship floor | `no` | 4 个 Critical，且 `basic_usable < 4` |

不能发布：`name` 非法且与目录不一致、description 第一人称且无触发词、全文没有任何出口证据。先修 4 个 Critical，再补 Verification、完成标准，以及蓝灯配套。

| 模块 | 状态 | 说明 |
|------|------|------|
| 资料 references | fail | 无 `references/` |
| 案例 examples | fail | 无 `examples/` / 案例节 |
| 落地记忆 memory | na | 无跨次状态信号 |
| 脚本 scripts | na | 无自动化声称 |

| Severity | Count (script + model) |
|----------|------:|
| Critical | 4 |
| Should fix | 12 |
| Nice | 1 |

脚本计数为 Critical 4 / Should fix 12 / Nice 0（含 `6.1`/`6.2`）；下面的 N1 是模型追加的定性发现。

---

## PDCA × SMART（模型，须填）

| PDCA | Status | Evidence (quote / section) |
|------|--------|----------------------------|
| Plan | missing | 无 When / When NOT / 检查轴；只有 “Git is important.” |
| Do | weak | `## Steps` 有 1–3 编号，但「Look at the changes / Write a message / Done」没有任何完成标准 |
| Check | missing | 无 Verification，无 Done when，`Done` 只是第三步的标题 |
| Act | missing | 无 Red Flags、无 Rationalizations、失败无去处 |

| SMART | Status | Note |
|-------|--------|------|
| Specific | missing | “help you with git stuff” 未说明交付物是 commit message |
| Measurable | missing | 无格式约束（长度 / type 前缀）、无验收证据 |
| Achievable | weak | 范围看似小，但没有 When NOT，容易被当成通用 git 助手 |
| Relevant | weak | 触发词与正文都指向 commit，但 description 泛化到「git stuff」 |
| Time / run-bound | missing | 第三步写 `Done` 却没定义完成条件，等于没有终点 |

可用性和闭环双失：不只是「能用但没闭环」，而是 Plan / Check / Act 三段都空。

---

## Critical

### C1. `name` 含大写，非法 · source: `script`

- **问题:** `name: Helper`（脚本 1.3，evidence `Helper`）。
- **为什么:** Cursor 要求小写字母 / 数字 / 连字符，≤64 字符；名称是发现与安装的主键。
- **建议改法:**

```yaml
name: writing-commit-messages
```

### C2. `name` 与目录不一致 · source: `script`

- **问题:** 脚本 1.4：`name='Helper' dir='bad-commit-helper'`。
- **为什么:** 名称与目录不一致时，安装后可能加载不到或重名覆盖。
- **建议改法:** 目录同步改名为 `writing-commit-messages/`，与 `name` 逐字相同。

### C3. description 用第一 / 第二人称 · source: `script`

- **问题:** `I can help you with git stuff when you need it.`（脚本 1.6）。
- **为什么:** description 会被注入系统提示，须第三人称陈述能力，而不是对用户说话。
- **建议改法:** 见 C4 的整段重写。

### C4. description 缺 WHEN 触发词 · source: `script`

- **问题:** 脚本 1.7：模型可调用的技能没有可判定的触发条件。
- **为什么:** 触发过宽会到处乱调用，过窄则永不触发——两者都会让行为不可预测。
- **建议改法:**

```yaml
description: >-
  Generates concise conventional-commit messages from staged diffs.
  Use when the user asks for a commit message, reviews staged changes,
  or wants help wording a commit.
```

---

## Should fix

| # | 发现 | 问题 → 建议改法 | 来源 |
|---|------|-----------------|------|
| S1 | 1.7b 缺 WHAT 动词 | “help with git stuff” 未说明产出 → 以 `Generates …` 开头 | script |
| S2 | 1.10 无 Verification / Done when | 没有出口证据 → 加 `## Verification` 复选框 | script |
| S3 | 3.2 缺 When to Use | 无正向触发清单 → 列「用户要 commit message」等 3 条 | script |
| S4 | 3.3 缺 When NOT to use | 易被当通用 git 助手 → 排除「改写历史 / 解决冲突」 | script |
| S5 | 3.10 检查轴未命名 | `detected_axes=[]` → 命名 summary 格式 / body 理由 / 是否代提交 | script |
| S6 | 3.5 无带证据的复选框 | 「看起来做完了」→ 已读 diff / 格式正确 / 未擅自 commit | script |
| S7 | 3.6 缺 Rationalizations / Red Flags | 小 diff 时爱跳过阅读 → 表里写明「Diff 小也要读全」 | script |
| S8 | 4.4 时效性表述 | 「before 2024 people used different formats」会过期 → 删除或折叠进 Old patterns | script |
| S9 | 2.6 无操作指令 | 「be careful」「think step by step」不改变默认行为 → 删掉换成可检查约束 | script |
| S10 | 2.5 否定密度过高 | 3 处 “Don't …” 未给目标形状 → 「Summary 说明改动意图，body 解释原因」 | script |
| S11 | 6.1 缺资料包 | 工作流无 `references/` → 加材料或标 `资料 N/A` | script |
| S12 | 6.2 缺案例包 | 无 examples/案例 → 加 fixture 或标 `案例 N/A` | script |

**S2 / S6 paste-ready:**

```markdown
## Verification

- [ ] 已读取完整 `git diff --staged`
- [ ] Summary ≤72 字符且带 conventional type
- [ ] 已展示消息，未擅自执行 commit
```

---

## Nice

### N1. 用一个锚词收束质量标准 · source: `model`

- **问题:** 「Make things better / Improve the message / write something nice」三处形容词各说各话。
- **为什么:** 一个预训练概念（*conventional commit*）比三处模糊形容词更省 token、行为更稳。
- **建议改法:** 全文以 conventional commit 作为唯一质量锚，删掉「或不用 / 或写得好看」的并列选项。

---

## 还需你确认（只有你知道的空缺）

C4 / S4 / S6 里给的都是**建议稿**：触发场景、排除范围、验收凭据取决于你团队怎么做事，我不替你定。
一次问一个，一轮最多三个。

| # | 对应 finding | 要问你的一句话 | 我建议的答案（可直接改） | 状态 |
|---|--------------|----------------|--------------------------|------|
| Q1 | `3.3` 缺 何时不用 | 「什么情况下**不该**让它写 commit message？有没有必须你自己动手的？」 | 排除改写历史、解决冲突、代你执行 `git commit` | 待回答 |
| Q2 | `3.5` 验收没有凭据 | 「它写完之后，你看什么就知道写对了？」 | Summary ≤72 字符且带 conventional type，且消息只展示不提交 | 待回答 |
| Q3 | `1.7` / `3.2` 触发场景 | 「你平时会说哪句话让它上场？给我一两句原话。」 | 「帮我写个 commit」「看下暂存区改了啥」 | 待回答 |

## 各 Pass 覆盖情况

| Pass | 结果 |
|------|------|
| 0 脚本 | 已运行；exit 1，`ship_floor_met: false` |
| 1 硬门禁 | fail：4 Critical（1.3 / 1.4 / 1.6 / 1.7） |
| 2 可预测性 | S9 / S10（脚本命中）+ N1（模型） |
| 3 结构解剖 | S3–S7 |
| 4 修剪 | S8；`line_count` 23，无超长问题 |
| 5 PDCA+SMART | 矩阵已填：Plan / Check / Act 全缺 |
| 6 配套齐备 | S11 / S12；`support_kit 0/2` |

## 下一步

Ship floor 未达到：先修 4 个 Critical，再按 S1–S10 补契约，不要指望「先用起来再观察」。  
Smoke 判据：`before-after.md` 列出的主题（弱 description、缺 verification、no-op、negation、缺完成标准）全部被命中。  
说 **「按意见改」** 可对真实目标技能应用 Critical / Should fix。  
说 **「帮我补」** 我按 Q1–Q3 一次问一个，答完再写进文件。
