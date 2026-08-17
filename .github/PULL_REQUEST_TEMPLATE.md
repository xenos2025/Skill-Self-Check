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
- [ ] `python tests/test_hard_gates.py`
- [ ] `python tests/test_ship_safety.py`
- [ ] `python tests/test_readiness_gates.py`
- [ ] `python tests/test_full_audit_runner.py`
- [ ] Fixture run (if scoring changed):
      `python skills/skill-self-check/scripts/hard_gates.py skills/skill-self-check/examples/fixtures/bad-commit-helper --pretty`
- [ ] Business and technical reports share the same counts, finding IDs, and conclusion
- [ ] CHANGELOG `[Unreleased]` updated when user-visible

## Notes

<!-- Paste script score summary for scoring PRs -->
