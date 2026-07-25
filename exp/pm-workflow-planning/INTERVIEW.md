# Client interview — 5W2H (ask until clear)

Status: **experiment**. Use in a private workspace. Do not paste customer PII into a public fork.

## Operating rule

Interview with **5W2H**. Ask **one question at a time**. Do not invent answers.
If the client is vague, ask a follow-up until the cell is **clear enough to design a workflow step**.

For every decision question, include:

1. the Agent's recommended answer based on confirmed context;
2. why that answer is recommended;
3. the main alternative or condition that would change it.

Wait for the client to confirm or correct the recommendation. If a fact can be
verified from the filesystem, connected tools, or permitted public sources,
look it up instead of asking. Business goals, risk tolerance, ownership, and
approval remain client decisions.

Do not start executing the workflow or drafting a Skill until the client
confirms the read-back summary.

**Done when (interview):** every 5W2H cell for the target process has a concrete answer, or an explicit `unknown — blocker` with who will supply it by when.

## 5W2H map

| Key | Chinese | Ask until clear | Weak answer (reject) | Clear enough (accept) |
| --- | --- | --- | --- | --- |
| **What** | 做什么 | What work / deliverable / decision is this? | "日常运营" | Named artifact or decision (e.g. "每周询盘复盘表") |
| **Why** | 为什么 | Why does it matter? Which KPI or risk? | "领导要的" | Tied to a metric or failure cost |
| **Who** | 谁 | Who does it, who approves, who is blocked? | "我们团队" | Role + name/title if known |
| **When** | 何时 | Cadence, deadline, trigger event? | "有空就做" | Trigger or schedule (daily / on inquiry / before ship) |
| **Where** | 在哪 | System, channel, file, store, factory line? | "电脑上" | Shopify Admin / WhatsApp / ERP / sheet path |
| **How** | 怎么做 | Steps, handoffs, tools, exceptions? | "看着办" | Ordered steps or "A then B; if X then C" |
| **How much** | 多少 | Volume, money, SLA, error rate, time cost? | "不少" | Number, range, or "unknown — need export" |

`How much` covers quantity, money, time, quality thresholds — pick what the process cares about.

## Session flow (PDCA for the interview itself)

1. **Plan** — Name the process under discussion (one process per pass). State which industry lens: 外贸 / 工厂 / 电商 / other.
2. **Do** — Walk 5W2H one cell at a time. Prefer open questions, then close with a confirm paraphrase.
3. **Check** — Read back the filled table. Ask: "有没有漏掉的例外 / 审批 / 系统？"
4. **Act** — Mark blockers; list Next Three Actions; only then draft workflow / skill proposal.

## Question bank (start here; adapt wording)

Ask in this order unless the client already answered a cell.

### What
- 我们今天要说清楚的**一件事**是什么？（一个流程 / 一个交付物）
- 做完之后，别人能看到的**结果**是什么？

### Why
- 不做这件事，最坏会发生什么？
- 成功时看哪个数字或信号？（询盘数、交期、转化、客诉…）

### Who
- 谁动手？谁审批？谁收结果？
- 客户侧 / 工厂侧 / 代理侧分别是谁？

### When
- 什么事件触发开始？（新询盘、每周一、出货前…）
- 必须在什么时间点之前完成？超时怎么办？

### Where
- 主要在哪个系统里做？（Shopify / ERP / 表格 / 邮件 / WhatsApp…）
- 证据或导出放在哪里？

### How
- 从第一步到最后一步，请按顺序说；我只记事实。
- 最常见的例外是什么？那时谁决定？

### How much
- 大概多大工作量？（单量 / SKU 数 / 周耗时）
- 可接受的错误率或 SLA 是多少？现在实际呢？

## Capture table (copy per process)

```markdown
## Process: <name>
Industry: 外贸 | 工厂 | 电商 | other
Date: YYYY-MM-DD
Interviewer:

| 5W2H | Answer | Clear? (Y/N) | Evidence / system | Open blocker |
| --- | --- | --- | --- | --- |
| What | | | | |
| Why | | | | |
| Who | | | | |
| When | | | | |
| Where | | | | |
| How | | | | |
| How much | | | | |

Next three actions:
1.
2.
3.
```

## Anti-patterns

| Temptation | Do instead |
| --- | --- |
| Ask five questions in one message | One question; wait |
| Ask a blank question with no point of view | Give a recommended answer and the main alternative |
| Fill empty cells from "industry common sense" | Leave `unknown — blocker` |
| Ask the client for a fact available in connected tools | Look it up and show the evidence |
| Jump to skill names mid-interview | Finish 5W2H table first |
| Accept slogan answers | Paraphrase + ask for artifact / number / system |
| Mix three processes in one table | New table per process |
| Start execution after the last question | Read back the workflow and wait for explicit confirmation |

## Handoff to proposal

When the table is clear, copy into [SKILL-PROPOSAL.template.md](SKILL-PROPOSAL.template.md) → **5W2H source** section, then PDCA / SMART / workflow outline.
