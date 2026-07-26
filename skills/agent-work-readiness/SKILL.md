---
name: agent-work-readiness
description: Guides beginners and teams from verbal, repeated work into a scored Agent-ready work package with clear goals, workflow, roles, standards, permissions, exceptions, and learning evidence. Use when users want to 梳理流程, turn口头约定 into SOP, clarify overlapping department responsibilities, define measurable completion, prepare an Agent employee, or assess whether one business process is ready to become a Skill.
---

# Agent Work Readiness

Turn one loosely described business process into a confirmed, machine-checkable
work package. Keep this business-readiness assessment separate from the
engineering audit of the final Skill.

## When to use

- The user relies on oral instructions, repeated chat, or personal memory.
- A process has unclear goals, steps, owners, approvals, or completion standards.
- Several departments appear to own the same work.
- The user wants an Agent employee but cannot yet describe a delegable job.
- A previous Skill audit shows that the upstream business process is still vague.

## When NOT to use

- Reviewing the structure or safety of a finished Skill: use `skill-self-check`
  and `skill-ship-safety`.
- Combining several unrelated company processes in one assessment.
- Inventing company policy, owners, targets, or approvals without confirmation.
- Executing the proposed business process or sending external messages.
- Storing secrets, credentials, customer PII, or private transcripts in this pack.

## Check axes

- Goal clarity: process, outcome, reason, trigger, and explicit boundary.
- Workflow clarity: ordered inputs, actions, outputs, and completion criteria.
- Role clarity: owners, approvers, handoffs, and duplicate responsibility.
- Measurable standards: formula, unit, direction, threshold, and metric owner.
- Delegation control: allowed work, forbidden work, human approval, exceptions,
  and escalation.
- Learning evidence: pilot records, evidence artifacts, retrospective, and version.

## Inputs

- One narrowly named business process.
- The people or roles currently doing and approving the work.
- Existing examples, forms, spreadsheets, messages, or system records when safe.
- An approved private workspace for the generated work package.

Use
[`assets/work-readiness.template.json`](assets/work-readiness.template.json)
as the canonical record. Read
[`references/readiness-contract.md`](references/readiness-contract.md)
before changing fields or interpreting B0–B6.

**Done when:** one process is selected and the first unanswered gate is known.

## Process

1. **Name one process.**
   Ask what visible result should exist when the work is finished. Reject broad
   answers such as “日常运营”.
   **Done when:** process name, intended outcome, reason, trigger, and out-of-scope
   boundary are confirmed.

2. **Ask 5W2H one question at a time.**
   Give a recommended answer and its reason, then let the user confirm or correct
   it. Keep unknown facts open as `unknown — blocker`.
   **Done when:** What, Why, Who, When, Where, How, and How much are concrete or
   have an owner for follow-up.

3. **Write the workflow.**
   For every step record input, action, output, responsible role, Done when, and
   exception. Convert only concrete work, rather than slogans, into steps.
   **Done when:** the user can read the steps in order and recognizes the real
   work.

4. **Separate responsibilities.**
   Record what each role owns, what it approves, and what it must not own.
   Add handoff deliverables and acceptance rules when more than one role is used.
   **Done when:** every step has one responsible role and every handoff has one
   accepting role.

5. **Make completion measurable.**
   Record at least one metric with formula, unit, direction, threshold, and owner.
   Use an explicit qualitative rule only when a numeric metric is genuinely not
   applicable, and explain why.
   **Done when:** two people applying the same rule reach the same pass/fail result.

6. **Define the Agent boundary.**
   List allowed actions, forbidden actions, human approval points, step-level
   exceptions, and escalation. Keep irreversible or high-impact decisions human.
   **Done when:** the Agent knows what it may do, what it must stop before doing,
   and who decides next.

7. **Record learning evidence.**
   After approved pilots, link relative evidence artifacts and write a
   retrospective. Claim B6 only from local, reviewable evidence.
   **Done when:** two pilot records and one retrospective artifact can be found
   inside the private work package.

8. **Run the deterministic assessment.**

   ```bash
   python scripts/readiness_gates.py <work-package-or-json> --pretty
   ```

   The script reports B0–B6, six gate states, badges, findings, and one next
   quest. It does not call a model or execute the business process.
   **Done when:** the JSON result parses and the user understands the next gate.

9. **Decide the handoff.**
   - Below B5: continue process clarification.
   - At B5: draft an Agent job description or Skill proposal.
   - At B6: keep pilot evidence and then audit the drafted Skill separately.
   **Done when:** the next action is confirmed and no premature automation began.

## Output contract

Return:

1. `work-readiness.json` in the user's approved private workspace;
2. the `readiness_gates.py` JSON result;
3. a plain-language summary with current level, strengths, first blocked gate,
   and next quest;
4. explicit unknowns and who will resolve them.

Persistent state lives in the user's work package, not this repository. Preserve
`schema_version`, process identity, confirmed decisions, and evidence paths
between runs. Prefer the structured answer over retaining raw transcripts.

## Verification

- [ ] Exactly one process was assessed.
- [ ] The work package contains no credentials or customer PII.
- [ ] The user confirmed business decisions; the model did not invent them.
- [ ] Each workflow step has input, action, output, owner, Done when, and exception.
- [ ] Duplicate or overlapping responsibility is resolved or remains an open blocker.
- [ ] Metrics include a reproducible standard or an explained N/A.
- [ ] Agent permissions, forbidden actions, approval, and escalation are explicit.
- [ ] Pilot evidence uses relative paths inside the private work package.
- [ ] The reported B level comes from `readiness_gates.py`.
- [ ] A finished Skill is sent to the engineering audit instead of being self-approved.

## Common rationalizations

| Rationalization | Required response |
| --- | --- |
| “大家都知道怎么做。” | Ask for ordered steps, owner, output, and Done when. |
| “这个部门一起负责。” | Name one responsible role and one approving role. |
| “做好就行，不用数字。” | Define an observable pass rule; add a number where the work supports one. |
| “Agent 先做起来再说。” | Reach B5 before real delegation. |
| “试过几次，应该算稳定。” | Link pilot evidence and a retrospective before B6. |
| “把所有流程一次录进去。” | Assess one process per work package. |

## Red Flags

- Writing B5/B6 without `readiness_gates.py` JSON
- Inventing owners, approvals, or metrics the user never confirmed
- Assessing more than one process in a single work package
- Storing credentials, PII, or raw private transcripts in the package
- Drafting a Skill before the first blocked gate below B5 is resolved

## Examples

- Beginner fixture:
  [`examples/fixtures/oral-process/work-readiness.json`](examples/fixtures/oral-process/work-readiness.json)
- Agent-ready fixture:
  [`examples/fixtures/agent-ready/work-readiness.json`](examples/fixtures/agent-ready/work-readiness.json)
