import unittest
import tempfile
from pathlib import Path
from test_hard_gates import ZH_SKILL, write_skill, run_script

class AuditHelper:
    def audit(self, *, description):
        with tempfile.TemporaryDirectory() as folder:
            body=ZH_SKILL.replace("检查中文技能说明书的结构，用于用户写完说明书后需要一次自检时。",description)
            target=write_skill(Path(folder),"sample",body)
            return run_script(target,"--repo-root",folder)[1]
    def ids(self, report):
        return {item["id"] for item in report["findings"]}

class UseForTests(unittest.TestCase):
    def test_scoped_use_for_descriptions(self):
        helper = AuditHelper()
        for description in ("Use for evidence-backed crawl audits and technical validation.",
                            "Use for Codex models/pricing, scheduled tasks and configuration.",
                            "Reviews crawl evidence. Use for website audit reports."):
            with self.subTest(description=description):
                self.assertNotIn("1.7", helper.ids(helper.audit(description=description)))

    def test_vague_and_negated_remain_failures(self):
        helper = AuditHelper()
        for description in ("Use for anything.", "Use for general assistance.", "Use for audits.",
                            "Reviews files. Do not use for crawl audits.", "Use for everything including crawl audits."):
            with self.subTest(description=description):
                self.assertIn("1.7", helper.ids(helper.audit(description=description)))

if __name__ == "__main__": unittest.main()
