#!/usr/bin/env python3
"""Regression tests for role/Prompt behavior-evidence validation."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PRODUCT_SKILL = REPO / "skills" / "skill-self-check"
SCRIPT = PRODUCT_SKILL / "scripts" / "role_prompt_behavior_check.py"
EXAMPLE = PRODUCT_SKILL / "examples" / "role-prompt-behavior.example.json"


def run_check(record: dict) -> tuple[int, dict]:
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "behavior.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    return result.returncode, json.loads(result.stdout)


def example_record() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


class RolePromptBehaviorCheckTests(unittest.TestCase):
    def test_same_fixture_with_preserved_global_outcome_is_unchanged(self) -> None:
        code, report = run_check(example_record())

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("unchanged", report["behavior_verdict"])
        self.assertEqual("eligible", report["release_recommendation"])
        self.assertEqual("none", report["gate_effect"])

    def test_single_context_cannot_be_implemented_by_subagents(self) -> None:
        record = example_record()
        record["candidate"]["agent_count"] = 3
        record["candidate"]["implicit_delegation"] = True
        code, report = run_check(record)

        self.assertEqual(1, code)
        self.assertEqual("regressed", report["behavior_verdict"])
        self.assertIn("RPB.1", {item["id"] for item in report["findings"]})

    def test_loss_of_global_objective_blocks_release(self) -> None:
        record = example_record()
        check = next(item for item in record["checks"] if item["id"] == "global_objective")
        check["candidate"] = "fail"
        check["evidence"] = "Candidate optimized a local compliance gate and lost the requested product story."
        code, report = run_check(record)

        self.assertEqual(1, code)
        self.assertEqual("regressed", report["behavior_verdict"])
        self.assertIn("RPB.2", {item["id"] for item in report["findings"]})

    def test_improvement_requires_no_regression(self) -> None:
        record = example_record()
        authority = next(item for item in record["checks"] if item["id"] == "authority_boundaries")
        authority["baseline"] = "fail"
        code, report = run_check(record)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("improved", report["behavior_verdict"])
        self.assertEqual(["authority_boundaries"], report["comparison"]["improvements"])

    def test_missing_required_check_is_not_assessed(self) -> None:
        record = example_record()
        record["checks"] = [
            item for item in record["checks"] if item["id"] != "integration_quality"
        ]
        code, report = run_check(record)

        self.assertEqual(1, code)
        self.assertEqual("not_assessed", report["behavior_verdict"])
        self.assertIn("integration_quality", report["findings"][0]["evidence"])

    def test_current_run_only_cannot_make_comparative_claim(self) -> None:
        record = example_record()
        record["evidence_type"] = "current_run_only"
        code, report = run_check(record)

        self.assertEqual(1, code)
        self.assertEqual("not_assessed", report["behavior_verdict"])
        self.assertIn("RPB.0", {item["id"] for item in report["findings"]})

    def test_non_independent_evaluator_is_not_assessed(self) -> None:
        record = copy.deepcopy(example_record())
        record["evaluator"]["independent_context"] = False
        record["evaluator"]["expected_verdict_disclosed"] = True
        code, report = run_check(record)

        self.assertEqual(1, code)
        self.assertEqual("not_assessed", report["behavior_verdict"])


if __name__ == "__main__":
    unittest.main()
