#!/usr/bin/env python3
"""Validate same-fixture behavior evidence for a role/Prompt rewrite.

This checker never invokes the target Skill or a model. It validates a record
produced by an independent before/after evaluation and computes the comparative
verdict without changing the core gate_verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPORT_SCHEMA_VERSION = "1.0"
REQUIRED_CHECK_IDS = {
    "global_objective",
    "required_business_outcomes",
    "shared_context",
    "end_to_end_ownership",
    "authority_boundaries",
    "integration_quality",
}
GLOBAL_PURPOSE_CHECK_IDS = {
    "global_objective",
    "required_business_outcomes",
    "shared_context",
    "end_to_end_ownership",
    "integration_quality",
}
CHECK_STATUSES = {"pass", "fail", "not_assessed"}
RUNTIME_MODES = {"single_context", "workflow_nodes"}


def force_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def issue(
    finding_id: str,
    field: str,
    evidence: object,
    message: str,
) -> dict[str, Any]:
    return {
        "id": finding_id,
        "severity": "error",
        "scope": "role_prompt_behavior",
        "field": field,
        "evidence": evidence,
        "message": message,
    }


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_shape(record: object) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not isinstance(record, dict):
        return [
            issue(
                "RPB.0",
                "record",
                record,
                "Behavior evidence must be a JSON object",
            )
        ]
    if record.get("schema_version") != "1.0":
        findings.append(
            issue(
                "RPB.0",
                "schema_version",
                record.get("schema_version"),
                "schema_version must be 1.0",
            )
        )
    if record.get("evidence_type") != "same_fixture_before_after":
        findings.append(
            issue(
                "RPB.0",
                "evidence_type",
                record.get("evidence_type"),
                "Comparative verdicts require same_fixture_before_after evidence",
            )
        )

    fixture = record.get("fixture")
    if not isinstance(fixture, dict):
        findings.append(issue("RPB.0", "fixture", fixture, "fixture must be an object"))
    else:
        if not nonempty_string(fixture.get("id")):
            findings.append(
                issue("RPB.0", "fixture.id", fixture.get("id"), "fixture.id is required")
            )
        for field in ("inputs_unchanged", "success_criteria_unchanged"):
            if fixture.get(field) is not True:
                findings.append(
                    issue(
                        "RPB.0",
                        f"fixture.{field}",
                        fixture.get(field),
                        f"{field} must be true for a comparative verdict",
                    )
                )

    evaluator = record.get("evaluator")
    if not isinstance(evaluator, dict):
        findings.append(
            issue("RPB.0", "evaluator", evaluator, "evaluator must be an object")
        )
    else:
        if evaluator.get("independent_context") is not True:
            findings.append(
                issue(
                    "RPB.0",
                    "evaluator.independent_context",
                    evaluator.get("independent_context"),
                    "The evaluator must use an independent context",
                )
            )
        if evaluator.get("expected_verdict_disclosed") is not False:
            findings.append(
                issue(
                    "RPB.0",
                    "evaluator.expected_verdict_disclosed",
                    evaluator.get("expected_verdict_disclosed"),
                    "Do not disclose the expected verdict to the evaluator",
                )
            )

    for side in ("baseline", "candidate"):
        value = record.get(side)
        if not isinstance(value, dict):
            findings.append(issue("RPB.0", side, value, f"{side} must be an object"))
            continue
        if value.get("runtime_mode") not in RUNTIME_MODES:
            findings.append(
                issue(
                    "RPB.0",
                    f"{side}.runtime_mode",
                    value.get("runtime_mode"),
                    "runtime_mode must be single_context or workflow_nodes",
                )
            )
        agent_count = value.get("agent_count")
        if not isinstance(agent_count, int) or isinstance(agent_count, bool) or agent_count < 1:
            findings.append(
                issue(
                    "RPB.0",
                    f"{side}.agent_count",
                    agent_count,
                    "agent_count must be a positive integer",
                )
            )
        if not isinstance(value.get("implicit_delegation"), bool):
            findings.append(
                issue(
                    "RPB.0",
                    f"{side}.implicit_delegation",
                    value.get("implicit_delegation"),
                    "implicit_delegation must be boolean",
                )
            )

    checks = record.get("checks")
    if not isinstance(checks, list):
        findings.append(issue("RPB.0", "checks", checks, "checks must be a list"))
        return findings
    seen: set[str] = set()
    for index, check in enumerate(checks):
        field = f"checks[{index}]"
        if not isinstance(check, dict):
            findings.append(issue("RPB.0", field, check, "Each check must be an object"))
            continue
        check_id = check.get("id")
        if not nonempty_string(check_id):
            findings.append(issue("RPB.0", f"{field}.id", check_id, "check id is required"))
        elif check_id in seen:
            findings.append(issue("RPB.0", f"{field}.id", check_id, "check ids must be unique"))
        else:
            seen.add(check_id)
        for side in ("baseline", "candidate"):
            if check.get(side) not in CHECK_STATUSES:
                findings.append(
                    issue(
                        "RPB.0",
                        f"{field}.{side}",
                        check.get(side),
                        f"{side} must be pass, fail, or not_assessed",
                    )
                )
        if not nonempty_string(check.get("evidence")):
            findings.append(
                issue(
                    "RPB.0",
                    f"{field}.evidence",
                    check.get("evidence"),
                    "Every check requires concise artifact evidence",
                )
            )
    missing = sorted(REQUIRED_CHECK_IDS - seen)
    if missing:
        findings.append(
            issue(
                "RPB.0",
                "checks",
                missing,
                "Required behavior checks are missing",
            )
        )
    return findings


def evaluate(record: object) -> dict[str, Any]:
    shape_findings = validate_shape(record)
    if shape_findings or not isinstance(record, dict):
        return report("not_assessed", shape_findings)

    baseline = record["baseline"]
    candidate = record["candidate"]
    findings: list[dict[str, Any]] = []
    if (
        candidate["runtime_mode"] == "single_context"
        and (candidate["agent_count"] != 1 or candidate["implicit_delegation"])
    ):
        findings.append(
            issue(
                "RPB.1",
                "candidate",
                {
                    "runtime_mode": candidate["runtime_mode"],
                    "agent_count": candidate["agent_count"],
                    "implicit_delegation": candidate["implicit_delegation"],
                },
                "single_context must remain one Agent with no implicit delegation",
            )
        )

    checks = {item["id"]: item for item in record["checks"]}
    unassessed = sorted(
        check_id
        for check_id, item in checks.items()
        if item["baseline"] == "not_assessed" or item["candidate"] == "not_assessed"
    )
    if unassessed:
        findings.append(
            issue(
                "RPB.0",
                "checks",
                unassessed,
                "Comparative checks cannot be not_assessed",
            )
        )
        return report("not_assessed", findings)

    regressions = sorted(
        check_id
        for check_id, item in checks.items()
        if item["baseline"] == "pass" and item["candidate"] == "fail"
    )
    improvements = sorted(
        check_id
        for check_id, item in checks.items()
        if item["baseline"] == "fail" and item["candidate"] == "pass"
    )
    for check_id in regressions:
        finding_id = "RPB.2" if check_id in GLOBAL_PURPOSE_CHECK_IDS else "RPB.3"
        findings.append(
            issue(
                finding_id,
                f"checks.{check_id}",
                checks[check_id]["evidence"],
                "Candidate regressed from pass to fail on this behavior check",
            )
        )

    if any(item["id"] in {"RPB.1", "RPB.2"} for item in findings):
        verdict = "regressed"
    elif regressions and improvements:
        verdict = "mixed"
    elif regressions:
        verdict = "regressed"
    elif improvements:
        verdict = "improved"
    else:
        verdict = "unchanged"
    result = report(verdict, findings)
    result["comparison"] = {
        "improvements": improvements,
        "regressions": regressions,
        "baseline_runtime_mode": baseline["runtime_mode"],
        "candidate_runtime_mode": candidate["runtime_mode"],
    }
    return result


def report(verdict: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "audit_level": "role_prompt_behavior_evidence",
        "status": "completed" if verdict != "not_assessed" else "not_assessed",
        "behavior_verdict": verdict,
        "release_recommendation": (
            "eligible" if verdict in {"improved", "unchanged"} else "block"
        ),
        "gate_effect": "none",
        "findings": findings,
        "limitations": [
            "This checker validates supplied evidence; it does not run the Skill or a model.",
            "An unchanged verdict does not prove improvement.",
            "The core gate_verdict remains independent.",
        ],
    }


def main() -> int:
    force_utf8_streams()
    parser = argparse.ArgumentParser(
        description="Validate same-fixture role/Prompt behavior evidence"
    )
    parser.add_argument("evidence_json", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        record = json.loads(args.evidence_json.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result = report(
            "not_assessed",
            [issue("RPB.0", "evidence_json", str(args.evidence_json), str(exc))],
        )
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
        return 2
    result = evaluate(record)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0 if result["release_recommendation"] == "eligible" else 1


if __name__ == "__main__":
    raise SystemExit(main())
