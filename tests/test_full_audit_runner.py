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
            self.assertEqual(
                manifest["checks"]["package_health"],
                "valid_skill_package",
            )
            self.assertEqual(
                manifest["audit_execution"]["status"],
                "observed",
            )
            self.assertGreaterEqual(
                manifest["audit_execution"]["duration_ms"],
                0,
            )
            personal = json.loads(
                (output / "personal-profile.json").read_text(encoding="utf-8")
            )
            project = json.loads(
                (output / "project-profile.json").read_text(encoding="utf-8")
            )
            self.assertEqual(personal["default_view"], "growth")
            self.assertEqual(project["default_view"], "detection")
            self.assertEqual(project["sources"]["behavior"], "not_supplied")
            self.assertIn(
                "没有把静态声明当作行为验证",
                " ".join(project["limitations"]),
            )
            metrics = project["skill_engineering"]["operational_metrics"]
            self.assertEqual(
                metrics["token_consumption"]["status"],
                "estimated",
            )
            self.assertGreater(
                metrics["token_consumption"]["estimated_input_tokens"],
                0,
            )
            self.assertEqual(
                metrics["runtime_duration"]["status"],
                "not_measured",
            )
            self.assertEqual(
                project["audit_execution"]["duration_ms"],
                manifest["audit_execution"]["duration_ms"],
            )
            self.assertIn(
                "sample-skill",
                (output / "personal-scorecard.html").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "Token 消耗",
                (output / "project-scorecard.html").read_text(encoding="utf-8"),
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
            project = json.loads(
                (output / "project-profile.json").read_text(encoding="utf-8")
            )
            personal = json.loads(
                (output / "personal-profile.json").read_text(encoding="utf-8")
            )
            manifest = json.loads(
                (output / "audit-manifest.json").read_text(encoding="utf-8")
            )
            html = (output / "project-scorecard.html").read_text(
                encoding="utf-8"
            )

        self.assertEqual(project["verdict"], "invalid_skill_package")
        self.assertEqual(
            project["skill_engineering"]["status"],
            "invalid_package",
        )
        self.assertIsNone(project["skill_engineering"]["level"])
        self.assertEqual(personal["default_view"], "detection")
        self.assertEqual(
            manifest["checks"]["package_health"],
            "invalid_skill_package",
        )
        self.assertIn("package-health-banner", html)
        self.assertIn("不是标准 Skill 包 · 暂停成熟度评分", html)
        self.assertIn("局部文件诊断", html)
        self.assertNotIn('"level": {"id": "Lv', html)

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
