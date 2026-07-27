#!/usr/bin/env python3
"""Re-check a Skill after fixes and report the score/finding delta.

Usage:
  python verify_fix.py <skill-dir> --baseline <hard-gates.json>

The baseline is the `hard_gates.py` report captured before the edits. This
script re-runs the same deterministic checker and compares the two fact sets;
it never executes the audited Skill and never edits it.

Stdout: JSON delta report
Stderr: human one-line summary
Exit: 0 when nothing regressed, 1 when a regression is detected
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
SEVERITY_ORDER = {"critical": 3, "should_fix": 2, "nice": 1, "info": 0}
SCORED_DIMENSIONS = ("basic_usable", "contract_clarity", "support_kit")
# This product entry is permanently a read-only DRY_RUN with respect to the
# audited Skill and external systems. It may launch only the sibling hard-gate
# checker; there is no flag that enables target code.
READ_ONLY_DRY_RUN = True


def force_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def read_json_text(path: Path) -> str:
    """Decode a baseline file, tolerating Windows shell redirection encodings.

    `hard_gates.py ... > baseline.json` in PowerShell produces UTF-16, so a
    strict UTF-8 read would reject a file the user reasonably expects to work.
    """
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"无法读取基线文件：{path.name}：{exc}") from exc
    for encoding in ("utf-8-sig", "utf-8", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            text = raw.decode(encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
        if text.lstrip().startswith("{"):
            return text
    raise ValueError(
        f"基线文件不是可读的 JSON 文本：{path.name}；请用 UTF-8 保存 hard_gates.py 的输出"
    )


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read_json_text(path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"无法解析 JSON：{path.name}：{exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON 顶层必须是对象：{path.name}")
    return value


def load_baseline(path: Path) -> dict[str, Any]:
    report = load_json(path)
    if report.get("error"):
        raise ValueError("基线报告记录的是一次失败的检查，不能作为对比基准")
    scores = report.get("scores")
    if not isinstance(scores, dict) or "basic_usable" not in scores:
        raise ValueError(
            "基线文件不是 hard_gates.py 的报告；请提供修改前保存的 hard-gates.json"
        )
    return report


def run_hard_gates(script: Path, target: Path) -> dict[str, Any]:
    if not READ_ONLY_DRY_RUN:
        raise ValueError("复检入口必须保持只读预演模式")
    result = subprocess.run(
        [sys.executable, str(script), str(target)],
        cwd=script.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{script.name} 没有返回可读取的 JSON：{exc}") from exc
    return report


def score_value(report: dict[str, Any], dimension: str) -> tuple[int | None, int | None]:
    block = (report.get("scores") or {}).get(dimension)
    if not isinstance(block, dict):
        return None, None
    score = block.get("score")
    maximum = block.get("max")
    return (
        score if isinstance(score, int) else None,
        maximum if isinstance(maximum, int) else None,
    )


def compare_scores(
    baseline: dict[str, Any], current: dict[str, Any]
) -> tuple[dict[str, Any], bool, bool]:
    """Compare each scored dimension.

    `support_kit.max` shifts when a module changes between applicable and N/A
    (a skill that gains real steps suddenly owes references and examples).
    Scores across different maxima are not comparable, so those dimensions are
    reported as `not_comparable` instead of faking an improvement or a drop.
    """
    scores: dict[str, Any] = {}
    improved = False
    regressed = False
    for dimension in SCORED_DIMENSIONS:
        before, before_max = score_value(baseline, dimension)
        after, after_max = score_value(current, dimension)
        if before is None or after is None:
            direction = "unknown"
        elif before_max != after_max:
            direction = "not_comparable"
        elif after > before:
            direction = "improved"
            improved = True
        elif after < before:
            direction = "regressed"
            regressed = True
        else:
            direction = "unchanged"
        scores[dimension] = {
            "before": before,
            "after": after,
            "before_max": before_max,
            "after_max": after_max,
            "direction": direction,
        }
    return scores, improved, regressed


def index_findings(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for finding in report.get("findings") or []:
        if not isinstance(finding, dict):
            continue
        item_id = str(finding.get("id") or "").strip()
        if not item_id:
            continue
        existing = indexed.get(item_id)
        if existing is None or SEVERITY_ORDER.get(
            str(finding.get("severity")), 0
        ) > SEVERITY_ORDER.get(str(existing.get("severity")), 0):
            indexed[item_id] = finding
    return indexed


def summarize_finding(item_id: str, finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item_id,
        "severity": finding.get("severity"),
        "message": finding.get("message"),
    }


def compare_findings(
    baseline: dict[str, Any], current: dict[str, Any]
) -> tuple[dict[str, Any], bool, bool, bool]:
    """Split the finding delta into resolved, newly introduced, and persisting.

    Returns `(delta, improved, hard_regression, soft_regression)`. A new
    Critical is a hard regression; a new lower-severity item is often a check
    that only became applicable after the fix, so it is surfaced without
    failing the run unless the caller asks for strict mode.
    """
    before = index_findings(baseline)
    after = index_findings(current)
    resolved = [
        summarize_finding(item_id, before[item_id])
        for item_id in sorted(set(before) - set(after))
    ]
    introduced = [
        summarize_finding(item_id, after[item_id])
        for item_id in sorted(set(after) - set(before))
    ]
    persisting: list[dict[str, Any]] = []
    escalated: list[dict[str, Any]] = []
    for item_id in sorted(set(before) & set(after)):
        record = summarize_finding(item_id, after[item_id])
        before_severity = str(before[item_id].get("severity"))
        after_severity = str(after[item_id].get("severity"))
        if before_severity != after_severity:
            record["severity_before"] = before_severity
            if SEVERITY_ORDER.get(after_severity, 0) > SEVERITY_ORDER.get(
                before_severity, 0
            ):
                escalated.append(record)
        persisting.append(record)
    new_critical = [
        record for record in introduced if record["severity"] == "critical"
    ]
    resolved_critical = [
        record for record in resolved if record["severity"] == "critical"
    ]
    delta = {
        "resolved": resolved,
        "introduced": introduced,
        "persisting": persisting,
        "counts": {
            "resolved": len(resolved),
            "resolved_critical": len(resolved_critical),
            "introduced": len(introduced),
            "persisting": len(persisting),
            "new_critical": len(new_critical),
            "newly_surfaced_non_critical": len(introduced) - len(new_critical),
            "escalated": len(escalated),
        },
    }
    improved = bool(resolved_critical)
    hard_regression = bool(new_critical) or bool(escalated)
    soft_regression = len(introduced) > len(new_critical)
    return delta, improved, hard_regression, soft_regression


def gate_transition(
    baseline: dict[str, Any], current: dict[str, Any]
) -> tuple[dict[str, Any], bool, bool]:
    before_floor = bool((baseline.get("scores") or {}).get("ship_floor_met"))
    after_floor = bool((current.get("scores") or {}).get("ship_floor_met"))
    before_package = str(
        (baseline.get("package_health") or {}).get("status") or "not_assessed"
    )
    after_package = str(
        (current.get("package_health") or {}).get("status") or "not_assessed"
    )
    package_was_valid = before_package == "valid_skill_package"
    package_is_valid = after_package == "valid_skill_package"
    improved = (after_floor and not before_floor) or (
        package_is_valid and not package_was_valid
    )
    regressed = (before_floor and not after_floor) or (
        package_was_valid and not package_is_valid
    )
    return (
        {
            "ship_floor": {
                "before": before_floor,
                "after": after_floor,
                "direction": (
                    "improved"
                    if after_floor and not before_floor
                    else "regressed"
                    if before_floor and not after_floor
                    else "unchanged"
                ),
            },
            "package_health": {
                "before": before_package,
                "after": after_package,
                "direction": (
                    "improved"
                    if package_is_valid and not package_was_valid
                    else "regressed"
                    if package_was_valid and not package_is_valid
                    else "unchanged"
                ),
            },
        },
        improved,
        regressed,
    )


def efficiency_transition(
    baseline: dict[str, Any], current: dict[str, Any]
) -> dict[str, Any]:
    def metrics(report: dict[str, Any]) -> dict[str, Any]:
        return report.get("operational_metrics") or {}

    def loop_status(report: dict[str, Any]) -> str:
        guard = metrics(report).get("loop_guard")
        if not isinstance(guard, dict):
            return "not_assessed"
        return str(guard.get("status") or "not_assessed")

    def token_estimate(report: dict[str, Any]) -> int | None:
        token = metrics(report).get("token_consumption")
        if not isinstance(token, dict):
            return None
        value = token.get("estimated_input_tokens")
        return value if isinstance(value, int) else None

    def budget_status(report: dict[str, Any]) -> str:
        token = metrics(report).get("token_consumption")
        if not isinstance(token, dict):
            return "not_assessed"
        budget = token.get("budget")
        if not isinstance(budget, dict):
            return "not_assessed"
        return str(budget.get("status") or "not_assessed")

    before_tokens = token_estimate(baseline)
    after_tokens = token_estimate(current)
    saved = (
        before_tokens - after_tokens
        if before_tokens is not None and after_tokens is not None
        else None
    )
    return {
        "loop_guard": {
            "before": loop_status(baseline),
            "after": loop_status(current),
        },
        "estimated_input_tokens": {
            "before": before_tokens,
            "after": after_tokens,
            "saved": saved,
        },
        "token_budget": {
            "before": budget_status(baseline),
            "after": budget_status(current),
        },
    }


def target_identity(
    baseline: dict[str, Any], current: dict[str, Any], target: Path
) -> dict[str, Any]:
    baseline_name = str((baseline.get("frontmatter") or {}).get("name") or "")
    current_name = str((current.get("frontmatter") or {}).get("name") or "")
    baseline_dir = Path(str(baseline.get("skill_dir") or "")).name
    current_dir = target.name
    return {
        "baseline_name": baseline_name or None,
        "current_name": current_name or None,
        "baseline_directory": baseline_dir or None,
        "current_directory": current_dir,
        # A rename is a legitimate fix for 1.4 / PKG.2, so record it instead of
        # refusing the comparison.
        "name_changed": bool(baseline_name and baseline_name != current_name),
        "directory_changed": bool(baseline_dir and baseline_dir != current_dir),
    }


def verify(target: Path, baseline_path: Path, *, strict: bool) -> dict[str, Any]:
    if not target.is_dir() or not (target / "SKILL.md").is_file():
        raise ValueError("被复检目录必须存在，并且包含 SKILL.md")
    script = Path(__file__).resolve().parent / "hard_gates.py"
    if not script.is_file():
        raise ValueError("缺少 hard_gates.py，无法复检")
    baseline = load_baseline(baseline_path)
    current = run_hard_gates(script, target)

    scores, score_up, score_down = compare_scores(baseline, current)
    findings, finding_up, finding_hard, finding_soft = compare_findings(
        baseline, current
    )
    gates, gate_up, gate_down = gate_transition(baseline, current)

    hard_regression = score_down or finding_hard or gate_down
    # Findings can also disappear because a check stopped applying (a Skill that
    # loses its steps no longer owes examples). Minor items that vanish only
    # count as progress when nothing hard broke at the same time.
    resolved_any = findings["counts"]["resolved"] > 0
    improved = (
        score_up
        or gate_up
        or finding_up
        or (resolved_any and not hard_regression)
    )
    if hard_regression and improved:
        verdict = "mixed"
    elif hard_regression:
        verdict = "regressed"
    elif improved:
        verdict = "improved"
    elif finding_soft:
        verdict = "mixed"
    else:
        verdict = "unchanged"
    remaining = (current.get("counts") or {}).get("critical")
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_level": "static_fix_verification",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": verdict,
        "regression_detected": hard_regression or (strict and finding_soft),
        "hard_regression": hard_regression,
        "strict": strict,
        "target": target_identity(baseline, current, target),
        "scores": scores,
        "gates": gates,
        "findings": findings,
        "efficiency": efficiency_transition(baseline, current),
        "counts": {
            "before": baseline.get("counts") or {},
            "after": current.get("counts") or {},
        },
        "remaining_critical": remaining if isinstance(remaining, int) else None,
        "limitations": [
            "对比只覆盖 hard_gates.py 的静态结构与契约信号",
            "修改后的行为正确性与安全性仍需单独验证",
            "本次复检没有执行被检查的 Skill，也没有修改它",
            "分数上限变化的维度标为 not_comparable：检查项的适用范围变了，"
            "前后分数不能直接比",
        ],
    }


def main() -> int:
    force_utf8_streams()
    parser = argparse.ArgumentParser(
        description="Compare a Skill against its pre-fix hard-gate baseline"
    )
    parser.add_argument("skill_dir", type=Path, help="Path to the skill directory")
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="hard_gates.py JSON captured before the fixes",
    )
    parser.add_argument(
        "--out", type=Path, help="Optional path for the delta JSON report"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also fail when non-critical findings appear that were not there before",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    try:
        report = verify(args.skill_dir.resolve(), args.baseline, strict=args.strict)
    except ValueError as exc:
        print(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "audit_level": "static_fix_verification",
                    "verdict": "not_verified",
                    "regression_detected": False,
                    "error": str(exc),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        print(f"verify_fix: {exc}", file=sys.stderr)
        return 1

    dump = json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None)
    print(dump)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(dump + "\n", encoding="utf-8")
    counts = report["findings"]["counts"]
    print(
        f"verify_fix: {report['verdict']} · "
        f"resolved={counts['resolved']} "
        f"(critical {counts['resolved_critical']}) · "
        f"introduced={counts['introduced']} "
        f"(critical {counts['new_critical']}) · "
        f"remaining_critical={report['remaining_critical']} · "
        f"ship_floor={report['gates']['ship_floor']['after']}",
        file=sys.stderr,
    )
    return 1 if report["regression_detected"] else 0


if __name__ == "__main__":
    sys.exit(main())
