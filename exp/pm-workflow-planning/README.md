# exp/pm-workflow-planning (stub)

Status: **experiment / not a shippable skill yet.**

## Intent

Help a product or ops lead at a foreign-trade, factory, or ecommerce company:

1. **Interview with 5W2H** until the process is clear ([INTERVIEW.md](INTERVIEW.md))
2. Draw a minimal agent-ready workflow
3. Propose skills to build or reuse (with acceptance + evidence)
4. Hand drafts to `skill-self-check` before anyone installs them

## Method stack

| Layer | Use |
| --- | --- |
| **5W2H** | Client interview clarity (What/Why/Who/When/Where/How/How much) |
| **PDCA** | Interview loop + skill loop |
| **SMART** | Outcome contract for proposed skills |
| **skill-self-check** | Ship floor before install |

## Artifacts

```text
exp/pm-workflow-planning/
  README.md
  INTERVIEW.md                 # 5W2H intake (one question at a time)
  SKILL-PROPOSAL.template.md
  WORKFLOW-CANVAS.example.md   # TODO
  industries/                  # TODO example packs
```

## Entry criteria to leave `exp/`

- [ ] Interview uses 5W2H; every cell clear or explicit blocker
- [ ] Interview produces a workflow with named evidence per step
- [ ] Skill proposals include When / When-NOT / check axes + PDCA/SMART
- [ ] At least one real pilot (anonymized notes)
- [ ] Draft skill passes `hard_gates.py` ship floor
- [ ] Docs + CHANGELOG updated; folder moved under `skills/`

## Non-goals for this stub

- Running Shopify Admin writes
- Replacing vertical industry ops packs
- Storing live client data in git
