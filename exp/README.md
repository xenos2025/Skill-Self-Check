# Experiments (`exp/`)

**Not installed by default.** This tree is the open hook for productizing the
next layer of this pack: **PM / workflow planning** for foreign trade, factory,
and ecommerce teams.

## Why this folder exists

Today’s stable product is `skills/skill-self-check` (audit a skill after you
write it).

Tomorrow’s product bet: help operators and PMs **plan the workflow first**,
then propose which skills to build — with the same ship-floor discipline.

```text
Client interview (5W2H — ask until clear)
    -> Workflow map (roles, systems, evidence)
        -> Skill gap proposal (build / reuse / buy)
            -> Draft SKILL.md
                -> skill-self-check (promote only if ship floor met)
```

Interview method: [pm-workflow-planning/INTERVIEW.md](pm-workflow-planning/INTERVIEW.md).

## Rules

1. Drafts and demos only — no customer PII, tokens, or production CSVs.
2. Prefer `*.example.md` / `*.example.csv` for samples.
3. Promotion path: pilot notes → self-check pass → move into `skills/` →
   CHANGELOG + version bump in `plugin.json`.
4. Agents working on this repo: see root [AGENTS.md](../AGENTS.md).

## Current experiments

| Folder | Status | Intent |
| --- | --- | --- |
| [pm-workflow-planning/](pm-workflow-planning/) | working experiment | one-question interview → evidence-backed workflow → skill proposal; includes customer background investigation example |

## Scope of `exp/`

Horizontal methodology: propose and harden skills for 外贸 / 工厂 / 电商.
It may later *recommend* vertical industry packs; it does not replace them.
