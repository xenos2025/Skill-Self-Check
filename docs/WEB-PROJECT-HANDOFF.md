# Skill Self-Check Web 项目交接

## 1. 交接快照

- 日期：2026-07-29
- 时区：Asia/Shanghai
- 检测引擎仓库：`D:\Codex\projects\skill-skill`
- 建议的新项目目录：`D:\Codex\projects\skill-self-check-web`
- 检测引擎基线提交：`5913c9f727b1c0730305cfeffe45f451655286b9`
- 当前插件版本：`0.1.0`
- 依据：当前仓库代码、测试、README、架构文档，以及本机当前 Codex Sites
  的构建、D1、R2、运行时变量和部署能力

新任务开始时应重新确认检测引擎提交和 Sites 能力；不要默认本快照之后没有变化。

## 2. 项目目标

新建一个独立 Web 产品，允许用户上传一个待检 Skill，运行现有确定性检测，
生成普通用户报告和技术报告，并在后台保留检测记录。AI 是可选增强层，不得
修改脚本分数、问题编号或修复前后差值。

第一版的核心体验：

1. 上传单个 `SKILL.md` 或 Skill ZIP。
2. 创建检测任务并显示状态。
3. 调用现有 Python 检测引擎。
4. 展示脚本分数、三盏灯、问题和证据。
5. 可选调用一个文本模型 API，生成定性分析和改写建议。
6. 保存任务、结果和报告。
7. 查看历史记录并重新打开 HTML 报告。
8. 通过浏览器打印功能保存 PDF。

## 3. 已确定的架构决策

### 3.1 独立项目

Web 产品放在当前仓库的同级目录，并建立独立 Git 仓库：

```text
D:\Codex\projects\
├─ skill-skill\              # 现有检测引擎
└─ skill-self-check-web\     # 新 Web 产品
```

不要把 Web 项目放进 `skill-skill\web`，也不要在现有仓库中建立嵌套 Git
仓库。

### 3.2 复用检测引擎，不重写评分规则

当前仓库继续负责：

- `hard_gates.py` 的硬门槛、分数和 Critical findings；
- `verify_fix.py` 的修复前后差值；
- `ship_safety.py` 的静态外部动作预检；
- `readiness_gates.py` 的业务准备度判断；
- 成绩单所需的确定性 JSON 事实；
- 回归测试和测试夹具。

新项目负责：

- Web 页面和管理后台；
- 上传、任务状态和报告历史；
- 数据库和文件存储；
- Python 检测服务接入；
- 可选 AI 分析；
- 部署、访问控制和运行时配置。

脚本结果是权威事实。AI 只能解释、补充定性发现和提供改写建议。

### 3.3 Sites 的职责

Codex Sites 用于：

- Web 前端和服务端路由；
- D1 持久化结构化数据；
- R2 保存上传文件和生成的报告；
- 保存 AI API Key 等服务器端运行时变量；
- 部署和访问控制。

Sites 的服务端目标是 Cloudflare Worker 兼容的 JavaScript/TypeScript。
现有 Python 脚本不能原封不动直接在 Sites 运行。

### 3.4 Python 检测服务

第一版保留现有 Python 代码，增加一个薄接口层。接口层只能负责：

- 接收受限的上传包或规范化文件集合；
- 在隔离的临时目录中调用现有 CLI；
- 收集退出码、标准 JSON 和错误分类；
- 返回统一、带版本的 JSON；
- 清理临时文件。

不要在接口层复制评分规则。生产环境使用哪个 Python 托管平台尚未确定；本地
开发可以先启动独立的 Python HTTP 服务。

### 3.5 AI 层

一个文本模型 API、一个服务器端 Key 即可支撑第一版。建议使用统一适配器：

```ts
interface AIReviewer {
  review(input: {
    skillText: string;
    scriptResult: AuditScriptResult;
  }): Promise<AIReviewResult>;
}
```

需要的运行时配置至少包括：

```text
AI_PROVIDER
AI_BASE_URL
AI_MODEL
AI_API_KEY
```

`AI_API_KEY` 必须作为服务器端 secret 保存，不能出现在浏览器代码、数据库明文、
日志、报告或 Git 历史中。

AI 默认应为用户主动启用。AI 失败、超时或未配置时，脚本检测和报告仍必须完成。

## 4. 目标架构

```text
浏览器
  │
  ▼
Sites Web 应用
  ├─ D1：任务、结构化结果、状态、用量、文件元数据
  ├─ R2：上传包、HTML 报告、导出文件
  ├─ Python Audit API：现有确定性检测脚本
  └─ AI API：可选定性分析和改写建议
```

建议的数据流：

1. Sites 校验上传类型和基础限制。
2. 上传原文件进入 R2，并在 D1 创建任务。
3. Sites 将受控输入交给 Python Audit API。
4. Python 服务运行确定性检测并返回带版本 JSON。
5. Sites 保存脚本结果。
6. 用户启用 AI 时，Sites 将必要文本和脚本 JSON 发送给 AI。
7. Sites 分开保存 `script` 与 `model` 结果。
8. 报告生成器合并两类结果，但不允许模型覆盖脚本事实。

## 5. 最小数据模型

### `audit_jobs`

- `id`
- `status`: `queued | running | completed | failed`
- `source_name`
- `source_sha256`
- `engine_commit`
- `engine_version`
- `ai_enabled`
- `ai_status`
- `created_at`
- `started_at`
- `completed_at`
- `error_code`
- `error_message`

### `audit_results`

- `id`
- `job_id`
- `schema_version`
- `script_result_json`
- `ai_result_json`
- `business_summary_json`
- `technical_summary_json`
- `created_at`

### `artifacts`

- `id`
- `job_id`
- `kind`: `source | business_html | technical_html | export`
- `r2_key`
- `sha256`
- `content_type`
- `size_bytes`
- `created_at`
- `expires_at`

第一版没有账号系统时，可使用不可猜测的任务 ID 访问结果。正式多用户版再增加
`users`、所有权字段、团队和权限表。

## 6. 接口边界

### Web 产品接口

```text
POST /api/audits
GET  /api/audits/:id
GET  /api/audits/:id/report/business
GET  /api/audits/:id/report/technical
POST /api/audits/:id/ai-review
DELETE /api/audits/:id
```

### Python Audit API

```text
POST /v1/audits
GET  /v1/health
```

`POST /v1/audits` 的输出必须包含：

- `schema_version`
- `engine_commit`
- `engine_version`
- `input_sha256`
- 每个脚本的退出状态；
- 原始脚本 JSON；
- 明确的错误分类；
- 开始和完成时间。

Web 项目应保存原始脚本 JSON，不要只保存前端加工后的摘要。

## 7. 报告规则

- 普通用户报告回答“能不能进入受控试用、为什么、下一步做什么”。
- 技术报告保留分数、问题编号、证据、脚本版本和来源。
- 每条发现必须标记 `source: script` 或 `source: model`。
- AI 不得生成或更改 `basic_usable`、数值分数、Critical 数量和修复差值。
- `ship_safety.py` 只是静态预检，报告不得声称真实行为已经安全。
- HTML 是第一版正式报告格式；PDF 使用浏览器打印，服务器端 PDF 后置。
- 报告必须显示检测引擎版本和输入文件哈希，以便复现。

## 8. 上传和安全边界

所有上传都按不可信输入处理：

- 只读取，不执行用户上传的脚本、命令或二进制文件；
- 防止 ZIP 路径穿越；
- 拒绝指向包外的软链接；
- 配置压缩包大小、解压后大小、文件数和单文件大小上限；
- 使用随机临时目录，任务结束后清理；
- 不记录文件原文、Authorization header、API Key 或 Cookie；
- 默认设置上传和报告保留期限；
- 删除任务时同步删除 D1 记录和 R2 文件；
- 对发送给 AI 的内容进行最小化，只发送完成定性审查所需文本；
- 用户未启用 AI 时，不向任何模型供应商发送 Skill 内容；
- 不把真实客户报告、上传包或敏感样例提交到任一源码仓库。

错误必须分类为代码缺陷、环境、权限、依赖、输入无效、外部服务不可用或工具限制，
不能统一显示成“检测失败”。

## 9. 第一版不做

- 不把全部 Python 评分规则迁移到 TypeScript；
- 不执行用户 Skill 的真实业务动作；
- 不承诺行为安全认证；
- 不自动修改用户上传的 Skill；
- 不做支付、套餐和复杂团队权限；
- 不做公开报告分享链接；
- 不做向量数据库或知识库；
- 不做多 Agent 编排；
- 不在第一版生成服务器端 PDF；
- 不因 AI 不可用而阻断确定性检测。

## 10. 实施顺序

### 阶段 0：新仓库骨架

1. 在 `D:\Codex\projects\skill-self-check-web` 建立独立项目和 Git 仓库。
2. 使用当前 Sites 官方初始化流程创建站点；只初始化一次。
3. 添加新项目自己的 `AGENTS.md`、README、`.gitignore` 和环境变量示例。
4. 不修改 `D:\Codex\projects\skill-skill`。

### 阶段 1：无 AI 纵向切片

1. 完成上传页面。
2. 建立 Python Audit API 薄封装。
3. 跑通一个现有测试夹具。
4. 返回原始脚本 JSON。
5. 展示检测状态和最小 HTML 报告。
6. 证明相同输入在 CLI 和 Web 路径得到相同分数与 Critical findings。

### 阶段 2：持久化

1. 增加 D1 schema 和迁移。
2. 增加 R2 上传与报告保存。
3. 增加历史记录、报告重开和删除。
4. 验证刷新页面和重新部署后记录仍存在。

### 阶段 3：AI 增强

1. 增加统一 AI 适配器。
2. 使用结构化 JSON 输出。
3. 明确隔离 `script` 与 `model` 结果。
4. 增加超时、失败和未配置降级。
5. 记录调用状态和用量，不记录密钥或完整敏感请求。

### 阶段 4：上线准备

1. 明确访问级别和是否需要账号。
2. 确定 Python 服务生产托管方式。
3. 确定保留期限和上传限制。
4. 运行安全、构建和浏览器流程验证。
5. 使用 Sites 保存运行时 secret 并部署。

## 11. 验收标准

- 不配置 AI Key 时，完整的脚本检测和报告仍能运行。
- AI 调用失败时，脚本结果不会丢失或被标记为失败。
- Web 路径与基线 CLI 对同一夹具给出完全相同的确定性分数、问题编号和 Critical
  findings。
- 上传内容从未作为代码执行。
- 报告能区分脚本事实与模型建议。
- D1 保存结构化记录，R2 保存文件，不用浏览器存储充当权威数据源。
- 删除任务后，相应记录和文件按产品策略清理。
- 前端构建产物和浏览器请求中不存在 AI API Key。
- Git 历史、日志、测试夹具和报告中不存在凭据或真实客户敏感数据。
- 每个结果能追溯到输入哈希、检测引擎提交和结果 schema 版本。
- 生产部署前完成至少一次无 AI 流程和一次 AI 降级流程验证。

## 12. 尚待用户决定

以下事项不阻塞新仓库骨架和无 AI 纵向切片，但上线前必须确认：

1. Python Audit API 的生产托管位置。
2. AI 供应商、模型和预算上限。
3. 网站是私有、邀请制还是公开。
4. 是否第一版就需要账号和权限。
5. 上传包大小、文件数和解压后大小上限。
6. 上传文件、报告和操作日志的保留期限。
7. 是否允许用户下载原始脚本 JSON。

## 13. 新目录任务启动文本

在新目录打开一个新的 Codex 任务后，可直接发送：

```text
请在 D:\Codex\projects\skill-self-check-web 建立独立的 Skill Self-Check Web
项目。先完整读取：
D:\Codex\projects\skill-skill\docs\WEB-PROJECT-HANDOFF.md

把 D:\Codex\projects\skill-skill 视为只读的权威检测引擎，不要修改或复制
评分规则。使用 Codex Sites 构建 Web 产品层，第一步只完成“无 AI 纵向切片”：
上传一个 Skill、调用现有 Python 检测路径、返回权威 JSON、展示最小报告，并用
现有夹具证明 CLI 与 Web 的确定性结果一致。

开始前检查新目录是否为空、当前检测引擎提交、适用的 AGENTS.md 和当前 Sites
能力。需要初始化时只初始化一次。不要配置或写入真实 API Key；先使用环境变量
占位。完成本地验证后再报告下一阶段需要的生产托管决策。
```

## 14. 权威参考

- `D:\Codex\projects\skill-skill\AGENTS.md`
- `D:\Codex\projects\skill-skill\README.md`
- `D:\Codex\projects\skill-skill\docs\ARCHITECTURE.md`
- `D:\Codex\projects\skill-skill\docs\DESIGN.md`
- `D:\Codex\projects\skill-skill\CONTRIBUTING.md`
- `D:\Codex\projects\skill-skill\skills\skill-self-check\SKILL.md`
- `D:\Codex\projects\skill-skill\skills\skill-self-check\scripts\hard_gates.py`
- `D:\Codex\projects\skill-skill\skills\skill-self-check\scripts\verify_fix.py`
- `D:\Codex\projects\skill-skill\skills\skill-ship-safety\scripts\ship_safety.py`
- `D:\Codex\projects\skill-skill\tests`
