---
name: skill-growth-scorecard
description: >-
  Combines readiness, hard-gate, ship-safety, and optional advanced-audit
  behavior JSON into offline personal and project scorecards for building
  usable business Skill employees. Use when users want a growth type, level,
  enterprise next practice, suite audit scorecard, or printable offline result
  without changing the audited Skill.
---

# Skill Growth Scorecard

Create one friendly growth profile from several independent checks. Preserve the
original audit facts. Default narrative helps enterprises build **usable
business Skill employees** — clear triggers, steps, acceptance, stop rules —
not multi-platform certification engineering.

Present the growth view as a personal capability profile based on the current
work sample; keep project delivery verdicts in detection and technical evidence
rather than turning them into personal labels.

## When to use

- Someone finished a business Skill draft and wants a plain scorecard: can we
  trial it, what’s the one next practice.
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
- Treating missing advanced-audit behavior JSON as “the Skill failed enterprise use”
  when the enterprise mainline gate already passed.
- Replacing a missing behavior test with model confidence.
- Publishing a real client report inside this open-source repository.
- Executing the audited Skill or its external actions.

## Check axes

- **Enterprise mainline** — package health, ship floor, static safety, plain
  next practice (trial one real scenario / tighten acceptance).
- **Advanced audit (optional)** — behavior JSON, failure recovery, portable
  contract, two-platform fingerprints; shown in `advanced_audit`, not as the
  default next quest.
- **Business readiness** — B0–B6 and the first failed gate.
- **Package health** — the Skill must be one installable, portable package
  before any Lv0–Lv5 or type is displayed.
- **Skill maturity** — Lv0–Lv5; Lv3+ are author-track unlocks.
- **Skill type** — six versioned dimensions.
- **Next quest** — enterprise practice after the enterprise-ready gate; advanced steps stay
  under `advanced_audit.next_quest`.
- **Personal learning quest** — separate from project remediation.
- **View agreement** — growth, detection, and technical evidence stay aligned.
- **Capability vs delivery** — personal language stays separate from project status.
- **Token consumption** — estimated static input or trusted observed usage,
  shown separately from evidence coverage and levels.
- **Runtime duration** — trusted target-run timing or an explicit
  `not_measured` state.
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
   Read `hard_gates.package_health` before computing Skill maturity. When it is
   invalid, preserve raw diagnostics but emit `skill_engineering.status =
   invalid_package`, `level = null`, null dimension states, no capability badge,
   and the root verdict `invalid_skill_package`.
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
- Static floor plus static safety pass can reach Lv2 — **enterprise mainline
  “ready enough to trial”**.
- Root `verdict` is `ready_for_controlled_use` when package health is
  assessable, ship floor and the contract minimum are met, static safety passes,
  and Critical count is zero. Missing behavior JSON is an advanced-audit note,
  not an enterprise fail.
- Root `next_quest` after that enterprise-ready gate is enterprise practice
  (real scenario / acceptance / materials). Author steps live in
  `advanced_audit.next_quest`.
- Lv3+ (advanced audit): core-flow + PDCA behavior evidence; Lv4 adds failure
  recovery and applicable safety controls; Lv5 adds portable contract + two
  verified platforms with the same SHA-256 contract/fixture IDs.

Read the complete schema and type rules in
[`references/profile-contract.md`](references/profile-contract.md).
Use [`references/platform-evidence.md`](references/platform-evidence.md) only
for **advanced audit** comparable platform evidence.

## Output contract

The generator returns one JSON fact set. The HTML embeds that same JSON and
renders:

1. Growth Profile — personal capability type and stage, original Skill
   character, six single-direction evidence-coverage axes, strengths, badges,
   a concrete `personal_interpretation`, and a personal learning quest; it does not show
   project delivery verdict badges or product-explanation meta copy;
2. Detection Results — project source scores, informational token/runtime
   metrics, delivery status, lifecycle, highest-priority remediation, findings,
   and filters;
3. Technical Evidence — ruleset, sources, execution status, limitations, JSON.

All views render the package-health banner before score content. An invalid
package must say that maturity is paused; the detection view may show raw source
scores only with a partial-diagnostic label.

Whole-suite profiles additionally render an audited Skill matrix, test summary,
snapshot basis, project conclusion, and verified qualitative findings. Suite
aggregation uses the weakest shipped Skill for each static score, so a weak or
blocking Skill stays visible in the suite result.

All three views show or preserve the analyzed `subject`. Printed and saved
scorecards must remain attributable to one Skill or work process.
Axis percentages are a visual translation of the existing 0–4 evidence state,
not personality probabilities, complementary gap scores, or a new combined
score. The only displayed percentage is the current evidence coverage; 100%
means that dimension's declared full-evidence criteria are met within the
current rules and test scope.
Token consumption and runtime duration are not seventh and eighth evidence
axes: they remain quantitative operational metrics, and profile type, level,
verdict, and ship floor are computed independently of them.

Persistent comparison is **N/A** inside this stateless generator. A caller may
store previous profile JSON in an approved private workspace and compare it in a
future invocation.

## Verification

- [ ] Every available source report was produced by its script.
- [ ] Missing reports remain `not_started` or `needs_confirmation`.
- [ ] `stop_ship` is visible in detection and technical evidence, caps the
      engineering-derived ability level, and is not shown as a personal badge.
- [ ] No behavior evidence means no Lv3 or higher (advanced audit); enterprise
      `ready_for_controlled_use` may still hold at Lv2.
- [ ] Root `next_quest` is enterprise practice after the enterprise-ready gate;
      advanced steps appear only under `advanced_audit`.
- [ ] `not_applicable` is accepted only with its required scope and integrity
      evidence; omission counts as missing evidence.
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
- [ ] Invalid package health suppresses levels, types, badges, and delivery-pass
      language while preserving raw diagnostics.
- [ ] Token and runtime values preserve `estimated` / `observed` /
      `not_measured` status, and levels and verdicts hold without them.
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
| “Static pass proves the workflow works.” | Enterprise may trial at Lv2; advanced audit still needs behavior evidence for Lv3+. |
| “Missing behavior JSON means the Skill failed.” | If the enterprise-ready gate passed, say ready for controlled use and park author evidence under advanced audit. |
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
