# Workflow canvas example — customer background investigation

## Scope

- Process: qualify a new overseas B2B inquiry.
- Intended decision: invest in a first sales discovery call or hold for more
  information.
- Trigger: inquiry includes a company name and at least one contact route.
- Owner: sales operations.
- Approver: account owner or sales manager.
- Out of scope: credit rating, sanctions clearance, legal advice, automated
  rejection, private-person investigation.

## Module selection

| Module | Apply? | Reason | Artifact |
| --- | --- | --- | --- |
| L — numeric value/score | Y | recurring leads are prioritized by an approved margin rule | `score-rules.csv` |
| S — source provenance | Y | identity and capability claims come from several source types | `source-register.csv` |
| V — verification strength | Y | screenshots, exports, and corroboration change decision confidence | `evidence-log.csv` |
| R — run/history record | Y | outcomes and human overrides must improve later rules | `run-log.csv` |

## Measurable goal

| Metric ID | Formula | Unit | L1 | L2 | L3 | Required V for action | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `projected_gross_margin_pct` | `(quoted revenue - estimated total cost) / quoted revenue × 100` | percent | `<15` | `15–24.99` | `>=25` | L1/L2: V2; L3 priority: V3 | sales manager |

Rule version: `sales-qualification-v1`. Thresholds are fictional and require
company confirmation.

## Source and capability matrix

These are example placeholders. A real run must replace them with tested
results.

| Source ID | Source | Claim scope | S grade | Required? | Runtime status | Fallback / blocker owner |
| --- | --- | --- | --- | --- | --- | --- |
| `src-google` | Google Search | discovery | S1 | Yes | not tested | permitted alternative search / sales ops |
| `src-linkedin` | LinkedIn public page | public company presence | S2 | Optional | not tested | mark unverified; keep access controls intact |
| `src-official-site` | Official website | first-party products/capabilities | S2 | When claimed | not tested | request corrected URL / sales ops |
| `src-registry` | Public registry | legal identity | S3 | Jurisdiction-dependent | not tested | identify registry / sales ops |
| `src-erp` | Internal ERP | margin and order history | S3 | Yes for scoring | not tested | authorized export / sales manager |
| `browser-screenshot` | Browser capture | browser evidence artifact | n/a | Yes for web V2 | not tested | connect browser or stop live verification |

## Verification levels

| Level | Customer-research meaning |
| --- | --- |
| V0 | not checked/tool unavailable |
| V1 | source or snippet discovered only |
| V2 | source opened and durable artifact captured; web evidence includes screenshot + URL + time |
| V3 | V2 plus independent/authoritative corroboration and conflict handling |

## Workflow

| Step | Role | Action | Metric/source | Evidence and V | Record written | Done when | Exception / escalation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1. Confirm purpose and score | Agent + sales owner | Confirm decision, formula, thresholds, actions, version | gross margin / L1–L3 | Approved rule | `score-rules.csv` | Rule has numeric boundaries and owner | Missing cost basis → blocker |
| 2. Test sources | Agent | Test Google, browser, site, LinkedIn, registry, ERP | source register / S1–S3 | Access-test evidence | `source-register.csv` | Every required source has status/fallback | Missing browser → planning only |
| 3. Resolve entity | Agent | Match identifiers | S2/S3 candidate sources | Evidence rows V1–V3 | `evidence-log.csv` | One entity supported or ambiguity explicit | Multiple matches → request identifiers |
| 4. Discover sources | Agent | Search and open underlying sources | Google S1 → target source | Query plus opened-page rows | `evidence-log.csv` | Snippets remain V1 | Search blocked → fallback/lower coverage |
| 5. Verify official site | Agent | Open page and capture visible claims | official site S2 | Screenshot + URL + time = V2 | `evidence-log.csv` | Every website claim points to artifact | Blank/blocked → V0 and blocker |
| 6. Corroborate | Agent | Check registry/independent source | fit-for-claim S2/S3 | Two linked rows = candidate V3 | `evidence-log.csv` | Conflict resolved or escalated | Access challenge → keep controls intact |
| 7. Calculate L and overall V | Agent | Apply approved rule; choose lowest required V across material claims | score rule version | Calculation and evidence links | `run-log.csv` | L and V are separately recorded | L3 with V0/V1 → continue verification |
| 8. Human decision | Sales owner | Call / request information / hold | L×V matrix | Decision and override reason | `run-log.csv` | Named human records action | Agent does not auto-reject |

## Decision points

| Decision | Recommended default | User/role who decides | Evidence needed | Alternative |
| --- | --- | --- | --- | --- |
| Investigation purpose | Sales qualification only | Sales owner | Inquiry context | Authorized credit/compliance workflow |
| LinkedIn required? | Optional corroboration | Sales ops | Source policy and access | Continue with limitation |
| Proceed to call? | Human decision | Account owner | Evidence brief | Request more identifiers / hold |

## Recording contract

| Table | One row per | Example |
| --- | --- | --- |
| `score-rules.csv` | level rule | [score-rules.example.csv](score-rules.example.csv) |
| `source-register.csv` | source/capability | [source-register.example.csv](source-register.example.csv) |
| `evidence-log.csv` | claim-source observation | [evidence-log.example.csv](evidence-log.example.csv) |
| `run-log.csv` | research run | [run-log.example.csv](run-log.example.csv) |

## Completion

The workflow is complete when:

- the purpose and exclusions are confirmed;
- every required source is tested and its status recorded;
- official-site claims have screenshots, URLs, and timestamps;
- verified facts, first-party claims, conflicts, and unknowns are separated;
- L and V are calculated separately under named rule/schema versions;
- all four CSV tables have linked rows using `run_id`;
- a human owner makes the final sales decision.
