#!/usr/bin/env python3
"""Regression tests for skill-growth-scorecard/scripts/profile_engine.py."""

from __future__ import annotations

import json
import re
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "skill-growth-scorecard"
SCRIPT = SKILL / "scripts" / "profile_engine.py"
FIXTURE = SKILL / "examples" / "fixtures" / "basic-profile"
READINESS = FIXTURE / "readiness.json"
HARD = FIXTURE / "hard-gates.json"
SAFETY = FIXTURE / "ship-safety.json"


def run_script(*args: str | Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        capture_output=True,
    )
    return proc.returncode, json.loads(proc.stdout.decode("utf-8"))


class ProfileEngineTests(unittest.TestCase):
    def test_combined_fixture_preserves_stop_ship_and_business_priority(self) -> None:
        code, profile = run_script(
            "--readiness",
            READINESS,
            "--hard-gates",
            HARD,
            "--ship-safety",
            SAFETY,
        )
        self.assertEqual(code, 0, profile)
        self.assertEqual(profile["business_readiness"]["level"]["id"], "B1")
        self.assertEqual(profile["skill_engineering"]["level"]["id"], "Lv1")
        self.assertEqual(profile["verdict"], "stop_ship")
        self.assertEqual(profile["next_quest"]["lane"], "business_readiness")
        self.assertEqual(profile["counts"]["critical"], 1)
        interpretation = profile["skill_engineering"]["personal_interpretation"]
        self.assertEqual(
            interpretation["headline"],
            "你能把模糊任务梳理成一条可执行路线",
        )
        self.assertIn("目前仍处于起步阶段", interpretation["summary"])
        self.assertIn("使用边界、实现一致性和安全验证", interpretation["summary"])
        self.assertNotIn("类型讲", interpretation["summary"])
        learning = profile["skill_engineering"]["learning_quest"]
        self.assertEqual(learning["lane"], "personal_capability")
        learning_text = json.dumps(learning, ensure_ascii=False)
        self.assertIn("Harness", learning_text)
        self.assertNotIn("CMD.", learning_text)
        self.assertEqual(
            profile["subject"],
            {
                "kind": "skill",
                "label": "Skill",
                "name": "example-skill",
                "source": "hard_gates.frontmatter.name",
            },
        )

    def test_blocking_quest_uses_beginner_facing_language(self) -> None:
        code, profile = run_script("--hard-gates", HARD, "--ship-safety", SAFETY)
        self.assertEqual(code, 0, profile)
        quest = profile["next_quest"]
        self.assertEqual(quest["title"], "补齐实现与安全控制能力")
        self.assertIn("说明书", quest["action"])
        self.assertNotIn("critical", quest["acceptance"])

    def test_readiness_only_does_not_invent_skill_level(self) -> None:
        code, profile = run_script("--readiness", READINESS)
        self.assertEqual(code, 0, profile)
        self.assertEqual(profile["skill_engineering"]["status"], "not_started")
        self.assertIsNone(profile["skill_engineering"]["level"])
        self.assertEqual(profile["verdict"], "planning")
        self.assertEqual(profile["subject"]["kind"], "work_process")
        self.assertEqual(profile["subject"]["name"], "每周询盘复盘")
        self.assertEqual(
            profile["subject"]["source"],
            "readiness.input.process_name",
        )
        self.assertEqual(
            profile["skill_engineering"]["learning_quest"]["lane"],
            "personal_capability",
        )

    def test_every_skill_level_has_a_personal_learning_quest(self) -> None:
        module = runpy.run_path(str(SCRIPT))
        templates = module["LEVEL_LEARNING_QUESTS"]
        self.assertEqual(set(templates), set(range(6)))
        for level, quest in templates.items():
            with self.subTest(level=level):
                self.assertTrue(quest["title"])
                self.assertTrue(quest["action"])
                self.assertGreaterEqual(len(quest["practice_points"]), 3)
                self.assertTrue(quest["acceptance"])

    def test_automation_beginner_learns_reuse_judgment_and_harness_position(
        self,
    ) -> None:
        hard = json.loads(HARD.read_text(encoding="utf-8"))
        safety = json.loads(SAFETY.read_text(encoding="utf-8"))
        hard["scores"]["basic_usable"]["score"] = 5
        hard["scores"]["contract_clarity"]["score"] = 1
        hard["scores"]["support_kit"]["score"] = 3
        hard["scores"]["support_kit"]["max"] = 4
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hard_path = root / "hard.json"
            safety_path = root / "safety.json"
            hard_path.write_text(json.dumps(hard), encoding="utf-8")
            safety_path.write_text(json.dumps(safety), encoding="utf-8")
            code, profile = run_script(
                "--hard-gates",
                hard_path,
                "--ship-safety",
                safety_path,
            )
        self.assertEqual(code, 0, profile)
        engineering = profile["skill_engineering"]
        self.assertEqual(engineering["archetype"]["id"], "automation-craftsperson")
        learning = engineering["learning_quest"]
        self.assertEqual(
            learning["title"],
            "练习把自动化脚本接入可验证的工程闭环",
        )
        labels = [item["label"] for item in learning["practice_points"]]
        self.assertEqual(
            labels,
            ["量化目标", "判断流程", "可复用脚本", "Harness 位置"],
        )
        self.assertIn("目标 Skill 外部", learning["practice_points"][3]["text"])
        self.assertNotIn("CMD.", json.dumps(learning, ensure_ascii=False))

    def test_explicit_subject_name_overrides_report_metadata(self) -> None:
        code, profile = run_script(
            "--hard-gates",
            HARD,
            "--subject-name",
            "  customer-support\nassistant  ",
        )
        self.assertEqual(code, 0, profile)
        self.assertEqual(profile["subject"]["kind"], "skill")
        self.assertEqual(profile["subject"]["name"], "customer-support assistant")
        self.assertEqual(profile["subject"]["source"], "argument")

    def test_clean_static_inputs_unlock_static_level_only(self) -> None:
        hard = json.loads(HARD.read_text(encoding="utf-8"))
        safety = json.loads(SAFETY.read_text(encoding="utf-8"))
        hard["scores"]["contract_clarity"]["score"] = 5
        hard["scores"]["support_kit"]["score"] = 4
        hard["scores"]["support_kit"]["kit_complete"] = True
        hard["findings"] = []
        safety["verdict"] = "static_pass"
        safety["counts"]["critical"] = 0
        safety["execution"]["status"] = "not_run"
        safety["findings"] = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hard_path = root / "hard.json"
            safety_path = root / "safety.json"
            hard_path.write_text(json.dumps(hard), encoding="utf-8")
            safety_path.write_text(json.dumps(safety), encoding="utf-8")
            code, profile = run_script(
                "--hard-gates",
                hard_path,
                "--ship-safety",
                safety_path,
            )
        self.assertEqual(code, 0, profile)
        self.assertEqual(profile["skill_engineering"]["level"]["id"], "Lv2")
        self.assertEqual(profile["verdict"], "needs_evidence")

    def test_behavior_and_two_verified_platforms_unlock_expert_level(self) -> None:
        hard = json.loads(HARD.read_text(encoding="utf-8"))
        safety = json.loads(SAFETY.read_text(encoding="utf-8"))
        hard["scores"]["contract_clarity"]["score"] = 5
        hard["scores"]["support_kit"]["score"] = 4
        hard["scores"]["support_kit"]["kit_complete"] = True
        hard["findings"] = []
        safety["verdict"] = "static_pass"
        safety["counts"]["critical"] = 0
        safety["findings"] = []
        behavior = {
            "core_flow_tested": True,
            "pdca_evidence": True,
            "safe_external_actions": True,
            "write_back_integrity": True,
            "failure_recovery": True,
            "portable_contract": True,
            "platforms": [
                {
                    "name": "Platform A",
                    "status": "verified",
                    "evidence": "evidence/a.json",
                    "contract_id": f"sha256:{'a' * 64}",
                    "fixture_id": f"sha256:{'b' * 64}",
                },
                {
                    "name": "Platform B",
                    "status": "verified",
                    "evidence": "evidence/b.json",
                    "contract_id": f"sha256:{'a' * 64}",
                    "fixture_id": f"sha256:{'b' * 64}",
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hard_path = root / "hard.json"
            safety_path = root / "safety.json"
            behavior_path = root / "behavior.json"
            hard_path.write_text(json.dumps(hard), encoding="utf-8")
            safety_path.write_text(json.dumps(safety), encoding="utf-8")
            behavior_path.write_text(json.dumps(behavior), encoding="utf-8")
            code, profile = run_script(
                "--hard-gates",
                hard_path,
                "--ship-safety",
                safety_path,
                "--behavior",
                behavior_path,
            )
        self.assertEqual(code, 0, profile)
        self.assertEqual(profile["skill_engineering"]["level"]["id"], "Lv5")
        self.assertEqual(profile["skill_engineering"]["archetype"]["id"], "balanced")
        self.assertEqual(profile["verdict"], "ready_for_controlled_use")
        interpretation = profile["skill_engineering"]["personal_interpretation"]
        self.assertEqual(
            interpretation["headline"],
            "你已经能把六项 Skill 能力连成完整闭环",
        )
        self.assertIn("目前已进入专家阶段", interpretation["summary"])
        self.assertTrue(
            all(
                axis["state"] == 4
                for axis in profile["skill_engineering"]["dimensions"].values()
            )
        )
        portability = profile["skill_engineering"]["portability"]
        self.assertEqual(portability["verified_platform_count"], 2)
        self.assertEqual(portability["contract_id"], f"sha256:{'a' * 64}")
        self.assertEqual(portability["fixture_id"], f"sha256:{'b' * 64}")

    def test_verified_not_applicable_controls_unlock_closed_loop_level(self) -> None:
        hard = json.loads(HARD.read_text(encoding="utf-8"))
        safety = json.loads(SAFETY.read_text(encoding="utf-8"))
        hard["scores"]["contract_clarity"]["score"] = 5
        hard["scores"]["support_kit"]["score"] = 4
        hard["scores"]["support_kit"]["kit_complete"] = True
        hard["findings"] = []
        safety["verdict"] = "static_pass"
        safety["counts"]["critical"] = 0
        safety["findings"] = []
        safety["external_actions"] = []
        behavior = {
            "core_flow_tested": True,
            "pdca_evidence": True,
            "safe_external_actions": False,
            "write_back_integrity": False,
            "failure_recovery": True,
            "portable_contract": False,
            "target_unchanged": True,
            "applicability": {
                "external_actions": {
                    "status": "not_applicable",
                    "evidence": "audit-manifest.json#external-actions",
                },
                "write_back": {
                    "status": "not_applicable",
                    "evidence": "audit-manifest.json#target-integrity",
                },
            },
            "platforms": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hard_path = root / "hard.json"
            safety_path = root / "safety.json"
            behavior_path = root / "behavior.json"
            hard_path.write_text(json.dumps(hard), encoding="utf-8")
            safety_path.write_text(json.dumps(safety), encoding="utf-8")
            behavior_path.write_text(json.dumps(behavior), encoding="utf-8")
            code, profile = run_script(
                "--hard-gates",
                hard_path,
                "--ship-safety",
                safety_path,
                "--behavior",
                behavior_path,
            )
        self.assertEqual(code, 0, profile)
        engineering = profile["skill_engineering"]
        self.assertEqual(engineering["level"]["id"], "Lv4")
        self.assertEqual(
            engineering["dimensions"]["safety_control"]["state"],
            4,
        )
        applicability = engineering["safety"]["applicability"]
        self.assertTrue(applicability["external_actions"]["satisfied"])
        self.assertTrue(applicability["write_back"]["satisfied"])
        self.assertIn(
            "不适用项有证据",
            [item["label"] for item in engineering["badges"]],
        )

    def test_not_applicable_without_evidence_does_not_unlock_level(self) -> None:
        hard = json.loads(HARD.read_text(encoding="utf-8"))
        safety = json.loads(SAFETY.read_text(encoding="utf-8"))
        hard["scores"]["contract_clarity"]["score"] = 5
        hard["scores"]["support_kit"]["score"] = 4
        hard["scores"]["support_kit"]["kit_complete"] = True
        hard["findings"] = []
        safety["verdict"] = "static_pass"
        safety["counts"]["critical"] = 0
        safety["findings"] = []
        safety["external_actions"] = []
        behavior = {
            "core_flow_tested": True,
            "pdca_evidence": True,
            "failure_recovery": True,
            "target_unchanged": False,
            "applicability": {
                "external_actions": {"status": "not_applicable", "evidence": ""},
                "write_back": {
                    "status": "not_applicable",
                    "evidence": "C:\\private\\manifest.json",
                },
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hard_path = root / "hard.json"
            safety_path = root / "safety.json"
            behavior_path = root / "behavior.json"
            hard_path.write_text(json.dumps(hard), encoding="utf-8")
            safety_path.write_text(json.dumps(safety), encoding="utf-8")
            behavior_path.write_text(json.dumps(behavior), encoding="utf-8")
            code, profile = run_script(
                "--hard-gates",
                hard_path,
                "--ship-safety",
                safety_path,
                "--behavior",
                behavior_path,
            )
        self.assertEqual(code, 0, profile)
        engineering = profile["skill_engineering"]
        self.assertEqual(engineering["level"]["id"], "Lv3")
        self.assertFalse(
            engineering["safety"]["applicability"]["external_actions"]["satisfied"]
        )
        self.assertFalse(
            engineering["safety"]["applicability"]["write_back"]["satisfied"]
        )

    def test_platform_records_must_share_contract_and_fixture(self) -> None:
        hard = json.loads(HARD.read_text(encoding="utf-8"))
        safety = json.loads(SAFETY.read_text(encoding="utf-8"))
        hard["scores"]["contract_clarity"]["score"] = 5
        hard["scores"]["support_kit"]["score"] = 4
        hard["scores"]["support_kit"]["kit_complete"] = True
        hard["findings"] = []
        safety["verdict"] = "static_pass"
        safety["counts"]["critical"] = 0
        safety["findings"] = []
        behavior = {
            "core_flow_tested": True,
            "pdca_evidence": True,
            "safe_external_actions": True,
            "write_back_integrity": True,
            "failure_recovery": True,
            "portable_contract": True,
            "platforms": [
                {
                    "name": "Platform A",
                    "status": "verified",
                    "evidence": "evidence/a.json",
                    "contract_id": f"sha256:{'a' * 64}",
                    "fixture_id": f"sha256:{'b' * 64}",
                },
                {
                    "name": "Platform B",
                    "status": "verified",
                    "evidence": "evidence/b.json",
                    "contract_id": f"sha256:{'a' * 64}",
                    "fixture_id": f"sha256:{'c' * 64}",
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hard_path = root / "hard.json"
            safety_path = root / "safety.json"
            behavior_path = root / "behavior.json"
            hard_path.write_text(json.dumps(hard), encoding="utf-8")
            safety_path.write_text(json.dumps(safety), encoding="utf-8")
            behavior_path.write_text(json.dumps(behavior), encoding="utf-8")
            code, profile = run_script(
                "--hard-gates",
                hard_path,
                "--ship-safety",
                safety_path,
                "--behavior",
                behavior_path,
            )
        self.assertEqual(code, 0, profile)
        engineering = profile["skill_engineering"]
        self.assertEqual(engineering["level"]["id"], "Lv4")
        self.assertEqual(
            engineering["portability"]["verified_platform_count"],
            1,
        )

    def test_static_evidence_cannot_display_full_coverage(self) -> None:
        hard = json.loads(HARD.read_text(encoding="utf-8"))
        safety = json.loads(SAFETY.read_text(encoding="utf-8"))
        hard["scores"]["contract_clarity"]["score"] = 5
        hard["scores"]["support_kit"]["score"] = 4
        hard["scores"]["support_kit"]["kit_complete"] = True
        hard["findings"] = []
        safety["verdict"] = "static_pass"
        safety["counts"]["critical"] = 0
        safety["execution"]["status"] = "not_run"
        safety["findings"] = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hard_path = root / "hard.json"
            safety_path = root / "safety.json"
            hard_path.write_text(json.dumps(hard), encoding="utf-8")
            safety_path.write_text(json.dumps(safety), encoding="utf-8")
            code, profile = run_script(
                "--hard-gates",
                hard_path,
                "--ship-safety",
                safety_path,
            )
        self.assertEqual(code, 0, profile)
        self.assertTrue(
            all(
                axis["state"] <= 2
                for axis in profile["skill_engineering"]["dimensions"].values()
            )
        )

    def test_behavior_cannot_override_static_safety_red_light(self) -> None:
        hard = json.loads(HARD.read_text(encoding="utf-8"))
        safety = json.loads(SAFETY.read_text(encoding="utf-8"))
        behavior = {
            "core_flow_tested": True,
            "pdca_evidence": True,
            "safe_external_actions": True,
            "write_back_integrity": True,
            "failure_recovery": True,
            "portable_contract": True,
            "platforms": [
                {"name": "Platform A", "status": "verified", "evidence": "a.md"},
                {"name": "Platform B", "status": "verified", "evidence": "b.md"},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hard_path = root / "hard.json"
            safety_path = root / "safety.json"
            behavior_path = root / "behavior.json"
            hard_path.write_text(json.dumps(hard), encoding="utf-8")
            safety_path.write_text(json.dumps(safety), encoding="utf-8")
            behavior_path.write_text(json.dumps(behavior), encoding="utf-8")
            code, profile = run_script(
                "--hard-gates",
                hard_path,
                "--ship-safety",
                safety_path,
                "--behavior",
                behavior_path,
            )
        self.assertEqual(code, 0, profile)
        self.assertEqual(profile["verdict"], "stop_ship")
        self.assertEqual(
            profile["skill_engineering"]["dimensions"]["safety_control"]["state"],
            0,
        )

    def test_html_is_single_file_offline_view_of_same_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            json_path = root / "profile.json"
            html_path = root / "profile.html"
            code, stdout_profile = run_script(
                "--readiness",
                READINESS,
                "--hard-gates",
                HARD,
                "--ship-safety",
                SAFETY,
                "--out-json",
                json_path,
                "--out-html",
                html_path,
            )
            stored_profile = json.loads(json_path.read_text(encoding="utf-8"))
            html = html_path.read_text(encoding="utf-8")
        self.assertEqual(code, 0, stdout_profile)
        self.assertEqual(stored_profile, stdout_profile)
        self.assertIn("成长画像", html)
        self.assertIn("检测结果", html)
        self.assertIn("技术证据", html)
        self.assertIn("YOUR SKILL-BUILDING TYPE IS", html)
        self.assertIn("DNA 证据轴", html)
        self.assertIn('class="skill-avatar"', html)
        self.assertIn("达到 100%", html)
        self.assertNotIn("待补证据", html)
        self.assertIn("你的能力画像", html)
        self.assertIn('id="ability-summary-copy"', html)
        self.assertNotIn("类型讲创作风格", html)
        self.assertIn("个人能力下一关", html)
        self.assertIn('id="quest-practice"', html)
        self.assertIn("练成标准", html)
        self.assertIn("项目优先整改", html)
        self.assertIn('id="project-quest-title"', html)
        self.assertIn("项目交付状态", html)
        self.assertNotIn("暂停交付", html)
        self.assertIn('id="ability-level-id"', html)
        self.assertIn('id="subject-name"', html)
        self.assertIn('id="profile-subject-name"', html)
        self.assertIn("example-skill", html)
        self.assertNotIn("__PROFILE_JSON__", html)
        self.assertNotRegex(html, re.compile(r"<script[^>]+src=", re.I))
        self.assertNotRegex(html, re.compile(r"<link[^>]+href=[\"']https?://", re.I))
        self.assertIn('"profile_schema_version": "0.2"', html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
