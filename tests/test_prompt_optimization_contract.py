#!/usr/bin/env python3
"""Contract tests for the optional prompt-optimization audit route."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PRODUCT_SKILL = REPO / "skills" / "skill-self-check"
SKILL_MD = PRODUCT_SKILL / "SKILL.md"
PROMPT_REFERENCE = PRODUCT_SKILL / "references" / "prompt-optimization.md"
HARD_GATES = PRODUCT_SKILL / "scripts" / "hard_gates.py"


class PromptOptimizationContractTests(unittest.TestCase):
    def test_public_skill_contract_routes_prompt_optimization_requests(self) -> None:
        skill_text = SKILL_MD.read_text(encoding="utf-8")
        frontmatter = skill_text.split("---", 2)[1].lower()

        self.assertIn("prompt optimization", frontmatter)
        self.assertIn("references/prompt-optimization.md", skill_text)
        self.assertLessEqual(
            (len(SKILL_MD.read_bytes()) + 3) // 4,
            2500,
            "The optional route must not bloat the default prompt beyond 2,500 estimated tokens",
        )

    def test_prompt_optimization_reference_preserves_evidence_boundaries(self) -> None:
        reference = PROMPT_REFERENCE.read_text(encoding="utf-8")

        for required_heading in (
            "## Authority",
            "## Evidence baseline",
            "## Review axes",
            "## Output contract",
            "## Verified case study",
        ):
            self.assertIn(required_heading, reference)

        for required_term in (
            "source: model_review",
            "behavioral equivalence",
            "scope",
            "evidence",
            "severity",
            "confidence",
            "verification status",
        ):
            self.assertIn(required_term, reference)

    def test_product_hard_gate_still_accepts_the_routed_skill(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(HARD_GATES), str(PRODUCT_SKILL)],
            capture_output=True,
            check=False,
        )
        report = json.loads(proc.stdout.decode("utf-8"))

        self.assertEqual(proc.returncode, 0, report["findings"])
        self.assertEqual(report["gate_verdict"], "pass")
        self.assertEqual(
            report["package_health"]["checks"]["resource_links"]["missing_count"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
