# Skill Self-Check · AI 工作说明书自检包

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](docs/INSTALLATION.md)

**[中文（老板 / 非技术优先看这里）](#中文版本)** · [English](#english)

---

# 中文版本

把「AI 怎么做事」写成说明书（Skill）之后，用本包做一次**验货式自检**：
电脑先跑明确的硬门槛，再给修改意见。数字分数会作为信息写进 JSON，但不参与
门禁。
规则在本地，**不会联网去 GitHub 拉规则**。

适合：写说明书的人、要拍板「能不能推广」的老板、外贸 / 工厂 / 电商里要先问清流程的人。

## 给朋友 / AI 初学者：最快怎么用

你**不用先会装仓库、跑命令**。按自己平时的办法先写一份 Skill，再让帮你写 Skill 的 AI 做自检即可。

1. **先按自己的流程写一份 Skill**（Cursor / Claude / 其他平台都行），得到一个含 `SKILL.md` 的文件夹。
2. **把本仓库地址发给那个 AI**（复制下面整段即可）：

```text
请用这个开源包帮我自检刚写好的 Skill：
https://github.com/xenos2025/Skill-Self-Check

做法：
1. 克隆或打开上面的仓库，按它的说明安装 skill-self-check（或直接读 skills/skill-self-check/SKILL.md）
2. 对我的 Skill 目录跑自检（目录里要有 SKILL.md）
3. 先出报告，不要直接改我的文件；等我说「按意见改」再改
```

3. **先看 `gate_verdict` 和必须解决的问题**：默认报告会列出全部
   Critical、最多三项 Should fix，并给可直接采用的修改建议。数字分数不决定通过。
4. **说「按意见改」之后，要再跑一轮证明修好了**：用改前保存的 `hard-gates.json` 对照改后结果（`verify_fix.py`）。不能凭记忆说“已修复”。

更细的本机安装见下面「三分钟上手」；只会点聊天、不会开终端的人，**只用上面 1–4 就够了**。

如果公司很多事情还靠口头约定，先用 **agent-work-readiness** 把一个具体工作
练到“目标、步骤、负责人、交接、标准和权限”说清楚，再写 Skill。

**两条路径（别混）：** 默认快速审计只看确定性门禁并给整改；模型的
PDCA / SMART 属于显式深审。

## 可视化上手（先看图）

重画图：`python branding/generate_diagrams.py`

### 1. 怎么用（整条链路）

![怎么用](assets/diagrams/zh/01-how-to-use.svg)

### 2. 改完再检（闭环）

写好 → 跑检查 → 看报告；**不过就改，改完再跑**。核心门禁通过表示
Skill 包结构和必备检查达标且没有脚本 Critical；外部发送、真实数据和运行行为
仍需可选的安全 / 行为证据。

![改完再检](assets/diagrams/zh/06-fix-loop.svg)

### 3. 门禁与三盏灯怎么读（给老板）

![三盏灯](assets/diagrams/zh/05-three-lights.svg)

| 灯 | 白话 |
| --- | --- |
| `gate_verdict` | 权威门禁：包有效、必备检查通过、没有脚本 Critical |
| `basic_usable` | 信息性结构分，不决定门禁 |
| `contract_clarity` | 信息性契约分：何时用 / 不用、检查轴、验收 |
| `support_kit` | 信息性配套分：资料 / 案例 / 记忆 / 脚本 |
| 门禁通过 | 核心静态审计通过；不等于真实行为或外部动作已验证 |
| 蓝灯某项 N/A | 声明不适用即可，不扣分 |

### 4. PDCA：做事要闭环

![PDCA](assets/diagrams/zh/02-pdca.svg)

计划 → 执行 → 检查 → 改进。缺「检查」或「改进」，就容易变成瞎忙。

### 5. SMART：目标要说人话

![SMART](assets/diagrams/zh/03-smart.svg)

别说「做好运营」；要说清交付物、怎么验收、这次跑完算结束。

### 6. 5W2H：跟客户谈话问清楚

![5W2H](assets/diagrams/zh/04-5w2h.svg)

做什么 / 为什么 / 谁 / 何时 / 在哪 / 怎么做 / 多少——**一次只问一句**，口号式回答要追问。  
访谈稿：[exp/pm-workflow-planning/INTERVIEW.md](exp/pm-workflow-planning/INTERVIEW.md)

流程梳理实验区会先判断是否需要业务数据模块；不明确时问用户一次并给出建议。
需要重复分级、取证或复盘时，可按情况启用 `L1–L3` 业务价值、`S1–S3`
来源等级、`V0–V3` 验证强度和运行记录。合理的 `N/A` 不影响通用自检。详见
[operational-data-contract.md](exp/pm-workflow-planning/references/operational-data-contract.md)。

## 三分钟上手

```powershell
git clone https://github.com/xenos2025/Skill-Self-Check.git
cd Skill-Self-Check
./install.ps1 -Skills skill-self-check
py -3 skills/skill-self-check/scripts/hard_gates.py C:\你的Skill目录 `
  --out-json "$HOME\Documents\skill-audits\本次\hard-gates.json" --pretty
```

上面的默认命令只运行独立、快速的确定性门禁。也可以在 Cursor 里点名
**skill-self-check** 并给出待检说明书路径。默认只出整改报告；说「按意见改」
后才编辑文件。想一次安装三个正式 Skill 时，改用不带 `-Skills` 的
`./install.ps1`。

需要一条命令同时运行结构门禁和静态安全预检时，使用完整静态检查入口；提供
`--work-package` 还会加入工作成熟度检查：

```powershell
py -3 skills/skill-self-check/scripts/run_full_audit.py C:\你的Skill目录 `
  --out-dir "$HOME\Documents\skill-audits\完整报告" --pretty
```

多步骤 workflow 如果每一步都会单独调用模型，可复制
`skills/skill-self-check/examples/workflow-prompts.example.json` 到目标 Skill
的 `references/workflow-prompts.json`，声明每个节点后运行：

```powershell
py -3 skills/skill-self-check/scripts/workflow_prompt_audit.py C:\你的Skill目录 --pretty
```

这个可选检查验证节点契约、Prompt 文件、占位符、结构标签、资料隔离和节点连接；
结果不改变核心 `gate_verdict`，也不代表真实模型行为已经通过。
没有独立模型调用节点时，可在 `SKILL.md` 写明
`Workflow prompt audit: N/A — <理由>`；结果为 `not_applicable`，不会冒充通过。

真实报告必须写在目标和源码仓库之外。`skill-self-check` 本身不依赖另外两个
Skill；核心审计可以单独使用。

准备让 AI 修改时，先用 `--out-json` 把修改前报告保存为仓库外的
`hard-gates.json`；改完用它对照：

```powershell
py -3 skills/skill-self-check/scripts/verify_fix.py C:\你的Skill目录 `
  --baseline "$HOME\Documents\skill-audits\本次\hard-gates.json" --pretty
```

## 仓库里有什么（白话）

| 文件夹 | 白话 |
| --- | --- |
| `skills/` | 正式产品（安装器会拷贝） |
| `exp/` | 试验区：客户访谈 → 流程 → 再写说明书（默认不安装） |
| `assets/diagrams/` | 上图；`zh/` 为中文 |
| `tests/` | 回归测试（中文技能、非 UTF-8 文件都覆盖） |
| `docs/` | 安装与设计说明 |

更多：[docs/INSTALLATION.md](docs/INSTALLATION.md) · [docs/PLATFORM-COMPATIBILITY.md](docs/PLATFORM-COMPATIBILITY.md) · [docs/AUDIENCE.md](docs/AUDIENCE.md) · [exp/README.md](exp/README.md)

正式产品共三块：业务准备度、Skill 结构自检、安全预检。它们都只
读取本地文件；真实客户报告默认不应提交到这个开源仓库。自检还含效率护栏
（无限重试 / 超长说明书）和改完复核（`verify_fix.py`），避免“改了就算修好”。

### 平台适配进度（不是认证）

| 平台 | 状态 | 说明 |
| --- | --- | --- |
| Cursor | 在用 | 日常编写与快速门禁入口 |
| Codex | 可测 | 下一组跨平台对照的第二平台 |
| Claude Code | 未测 | 后续适配候选 |
| WorkBuddy | 未测 | 中国市场候选，安装/调用方式待探 |
| Coze | 未测 | 中国市场候选，安装/调用方式待探 |

跨平台“已验证”需要 Cursor + Codex（或任意两个不同平台）使用**同一契约文件**和
**同一脱敏夹具**，并各自留下 `verified` 记录。详见
[docs/PLATFORM-COMPATIBILITY.md](docs/PLATFORM-COMPATIBILITY.md)。

## 致谢与参考（写清楚我们站在谁的肩膀上）

本仓库是**融合与工程化**，不是从零发明整套方法论。详细法律致谢见 [NOTICE](NOTICE)。

| 参考项目 | 链接 | 我们用了什么 | 我们自己的部分 |
| --- | --- | --- | --- |
| Matt Pocock · writing-great-skills | [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-great-skills) | 可预测性、完成标准、修剪与失败模式等词汇 → 白话检查项 | 自检流程与报告模板 |
| Addy Osmani · agent-skills | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Skill 解剖、Verification、反合理化、质量门槛 | 脚本打分 + 新手报告 |
| Cursor · create-skill | Cursor 内置 skill 规范 | frontmatter、第三人称 WHAT+WHEN、行数与披露规则 | 与上两者的融合清单 |
| 管理常识 | PDCA · SMART · 5W2H | 作为可检查的 Pass / 访谈法 | 映射到 Skill 字段的具体表 |

## 贡献 / 安全 / 许可

[CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) · [SUPPORT.md](SUPPORT.md) · [MIT](LICENSE) · [NOTICE](NOTICE)

---

# English

A beginner-friendly **Agent Skill self-check pack**: a local Python script
evaluates explicit deterministic gates and your coding agent suggests focused
fixes. Informational scores remain in the JSON; PDCA × SMART review is an
opt-in route. Nothing is fetched from GitHub at runtime.

Diagrams use a simple Swiss blue/white style. Regenerate with `python branding/generate_diagrams.py`.

## For friends / AI beginners (no terminal required)

1. **Write a Skill your usual way** (any platform). You need a folder that contains `SKILL.md`.
2. **Paste this to the same AI that wrote the Skill:**

```text
Please self-check my Skill with this open-source pack:
https://github.com/xenos2025/Skill-Self-Check

Steps:
1. Clone or open that repo; install skill-self-check (or read skills/skill-self-check/SKILL.md)
2. Run the self-check on my Skill directory (must contain SKILL.md)
3. Report only — do not edit my files until I say “apply fixes”
```

3. **Read `gate_verdict` first:** the default response lists every Critical,
   at most three Should-fix items, and actionable rewrites. Numeric scores do
   not decide the gate.
4. **After “apply fixes”, prove the delta:** re-check against the pre-edit `hard-gates.json` with `verify_fix.py`. Do not claim “fixed” from memory.

**Two routes:** fast deterministic audit is the default; qualitative
PDCA/SMART review is explicit deep audit.

## Visual guide

### How it works

![How to use](assets/diagrams/01-how-to-use.svg)

### Fix & retry loop

Write → run gates → report; if it fails, fix and run again. A passing core gate
means the package and named required checks passed with no deterministic
Criticals. It does not prove runtime behavior or external actions safe.

![Fix loop](assets/diagrams/06-fix-loop.svg)

### Three lights (boss-friendly scores)

![Three lights](assets/diagrams/05-three-lights.svg)

### PDCA

![PDCA](assets/diagrams/02-pdca.svg)

### SMART

![SMART](assets/diagrams/03-smart.svg)

### 5W2H interviews

![5W2H](assets/diagrams/04-5w2h.svg)

The workflow-planning experiment first judges whether business-data modules are
useful and asks once with a recommendation when unclear. It can selectively
enable `L1–L3` value, `S1–S3` source fitness, `V0–V3` verification, and run
records. A justified N/A does not lower the general self-check score. See
[operational-data-contract.md](exp/pm-workflow-planning/references/operational-data-contract.md).

## Quick start

```bash
git clone https://github.com/xenos2025/Skill-Self-Check.git
cd Skill-Self-Check
./install.sh --skills skill-self-check
# Windows: ./install.ps1 -Skills skill-self-check
python skills/skill-self-check/scripts/hard_gates.py \
  /path/to/your-skill \
  --out-json "$HOME/Documents/skill-audits/current/hard-gates.json" --pretty
```

The default command runs the standalone deterministic gate. In Cursor, invoke
**skill-self-check** and pass a skill path. It reports all Criticals and up to
three Should-fix items; say “apply fixes” to authorize edits. Run `./install.sh`
without `--skills` only when you want all three shipped Skills. To prove fixes:

```bash
python skills/skill-self-check/scripts/verify_fix.py /path/to/your-skill \
  --baseline "$HOME/Documents/skill-audits/current/hard-gates.json" --pretty
```

Capture that baseline before authorizing edits.

The full runner remains available when you explicitly want structure and
static safety checks in one JSON-only report set. Add `--work-package` to
include work-readiness:

```bash
python skills/skill-self-check/scripts/run_full_audit.py \
  /path/to/your-skill \
  --out-dir "$HOME/Documents/skill-audits/full-report" --pretty
```

For a multi-step workflow with a separate model call at each step, copy
`skills/skill-self-check/examples/workflow-prompts.example.json` to the target
Skill as `references/workflow-prompts.json`, declare every node, then run:

```bash
python skills/skill-self-check/scripts/workflow_prompt_audit.py \
  /path/to/your-skill --pretty
```

This optional audit checks node contracts, prompt files, placeholders,
XML-style tags, source isolation, and graph links. It does not change the core
`gate_verdict` or prove runtime model behavior.
When no separate model-call nodes exist, declare
`Workflow prompt audit: N/A — <reason>` in `SKILL.md`; the result is
`not_applicable`, never `pass`.

The core self-check remains usable when the other two Skills are absent.

## Layout

```text
skills/skill-self-check/    # static structure/contract audit
  references/plain-language-response.md # default plain-language response contract
  scripts/workflow_prompt_audit.py # optional model-call node contract audit
skills/skill-ship-safety/   # static external-action preflight
skills/agent-work-readiness/# oral workflow → B0–B6 readiness
exp/                        # PM interview → workflow experiments (not installed)
tests/                      # regression suite mirrored by CI
assets/diagrams/            # EN SVGs · zh/ for Chinese
branding/generate_diagrams.py
docs/
```

Chinese and English skills score identically: `用于` / `适用` / `当用户` count as WHEN triggers, and `何时不用` / `检查轴` / `验收` are recognised headings. A non-UTF-8 `SKILL.md` is scored and flagged (`1.11`) rather than crashing the run.

### Platform matrix (not a certification)

| Platform | Status | Notes |
| --- | --- | --- |
| Cursor | In active use | Primary authoring + fast deterministic gate |
| Codex | Available for testing | Chosen second platform for the next comparable pair |
| Claude Code | Not tested yet | Later adapter candidate |
| WorkBuddy | Not tested yet | China-market candidate |
| Coze | Not tested yet | China-market candidate |

Cross-platform credit needs two distinct platforms sharing the same contract and
sanitized fixture identifiers. See
[PLATFORM COMPATIBILITY](docs/PLATFORM-COMPATIBILITY.md).

## Docs

[INSTALLATION](docs/INSTALLATION.md) · [PLATFORM COMPATIBILITY](docs/PLATFORM-COMPATIBILITY.md) · [ARCHITECTURE](docs/ARCHITECTURE.md) · [AUDIENCE](docs/AUDIENCE.md) · [DESIGN](docs/DESIGN.md) · [FEATURES](docs/FEATURES.md) · [TROUBLESHOOTING](docs/TROUBLESHOOTING.md) · [TODO](TODO.md)

## Credits / references

This pack **fuses and engineers** prior work; it does not claim to invent the whole methodology. Legal acknowledgements: [NOTICE](NOTICE).

| Project | What we reused | What is ours |
| --- | --- | --- |
| [mattpocock/skills — writing-great-skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-great-skills) | Predictability, completion criteria, pruning / failure modes → plain checklist | Self-check flow + report |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Skill anatomy, Verification, rationalizations, quality bar | Scripted scores + beginner report |
| Cursor `create-skill` | Frontmatter, third-person WHAT+WHEN, length / disclosure | Fused checklist |
| PDCA · SMART · 5W2H | Classic management heuristics as checkable passes / interview method | Mapping onto Skill fields |

## Contributing / security / license

[CONTRIBUTING.md](CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) · [SECURITY.md](SECURITY.md) · [SUPPORT.md](SUPPORT.md) · [PRIVACY.md](PRIVACY.md) · [MIT](LICENSE) · [NOTICE](NOTICE)
