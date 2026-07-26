# Ship-Safety Technical Report（安全真发审计·技术版）

**Target:** `<path/to/skill>`  
**Date:** `<YYYY-MM-DD>`  
**Script:** `python scripts/ship_safety.py <skill-dir> --pretty`
**Passes covered:** 0 Script · 1 Criticals · 2 Gate bypass · 3 Write-back · 4 Claims
**Schema:** `<schema_version>` · **Audit level:** `<audit_level>`

## 判决

# **静态通过 / 停发 / 未完成安全验证**

`<One sentence: why. Static pass is not permission to send.>`

| 来源 | 结果 |
|------|------|
| 脚本 verdict（禁止手改宽松） | `stop_ship / static_pass / execution_unverified` |
| 目标程序执行 | `未执行 / 可信隔离运行器已执行` |
| 门禁旁路测试（可信隔离） | `全部拦截 / 有放行（Critical）/ 未验证` |
| 默认不真发 | `已验证 / 未验证 / 默认真发（Critical）` |

| Severity | Count (script + model) |
|----------|------:|
| Critical | 0 |
| Should fix | 0 |
| Watchlist / info | 0 |

## 承诺清单（脚本）

| 文档命令 | 出处 | 脚本存在 | 子命令静态证据 | 行为验证 |
|----------|------|----------|--------------|-------|
| `scripts/x.py foo` | SKILL.md:12 | yes/no | yes/no/– | 可信隔离通过 / 未验证 |

## 外发入口（脚本 + 模型判默认值）

| 文件 | 能力 | dry-run guard | 默认不真发？（模型） |
|------|------|---------------|----------------------|
| `scripts/sender.py` | smtp | yes/no | yes / no / 未验证 |

## 门禁旁路测试（可信隔离运行器）

| 门禁 | fixture | 期望 | 实测 | 结果 |
|------|---------|------|------|------|
| blacklist | blocked@fixture.test | 拦截且不记为已发 | … | pass / FAIL |

## 必须先解决（Critical / 停发项）

### C1. `<short title>` · source: `script|model`

- **问题:** …
- **证据:** …
- **建议改法:** …

## 建议尽快改进（Should fix）

### S1. `<short title>` · source: `script|model`

- **问题:** … / **建议改法:** …

## Watchlist（放行后观察项）

- …

## 下一步

- 判决为**停发**：先修必须解决项，逐条附带证据复测。
- 判决为**未完成安全验证**：取得可信隔离运行证据；不要用临时目录代替。
- 判决为**静态通过**：仍需完成默认关闭和门禁行为验证，才能申请真发放行。
- 说 **「按意见改」** —— 代改 Critical / Should fix（外发默认关不动摇）。
