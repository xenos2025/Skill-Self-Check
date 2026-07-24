# Architecture

## Product vs experiment

```text
                    ┌──────────────────────────────────────┐
                    │           Public repository          │
                    ├──────────────────┬───────────────────┤
                    │ skills/          │ exp/              │
                    │ (stable product) │ (experiments)     │
                    │  skill-self-check│  pm-workflow-…    │
                    │  [future skills] │  industry drafts  │
                    └────────┬─────────┴─────────▲─────────┘
                             │ install            │ promote only
                             ▼                    │ after pilot
                    ~/.cursor/skills/        skills/
```

- **`skills/`** — what installers copy; must stay reviewable and ship-floor friendly.
- **`exp/`** — sandbox for productizing **PM / workflow planning** (外贸 / 工厂 / 电商).
  Not on the default install path. See [exp/README.md](../exp/README.md).

## skill-self-check runtime split

```text
User / Agent
    │
    ├─1─► hard_gates.py ──► JSON scores + Critical findings  (deterministic)
    │
    └─2─► Checklist Pass 2–4 ──► qualitative Should/Nice + rewrites (model)
              │
              ▼
         REPORT-TEMPLATE.md
```

| Concern | Owner |
| --- | --- |
| Frontmatter, name, description shape, line count, axis headings, checkbox Verification | Script |
| Completion-criterion quality, leading words, prose pruning | Model |
| Numeric scores in the report | Script only |

## Inspiration

Full credit table: root [README](../README.md)（致谢与参考）and [NOTICE](../NOTICE).

Checklist axes fuse:

- [Matt Pocock — writing-great-skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-great-skills)
- [Addy Osmani — agent-skills](https://github.com/addyosmani/agent-skills)
- Cursor `create-skill` hard rules

Packaging uses a standard open-source skill-pack layout (`skills/` product,
`exp/` experiments, MIT + SECURITY/CONTRIBUTING). PDCA / SMART / 5W2H are
mapped as checkable passes, not slogans.
