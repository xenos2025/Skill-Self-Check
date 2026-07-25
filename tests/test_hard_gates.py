#!/usr/bin/env python3
"""Regression tests for scripts/hard_gates.py (stdlib only).

Run:
  python tests/test_hard_gates.py
"""

from __future__ import annotations

import json
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
        self.assertEqual(report["scores"]["basic_usable"]["score"], 5)
        self.assertEqual(report["scores"]["contract_clarity"]["score"], 5)
        self.assertEqual(report["counts"]["critical"], 0)
        kit = report["scores"]["support_kit"]
        self.assertTrue(kit["kit_complete"])
        self.assertEqual(kit["modules"]["references"]["status"], "pass")
        self.assertEqual(kit["modules"]["examples"]["status"], "pass")
        self.assertEqual(kit["modules"]["scripts"]["status"], "pass")
        self.assertEqual(kit["modules"]["memory"]["status"], "na")

    def test_bad_fixture_fails_ship_floor(self) -> None:
        code, report = run_script(BAD_FIXTURE)
        self.assertEqual(code, 1)
        self.assertFalse(report["scores"]["ship_floor_met"])
        self.assertGreater(report["counts"]["critical"], 0)

    def test_missing_skill_md_still_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_script(Path(tmp))
        self.assertEqual(code, 1)
        self.assertEqual([f["id"] for f in report["findings"]], ["1.1"])


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


class SupportKitTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
