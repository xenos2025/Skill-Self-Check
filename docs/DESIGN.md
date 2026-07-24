# Design bets

## Bet 1 — Scores must be boring

Hard gates and numeric scores are **scripted**. Models explain and rewrite; they
do not invent `basic_usable` numbers. Predictability beats clever judgment for
the floor that decides “can we use this yet?”

## Bet 2 — Contract clarity is a product surface

A skill that never names **check axes** (color / composition / copy, or role /
handoff / verification) will drift. `contract_clarity` exists so beginners feel
that gap before real-world observation.

## Bet 3 — Product vs experiment split

Open-source users should trust `skills/`. Speculative PM work for 外贸 / 工厂 /
电商 workflow planning lands in `exp/` first:

1. Interview & workflow map (draft)
2. Skill gap proposal (draft)
3. Pilot with self-check ship floor
4. Promote into `skills/` + CHANGELOG

This mirrors mature packs that separate **product logic** from **fillable /
experimental state**, without requiring a per-client workspace yet.

## Bet 4 — PDCA + SMART are checkable, not posters

Every audited skill should close a **PDCA** loop (Plan → Do → Check → Act) and
state a **SMART** outcome contract. In this pack:

- Plan ≈ When / When NOT / check axes
- Do ≈ steps with Done when
- Check ≈ Verification + evidence
- Act ≈ Red Flags / Rationalizations / retry
- SMART **T** means **run-bound exit** (finish the invocation), not a fake
  quarterly date unless the domain is truly calendar ops

Self-check Pass 5 and `references/pdca-smart.md` enforce this in reports.
`exp/pm-workflow-planning` proposals should use the same language before
promotion. Client intake uses **5W2H** ([INTERVIEW.md](../exp/pm-workflow-planning/INTERVIEW.md)):
ask one question at a time until What/Why/Who/When/Where/How/How much are clear.

## Non-goals (v0.1)

- Pulling rules from GitHub at runtime
- Replacing `create-skill` for greenfield authoring
- Shopify write gates (out of scope; see specialized ops packs)
