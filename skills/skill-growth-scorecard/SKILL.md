---
name: skill-growth-scorecard
description: Combines readiness, hard-gate, ship-safety, and optional behavior JSON into deterministic offline personal and project scorecards. Use when users want a Skill growth type and level, a suite audit scorecard, one next quest, or a printable offline result without changing the audited Skill.
---

# Skill Growth Scorecard

Create one friendly growth profile from several independent checks. Preserve the
original audit facts. Present the growth view as a personal capability profile
based on the current work sample; keep project delivery verdicts in detection
and technical evidence rather than turning them into personal labels.

## When to use

- `readiness_gates.py` has produced a business-readiness JSON report.
- `hard_gates.py` or `ship_safety.py` has produced a Skill audit JSON report.
- A beginner needs a plain-language type, level, strength, and next quest.
- A technical reviewer needs the original scores, findings, evidence, and limits.
- The user wants one offline HTML result with growth, detection, and evidence views.
- A repository owner wants one personal capability scorecard and one project
  delivery scorecard covering every direct product Skill under `skills/`.

## When NOT to use

- Inventing a score without running the applicable deterministic scripts.
- Treating a Skill type as the author's personality.
- Replacing a missing behavior test with model confidence.
- Publishing a real client report inside this open-source repository.
- Executing the audited Skill or its external actions.

## Check axes

- **Business readiness** — B0–B6 and the first failed gate.
- **Skill maturity** — Lv0–Lv5 with hard caps for missing safety or behavior evidence.
- **Skill type** — six versioned engineering dimensions.
- **Next quest** — first blocking business or engineering gate.
- **Personal learning quest** — separate from project remediation.
- **View agreement** — growth, detection, and technical evidence stay aligned.
- **Capability vs delivery** — personal language stays separate from project status.
- **Privacy** — no full local path, secret, or customer detail in the share layer.
- **Browser behavior** — tabs, filters, evidence, print, desktop, and mobile.

## Inputs

All inputs are optional individually, but at least one is required:

- `readiness-result.json` from `agent-work-readiness`;
- `hard-gates.json` from `skill-self-check`;
- `ship-safety.json` from `skill-ship-safety`;
- optional behavior evidence described in
  [`references/profile-contract.md`](references/profile-contract.md).
- optional `--subject-name` when the report metadata does not contain a safe,
  recognizable Skill or work-process name.

**Done when:** the supplied JSON files parse and their assessment types are known.

## Process

1. **Run the source checks.**
   Run only the checks that have valid inputs. Mark unavailable reports as not supplied.
   **Done when:** each available report is saved as UTF-8 JSON.

2. **Generate the profile.**

   ```bash
   python scripts/profile_engine.py \
     --readiness readiness-result.json \
     --hard-gates hard-gates.json \
     --ship-safety ship-safety.json \
     --subject-name example-skill \
     --out-json growth-profile.json \
     --out-html growth-scorecard.html \
     --pretty
   ```

   Omit unavailable options. Normally the Skill name comes from
   `hard_gates.frontmatter.name`; use `--subject-name` only as an explicit
   override. The generator is stateless and does not execute the target Skill.
   **Done when:** profile JSON and optional HTML are written without parse errors.

   For the shipped Skill suite itself, use the suite runner. Keep the output
   outside the public repository:

   ```bash
   python scripts/suite_scorecards.py /path/to/skill-repo \
     --out-dir /private/deliverables/current-suite \
     --pretty
   ```

   It reruns hard gates, safety scans, and repository regression tests, then
   produces separate `personal-scorecard.html` and `project-scorecard.html`.
   The personal file opens on Growth; the project file opens on Detection.
   **Done when:** both files identify the suite and the project view lists every
   shipped Skill with the same source scores.

3. **Read the two growth lines separately.**
   - Business readiness explains whether the work can be delegated.
   - Skill capability stage explains what the creator has demonstrated through a
     structured, tested, controlled, and portable implementation.
   Keep them as two independent progress lines.
   **Done when:** both lines show a level or an explicit `not_started` state.

4. **Check the type and next quest.**
   Type is a positive description of the creator's strongest evidenced
   Skill-building pattern, not a personality claim.
   The next quest comes from the first blocking gate, with business readiness
   taking priority before real delegation.
   **Done when:** the type has evidence and the next quest has an acceptance rule.

5. **Open the HTML in a browser.**
   Verify Growth Profile, Detection Results, and Technical Evidence. Check filters,
   keyboard focus, mobile layout, print styles, console, and external requests.
   **Done when:** the page has no horizontal overflow or console error.

6. **Store the report safely.**
   Real scorecards belong in a private deliverables folder outside a public repo.
   A share card may use only whitelisted summary fields.
   **Done when:** no report or screenshot containing client information is staged.

## Level contract

- No Skill audit: engineering state is `not_started`, not a failure.
- `stop_ship`: engineering maturity is capped at Lv1.
- Static floor plus static safety pass can reach Lv2.
- Lv3 requires explicit core-flow and PDCA behavior evidence.
- Lv4 requires failure recovery plus evidence for every applicable safety
  control. A genuinely inapplicable external-action or write-back control needs
  explicit scope evidence; write-back N/A also needs `target_unchanged=true`.
- Lv5 requires a portable contract and at least two verified platform records
  that share the same contract and fixture SHA-256 identifiers.

Read the complete schema and type rules in
[`references/profile-contract.md`](references/profile-contract.md).
Use [`references/platform-evidence.md`](references/platform-evidence.md) when
preparing comparable evidence on a second Agent platform.

## Output contract

The generator returns one JSON fact set. The HTML embeds that same JSON and
renders:

1. Growth Profile — personal capability type and stage, original Skill
   character, six single-direction evidence-coverage axes, strengths, badges,
   a concrete `personal_interpretation`, and a personal learning quest; it does not show
   project delivery verdict badges or product-explanation meta copy;
2. Detection Results — project source scores, delivery status, lifecycle,
   highest-priority remediation, findings, and filters;
3. Technical Evidence — ruleset, sources, execution status, limitations, JSON.

Whole-suite profiles additionally render an audited Skill matrix, test summary,
snapshot basis, project conclusion, and verified qualitative findings. Suite
aggregation uses the weakest shipped Skill for each static score; it never
averages away a weak or blocking Skill.

All three views show or preserve the analyzed `subject`. Printed and saved
scorecards must remain attributable to one Skill or work process.
Axis percentages are a visual translation of the existing 0–4 evidence state,
not personality probabilities, complementary gap scores, or a new combined
score. The only displayed percentage is the current evidence coverage; 100%
means that dimension's declared full-evidence criteria are met within the
current rules and test scope.

Persistent comparison is **N/A** inside this stateless generator. A caller may
store previous profile JSON in an approved private workspace and compare it in a
future invocation.

## Verification

- [ ] Every available source report was produced by its script.
- [ ] Missing reports remain `not_started` or `needs_confirmation`.
- [ ] `stop_ship` is visible in detection and technical evidence, caps the
      engineering-derived ability level, and is not shown as a personal badge.
- [ ] No behavior evidence means no Lv3 or higher.
- [ ] `not_applicable` is accepted only with its required scope and integrity
      evidence; omission never becomes a free pass.
- [ ] Two-platform credit uses distinct platform names with the same
      `contract_id` and `fixture_id`.
- [ ] Type, level, badge, and next quest rules are deterministic.
- [ ] `personal_interpretation` states a demonstrated capability, current
      stage, and evidence-based growth priorities; the HTML does not compose
      its own assessment.
- [ ] The Growth view teaches a capability through `learning_quest`; it does
      not display finding IDs or tell the person to repair a project command.
- [ ] The Detection view still displays the root project `next_quest`.
- [ ] Growth and audit views use the same counts and finding IDs.
- [ ] The header, technical evidence, and JSON identify the analyzed subject.
- [ ] HTML contains no external font, CDN, tracker, or network dependency.
- [ ] Full local paths and client details are not placed in the share layer.
- [ ] Desktop, mobile, filters, tabs, evidence, console, and print are checked.
- [ ] The audited Skill was not modified or executed.
- [ ] Whole-suite reports were written outside the source repository and the
      personal/project files default to Growth/Detection respectively.

## Common rationalizations

| Rationalization | Required response |
| --- | --- |
| “The type looks advanced, so it can ship.” | Delivery follows safety and behavior gates, not the type. |
| “No Skill exists, so give it Lv0.” | Use `not_started`; continue the business-readiness next quest. |
| “Static pass proves the workflow works.” | Stop at Lv2 until behavior evidence exists. |
| “One total score is easier.” | Keep business and engineering levels separate. |
| “The HTML can calculate the level.” | Calculate in Python; HTML only renders JSON. |
| “A full path helps technical users.” | Keep full paths in private source reports, not the profile/share layer. |
| “Put the project red light on the personal card.” | Keep the personal card about demonstrated capability; show the unchanged verdict in detection and technical evidence. |

## Red Flags

- Showing a level without the underlying script JSON
- Promoting past Lv2 without behavior evidence
- Averaging suite scores so a weak Skill disappears
- Writing real client reports into the public repository
- Putting full local paths or secrets into the share layer
- Treating Skill type as the author's personality or as ship approval

## Example

Use the sanitized inputs under
[`examples/fixtures/basic-profile`](examples/fixtures/basic-profile)
to generate a profile without accessing a real Skill or customer process.
