# Skill Self-Check · AI 工作说明书自检包

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](docs/INSTALLATION.md)

**[中文（老板 / 非技术优先看这里）](#中文版本)** · [English](#english)

---

# 中文版本

把「AI 怎么做事」写成说明书（Skill）之后，用本包做一次**验货式自检**：  
电脑先打分，再给修改意见。规则在本地，**不会联网去 GitHub 拉规则**。

适合：写说明书的人、要拍板「能不能推广」的老板、外贸 / 工厂 / 电商里要先问清流程的人。

## 可视化上手（先看图）

重画图：`python branding/generate_diagrams.py`

### 1. 怎么用（整条链路）

![怎么用](assets/diagrams/zh/01-how-to-use.svg)

### 2. 两盏灯怎么读（给老板）

![两盏灯](assets/diagrams/zh/05-two-lights.svg)

| 灯 | 白话 |
| --- | --- |
| 绿灯 `basic_usable` | 结构过关，可以先真用 |
| 黄灯 `contract_clarity` | 查什么、何时用说清楚了吗 |
| 两盏都亮 | 可以放心推广 |
| 只有绿灯 | 能用，但容易各做各的 |
| 绿灯不亮 | 先改，别急着推广 |

### 3. PDCA：做事要闭环

![PDCA](assets/diagrams/zh/02-pdca.svg)

计划 → 执行 → 检查 → 改进。缺「检查」或「改进」，就容易变成瞎忙。

### 4. SMART：目标要说人话

![SMART](assets/diagrams/zh/03-smart.svg)

别说「做好运营」；要说清交付物、怎么验收、这次跑完算结束。

### 5. 5W2H：跟客户谈话问清楚

![5W2H](assets/diagrams/zh/04-5w2h.svg)

做什么 / 为什么 / 谁 / 何时 / 在哪 / 怎么做 / 多少——**一次只问一句**，口号式回答要追问。  
访谈稿：[exp/pm-workflow-planning/INTERVIEW.md](exp/pm-workflow-planning/INTERVIEW.md)

## 三分钟上手

```powershell
git clone https://github.com/xenos2025/Skill-Self-Check.git
cd Skill-Self-Check
./install.ps1
py -3 skills/skill-self-check/scripts/hard_gates.py skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty
```

在 Cursor 里点名 **skill-self-check**，给出待检说明书路径。默认只出报告；说「按意见改」再改文件。

## 仓库里有什么（白话）

| 文件夹 | 白话 |
| --- | --- |
| `skills/` | 正式产品（安装器会拷贝） |
| `exp/` | 试验区：客户访谈 → 流程 → 再写说明书（默认不安装） |
| `assets/diagrams/` | 上图；`zh/` 为中文 |
| `tests/` | 回归测试（中文技能、非 UTF-8 文件都覆盖） |
| `docs/` | 安装与设计说明 |

更多：[docs/INSTALLATION.md](docs/INSTALLATION.md) · [docs/AUDIENCE.md](docs/AUDIENCE.md) · [exp/README.md](exp/README.md)

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

A beginner-friendly **Agent Skill self-check pack**: a local Python script scores hard gates; your coding agent suggests fixes — including a **PDCA × SMART** matrix. Nothing is fetched from GitHub at runtime.

Diagrams use a simple Swiss blue/white style. Regenerate with `python branding/generate_diagrams.py`.

## Visual guide

### How it works

![How to use](assets/diagrams/01-how-to-use.svg)

### Two lights (boss-friendly scores)

![Two lights](assets/diagrams/05-two-lights.svg)

### PDCA

![PDCA](assets/diagrams/02-pdca.svg)

### SMART

![SMART](assets/diagrams/03-smart.svg)

### 5W2H interviews

![5W2H](assets/diagrams/04-5w2h.svg)

## Quick start

```bash
git clone https://github.com/xenos2025/Skill-Self-Check.git
cd Skill-Self-Check
./install.sh   # or ./install.ps1 on Windows
python skills/skill-self-check/scripts/hard_gates.py \
  skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty
```

In Cursor, invoke **skill-self-check** and pass a skill path. Report-only by default; say “apply fixes” to edit.

## Layout

```text
skills/skill-self-check/   # installable product
exp/                       # PM interview → workflow experiments (not installed)
tests/                     # regression suite mirrored by CI
assets/diagrams/           # EN SVGs · zh/ for Chinese
branding/generate_diagrams.py
docs/
```

Chinese and English skills score identically: `用于` / `适用` / `当用户` count as WHEN triggers, and `何时不用` / `检查轴` / `验收` are recognised headings. A non-UTF-8 `SKILL.md` is scored and flagged (`1.11`) rather than crashing the run.

## Docs

[INSTALLATION](docs/INSTALLATION.md) · [ARCHITECTURE](docs/ARCHITECTURE.md) · [AUDIENCE](docs/AUDIENCE.md) · [DESIGN](docs/DESIGN.md) · [FEATURES](docs/FEATURES.md) · [TROUBLESHOOTING](docs/TROUBLESHOOTING.md) · [TODO](TODO.md)

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
