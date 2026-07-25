# Operational data contract

Use selected parts of this contract to turn experience-based work into
measurable, reviewable, and repeatable Skill runs. This contract is optional and
modular. Applying every module to every Skill creates ceremony without value.

## Contents

1. Selection gate
2. Goal gate: measurable value level (`L1–L3`)
3. Source module: source fitness (`S1–S3`)
4. Verification module: evidence strength (`V0–V3`)
5. Record module: linked records when history is needed
6. Decision matrix and evolution loop

## 1. Selection gate

Judge applicability from the process first. If it is unclear, ask one question
and include a recommendation:

> 这个 Skill 的结果会不会被重复用于分级、审批或跟进，并且需要以后根据历史结果调整规则？根据目前的流程，我建议启用 `<modules>`，跳过 `<modules>`，因为 `<reason>`。

Select modules independently:

| Module | Enable when | Usually skip when |
| --- | --- | --- |
| **L — value/score** | repeated ranking, thresholds, prioritization, approval, KPI, accept/reject decision | creative output, deterministic transformation, one-off exploration, or no meaningful numeric business decision |
| **S — source** | facts come from multiple internal/external sources and provenance/access matter | the input is one fixed user-provided artifact or the source is already governed elsewhere |
| **V — verification strength** | claims need screenshots, exports, confidence levels, cross-checking, QA, or risk-based evidence | a simple deterministic operation already has a binary test and evidence strength does not vary |
| **R — record/history** | repeated runs, handoff, audit, trend analysis, feedback learning, or rule improvement | one-off/private work, or an existing CRM/ERP/log already records the required fields |

Valid partial choices include:

- `S+V`: one-off web fact verification without lead scoring.
- `L+R`: internal prioritization using an existing system of record.
- `R`: repeated deterministic jobs where only run history matters.
- `none`: brainstorming, creative drafting, simple explanation, or a one-off
  transformation with an adequate completion check.
- `L+S+V+R`: recurring business decisions using multiple sources and a feedback
  loop, such as customer qualification.

Record `Y`, `N`, or `Ask user` for L/S/V/R and one-sentence reasoning. A
well-justified `N/A` is not a Skill defect and must not lower the general
`skill-self-check` score.

## 2. Goal gate — L1 to L3

Apply this section only when L is selected. Then require a measurable objective
before designing the scoring workflow. “Good lead,” “high profit,” and
“important customer” are prompts for clarification, not scoring rules.

Define:

| Field | Requirement |
| --- | --- |
| `metric_id` | Stable machine-readable name, such as `gross_margin_pct` |
| `metric_name` | Human-readable name |
| `formula` | Exact calculation or lookup rule |
| `unit` | `%`, CNY, USD, days, count, rate, boolean, or named category |
| `direction` | `higher_better`, `lower_better`, `target_range`, or `binary` |
| `weight` | Numeric weight when several metrics form one score |
| `baseline` | Current value or `unknown — needs data` |
| `L1/L2/L3` | Non-overlapping thresholds and boundary handling |
| `owner` | Role allowed to approve the rule |
| `score_rule_version` | Version used to preserve historical comparability |

Recommended level meaning:

- **L1:** low business value or below the approved minimum.
- **L2:** viable but needs normal review or improvement.
- **L3:** high business value and eligible for priority handling.

For a multi-metric score, normalize to `0–100` and let the user confirm the
level bands. A starting proposal may use `L1=0–39`, `L2=40–69`, `L3=70–100`,
but the Skill must wait for the business owner to approve or replace them.

Illustrative single-metric rule:

| Metric | L1 | L2 | L3 |
| --- | --- | --- | --- |
| projected gross margin | `<15%` | `15%–24.99%` | `>=25%` |

The example is not a universal margin rule. Confirm whether the company means
gross margin, contribution margin, or net margin and which costs/currency apply.

## 3. Source module — S1 to S3

Apply this section only when S is selected. Grade a source by how well it can
support a specific claim:

| Grade | Meaning | Typical use |
| --- | --- | --- |
| **S1 — discovery** | Leads to possible evidence but is weak alone | Google results, directories, unverified social mentions |
| **S2 — direct/credible** | Direct first-party statement or credible independent source | visible official website, public company page, reputable industry source |
| **S3 — authoritative** | System of record or authority suited to the claim | public registry for legal identity, ERP export for internal margin, signed document |

Important:

- Google is a discovery channel, not the final source.
- An official website is S2 for the company’s own product/capability claims, but
  it is not automatically S3 for legal registration, credit, or compliance.
- Source grade is claim-specific. Record `claim_scope`.
- Record runtime access status separately from source grade.

## 4. Verification module — V0 to V3

Apply this section only when evidence strength can vary and V is selected.

| Level | Meaning | Minimum artifact |
| --- | --- | --- |
| **V0 — not verified** | Not attempted, tool unavailable, or no evidence | Blocker and next action |
| **V1 — discovered** | Candidate source or snippet found; underlying claim not captured | Query/URL and access status |
| **V2 — directly observed** | Source opened and the claim captured in a durable artifact | Browser: screenshot + URL + timestamp; data system: export/query result + timestamp |
| **V3 — corroborated** | V2 evidence plus a second independent or authoritative fit-for-claim source; conflicts resolved or escalated | Two linked evidence rows and resolution note |

For browser facts, oral summaries and model memory stay at V0. A search snippet
stays at V1. The visible page plus screenshot can reach V2. Cross-source
corroboration can reach V3.

## 5. Record module — linked records

Apply this section only when R is selected. Reuse an existing approved
CRM/ERP/database/log when it already satisfies the required fields. Otherwise,
use UTF-8 CSV with a header row and ISO 8601 timestamps including timezone.
Keep one fact per cell. Use `run_id` to join selected tables.

### `score-rules.csv`

Configuration: metrics, formulas, weights, thresholds, rule owner, and version.
Change rules by creating a new version; keep historical versions.

### `source-register.csv`

Configuration/runtime inventory: source purpose, S grade, access method,
runtime status, last test time, fallback, and owner.

### `evidence-log.csv`

One row per claim-source observation: query/URL, method, artifact, observed
value, S grade, V level, result, timestamp, confidence, and limitation.

### `run-log.csv`

One row per completed or blocked run: subject, primary metric ID, reproducible
score value/unit, L level, overall V level, decision, human owner/override, next
action, and record version. For a multi-metric `0–100` score, use a named
aggregate metric such as `weighted_total` and preserve its formula in the score
rules.

Create only the selected records:

- L selected → `score-rules.csv`.
- S selected → `source-register.csv`.
- V selected → `evidence-log.csv`.
- R selected → `run-log.csv` or an equivalent existing system record.

Copy the header-only templates from `assets/templates/` when CSV is the chosen
storage.

## 6. Decision matrix

Use this matrix only when both L and V are selected. Business value and
verification strength remain separate:

| Value × verification | Recommended action |
| --- | --- |
| `L3 + V3` | Priority action is supportable; hand to the named human owner |
| `L3 + V2` | Provisional priority; human review or one more corroborating source |
| `L3 + V0/V1` | High potential only; continue verification before relying on it |
| `L2 + V2/V3` | Normal workflow |
| `L1 + V2/V3` | Low-priority/stop recommendation may be recorded; human policy decides |
| Any `L + V0/V1` | No final automated business decision |

The final decision rule must name the human owner and any allowed automation.

## Evolution loop

When R is selected, use records to improve the Skill:

1. Compare predicted L level and decision with later real outcomes.
2. Count human overrides and group `override_reason`.
3. Track missing-source and V0/V1 rates.
4. Propose a new `score_rule_version` when thresholds or weights change.
5. Preserve prior rows; evaluate before/after by version.

Minimum review metrics:

- runs by L level;
- runs by V level;
- conversion or outcome by L level;
- human override rate;
- blocked-source rate;
- missing-evidence rate;
- false-positive/false-negative examples confirmed by humans.
