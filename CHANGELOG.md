# Changelog

本文件记录 Skill Self-Check 的用户可见变更。版本号遵循
[Semantic Versioning](https://semver.org/spec/v2.0.0.html)，记录格式参考
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)。

版本来源以 [`plugin.json`](plugin.json) 为准。发布新版本时，应同时更新
`plugin.json`、本文件和 README 的版本标识。

## [Unreleased]

### Changed

- 重写 README，明确三个正式 Skill、默认门禁、可选检查、修复复检和安全边界，
  并减少中英文重复内容和旧架构术语。
- 将历史变更从单一 `Unreleased` 区域整理为 `0.1.0`、`0.2.0` 和
  `Unreleased` 三个版本段。

## [0.2.0] - 2026-08-18

### Added

- 新增明确的确定性门禁契约：`gate_verdict`、结构化 `gate_reasons` 和必备检查
  成为阻断结论的唯一来源；数字分数改为信息性诊断。
- 新增 `hard_gates.py --out-json`，以 UTF-8 JSON 保存修改前基线，并拒绝把真实
  报告写入被审计 Skill。
- 新增 `verify_fix.py`，对比修改前后门禁、已解决问题、新增问题和仍存在的问题；
  硬回归会返回非零退出码。
- 新增可选 `--repo-root`，支持经明确批准的同仓库共享资源，同时继续阻止绝对路径
  和越出批准根目录的引用。
- 新增 `run_full_audit.py`，把结构门禁、静态外部操作预检和可选工作准备度检查输出
  到仓库外目录。
- 新增 workflow 节点 Prompt 静态审计：检查每个模型调用节点的 Prompt 文件、
  输入输出契约、占位符、决策门、验收和停止条件、非可信资料隔离、结构标签与图连接。
  该结果独立于核心 `gate_verdict`。
- 新增效率检查：识别无停止条件的重试、无限优化指令和过长说明书。
- 新增 Windows、中文 Skill、非 UTF-8 文件、安装器、修复复检、外部操作安全和
  workflow Prompt 的回归测试。

### Changed

- 正式发布包精简为三个 Skill：`skill-self-check`、`skill-ship-safety` 和
  `agent-work-readiness`。
- `skill-self-check` 改为门禁优先：默认先完成快速确定性审计，完整静态检查、
  PDCA/SMART 模型深审和其他模块只在明确请求时加载。
- 压缩并拆分 `skill-self-check` 的 Prompt 契约，将深度审计、完整静态检查、
  Prompt 优化和修复复检放入按需读取的 reference。
- 默认报告聚焦 `gate_verdict`、全部 Critical、最多三项 Should fix 和可直接采用的
  修改建议。
- `skill-ship-safety` 继续保持静态检查边界：内置脚本不执行被审计 Skill，也不会把
  缺少真实运行证据误报为已经通过行为验证。
- 安装器、插件清单、贡献指南和架构文档同步为三个正式 Skill。

### Removed

- 从正式发布包、默认安装器和完整静态检查中移除实验性的离线
  `skill-growth-scorecard`。相关成长画像不再是核心门禁或安装依赖。

## [0.1.0] - 2026-07-25

### Added

- 首次发布 `skill-self-check`：检查 `SKILL.md` frontmatter、名称、使用时机、
  不适用场景、检查步骤、验收标准和配套资源。
- 提供 JSON 审计元数据、技术报告模板、普通用户报告和问题修复模板。
- 提供中英文硬门禁、示例夹具、基础回归测试和 GitHub Actions。
- 提供 PowerShell 与 Bash 安装器、MIT 许可证、贡献指南、安全政策和项目文档。
- 提供使用流程、修改复检、PDCA、SMART、5W2H 和信息性分数图示。
- 建立 `exp/` 实验区，用于尚未进入正式安装包的流程规划方法。
