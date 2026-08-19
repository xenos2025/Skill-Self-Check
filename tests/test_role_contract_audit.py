#!/usr/bin/env python3
"""Regression tests for conditional Skill and workflow role-contract routing."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PRODUCT_SKILL = REPO / "skills" / "skill-self-check"
SCRIPT = PRODUCT_SKILL / "scripts" / "role_contract_audit.py"
ROLE_ROUTE = PRODUCT_SKILL / "references" / "role-contract-audit.md"
ROLE_REVIEW = PRODUCT_SKILL / "references" / "role-prompt-review.md"
ROLE_ARCHETYPES = PRODUCT_SKILL / "references" / "role-archetypes.md"
ROLE_EXAMPLE = PRODUCT_SKILL / "examples" / "role-contract.example.json"
SHIPPED_SKILLS = (
    REPO / "skills" / "agent-work-readiness",
    PRODUCT_SKILL,
    REPO / "skills" / "skill-ship-safety",
)


def run_audit(skill: Path, *extra: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(skill), *extra],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.returncode, json.loads(result.stdout)


def write_skill(root: Path, *, include_contract: bool = True) -> Path:
    skill = root / "sample-role-skill"
    references = skill / "references"
    references.mkdir(parents=True)
    contract = {
        "schema_version": "1.0",
        "role": "Deterministic audit interpreter",
        "purpose": "Explain checker findings without changing their status.",
        "responsibilities": ["Run the checker and map findings to evidence."],
        "out_of_scope": ["Do not override the checker verdict."],
        "decision_authority": ["May report only the checker verdict."],
        "handoff_to": ["Send authorized repairs to verification."],
    }
    lines = [
        "---",
        "name: sample-role-skill",
        "description: Audits a local sample when the user requests a role check.",
        "---",
        "",
        "# Sample",
        "",
        "Workflow prompt audit: N/A — one agent instruction context.",
        "",
        "## Role contract",
    ]
    for field in (
        "role",
        "purpose",
        "responsibilities",
        "out_of_scope",
        "decision_authority",
        "handoff_to",
    ):
        value = contract[field]
        values = [value] if isinstance(value, str) else value
        lines.extend(f"- {item}" for item in values)
    (skill / "SKILL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if include_contract:
        (references / "role-contract.json").write_text(
            json.dumps(contract, indent=2) + "\n", encoding="utf-8"
        )
    return skill


def write_v11_skill(root: Path, *, sequential: bool = True) -> Path:
    skill = root / "v11-role-skill"
    references = skill / "references"
    references.mkdir(parents=True)
    roles = [
        {
            "id": "evidence-review",
            "role": "Evidence boundary reviewer",
            "purpose": "Classify supplied evidence and label unresolved facts.",
            "inputs": ["Source packet", "Evidence policy"],
            "responsibilities": ["Produce a bounded evidence map."],
            "out_of_scope": ["Do not invent facts or approve external actions."],
            "decision_authority": ["May label facts supported, missing, or conflicting."],
            "outputs": ["Reviewed evidence map"],
            "acceptance_tests": ["Every source fact has an evidence status."],
            "stop_conditions": ["Stop after all supplied sources are classified."],
            "next": ["report-builder"] if sequential else [],
            "handoff_to": [],
        },
        {
            "id": "report-builder",
            "role": "Evidence report builder",
            "purpose": "Turn the reviewed evidence map into the requested report format.",
            "inputs": ["Reviewed evidence map", "Report schema"],
            "responsibilities": ["Format findings without changing evidence status."],
            "out_of_scope": ["Do not reclassify evidence or add unsupported conclusions."],
            "decision_authority": ["May choose report structure within the supplied schema."],
            "outputs": ["Structured evidence report"],
            "acceptance_tests": ["The report preserves every evidence status and required field."],
            "stop_conditions": ["Stop when the report passes the supplied schema checks."],
            "next": [],
            "handoff_to": ["Report delivery"],
        },
    ]
    if not sequential:
        roles = roles[:1]
    contract = {
        "schema_version": "1.1",
        "runtime_mode": "single_context",
        "role_mode": "sequential_roles" if sequential else "single_role",
        "entry_role": "evidence-review",
        "roles": roles,
    }
    lines = [
        "---",
        "name: v11-role-skill",
        "description: Builds an evidence-bound product page when the user requests one.",
        "---",
        "",
        "# Product Page Skill",
        "",
        "Workflow prompt audit: N/A — one agent instruction context.",
        "",
        "## Functional role Prompt",
    ]
    for role in roles:
        lines.append(f"### {role['role']}")
        for field in (
            "purpose",
            "inputs",
            "responsibilities",
            "out_of_scope",
            "decision_authority",
            "outputs",
            "acceptance_tests",
            "stop_conditions",
            "next",
            "handoff_to",
        ):
            value = role[field]
            values = [value] if isinstance(value, str) else value
            lines.extend(f"- {item}" for item in values)
    (skill / "SKILL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (references / "role-contract.json").write_text(
        json.dumps(contract, indent=2) + "\n", encoding="utf-8"
    )
    return skill


def write_workflow_skill(root: Path, *, schema_version: str = "1.1") -> Path:
    skill = root / "workflow-role-skill"
    references = skill / "references"
    prompts = references / "prompts"
    prompts.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        """---
name: workflow-role-skill
description: Reviews a declared workflow when the user requests a node role check.
---

# Workflow Role Skill
""",
        encoding="utf-8",
    )
    prompt_rules = [
        "Role: Evidence reviewer",
        "Purpose: Review supplied evidence.",
        "Responsibilities: Label supported and missing facts.",
        "Out of scope: Do not approve external actions.",
        "Decision authority: READY",
        "READY only when facts are supported.",
        "result",
        "Every result labels missing facts.",
        "Stop after one review pass.",
    ]
    (prompts / "review.md").write_text(
        "\n".join(prompt_rules) + "\n", encoding="utf-8"
    )
    node = {
        "id": "review",
        "prompt_file": "references/prompts/review.md",
        "prompt_format": "markdown",
        "inputs": ["evidence"],
        "variables": [],
        "uses_untrusted_sources": False,
        "decision_gates": ["READY only when facts are supported."],
        "output_schema": ["result"],
        "acceptance_tests": ["Every result labels missing facts."],
        "stop_conditions": ["Stop after one review pass."],
        "next": [],
    }
    if schema_version == "1.1":
        node["role_contract"] = {
            "role": "Evidence reviewer",
            "purpose": "Review supplied evidence.",
            "responsibilities": ["Label supported and missing facts."],
            "out_of_scope": ["Do not approve external actions."],
            "decision_authority": ["READY"],
            "handoff_to": [],
        }
    manifest = {
        "schema_version": schema_version,
        "workflow_id": "evidence-review",
        "entry_node": "review",
        "nodes": [node],
    }
    (references / "workflow-prompts.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return skill


class RoleContractAuditTests(unittest.TestCase):
    def test_shipped_skills_use_single_context_roles(self) -> None:
        for skill in SHIPPED_SKILLS:
            with self.subTest(skill=skill.name):
                code, report = run_audit(skill)
                self.assertEqual(0, code, report["findings"])
                self.assertEqual("single_context", report["mode"])
                self.assertEqual("single_context", report["runtime_mode"])
                self.assertEqual("single_role", report["role_mode"])
                self.assertEqual(1, report["role_count"])
                self.assertEqual("pass", report["status"])
                self.assertTrue(report["role"])
                self.assertTrue(
                    (skill / "references" / "role-contract.json").is_file()
                )
                self.assertFalse(
                    (skill / "references" / "workflow-prompts.json").exists()
                )

    def test_single_context_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir))
            code, report = run_audit(skill)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("single_context", report["mode"])
        self.assertEqual("pass", report["status"])
        self.assertEqual("single_role", report["role_mode"])
        self.assertEqual(1, report["role_count"])

    def test_schema_1_1_single_role_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_v11_skill(Path(temp_dir), sequential=False)
            code, report = run_audit(skill)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("single_context", report["runtime_mode"])
        self.assertEqual("single_role", report["role_mode"])
        self.assertEqual("evidence-review", report["entry_role"])
        self.assertEqual(1, report["role_count"])
        self.assertEqual(
            "Evidence boundary reviewer",
            report["role"],
        )

    def test_schema_1_1_sequential_roles_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_v11_skill(Path(temp_dir))
            code, report = run_audit(skill)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("sequential_roles", report["role_mode"])
        self.assertEqual("evidence-review", report["entry_role"])
        self.assertEqual(2, report["role_count"])
        self.assertIsNone(report["role"])
        self.assertEqual(["report-builder"], report["roles"][0]["next"])

    def test_schema_1_1_invalid_role_topologies_report_rca_3(self) -> None:
        mutations = {
            "duplicate id": lambda contract: contract["roles"][1].update(
                {"id": "evidence-review"}
            ),
            "bad entry": lambda contract: contract.update({"entry_role": "missing"}),
            "missing next target": lambda contract: contract["roles"][0].update(
                {"next": ["missing"]}
            ),
            "cycle": lambda contract: contract["roles"][1].update(
                {"next": ["evidence-review"]}
            ),
            "unreachable": lambda contract: contract["roles"][0].update(
                {"next": []}
            ),
            "wrong role count": lambda contract: contract.update(
                {"role_mode": "single_role"}
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory() as temp_dir:
                skill = write_v11_skill(Path(temp_dir))
                contract_path = skill / "references" / "role-contract.json"
                contract = json.loads(contract_path.read_text(encoding="utf-8"))
                mutate(contract)
                contract_path.write_text(
                    json.dumps(contract, indent=2) + "\n", encoding="utf-8"
                )
                code, report = run_audit(skill)

            self.assertEqual(1, code)
            self.assertIn("RCA.3", {item["id"] for item in report["findings"]})

    def test_schema_1_1_declared_prompt_text_must_appear_in_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_v11_skill(Path(temp_dir))
            skill_md = skill / "SKILL.md"
            skill_md.write_text(
                skill_md.read_text(encoding="utf-8").replace(
                    "Do not reclassify evidence or add unsupported conclusions.", ""
                ),
                encoding="utf-8",
            )
            code, report = run_audit(skill)

        self.assertEqual(1, code)
        finding = next(item for item in report["findings"] if item["id"] == "RCA.2")
        self.assertEqual("roles[1].out_of_scope", finding["field"])

    def test_terminal_single_context_role_may_have_no_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir))
            contract_path = skill / "references" / "role-contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["handoff_to"] = []
            contract_path.write_text(
                json.dumps(contract, indent=2) + "\n", encoding="utf-8"
            )
            code, report = run_audit(skill)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("pass", report["status"])

    def test_single_context_missing_contract_is_not_assessed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir), include_contract=False)
            code, report = run_audit(skill)

        self.assertEqual(1, code)
        self.assertEqual("not_assessed", report["status"])
        self.assertEqual("RCA.0", report["findings"][0]["id"])

    def test_reasoned_role_not_applicable_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir), include_contract=False)
            with (skill / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write(
                    "\nRole contract audit: N/A — role wording would not change decisions, evidence, output, permissions, or handoff.\n"
                )
            code, report = run_audit(skill)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("not_applicable", report["status"])
        self.assertIn("would not change", report["applicability_reason"])

    def test_declared_role_text_must_appear_in_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir))
            skill_md = skill / "SKILL.md"
            skill_md.write_text(
                skill_md.read_text(encoding="utf-8").replace(
                    "Do not override the checker verdict.", ""
                ),
                encoding="utf-8",
            )
            code, report = run_audit(skill)

        self.assertEqual(1, code)
        finding = next(item for item in report["findings"] if item["id"] == "RCA.2")
        self.assertEqual("out_of_scope", finding["field"])

    def test_single_context_delegation_directive_reports_rca_4(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir))
            with (skill / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\n## Process\n\n把角色拆开后分派给两个子 Agent 并行执行。\n")
            code, report = run_audit(skill)

        self.assertEqual(1, code)
        self.assertEqual("needs_work", report["status"])
        finding = next(item for item in report["findings"] if item["id"] == "RCA.4")
        self.assertEqual("runtime_topology", finding["field"])
        self.assertEqual("single_context", finding["mode"])
        self.assertIn("子 Agent", finding["evidence"][0]["text"])
        self.assertGreater(finding["evidence"][0]["line"], 0)

    def test_english_delegation_directive_reports_rca_4(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir))
            with (skill / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write(
                    "\n## Process\n\nSpawn one subagent per review pass and merge the results.\n"
                )
            code, report = run_audit(skill)

        self.assertEqual(1, code)
        finding = next(item for item in report["findings"] if item["id"] == "RCA.4")
        self.assertEqual("runtime_topology", finding["field"])

    def test_prohibited_delegation_wording_is_not_a_leak(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir))
            with (skill / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write(
                    "\n## Process\n\n不得把角色分派给子 Agent。\n"
                    "Never dispatch a subagent for a review pass.\n"
                )
            code, report = run_audit(skill)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("pass", report["status"])

    def test_delegation_named_inside_prohibitive_section_is_not_a_leak(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir))
            with (skill / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\n## Red Flags\n\n- 分派给子 Agent\n")
            code, report = run_audit(skill)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("pass", report["status"])

    def test_delegation_inside_code_block_is_not_a_leak(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir))
            with (skill / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\n## Process\n\n```bash\ndispatch --subagent review\n```\n")
            code, report = run_audit(skill)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("pass", report["status"])

    def test_reasoned_role_not_applicable_still_reports_delegation_leak(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_skill(Path(temp_dir), include_contract=False)
            with (skill / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write(
                    "\nRole contract audit: N/A — role wording would not change decisions, evidence, output, permissions, or handoff.\n"
                    "\n## Process\n\n把复核任务委派给另一个子 Agent。\n"
                )
            code, report = run_audit(skill)

        self.assertEqual(1, code)
        self.assertEqual("needs_work", report["status"])
        self.assertEqual("RCA.4", report["findings"][0]["id"])

    def test_workflow_node_mode_does_not_report_delegation_leak(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_workflow_skill(Path(temp_dir))
            with (skill / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\n## Process\n\n分派给两个子 Agent 并行执行。\n")
            code, report = run_audit(skill)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("workflow_nodes", report["mode"])
        self.assertEqual([], [item for item in report["findings"] if item["id"] == "RCA.4"])

    def test_schema_1_1_workflow_routes_to_node_roles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_workflow_skill(Path(temp_dir))
            code, report = run_audit(skill)

        self.assertEqual(0, code, report["findings"])
        self.assertEqual("workflow_nodes", report["mode"])
        self.assertEqual("per_model_call", report["role_mode"])
        self.assertEqual(1, report["role_count"])
        self.assertEqual("review", report["entry_role"])
        self.assertEqual("pass", report["status"])
        self.assertEqual("Evidence reviewer", report["nodes"][0]["role"])

    def test_schema_1_0_workflow_role_is_not_assessed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = write_workflow_skill(Path(temp_dir), schema_version="1.0")
            code, report = run_audit(skill)

        self.assertEqual(1, code)
        self.assertEqual("workflow_nodes", report["mode"])
        self.assertEqual("not_assessed", report["status"])
        self.assertEqual("RCA.0", report["findings"][0]["id"])

    def test_routes_and_archetype_library_are_documented(self) -> None:
        skill_text = (PRODUCT_SKILL / "SKILL.md").read_text(encoding="utf-8")
        route_text = ROLE_ROUTE.read_text(encoding="utf-8")
        review_text = ROLE_REVIEW.read_text(encoding="utf-8")
        archetype_text = ROLE_ARCHETYPES.read_text(encoding="utf-8")
        example = json.loads(ROLE_EXAMPLE.read_text(encoding="utf-8"))

        self.assertIn("scripts/role_contract_audit.py", skill_text)
        self.assertIn("workflow_nodes", route_text)
        self.assertIn("single_context", route_text)
        self.assertIn("sequential_roles", route_text)
        self.assertIn("RCA.3", route_text)
        self.assertIn("RCA.4", route_text)
        self.assertIn("## Work-unit inventory", review_text)
        self.assertIn("## Preserve the global mission first", review_text)
        self.assertIn("## Integration coupling and split decision", review_text)
        self.assertIn("## Synthesize the Prompt", review_text)
        self.assertIn("single_agent_shared_context", review_text)
        self.assertIn("unresolved placeholder", review_text)
        self.assertIn("blocking intake patch", review_text)
        self.assertIn("behavior_eval_required", review_text)
        self.assertIn("Router / gatekeeper", archetype_text)
        self.assertIn("generic labels", archetype_text)
        self.assertIn("Claims Gate", archetype_text)
        self.assertEqual("1.1", example["schema_version"])
        self.assertEqual("single_role", example["role_mode"])
        self.assertEqual(1, len(example["roles"]))
        self.assertEqual([], example["roles"][0]["next"])


if __name__ == "__main__":
    unittest.main()
