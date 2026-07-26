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

## Four-skill product flow

```text
口头约定 / 零散流程
        │
        ▼
agent-work-readiness ──► B0–B6 业务准备度
        │                         │
        ▼                         │
     写成 Skill                   │
        │                         │
        ├─► skill-self-check ─────┤
        └─► skill-ship-safety ────┤
                                  ▼
                       skill-growth-scorecard
                         JSON + 离线 HTML
```

- `agent-work-readiness` 独立评估业务目标、步骤、职责、标准、委派边界和运行复盘。
- `skill-self-check` 保留确定性的结构与契约检查。
- `skill-ship-safety` 保留静态承诺差距和外部动作预检。
- `skill-growth-scorecard` 只组合已有 JSON 事实，不替代上游检查，也不虚构缺失分数。

普通用户不需要手工串联四个脚本。安装完整产品包后，
`skill-self-check/scripts/run_full_audit.py` 是统一入口：它调用结构检查和安全
预检，按需读取业务工作包与可信行为证据，并从同一事实集生成个人能力与项目
两份成绩单。脚本会比较审计前后的目标指纹，并拒绝把真实报告写进目标或其源码
仓库。

## skill-self-check runtime split

```text
User / Agent
    │
    ├─1─► hard_gates.py ──► JSON scores + Critical findings  (deterministic)
    │
    └─2─► Checklist Pass 2–4 ──► qualitative Should/Nice + rewrites (model)
              │
              ├─► REPORT-BUSINESS-TEMPLATE.md  (plain language)
              └─► REPORT-TEMPLATE.md           (technical evidence)
```

| Concern | Owner |
| --- | --- |
| Frontmatter, name, description shape, line count, axis headings, checkbox Verification | Script |
| Completion-criterion quality, leading words, prose pruning | Model |
| Numeric scores in the report | Script only |
| Business/technical wording | Model/templates; facts and IDs must match |

## skill-ship-safety execution boundary

`ship_safety.py` performs static inspection only. It inventories documented
Python commands, checks for implementation evidence, and scans shipped source
files for external-action capabilities. It does not execute target code.

Behavior tests require a platform or CI runner that independently enforces
network denial, writable-file boundaries, environment allowlisting, and
process/time limits. A copied directory plus `DRY_RUN=1` is not treated as a
security sandbox. When such a runner is unavailable, the result stays
`execution_unverified`.

`skill-growth-scorecard` 的 Lv3–Lv5 必须接收额外行为证据。静态报告最高只能
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
