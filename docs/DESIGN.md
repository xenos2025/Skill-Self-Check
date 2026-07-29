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
3. Pilot after the explicit self-check gate passes
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

## Bet 5 — One result, multiple audience views

Every audit produces one authoritative fact set. The core Skill exposes two
presentation depths:

- a compact plain-language response contract for the default route
- an explicit technical report with scores, finding IDs, evidence, and
  reproduction

The optional growth scorecard adds three screen lenses over the same facts: growth,
detection, and technical evidence. The wording may differ; counts, IDs, and
pass/fail conclusions may not. The growth lens is a personal capability view:
it describes the creator's demonstrated Skill-building style and stage based on
the current artifact. Project delivery verdicts remain visible in detection and
technical evidence, but do not become personal badges.

## Bet 6 — Static pass is not behavior proof

The stdlib scripts inspect files and contracts. They do not certify platform
compatibility, execute target code, or prove external actions are safe.
Behavioral approval requires a separately supplied trusted isolation runner.

## Bet 7 — A growth profile is an evidence portrait

The scorecard may use a memorable type headline, an original character, and
single-direction visual axes so a beginner can understand the result at a glance. The
type describes the creator's evidenced Skill-building pattern, never a fixed
personality or psychological trait.

Each axis converts the deterministic 0–4 evidence state to
0 / 25 / 50 / 75 / 100 percent. That percentage means **evidence coverage**,
not a probability, personality trait, evidence-gap percentage, or blended
readiness score. The UI shows one current percentage; 100% always means the
dimension's full-evidence criteria are met within the declared rules and test
scope, never that future risk is impossible. Safety conclusions remain
authoritative in the project views: a friendly personal-growth surface can move
the verdict out of the personal card, but can never hide or override
`stop_ship` in detection or technical evidence.

The personal capability card must make a concrete judgment from the evidence:
what the creator has demonstrated, the current capability stage, and up to
three growth priorities. Product explanations such as “type describes style,
level describes stage” belong in documentation, not in the assessment card.
The Python profile engine owns this deterministic interpretation; the HTML
renders it without inventing or recalculating copy.

## Bet 8 — “不适用”也必须有证据

只读 Skill 不应因为没有写回功能被误判为能力缺失，但一句 `N/A` 也不能自动
得到满分。成长评分把“适用性”和“是否通过”分开：

- 外部动作适用：验证授权、默认关闭、确认和失败阻断；
- 外部动作不适用：静态安全必须通过、不得检出外部动作，并提供范围证据；
- 写回适用：验证写入前后一致性和恢复；
- 写回不适用：提供范围证据，并由可信 Harness 证明
  `target_unchanged=true`。

因此“安全与控制 100%”表示当前范围内所有**适用控制已验证**、所有
**不适用控制已证明范围**，不表示未来使用永远没有风险。

## Bet 9 — 跨平台证据必须可比较

两个平台名并不等于完成跨平台验证。Lv5 只接受两个不同 Agent 平台使用同一
契约文件和同一脱敏测试夹具的记录；两者都用 SHA-256 内容指纹固定。更换模型、
提示词、验收规则或夹具后得到的两次成功，不能拼成一组跨平台证据。

## Non-goals (v0.1)

- Pulling rules from GitHub at runtime
- Replacing `create-skill` for greenfield authoring
- Providing a universal security sandbox
- Shopify write gates (out of scope; see specialized ops packs)
