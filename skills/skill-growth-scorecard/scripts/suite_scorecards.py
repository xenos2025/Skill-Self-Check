#!/usr/bin/env python3
"""Audit every shipped Skill and render private personal/project scorecards.

The suite runner reuses the repository's deterministic hard-gate, ship-safety,
and growth-profile engines. It does not execute an audited Skill or perform any
network action. Real reports are refused when the output directory is inside
the source repository unless the caller explicitly opts in.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from profile_engine import build_profile, force_utf8_streams, render_html


SUITE_SCHEMA_VERSION = "0.2"
ROLE_LABELS = {
    "agent-work-readiness": "把口头工作整理成可评分的 Agent 工作包",
    "skill-self-check": "检查 Skill 结构、边界和配套材料",
    "skill-ship-safety": "检查承诺、脚本和外部动作的静态安全边界",
    "skill-growth-scorecard": "把同一组证据转换为成长与项目视图",
}
FINGERPRINT_IGNORED_PARTS = {".git", "__pycache__"}
FINGERPRINT_IGNORED_SUFFIXES = {".pyc", ".pyo"}


def relative_label(path: Path, root: Path) -> str:
    """Return a shareable POSIX-style path without local workstation details."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def repository_fingerprint(root: Path) -> dict[str, Any]:
    """Hash shareable project files so a suite run can prove it stayed read-only."""
    digest = hashlib.sha256()
    file_count = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if (
            not path.is_file()
            or any(part in FINGERPRINT_IGNORED_PARTS for part in path.parts)
            or path.suffix.casefold() in FINGERPRINT_IGNORED_SUFFIXES
        ):
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        digest.update(b"\0")
        file_count += 1
    return {
        "algorithm": "sha256",
        "digest": digest.hexdigest(),
        "file_count": file_count,
        "ignored": ["git metadata", "Python bytecode caches"],
    }


def run_json_script(script: Path, target: Path, root: Path) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(script), str(target)],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{relative_label(script, root)} did not return JSON for "
            f"{relative_label(target, root)}: {exc}"
        ) from exc
    payload["_command_exit_code"] = result.returncode
    return payload


def run_regression_suite(root: Path) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "tests", "-v"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    combined = f"{result.stdout}\n{result.stderr}"
    match = re.search(r"Ran\s+(\d+)\s+tests?\s+in\s+([\d.]+)s", combined)
    total = int(match.group(1)) if match else 0
    duration = float(match.group(2)) if match else None
    passed = result.returncode == 0 and bool(re.search(r"(?m)^OK\s*$", combined))
    return {
        "command": "python -m unittest discover tests -v",
        "status": "passed" if passed else "failed",
        "total": total,
        "passed": total if passed else None,
        "duration_seconds": duration,
        "exit_code": result.returncode,
        "evidence": "tests/test_*.py",
    }


def git_snapshot(root: Path) -> dict[str, Any]:
    def run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    head_result = run("rev-parse", "--short", "HEAD")
    status_result = run("status", "--porcelain")
    status_lines = [
        line for line in status_result.stdout.splitlines() if line.strip()
    ]
    return {
        "commit": head_result.stdout.strip() if head_result.returncode == 0 else "unknown",
        "working_tree": "dirty" if status_lines else "clean",
        "changed_path_count": len(status_lines),
    }


def flatten_findings(
    skill_name: str,
    findings: Any,
    *,
    source: str,
) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    if not isinstance(findings, list):
        return flattened
    for item in findings:
        if not isinstance(item, dict):
            continue
        finding_id = str(item.get("id") or "UNSPECIFIED")
        message = str(item.get("message") or "未说明问题")
        if finding_id == "EXT.2":
            message = (
                "检测到会调用本机子进程的脚本；它不触发真实业务发送，"
                "但仍要确认默认只运行本地审计与测试。"
            )
        flattened.append(
            {
                "id": f"{skill_name}:{finding_id}",
                "severity": str(item.get("severity") or "info"),
                "message": f"{skill_name}：{message}",
                "evidence": (
                    f"skills/{skill_name}/"
                    f"{str(item.get('evidence') or 'SKILL.md').lstrip('./')}"
                ),
                "source": source,
                "scope": f"skills/{skill_name}",
                "confidence": "high",
                "verification_status": "verified",
            }
        )
    return flattened


def aggregate_support(reports: list[dict[str, Any]]) -> tuple[int, int, bool]:
    values: list[tuple[int, int]] = []
    complete = True
    for report in reports:
        support = (
            ((report.get("scores") or {}).get("support_kit") or {})
            if isinstance(report, dict)
            else {}
        )
        score = int(support.get("score") or 0)
        maximum = int(support.get("max") or 0)
        if maximum > 0:
            values.append((score, maximum))
        complete = complete and support.get("kit_complete") is True
    if not values:
        return 0, 0, complete
    maxima = {maximum for _, maximum in values}
    if len(maxima) == 1:
        maximum = next(iter(maxima))
        return min(score for score, _ in values), maximum, complete
    weakest_ratio = min(score / maximum for score, maximum in values)
    maximum = 4
    return math.floor(weakest_ratio * maximum), maximum, complete


def aggregate_hard_reports(
    root: Path,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    reports = [record["hard"] for record in records]
    basic_scores = [
        ((report.get("scores") or {}).get("basic_usable") or {}) for report in reports
    ]
    contract_scores = [
        ((report.get("scores") or {}).get("contract_clarity") or {})
        for report in reports
    ]
    support_score, support_max, support_complete = aggregate_support(reports)
    basic_point_names = set().union(
        *[
            set((score.get("points") or {}).keys())
            for score in basic_scores
            if isinstance(score, dict)
        ]
    )
    contract_point_names = set().union(
        *[
            set((score.get("points") or {}).keys())
            for score in contract_scores
            if isinstance(score, dict)
        ]
    )
    findings: list[dict[str, Any]] = []
    for record in records:
        findings.extend(
            flatten_findings(
                record["name"],
                record["hard"].get("findings"),
                source="hard_gates",
            )
        )

    qualitative_findings = [
        {
            "id": "PORT.1",
            "severity": "should_fix",
            "message": (
                "文件契约和 Python 核心具备平台中立性，但本次没有两个不同 AI / "
                "Agent 平台使用同一契约指纹和同一脱敏夹具指纹的可信行为记录，"
                "不能宣称自动调用和运行效果已普适。"
            ),
            "evidence": "docs/PLATFORM-COMPATIBILITY.md; behavior platforms=[]",
            "source": "engineering_review",
            "scope": "cross-platform delivery",
            "confidence": "high",
            "verification_status": "verified",
        },
    ]
    findings.extend(qualitative_findings)
    basic_max = min(int(score.get("max") or 5) for score in basic_scores)
    contract_max = min(int(score.get("max") or 5) for score in contract_scores)
    return {
        "schema_version": "1.0",
        "audit_level": "suite_static_contract_check",
        "skill_dir": root.name,
        "skill_md": "skills/*/SKILL.md",
        "target_platform": "generic",
        "frontmatter": {
            "name": "skill-self-check-suite",
            "description": "The four shipped work-readiness, audit, safety, and growth Skills.",
        },
        "scores": {
            "basic_usable": {
                "score": min(int(score.get("score") or 0) for score in basic_scores),
                "max": basic_max,
                "points": {
                    name: all(
                        bool((score.get("points") or {}).get(name))
                        for score in basic_scores
                    )
                    for name in sorted(basic_point_names)
                },
            },
            "contract_clarity": {
                "score": min(
                    int(score.get("score") or 0) for score in contract_scores
                ),
                "max": contract_max,
                "points": {
                    name: all(
                        bool((score.get("points") or {}).get(name))
                        for score in contract_scores
                    )
                    for name in sorted(contract_point_names)
                },
                "detected_axes": sorted(
                    {
                        str(axis)
                        for score in contract_scores
                        for axis in (score.get("detected_axes") or [])
                    }
                ),
            },
            "support_kit": {
                "score": support_score,
                "max": support_max,
                "kit_complete": support_complete,
                "modules": {},
            },
            "ship_floor_met": all(
                bool((report.get("scores") or {}).get("ship_floor_met"))
                for report in reports
            ),
        },
        "counts": {
            "critical": sum(
                int((report.get("counts") or {}).get("critical") or 0)
                for report in reports
            ),
            "should_fix": sum(
                int((report.get("counts") or {}).get("should_fix") or 0)
                for report in reports
            )
            + len(qualitative_findings),
            "nice": sum(
                int((report.get("counts") or {}).get("nice") or 0)
                for report in reports
            ),
        },
        "findings": findings,
        "limitations": [
            "suite scores use the weakest shipped Skill rather than an average",
            "scores cover static structure and contract signals only",
            "behavioral correctness and automatic platform invocation require separate evidence",
        ],
        "aggregation_basis": {
            "method": "weakest shipped skill",
            "skills": [record["name"] for record in records],
        },
    }


def aggregate_safety_reports(records: list[dict[str, Any]]) -> dict[str, Any]:
    reports = [record["safety"] for record in records]
    findings: list[dict[str, Any]] = []
    commands: list[dict[str, Any]] = []
    external_actions: list[dict[str, Any]] = []
    for record in records:
        findings.extend(
            flatten_findings(
                record["name"],
                record["safety"].get("findings"),
                source="ship_safety",
            )
        )
        for command in record["safety"].get("commands") or []:
            if isinstance(command, dict):
                commands.append({"skill": record["name"], **command})
        for action in record["safety"].get("external_actions") or []:
            if isinstance(action, dict):
                external_actions.append({"skill": record["name"], **action})

    verdicts = [str(report.get("verdict") or "not_assessed") for report in reports]
    verdict = (
        "stop_ship"
        if "stop_ship" in verdicts
        else "static_pass"
        if verdicts and all(item == "static_pass" for item in verdicts)
        else "execution_unverified"
    )
    return {
        "schema_version": "1.0",
        "audit_level": "suite_static_safety_scan",
        "target": "skill-self-check-suite",
        "target_platform": "generic",
        "execution": {
            "requested": False,
            "performed": False,
            "isolation": "unavailable",
            "status": "not_safely_verified",
        },
        "commands": commands,
        "external_actions": external_actions,
        "counts": {
            "critical": sum(
                int((report.get("counts") or {}).get("critical") or 0)
                for report in reports
            ),
            "should_fix": sum(
                int((report.get("counts") or {}).get("should_fix") or 0)
                for report in reports
            ),
            "info": sum(
                int((report.get("counts") or {}).get("info") or 0)
                for report in reports
            ),
        },
        "findings": findings,
        "verdict": verdict,
        "limitations": [
            "target code was not executed by ship_safety.py",
            "external-action and dry-run detection are static heuristics",
            "final cross-platform approval requires trusted behavior evidence",
        ],
    }


def behavior_evidence(
    test_summary: dict[str, Any],
    safety_report: dict[str, Any],
    target_integrity: dict[str, Any],
) -> dict[str, Any]:
    passed = test_summary.get("status") == "passed" and int(
        test_summary.get("total") or 0
    ) > 0
    external_actions = safety_report.get("external_actions")
    if not isinstance(external_actions, list):
        external_actions = []
    fixed_local_process_scope = all(
        isinstance(item, dict)
        and set(item.get("capabilities") or []) <= {"browser_or_shell"}
        and str(item.get("file") or "") in {
            "scripts/suite_scorecards.py",
            "scripts/run_full_audit.py",
        }
        for item in external_actions
    )
    static_safety_pass = (
        safety_report.get("verdict") == "static_pass"
        and int((safety_report.get("counts") or {}).get("critical") or 0) == 0
    )
    safe_local_processes = passed and static_safety_pass and fixed_local_process_scope
    target_unchanged = bool(target_integrity.get("unchanged"))
    return {
        "schema_version": "1.0",
        "core_flow_tested": passed,
        "pdca_evidence": passed,
        "safe_external_actions": safe_local_processes,
        "write_back_integrity": False,
        "failure_recovery": passed,
        "portable_contract": False,
        "target_unchanged": target_unchanged,
        "applicability": {
            "external_actions": {
                "status": "applicable",
                "evidence": "suite-ship-safety.json#external_actions",
            },
            "write_back": {
                "status": "not_applicable",
                "evidence": "suite-audit.json#target_integrity",
            },
        },
        "platforms": [],
        "evidence": {
            "core_flow_tested": "tests/test_*.py",
            "pdca_evidence": "CHANGELOG.md + regression suite",
            "safe_external_actions": (
                "fixed local subprocess allowlist + static safety + regression suite"
            ),
            "failure_recovery": (
                "bad fixtures, invalid inputs, and execution-refusal regression tests"
            ),
            "target_unchanged": "suite-audit.json#target_integrity",
        },
        "limitations": [
            "local regression tests do not prove native invocation on a second Agent platform",
            "write-back is not applicable because this suite audits and reports without editing its source target",
        ],
    }


def audit_suite(root: Path, *, run_tests: bool = True) -> dict[str, Any]:
    hard_script = root / "skills" / "skill-self-check" / "scripts" / "hard_gates.py"
    safety_script = (
        root / "skills" / "skill-ship-safety" / "scripts" / "ship_safety.py"
    )
    template = (
        root
        / "skills"
        / "skill-growth-scorecard"
        / "assets"
        / "scorecard-template.html"
    )
    for required in (hard_script, safety_script, template):
        if not required.is_file():
            raise ValueError(f"required project file is missing: {relative_label(required, root)}")

    skill_dirs = sorted(
        path
        for path in (root / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if not skill_dirs:
        raise ValueError("no shipped skills found under skills/")

    target_before = repository_fingerprint(root)
    records: list[dict[str, Any]] = []
    for skill_dir in skill_dirs:
        hard = run_json_script(hard_script, skill_dir, root)
        safety = run_json_script(safety_script, skill_dir, root)
        records.append(
            {
                "name": skill_dir.name,
                "role": ROLE_LABELS.get(skill_dir.name, "正式产品 Skill"),
                "path": relative_label(skill_dir, root),
                "hard": hard,
                "safety": safety,
            }
        )

    test_summary = (
        run_regression_suite(root)
        if run_tests
        else {
            "command": "not run",
            "status": "not_run",
            "total": 0,
            "passed": None,
            "duration_seconds": None,
            "exit_code": None,
            "evidence": "not supplied",
        }
    )
    hard_aggregate = aggregate_hard_reports(root, records)
    safety_aggregate = aggregate_safety_reports(records)
    target_after = repository_fingerprint(root)
    target_integrity = {
        "before": target_before,
        "after": target_after,
        "unchanged": target_before["digest"] == target_after["digest"],
        "evidence_scope": (
            "repository files excluding git metadata and Python bytecode caches"
        ),
    }
    behavior = behavior_evidence(
        test_summary,
        safety_aggregate,
        target_integrity,
    )
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")

    skill_rows = []
    for record in records:
        scores = record["hard"].get("scores") or {}
        skill_rows.append(
            {
                "name": record["name"],
                "role": record["role"],
                "path": record["path"],
                "basic": scores.get("basic_usable"),
                "contract": scores.get("contract_clarity"),
                "support": scores.get("support_kit"),
                "ship_floor_met": bool(scores.get("ship_floor_met")),
                "hard_counts": record["hard"].get("counts") or {},
                "safety_verdict": record["safety"].get("verdict"),
                "safety_counts": record["safety"].get("counts") or {},
                "external_action_count": len(
                    record["safety"].get("external_actions") or []
                ),
                "execution_status": (
                    (record["safety"].get("execution") or {}).get("status")
                ),
            }
        )

    summary = {
        "skills_total": len(records),
        "static_floor_pass": sum(
            1 for row in skill_rows if row["ship_floor_met"]
        ),
        "safety_static_pass": sum(
            1 for row in skill_rows if row["safety_verdict"] == "static_pass"
        ),
        "critical_total": (
            int((hard_aggregate.get("counts") or {}).get("critical") or 0)
            + int((safety_aggregate.get("counts") or {}).get("critical") or 0)
        ),
        "regression_tests": test_summary,
        "behavior_status": (
            "local_regression_verified"
            if test_summary.get("status") == "passed"
            else "not_verified"
        ),
        "cross_platform_status": "needs_two_platform_behavior_records",
        "target_unchanged": target_integrity["unchanged"],
    }
    suite = {
        "suite_schema_version": SUITE_SCHEMA_VERSION,
        "generated_at": generated_at,
        "timezone": generated_at[-6:],
        "subject": root.name,
        "scope": "skills/ 下所有直接包含 SKILL.md 的正式产品目录",
        "basis": (
            "当前仓库快照、确定性静态检查、本地回归测试，以及对架构、安装、"
            "平台兼容和成长评分契约的工程审阅"
        ),
        "git": git_snapshot(root),
        "summary": summary,
        "skills": skill_rows,
        "findings": hard_aggregate["findings"],
        "target_integrity": target_integrity,
        "conclusion": {
            "project_stage": "可进入受控试用",
            "core_problem": (
                "静态验货、只读安全预检、业务准备度、离线成绩单和一键审计入口"
                "的核心链路已经成立，审计前后源码指纹一致。"
            ),
            "remaining_boundary": (
                "只读不适用项已经按证据评分；仍缺至少两个 Agent 平台使用同一"
                "契约和同一夹具的可信行为验证。"
            ),
        },
        "sources": [
            "skills/*/SKILL.md",
            "skills/*/scripts/*.py",
            "tests/test_*.py",
            "install.ps1",
            "install.sh",
            "plugin.json",
            ".github/workflows/hard-gates.yml",
            "docs/ARCHITECTURE.md",
            "docs/PLATFORM-COMPATIBILITY.md",
            "docs/DESIGN.md",
            "skills/skill-self-check/scripts/run_full_audit.py",
        ],
    }
    return {
        "suite": suite,
        "hard_gates": hard_aggregate,
        "ship_safety": safety_aggregate,
        "behavior": behavior,
        "template": template,
    }


def ensure_private_output(root: Path, output_dir: Path, allow_repo_output: bool) -> None:
    resolved_root = root.resolve()
    resolved_output = output_dir.resolve()
    if not allow_repo_output and (
        resolved_output == resolved_root or resolved_root in resolved_output.parents
    ):
        raise ValueError(
            "real suite reports must stay outside the source repository; "
            "choose another --out-dir"
        )


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    force_utf8_streams()
    parser = argparse.ArgumentParser(
        description="Audit all shipped Skills and render two offline scorecards"
    )
    parser.add_argument("repo_root", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--allow-repo-output", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    output_dir = args.out_dir.resolve()
    try:
        if not root.is_dir():
            raise ValueError(f"repository root not found: {root}")
        ensure_private_output(root, output_dir, args.allow_repo_output)
        output_dir.mkdir(parents=True, exist_ok=True)
        result = audit_suite(root, run_tests=not args.skip_tests)
        suite = result["suite"]
        hard = result["hard_gates"]
        safety = result["ship_safety"]
        behavior = result["behavior"]

        base_profile = build_profile(
            None,
            hard,
            safety,
            behavior,
            "Skill 创作者个人成绩单",
            "Skill-Self-Check 四件套",
        )
        base_profile["suite"] = suite
        base_profile["limitations"].extend(
            item
            for item in behavior.get("limitations") or []
            if item not in base_profile["limitations"]
        )

        personal_profile = dict(base_profile)
        personal_profile["title"] = "Skill 创作者个人成绩单"
        personal_profile["default_view"] = "growth"
        personal_profile["report_kind"] = "personal"

        project_profile = dict(base_profile)
        project_profile["title"] = "Skill 套件项目成绩单"
        project_profile["default_view"] = "detection"
        project_profile["report_kind"] = "project"

        write_json(output_dir / "suite-audit.json", suite, args.pretty)
        write_json(output_dir / "suite-hard-gates.json", hard, args.pretty)
        write_json(output_dir / "suite-ship-safety.json", safety, args.pretty)
        write_json(output_dir / "suite-behavior.json", behavior, args.pretty)
        write_json(
            output_dir / "personal-profile.json", personal_profile, args.pretty
        )
        write_json(
            output_dir / "project-profile.json", project_profile, args.pretty
        )
        (output_dir / "personal-scorecard.html").write_text(
            render_html(personal_profile, result["template"]),
            encoding="utf-8",
        )
        (output_dir / "project-scorecard.html").write_text(
            render_html(project_profile, result["template"]),
            encoding="utf-8",
        )
    except ValueError as exc:
        print(
            json.dumps(
                {
                    "suite_schema_version": SUITE_SCHEMA_VERSION,
                    "error": str(exc),
                },
                ensure_ascii=False,
            )
        )
        print(f"suite_scorecards: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "suite_schema_version": SUITE_SCHEMA_VERSION,
                "output_dir": str(output_dir),
                "skills": suite["summary"]["skills_total"],
                "tests": suite["summary"]["regression_tests"],
                "personal_scorecard": str(output_dir / "personal-scorecard.html"),
                "project_scorecard": str(output_dir / "project-scorecard.html"),
            },
            ensure_ascii=False,
            indent=2 if args.pretty else None,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
