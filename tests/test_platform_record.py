#!/usr/bin/env python3
"""Regression tests for comparable platform evidence records."""

from __future__ import annotations

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
    / "skill-growth-scorecard"
    / "scripts"
    / "platform_record.py"
)


def run_record(*args: str | Path) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        capture_output=True,
        check=False,
    )
    return result.returncode, json.loads(result.stdout.decode("utf-8"))


class PlatformRecordTests(unittest.TestCase):
    def test_same_contract_and_fixture_create_comparable_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contract = root / "contract.json"
            fixture = root / "fixture.json"
            contract.write_text('{"output":"summary"}\n', encoding="utf-8")
            fixture.write_text('{"input":"sanitized"}\n', encoding="utf-8")
            code_a, record_a = run_record(
                "--platform",
                "Platform A",
                "--contract",
                contract,
                "--fixture",
                fixture,
                "--evidence",
                "evidence/a.json",
            )
            code_b, record_b = run_record(
                "--platform",
                "Platform B",
                "--contract",
                contract,
                "--fixture",
                fixture,
                "--evidence",
                "evidence/b.json",
            )
        self.assertEqual(code_a, 0, record_a)
        self.assertEqual(code_b, 0, record_b)
        self.assertEqual(record_a["status"], "needs_review")
        self.assertEqual(record_a["contract_id"], record_b["contract_id"])
        self.assertEqual(record_a["fixture_id"], record_b["fixture_id"])
        self.assertRegex(record_a["contract_id"], r"^sha256:[0-9a-f]{64}$")

    def test_verified_requires_explicit_review_note(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contract = root / "contract.json"
            fixture = root / "fixture.json"
            contract.write_text("{}", encoding="utf-8")
            fixture.write_text("{}", encoding="utf-8")
            code, payload = run_record(
                "--platform",
                "Platform A",
                "--contract",
                contract,
                "--fixture",
                fixture,
                "--evidence",
                "evidence/a.json",
                "--verified",
            )
        self.assertEqual(code, 2)
        self.assertIn("--review-note", payload["error"])

    def test_absolute_local_evidence_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contract = root / "contract.json"
            fixture = root / "fixture.json"
            contract.write_text("{}", encoding="utf-8")
            fixture.write_text("{}", encoding="utf-8")
            code, payload = run_record(
                "--platform",
                "Platform A",
                "--contract",
                contract,
                "--fixture",
                fixture,
                "--evidence",
                "C:\\private\\run.json",
            )
        self.assertEqual(code, 2)
        self.assertIn("不能使用本机绝对路径", payload["error"])


if __name__ == "__main__":
    unittest.main()
