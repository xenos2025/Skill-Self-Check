---
name: skill-ship-safety
description: >-
  Audits whether a skill that sends email / WhatsApp or triggers other
  external actions is safe to run for real (安全真发): verifies documented
  commands actually exist, send gates are enforced in code rather than prose,
  and real sending is off by default. Returns a ship / stop-ship verdict.
  Use when the user asks 安全真发审计, 能不能真发, ship-safety review, or
  wants an intent-vs-implementation check before the first real send.
disable-model-invocation: true
---

# Skill Ship-Safety Check

Behavioral audit of a target skill: does the implementation honor what the
docs promise, and can it be trusted to touch the outside world? The output is
a **ship (放行)** or **stop-ship (停发)** verdict with evidence.

Complements `skill-self-check` (static structure audit). A skill can score
5/5 on structure while its send path is still unsafe — this skill audits that
gap. Run it **after** the structure audit passes.

**Authority split:** promise inventory, command existence, and external-action
scan = **script** ([scripts/ship_safety.py](scripts/ship_safety.py)).
Gate-bypass sandbox tests, default-off verification, and compliance wording =
**model**, following [references/gate-bypass.md](references/gate-bypass.md).
Script Critical findings and the stop-ship rule stay authoritative.

## When to use

- User asks 安全真发 / 能不能安全真发 / "ship-safety review" / "audit before real send"
- The target skill sends email or WhatsApp, calls external APIs, or mutates
  business data via scripts
- A structure audit passed but nobody has verified the code enforces the
  documented gates

## When NOT to use

- Structure / wording / contract audit — use `skill-self-check`
- Target skill has no scripts and no external actions — self-check is enough
- Legal compliance certification — this skill flags risky wording
  (CAN-SPAM, WhatsApp policy, unsourced numbers) but is not legal counsel

## Check axes

This audit always reports on:

- **Promise vs implementation** — every documented command exists and its
  subcommand is implemented (script)
- **Send gates in code** — blacklist / dedupe / per-day caps documented in
  prose are actually enforced by the send entrypoints (model, sandbox)
- **Default dry-run** — real SMTP / WhatsApp / API sending requires an
  explicit opt-in; guards exist and default to off (script hint + model)
- **Write-back integrity** — success and failure paths update the data layer;
  child-process errors are not silently swallowed (model)
- **Claims and compliance wording** — unsourced statistics and "compliant
  out of the box" claims are downgraded, not certified (model)

## Inputs

1. Absolute path to the target skill directory (must contain `SKILL.md`).
2. Confirm with the user that the audit may execute target scripts in a
   sandbox. Never point probes at production data or real credentials.

**Completion criterion:** target path known; sandbox execution approved.

## Process

### Pass 0 — Run the script (required)

```bash
python scripts/ship_safety.py /absolute/path/to/target-skill --pretty
```

Add `--exec` to probe each documented command inside a **sandbox copy of the
whole skill directory** with sanitized env (credentials stripped,
`DRY_RUN=1`), so scripts that write next to themselves cannot touch the
user's real files. Use `--exec` only after reviewing the inventory once
without it.

- Read stdout JSON as the source of truth for `commands`,
  `external_actions`, `counts`, and `verdict`.
- Exit code 1 means stop-ship — continue the review to explain why.

**Completion criterion:** JSON parsed; every `CMD.*` / `EXT.*` finding known.

### Pass 1 — Map script findings

Copy script findings into the report. `CMD.1` (missing script), `CMD.2`
(documented subcommand not implemented), `CMD.3` (probe rejected), and
`EXT.1` on SMTP/IMAP files are stop-ship Criticals. You may explain them;
you may not mark them passed.

**Completion criterion:** every script Critical appears with a fix suggestion.

### Pass 2 — Gate-bypass sandbox test (model)

Follow [references/gate-bypass.md](references/gate-bypass.md): build a temp
sandbox, seed poisoned fixtures (blacklisted address, recent-contact row,
duplicate domain), run the documented send entrypoint with `DRY_RUN=1`, and
verify every poisoned lead is blocked and not counted as sent.

**Completion criterion:** each documented gate has a tested pass/fail row;
any pass-through is recorded as Critical.

### Pass 3 — Write-back and failure paths (model)

Read the send entrypoints. Verify: a failed send is not recorded as sent;
child-process calls do not swallow errors (e.g. `check=False` with ignored
output); partial batches leave a recoverable state.

**Completion criterion:** each send entrypoint has a one-line verdict on its
failure path.

### Pass 4 — Claims and compliance wording (model)

Flag unsourced statistics ("99.5% bounce rate") and "compliant for listing"
claims lacking unsubscribe / sender-identity / opt-in mechanics. Suggest
downgraded wording; do not certify compliance.

**Completion criterion:** every flagged claim has a suggested rewrite.

### Verdict

- **Stop-ship** if any script Critical stands, any gate-bypass test let a
  poisoned lead through, or real sending is on by default.
- **Ship** only when all Criticals are resolved, gates held in the sandbox,
  and defaults verified off. List remaining Should-fix items as a watchlist.

## Write the report

Copy [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md). Fill every section. Keep the
script's `verdict` and counts verbatim; the model may only move the verdict
from ship to stop-ship (never the reverse).

**Completion criterion (skill done):** report contains the verdict, the
command inventory table, gate-bypass test results, and a fix list — and no
real message was sent during the audit.

## Verification

- [ ] `ship_safety.py` was executed on the target directory
- [ ] Report verdict and counts match the script JSON (or are stricter)
- [ ] Gate-bypass tests ran in a sandbox, never against production data
- [ ] No real email / WhatsApp / API call was made during the audit
- [ ] Every stop-ship reason cites evidence (file, line, or probe output)
- [ ] User was told the single next action: fix Criticals or ship

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "The docs describe the gate, that's enough" | Prose is not enforcement. Test the entrypoint with a poisoned fixture. |
| "DRY_RUN exists, so it's safe" | A guard that defaults to off-guard is a loaded gun. Verify the default. |
| "The structure audit scored 5/5" | Structure and send-safety are different audits. 5/5 structure ships unsafe code every day. |
| "Probing scripts is risky, skip it" | Unprobed promises are how `Unknown command` reaches production. Probe in the sandbox with stripped credentials. |
| "The stats are probably from real runs" | Unsourced numbers get downgraded wording, not benefit of the doubt. |

## Red Flags

- Writing a verdict without running the script
- Marking a `CMD.2` finding as passed because "the feature is planned"
- Running gate tests against the user's real data directory
- Leaving real credentials in the environment during `--exec` probes
- Calling a skill "ship" while any poisoned fixture passed through

## Out of scope

- Structure / contract scoring (that is `skill-self-check`)
- Editing the target skill unless the user explicitly asks
- Legal sign-off on CAN-SPAM / GDPR / WhatsApp Business policy
- Load, deliverability, or inbox-placement testing
