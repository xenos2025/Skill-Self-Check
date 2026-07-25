# exp/pm-workflow-planning

Status: **working experiment / not a shippable skill yet.**

## Intent

Help a product or ops lead at a foreign-trade, factory, or ecommerce company:

1. **Interview with 5W2H** until the process is clear ([INTERVIEW.md](INTERVIEW.md))
2. Draw a minimal agent-ready workflow
3. Propose skills to build or reuse (with acceptance + evidence)
4. Hand drafts to `skill-self-check` before anyone installs them

The experimental entry point is [SKILL.md](SKILL.md). Live-web workflows must
also follow [references/browser-evidence.md](references/browser-evidence.md):
access is tested, and official-site facts require real-browser screenshots.
For recurring business decisions, evidence, or history, selectively apply
[references/operational-data-contract.md](references/operational-data-contract.md):
L value, S source, V verification, and R record modules are judged separately.
A justified N/A is valid and is not a general self-check failure.

## Method stack

| Layer | Use |
| --- | --- |
| **5W2H** | Client interview clarity (What/Why/Who/When/Where/How/How much) |
| **PDCA** | Interview loop + skill loop |
| **SMART** | Outcome contract for proposed skills |
| **Conditional L/S/V/R** | Optional value / source / verification / record modules |
| **skill-self-check** | Ship floor before install |

## Artifacts

```text
exp/pm-workflow-planning/
  SKILL.md
  README.md
  INTERVIEW.md                 # 5W2H intake (one question at a time)
  SKILL-PROPOSAL.template.md
  WORKFLOW-CANVAS.template.md
  assets/templates/
    score-rules.csv
    source-register.csv
    evidence-log.csv
    run-log.csv
  references/
    browser-evidence.md
    operational-data-contract.md
  examples/
    customer-background-investigation/
```

## Entry criteria to leave `exp/`

- [ ] Interview uses 5W2H; every cell clear or explicit blocker
- [ ] Interview produces a workflow with named evidence per step
- [ ] Skill proposals include When / When-NOT / check axes + PDCA/SMART
- [ ] L/S/V/R applicability is judged; skipped modules have a reason
- [ ] Selected modules have versioned rules/evidence/records or an existing-system mapping
- [ ] At least one real pilot (anonymized notes)
- [ ] Draft skill passes `hard_gates.py` ship floor
- [ ] Docs + CHANGELOG updated; folder moved under `skills/`

## Non-goals for this stub

- Running Shopify Admin writes
- Replacing vertical industry ops packs
- Storing live client data in git
- Bypassing login, CAPTCHA, rate limits, or other access controls
