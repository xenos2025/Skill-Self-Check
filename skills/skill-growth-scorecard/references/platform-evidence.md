# Comparable platform evidence

Use this contract when one Skill is tested on different AI or Agent platforms.
The goal is to compare the platform behavior, not two different test setups.

## What must stay the same

Both runs must use byte-for-byte identical:

1. **contract file** — the stable inputs, outputs, stop rules, permissions, and
   acceptance checks expected from the Skill;
2. **sanitized fixture** — the same fake or approved test input;
3. **acceptance method** — the same assertions and severity rules.

Hash the contract and fixture with SHA-256. A platform record is eligible only
when both identifiers use `sha256:` followed by 64 lowercase hexadecimal
characters.

The bundled helper computes both identifiers without running a platform:

```bash
python scripts/platform_record.py \
  --platform "Agent Platform A" \
  --contract evidence/portable-contract.json \
  --fixture evidence/sanitized-fixture.json \
  --evidence evidence/platform-a-run.json \
  --out evidence/platform-a-record.json \
  --pretty
```

The default status is `needs_review`. After a trusted runner or reviewer checks
the items below, rerun with `--verified --review-note "reviewed assertion set
and isolation log"` or update the record through the same controlled review
process.

## What may differ

- platform and adapter name;
- model name or version;
- platform-native invocation and tool wiring;
- timestamps, latency, and diagnostic logs.

These differences belong in the evidence record. They must not silently change
the contract, fixture, or expected result.

## Minimum record

```json
{
  "name": "Agent Platform A",
  "status": "verified",
  "evidence": "evidence/platform-a-run.json",
  "contract_id": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "fixture_id": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
}
```

Recommended evidence fields include `model`, `adapter_version`, `run_at`,
`result_digest`, passed and failed assertions, isolation controls, and a
redacted diagnostic summary.

## Verification rule

A trusted runner or reviewer may set `status: verified` only after confirming:

- the platform invoked the intended Skill and adapter;
- the saved contract and fixture hashes match the record;
- no real customer secrets are present;
- external actions stayed inside the declared test boundary;
- every acceptance assertion has an explicit result;
- the evidence reference is shareable and is not a workstation-local absolute
  path.

Two records unlock cross-platform credit only when their platform names are
distinct and both `contract_id` and `fixture_id` are identical. Different
models on one platform can be useful extra evidence, but they do not count as
two Agent platforms.

## Failure handling

Keep failed runs. Mark them `failed` or `needs_review`, explain the failed
assertion, and do not rewrite them as verified. Fix the Skill or adapter, rerun
the **same** contract and fixture, and save the new record separately.
