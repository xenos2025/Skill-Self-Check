#!/usr/bin/env python3
"""Regression tests for the public skill installers."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
POWERSHELL_INSTALLER = REPO / "install.ps1"
BASH_INSTALLER = REPO / "install.sh"
SHIP_SAFETY_SKILL = REPO / "skills" / "skill-ship-safety"


class InstallerTests(unittest.TestCase):
    def test_shipped_ship_safety_retains_a_runtime_example(self) -> None:
        examples = SHIP_SAFETY_SKILL / "examples"
        retained = [
            path
            for path in examples.rglob("*")
            if path.is_file()
            and "fixtures" not in path.relative_to(examples).parts
        ]
        self.assertTrue(
            retained,
            "installers remove examples/fixtures, so ship-safety needs a runtime example",
        )

    @contextmanager
    def source_skill(self) -> Iterator[tuple[Path, str]]:
        with tempfile.TemporaryDirectory(
            prefix="installer-test-", dir=REPO / "skills"
        ) as source_dir:
            source = Path(source_dir)
            skill_name = source.name
            retained_files = {
                "SKILL.md": (
                    f"---\nname: {skill_name}\ndescription: Installer fixture.\n"
                    "---\n\n# Fixture\n"
                ),
                "examples/before-after.md": "retained example\n",
                "scripts/run.py": "print('fixture')\n",
            }
            excluded_files = {
                "tests/test_fixture.py": "raise AssertionError\n",
                "examples/fixtures/nested/SKILL.md": "fixture-only skill\n",
                "backup/SKILL.md": "old skill\n",
                "backups/old.txt": "old content\n",
                "nested/backup/old.txt": "old content\n",
                "nested/backups/old.txt": "old content\n",
                "SKILL.md.bak": "old root skill\n",
                "notes.backup": "old notes\n",
                "nested/OLD.BAK": "old content\n",
                "__pycache__/fixture.pyc": "compiled residue\n",
            }
            for relative_path, content in (retained_files | excluded_files).items():
                path = source / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            yield source, skill_name

    def assert_runtime_package(self, installed: Path) -> None:
        self.assertTrue((installed / "SKILL.md").is_file())
        self.assertTrue((installed / "examples" / "before-after.md").is_file())

        skill_files = sorted(path.relative_to(installed) for path in installed.rglob("SKILL.md"))
        self.assertEqual(skill_files, [Path("SKILL.md")])

        installed_paths = [path.relative_to(installed) for path in installed.rglob("*")]
        for path in installed_paths:
            lower_parts = tuple(part.lower() for part in path.parts)
            self.assertNotEqual(lower_parts[:1], ("tests",))
            self.assertNotEqual(lower_parts[:2], ("examples", "fixtures"))
            self.assertFalse({"backup", "backups"}.intersection(lower_parts))
            self.assertNotIn("__pycache__", lower_parts)
            self.assertNotIn(path.suffix.lower(), {".bak", ".backup", ".pyc"})

    def test_powershell_installer_excludes_maintainer_only_content(self) -> None:
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if powershell is None:
            self.skipTest("PowerShell is unavailable")

        with self.source_skill() as (_, skill_name), tempfile.TemporaryDirectory(
            dir=REPO
        ) as temp_dir:
            installed = Path(temp_dir) / skill_name
            proc = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(POWERSHELL_INSTALLER),
                    "-Dest",
                    str(installed),
                    "-Skills",
                    skill_name,
                ],
                capture_output=True,
                check=False,
                encoding="utf-8",
                errors="replace",
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            self.assert_runtime_package(installed)

    def test_bash_installer_excludes_maintainer_only_content(self) -> None:
        bash = shutil.which("bash")
        if bash is None:
            for candidate in (
                Path(r"C:\Program Files\Git\bin\bash.exe"),
                Path(r"C:\Program Files\Git\usr\bin\bash.exe"),
            ):
                if candidate.is_file():
                    bash = str(candidate)
                    break
        if bash is None:
            self.skipTest("Bash is unavailable")

        with self.source_skill() as (_, skill_name), tempfile.TemporaryDirectory(
            dir=REPO
        ) as temp_dir:
            installed = Path(temp_dir) / skill_name
            proc = subprocess.run(
                [
                    bash,
                    str(BASH_INSTALLER),
                    "--dest",
                    str(installed),
                    "--skills",
                    skill_name,
                ],
                capture_output=True,
                check=False,
                encoding="utf-8",
                errors="replace",
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            self.assert_runtime_package(installed)


if __name__ == "__main__":
    unittest.main()
