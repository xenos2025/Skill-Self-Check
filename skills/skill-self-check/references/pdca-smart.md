# PDCA + SMART for Agent Skills

Use this when auditing a target skill (Pass 5). Plain mapping — no slogans without evidence.

## PDCA (skill as a managed loop)

| Phase | What the skill must make explicit | Fail smell |
| --- | --- | --- |
| **Plan** | When / When NOT; named check axes; what success looks like before work starts | Jumps straight into tips; no scope |
| **Do** | Ordered steps (or apply-all rules) with **Done when** on each unit | Vibes-only process; no observable progress |
| **Check** | Verification with evidence (checkboxes, script output, screenshots, etc.) | "Looks good"; no proof |
| **Act** | How to correct course: Red Flags, Rationalizations, retry/fix path, or escalate | One-shot prose; failure has nowhere to go |

A skill can be short and still complete the loop. Missing **Check** or **Act** is the usual hole.

## SMART (goals / outcomes the skill steers toward)

Apply SMART to the skill's **outcome contract** (description + Done when + Verification), not to calendar OKRs unless the skill is literally time-boxed ops.

| Letter | Skill meaning | Fail smell |
| --- | --- | --- |
| **S**pecific | Clear WHAT + named check axes / deliverable shape | "Help with git / design / ops" |
| **M**easurable | Done when + Verification evidence an agent can observe | "Improve quality" with no metric or artifact |
| **A**chievable | When NOT + scope fits one skill; escape hatches for blockers | One skill promises an entire company transformation |
| **R**elevant | Triggers and steps match the user's job-to-be-done | Body drifts into unrelated encyclopedia |
| **T**ime-bound | **Run-bound exit**: each invocation has a finish line (Verification / ship floor / handoff). Prefer session exit criteria over fake calendar dates unless the domain needs them | Endless "keep refining" with no stop |

## How to score in the report (model)

Fill the PDCA×SMART matrix in [REPORT-TEMPLATE.md](../REPORT-TEMPLATE.md):

- Mark each cell `ok` / `weak` / `missing` with a one-line evidence quote
- Any **missing** Plan/Do/Check/Act → at least Should fix
- Missing Check on a workflow skill → Should fix (Critical if the skill claims a quality gate)
- SMART gaps usually attach to description, Done when, or Verification rewrites
