# Architecture

## Product vs experiment

```text
                    ┌──────────────────────────────────────┐
                    │           Public repository          │
                    ├──────────────────┬───────────────────┤
                    │ skills/          │ exp/              │
                    │ (stable product) │ (experiments)     │
                    │  3 stable skills │  pm-workflow-…    │
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
              ┌──────────────┴──────────────┐
              │明确深审                      │明确安全预检
              ▼                             ▼
       model_review                 skill-ship-safety
       advisory only                static JSON

口头/重复工作流程 ──► agent-work-readiness ──► B0–B6 JSON
```

- `skill-self-check` 是默认核心入口，独立评估包结构、明确必备检查和脚本
  Critical，并输出聚焦整改。
- `agent-work-readiness` 独立评估业务目标、步骤、职责、标准、委派边界和运行复盘。
- `skill-ship-safety` 保留静态承诺差距和外部动作预检。

普通用户默认只需要 `skill-self-check/scripts/hard_gates.py`。核心 Skill
不得要求另外两个 Skill 已安装。只有用户明确要求完整静态检查时，
`skill-self-check/scripts/run_full_audit.py` 才调用结构门禁和安全预检；提供工作包
时再调用 readiness。它只保存各检查器的源 JSON 和审计清单，会比较审计前后的
目标指纹，并拒绝把真实报告写进目标或其源码仓库。

三个检查器各自是独立 Module。CLI JSON 是它们的 Interface，也是组合入口的
Seam；`run_full_audit.py` 只编排，不复制任何评分或门禁 Implementation。

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
    └─explicit full static audit─► hard-gates + ship-safety JSON
```

| Concern | Owner |
| --- | --- |
| `gate_verdict`, required checks, Criticals, exit code | `hard_gates.py` only |
| Numeric scores | Script-produced, informational only |
| Completion-criterion quality, leading words, prose pruning | Optional model review; non-blocking |
| Full static report set | `run_full_audit.py`, preserving each checker result |
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

For maintainers auditing this repository itself, run the regression suite and
each checker directly. The full runner preserves source results without
averaging or translating them into another scoring system.

## Inspiration

Full credit table: root [README](../README.md)（致谢与参考）and [NOTICE](../NOTICE).

Checklist axes fuse:

- [Matt Pocock — writing-great-skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-great-skills)
- [Addy Osmani — agent-skills](https://github.com/addyosmani/agent-skills)
- Cursor `create-skill` hard rules

Packaging uses a standard open-source skill-pack layout (`skills/` product,
`exp/` experiments, MIT + SECURITY/CONTRIBUTING). PDCA / SMART / 5W2H are
mapped as checkable passes, not slogans.
