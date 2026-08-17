#!/usr/bin/env python3
"""Regression tests for skills/skill-ship-safety/scripts/ship_safety.py (stdlib only).

Run:
  python tests/test_ship_safety.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "skill-ship-safety" / "scripts" / "ship_safety.py"
BAD_FIXTURE = (
    REPO / "skills" / "skill-ship-safety" / "examples" / "fixtures" / "promise-gap"
)
SELF_CHECK_SKILL = REPO / "skills" / "skill-self-check"
SHIP_SAFETY_SKILL = REPO / "skills" / "skill-ship-safety"

GOOD_SKILL_MD = """---
name: good-cli
description: Fixture with a fully implemented documented command. Use when testing.
---

# Good CLI

```bash
python3 scripts/tool.py ping <host>
```
"""

GOOD_TOOL_PY = '''#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "ping":
        print("pong")
    else:
        print(f"Unknown command: {sys.argv[1:] or ''}")

if __name__ == "__main__":
    main()
'''


def run_script(target: Path, *flags: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(target), *flags],
        capture_output=True,
    )
    payload = json.loads(proc.stdout.decode("utf-8"))
    return proc.returncode, payload


class BadFixtureTests(unittest.TestCase):
    def test_promise_gap_stops_ship(self) -> None:
        code, report = run_script(BAD_FIXTURE)
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "stop_ship")
        ids = [f["id"] for f in report["findings"]]
        self.assertIn("CMD.1", ids, "missing script must be flagged")
        self.assertIn("CMD.2", ids, "unimplemented subcommand must be flagged")
        self.assertIn("EXT.1", ids, "smtplib without dry-run guard must be flagged")
        crit_ids = [f["id"] for f in report["findings"] if f["severity"] == "critical"]
        self.assertIn("CMD.2", crit_ids)
        self.assertIn("EXT.1", crit_ids)

    def test_exec_is_refused_without_trusted_isolation(self) -> None:
        code, report = run_script(BAD_FIXTURE, "--exec")
        self.assertEqual(code, 1)
        self.assertFalse(report["execution"]["performed"])
        self.assertEqual(report["execution"]["status"], "not_safely_verified")
        self.assertIn("EXEC.0", [f["id"] for f in report["findings"]])


class CleanTargetTests(unittest.TestCase):
    def test_node_shopify_cli_and_graphql_mutation_are_inventoried(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "multi-runtime"
            (skill / "scripts").mkdir(parents=True)
            (skill / "graphql").mkdir()
            (skill / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "multi-runtime")
                + "\nnode scripts/helper.mjs sync\n"
                + "shopify store auth --store example.myshopify.com --scopes read_products\n"
                + "shopify store execute --store example.myshopify.com --query-file graphql/update.graphql\n",
                encoding="utf-8",
            )
            (skill / "scripts" / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            (skill / "scripts" / "helper.mjs").write_text("console.log('sync');\n", encoding="utf-8")
            (skill / "graphql" / "update.graphql").write_text(
                "mutation UpdateProduct { productUpdate(product: {id: \"gid://shopify/Product/1\"}) { userErrors { message } } }\n",
                encoding="utf-8",
            )
            (skill / "graphql" / "read.graphql").write_text("query ReadShop { shop { name } }\n", encoding="utf-8")
            _, report = run_script(skill)
        kinds = {command["kind"] for command in report["commands"]}
        self.assertTrue({"python", "node", "shopify_cli"} <= kinds)
        capabilities = {
            capability
            for action in report["external_actions"]
            for capability in action["capabilities"]
        }
        self.assertIn("shopify_cli", capabilities)
        self.assertIn("graphql_mutation_definition", capabilities)
        mutation_files = [
            action["file"]
            for action in report["external_actions"]
            if "graphql_mutation_definition" in action["capabilities"]
        ]
        self.assertEqual(["graphql/update.graphql"], mutation_files)

    def test_distinct_shopify_execute_commands_preserve_write_guards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "shopify-commands"
            (skill / "scripts").mkdir(parents=True)
            (skill / "graphql").mkdir()
            (skill / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "shopify-commands")
                + "\nshopify store execute --store example.myshopify.com --query-file graphql/read.graphql\n"
                + "shopify store execute --store example.myshopify.com --query-file graphql/update.graphql\n"
                + "shopify store execute --store example.myshopify.com --query-file graphql/update.graphql --allow-mutations\n"
                + "shopify app execute --store example.myshopify.com --query-file graphql/update.graphql\n",
                encoding="utf-8",
            )
            (skill / "scripts" / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            (skill / "graphql" / "read.graphql").write_text(
                "query ReadShop { shop { name } }\n",
                encoding="utf-8",
            )
            (skill / "graphql" / "update.graphql").write_text(
                "mutation UpdateProduct { productUpdate(product: {id: \"gid://shopify/Product/1\"}) { userErrors { message } } }\n",
                encoding="utf-8",
            )
            code, report = run_script(skill)
        shopify_commands = [
            command for command in report["commands"] if command["kind"] == "shopify_cli"
        ]
        self.assertEqual(4, len(shopify_commands))
        guarded = [
            action
            for action in report["external_actions"]
            if action.get("guard_status") == "mutations_disabled_by_default"
        ]
        self.assertEqual(1, len(guarded))
        critical_writes = [
            finding
            for finding in report["findings"]
            if finding["severity"] == "critical"
            and "business_data_write" in finding["message"]
        ]
        self.assertEqual(2, len(critical_writes))
        self.assertEqual(1, code)

    def test_unreferenced_graphql_mutation_is_inventory_not_stop_ship(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "mutation-library"
            (skill / "scripts").mkdir(parents=True)
            (skill / "graphql").mkdir()
            (skill / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "mutation-library"),
                encoding="utf-8",
            )
            (skill / "scripts" / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            (skill / "graphql" / "update.graphql").write_text(
                "mutation UpdateProduct { productUpdate(product: {id: \"gid://shopify/Product/1\"}) { userErrors { message } } }\n",
                encoding="utf-8",
            )
            code, report = run_script(skill)
        self.assertEqual(0, code, report["findings"])
        self.assertEqual(0, report["counts"]["critical"])
        self.assertIn(
            "graphql_mutation_definition",
            report["external_actions"][0]["capabilities"],
        )

    def test_repo_relative_command_resolves_only_from_approved_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "pack"
            target = repo / "skills" / "target"
            sibling = repo / "skills" / "shared" / "scripts"
            target.mkdir(parents=True)
            sibling.mkdir(parents=True)
            (target / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "target").replace(
                    "python3 scripts/tool.py ping <host>",
                    "python3 skills/shared/scripts/tool.py ping",
                ),
                encoding="utf-8",
            )
            (sibling / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            code, report = run_script(target, "--repo-root", str(repo))
        self.assertEqual(0, code, report["findings"])
        self.assertEqual("repo", report["commands"][0]["resolution_scope"])

    def test_repo_relative_command_does_not_fall_back_to_target_basename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "pack"
            target = repo / "skills" / "target"
            local_scripts = target / "scripts"
            local_scripts.mkdir(parents=True)
            (target / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "target").replace(
                    "python3 scripts/tool.py ping <host>",
                    "python3 skills/shared/scripts/tool.py ping",
                ),
                encoding="utf-8",
            )
            (local_scripts / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            code, report = run_script(target, "--repo-root", str(repo))
        self.assertEqual(1, code)
        self.assertIn("CMD.1", [finding["id"] for finding in report["findings"]])

    def test_repo_relative_command_auto_detects_nearest_git_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "pack"
            target = repo / "skills" / "target"
            sibling = repo / "skills" / "shared" / "scripts"
            (repo / ".git").mkdir(parents=True)
            target.mkdir(parents=True)
            sibling.mkdir(parents=True)
            (target / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "target").replace(
                    "python3 scripts/tool.py ping <host>",
                    "python3 skills/shared/scripts/tool.py ping",
                ),
                encoding="utf-8",
            )
            (sibling / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            code, report = run_script(target)
        self.assertEqual(0, code, report["findings"])
        self.assertEqual("repo", report["commands"][0]["resolution_scope"])

    def test_repo_relative_path_traversal_remains_critical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "pack"
            target = repo / "skills" / "target"
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "target").replace(
                    "python3 scripts/tool.py ping <host>",
                    "python3 skills/../outside/tool.py ping",
                ),
                encoding="utf-8",
            )
            code, report = run_script(target, "--repo-root", str(repo))
        self.assertEqual(1, code)
        self.assertIn("CMD.1", [finding["id"] for finding in report["findings"]])

    def test_fully_implemented_command_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "good-cli"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(GOOD_SKILL_MD, encoding="utf-8")
            (skill / "scripts" / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            code, report = run_script(skill)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["schema_version"], "1.0")
        self.assertEqual(report["audit_level"], "static_safety_scan")
        self.assertEqual(report["target_platform"], "generic")
        self.assertTrue(report["limitations"])
        self.assertEqual(report["verdict"], "static_pass")
        cmd = report["commands"][0]
        self.assertTrue(cmd["script_exists"])
        self.assertTrue(cmd["subcommand_implemented"])
        self.assertEqual(cmd["probe"]["status"], "not_run")

    def test_comment_only_subcommand_is_not_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "comment-cli"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "comment-cli").replace("ping", "deploy"),
                encoding="utf-8",
            )
            (skill / "scripts" / "tool.py").write_text(
                "# TODO: implement deploy\nprint('not implemented')\n",
                encoding="utf-8",
            )
            code, report = run_script(skill)
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "stop_ship")
        self.assertIn("CMD.2", [f["id"] for f in report["findings"]])

    def test_exec_request_on_clean_target_is_unverified_not_passed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "good-cli"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(GOOD_SKILL_MD, encoding="utf-8")
            (skill / "scripts" / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            code, report = run_script(skill, "--exec")
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "execution_unverified")
        self.assertFalse(report["execution"]["performed"])

    def test_placeholder_command_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "placeholder-cli"
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "placeholder-cli"),
                encoding="utf-8",
            )
            (skill / "scripts").mkdir()
            (skill / "scripts" / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            (skill / "references" / "template.md").write_text(
                "python scripts/<sender>.py batch.json\n",
                encoding="utf-8",
            )
            code, report = run_script(skill)
        self.assertEqual(code, 0, report["findings"])
        self.assertNotIn("CMD.1", [f["id"] for f in report["findings"]])

    def test_from_import_network_capability_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "network-cli"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "network-cli"),
                encoding="utf-8",
            )
            (skill / "scripts" / "tool.py").write_text(
                "from urllib import request\n"
                "import sys\n"
                "DRY_RUN = True\n"
                "if len(sys.argv) > 1 and sys.argv[1] == 'ping':\n"
                "    print(request)\n",
                encoding="utf-8",
            )
            code, report = run_script(skill)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["external_actions"][0]["capabilities"], ["network"])

    def test_self_check_skill_has_no_criticals(self) -> None:
        code, report = run_script(SELF_CHECK_SKILL)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["counts"]["critical"], 0)

    def test_ship_safety_skill_ignores_its_unsafe_fixture(self) -> None:
        code, report = run_script(SHIP_SAFETY_SKILL)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["verdict"], "static_pass")
        self.assertEqual(report["counts"]["critical"], 0)
        self.assertEqual(report["external_actions"], [])

    def test_dual_report_templates_are_wired(self) -> None:
        skill_text = (SHIP_SAFETY_SKILL / "SKILL.md").read_text(encoding="utf-8")
        for name in ("REPORT-BUSINESS-TEMPLATE.md", "REPORT-TEMPLATE.md"):
            self.assertTrue((SHIP_SAFETY_SKILL / name).is_file())
            self.assertIn(name, skill_text)

    def test_missing_skill_md_stops_ship(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_script(Path(tmp))
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "stop_ship")
        self.assertEqual(report["findings"][0]["id"], "CMD.0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
