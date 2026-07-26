# Gate-bypass isolated test plan (conditional Pass 2)

Goal: prove that the gates the target skill documents (blacklist, dedupe,
recent-contact cooldown, per-day cap, channel exclusivity) are enforced by
the **send entrypoints**, not just described in prose.

This file is a test plan, not a local execution instruction. Run it only
inside a trusted isolation runner supplied by the current platform or CI.
A temporary directory, copied project, `DRY_RUN=1`, or stripped environment
alone does not prevent network access or writes elsewhere.

## Hard rules

1. If trusted isolation is unavailable, do not run the target. Report
   `未完成安全验证`.
2. The runner must block network access by default, expose only fixture files
   as writable, pass environment variables by allowlist, and enforce process
   and time limits.
3. **Never** mount the user's real data directory or credentials.
4. Every probe also uses `DRY_RUN=1` (or the target's equivalent). This is an
   application guard, not a replacement for isolation.
5. A single poisoned lead passing through = Critical = stop-ship. No
   averaging.

## Procedure

1. **Prepare an isolated workspace.** Inside the trusted runner, copy the
   target's `scripts/` and create only the fixture data files the scripts
   expect.
2. **Seed poisoned fixtures.** One row per documented gate, e.g.:
   - `blocked@fixture.test` in the blacklist file
   - `recent@fixture.test` contacted yesterday (inside the cooldown window)
   - `dupe@fixture.test` sharing a domain with an existing contact
   - a contact marked as WhatsApp-only (or the target's channel-exclusive flag)
3. **Prepare the input batch.** A JSON/CSV batch containing every poisoned
   lead plus one clean lead (`clean@fixture.test`).
4. **Run the documented send entrypoint** inside the trusted runner. The
   following commands assume the runner has already enforced the hard rules:

```powershell
$env:DRY_RUN = "1"
Remove-Item Env:SMTP_*, Env:IMAP_* -ErrorAction SilentlyContinue
python scripts/<sender>.py batch.json
```

```bash
DRY_RUN=1 SMTP_HOST= SMTP_USER= SMTP_PASS= python3 scripts/<sender>.py batch.json
```

5. **Assert, per poisoned lead:**
   - it was skipped or rejected (visible in output), and
   - it was **not** recorded as sent in the data layer afterwards.
   The clean lead may proceed (as a dry-run preview).
6. **Failure-path check.** Re-run with the clean lead only and credentials
   still stripped: the send must fail, and the data layer must **not** record
   it as sent. If the entrypoint reports success while the child call failed,
   record it as a write-back Critical (Pass 3 evidence).

## Reporting

| Gate | Fixture | Expected | Observed | Result |
|------|---------|----------|----------|--------|
| blacklist | blocked@fixture.test | skipped, not recorded | … | pass / FAIL |

Any FAIL row → Critical finding with the exact command and output line
pasted as evidence.
