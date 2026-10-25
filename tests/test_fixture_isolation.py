"""Maintainer fixtures must never be discoverable as installable skills."""
from pathlib import Path
import unittest

REPO = Path(__file__).resolve().parents[1]


class FixtureIsolationTests(unittest.TestCase):
    def test_only_product_skill_entrypoints_are_installable(self):
        discovered = {p.relative_to(REPO / "skills").as_posix()
                      for p in (REPO / "skills").rglob("SKILL.md")}
        self.assertEqual(discovered, {
            "agent-work-readiness/SKILL.md",
            "skill-self-check/SKILL.md",
            "skill-ship-safety/SKILL.md",
        })

    def test_bad_fixtures_remain_available_to_maintainers(self):
        for name in ("bad-commit-helper", "promise-gap"):
            self.assertTrue((REPO / "tests/fixtures" / name / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
