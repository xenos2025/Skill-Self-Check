#!/usr/bin/env python3
"""Regression tests for scripts/hard_gates.py (stdlib only).

Run:
  python tests/test_hard_gates.py
"""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "skill-self-check" / "scripts" / "hard_gates.py"
PRODUCT_SKILL = REPO / "skills" / "skill-self-check"
BAD_FIXTURE = PRODUCT_SKILL / "examples" / "fixtures" / "bad-commit-helper"

ZH_SKILL = """---
name: {name}
description: 检查中文技能说明书的结构，用于用户写完说明书后需要一次自检时。
---

# 中文技能

## 何时使用

- 写完说明书之后

## 何时不用

- 从零创建说明书

## 检查轴

- 颜色
- 构图
- 文案

## 步骤

1. 读取目标文件
   完成标准: 已拿到全文
2. 输出报告
   完成标准: 报告含分数

## 验收

- [ ] 已输出报告
- [ ] 分数与脚本一致

## 常见借口

| 借口 | 事实 |
|------|------|
| 文件小就不用读 | 仍要读全文 |
"""


def run_script(target: Path, env: dict[str, str] | None = None) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True,
        env=env,
    )
    payload = json.loads(proc.stdout.decode("utf-8"))
    return proc.returncode, payload


def write_skill(tmp: Path, name: str, body: str, encoding: str = "utf-8") -> Path:
    skill_dir = tmp / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_bytes(body.format(name=name).encode(encoding))
    return skill_dir


class ProductSkillTests(unittest.TestCase):
    def test_product_skill_meets_ship_floor(self) -> None:
        code, report = run_script(PRODUCT_SKILL)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["schema_version"], "1.4")
        self.assertEqual(report["audit_level"], "static_contract_check")
        self.assertEqual(report["target_platform"], "generic")
        self.assertTrue(report["limitations"])
        self.assertEqual(report["gate_verdict"], "pass")
        self.assertEqual(report["gate_reasons"], [])
        self.assertEqual(
            report["gate_policy"]["id"],
            "explicit-required-checks-v1",
        )
        self.assertTrue(
            all(
                item["status"] == "pass"
                for item in report["gate_policy"]["required_checks"].values()
            )
        )
        self.assertEqual(report["scores"]["basic_usable"]["score"], 5)
        self.assertEqual(report["scores"]["contract_clarity"]["score"], 5)
        self.assertEqual(
            report["scores"]["scoring_effect"],
            "informational_only",
        )
        self.assertTrue(report["scores"]["ship_floor_met"])
        self.assertEqual(
            report["deprecated_fields"]["scores.ship_floor_met"]["replacement"],
            "gate_verdict",
        )
        self.assertEqual(report["counts"]["critical"], 0)
        package = report["package_health"]
        self.assertEqual(package["status"], "valid_skill_package")
        self.assertTrue(package["assessable"])
        self.assertEqual(
            package["installability"]["status"],
            "pass",
        )
        kit = report["scores"]["support_kit"]
        self.assertTrue(kit["kit_complete"])
        self.assertEqual(kit["modules"]["references"]["status"], "pass")
        self.assertEqual(kit["modules"]["examples"]["status"], "pass")
        self.assertEqual(kit["modules"]["scripts"]["status"], "pass")
        self.assertEqual(kit["modules"]["memory"]["status"], "na")
        metrics = report["operational_metrics"]
        token = metrics["token_consumption"]
        self.assertEqual(token["status"], "estimated")
        self.assertEqual(
            token["estimated_input_tokens"],
            (len((PRODUCT_SKILL / "SKILL.md").read_bytes()) + 3) // 4,
        )
        self.assertEqual(token["confidence"], "low")
        self.assertEqual(token["budget"]["status"], "within")
        self.assertEqual(
            metrics["runtime_duration"]["status"],
            "not_measured",
        )
        self.assertIn(
            metrics["loop_guard"]["status"], {"pass", "not_applicable"}
        )
        self.assertEqual(
            [f["id"] for f in report["findings"] if f["id"].startswith("EFF")],
            [],
        )

    def test_out_json_writes_same_utf8_report_as_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "reports" / "hard-gates.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(PRODUCT_SKILL),
                    "--out-json",
                    str(output),
                    "--pretty",
                ],
                capture_output=True,
                check=False,
            )
            stdout_report = json.loads(proc.stdout.decode("utf-8"))
            stored_bytes = output.read_bytes()
            stored_report = json.loads(stored_bytes.decode("utf-8"))
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8"))
        self.assertFalse(stored_bytes.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(stored_report, stdout_report)

    def test_out_json_is_refused_inside_audited_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "zh-skill", ZH_SKILL)
            output = skill / "hard-gates.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(skill),
                    "--out-json",
                    str(output),
                ],
                capture_output=True,
                check=False,
            )
            output_exists = output.exists()
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(output_exists)
        self.assertIn(
            "--out-json must stay outside the audited Skill",
            proc.stderr.decode("utf-8"),
        )

    def test_plain_language_and_technical_views_are_wired(self) -> None:
        skill_text = (PRODUCT_SKILL / "SKILL.md").read_text(encoding="utf-8")
        for name in (
            "references/plain-language-response.md",
            "REPORT-TEMPLATE.md",
        ):
            self.assertTrue((PRODUCT_SKILL / name).is_file())
            self.assertIn(name, skill_text)
        self.assertFalse(
            (PRODUCT_SKILL / "REPORT-BUSINESS-TEMPLATE.md").exists()
        )

    def test_bad_fixture_fails_ship_floor(self) -> None:
        code, report = run_script(BAD_FIXTURE)
        self.assertEqual(code, 1)
        self.assertEqual(report["gate_verdict"], "invalid_skill_package")
        self.assertTrue(report["gate_reasons"])
        self.assertFalse(report["scores"]["ship_floor_met"])
        self.assertGreater(report["counts"]["critical"], 0)

    def test_gate_policy_is_explicit_and_does_not_read_numeric_score(self) -> None:
        module = runpy.run_path(str(SCRIPT))
        evaluate_gate = module["evaluate_gate"]
        points = {
            "file_and_frontmatter": True,
            "name_valid_and_matched": True,
            "description_voice_and_triggers": True,
            "body_actionable": True,
            "verification_or_done_when": False,
        }
        verdict, reasons, policy = evaluate_gate(
            points,
            [],
            {
                "status": "valid_skill_package",
                "assessable": True,
            },
        )
        self.assertEqual(sum(1 for passed in points.values() if passed), 4)
        self.assertEqual(verdict, "pass")
        self.assertEqual(reasons, [])
        self.assertNotIn(
            "verification_or_done_when",
            policy["required_checks"],
        )
        self.assertEqual(policy["scoring_effect"], "none")

    def test_missing_skill_md_still_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_script(Path(tmp))
        self.assertEqual(code, 1)
        self.assertEqual(
            [f["id"] for f in report["findings"]],
            ["1.1", "PKG.1"],
        )
        self.assertEqual(
            report["package_health"]["status"],
            "invalid_skill_package",
        )
        self.assertEqual(
            report["operational_metrics"]["token_consumption"]["status"],
            "not_assessed",
        )


class ChineseSkillTests(unittest.TestCase):
    def test_chinese_skill_passes_hard_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "zh-skill", ZH_SKILL)
            code, report = run_script(skill)
        ids = [f["id"] for f in report["findings"]]
        self.assertNotIn("1.7", ids, "Chinese WHEN triggers must be recognised")
        self.assertNotIn("1.7b", ids, "Chinese WHAT verbs must be recognised")
        self.assertNotIn("3.3", ids, "'何时不用' must count as When NOT to use")
        self.assertEqual(report["scores"]["basic_usable"]["score"], 5)
        self.assertEqual(report["scores"]["contract_clarity"]["score"], 5)
        self.assertEqual(code, 0)

    def test_non_utf8_file_is_flagged_not_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "gbk-skill", ZH_SKILL, encoding="gb18030")
            code, report = run_script(skill)
        ids = [f["id"] for f in report["findings"]]
        self.assertIn("1.11", ids, "non-UTF-8 SKILL.md must raise a finding")
        self.assertEqual(report["scores"]["basic_usable"]["score"], 5)
        self.assertEqual(code, 0, "encoding fallback must not break scoring")

    def test_json_is_utf8_under_legacy_codepage(self) -> None:
        import os

        env = dict(os.environ, PYTHONIOENCODING="cp936")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "zh-skill", ZH_SKILL)
            _, report = run_script(skill, env=env)
        self.assertIn("检查中文技能", report["frontmatter"]["description"])


class ParsingRegressionTests(unittest.TestCase):
    def test_hyphenated_check_axis_is_not_truncated(self) -> None:
        body = ZH_SKILL.replace(
            "- 颜色\n- 构图\n- 文案",
            "- Per-role coverage: reviewer mapping\n- Evidence quality: source citations",
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "axis-skill", body)
            _, report = run_script(skill)
        axes = report["scores"]["contract_clarity"]["detected_axes"]
        self.assertIn("Per-role coverage", axes)
        self.assertNotIn("Per", axes)

    def test_weak_run_after_phrase_does_not_count_as_trigger(self) -> None:
        body = ZH_SKILL.replace(
            "description: 检查中文技能说明书的结构，用于用户写完说明书后需要一次自检时。",
            "description: Reviews a drafted skill. Run after drafting.",
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "weak-trigger", body)
            code, report = run_script(skill)
        self.assertEqual(code, 1)
        self.assertIn("1.7", [f["id"] for f in report["findings"]])

    def test_routes_and_orchestrates_count_as_what_verbs(self) -> None:
        for verb in ("Routes", "Orchestrates"):
            body = ZH_SKILL.replace(
                "description: 检查中文技能说明书的结构，用于用户写完说明书后需要一次自检时。",
                f"description: {verb} requests to specialist workflows. Use when triaging work.",
            )
            with self.subTest(verb=verb), tempfile.TemporaryDirectory() as tmp:
                skill = write_skill(Path(tmp), f"{verb.lower()}-skill", body)
                _, report = run_script(skill)
            self.assertNotIn("1.7b", [f["id"] for f in report["findings"]])

    def test_user_invoked_missing_when_heading_has_finding(self) -> None:
        body = ZH_SKILL.replace(
            "name: {name}",
            "name: {name}\ndisable-model-invocation: true",
        ).replace("## 何时使用\n\n- 写完说明书之后\n\n", "")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "manual-skill", body)
            code, report = run_script(skill)
        self.assertEqual(code, 0)
        self.assertEqual(
            report["scores"]["contract_clarity"]["points"]["when_to_use"],
            False,
        )
        self.assertIn("3.2", [f["id"] for f in report["findings"]])

    def test_automation_boundary_does_not_claim_a_script(self) -> None:
        body = ZH_SKILL.replace(
            "## 常见借口",
            "Automation boundary and human decision ownership.\n\n## 常见借口",
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "boundary-skill", body)
            _, report = run_script(skill)
        ids = [f["id"] for f in report["findings"]]
        self.assertNotIn("6.4b", ids)
        self.assertEqual(
            report["scores"]["support_kit"]["modules"]["scripts"]["status"],
            "na",
        )


class SupportKitTests(unittest.TestCase):
    def test_placeholder_prefixed_posix_path_is_portable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "portable-placeholder", ZH_SKILL)
            (skill / "references").mkdir()
            (skill / "references" / "paths.md").write_text(
                "Write temporary state under <workspace>/tmp/tool/<operation-id>/.\n",
                encoding="utf-8",
            )
            _, report = run_script(skill)
        self.assertNotIn("PKG.4", [finding["id"] for finding in report["findings"]])

    def test_placeholder_does_not_hide_real_path_on_same_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "mixed-paths", ZH_SKILL)
            (skill / "references").mkdir()
            (skill / "references" / "paths.md").write_text(
                "Use <workspace>/tmp/<operation-id>/, never C:\\Users\\Alice\\private.txt.\n",
                encoding="utf-8",
            )
            _, report = run_script(skill)
        pkg_findings = [
            finding for finding in report["findings"] if finding["id"] == "PKG.4"
        ]
        self.assertEqual(1, len(pkg_findings))
        self.assertIn("references/paths.md:1", pkg_findings[0]["evidence"])

    def test_node_esm_helper_counts_as_documented_script(self) -> None:
        body = ZH_SKILL.replace(
            "## 常见借口",
            "Run `node scripts/helper.mjs` for deterministic automation.\n\n## 常见借口",
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "esm-helper", body)
            (skill / "scripts").mkdir()
            (skill / "scripts" / "helper.mjs").write_text("console.log('ok');\n", encoding="utf-8")
            _, report = run_script(skill)
        self.assertNotIn("6.4b", [finding["id"] for finding in report["findings"]])
        self.assertEqual("pass", report["scores"]["support_kit"]["modules"]["scripts"]["status"])

    def test_workflow_without_kit_gets_should_fix_not_critical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "bare-flow", ZH_SKILL)
            code, report = run_script(skill)
        ids = [f["id"] for f in report["findings"]]
        self.assertIn("6.1", ids)
        self.assertIn("6.2", ids)
        self.assertEqual(code, 0, "support_kit must not block ship floor")
        self.assertFalse(report["scores"]["support_kit"]["kit_complete"])

    def test_explicit_na_clears_support_kit(self) -> None:
        body = ZH_SKILL + """

## 配套模块

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 资料 | N/A | 全文自包含 |
| 案例 | N/A | 无样例需求 |
"""
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "na-kit", body)
            code, report = run_script(skill)
        kit = report["scores"]["support_kit"]
        self.assertEqual(kit["modules"]["references"]["status"], "na")
        self.assertEqual(kit["modules"]["examples"]["status"], "na")
        self.assertTrue(kit["kit_complete"])
        self.assertEqual(code, 0)
        ids = [f["id"] for f in report["findings"]]
        self.assertNotIn("6.1", ids)
        self.assertNotIn("6.2", ids)

    def test_memory_signal_requires_schema(self) -> None:
        body = ZH_SKILL.replace(
            "## 常见借口",
            "冷却期状态要跨次保留，禁止重复触达。\n\n## 常见借口",
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(Path(tmp), "mem-thin", body)
            _, report = run_script(skill)
        ids = [f["id"] for f in report["findings"]]
        self.assertIn("6.3", ids)
        self.assertEqual(report["scores"]["support_kit"]["modules"]["memory"]["status"], "fail")


class PackageHealthTests(unittest.TestCase):
    def test_workspace_like_target_blocks_maturity_assessment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project-workspace"
            root.mkdir()
            body = ZH_SKILL.format(name="fixed-model-tryon").replace(
                "1. 读取目标文件",
                "1. 读取 `assets/model-reference.jpg`\n"
                "   并写入 `D:\\\\old-workspace\\\\生成的模特图`\n"
                "2. 读取 `references/missing.md`\n"
                "3. 读取目标文件",
            )
            (root / "SKILL.md").write_text(body, encoding="utf-8")
            (root / "assets").mkdir()
            model_bytes = b"x" * (70 * 1024)
            (root / "assets" / "model-reference.jpg").write_bytes(model_bytes)
            child_assets = root / "fixed-model-tryon" / "assets"
            child_assets.mkdir(parents=True)
            (child_assets / "model-reference.jpg").write_bytes(model_bytes)
            outputs = root / "outputs"
            outputs.mkdir()
            (outputs / "generated.png").write_bytes(b"y" * (70 * 1024))
            nonstandard = root / "style-library"
            nonstandard.mkdir()
            (nonstandard / "look.jpg").write_bytes(b"z" * (70 * 1024))

            code, report = run_script(root)

        self.assertEqual(code, 1)
        package = report["package_health"]
        self.assertEqual(package["status"], "invalid_skill_package")
        self.assertFalse(package["assessable"])
        self.assertEqual(package["installability"]["status"], "fail")
        self.assertGreaterEqual(
            package["summary"]["blocking_check_count"],
            4,
        )
        checks = package["checks"]
        self.assertEqual(checks["single_skill_root"]["status"], "fail")
        self.assertEqual(checks["name_matches_root"]["status"], "fail")
        self.assertEqual(checks["standard_topology"]["status"], "fail")
        self.assertEqual(checks["portable_paths"]["status"], "fail")
        self.assertEqual(checks["resource_links"]["status"], "fail")
        self.assertEqual(checks["resource_uniqueness"]["status"], "warn")
        ids = {finding["id"] for finding in report["findings"]}
        self.assertTrue(
            {"PKG.1c", "PKG.2", "PKG.3", "PKG.3b", "PKG.4", "PKG.5", "PKG.7"}
            <= ids
        )
        package_findings = [
            finding
            for finding in report["findings"]
            if finding["id"].startswith("PKG.")
        ]
        self.assertTrue(
            all(finding["verification_status"] == "verified" for finding in package_findings)
        )


class EfficiencyGateTests(unittest.TestCase):
    def test_unguarded_retry_is_flagged(self) -> None:
        body = ZH_SKILL.replace(
            "2. 输出报告\n   完成标准: 报告含分数",
            "2. 输出报告\n   完成标准: 报告含分数\n3. 如果生成失败就重试",
        )
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_script(write_skill(Path(tmp), "loopy-skill", body))
        self.assertEqual(code, 0, report["findings"])
        ids = [f["id"] for f in report["findings"]]
        self.assertIn("EFF.1", ids)
        guard = report["operational_metrics"]["loop_guard"]
        self.assertEqual(guard["status"], "warn")
        self.assertEqual(guard["loop_directive_count"], 1)
        self.assertEqual(guard["guarded_count"], 0)
        self.assertTrue(guard["unguarded_lines"])

    def test_bounded_retry_passes(self) -> None:
        body = ZH_SKILL.replace(
            "2. 输出报告\n   完成标准: 报告含分数",
            "2. 输出报告\n   完成标准: 报告含分数\n"
            "3. 如果生成失败最多重试 2 次，仍失败则停止并报告错误",
        )
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_script(write_skill(Path(tmp), "bounded-skill", body))
        self.assertEqual(code, 0, report["findings"])
        ids = [f["id"] for f in report["findings"]]
        self.assertNotIn("EFF.1", ids)
        guard = report["operational_metrics"]["loop_guard"]
        self.assertEqual(guard["status"], "pass")
        self.assertEqual(guard["loop_directive_count"], 1)
        self.assertEqual(guard["guarded_count"], 1)

    def test_negated_loop_instruction_is_not_a_directive(self) -> None:
        body = ZH_SKILL.replace(
            "2. 输出报告\n   完成标准: 报告含分数",
            "2. 输出报告\n   完成标准: 报告含分数\n"
            "3. 不要为了相同证据\n   重复运行检查脚本",
        )
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_script(write_skill(Path(tmp), "guarded-skill", body))
        self.assertEqual(code, 0, report["findings"])
        ids = [f["id"] for f in report["findings"]]
        self.assertNotIn("EFF.1", ids)
        guard = report["operational_metrics"]["loop_guard"]
        self.assertEqual(guard["loop_directive_count"], 0)

    def test_unbounded_refinement_phrase_is_flagged(self) -> None:
        body = ZH_SKILL.replace(
            "2. 输出报告\n   完成标准: 报告含分数",
            "2. 输出报告\n   完成标准: 报告含分数\n3. 不断优化文案直到满意",
        )
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_script(write_skill(Path(tmp), "endless-skill", body))
        self.assertEqual(code, 0, report["findings"])
        ids = [f["id"] for f in report["findings"]]
        self.assertIn("EFF.2", ids)
        guard = report["operational_metrics"]["loop_guard"]
        self.assertEqual(guard["status"], "warn")
        self.assertTrue(guard["unbounded_phrase_lines"])

    def test_oversized_instruction_text_exceeds_token_budget(self) -> None:
        padding = "\n".join(
            f"- 规则第 {i} 条：所有输出必须先给出证据再给结论。" for i in range(700)
        )
        body = ZH_SKILL.replace(
            "## 常见借口",
            f"## 附加规则\n\n{padding}\n\n## 常见借口",
        )
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_script(write_skill(Path(tmp), "huge-skill", body))
        ids = [f["id"] for f in report["findings"]]
        self.assertIn("EFF.3", ids)
        token = report["operational_metrics"]["token_consumption"]
        self.assertEqual(token["budget"]["status"], "exceeded")
        self.assertGreater(
            token["estimated_input_tokens"],
            token["budget"]["max_recommended_input_tokens"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
