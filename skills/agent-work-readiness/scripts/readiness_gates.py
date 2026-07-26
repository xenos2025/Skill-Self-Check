#!/usr/bin/env python3
"""Deterministic B0-B6 readiness gates for one business work package.

Usage:
  python readiness_gates.py <work-package-dir-or-json> [--pretty] [--out FILE]

The script inspects structured declarations and local evidence references only.
It never executes the described process or accesses external systems.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


LEVELS = [
    ("B0", "口头经验"),
    ("B1", "目标澄清"),
    ("B2", "流程成形"),
    ("B3", "职责分清"),
    ("B4", "标准量化"),
    ("B5", "Agent 可委派"),
    ("B6", "Agent 可运营"),
]

GATE_DEFS = [
    {
        "id": "goal_clarity",
        "level": "B1",
        "label": "目标与边界",
        "title": "把目标说清楚",
        "action": "确认流程名称、结果、原因、触发条件和明确边界。",
        "acceptance": "另一位同事能复述要完成什么、为什么做、何时开始。",
    },
    {
        "id": "workflow_clarity",
        "level": "B2",
        "label": "流程与输出",
        "title": "把口头经验写成步骤",
        "action": "为每一步补齐输入、动作、输出和完成标准。",
        "acceptance": "步骤顺序明确，每一步都有可见输出和 Done when。",
    },
    {
        "id": "role_clarity",
        "level": "B3",
        "label": "职责与交接",
        "title": "把负责人和交接点分清",
        "action": "指定流程负责人、审批人、步骤角色和跨角色交接规则。",
        "acceptance": "每一步只有一个负责角色，每次交接都有接收标准。",
    },
    {
        "id": "measurable_standards",
        "level": "B4",
        "label": "量化与标准",
        "title": "建立可重复判断的完成标准",
        "action": "至少定义一个带公式、单位、方向、阈值和负责人的指标。",
        "acceptance": "两个人使用同一规则会得到相同的通过或不通过结论。",
    },
    {
        "id": "delegation_control",
        "level": "B5",
        "label": "委派与控制",
        "title": "安装 Agent 的权限和异常闸门",
        "action": "写清允许、禁止、人工确认、异常处理和升级负责人。",
        "acceptance": "Agent 知道何时可以继续、何时必须停止并请人决定。",
    },
    {
        "id": "learning_evidence",
        "level": "B6",
        "label": "运行与复盘",
        "title": "用运行证据完成复盘",
        "action": "保存至少两次试运行证据和一份复盘，并给工作包标注版本。",
        "acceptance": "证据文件位于工作包内，复盘写明下一版如何调整。",
    },
]


def force_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return False
        lowered = text.lower()
        return not (
            lowered in {"todo", "tbd", "unknown", "n/a", "na", "none"}
            or lowered.startswith("unknown ")
            or lowered.startswith("unknown—")
            or lowered.startswith("unknown —")
        )
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def nested(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def missing_fields(data: dict[str, Any], paths: list[str]) -> list[str]:
    return [path for path in paths if not meaningful(nested(data, path))]


def valid_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def relative_existing_file(base: Path, raw: Any) -> tuple[bool, str]:
    if not isinstance(raw, str) or not raw.strip():
        return False, "missing"
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        return False, "must be a safe relative path"
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError:
        return False, "escapes the work package"
    if not resolved.is_file():
        return False, "file not found"
    return True, ""


def load_work_package(target: Path) -> tuple[Path, Path, dict[str, Any]]:
    json_path = target / "work-readiness.json" if target.is_dir() else target
    if not json_path.is_file():
        raise ValueError(f"work-readiness.json not found: {json_path}")
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("top-level JSON value must be an object")
    return json_path, json_path.parent, payload


def assess(target: Path) -> dict[str, Any]:
    json_path, base, data = load_work_package(target)
    findings: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []

    def add_gate(
        definition: dict[str, str],
        passed: bool,
        missing: list[str],
        notes: list[str] | None = None,
    ) -> None:
        gate = {
            "id": definition["id"],
            "level": definition["level"],
            "label": definition["label"],
            "status": "pass" if passed else "needs_work",
            "missing": missing,
            "notes": notes or [],
        }
        gates.append(gate)
        if not passed:
            evidence = ", ".join(missing + (notes or []))
            findings.append(
                {
                    "id": f"READY.{definition['level'][1:]}",
                    "severity": "should_fix",
                    "message": definition["title"],
                    "evidence": evidence,
                    "source": "script",
                }
            )

    goal_missing = missing_fields(
        data,
        [
            "process.name",
            "process.intended_outcome",
            "process.why",
            "process.trigger",
            "process.out_of_scope",
        ],
    )
    add_gate(GATE_DEFS[0], not goal_missing, goal_missing)

    steps = valid_list(data.get("steps"))
    workflow_missing: list[str] = []
    workflow_notes: list[str] = []
    if not steps:
        workflow_missing.append("steps")
    step_ids: list[str] = []
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            workflow_missing.append(f"steps[{index}]")
            continue
        for field in ("id", "input", "action", "output", "done_when"):
            if not meaningful(step.get(field)):
                workflow_missing.append(f"steps[{index}].{field}")
        if meaningful(step.get("id")):
            step_ids.append(str(step["id"]).strip())
    if len(step_ids) != len(set(step_ids)):
        workflow_notes.append("step ids must be unique")
    add_gate(
        GATE_DEFS[1],
        bool(steps) and not workflow_missing and not workflow_notes,
        workflow_missing,
        workflow_notes,
    )

    role_missing = missing_fields(data, ["process.owner", "process.approver"])
    role_notes: list[str] = []
    roles = valid_list(data.get("roles"))
    declared_roles: set[str] = set()
    ownership: defaultdict[str, list[str]] = defaultdict(list)
    if not roles:
        role_missing.append("roles")
    for index, role in enumerate(roles, start=1):
        if not isinstance(role, dict):
            role_missing.append(f"roles[{index}]")
            continue
        role_name = str(role.get("role", "")).strip()
        owns = valid_list(role.get("owns"))
        if not role_name:
            role_missing.append(f"roles[{index}].role")
        else:
            declared_roles.add(role_name)
        if not any(meaningful(item) for item in owns):
            role_missing.append(f"roles[{index}].owns")
        for item in owns:
            if meaningful(item):
                ownership[str(item).strip().casefold()].append(role_name)
    duplicates = sorted(key for key, owners in ownership.items() if len(set(owners)) > 1)
    if duplicates:
        role_notes.append("overlapping ownership: " + ", ".join(duplicates))

    step_roles = {
        str(step.get("role", "")).strip()
        for step in steps
        if isinstance(step, dict) and meaningful(step.get("role"))
    }
    for index, step in enumerate(steps, start=1):
        if isinstance(step, dict) and not meaningful(step.get("role")):
            role_missing.append(f"steps[{index}].role")
    unknown_roles = sorted(role for role in step_roles if role not in declared_roles)
    if unknown_roles:
        role_notes.append("undeclared step roles: " + ", ".join(unknown_roles))

    handoffs = valid_list(data.get("handoffs"))
    if len(step_roles) > 1:
        if not handoffs:
            role_missing.append("handoffs")
        for index, handoff in enumerate(handoffs, start=1):
            if not isinstance(handoff, dict):
                role_missing.append(f"handoffs[{index}]")
                continue
            for field in ("from", "to", "deliverable", "acceptance"):
                if not meaningful(handoff.get(field)):
                    role_missing.append(f"handoffs[{index}].{field}")
    add_gate(
        GATE_DEFS[2],
        not role_missing and not role_notes,
        sorted(set(role_missing)),
        role_notes,
    )

    metric_missing: list[str] = []
    metrics = valid_list(data.get("metrics"))
    if not metrics:
        metric_missing.append("metrics")
    for index, metric in enumerate(metrics, start=1):
        if not isinstance(metric, dict):
            metric_missing.append(f"metrics[{index}]")
            continue
        for field in ("id", "name", "formula", "unit", "direction", "threshold", "owner"):
            if not meaningful(metric.get(field)):
                metric_missing.append(f"metrics[{index}].{field}")
    add_gate(GATE_DEFS[3], bool(metrics) and not metric_missing, metric_missing)

    boundary_missing = missing_fields(data, ["agent_boundary.escalation"])
    boundary = data.get("agent_boundary")
    if not isinstance(boundary, dict):
        boundary = {}
        boundary_missing.append("agent_boundary")
    for field in ("allowed_actions", "forbidden_actions", "human_approval"):
        values = valid_list(boundary.get(field))
        if not any(meaningful(item) for item in values):
            boundary_missing.append(f"agent_boundary.{field}")
    for index, step in enumerate(steps, start=1):
        if isinstance(step, dict) and not meaningful(step.get("exception")):
            boundary_missing.append(f"steps[{index}].exception")
    add_gate(GATE_DEFS[4], not boundary_missing, sorted(set(boundary_missing)))

    learning_missing: list[str] = []
    learning_notes: list[str] = []
    evidence = data.get("evidence")
    if not isinstance(evidence, dict):
        evidence = {}
        learning_missing.append("evidence")
    if not meaningful(evidence.get("version")):
        learning_missing.append("evidence.version")
    retro_ok, retro_reason = relative_existing_file(base, evidence.get("retrospective"))
    if not retro_ok:
        learning_missing.append("evidence.retrospective")
        if retro_reason not in {"missing", "file not found"}:
            learning_notes.append(f"retrospective {retro_reason}")
    pilot_runs = valid_list(evidence.get("pilot_runs"))
    if len(pilot_runs) < 2:
        learning_missing.append("evidence.pilot_runs[2]")
    for index, run in enumerate(pilot_runs, start=1):
        if not isinstance(run, dict):
            learning_missing.append(f"evidence.pilot_runs[{index}]")
            continue
        for field in ("run_id", "outcome", "reviewed_by"):
            if not meaningful(run.get(field)):
                learning_missing.append(f"evidence.pilot_runs[{index}].{field}")
        artifact_ok, artifact_reason = relative_existing_file(base, run.get("artifact"))
        if not artifact_ok:
            learning_missing.append(f"evidence.pilot_runs[{index}].artifact")
            if artifact_reason not in {"missing", "file not found"}:
                learning_notes.append(
                    f"pilot run {index} artifact {artifact_reason}"
                )
    add_gate(
        GATE_DEFS[5],
        not learning_missing and not learning_notes,
        sorted(set(learning_missing)),
        learning_notes,
    )

    passed_count = 0
    for gate in gates:
        if gate["status"] != "pass":
            break
        passed_count += 1
    level_id, level_label = LEVELS[passed_count]

    next_gate = next((gate for gate in gates if gate["status"] != "pass"), None)
    next_quest: dict[str, Any] | None = None
    if next_gate:
        definition = next(item for item in GATE_DEFS if item["id"] == next_gate["id"])
        next_level_id, next_level_label = LEVELS[passed_count + 1]
        next_quest = {
            "lane": "business_readiness",
            "gate_id": definition["id"],
            "title": definition["title"],
            "action": definition["action"],
            "acceptance": definition["acceptance"],
            "unlocks": {"id": next_level_id, "label": next_level_label},
        }

    badges = [
        {"id": gate["id"], "label": gate["label"]}
        for gate in gates
        if gate["status"] == "pass"
    ]
    return {
        "schema_version": "1.0",
        "assessment": "agent_work_readiness",
        "audit_level": "static_work_package_check",
        "target_platform": "generic",
        "input": {
            "file": str(json_path),
            "process_name": nested(data, "process.name") or "",
        },
        "level": {
            "id": level_id,
            "label": level_label,
            "ordinal": passed_count,
            "max_ordinal": 6,
        },
        "gates": gates,
        "badges": badges,
        "next_quest": next_quest,
        "findings": findings,
        "counts": {
            "critical": 0,
            "should_fix": len(findings),
            "passed_gates": passed_count,
        },
        "limitations": [
            "checks structured declarations and local evidence references only",
            "does not prove that described business behavior is correct",
            "does not execute the process or access external systems",
            "business owners must confirm goals, roles, thresholds, and permissions",
        ],
    }


def error_report(target: Path, message: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "assessment": "agent_work_readiness",
        "audit_level": "static_work_package_check",
        "target_platform": "generic",
        "input": {"file": str(target), "process_name": ""},
        "level": {"id": "B0", "label": "口头经验", "ordinal": 0, "max_ordinal": 6},
        "gates": [],
        "badges": [],
        "next_quest": {
            "lane": "business_readiness",
            "gate_id": "goal_clarity",
            "title": "创建可读取的工作准备度记录",
            "action": "复制 work-readiness.template.json 并填写一个流程。",
            "acceptance": "readiness_gates.py 可以读取 UTF-8 JSON。",
            "unlocks": {"id": "B1", "label": "目标澄清"},
        },
        "findings": [
            {
                "id": "READY.0",
                "severity": "critical",
                "message": message,
                "evidence": str(target),
                "source": "script",
            }
        ],
        "counts": {"critical": 1, "should_fix": 0, "passed_gates": 0},
        "limitations": ["input could not be assessed"],
    }


def main() -> int:
    force_utf8_streams()
    parser = argparse.ArgumentParser(description="Agent work readiness gates")
    parser.add_argument("target", type=Path, help="Work package directory or JSON file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser.add_argument("--out", type=Path, help="Also write JSON to this file")
    args = parser.parse_args()

    try:
        report = assess(args.target)
        exit_code = 0
    except ValueError as exc:
        report = error_report(args.target, str(exc))
        exit_code = 2

    dump = json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None)
    print(dump)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(dump + "\n", encoding="utf-8")
    print(
        f"readiness_gates: {report['level']['id']} {report['level']['label']} · "
        f"passed={report['counts']['passed_gates']}/6 · "
        f"critical={report['counts']['critical']}",
        file=sys.stderr,
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

