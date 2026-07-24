## Summary

<!-- Why this change exists -->

## Type

- [ ] Skill behavior (`skills/`)
- [ ] Hard-gate script
- [ ] Docs / OSS packaging
- [ ] Experiment only (`exp/`)
- [ ] Installer / plugin metadata

## Test plan

- [ ] `python skills/skill-self-check/scripts/hard_gates.py skills/skill-self-check --pretty`
- [ ] Fixture run (if scoring changed):
      `python skills/skill-self-check/scripts/hard_gates.py skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty`
- [ ] CHANGELOG `[Unreleased]` updated when user-visible

## Notes

<!-- Paste script score summary for scoring PRs -->
