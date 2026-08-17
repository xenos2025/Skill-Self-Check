# Plain-Language Gate Response

Use this reference to translate the deterministic core audit into concise,
plain language. It is a response shape, not a second audit or
business-readiness assessment.

## Source mapping

| Source field | Plain-language role |
| --- | --- |
| `gate_verdict` | Whether the static core gate passed |
| `gate_reasons` | Why the gate did not pass |
| `package_health` | Whether the target is an assessable Skill package |
| Critical findings | Everything that must be fixed first |
| Should-fix findings | Up to three highest-priority improvements |

Do not recalculate, soften, or override these fields. Numeric scores are
optional context and never replace the gate result.

## Response shape

### 一句话结论

Choose the sentence that matches the source result, then add the most important
reason:

- `pass` — “基础静态门禁已通过，可以进入受控试用；这不等于运行行为已经验证。”
- `fail` — “Skill 可以识别，但还有必须先修的结构或契约问题。”
- `invalid_skill_package` — “当前目录还不是可可靠安装和评估的 Skill 包。”

Show the source value once as `gate_verdict: <value>`, then use ordinary
language in the rest of the response.

### 必须先解决

Include every script Critical. For each item use:

```markdown
1. <白话标题>
   - 发生了什么：<evidence>
   - 为什么重要：<impact>
   - 建议怎么改：<paste-ready fix>
```

If there are no Criticals, say:

> 本次没有发现阻止基础使用的确定性问题。

### 建议尽快改进

Show no more than three highest-priority Should-fix findings. Use one line per
item:

```markdown
- <问题> → <影响> → <具体改法>
```

Do not hide the remaining findings. State how many are not shown and keep them
in the source JSON.

### 下一步

Give one action:

- If blockers remain: “说‘按意见改’，我会先保存基线，再修改并复检。”
- If the gate passed: “可以进入受控试用；如需 PDCA/SMART 深审或完整静态检查，请明确提出。”
- If fixes were already applied: report the `verify_fix.py` gate transition and
  remaining Critical count.

## Language guardrails

- Explain internal IDs after the plain-language title, not instead of it.
- Say “静态门禁通过”, never “已经完全安全” or “行为已经认证”.
- Do not treat a missing optional safety scan, readiness package, or
  behavior record as a core-audit failure.
- Do not invent scores, findings, evidence, or a before/after improvement.
- Keep the default response short: conclusion, all Criticals, up to three
  Should-fix items, and one next action.
