# Browser evidence and access gates

Use this reference when a proposed workflow depends on Google, LinkedIn,
official websites, public registries, or other live web sources.

Apply the L/S/V and CSV definitions from
[operational-data-contract.md](operational-data-contract.md). In short:
Google discovery starts at S1/V1; an opened browser page with screenshot, URL,
and timestamp can reach V2; V3 also needs fit-for-claim corroboration.

## Principle

Access is a runtime fact, not a model capability claim. Test the current
environment before promising coverage. A model’s memory, a search snippet, or a
plausible domain name is not evidence that a page is accessible or that a claim
is true.

## Capability matrix

Record this before live research:

| Source | Required for | Test method | Status | Evidence | Fallback / next action |
| --- | --- | --- | --- | --- | --- |
| Google Search | discovery | Run one harmless, relevant query | not tested | | |
| LinkedIn public page | company/person role corroboration | Open the public URL in a browser | not tested | | |
| Official company website | first-party claims | Open in a browser and capture visible content | not tested | | |
| Public registry | legal-entity facts | Open permitted official source | not tested | | |
| Browser screenshots | visual verification | Capture a test page | not tested | | |

Allowed status values:

- `verified accessible`;
- `verified blocked`;
- `tool unavailable`;
- `not tested`;
- `not required for this scope`.

Never convert `not tested` into `accessible` because another environment usually
supports it.

## Source-specific rules

### Google Search

1. Run a neutral query relevant to the target entity.
2. Record the exact query and test time.
3. Confirm that result links are visible and usable.
4. Treat snippets as leads, not as evidence.
5. Open the underlying source before citing a claim.

If Google is blocked or unavailable:

- do not claim that no information exists;
- try another permitted search source, direct official URLs, public registries,
  or user-provided documents;
- label Google coverage `not verified`;
- state how the missing source reduces confidence.

### LinkedIn

Use only pages available through the current authorized browser session.

- Never bypass login, CAPTCHA, rate limits, robots controls, or other access
  restrictions.
- Never ask the user to expose cookies or credentials.
- If the page redirects to login or an access challenge, record `verified
  blocked`.
- A search-result snippet that mentions LinkedIn does not verify the current
  company page, employee role, or employment dates.
- Keep personal-data collection limited to the legitimate business purpose.

### Official company website

For every material first-party claim:

1. Open the exact page in a real browser.
2. Wait until the relevant visible region has rendered.
3. Capture a screenshot showing the claim and enough surrounding context to
   identify the page.
4. Inspect what is visibly rendered. Do not infer the claim from the domain
   name, title, markup alone, or model memory.
5. Record the final URL, page title, capture time, screenshot path/attachment,
   and the observed wording in paraphrase.
6. Use DOM/text extraction as supporting evidence when available, not as a
   replacement for the screenshot.

If the page is blank, blocked, under construction, or only renders after an
unsupported interaction, report that state. Do not reconstruct likely content.

## Evidence ledger

Use one row per material claim:

| Claim | Source type | Final URL | Visible evidence / screenshot | Captured at + timezone | Confidence | Conflict / limitation |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

Persist the same information in `evidence-log.csv` and join it to the final
`run-log.csv` row with `run_id`.

Confidence guidance:

- **High:** first-party or official registry evidence, visibly verified, and
  corroborated where the risk warrants it.
- **Medium:** credible source with partial corroboration or a minor access gap.
- **Low:** single indirect source, unresolved entity match, stale evidence, or
  missing required source.
- **Unverified:** no accessible evidence. Do not phrase this as a fact.

## Conflict handling

When sources disagree:

1. Preserve both claims and their capture dates.
2. Prefer official registry facts for legal identity.
3. Prefer the company’s current visible site for its own current marketing
   claims, while labeling them first-party claims.
4. Ask for human judgment when the conflict affects credit, compliance,
   contracting, or account approval.

## Forbidden shortcuts

- Do not use model memory as a substitute for live access.
- Do not treat a screenshot as proof of facts that are not visibly present.
- Do not identify two companies as the same entity from name similarity alone.
- Do not hide a blocked source behind a confident summary.
- Do not collect sensitive personal data unrelated to the stated business
  purpose.
