# Growth profile contract

## Contents

1. [Dual track](#dual-track)
2. [Source reports](#source-reports)
3. [Package health preflight](#package-health-preflight)
4. [Two growth lines](#two-growth-lines)
5. [Skill levels](#skill-levels)
6. [Skill type](#skill-type)
7. [Operational metrics](#operational-metrics)
8. [Behavior evidence](#behavior-evidence)
9. [Analyzed subject](#analyzed-subject)
10. [Personal interpretation](#personal-interpretation)
11. [Personal learning quest](#personal-learning-quest)
12. [Privacy](#privacy)

## Dual track

The scorecard serves **enterprise Skill employees** first: people who need a
usable business Skill with clear triggers, steps, acceptance, and stop rules.
They do **not** need to understand every Agent platform or maintain this
repository's certification engineering.

| Track | Audience | Default surface | Typical bar |
| --- | --- | --- | --- |
| **Enterprise mainline** | Business authors / operators | `verdict`, root `next_quest`, learning quest | Package health, ship floor, static safety, plain next practice |
| **Advanced audit** | Skill authors / maintainers | `advanced_audit` block | Behavior JSON, failure recovery, portable contract, two-platform fingerprints |

Rules:

- When package health is assessable, ship floor and the contract minimum are
  met, static safety passes, and Critical count is zero, root `verdict` is
  `ready_for_controlled_use` even if author behavior evidence is missing.
- Missing behavior / multi-platform proof is recorded on `advanced_audit.note`
  (for example “作者进阶证据未附”), not as the enterprise headline failure.
- Root `next_quest` stays on enterprise practice after the enterprise-ready
  gate (real scenario trial, acceptance evidence, materials). Behavior JSON
  and cross-platform steps live only under `advanced_audit.next_quest`.
- Lv3–Lv5 unlock math is unchanged for advanced audit; Lv4–Lv5 labels are
  marked as the author track.

`skill_engineering.scores.enterprise_ready` is the canonical boolean for that
mainline gate. The root verdict, Lv2 unlock, and advanced-audit note must consume
this value instead of recomputing a weaker ship-floor-only substitute.

## Source reports

`profile_engine.py` accepts four independent UTF-8 JSON inputs:

| Input | Producer | Required? |
| --- | --- | --- |
| readiness | `readiness_gates.py` | No |
| hard gates | `hard_gates.py` | No |
| ship safety | `ship_safety.py` | No |
| behavior | trusted test process | No |

At least one input is required. Missing inputs remain explicit and are never
treated as passing.

## Package health preflight

New hard-gate reports contain `package_health`. Maturity is assessable only when
`status` is `valid_skill_package` and `assessable` is `true`. The checks cover:

- one unambiguous Skill root;
- frontmatter name/root basename agreement;
- standard top-level layout and separation of runtime outputs;
- portable paths;
- valid explicit bundled-resource links;
- filename/residue hygiene and duplicate large resources;
- static installability.

When the package is invalid, `skill_engineering.status` is `invalid_package`,
`level` is `null`, every dimension is `state: null` with
`status: not_assessable`, and badges are empty. The root verdict is
`invalid_skill_package`. Raw basic/contract/support scores remain available only
as `partial_file_diagnostics_only`; they must not be described as maturity or
capability.

## Analyzed subject

Every profile contains a `subject` object so a saved or printed scorecard can
identify what it analyzed:

```json
{
  "kind": "skill",
  "label": "Skill",
  "name": "example-skill",
  "source": "hard_gates.frontmatter.name"
}
```

The deterministic precedence is:

1. explicit `--subject-name`;
2. `hard_gates.frontmatter.name`;
3. the basename of `ship_safety.target`;
4. `readiness.input.process_name`;
5. `未命名分析对象`.

Only a safe display name is stored. A full source path is never copied into
`subject`. When no Skill audit exists, a readiness-only result is labeled
`业务流程` rather than pretending that a Skill already exists.

## Two growth lines

- `business_readiness` answers whether the work can be delegated.
- `skill_engineering` answers whether the implementation is structured, tested,
  controlled, and portable.

Do not add the two levels, average them, or convert them into one percentage.

### Personal capability view vs project status

The growth view interprets `skill_engineering` as the creator's **demonstrated
Skill-building capability** based on the analyzed work sample. It may show type,
ability stage, evidence axes, badges, and the next practice task. It does not
show `stop_ship`, `static_pass`, or other project delivery verdicts as personal
badges.

Detection and technical evidence remain project views. They preserve the exact
delivery verdict, severity counts, finding IDs, and limitations. Moving a
verdict out of the personal card must never delete, soften, or recalculate it.

## Personal interpretation

`skill_engineering.personal_interpretation` is generated by Python from the
same type, level, dimension states, and finding IDs:

```json
{
  "eyebrow": "你的能力画像",
  "headline": "你擅长把复杂任务做成可执行工具",
  "summary": "从这份 Skill 的结构和配套材料看……"
}
```

The headline states one concrete demonstrated capability. The summary combines
one evidence-based strength, the current capability stage, and no more than
three growth priorities. It must not explain how the UI works, use project
delivery verdicts as personal labels, or claim more than the evidence supports.
The offline HTML renders these fields and does not compose a new assessment.

## Personal learning quest

`skill_engineering.learning_quest` is a personal capability practice plan.
It is separate from the root `next_quest`, which remains the highest-priority
project remediation:

- the Growth view renders `learning_quest`;
- the Detection view renders the root `next_quest`;
- `learning_quest` may teach measurable goals, scenario judgment, reusable
  components or scripts, Harness placement, behavior testing, safety controls,
  recovery, and platform adaptation;
- `learning_quest` must not contain finding IDs, delivery verdicts, or commands
  to repair the current artifact.

Every Lv0–Lv5 stage has a deterministic practice template containing a title,
short action, three or more `practice_points`, and one `acceptance` statement.
Harness means an external test driver that supplies sanitized inputs, invokes
the target Skill, records outputs, and checks rules without performing real
business sends or writes.

## Skill levels

| Level | Required evidence | Track |
| --- | --- | --- |
| Lv0 | A Skill exists but basic structure is below the minimum | Enterprise |
| Lv1 | Basic structure is recognizable | Enterprise |
| Lv2 | Static floor, contract minimum, zero criticals, and static safety pass | Enterprise (default “good enough to trial”) |
| Lv3 | Lv2 plus core-flow and PDCA behavior evidence | Advanced audit |
| Lv4 | Lv3 plus failure recovery and evidence for every applicable safety control; a genuinely inapplicable external-action or write-back control needs explicit scope evidence | Advanced audit |
| Lv5 | Lv4 plus a portable contract and two verified platform records that share the same contract and fixture fingerprints | Advanced audit |

`stop_ship` caps the level at Lv1.

## Skill type

Types describe the creator's strongest evidenced Skill-building pattern in the
current work sample. They are personal capability interpretations, not fixed
personality or psychological claims.

Six dimensions use evidence states from 0 to 4:

1. intent and contract;
2. workflow and execution;
3. tooling and support;
4. verification and learning;
5. safety and control;
6. portability and adaptation.

The generator calculates fixed affinities for six types and uses a fixed tie
order. A balanced type requires all dimensions at state 3 or 4 with a maximum
spread of one.

### Visual evidence axes

The offline HTML renders every 0–4 state as one single-direction evidence axis:

| State | Displayed coverage |
| --- | --- |
| 0 | 0% |
| 1 | 25% |
| 2 | 50% |
| 3 | 75% |
| 4 | 100% |

Only the current coverage is displayed. The UI does not show a complementary
gap percentage because readers naturally interpret a visible 100% as a strong
result. These percentages are only a visual translation of the existing
deterministic state; they are not personality probabilities, averages across
the two growth lines, or new scores. An unassessed axis displays `—` and remains
explicitly unassessed in its accessible label.

State 2 (50%) is the ceiling for static files and declarations. State 3 (75%)
requires trusted behavior evidence. State 4 (100%) means the dimension-specific
full-evidence gate below is met:

| Dimension | 100% full-evidence gate |
| --- | --- |
| Intent and contract | Complete static contract plus failure recovery and satisfied applicable-control gates; a not-applicable gate counts only with scope evidence |
| Workflow and execution | Core flow and failure recovery have trusted behavior evidence |
| Tooling and support | Complete support kit used by a tested core flow with failure-recovery evidence |
| Verification and learning | Both core-flow testing and PDCA learning evidence are present |
| Safety and control | Static safety passes with zero criticals, plus failure recovery and satisfied external-action/write-back gates; a not-applicable gate requires the evidence rules below |
| Portability and adaptation | A portable contract plus at least two verified platforms using the same contract and fixture SHA-256 identifiers |

For safety, 100% means every control that applies to this Skill has trusted
evidence within the current rules and test scope. If an external-action or
write-back control genuinely does not apply, the record must prove that scope
instead of silently omitting the check. For a write-back waiver, a trusted
harness must also show `target_unchanged: true`. For an external-action waiver,
static safety must pass with zero criticals and the safety report must contain
no detected external action. This does **not** guarantee that all future uses
are permanently risk-free.

## Operational metrics

`skill_engineering.operational_metrics` adds two informational dimensions
without changing the six evidence axes, type, level, verdict, or ship floor:

- `token_consumption`: `hard_gates.py` estimates the static `SKILL.md` input as
  `ceil(UTF-8 byte length / 4)`. This model-neutral estimate is low confidence
  and excludes output, tools, conversation history, and support files loaded
  on demand. A valid behavior observation replaces it.
- `runtime_duration`: static audit reports always use `not_measured` because
  they do not execute the target Skill. Only trusted behavior evidence may set
  it to `observed`.

A token observation needs non-negative integer `total_tokens` (or both
`input_tokens` and `output_tokens`), consistent component totals, a positive
integer `runs`, and a shareable evidence reference. A runtime observation needs
non-negative `duration_ms`, a positive integer `runs`, and a shareable evidence
reference. Invalid or local-absolute evidence never becomes an observed value.

`run_full_audit.py` also records `audit_execution.duration_ms`. That is the
audit tool's own elapsed assessment time, not the target Skill's runtime.

## Behavior evidence

Behavior evidence is **advanced audit only**. Enterprise mainline does not
require it for `ready_for_controlled_use`. When supplied, it must come from a
trusted test process:

```json
{
  "schema_version": "1.1",
  "core_flow_tested": false,
  "pdca_evidence": false,
  "safe_external_actions": false,
  "write_back_integrity": false,
  "failure_recovery": false,
  "portable_contract": false,
  "target_unchanged": true,
  "applicability": {
    "external_actions": {
      "status": "not_applicable",
      "evidence": "evidence/scope-review.md#external-actions"
    },
    "write_back": {
      "status": "not_applicable",
      "evidence": "evidence/run-manifest.json#target-integrity"
    }
  },
  "platforms": [
    {
      "name": "platform name",
      "status": "verified",
      "evidence": "evidence/platform-run.json",
      "contract_id": "sha256:64-lowercase-hex-characters",
      "fixture_id": "sha256:64-lowercase-hex-characters"
    }
  ],
  "operational_metrics": {
    "token_consumption": {
      "status": "observed",
      "input_tokens": 800,
      "output_tokens": 200,
      "total_tokens": 1000,
      "runs": 1,
      "evidence": "evidence/run.json#usage"
    },
    "runtime_duration": {
      "status": "observed",
      "duration_ms": 1250,
      "runs": 1,
      "statistic": "single_run",
      "evidence": "evidence/run.json#timing"
    }
  }
}
```

Boolean values must be literal JSON booleans. Missing applicability records keep
the legacy meaning `applicable`; this prevents omission from becoming a waiver.
`status: not_applicable` counts only when the rules above are satisfied and the
evidence is a shareable relative or approved reference rather than a local
absolute path.

A platform counts only when it has a non-empty name, `verified` status, a
shareable evidence reference, and valid `sha256:` contract and fixture IDs.
Lv5 requires two distinct platform names in the **same** contract/fixture
fingerprint group. Two platform records created from different prompts,
contracts, or fixtures do not demonstrate comparable cross-platform behavior.

## Privacy

- Real source reports and generated scorecards belong outside the public repo.
- The profile strips complete local paths from finding evidence.
- The HTML embeds the sanitized profile, not the original input reports.
- Do not treat this sanitization as a substitute for reviewing free-text
  messages before sharing a report.
