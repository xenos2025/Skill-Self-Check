# Gate-bypass sandbox test (model-owned, Pass 2)

Goal: prove that the gates the target skill documents (blacklist, dedupe,
recent-contact cooldown, per-day cap, channel exclusivity) are enforced by
the **send entrypoints**, not just described in prose.

## Hard rules

1. **Never** run against the user's real data directory or credentials.
2. Every probe runs with `DRY_RUN=1` (or the target's equivalent) **and**
   credential env vars stripped. Two layers, because one may be broken —
   that is exactly what this test measures.
3. A single poisoned lead passing through = Critical = stop-ship. No
   averaging.

## Procedure

1. **Build the sandbox.** Create a temp directory. Copy the target's
   `scripts/` into it. Create the data files the scripts expect (read the
   target's data schema from its docs or script source).
2. **Seed poisoned fixtures.** One row per documented gate, e.g.:
   - `blocked@fixture.test` in the blacklist file
   - `recent@fixture.test` contacted yesterday (inside the cooldown window)
   - `dupe@fixture.test` sharing a domain with an existing contact
   - a contact marked as WhatsApp-only (or the target's channel-exclusive flag)
3. **Prepare the input batch.** A JSON/CSV batch containing every poisoned
   lead plus one clean lead (`clean@fixture.test`).
4. **Run the documented send entrypoint** from the sandbox directory:

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
