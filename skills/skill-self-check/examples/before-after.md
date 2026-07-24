# Before / After — weak commit helper

Use this pair to validate `skill-self-check`. Auditing **Before** should surface at least: weak description, missing verification, no-op lines, negation-heavy steering, and missing completion criteria.

---

## Before (intentionally weak)

Path for smoke: treat the block below as `bad-commit-helper/SKILL.md`.

```markdown
---
name: Helper
description: I can help you with git stuff when you need it.
---

# Helper

Git is important. Always be careful and think step by step.

## Tips

Don't write bad commit messages. Don't be vague. Don't forget the body.

Make things better. Improve the message. Understand the diff.

You can use conventional commits, or not, or just write something nice.
Sometimes before 2024 people used different formats — keep that in mind.

## Steps

1. Look at the changes
2. Write a message
3. Done
```

**Expected findings (minimum):**

| Finding | Pass | Sev |
|---------|------|-----|
| `name` invalid / ≠ directory | 1 | Critical |
| First-person description; no clear WHAT+WHEN | 1 | Critical |
| Steps lack checkable completion criteria | 2 | Should fix |
| "Be careful / think step by step" no-ops | 2 | Should fix |
| Negation cluster without positive target | 2 | Should fix |
| No Verification section | 3 | Should fix |
| No When NOT / rationalizations for a workflow | 3 | Should fix |
| Time-sensitive / vague multi-option advice | 4 | Should fix / Nice |

---

## After (acceptable v1)

```markdown
---
name: writing-commit-messages
description: >-
  Generates concise git commit messages from staged diffs using conventional
  commits. Use when the user asks for a commit message, reviews staged changes,
  or wants help wording a commit.
---

# Writing Commit Messages

## Overview

Turn a staged diff into one conventional-commit message the user can paste.

## When to Use

- User asks for a commit message or to "write the commit"
- Staged changes are ready and need a summary

### When NOT to use

- User wants to rewrite history / interactive rebase policy
- No diff available and user refuses to show changes

## Process

1. Read staged diff (`git diff --staged`). If empty, say so and stop.
   **Done when:** You have the full staged diff or an explicit empty-diff notice.
2. Draft one message: `type(scope): summary` plus optional body for why.
   **Done when:** Summary ≤72 chars, type from `feat|fix|docs|refactor|test|chore`, and body (if any) explains motivation not implementation dump.
3. Show message in a fenced block; do not commit unless asked.
   **Done when:** User-visible message block is the only proposed commit text.

Prefer positive shape: short summary that states the change; body explains why.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Diff is small, skip reading it" | Message quality comes from the diff. Read it. |
| "I'll commit for them" | Draft only unless they ask to commit. |

## Red Flags

- Message describes files not in the staged diff
- Summary restates "update code" with no intent
- Multiple unrelated concerns in one commit message without noting a split

## Verification

- [ ] Staged diff was read (or emptiness reported)
- [ ] Message matches conventional format above
- [ ] No commit ran unless the user asked
```

---

## Smoke procedure

1. Script (deterministic):

```bash
python skills/skill-self-check/scripts/hard_gates.py \
  skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty
```

Expect: `basic_usable` about 2/5, `ship_floor_met: false`, Critical on name/description; hints for no-op, negation, missing verification.

2. Full skill review: run `skill-self-check` in chat against the same fixture (or After example).
3. After fixture / After block: script Critical should be 0 for a cleaned skill; model may still suggest Nice polish.
