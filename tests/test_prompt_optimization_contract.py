#!/usr/bin/env python3
"""Contract tests for standard static and selected Prompt-review routes."""

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
ROLE_DIAGRAMS = (
    REPO / "assets" / "diagrams" / "07-workflow-prompt-audit.svg",
    REPO / "assets" / "diagrams" / "zh" / "07-workflow-prompt-audit.svg",
)


class PromptOptimizationContractTests(unittest.TestCase):
    def test_public_skill_contract_routes_prompt_optimization_requests(self) -> None:
        skill_text = SKILL_MD.read_text(encoding="utf-8")
        frontmatter = skill_text.split("---", 2)[1].lower()

        self.assertIn("prompt optimization", frontmatter)
        self.assertIn("references/prompt-optimization.md", skill_text)
        for checker in (
            "scripts/hard_gates.py",
            "scripts/workflow_prompt_audit.py",
            "scripts/role_contract_audit.py",
        ):
            self.assertIn(checker, skill_text)
        self.assertIn("For every general audit", skill_text)
        self.assertIn("execute it instead of returning `not_run`", skill_text)
        self.assertIn("role and Prompt enhancement", skill_text)
        self.assertLessEqual(
            (len(SKILL_MD.read_bytes()) + 3) // 4,
            2500,
            "Standard routing must keep SKILL.md within 2,500 estimated tokens",
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
            "Role and work boundary",
            "role-prompt-review.md",
            "before context pruning",
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

    def test_role_diagrams_show_both_topology_axes(self) -> None:
        for diagram in ROLE_DIAGRAMS:
            with self.subTest(diagram=diagram):
                text = diagram.read_text(encoding="utf-8")
                self.assertIn("runtime_mode", text)
                self.assertIn("role_mode", text)
                self.assertIn("role_count", text)
                self.assertIn("aria-labelledby", text)


if __name__ == "__main__":
    unittest.main()
