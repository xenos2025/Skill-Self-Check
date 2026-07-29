#!/usr/bin/env python3
"""Regression tests for scripts/verify_fix.py (stdlib only).

Run:
  python tests/test_verify_fix.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SELF_CHECK = REPO / "skills" / "skill-self-check"
HARD_GATES = SELF_CHECK / "scripts" / "hard_gates.py"
VERIFY = SELF_CHECK / "scripts" / "verify_fix.py"

GOOD_SKILL = """---
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

WEAK_SKILL = """---
name: Helper
description: I can help you with stuff when you need it.
---

# Helper

Always be careful and think step by step.

## Tips

Don't be vague. Don't forget the details. Never skip the diff.
"""


def write_skill(directory: Path, name: str, body: str) -> Path:
    skill_dir = directory / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(body.format(name=name), encoding="utf-8")
    return skill_dir


def capture_baseline(target: Path, destination: Path, encoding: str = "utf-8") -> Path:
    proc = subprocess.run(
        [sys.executable, str(HARD_GATES), str(target)],
        capture_output=True,
        check=False,
    )
    payload = proc.stdout.decode("utf-8")
    destination.write_bytes(payload.encode(encoding))
    return destination


def run_verify(target: Path, baseline: Path, *, strict: bool = False) -> tuple[int, dict]:
    command = [sys.executable, str(VERIFY), str(target), "--baseline", str(baseline)]
    if strict:
        command.append("--strict")
    proc = subprocess.run(command, capture_output=True, check=False)
    return proc.returncode, json.loads(proc.stdout.decode("utf-8"))


def partly_fixed_skill(name: str) -> str:
    """Frontmatter and structure fixed, but the rewrite adds an unguarded loop."""
    return GOOD_SKILL.format(name=name).replace(
        "2. 输出报告\n   完成标准: 报告含分数",
        "2. 输出报告\n   完成标准: 报告含分数\n3. 如果生成失败就重试",
    )


class UnchangedTargetTests(unittest.TestCase):
    def test_identical_target_reports_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "steady-skill", GOOD_SKILL)
            baseline = capture_baseline(target, root / "baseline.json")
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 0)
        self.assertEqual(report["verdict"], "unchanged")
        self.assertFalse(report["regression_detected"])
        self.assertEqual(report["findings"]["counts"]["resolved"], 0)
        self.assertEqual(report["findings"]["counts"]["introduced"], 0)

    def test_utf16_baseline_from_shell_redirect_is_readable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "steady-skill", GOOD_SKILL)
            baseline = capture_baseline(target, root / "baseline.json", "utf-16")
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 0)
        self.assertEqual(report["verdict"], "unchanged")


class ImprovementTests(unittest.TestCase):
    def test_fixed_skill_reports_resolved_findings_and_floor_gain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "weak-skill", WEAK_SKILL)
            baseline = capture_baseline(target, root / "baseline.json")
            (target / "SKILL.md").write_text(
                GOOD_SKILL.format(name="weak-skill"), encoding="utf-8"
            )
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 0)
        self.assertEqual(report["verdict"], "improved")
        self.assertFalse(report["regression_detected"])
        self.assertGreater(report["findings"]["counts"]["resolved_critical"], 0)
        self.assertEqual(report["findings"]["counts"]["new_critical"], 0)
        self.assertEqual(report["scores"]["basic_usable"]["direction"], "improved")
        self.assertEqual(report["scores"]["scoring_effect"], "informational_only")
        self.assertEqual(
            report["gates"]["gate_verdict"]["direction"],
            "improved",
        )
        self.assertEqual(report["gates"]["ship_floor"]["before"], False)
        self.assertEqual(report["gates"]["ship_floor"]["after"], True)
        self.assertEqual(report["gates"]["ship_floor"]["direction"], "improved")
        self.assertEqual(report["remaining_critical"], 0)

    def test_newly_applicable_checks_are_surfaced_not_called_regressions(self) -> None:
        """Gaining real steps makes the support-kit checks apply for the first time."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "weak-skill", WEAK_SKILL)
            baseline = capture_baseline(target, root / "baseline.json")
            (target / "SKILL.md").write_text(
                GOOD_SKILL.format(name="weak-skill"), encoding="utf-8"
            )
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 0)
        self.assertFalse(report["hard_regression"])
        introduced = [item["id"] for item in report["findings"]["introduced"]]
        self.assertIn("6.1", introduced)
        self.assertGreater(
            report["findings"]["counts"]["newly_surfaced_non_critical"], 0
        )
        # support_kit went from 0/0 to 0/2, so the two scores are not comparable.
        self.assertEqual(
            report["scores"]["support_kit"]["direction"], "not_comparable"
        )

    def test_renaming_to_match_directory_is_recorded_not_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "renamed-skill", WEAK_SKILL)
            baseline = capture_baseline(target, root / "baseline.json")
            (target / "SKILL.md").write_text(
                GOOD_SKILL.format(name="renamed-skill"), encoding="utf-8"
            )
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 0)
        self.assertTrue(report["target"]["name_changed"])
        self.assertFalse(report["target"]["directory_changed"])
        self.assertEqual(report["target"]["current_name"], "renamed-skill")

    def test_moving_bulk_material_out_records_token_savings(self) -> None:
        padding = "\n".join(
            f"- 规则第 {i} 条：所有输出必须先给出证据再给结论。" for i in range(700)
        )
        bloated = GOOD_SKILL.replace(
            "## 常见借口", f"## 附加规则\n\n{padding}\n\n## 常见借口"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "slim-skill", bloated)
            baseline = capture_baseline(target, root / "baseline.json")
            (target / "SKILL.md").write_text(
                GOOD_SKILL.format(name="slim-skill"), encoding="utf-8"
            )
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 0)
        efficiency = report["efficiency"]
        self.assertGreater(efficiency["estimated_input_tokens"]["saved"], 0)
        self.assertEqual(efficiency["token_budget"]["before"], "exceeded")
        self.assertEqual(efficiency["token_budget"]["after"], "within")
        self.assertIn(
            "EFF.3",
            [item["id"] for item in report["findings"]["resolved"]],
        )


class RegressionTests(unittest.TestCase):
    def test_score_drop_does_not_create_a_hard_regression(self) -> None:
        without_verification = GOOD_SKILL.replace(
            "## 验收\n\n- [ ] 已输出报告\n- [ ] 分数与脚本一致\n\n",
            "",
        ).replace("完成标准:", "结果:")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "score-drop-skill", GOOD_SKILL)
            baseline = capture_baseline(target, root / "baseline.json")
            (target / "SKILL.md").write_text(
                without_verification.format(name="score-drop-skill"),
                encoding="utf-8",
            )
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 0)
        self.assertEqual(
            report["scores"]["basic_usable"]["direction"],
            "regressed",
        )
        self.assertFalse(report["hard_regression"])
        self.assertEqual(
            report["gates"]["gate_verdict"]["direction"],
            "unchanged",
        )
        self.assertEqual(report["gates"]["gate_verdict"]["after"], "pass")

    def test_new_critical_marks_the_fix_as_regressed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "broken-skill", GOOD_SKILL)
            baseline = capture_baseline(target, root / "baseline.json")
            (target / "SKILL.md").write_text(
                WEAK_SKILL, encoding="utf-8"
            )
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "regressed")
        self.assertTrue(report["regression_detected"])
        self.assertGreater(report["findings"]["counts"]["new_critical"], 0)
        self.assertEqual(
            report["gates"]["gate_verdict"]["direction"],
            "regressed",
        )
        self.assertEqual(report["gates"]["ship_floor"]["direction"], "regressed")

    def test_rewrite_that_adds_an_unguarded_loop_is_reported_not_hidden(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "mixed-skill", WEAK_SKILL)
            baseline = capture_baseline(target, root / "baseline.json")
            (target / "SKILL.md").write_text(
                partly_fixed_skill("mixed-skill"), encoding="utf-8"
            )
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 0)
        self.assertEqual(report["verdict"], "improved")
        self.assertFalse(report["hard_regression"])
        self.assertIn(
            "EFF.1",
            [item["id"] for item in report["findings"]["introduced"]],
        )

    def test_strict_mode_fails_on_a_newly_introduced_non_critical_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "mixed-skill", WEAK_SKILL)
            baseline = capture_baseline(target, root / "baseline.json")
            (target / "SKILL.md").write_text(
                partly_fixed_skill("mixed-skill"), encoding="utf-8"
            )
            code, report = run_verify(target, baseline, strict=True)
        self.assertEqual(code, 1)
        self.assertTrue(report["strict"])
        self.assertTrue(report["regression_detected"])
        self.assertFalse(report["hard_regression"])


class BadInputTests(unittest.TestCase):
    def test_non_report_baseline_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "steady-skill", GOOD_SKILL)
            baseline = root / "notes.json"
            baseline.write_text('{"note": "not a report"}', encoding="utf-8")
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "not_verified")
        self.assertIn("hard_gates", report["error"])

    def test_missing_skill_md_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = write_skill(root, "steady-skill", GOOD_SKILL)
            baseline = capture_baseline(target, root / "baseline.json")
            (target / "SKILL.md").unlink()
            code, report = run_verify(target, baseline)
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "not_verified")


if __name__ == "__main__":
    unittest.main(verbosity=2)
