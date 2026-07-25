# Skill proposal example — customer-background-research

## Context

- Company type: foreign-trade manufacturer.
- Primary outcome: decide whether to invest in a first discovery call.
- Trigger: new B2B inquiry with company name and contact route.
- Pain: salespeople currently rely on search snippets and intuition.

## Proposed Skill

- Working name: `customer-background-research`
- Invocation: user-invoked because purpose, scope, and identifiers must be
  confirmed.
- WHAT: produce an evidence-backed sales-qualification brief from public
  business sources.
- WHEN: new overseas B2B inquiry; pre-call qualification; user asks to investigate
  a company.
- When NOT: credit scoring, sanctions clearance, legal advice, private-person
  investigation, or automatic rejection.

## Check axes

- Entity resolution.
- Runtime source-access capability.
- Browser screenshot evidence for official-site claims.
- Source quality and claim labeling.
- Conflicts, unknowns, and confidence.
- Human decision handoff.

## Operational data contract

### Module selection

| Module | Apply? | Reason |
| --- | --- | --- |
| L | Y | recurring lead-priority decision uses a margin threshold |
| S | Y | claims depend on Google-discovered, first-party, registry, and ERP sources |
| V | Y | evidence strength varies from snippet to screenshot to corroboration |
| R | Y | later conversion and overrides should tune the scoring rule |

This example uses the full contract because all four conditions are present.
Other Skills may select fewer modules or mark them N/A with a reason.

### Value level

| Metric | L1 | L2 | L3 | Rule version | Owner |
| --- | --- | --- | --- | --- | --- |
| projected gross margin | `<15%` | `15%–24.99%` | `>=25%` | `sales-qualification-v1` | sales manager |

These fictional thresholds require company confirmation. L3 means business
potential, not verified identity.

### Source and verification

- S1: discovery lead, including Google results.
- S2: visible direct/credible source, including official-site claims.
- S3: fit-for-claim authority/system of record, including registry or ERP.
- V0: not verified.
- V1: source discovered only.
- V2: opened and captured in a durable artifact; browser claims require
  screenshot + URL + time.
- V3: V2 plus independent/authoritative corroboration and conflict handling.

### Decision rule

- `L3 + V3`: eligible for priority human follow-up.
- `L3 + V2`: provisional; human review or another corroborating source.
- Any `L + V0/V1`: no final automated decision.

### Records

- `score-rules.csv`
- `source-register.csv`
- `evidence-log.csv`
- `run-log.csv`

Use `run_id`, ISO 8601 timestamps with timezone, `score_rule_version`, Skill
version, and record schema version.

## PDCA

| Phase | Contract |
| --- | --- |
| Plan | Confirm decision, L rules, source register, required V, exclusions, and schema versions |
| Do | Resolve entity, discover sources, capture artifacts, and append evidence rows |
| Check | Apply S/V rules, cross-check conflicts, and calculate L and V separately |
| Act | Append run row; human decides/overrides; compare outcomes by rule version |

## SMART outcome

| Letter | Draft |
| --- | --- |
| Specific | One entity, one qualification purpose, one brief |
| Measurable | Numeric L result, V level, four linked CSV records, and evidence for every material claim |
| Achievable | Uses available public sources and explicit fallbacks |
| Relevant | Supports sales-time allocation, not unrelated compliance decisions |
| Time / run-bound exit | Ends after evidence brief and human handoff, or earlier with a documented blocker |

## Evidence and tool contract

- Test Google Search; never assume access.
- Treat search snippets as discovery only.
- Open LinkedIn public pages only; do not bypass login/CAPTCHA/access controls.
- Open the official website in a real browser.
- Capture screenshots showing each material official-site claim.
- Record final URL, page title, time/timezone, and screenshot path.
- If browser screenshots are unavailable, stop live website verification and
  report the blocker.

## Build vs reuse

| Need | Decision |
| --- | --- |
| One-question interview discipline | Reuse `pm-workflow-planning` pattern |
| Browser/search control | Reuse connected browser/search Skill at runtime |
| Qualification-specific evidence contract | Build `customer-background-research` |
| Hard-gate review | Reuse `skill-self-check` |
| Credit/compliance decision | Keep outside this Skill; use authorized process |
| L/S/V and CSV contract | Reuse `pm-workflow-planning` operational data contract |

## Promotion gate

The draft must:

1. pass `hard_gates.py`;
2. be forward-tested with accessible, blocked, and ambiguous-entity cases;
3. complete at least one anonymized real pilot;
4. remain under `exp/` until those checks pass.
