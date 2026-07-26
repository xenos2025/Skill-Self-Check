#!/usr/bin/env python3
"""Integration checks for the ordinary-user one-command audit entry."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO
    / "skills"
    / "skill-self-check"
    / "scripts"
    / "run_full_audit.py"
)


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def write_target(root: Path) -> Path:
    target = root / "sample-skill"
    target.mkdir()
    (target / "SKILL.md").write_text(
        """---
name: sample-skill
description: Reviews a sample workflow when a user asks for a local check.
---

# Sample Skill

## When to use

Use for a local sample review.

## When NOT to use

Do not use for external sends.

## Process

1. Read the supplied sample.
2. Return a plain-language summary.

## Verification

- [ ] Summary names the supplied sample.
- [ ] No external action was performed.
""",
        encoding="utf-8",
    )
    return target


class FullAuditRunnerTests(unittest.TestCase):
    def test_one_command_writes_two_views_without_changing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = write_target(root)
            output = root / "private-report"
            before = tree_digest(target)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(target),
                    "--out-dir",
                    str(output),
                    "--pretty",
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertEqual(tree_digest(target), before)
            expected = {
                "audit-manifest.json",
                "hard-gates.json",
                "ship-safety.json",
                "behavior.json",
                "personal-profile.json",
                "project-profile.json",
                "personal-scorecard.html",
                "project-scorecard.html",
            }
            self.assertEqual({path.name for path in output.iterdir()}, expected)
            manifest = json.loads(
                (output / "audit-manifest.json").read_text(encoding="utf-8")
            )
            self.assertTrue(manifest["target"]["unchanged"])
            self.assertEqual(manifest["audit_mode"], "read_only_static")
            personal = json.loads(
                (output / "personal-profile.json").read_text(encoding="utf-8")
            )
            project = json.loads(
                (output / "project-profile.json").read_text(encoding="utf-8")
            )
            self.assertEqual(personal["default_view"], "growth")
            self.assertEqual(project["default_view"], "detection")
            self.assertIn(
                "sample-skill",
                (output / "personal-scorecard.html").read_text(encoding="utf-8"),
            )

    def test_report_is_refused_inside_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = write_target(Path(temp_dir))
            output = target / "audit-report"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(target),
                    "--out-dir",
                    str(output),
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertIn("不能放在被检查的 Skill 里面", payload["error"])
            self.assertFalse(output.exists())

    def test_report_is_refused_inside_source_repository(self) -> None:
        target = REPO / "skills" / "skill-self-check"
        output = REPO / "private-audit-output"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(target),
                "--out-dir",
                str(output),
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertIn("源码仓库外", payload["error"])
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
