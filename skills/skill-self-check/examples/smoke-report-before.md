# Skill Self-Check Report

**Target:** `examples/before-after.md` → Before block (as `bad-commit-helper/SKILL.md`)  
**Date:** 2026-07-24  
**Passes covered:** 1 Hard gates · 2 Predictability · 3 Anatomy · 4 Prune

## 总评

不能发布：硬门槛多处失败（非法 `name`、第一人称且无触发的 description、步骤不可验收）。四趟均有发现；先修 Critical，再补 Verification 与完成标准。

| Severity | Count |
|----------|------:|
| Critical | 3 |
| Should fix | 6 |
| Nice | 1 |

---

## Critical

### C1. `name` 非法且与目录不一致

- **问题:** `name: Helper` 含大写；若目录为 `bad-commit-helper` 则与 `name` 不一致。
- **为什么:** Cursor / agentskills 要求小写连字符；名称是发现与安装的主键。
- **建议改法:**

```yaml
name: writing-commit-messages
```

目录同步为 `writing-commit-messages/`。

### C2. description 第一人称且缺少 WHAT+WHEN

- **问题:** `I can help you with git stuff when you need it.`
- **为什么:** 注入系统提示应用第三人称；过宽触发会导致乱调用或从不调用。
- **建议改法:**

```yaml
description: >-
  Generates concise git commit messages from staged diffs using conventional
  commits. Use when the user asks for a commit message, reviews staged changes,
  or wants help wording a commit.
```

### C3. 正文几乎不可执行

- **问题:** Steps 为「看改动 → 写消息 → Done」，无工具、无格式、无退出证据。
- **为什么:** Agent 无法判断何时完成、产出何种形状；属于硬门槛「不可执行」。
- **建议改法:** 改为带完成标准的三步（读 `git diff --staged` → 起草 conventional message → 展示但不擅自 commit）。见 After 示例。

---

## Should fix

### S1. 步骤无完成标准 (completion criterion)

- **问题:** 「Understand the diff」「Improve the message」不可观察。
- **为什么:** 易导致未读完 diff 就交稿（premature completion）。
- **建议改法:** 每步写 **Done when:**（例如：已拿到完整 staged diff；summary ≤72 字符且含 type）。

### S2. 无操作指令 (no-op)

- **问题:** 「Always be careful and think step by step.」
- **为什么:** 不改变默认行为，只占 token。
- **建议改法:** 删除；改成可检查约束（读 staged diff、禁止无 diff 瞎写）。

### S3. 否定堆叠 (negation)

- **问题:** 「Don't write bad… Don't be vague… Don't forget…」
- **为什么:** 禁令激活坏模式；应描述目标形状。
- **建议改法:** 「Summary states the change intent; body explains why。」

### S4. 缺少 Verification

- **问题:** 无出口检查。
- **为什么:** 流程类 skill 无证据即「看起来写完了」。
- **建议改法:** 增加 Verification：已读 diff / 格式正确 / 未擅自 commit。

### S5. 缺少 When NOT 与 Rationalizations

- **问题:** 无排除场景；无「借口→反驳」表。
- **为什么:** 小 diff 时 agent 爱跳过阅读。
- **建议改法:** 补 When NOT；表中写明「Diff 小也要读」。

### S6. 多选项 + 时效闲话 (sediment / sprawl)

- **问题:** 「conventional 或不要或写得好看」+「2024 以前…」。
- **为什么:** 无默认路径；时效句易过期。
- **建议改法:** 默认 conventional；旧格式放折叠 Old patterns 或不写。

---

## Nice

### N1. 可用 leading word 收束质量

- **问题:** 「better / improve / nice」分散。
- **为什么:** 一个锚词（如 *conventional*）比三处形容词省 token、更稳。
- **建议改法:** 全文以 conventional commit 为唯一质量锚。

---

## Pass coverage notes

| Pass | Result |
|------|--------|
| 1 Hard gates | fail (3 Critical: name, description, actionable body) |
| 2 Predictability | findings S1–S3, N1 |
| 3 Anatomy | findings S4–S5 |
| 4 Prune | finding S6 |

## Next step

Smoke **passed**: expected themes from `before-after.md` all present (弱 description、缺 verification、no-op、negation、缺完成标准).  
Say **「按意见改」** to apply Critical / Should fix to a real target skill.
