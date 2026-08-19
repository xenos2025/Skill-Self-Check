# Changelog

本文件记录 Skill Self-Check 的用户可见变更。版本号遵循
[Semantic Versioning](https://semver.org/spec/v2.0.0.html)，记录格式参考
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)。

版本来源以 [`plugin.json`](plugin.json) 为准。发布新版本时，应同时更新
`plugin.json`、本文件和 README 的版本标识。

## [Unreleased]

### Added

- `role_contract_audit.py` 新增 `RCA.4`：声明为单上下文的 Skill 若在 `SKILL.md` 中给出
  无条件的委派指令（子智能体、并行工作者、分派），报告为拓扑泄漏；仅出现在禁止性
  章节或代码块中的委派词不计入。
- `ship_safety.py` 新增 `EXT.6` 与 `gate_bypass_switches`：从目标代码中静态识别关闸
  开关（如 `--disable-claim-gate`），要求逐个确认默认关闭且关闸产物不可交付。
- `ship_safety.py` 报告新增 `command_inventory`，公开 `documented`、
  `skipped_placeholder` 和 `coverage`；stderr 摘要同步输出 `coverage=`。

### Fixed

- `ship_safety.py` 此前会把带占位路径（如 `<skill目录>/scripts/render.mjs`）的文档命令
  静默丢弃，得出 `commands=0` 的乐观 `static_pass`。现在这类命令若指向目标真实拥有的
  脚本，报告为 `DOC.2`（should fix）并给出 `文件:行号`；仅作示意的模板占位
  （如 `scripts/<sender>.py`）不再误报。
- `hard_gates.py` 的包体拓扑计数不再统计点目录（`.git`、`.github`、`.vscode`），
  以仓库根为自身包体的 Skill 不再因版本控制元数据被判为非标准布局。

## [0.4.1] - 2026-08-19

### Fixed

- 角色与 Prompt 增强现在先固定全局目标、共享上下文、端到端负责人和集成验收，再判断
  工作单元与角色边界，避免局部合规或 QA 目标覆盖整体用户目的。
- 新增集成耦合判断：高耦合任务默认保持一个端到端角色；`single_context` 明确禁止被
  实现成子智能体、并行工作者或多个任务。
- 电商示例从两个隔离角色调整为一个电商创意生产负责人，Claim Gate 只限制受控宣称，
  不再切断完整素材、商品语义或视觉上下文。

### Added

- 新增独立 `role_prompt_behavior_check.py` 与专用测试模块，验证同一素材前后证据中的
  全局目的、业务结果、共享上下文、端到端所有权、权限边界、集成质量和隐式委派。
- 新增 `RPB.0`–`RPB.3` 证据问题，并输出独立的 `improved`、`unchanged`、`mixed`、
  `regressed` 或 `not_assessed`；该结论不改变 `gate_verdict`。

## [0.4.0] - 2026-08-19

### Added

- 单上下文角色契约新增 schema 1.1，独立声明 `runtime_mode`、`role_mode`、
  `entry_role` 与 `roles`，支持一个模型调用中的单角色或顺序功能角色，并继续兼容 1.0。
- `role_contract_audit.py` 新增角色 ID、数量、入口、连通性、唯一交接和无环检查，
  以 `RCA.3` 报告角色拓扑问题；报告新增角色模式、数量和顺序摘要。
- 角色与 Prompt 增强路由新增工作单元清单、可解释拆分规则、角色合同合成和十段式
  paste-ready Prompt；缺少权限或调用证据时保持 `needs_confirmation`。
- 功能角色库扩展为九类领域中立原型，并新增“电商运营与合规文案 + Claim Gate +
  UI/平面视觉设计”的单上下文顺序角色示例。
- 完整审计 manifest 升级到 schema 1.4，记录 `runtime_mode`、`role_mode` 和
  `role_count`，同时保持角色结果独立于核心 `gate_verdict`。

### Changed

- 常规 `skill-self-check` 审计现在默认执行结构门禁、workflow Prompt 适用性和角色契约
  三项静态检查；明确要求“快速/只看门禁”时才只运行 `hard_gates.py`。
- 点名角色、Prompt、增强或优化，以及询问“是否审查”时，会在同一轮执行对应只读
  路由和模型建议审阅，不再只报告 `not_run`；各状态仍不改变核心 `gate_verdict`。
- Prompt 优化顺序调整为先判断角色与工作边界，再做上下文精简、结构优化和指令去重。

## [0.3.0] - 2026-08-19

### Added

- workflow 节点 Prompt 清单新增 schema 1.1 `role_contract`，确定性检查每个节点的
  角色、目的、职责、禁区、决策权限和交接，并保持 schema 1.0 向后兼容。
- 新增条件式 `role_contract_audit.py`：真实独立模型调用使用节点角色；单一 Agent
  上下文使用 Skill 级角色契约；未声明调用形态时保持 `not_assessed`。
- 完整只读审计入口新增 `workflow-prompt.json` 与 `role-contract.json`，并把两项
  条件状态写入审计 manifest；核心 `gate_verdict` 仍保持独立。
- 三个正式 Skill 新增机器可读角色契约；`skill-ship-safety` 移除把同一上下文审阅
  Pass 误声明为两个模型调用节点的 manifest，改为带理由的 Prompt N/A。
- 新增小型功能角色原型库，明确角色必须改变决策、证据处理、输出、权限或交接，
  泛化“专家”职业不构成优化。
- 新增按需加载的角色 Prompt 模型审阅：检查角色必要性、跨节点职责冲突、权限边界、
  上下游交接和最小化改写；结果标记为 `source: model_review`，不改变脚本结论。
- 新增 workflow 节点 Prompt 静态审计的中英文 SVG 说明图，并接入 README；
  图中明确逐节点检查范围和结果不改变核心 `gate_verdict` 的边界。

### Changed

- 重写 README，明确三个正式 Skill、默认门禁、可选检查、修复复检和安全边界，
  并减少中英文重复内容和旧架构术语。
- 将历史变更从单一 `Unreleased` 区域整理为带版本号的发布段和
  `Unreleased` 待发布区。

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
