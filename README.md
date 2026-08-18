# Skill Self-Check · Agent Skill 静态审计包

[![Version: 0.2.0](https://img.shields.io/badge/version-0.2.0-2563eb.svg)](CHANGELOG.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](docs/INSTALLATION.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[中文](#中文)** · **[English](#english)**

当前版本：**0.2.0**。版本来源以 [`plugin.json`](plugin.json) 为准，变更记录见
[`CHANGELOG.md`](CHANGELOG.md)。

---

# 中文

Skill Self-Check 用确定性 Python 脚本检查 Agent Skill 的结构、使用契约和静态安全线索，
再由 AI 根据脚本证据给出修改建议。内置脚本只读取本地文件，**不会执行被审计 Skill 的代码**。

`gate_verdict` 是核心门禁结论；数字分数只提供诊断信息，不决定是否通过。运行行为、真实外部操作和
平台兼容性需要单独验证。

## 三个正式 Skill

| Skill | 用途 | 何时使用 |
| --- | --- | --- |
| `skill-self-check` | 检查 Skill 包结构、触发条件、排除场景、验收标准和配套资源 | 默认入口；写完或修改 Skill 后使用 |
| `skill-ship-safety` | 静态检查邮件、消息、API 写入等外部操作风险 | Skill 会触达真实系统或数据时使用 |
| `agent-work-readiness` | 把口头流程整理成目标、步骤、角色、交接、指标和权限 | 工作流程还没有说清楚时先使用 |

三个 Skill 可以一起安装，也可以只安装 `skill-self-check`。核心门禁不依赖另外两个 Skill。

## 最快用法

已有一个包含 `SKILL.md` 的文件夹时，把下面内容发给正在协助你的 AI：

```text
请使用这个开源包检查我的 Skill：
https://github.com/xenos2025/Skill-Self-Check

要求：
1. 安装 skill-self-check，或直接读取仓库中的 skills/skill-self-check/SKILL.md
2. 对我提供的 Skill 目录运行默认快速审计
3. 先报告 gate_verdict、全部 Critical 和最多三项 Should fix
4. 不要修改文件；等我说“按意见改”后再修改，并在修改前保存基线
5. 修改后用 verify_fix.py 对照基线复检，不要凭记忆声称已经修复
```

默认流程：

1. 运行确定性门禁。
2. 先报告，不直接修改目标。
3. 用户明确说“按意见改”后，保存基线并修改。
4. 重新运行检查，报告修改前后的实际差异。

## 如何看结果

| 字段 | 含义 |
| --- | --- |
| `gate_verdict` | 权威门禁：`pass`、`fail` 或 `invalid_skill_package` |
| `gate_reasons` | 门禁未通过的确定性原因 |
| Critical | 必须先解决的问题；默认全部展示 |
| Should fix | 建议改进的问题；默认最多展示三项，其余保留在 JSON |
| `basic_usable` | 信息性结构分 |
| `contract_clarity` | 信息性契约分 |
| `support_kit` | 信息性配套资源分 |

门禁通过表示静态结构和必备契约检查通过，并且没有确定性 Critical；不表示目标 Skill 的实际行为、
外部操作或业务效果已经验证。

## 安装与默认审计

PowerShell：

```powershell
git clone https://github.com/xenos2025/Skill-Self-Check.git
cd Skill-Self-Check
./install.ps1 -Skills skill-self-check

py -3 skills/skill-self-check/scripts/hard_gates.py C:\你的Skill目录 `
  --out-json "$HOME\Documents\skill-audits\本次\hard-gates.json" --pretty
```

Bash：

```bash
git clone https://github.com/xenos2025/Skill-Self-Check.git
cd Skill-Self-Check
./install.sh --skills skill-self-check

python skills/skill-self-check/scripts/hard_gates.py /path/to/your-skill \
  --out-json "$HOME/Documents/skill-audits/current/hard-gates.json" --pretty
```

不传 `-Skills` / `--skills` 时，安装器会安装三个正式 Skill。

如果目标 Skill 有意引用同一源码仓库中的共享资源，增加
`--repo-root <源码仓库路径>`。默认仍只允许目标 Skill 内部资源；绝对路径和越出批准根目录的路径会被拦截。

## 修改后复检

必须在修改前保存 `hard-gates.json`。修改后运行：

```powershell
py -3 skills/skill-self-check/scripts/verify_fix.py C:\你的Skill目录 `
  --baseline "$HOME\Documents\skill-audits\本次\hard-gates.json" --pretty
```

`verify_fix.py` 会报告门禁变化、已解决问题、新增问题和仍未解决的问题。分数变化不代替门禁结论。

## 可选检查

### 完整静态检查

需要把结构门禁和外部操作安全预检汇总到同一输出目录时使用：

```powershell
py -3 skills/skill-self-check/scripts/run_full_audit.py C:\你的Skill目录 `
  --out-dir "$HOME\Documents\skill-audits\完整报告" --pretty
```

增加 `--work-package <文件路径>` 后，还会检查工作准备度。真实报告必须写在目标 Skill 和源码仓库之外。

### Workflow 节点 Prompt 检查

如果一个 workflow 的多个环节会分别调用模型，可把
[`workflow-prompts.example.json`](skills/skill-self-check/examples/workflow-prompts.example.json)
复制到目标 Skill 的 `references/workflow-prompts.json`，声明每个模型调用节点后运行：

```powershell
py -3 skills/skill-self-check/scripts/workflow_prompt_audit.py C:\你的Skill目录 --pretty
```

该检查覆盖节点输入输出契约、Prompt 文件、占位符、结构标签、非可信资料隔离、决策门和节点连接。
结果独立于核心 `gate_verdict`，也不代表真实模型输出已经通过。没有独立模型调用节点时，在
`SKILL.md` 中声明 `Workflow prompt audit: N/A — <理由>`。

## 处理流程

![使用流程](assets/diagrams/zh/01-how-to-use.svg)

![修改与复检](assets/diagrams/zh/06-fix-loop.svg)

其他图示：[`PDCA`](assets/diagrams/zh/02-pdca.svg) ·
[`SMART`](assets/diagrams/zh/03-smart.svg) ·
[`5W2H`](assets/diagrams/zh/04-5w2h.svg) ·
[`门禁与信息性分数`](assets/diagrams/zh/05-three-lights.svg)

重新生成图示：`python branding/generate_diagrams.py`

## 仓库结构

```text
skills/skill-self-check/     # 结构与契约门禁、修复复检、workflow Prompt 检查
skills/skill-ship-safety/    # 外部操作静态安全预检
skills/agent-work-readiness/ # 口头流程到 B0–B6 工作包
exp/                         # 实验性流程规划内容；默认不安装
tests/                       # 标准库回归测试
assets/diagrams/             # 英文图示；zh/ 为中文图示
docs/                        # 安装、架构、兼容性和设计说明
```

## 平台状态

| 平台 | 状态 | 说明 |
| --- | --- | --- |
| Cursor | 使用中 | 当前主要编写和审计入口 |
| Codex | 可测试 | 计划用于跨平台对照 |
| Claude Code | 未验证 | 后续适配候选 |
| WorkBuddy | 未验证 | 后续适配候选 |
| Coze | 未验证 | 后续适配候选 |

这张表不是兼容性认证。跨平台“已验证”需要至少两个不同平台使用同一契约和同一脱敏夹具完成测试，
并保留验证记录。详见 [`docs/PLATFORM-COMPATIBILITY.md`](docs/PLATFORM-COMPATIBILITY.md)。

## 文档与许可

[`安装`](docs/INSTALLATION.md) · [`架构`](docs/ARCHITECTURE.md) ·
[`功能`](docs/FEATURES.md) · [`平台兼容`](docs/PLATFORM-COMPATIBILITY.md) ·
[`故障排查`](docs/TROUBLESHOOTING.md) · [`贡献指南`](CONTRIBUTING.md) ·
[`安全策略`](SECURITY.md) · [`MIT License`](LICENSE) · [`NOTICE`](NOTICE)

本项目参考了 Matt Pocock 的 `writing-great-skills`、Addy Osmani 的 `agent-skills`、
Cursor Skill 规范以及 PDCA、SMART、5W2H 等通用方法。具体许可和署名见 [`NOTICE`](NOTICE)。

---

# English

Skill Self-Check uses deterministic Python scripts to audit Agent Skill package structure,
usage contracts, and static safety signals. An AI can then propose focused fixes from the
script evidence. Built-in scripts read local files only and **never execute target Skill code**.

Current version: **0.2.0**. [`plugin.json`](plugin.json) is the version source of truth;
see [`CHANGELOG.md`](CHANGELOG.md) for release notes.

`gate_verdict` is authoritative. Numeric scores are diagnostic only. Runtime behavior,
real external actions, and platform compatibility require separate evidence.

## Shipped Skills

| Skill | Purpose |
| --- | --- |
| `skill-self-check` | Package, trigger, exclusion, acceptance, and resource checks |
| `skill-ship-safety` | Static preflight for email, messaging, API writes, and other external actions |
| `agent-work-readiness` | Turns an oral process into a checkable B0–B6 work package |

The core self-check works independently; the other two Skills are optional routes.

## Quick start

```bash
git clone https://github.com/xenos2025/Skill-Self-Check.git
cd Skill-Self-Check
./install.sh --skills skill-self-check

python skills/skill-self-check/scripts/hard_gates.py /path/to/your-skill \
  --out-json "$HOME/Documents/skill-audits/current/hard-gates.json" --pretty
```

Windows PowerShell:

```powershell
./install.ps1 -Skills skill-self-check
py -3 skills/skill-self-check/scripts/hard_gates.py C:\path\to\skill `
  --out-json "$HOME\Documents\skill-audits\current\hard-gates.json" --pretty
```

Run the installers without `--skills` / `-Skills` to install all three shipped Skills.
Use `--repo-root /path/to/source-repository` only for intentional sibling or shared-resource
references in a multi-Skill source pack.

## Result contract

| Field | Meaning |
| --- | --- |
| `gate_verdict` | Authoritative `pass`, `fail`, or `invalid_skill_package` result |
| `gate_reasons` | Deterministic reasons for a failed gate |
| Critical | Blocking findings; the default response shows all of them |
| Should fix | Non-blocking improvements; the default response shows at most three |
| Scores | Informational diagnostics; they never override the gate |

A passing gate does not prove runtime behavior, external-action safety, or business outcomes.

## Verify fixes

Capture the baseline before editing, then run:

```bash
python skills/skill-self-check/scripts/verify_fix.py /path/to/your-skill \
  --baseline "$HOME/Documents/skill-audits/current/hard-gates.json" --pretty
```

The result reports gate transitions and resolved, introduced, and remaining findings.

## Optional audits

Full static audit:

```bash
python skills/skill-self-check/scripts/run_full_audit.py /path/to/your-skill \
  --out-dir "$HOME/Documents/skill-audits/full-report" --pretty
```

Add `--work-package <path>` to include work-readiness. Keep real audit output outside both
the target Skill and its source repository.

For workflows with separate model-call nodes, copy
[`workflow-prompts.example.json`](skills/skill-self-check/examples/workflow-prompts.example.json)
to `references/workflow-prompts.json` in the target Skill, declare every node, then run:

```bash
python skills/skill-self-check/scripts/workflow_prompt_audit.py \
  /path/to/your-skill --pretty
```

This optional audit checks node contracts, prompt files, placeholders, XML-style tags,
untrusted-source isolation, decision gates, and graph links. It does not change the core
`gate_verdict` or prove runtime model behavior. If there are no separate model-call nodes,
declare `Workflow prompt audit: N/A — <reason>` in `SKILL.md`.

## Repository layout

```text
skills/skill-self-check/     # core gate, fix verification, workflow prompt audit
skills/skill-ship-safety/    # static external-action preflight
skills/agent-work-readiness/ # oral process to B0–B6 work package
exp/                         # experiments; not installed by default
tests/                       # stdlib regression suite
assets/diagrams/             # English diagrams; zh/ contains Chinese versions
docs/                        # installation, architecture, compatibility, and design
```

## Platform status

Cursor is in active use. Codex is available for comparison testing. Claude Code,
WorkBuddy, and Coze are not yet verified. This is not a certification; see
[`docs/PLATFORM-COMPATIBILITY.md`](docs/PLATFORM-COMPATIBILITY.md) for the evidence contract.

## Documentation and license

[`Installation`](docs/INSTALLATION.md) · [`Architecture`](docs/ARCHITECTURE.md) ·
[`Features`](docs/FEATURES.md) · [`Compatibility`](docs/PLATFORM-COMPATIBILITY.md) ·
[`Troubleshooting`](docs/TROUBLESHOOTING.md) · [`Contributing`](CONTRIBUTING.md) ·
[`Security`](SECURITY.md) · [`MIT License`](LICENSE) · [`NOTICE`](NOTICE)
