---
name: pm-workflow-planning
description: >-
  Generates an evidence-backed business workflow and an Agent Skill proposal by
  interviewing operators and product owners. Use when a foreign-trade,
  manufacturing, engineering, or ecommerce team asks to 梳理流程, 盘点岗位工作,
  design a repeatable business workflow, or decide which Skills to build before
  drafting or installing them.
---

# PM Workflow Planning

Turn one messy business process into a confirmed workflow and a Skill proposal.
This is an experiment: keep the run to planning artifacts. Execute the business
process, edit stable `skills/`, or promote a draft only after an explicit user
request.

## When to use

- A business owner can describe the work but not an agent-ready process.
- A team needs roles, handoffs, evidence, exceptions, and acceptance criteria
  clarified before building Skills.
- A live-research workflow needs explicit source-access and browser-evidence
  gates.

## When NOT to use

- Reviewing a finished Skill: use `skill-self-check`.
- Performing the proposed workflow immediately.
- Gathering private personal data, bypassing access controls, or storing client
  secrets in this repository.
- Combining several unrelated processes in one interview.

## Check axes

- Process scope and intended decision.
- Appropriate selection of L/S/V/R business-experience modules.
- Measurable target, formula, threshold, owner, and scoring version when L is selected.
- Runtime capability and evidence access.
- Source fitness (`S1–S3`) and verification strength (`V0–V3`).
- Roles, handoffs, approvals, and exceptions.
- Completion criteria and evidence produced by each step.
- Machine-readable run/evidence records when R is selected or an existing log is reused.
- Automation boundary and human decision ownership.
- Skill proposal contract and promotion gate.

## Operating contract

1. Ask one question at a time and wait for the answer.
2. For every decision question, give a recommended answer, the reason, and the
   main alternative. Let the user confirm or correct it.
3. Look up discoverable facts with available tools instead of asking the user.
   Treat business goals, risk tolerance, ownership, and approval as user
   decisions.
4. Record unsupported or inaccessible facts as `unknown — blocker`. Keep gaps
   open until evidence replaces model memory or “industry common sense.”
5. Draft the Skill proposal only after the user confirms the workflow summary.

## Inputs

- One target process.
- Company/industry lens.
- Desired business outcome or failure to prevent.
- Known systems, roles, source restrictions, and approval boundaries.

**Done when:** the target process is named narrowly enough to interview, or the
first one-question prompt is ready.

## Process

### Pass 0 — Scope and module-selection gate

Name the process and its intended decision or deliverable.

Read
[references/operational-data-contract.md](references/operational-data-contract.md).
Judge L/S/V/R applicability. If the decision is clear from the process, select
modules and explain why. If it is unclear, ask one question with a recommended
selection and wait.

Use `N/A — <reason>` for skipped modules. Skipping a module with a clear reason
is not a defect and must not be converted into a self-check finding.

**Done when:** L/S/V/R each has `Y`, `N`, or `Ask user`, with a reason.

### Pass 1 — Conditional measurable goal gate

When L is selected, require the user to confirm metric, formula, unit,
direction, owner, L1/L2/L3 thresholds, allowed action, and
`score_rule_version`. Propose numeric defaults when helpful, then wait for
confirmation. Keep business value L separate from verification strength V.

When L is skipped, write a qualitative completion criterion and the N/A reason.

**Done when:** L rules are reproducible, or L is explicitly N/A.

### Pass 2 — Conditional source and capability gate

When S or V is selected for live web research, read
[references/browser-evidence.md](references/browser-evidence.md). Test and
record whether the current environment can access each required source. Start
Google, LinkedIn, company websites, registries, and browser capabilities in the
`not tested` state.

When S is selected, create the source register. Assign S1/S2/S3 by claim
fitness, not prestige. Google search remains S1 discovery until the underlying
source is opened.

**Done when:** selected source/verification modules have their contracts, or
S/V is explicitly N/A.

### Pass 3 — Interview one branch at a time

Follow [INTERVIEW.md](INTERVIEW.md). Resolve 5W2H cells in dependency order:

1. What and Why.
2. Who and approval.
3. Trigger, deadline, and handoffs.
4. Systems, evidence, exceptions, and volume.

For each question:

1. Ask one question.
2. Provide a recommended answer based on confirmed context.
3. Explain what would change the recommendation.
4. Wait for confirmation or correction.

**Done when:** each 5W2H cell is concrete or has an explicit blocker, owner, and
follow-up time.

### Pass 4 — Build the workflow

Copy [WORKFLOW-CANVAS.template.md](WORKFLOW-CANVAS.template.md). For every step,
name:

- trigger and input;
- responsible role and approval;
- action and system/tool;
- selected metric/source/evidence/record fields, if applicable;
- completion criterion;
- exception and escalation path.

Read the workflow back to the user. Continue only after explicit confirmation.

**Done when:** the user confirms the workflow and every step has evidence plus
a completion criterion.

### Pass 5 — Propose Skills

Copy [SKILL-PROPOSAL.template.md](SKILL-PROPOSAL.template.md). Separate:

- reusable generic discipline;
- company-specific policy or data;
- live tool/integration requirements;
- selected L/S/V/R rules and artifacts; N/A reasons for skipped modules;
- work that must remain a human decision;
- build, reuse, or buy choices.

Split independently triggered roles or materially different permissions into
separate Skills instead of a large all-in-one Skill.

**Done when:** each proposed Skill has WHAT, WHEN, When NOT, inputs, outputs,
check axes, a run-bound exit, and only the applicable L/S/V/R contracts.

### Pass 6 — Draft and hand off

Only after the user confirms the proposal:

1. Draft the approved Skill in the requested location.
2. Run `skill-self-check`.
3. Keep the draft experimental until the ship floor passes and a real,
   anonymized pilot has been recorded.

**Done when:** the proposal is handed off, blockers are explicit, and no
unapproved execution or promotion occurred.

## Rationalizations and required advice

| Rationalization | Required judgment and advice |
| --- | --- |
| “Google should be available.” | Test it. Record the query, result, and time. If blocked, use another permitted source and label Google coverage unverified. |
| “LinkedIn probably has the company.” | Open only a publicly accessible page. If login, CAPTCHA, or an access challenge appears, stop and record the blocker with access controls intact. |
| “The search snippet tells us enough.” | Treat snippets as discovery only. Open the underlying source before using a claim. |
| “The official website looks normal.” | Open it in a real browser, capture a screenshot of the relevant visible content, and attach the URL and capture time. |
| “HTML/text extraction is enough.” | Use extraction as support. For official-site claims, visual browser evidence is required; the screenshot must show the claimed content. |
| “No browser tool is available, but I can infer it.” | Mark live verification blocked. Produce a research plan or request a connected browser/source export. |
| “Good customers are L3.” | If L applies, define the metric, formula, unit, exact thresholds, owner, and scoring version. |
| “The margin is high.” | If L applies, name the margin type and cost basis, then record the observed numeric value and rule used. |
| “One score is enough.” | If L and V apply, keep business value L separate from verification V; high potential with weak evidence still needs verification. |
| “We can remember the result in chat.” | If R applies, write the selected records to the approved CSV/log or map them to an existing system. |
| “Every enterprise Skill needs all four modules.” | Select L/S/V/R independently. Use N/A with a reason when a module adds no decision, evidence, or learning value. |
| “This is standard industry practice.” | Ask for the company’s actual role, system, evidence, exception, and approval path. |
| “We can start researching while the scope is fuzzy.” | Resolve the intended decision first; sales qualification, credit risk, compliance, and meeting preparation need different evidence. |

## Verification

- [ ] One target process was used.
- [ ] L/S/V/R applicability was judged or asked once with a recommendation.
- [ ] Skipped modules have an N/A reason and are not treated as defects.
- [ ] If L is selected, metrics, formulas, thresholds, owner, and version are confirmed.
- [ ] If L and V are selected, business value and verification strength remain separate.
- [ ] Questions were asked one at a time with recommendations.
- [ ] Facts were looked up; decisions were confirmed by the user.
- [ ] Live-source capabilities were tested rather than assumed.
- [ ] If S is selected, each source has a claim-specific S grade and runtime status.
- [ ] Official-site claims have browser screenshots, URLs, and capture times.
- [ ] Blocked sources are explicit; no login/CAPTCHA/access control was bypassed.
- [ ] Every workflow step has role, evidence, exception, and Done when.
- [ ] If R is selected, the selected records or equivalent existing system fields are defined.
- [ ] The user confirmed the workflow before a Skill proposal was drafted.
- [ ] The proposal separates automated work from human decisions.

## Example

Use
[examples/customer-background-investigation/PROCESS-BRIEF.example.md](examples/customer-background-investigation/PROCESS-BRIEF.example.md)
to see the full path from a foreign-trade background-investigation request to a
workflow, proposal, and draft Skill.
