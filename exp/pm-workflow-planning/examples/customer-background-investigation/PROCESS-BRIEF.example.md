# Example process brief — customer background investigation

This is fictional and contains no real customer data.

## Starting request

> “收到一个海外客户询盘，帮我调查一下这个客户靠不靠谱。”

This request is too broad to execute. The same words could mean sales
qualification, legal-entity verification, credit risk, sanctions/compliance, or
pre-meeting preparation.

## First decision question

**Question:** 这次背景调查最终要支持哪个决定？

**Recommended answer:** 先限定为“销售资格判断”：确认主体是否基本真实、业务是否匹配、是否值得销售人员投入一次人工沟通。不要把它表述为信用审查或合规放行。

**Why:** 信用、制裁和合规结论需要不同的权威数据、权限和人工责任。把它们混在一个通用网络调查里会制造虚假的确定性。

**Main alternative:** 如果实际目标是授信或签约放行，停止此流程，改由有权限的财务/法务/合规流程定义来源和审批。

Wait for the user to confirm or correct this decision before asking the next
question.

## Confirmed fictional scope

- Company type: foreign-trade manufacturer.
- Trigger: a new B2B inquiry with company name, email domain, and claimed
  website.
- Intended decision: whether a salesperson should invest in a first discovery
  call.
- Output: evidence-backed qualification brief, not a credit/compliance verdict.
- Human owner: sales operations.
- Human approver: account owner or sales manager.
- Out of scope: private personal data, paid credit data, sanctions clearance,
  legal advice, automated rejection.

## Confirmed measurable target

This fictional company chooses projected gross margin as the first value metric:

| Metric | Formula | L1 | L2 | L3 | Rule owner |
| --- | --- | --- | --- | --- | --- |
| `projected_gross_margin_pct` | `(quoted revenue - estimated total cost) / quoted revenue × 100` | `<15%` | `15%–24.99%` | `>=25%` | sales manager |

These are example thresholds, not a universal margin standard. A real interview
must confirm margin type, cost basis, currency handling, thresholds, and
`score_rule_version`.

Business value and verification remain separate. An `L3` lead with only `V1`
evidence is “high potential, still unverified,” not an approved priority lead.

## Capability gate before research

The Agent must test, not assume:

| Source/capability | Why needed | Required action |
| --- | --- | --- |
| Google Search | discover corroborating sources | Run and record a relevant query; snippets are leads only |
| LinkedIn | optional public company/role corroboration | Open public pages only; stop at login/CAPTCHA/access challenge |
| Official website | verify first-party identity and business claims | Open in a real browser and capture relevant screenshots |
| Public registry | legal-entity corroboration when available | Use permitted official source and record jurisdiction limits |
| Screenshot capture | visible-page evidence | Verify capture works before promising official-site coverage |

If a required capability is unavailable, the output must say what was not
verified and how that affects confidence.

## Required record set

- `score-rules.csv` — approved L rules.
- `source-register.csv` — Google, official site, LinkedIn, registry, ERP and
  their claim-specific S grades/access status.
- `evidence-log.csv` — one row per claim/source/artifact with V level.
- `run-log.csv` — one row for the final L level, overall V level, human decision,
  and next action.

## Artifact chain

1. [WORKFLOW-CANVAS.example.md](WORKFLOW-CANVAS.example.md)
2. [SKILL-PROPOSAL.example.md](SKILL-PROPOSAL.example.md)
3. [customer-background-research/SKILL.md](customer-background-research/SKILL.md)
4. [score-rules.example.csv](score-rules.example.csv)
5. [source-register.example.csv](source-register.example.csv)
6. [evidence-log.example.csv](evidence-log.example.csv)
7. [run-log.example.csv](run-log.example.csv)
