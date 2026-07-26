---
name: skill-ship-safety
description: >-
  Audits static safety evidence for a skill that sends email / WhatsApp or
  triggers other external actions (安全真发): verifies documented commands
  exist, identifies external-action code, and records whether trusted isolated
  behavior tests remain unverified. Returns a static pass / stop / unverified
  result without executing target code.
  Use when the user asks 安全真发审计, 能不能真发, ship-safety review, or
  wants an intent-vs-implementation check before the first real send.
---

# Skill Ship-Safety Check

Preflight audit of a target skill: does the static implementation evidence
honor what the docs promise, and what still needs trusted behavior testing?
The built-in script performs static inspection only. Its output distinguishes
**static pass**, **stop-ship**, and **execution unverified**.

Complements `skill-self-check` (static structure audit). A skill can score
5/5 on structure while its send path is still unsafe — this skill audits that
gap. Run it **after** the structure audit passes.

**Authority split:** promise inventory, command existence, and external-action
scan = **script** ([scripts/ship_safety.py](scripts/ship_safety.py)). Gate-bypass
tests require a separately supplied trusted isolation runner; default-off
verification and compliance wording stay model-owned, following
[references/gate-bypass.md](references/gate-bypass.md). A temporary directory
alone is not a sandbox. Script stop-ship findings stay authoritative.

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
  prose are actually enforced by the send entrypoints (trusted isolated test)
- **Default dry-run** — real SMTP / WhatsApp / API sending requires an
  explicit opt-in; guards exist and default to off (script hint + model)
- **Write-back integrity** — success and failure paths update the data layer;
  child-process errors are not silently swallowed (model)
- **Claims and compliance wording** — unsourced statistics and "compliant
  out of the box" claims are downgraded, not certified (model)

## Inputs

1. Absolute path to the target skill directory (must contain `SKILL.md`).
2. Record whether the current platform provides a trusted isolation runner
   that blocks network access, limits writable files, strips credentials by
   allowlist, and enforces process/time limits.

**Completion criterion:** target path known; isolation capability recorded as
available or unavailable.

## Process

### Pass 0 — Run the script (required)

```bash
python scripts/ship_safety.py /absolute/path/to/target-skill --pretty
```

The compatibility flag `--exec` does **not** run target code. It returns
`execution_unverified` and explains that a separately supplied trusted runner
is required. Only such a runner satisfies the behavior-test step; a temporary
directory or sanitized environment is insufficient.

- Read stdout JSON as the source of truth for `commands`,
  `external_actions`, `execution`, `counts`, and `verdict`.
- Exit code 1 means stop-ship or requested execution was not safely verified;
  continue the review to explain which one.

**Completion criterion:** JSON parsed; every `CMD.*` / `EXT.*` finding known.

### Pass 1 — Map script findings

Copy script findings into the report. `CMD.1` (missing script), `CMD.2`
(documented subcommand not implemented), and `EXT.1` on SMTP/IMAP files are
stop-ship Criticals. `EXEC.0` means execution was requested but intentionally
not performed. You may explain findings; you may not mark them passed.

**Completion criterion:** every script Critical appears with a fix suggestion.

### Pass 2 — Gate-bypass isolated test (conditional)

Follow [references/gate-bypass.md](references/gate-bypass.md) only when a
trusted isolation runner is available. Seed poisoned fixtures (blacklisted
address, recent-contact row, duplicate domain), run the documented entrypoint
inside that runner, and verify every poisoned lead is blocked and not counted
as sent. If trusted isolation is unavailable, record **未完成安全验证** and do
not execute the target.

**Completion criterion:** either each documented gate has a tested pass/fail
row from a trusted runner, or the report explicitly says behavior was not
safely verified. Any pass-through is recorded as Critical.

### Pass 3 — Write-back and failure paths (model)

Read the send entrypoints. Verify: a failed send is recorded as failed;
child-process calls propagate errors (flag `check=False` with ignored output);
partial batches leave a recoverable state.

**Completion criterion:** each send entrypoint has a one-line verdict on its
failure path.

### Pass 4 — Claims and compliance wording (model)

Flag unsourced statistics ("99.5% bounce rate") and "compliant for listing"
claims lacking unsubscribe / sender-identity / opt-in mechanics. Suggest
downgraded wording and keep legal certification out of the report.

**Completion criterion:** every flagged claim has a suggested rewrite.

### Verdict

- **Stop-ship** if any script Critical stands, an isolated gate-bypass test let
  a poisoned lead through, or real sending is on by default.
- **Execution unverified（未完成安全验证）** when static checks pass but no
  trusted isolated behavior evidence exists. This is not ship approval.
- **Ship** only when all Criticals are resolved, every gate held in a trusted
  isolated runner, and defaults were verified off. List remaining watch items.

## Write the report

Create both reports from the same script result:

- [REPORT-BUSINESS-TEMPLATE.md](REPORT-BUSINESS-TEMPLATE.md) — plain-language
  version for non-technical readers.
- [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md) — technical evidence and
  reproduction version.

Keep the script's counts and finding IDs identical in both reports. The script
sets the least-strict verdict the model may use.

**Completion criterion (skill done):** both reports contain the same result
and next action; the technical report contains command inventory and evidence;
no target program or real message was executed by the built-in audit.

## Verification

- [ ] `ship_safety.py` was executed on the target directory
- [ ] Both report verdicts, counts, and finding IDs match
- [ ] Trusted isolation availability is stated explicitly
- [ ] Gate-bypass tests ran only in a trusted isolated runner, or are marked unverified
- [ ] No real email / WhatsApp / API call was made during the audit
- [ ] Every stop-ship reason cites evidence (file, line, or isolated-run output)
- [ ] User was told one next action: fix blockers, obtain isolated evidence, or ship

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "The docs describe the gate, that's enough" | Prose is not enforcement. Test the entrypoint with a poisoned fixture. |
| "DRY_RUN exists, so it's safe" | A guard that defaults to off-guard is a loaded gun. Verify the default. |
| "The structure audit scored 5/5" | Structure and send-safety are different audits. 5/5 structure ships unsafe code every day. |
| "A temporary copy is a sandbox" | A copied directory does not block network or writes elsewhere. Use trusted isolation or mark execution unverified. |
| "The stats are probably from real runs" | Unsourced numbers get downgraded wording, not benefit of the doubt. |

## Red Flags

- Writing a verdict without running the script
- Marking a `CMD.2` finding as passed because "the feature is planned"
- Running target code from the built-in audit or a plain temporary directory
- Running gate tests against the user's real data directory or credentials
- Calling a skill "ship" while any poisoned fixture passed through
- Calling static pass "safe to send" without trusted isolated evidence

## Out of scope

- Structure / contract scoring (that is `skill-self-check`)
- Editing the target skill unless the user explicitly asks
- Legal sign-off on CAN-SPAM / GDPR / WhatsApp Business policy
- Load, deliverability, or inbox-placement testing
