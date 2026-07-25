# Ship-Safety Report（安全真发审计）

**Target:** `<path/to/skill>`  
**Date:** `<YYYY-MM-DD>`  
**Script:** `python scripts/ship_safety.py <skill-dir> --pretty [--exec]`  
**Passes covered:** 0 Script · 1 Criticals · 2 Gate bypass · 3 Write-back · 4 Claims

## 判决

# **放行 / 停发**

`<One sentence: why. Stop-ship if any script Critical, any gate bypass, or real send on by default.>`

| 来源 | 结果 |
|------|------|
| 脚本 verdict（禁止手改宽松） | `stop_ship / pass_with_watchlist` |
| 门禁旁路测试（模型，沙盒） | `全部拦截 / 有放行（Critical）/ 未测` |
| 默认不真发 | `已验证 / 未验证 / 默认真发（Critical）` |

| Severity | Count (script + model) |
|----------|------:|
| Critical | 0 |
| Should fix | 0 |
| Watchlist / info | 0 |

## 承诺清单（脚本）

| 文档命令 | 出处 | 脚本存在 | 子命令已实现 | probe |
|----------|------|----------|--------------|-------|
| `scripts/x.py foo` | SKILL.md:12 | yes/no | yes/no/– | ok / Unknown command / 未跑 |

## 外发入口（脚本 + 模型判默认值）

| 文件 | 能力 | dry-run guard | 默认不真发？（模型） |
|------|------|---------------|----------------------|
| `scripts/sender.py` | smtp | yes/no | yes / no / 未验证 |

## 门禁旁路测试（模型，沙盒）

| 门禁 | fixture | 期望 | 实测 | 结果 |
|------|---------|------|------|------|
| blacklist | blocked@fixture.test | 拦截且不记为已发 | … | pass / FAIL |

## Critical（停发项）

### C1. `<short title>` · source: `script|model`

- **问题:** …
- **证据:** …
- **建议改法:** …

## Should fix

### S1. `<short title>` · source: `script|model`

- **问题:** … / **建议改法:** …

## Watchlist（放行后观察项）

- …

## 下一步

- 判决为**停发**：先修 Critical，逐条附带证据复测，全部通过后再申请放行。
- 判决为**放行**：保持外发默认关闭；首批真发用最小批量并人工复核 watchlist。
- 说 **「按意见改」** —— 代改 Critical / Should fix（外发默认关不动摇）。
