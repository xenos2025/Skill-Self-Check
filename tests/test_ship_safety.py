#!/usr/bin/env python3
"""Regression tests for skills/skill-ship-safety/scripts/ship_safety.py (stdlib only).

Run:
  python tests/test_ship_safety.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "skill-ship-safety" / "scripts" / "ship_safety.py"
BAD_FIXTURE = (
    REPO / "skills" / "skill-ship-safety" / "examples" / "fixtures" / "promise-gap"
)
SELF_CHECK_SKILL = REPO / "skills" / "skill-self-check"

GOOD_SKILL_MD = """---
name: good-cli
description: Fixture with a fully implemented documented command. Use when testing.
---

# Good CLI

```bash
python3 scripts/tool.py ping <host>
```
"""

GOOD_TOOL_PY = '''#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "ping":
        print("pong")
    else:
        print(f"Unknown command: {sys.argv[1:] or ''}")

if __name__ == "__main__":
    main()
'''


def run_script(target: Path, *flags: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(target), *flags],
        capture_output=True,
    )
    payload = json.loads(proc.stdout.decode("utf-8"))
    return proc.returncode, payload


class BadFixtureTests(unittest.TestCase):
    def test_promise_gap_stops_ship(self) -> None:
        code, report = run_script(BAD_FIXTURE)
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "stop_ship")
        ids = [f["id"] for f in report["findings"]]
        self.assertIn("CMD.1", ids, "missing script must be flagged")
        self.assertIn("CMD.2", ids, "unimplemented subcommand must be flagged")
        self.assertIn("EXT.1", ids, "smtplib without dry-run guard must be flagged")
        crit_ids = [f["id"] for f in report["findings"] if f["severity"] == "critical"]
        self.assertIn("CMD.2", crit_ids)
        self.assertIn("EXT.1", crit_ids)

    def test_exec_probe_detects_unknown_command(self) -> None:
        # confirm_win is caught statically (CMD.2), so probe the static-pass
        # path: check_lead should probe fine.
        code, report = run_script(BAD_FIXTURE, "--exec")
        checked = {
            (c["script"], c["subcommand"]): c for c in report["commands"]
        }
        probe = checked[("scripts/ops.py", "check_lead")]["probe"]
        self.assertTrue(probe["ran"])
        self.assertFalse(probe["unknown_command"])


class CleanTargetTests(unittest.TestCase):
    def test_fully_implemented_command_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "good-cli"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(GOOD_SKILL_MD, encoding="utf-8")
            (skill / "scripts" / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            code, report = run_script(skill, "--exec")
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["verdict"], "pass_with_watchlist")
        cmd = report["commands"][0]
        self.assertTrue(cmd["script_exists"])
        self.assertTrue(cmd["subcommand_implemented"])
        self.assertFalse(cmd["probe"]["unknown_command"])

    def test_self_check_skill_has_no_criticals(self) -> None:
        code, report = run_script(SELF_CHECK_SKILL)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["counts"]["critical"], 0)

    def test_missing_skill_md_stops_ship(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_script(Path(tmp))
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "stop_ship")
        self.assertEqual(report["findings"][0]["id"], "CMD.0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
