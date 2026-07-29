# Architecture

## Product vs experiment

```text
                    ┌──────────────────────────────────────┐
                    │           Public repository          │
                    ├──────────────────┬───────────────────┤
                    │ skills/          │ exp/              │
                    │ (stable product) │ (experiments)     │
                    │  4 stable skills │  pm-workflow-…    │
                    │  see flow below  │  industry drafts  │
                    └────────┬─────────┴─────────▲─────────┘
                             │ install            │ promote only
                             ▼                    │ after pilot
                    ~/.cursor/skills/        skills/
```

- **`skills/`** — what installers copy; must stay reviewable and ship-floor friendly.
- **`exp/`** — sandbox for productizing **PM / workflow planning** (外贸 / 工厂 / 电商).
  Not on the default install path. See [exp/README.md](../exp/README.md).

## Independent core with optional routes

```text
                         Skill 目录
                             │
                             ▼
                    skill-self-check
                  独立快速门禁 + 整改
                             │
              ┌──────────────┼──────────────┐
              │明确深审       │明确要成绩单   │明确安全预检
              ▼              ▼              ▼
       model_review    skill-growth-   skill-ship-
       advisory only   scorecard       safety
                      JSON + HTML

agent-work-readiness ──► 可选业务准备度 JSON ──► scorecard
```

- `skill-self-check` 是默认核心入口，独立评估包结构、明确必备检查和脚本
  Critical，并输出聚焦整改。
- `agent-work-readiness` 独立评估业务目标、步骤、职责、标准、委派边界和运行复盘。
- `skill-ship-safety` 保留静态承诺差距和外部动作预检。
- `skill-growth-scorecard` 是显式可选下游，只组合已有 JSON 事实，不重跑默认
  审计、不替代上游检查，也不虚构缺失分数。

普通用户默认只需要 `skill-self-check/scripts/hard_gates.py`。核心 Skill
不得要求另外三个 Skill 已安装。只有用户明确要求成绩单或完整报告时，
`skill-self-check/scripts/run_full_audit.py` 才作为兼容的完整入口：它调用可用
的增强检查，并从同一事实集生成个人能力与项目两份成绩单。脚本会比较审计
前后的目标指纹，并拒绝把真实报告写进目标或其源码仓库。

## skill-self-check runtime split

```text
User / Agent
    │
    ├─default─► hard_gates.py ──► gate_verdict + ranked fixes (deterministic)
    │
    ├─apply fixes─► verify_fix.py ──► gate/finding delta
    │
    ├─explicit deep audit─► model_review priorities (advisory only)
    │
    └─explicit scorecard─► existing JSON ──► skill-growth-scorecard
```

| Concern | Owner |
| --- | --- |
| `gate_verdict`, required checks, Criticals, exit code | `hard_gates.py` only |
| Numeric scores | Script-produced, informational only |
| Completion-criterion quality, leading words, prose pruning | Optional model review; non-blocking |
| Scorecard level/type/HTML | `skill-growth-scorecard`, consuming source JSON |
| Applied-fix proof | `verify_fix.py`; score changes do not create hard regression |

## skill-ship-safety execution boundary

`ship_safety.py` performs static inspection only. It inventories documented
Python commands, checks for implementation evidence, and scans shipped source
files for external-action capabilities. It does not execute target code.

Behavior tests require a platform or CI runner that independently enforces
network denial, writable-file boundaries, environment allowlisting, and
process/time limits. A copied directory plus `DRY_RUN=1` is not treated as a
security sandbox. When such a runner is unavailable, the result stays
`execution_unverified`.

`skill-growth-scorecard` 优先读取 `hard_gates.gate_verdict`，只对旧 JSON
回退读取已弃用的 `scores.ship_floor_met`。它不得通过数字分数覆盖核心门禁。
其 Lv3–Lv5 必须接收额外行为证据。静态报告最高只能
解锁 Lv2。只读场景的 `not_applicable` 必须由范围证据和目标未变化证据支持；
跨平台等级必须有至少两个平台使用同一契约和同一夹具指纹的 `verified` 记录。

For maintainers auditing this repository itself,
`skill-growth-scorecard/scripts/suite_scorecards.py` reruns the two deterministic
checks for every direct product Skill, runs the local regression suite, and
creates separate personal and project HTML files. The runner refuses real
outputs inside the source repository by default. Static suite scores use the
weakest shipped Skill, so an average cannot hide one weak product.

## Inspiration

Full credit table: root [README](../README.md)（致谢与参考）and [NOTICE](../NOTICE).

Checklist axes fuse:

- [Matt Pocock — writing-great-skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-great-skills)
- [Addy Osmani — agent-skills](https://github.com/addyosmani/agent-skills)
- Cursor `create-skill` hard rules

Packaging uses a standard open-source skill-pack layout (`skills/` product,
`exp/` experiments, MIT + SECURITY/CONTRIBUTING). PDCA / SMART / 5W2H are
mapped as checkable passes, not slogans.
