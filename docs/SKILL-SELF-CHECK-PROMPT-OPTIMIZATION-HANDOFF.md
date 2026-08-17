# Handoff — `skill-self-check` Prompt 优化

## 1. 交接范围

- 目标仓库：`D:\Codex\projects\skill-skill`
- 目标 Skill：`skills/skill-self-check`
- 核验时间：2026-08-18 02:23（Asia/Shanghai）
- 本阶段目标：缩短默认 Prompt 路径、明确脚本与模型的权威边界，同时保持确定性门禁行为不变。
- 当前状态：压缩和 Prompt 优化审查路线均已完成，并通过静态门禁、安全扫描和相关回归测试；尚未提交 Git。

## 2. 本阶段修改的文件

| 文件 | 状态 | 作用 |
| --- | --- | --- |
| `skills/skill-self-check/SKILL.md` | 已修改 | 精简默认路径；补充正向触发、排除边界、权威契约和输出契约 |
| `skills/skill-self-check/references/deep-qualitative-audit.md` | 新增 | 仅在请求深度定性审计时加载 |
| `skills/skill-self-check/references/full-static-audit.md` | 新增 | 仅在请求完整静态审计时加载 |
| `skills/skill-self-check/references/fix-verification.md` | 新增 | 仅在已授权修复后进行基线对比时加载 |
| `skills/skill-self-check/references/prompt-optimization.md` | 新增 | 仅在请求 Prompt 优化或上下文效率审查时加载 |
| `tests/test_prompt_optimization_contract.py` | 新增 | 锁定 Prompt 优化触发、路由、证据边界和默认路径预算 |
| `CHANGELOG.md` | 已修改 | 在 `[Unreleased] / Changed` 记录此次优化和量化结果 |

本阶段没有主动修改以下当前同样处于 dirty 状态的文件：

- `skills/skill-self-check/CHECKLIST.md`
- `skills/skill-self-check/REPORT-TEMPLATE.md`
- `skills/skill-self-check/references/plain-language-response.md`
- `skills/skill-self-check/scripts/hard_gates.py`
- `skills/skill-self-check/scripts/run_full_audit.py`
- `tests/` 下的现有改动

这些属于仓库中原有的其他工作，不要在后续处理中重置、覆盖或顺手整理。

## 3. 设计变化

### 默认快速路径

`SKILL.md` 继续保留日常审计所需的最短闭环：

1. 检查目标与包健康；
2. 运行脚本门禁；
3. 按脚本结果报告 gate、finding 和修复建议；
4. 仅在用户明确授权时修改目标；
5. 修改后使用保存的基线运行 `verify_fix.py`。

### 权威边界

- `hard_gates.py` 独占 `package_health`、`gate_verdict`、脚本 finding、severity 和退出码。
- `verify_fix.py` 独占基线前后修复验证结论。
- 模型只负责可选的定性分析，不得改写脚本结论。
- 数字评分仅供参考，不参与 gate 判定。

### 按需加载

- 深度定性审计 → `references/deep-qualitative-audit.md`
- 完整静态审计 → `references/full-static-audit.md`
- 修复后基线验证 → `references/fix-verification.md`
- Prompt 优化 / 上下文效率审查 → `references/prompt-optimization.md`

这样可以避免每次调用都读取低频流程，同时保留完整能力。

## 4. 优化前后数据

| 指标 | 优化前 | 压缩阶段 | 当前 | 当前净变化 |
| --- | ---: | ---: | ---: | ---: |
| `SKILL.md` 行数 | 308 | 196 | 200 | -108 |
| 静态估算输入 tokens | 4,044 | 2,306 | 2,413 | -1,631（约 40%） |
| `basic_usable` | 5/5 | 5/5 | 5/5 | 不变 |
| `contract_clarity` | 5/5 | 5/5 | 5/5 | 不变 |
| `support_kit` | 3/3 | 3/3 | 3/3 | 不变 |
| `gate_verdict` | pass | pass | pass | 不变 |
| 新增 finding | 0 | 0 | 0 | 无回归 |

两次 `verify_fix.py` 的 verdict 均为 `unchanged`。这里不表示优化无效，而是门禁和评分原本已经满分；本次收益体现在默认输入缩短、职责边界更清楚，以及新增的 Prompt 优化按需审查能力。新增路线相对压缩阶段增加 107 estimated tokens，但相对原始版本仍减少约 40%。

## 5. 已完成验证

### 硬门禁

```powershell
python skills/skill-self-check/scripts/hard_gates.py skills/skill-self-check --pretty
```

结果：

- `gate_verdict: pass`
- Critical：0
- Should fix：0
- Package：`valid_skill_package`
- 静态估算输入：2,413 tokens

### 基线对比

优化前基线暂存于：

```text
C:\Users\wangx\AppData\Local\Temp\skill-self-check-optimization-baseline-20260818.json
```

验证命令：

```powershell
python skills/skill-self-check/scripts/verify_fix.py skills/skill-self-check `
  --baseline "C:\Users\wangx\AppData\Local\Temp\skill-self-check-optimization-baseline-20260818.json" `
  --pretty
```

结果：

- `verdict: unchanged`
- `regression_detected: false`
- gate：`pass → pass`
- introduced findings：0
- estimated tokens saved：1,738

后续 Prompt 优化路线基线暂存于：

```text
C:\Users\wangx\AppData\Local\Temp\skill-self-check-prompt-optimization-baseline-20260818-0200.json
```

相对该基线的结果：`unchanged`，无回归、无新增 finding，默认路径增加 107 estimated tokens。

该基线位于系统临时目录，后续会话不能假定永久存在。若文件消失，需要基于可信的优化前版本重新建立基线，不能伪造对比结果。

### 静态安全扫描

```powershell
python skills/skill-ship-safety/scripts/ship_safety.py skills/skill-self-check --pretty
```

结果：`static_pass`，Critical 0，Should fix 0。两条 Info 仅提示带 dry-run guard 的脚本仍需在受信隔离环境验证真实执行行为。

### 回归测试

```powershell
python -m unittest tests.test_hard_gates tests.test_full_audit_runner -v
```

结果：原相关测试 32/32 通过；加入 Prompt 优化契约测试后共 35/35 通过。

说明：测试需要在系统临时目录创建和清理文件夹。受限沙箱内曾出现 `PermissionError: [WinError 5]`；获得临时目录权限后完整通过，属于环境权限问题，不是代码缺陷。

### 格式检查

```powershell
git diff --check -- CHANGELOG.md skills/skill-self-check
```

结果：通过，无输出。

## 6. 当前仓库风险

仓库当前存在大量其他修改与删除，包括文档、脚本、测试、工作流、图像和 `skill-growth-scorecard` 删除项。后续处理必须：

1. 不运行 `git reset --hard`、`git checkout -- .` 或类似恢复命令；
2. 不使用 `git add -A` 或整仓提交；
3. 提交前只暂存本交接第 2 节明确属于本阶段的文件或 hunk；`CHANGELOG.md` 必须按 hunk 复核，不能整文件盲目暂存；
4. 若需修改同目录其他 dirty 文件，先确认其现有差异和归属；
5. 不删除或覆盖未跟踪的 `docs/WEB-PROJECT-HANDOFF.md`。

## 7. 尚未完成

- 未创建 Git commit、tag 或 release；
- 未把本次优化同步到其他仓库或打包副本；
- 未运行真实模型行为评测或多平台安装验证；
- 未处理仓库中其他既有改动；
- 未决定三个新 reference 文件是否需要单独的文档索引或发布说明。

## 8. 推荐后续顺序

1. 重新读取仓库 `AGENTS.md`，再确认当前 `git status --short`。
2. 阅读本交接文件和第 2 节的 7 个目标文件。
3. 重跑硬门禁、相关 35 项回归测试和 `git diff --check`。
4. 若要继续优化，优先做行为测试，不要为了继续压缩而牺牲触发边界或验证步骤。
5. 若要提交，只暂存确认属于本阶段的文件，并在提交前复核 staged diff。

## 9. 新项目可直接使用的续接提示

```text
请读取 D:\Codex\projects\skill-skill\AGENTS.md 和
D:\Codex\projects\skill-skill\docs\SKILL-SELF-CHECK-PROMPT-OPTIMIZATION-HANDOFF.md，
继续处理 skill-self-check 的 Prompt 优化后续工作。

仓库已有大量其他未提交改动。只处理 handoff 中列出的范围，不重置、恢复、批量暂存或覆盖其他变更。
开始前先重新核验 git status、hard_gates、相关 35 项测试和 diff check，并明确区分已验证事实、当前假设和待确认事项。
```
