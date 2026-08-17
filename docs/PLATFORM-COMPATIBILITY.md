# Platform compatibility

The audit method is portable; installation, automatic invocation, and trusted
execution are platform capabilities.

## Capability levels

| Level | Platform capability | Available workflow |
| --- | --- | --- |
| A | Chat/file upload only | User supplies a work package, `SKILL.md`, or previously generated report for explanation |
| B | Read files + Python 3.10+ | Work-readiness, static contract, and safety checks |
| C | Native skill discovery | Level B plus platform-specific installation/invocation guidance |
| D | Trusted isolated runner | Controlled behavioral fixtures in addition to static scans |

Level B is the portable core. A platform without Level D must report behavior
as `not_safely_verified`; a temporary directory does not raise the capability
level.

The independently installed core exposes the default Level-B entry:

```bash
python path/to/skill-self-check/scripts/hard_gates.py \
  /path/to/target-skill --pretty
```

It runs the fast deterministic core gate and does not require the other two
Skills. It does not execute the target Skill.

When the user explicitly requests the full static pack, `run_full_audit.py`
adds static safety and optional work-readiness source JSON. Its output directory
must be outside the target and source repository.

## Portable result contract

Script results include:

- `schema_version`
- `audit_level`
- `target_platform`
- `gate_verdict` and `gate_reasons` for hard-gate reports
- `limitations`
- `execution` for safety scans

Readiness reports add `level`, `gates`, and `next_quest`.

Platform adapters may add metadata, but they must not change `gate_verdict`,
core scores, finding IDs, or a stricter verdict into a looser one.

All three shipped `SKILL.md` files use the common `name` and `description`
frontmatter contract. Platform-specific discovery metadata belongs in an
adapter or `agents/` file instead of changing deterministic scoring.

## Current platform matrix

This table is for pack maintainers. It is not a Skill pass/fail bar.

| Platform | Status | Notes |
| --- | --- | --- |
| Cursor | Maintainer-tested | Primary authoring and Level B/C workflow |
| Codex | Maintainer-tested | Second supported authoring environment |
| WorkBuddy | Maintainer-tested (smoke) | China-market discovery smoke only |
| Claude Code | Not tested yet | Candidate for a later adapter / discovery check |
| Coze | Not tested yet | China-market candidate; install/invoke adapter TBD |

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
