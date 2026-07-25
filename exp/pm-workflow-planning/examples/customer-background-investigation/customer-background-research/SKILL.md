---
name: customer-background-research
description: >-
  Generates an evidence-backed sales-qualification brief by researching a
  company through public business sources. Use when a foreign-trade,
  manufacturing, or engineering sales team receives a new B2B inquiry and asks
  to 调查客户背景, verify a company before a first call, or qualify whether the
  lead deserves human follow-up.
---

# Customer Background Research

Research one company for one confirmed sales-qualification purpose. Use public
business information only. The final decision belongs to the sales owner.

## When to use

- A new overseas B2B inquiry needs first-call sales qualification.
- The user provides a company name plus at least one matching identifier.
- The intended output is an evidence brief for a named human decision owner.

## When NOT to use

- Credit scoring, sanctions/compliance clearance, legal advice, or contracting
  approval.
- Private-person investigation or collection of unrelated sensitive data.
- Automatic lead rejection.
- Any request to bypass login, CAPTCHA, rate limits, or access controls.

## Inputs

- Intended decision.
- Company name plus country, domain, email domain, address, or another
  identifier.
- Claimed official website, if provided.
- Business metric, formula, unit, L1/L2/L3 thresholds, rule owner, and
  `score_rule_version`.
- Required/forbidden sources and report deadline.

If the intended decision is unclear, ask one question and recommend limiting the
run to first-call sales qualification. Wait for confirmation.

If the scoring rule is unclear, propose numeric thresholds and ask the business
owner to confirm or replace them. Clarify margin type and cost basis before
using profit/margin in a rule.

**Done when:** one target entity, one permitted purpose, and one versioned
numeric L1/L2/L3 rule are confirmed.

## Check axes

- Entity match.
- Business value level (`L1–L3`) and scoring version.
- Claim-specific source grade (`S1–S3`) and runtime access.
- Verification strength (`V0–V3`).
- Browser-visible official-site evidence.
- Corroboration and conflicts.
- CSV evidence/run records and limitations.
- Human handoff.

## Process

### 1. Confirm the measurable scoring contract

Define:

- metric ID, formula, unit, direction, and owner;
- non-overlapping L1/L2/L3 boundaries;
- minimum V level and human action allowed for each L level;
- scoring rule version.

Keep business value L separate from verification V. L3 with V0/V1 is high
potential, not a verified priority.

**Done when:** the approved rule can be written to `score-rules.csv`.

### 2. Test and grade source capabilities

Test rather than assume:

- Google Search or the permitted discovery source;
- browser access and screenshot capture;
- claimed official website;
- optional LinkedIn public page;
- relevant public registry.

Record each as `verified accessible`, `verified blocked`, `tool unavailable`,
`not tested`, or `not required`.

Assign:

- S1 to discovery leads such as Google results;
- S2 to direct/credible sources such as visibly verified official pages;
- S3 to fit-for-claim authorities/systems of record such as registries or ERP.

Grade sources per claim. An official website is S2 for first-party product
claims, not S3 for legal identity or credit.

If screenshot capture is unavailable, label official-site claims `unverified`.
Report the blocker or ask for a connected browser.

**Done when:** every required source has source ID, claim scope, S grade, tested
status, fallback, owner, and a `source-register.csv` row.

### 3. Resolve the entity

Match at least two available identifiers such as legal/trading name, domain,
country, address, registration number, or contact details. Keep same-name
companies as separate candidates until evidence supports a match.

**Done when:** one entity is supported, or ambiguity is explicit and the user is
asked for another identifier.

### 4. Discover and open sources

Run and record relevant searches. Treat snippets as leads only. Open the
underlying source before using a claim.

For LinkedIn, use only publicly accessible pages in the authorized browser
session. Stop at login, CAPTCHA, or an access challenge; record the blocker with
access controls intact.

Record discovered-only leads as V1.

**Done when:** candidate sources are opened or their access failures have V0/V1
evidence rows.

### 5. Verify the official website visually

For each material first-party claim:

1. Open the exact page in a real browser.
2. Wait for visible content to render.
3. Capture a screenshot showing the claim and surrounding page context.
4. Record final URL, page title, capture time/timezone, and screenshot
   path/attachment.
5. Paraphrase only what is visibly present.

Use DOM/text extraction as support, not as a replacement for browser screenshot
evidence.

Write one `evidence-log.csv` row per material claim. A visible browser page with
screenshot, URL, and time can reach V2.

**Done when:** every official-site claim points to a V2 artifact or is recorded
as V0/V1 with a blocker.

### 6. Corroborate and handle conflicts

Prefer:

- official registries for legal identity;
- visibly verified company pages for first-party business claims;
- credible independent sources for corroboration.

Preserve conflicting claims with dates and require explicit human judgment.
Escalate material identity, credit, compliance, or contracting conflicts to the
responsible human.

V3 requires V2 evidence plus a second independent or authoritative
fit-for-claim source. Link both evidence rows and record the conflict resolution
or escalation.

**Done when:** facts, first-party claims, conflicts, and unknowns are separated
and each material claim has a V level.

### 7. Calculate L and overall V

Apply only the confirmed `score_rule_version`.

- Calculate the numeric value and L level.
- Set overall V to the lowest verification level among claims required for the
  proposed action.
- Apply the L×V action matrix.
- Send L3+V0/V1 runs back for more verification.

**Done when:** calculation inputs, formula, L, V, rule version, and next action
are reproducible from records.

### 8. Write the brief and records

Include:

1. Purpose and scope.
2. Numeric score, L level, scoring rule version, and overall V level.
3. Entity match and unresolved ambiguity.
4. Source register with S grades and runtime access.
5. Evidence ledger: claim, source, URL, screenshot, captured time, V level,
   confidence, limitation.
6. Verified facts vs first-party claims.
7. Conflicts and missing coverage.
8. Recommended next action: call, request more identifiers, or hold for human
   review.

Restrict conclusions to supported observations. Reserve “safe,” “legitimate,”
or “creditworthy” conclusions for an authorized process.

Append:

- approved rules to `score-rules.csv`;
- source/access rows to `source-register.csv`;
- claim/artifact rows to `evidence-log.csv`;
- one completion/blocker row to `run-log.csv`.

Use one `run_id`, ISO 8601 timestamps with timezone, Skill/rule/schema versions,
and a named human owner.

**Done when:** the brief and four linked CSV records contain no unsupported
facts and end with a human decision request.

## Rationalizations

| Shortcut | Required response |
| --- | --- |
| “Google usually works.” | Test and record it. Use a permitted fallback if blocked. |
| “The snippet confirms it.” | Open the source; snippets are not evidence. |
| “LinkedIn likely has the employee.” | Open a public page or mark unverified; leave access controls intact. |
| “The domain proves the company.” | Resolve the entity with multiple identifiers. |
| “I extracted the HTML, so no screenshot is needed.” | Official-site material claims require visible browser screenshots. |
| “The browser is unavailable, but the model knows the brand.” | Stop live verification and report the tooling blocker. |
| “Missing evidence probably means fraud.” | Absence or blocked access is not proof; label the limitation. |
| “The customer looks high value.” | Record the metric, formula, value, unit, and L threshold used. |
| “Profit margin is good.” | Clarify gross/contribution/net margin and cost basis; then apply the approved numeric rule. |
| “L3 means verified.” | Record L and V separately; L3+V0/V1 returns to verification. |
| “The chat summary is the record.” | Append the four CSV rows with `run_id`, timestamps, and versions. |

## Verification

- [ ] Purpose and entity are confirmed.
- [ ] Numeric metric/formula/L thresholds and rule version are confirmed.
- [ ] L business value and V verification are recorded separately.
- [ ] Required sources were tested, not assumed.
- [ ] Each source has claim scope and S grade.
- [ ] Search snippets were not used as final evidence.
- [ ] No LinkedIn/login/CAPTCHA/access control was bypassed.
- [ ] Official-site claims have visible screenshots, URLs, and timestamps.
- [ ] Facts, claims, conflicts, and unknowns are separated.
- [ ] Confidence reflects source and access limitations.
- [ ] All four CSV tables have linked, versioned rows.
- [ ] Final action is handed to a named human role.

## Act / retry

If evidence is incomplete, list the exact missing source, blocker, owner, and
next permitted action. Retry only after access or identifiers change.
