# Platform compatibility

The audit method is portable; installation, automatic invocation, and trusted
execution are platform capabilities.

## Capability levels

| Level | Platform capability | Available workflow |
| --- | --- | --- |
| A | Chat/file upload only | User supplies a work package, `SKILL.md`, or previously generated report for explanation |
| B | Read files + Python 3.10+ | Work-readiness, static contract, safety, and offline scorecard generation |
| C | Native skill discovery | Level B plus platform-specific installation/invocation guidance |
| D | Trusted isolated runner | Controlled behavioral fixtures in addition to static scans |

Level B is the portable core. A platform without Level D must report behavior
as `not_safely_verified`; a temporary directory does not raise the capability
level.

The installed four-Skill pack exposes one Level-B entry:

```bash
python path/to/skill-self-check/scripts/run_full_audit.py \
  /path/to/target-skill \
  --out-dir /private/path/target-skill-audit \
  --pretty
```

It runs static structure and safety checks and creates separate personal and
project HTML scorecards. It does not execute the target Skill. The output
directory must be outside the target and its source repository.

## Portable result contract

Script results include:

- `schema_version`
- `audit_level`
- `target_platform`
- `limitations`
- `execution` for safety scans

Readiness reports add `level`, `gates`, and `next_quest`. Growth profiles add
`profile_schema_version`, two independent progress lines, `sources`, and one
prioritized next quest. The HTML is only a local view of that profile JSON.

Platform adapters may add metadata, but they must not change core scores,
finding IDs, or a stricter verdict into a looser one.

All four shipped `SKILL.md` files use the common `name` and `description`
frontmatter contract. Platform-specific discovery metadata belongs in an
adapter or `agents/` file instead of changing deterministic scoring.

## Current platform matrix (maintainer / advanced audit)

This table is for **pack maintainers and the advanced-audit author track**.
It is **not** an enterprise Skill pass/fail bar: business authors do not need
to understand every Agent platform to build a usable Skill employee.

Maintainer smoke (files + Python + skill discovery) is separate from comparable
two-platform SHA-256 proof below.

| Platform | Status | Notes |
| --- | --- | --- |
| Cursor | Maintainer-tested | Primary authoring and Level B/C workflow |
| Codex | Maintainer-tested | Second platform candidate for comparable evidence pairs |
| WorkBuddy | Maintainer-tested (smoke) | China-market; comparable fingerprint pair still optional advanced audit |
| Claude Code | Not tested yet | Candidate for a later adapter / discovery check |
| Coze | Not tested yet | China-market candidate; install/invoke adapter TBD |

**Advanced-audit comparable pair (optional):** Cursor + Codex (or another
verified pair) using the **same** contract file and sanitized fixture.
Enterprise scorecards stay on ship floor + static safety without this pair.

## Comparable two-platform proof (advanced audit only)

Cross-platform **author** maturity requires more than two platform labels.
Every eligible record must have:

- a distinct platform `name`;
- `status: verified`;
- a shareable evidence reference;
- the same `contract_id` in `sha256:<64 lowercase hex>` form;
- the same `fixture_id` in that form.

The contract fixes inputs, outputs, stop rules, permissions, and acceptance
checks. The sanitized fixture fixes the test case. Platform adapters and model
versions may differ, but they must not silently replace either file. Different
models on one platform do not count as two platforms. See
[`platform-evidence.md`](../skills/skill-growth-scorecard/references/platform-evidence.md).

## Capability check before an audit

Record whether the current environment can:

1. Read the target directory.
2. Run Python 3.10+.
3. Write reports or only return them in chat.
4. Discover/invoke skills automatically.
5. Provide trusted isolation with network denial, writable-file boundaries,
   environment allowlisting, and process/time limits.

When a capability is missing, degrade explicitly instead of pretending the
platform provides it.
