#!/usr/bin/env python3
"""Integration checks for the full static-audit entry."""

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
READINESS_FIXTURE = (
    REPO
    / "skills"
    / "agent-work-readiness"
    / "examples"
    / "fixtures"
    / "agent-ready"
    / "work-readiness.json"
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
description: Reviews a supplied sample workflow. Use when the user requests a local check.
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

## Review axes

- Input identity: the response names the supplied sample.
- Action boundary: the response performs no external action.
""",
        encoding="utf-8",
    )
    return target


class FullAuditRunnerTests(unittest.TestCase):
    def test_one_command_writes_source_reports_without_changing_target(self) -> None:
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
            }
            self.assertEqual({path.name for path in output.iterdir()}, expected)
            manifest = json.loads(
                (output / "audit-manifest.json").read_text(encoding="utf-8")
            )
            self.assertTrue(manifest["target"]["unchanged"])
            self.assertEqual(manifest["audit_mode"], "read_only_static")
            self.assertEqual(
                manifest["checks"]["package_health"],
                "valid_skill_package",
            )
            self.assertEqual(manifest["checks"]["core_gate"], "pass")
            self.assertEqual(
                manifest["audit_execution"]["status"],
                "observed",
            )
            self.assertGreaterEqual(
                manifest["audit_execution"]["duration_ms"],
                0,
            )
            hard = json.loads(
                (output / "hard-gates.json").read_text(encoding="utf-8")
            )
            self.assertEqual(hard["gate_verdict"], "pass")
            safety = json.loads(
                (output / "ship-safety.json").read_text(encoding="utf-8")
            )
            self.assertIsInstance(safety, dict)

    def test_work_package_adds_readiness_source_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = write_target(root)
            output = root / "private-report"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(target),
                    "--out-dir",
                    str(output),
                    "--work-package",
                    str(READINESS_FIXTURE),
                    "--pretty",
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            readiness = json.loads(
                (output / "readiness.json").read_text(encoding="utf-8")
            )
            manifest = json.loads(
                (output / "audit-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(readiness["level"]["id"], "B5")
            self.assertEqual(
                manifest["checks"]["business_readiness"],
                "completed",
            )

    def test_invalid_package_is_reported_without_a_maturity_level(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "workspace"
            target.mkdir()
            (target / "SKILL.md").write_text(
                """---
name: actual-skill
description: Reviews local assets when a user requests a package check.
---

# Actual Skill

## When to use

Use when local assets need review.

## When NOT to use

Do not use for external sends.

## Process

1. Read `assets/missing.png`.
2. Write results under `D:\\old-workspace\\outputs`.

## Verification

- [ ] The local package was checked.
""",
                encoding="utf-8",
            )
            (target / "actual-skill").mkdir()
            outputs = target / "outputs"
            outputs.mkdir()
            (outputs / "generated.png").write_bytes(b"x" * 100)
            output = root / "private-report"
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
            hard = json.loads(
                (output / "hard-gates.json").read_text(encoding="utf-8")
            )
            manifest = json.loads(
                (output / "audit-manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(
            hard["package_health"]["status"],
            "invalid_skill_package",
        )
        self.assertEqual(hard["gate_verdict"], "invalid_skill_package")
        self.assertEqual(
            manifest["checks"]["package_health"],
            "invalid_skill_package",
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
