#!/usr/bin/env python3
"""Deterministically audit the applicable functional role contract for a Skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from workflow_prompt_audit import (
    DEFAULT_MANIFEST,
    audit as audit_workflow,
    not_applicable_reason as workflow_not_applicable_reason,
)


REPORT_SCHEMA_VERSION = "1.1"
AUDIT_LEVEL = "role_contract_static"
DEFAULT_ROLE_CONTRACT = Path("references/role-contract.json")
ROLE_NOT_APPLICABLE_RE = re.compile(
    r"^\s*Role contract audit:\s*N/A\s*(?:—|–|-|:)\s*(\S.*)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
LEGACY_REQUIRED_STRING_FIELDS = ("role", "purpose")
LEGACY_REQUIRED_NONEMPTY_LIST_FIELDS = (
    "responsibilities",
    "out_of_scope",
    "decision_authority",
)
LEGACY_LIST_FIELDS = (
    *LEGACY_REQUIRED_NONEMPTY_LIST_FIELDS,
    "handoff_to",
)
ROLE_REQUIRED_STRING_FIELDS = ("id", "role", "purpose")
ROLE_REQUIRED_NONEMPTY_LIST_FIELDS = (
    "inputs",
    "responsibilities",
    "out_of_scope",
    "decision_authority",
    "outputs",
    "acceptance_tests",
    "stop_conditions",
)
ROLE_LIST_FIELDS = (
    *ROLE_REQUIRED_NONEMPTY_LIST_FIELDS,
    "next",
    "handoff_to",
)
ROLE_PROMPT_STRING_FIELDS = ("role", "purpose")
ROLE_PROMPT_LIST_FIELDS = ROLE_LIST_FIELDS
ROLE_MODES = {"single_role", "sequential_roles"}
MAX_LEAK_EVIDENCE = 10
DELEGATION_DIRECTIVE_RES = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"子\s*agent",
        r"子代理",
        r"子智能体",
        r"sub-?\s?agents?",
        r"委派",
        r"委托给",
        r"分派",
        r"派发",
        r"并行(?:执行|运行|处理|调用|任务)",
        r"parallel\s+(?:worker|agent|task|subtask)s?",
        r"\bspawn(?:s|ed|ing)?\b",
        r"\bdispatch(?:es|ed|ing)?\b",
        r"\bdelegat(?:e|es|ed|ing|ion)\b",
    )
)
# A well-written single-context Skill names delegation in order to forbid it, so a
# directive only leaks when nothing in its line or section negates it.
PROHIBITION_INLINE_RE = re.compile(
    r"不得|不要|不可|不能|禁止|严禁|避免|切勿|勿|不应|不允许|拒绝|绝不|从不|无需|不是"
    r"|\bnever\b|\bdo not\b|\bdon't\b|\bmust not\b|\bcannot\b|\bcan't\b|\bavoid\b"
    r"|\breject(?:s|ed|ing)?\b|\bforbid(?:s|den)?\b|\bprohibit(?:s|ed)?\b"
    r"|\bwithout\b|\binstead of\b|\brather than\b|\bnot\b",
    re.IGNORECASE,
)
PROHIBITION_HEADING_RE = re.compile(
    r"when\s+not\s+to\s+use|out\s+of\s+scope|red\s+flags?"
    r"|common\s+rationalizations?|anti-?patterns?"
    r"|不可违背|禁止|不适用|反例|红线",
    re.IGNORECASE,
)
ROLE_WORKFLOW_FINDING_IDS = {
    "WPA.0",
    "WPA.1",
    "WPA.2",
    "WPA.3",
    "WPA.6",
    "WPA.9",
    "WPA.10",
    "WPA.11",
    "WPA.12",
}


def force_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def finding(
    finding_id: str,
    field: str,
    evidence: object,
    message: str,
    *,
    mode: str,
    node_id: str | None = None,
) -> dict[str, Any]:
    return {
        "id": finding_id,
        "severity": "error",
        "scope": "role_contract",
        "mode": mode,
        "node_id": node_id,
        "field": field,
        "evidence": evidence,
        "message": message,
    }


def delegation_leak_findings(
    prompt_text: str, *, mode: str, declaration: str
) -> list[dict[str, Any]]:
    """Report delegation directives that contradict a single-context declaration."""
    leaks: list[dict[str, Any]] = []
    in_code_block = False
    prohibitive_section = False
    for number, line in enumerate(prompt_text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if stripped.startswith("#"):
            prohibitive_section = bool(PROHIBITION_HEADING_RE.search(stripped))
            continue
        if prohibitive_section or PROHIBITION_INLINE_RE.search(line):
            continue
        for pattern in DELEGATION_DIRECTIVE_RES:
            match = pattern.search(line)
            if match:
                leaks.append(
                    {
                        "line": number,
                        "directive": match.group(0),
                        "text": stripped[:200],
                    }
                )
                break
    if not leaks:
        return []
    return [
        finding(
            "RCA.4",
            "runtime_topology",
            leaks[:MAX_LEAK_EVIDENCE],
            "SKILL.md gives an unqualified delegation directive while "
            f"{declaration} declares one shared agent context",
            mode=mode,
        )
    ]


def read_skill_md(skill_dir: Path) -> str:
    try:
        return (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""


def base_report(
    skill_dir: Path,
    *,
    mode: str,
    source: Path | None,
    status: str,
    findings: list[dict[str, Any]],
    role: str | None = None,
    role_mode: str | None = None,
    entry_role: str | None = None,
    roles: list[dict[str, Any]] | None = None,
    applicability_reason: str | None = None,
    nodes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    role_records = roles or []
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "audit_level": AUDIT_LEVEL,
        "target": str(skill_dir),
        "mode": mode,
        "runtime_mode": mode,
        "role_mode": role_mode,
        "entry_role": entry_role,
        "role_count": len(role_records),
        "source": str(source) if source is not None else None,
        "status": status,
        "applicability_reason": applicability_reason,
        "role": role,
        "roles": role_records,
        "nodes": nodes or [],
        "counts": {
            "error": sum(item.get("severity") == "error" for item in findings),
            "warning": sum(
                item.get("severity") == "warning" for item in findings
            ),
        },
        "findings": findings,
        "limitations": [
            "Static contract audit only; it does not judge whether a role improves model output.",
            "Role necessity and rewrite quality remain advisory model review.",
            "Accuracy, token use, latency, and retry reduction require before/after behavior evidence.",
        ],
    }


def role_not_applicable_reason(skill_dir: Path) -> str | None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return None
    try:
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    match = ROLE_NOT_APPLICABLE_RE.search(text)
    return match.group(1).strip() if match else None


def valid_string_list(value: object, *, nonempty: bool) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not nonempty)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def validate_contract_shape(contract: object, *, mode: str) -> list[dict[str, Any]]:
    if not isinstance(contract, dict):
        return [
            finding(
                "RCA.1",
                "role_contract",
                contract,
                "Role contract must be a JSON object",
                mode=mode,
            )
        ]
    findings: list[dict[str, Any]] = []
    schema_version = contract.get("schema_version")
    if schema_version not in {"1.0", "1.1"}:
        findings.append(
            finding(
                "RCA.1",
                "schema_version",
                contract.get("schema_version"),
                "Role contract schema_version must be 1.0 or 1.1",
                mode=mode,
            )
        )
        return findings
    if schema_version == "1.1":
        return findings + validate_v11_contract_shape(contract, mode=mode)
    for field in LEGACY_REQUIRED_STRING_FIELDS:
        value = contract.get(field)
        if not isinstance(value, str) or not value.strip():
            findings.append(
                finding(
                    "RCA.1",
                    field,
                    value,
                    f"{field} must be a non-empty string",
                    mode=mode,
                )
            )
    for field in LEGACY_REQUIRED_NONEMPTY_LIST_FIELDS:
        value = contract.get(field)
        if not valid_string_list(value, nonempty=True):
            findings.append(
                finding(
                    "RCA.1",
                    field,
                    value,
                    f"{field} must be a non-empty string list",
                    mode=mode,
                )
            )
    handoff_to = contract.get("handoff_to")
    if not valid_string_list(handoff_to, nonempty=False):
        findings.append(
            finding(
                "RCA.1",
                "handoff_to",
                handoff_to,
                "handoff_to must be a string list; terminal roles may use an empty list",
                mode=mode,
            )
        )
    return findings


def validate_v11_contract_shape(
    contract: dict[str, Any], *, mode: str
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if contract.get("runtime_mode") != "single_context":
        findings.append(
            finding(
                "RCA.1",
                "runtime_mode",
                contract.get("runtime_mode"),
                "Single-context schema 1.1 requires runtime_mode=single_context",
                mode=mode,
            )
        )
    role_mode = contract.get("role_mode")
    if role_mode not in ROLE_MODES:
        findings.append(
            finding(
                "RCA.1",
                "role_mode",
                role_mode,
                "role_mode must be single_role or sequential_roles",
                mode=mode,
            )
        )
    entry_role = contract.get("entry_role")
    if not isinstance(entry_role, str) or not entry_role.strip():
        findings.append(
            finding(
                "RCA.1",
                "entry_role",
                entry_role,
                "entry_role must be a non-empty role ID",
                mode=mode,
            )
        )
    roles = contract.get("roles")
    if not isinstance(roles, list) or not roles:
        findings.append(
            finding(
                "RCA.1",
                "roles",
                roles,
                "roles must be a non-empty list",
                mode=mode,
            )
        )
        return findings
    for index, role_contract in enumerate(roles):
        prefix = f"roles[{index}]"
        if not isinstance(role_contract, dict):
            findings.append(
                finding(
                    "RCA.1",
                    prefix,
                    role_contract,
                    "Each roles item must be an object",
                    mode=mode,
                )
            )
            continue
        for field in ROLE_REQUIRED_STRING_FIELDS:
            value = role_contract.get(field)
            if not isinstance(value, str) or not value.strip():
                findings.append(
                    finding(
                        "RCA.1",
                        f"{prefix}.{field}",
                        value,
                        f"{field} must be a non-empty string",
                        mode=mode,
                    )
                )
        for field in ROLE_REQUIRED_NONEMPTY_LIST_FIELDS:
            value = role_contract.get(field)
            if not valid_string_list(value, nonempty=True):
                findings.append(
                    finding(
                        "RCA.1",
                        f"{prefix}.{field}",
                        value,
                        f"{field} must be a non-empty string list",
                        mode=mode,
                    )
                )
        for field in ("next", "handoff_to"):
            value = role_contract.get(field)
            if not valid_string_list(value, nonempty=False):
                findings.append(
                    finding(
                        "RCA.1",
                        f"{prefix}.{field}",
                        value,
                        f"{field} must be a string list",
                        mode=mode,
                    )
                )
    return findings


def topology_findings(
    contract: dict[str, Any], *, mode: str
) -> list[dict[str, Any]]:
    if contract.get("schema_version") != "1.1":
        return []
    raw_roles = contract.get("roles")
    if not isinstance(raw_roles, list):
        return []
    roles = [item for item in raw_roles if isinstance(item, dict)]
    role_ids = [
        item.get("id")
        for item in roles
        if isinstance(item.get("id"), str) and item["id"].strip()
    ]
    findings: list[dict[str, Any]] = []
    duplicates = sorted({item for item in role_ids if role_ids.count(item) > 1})
    if duplicates:
        findings.append(
            finding(
                "RCA.3",
                "roles.id",
                duplicates,
                "Role IDs must be unique",
                mode=mode,
            )
        )
    role_id_set = set(role_ids)
    entry_role = contract.get("entry_role")
    if not isinstance(entry_role, str) or entry_role not in role_id_set:
        findings.append(
            finding(
                "RCA.3",
                "entry_role",
                entry_role,
                "entry_role must reference a declared role ID",
                mode=mode,
            )
        )
    role_mode = contract.get("role_mode")
    if role_mode == "single_role" and len(raw_roles) != 1:
        findings.append(
            finding(
                "RCA.3",
                "role_mode",
                {"role_mode": role_mode, "role_count": len(raw_roles)},
                "single_role requires exactly one role",
                mode=mode,
            )
        )
    if role_mode == "sequential_roles" and len(raw_roles) < 2:
        findings.append(
            finding(
                "RCA.3",
                "role_mode",
                {"role_mode": role_mode, "role_count": len(raw_roles)},
                "sequential_roles requires at least two roles",
                mode=mode,
            )
        )

    role_map = {
        item["id"]: item
        for item in roles
        if isinstance(item.get("id"), str)
        and item["id"].strip()
        and role_ids.count(item["id"]) == 1
    }
    incoming = {role_id: 0 for role_id in role_map}
    for role_id, role_contract in role_map.items():
        next_roles = role_contract.get("next")
        if not isinstance(next_roles, list) or not all(
            isinstance(item, str) and item.strip() for item in next_roles
        ):
            continue
        if len(next_roles) > 1 or len(next_roles) != len(set(next_roles)):
            findings.append(
                finding(
                    "RCA.3",
                    f"roles.{role_id}.next",
                    next_roles,
                    "Sequential role chains allow at most one unique internal next role",
                    mode=mode,
                )
            )
        missing = sorted(set(next_roles) - role_id_set)
        if missing:
            findings.append(
                finding(
                    "RCA.3",
                    f"roles.{role_id}.next",
                    missing,
                    "Internal next roles must reference declared role IDs",
                    mode=mode,
                )
            )
        for next_role in next_roles:
            if next_role in incoming:
                incoming[next_role] += 1

    if role_mode == "single_role" and role_map:
        only_role = next(iter(role_map.values()))
        if only_role.get("next") != []:
            findings.append(
                finding(
                    "RCA.3",
                    "roles[0].next",
                    only_role.get("next"),
                    "single_role requires next=[]",
                    mode=mode,
                )
            )

    if isinstance(entry_role, str) and entry_role in role_map:
        reachable: set[str] = set()
        active: set[str] = set()
        cycle = False

        def visit(role_id: str) -> None:
            nonlocal cycle
            if role_id in active:
                cycle = True
                return
            if role_id in reachable:
                return
            active.add(role_id)
            reachable.add(role_id)
            next_roles = role_map[role_id].get("next")
            if isinstance(next_roles, list):
                for next_role in next_roles:
                    if next_role in role_map:
                        visit(next_role)
            active.remove(role_id)

        visit(entry_role)
        if cycle:
            findings.append(
                finding(
                    "RCA.3",
                    "roles.next",
                    role_ids,
                    "Internal role chain must be acyclic",
                    mode=mode,
                )
            )
        unreachable = sorted(role_id_set - reachable)
        if unreachable:
            findings.append(
                finding(
                    "RCA.3",
                    "roles.next",
                    unreachable,
                    "Every role must be reachable from entry_role",
                    mode=mode,
                )
            )
        if incoming.get(entry_role, 0) != 0:
            findings.append(
                finding(
                    "RCA.3",
                    "entry_role",
                    incoming.get(entry_role),
                    "entry_role cannot have an incoming internal handoff",
                    mode=mode,
                )
            )
        joined = sorted(
            role_id for role_id, count in incoming.items()
            if role_id != entry_role and count != 1
        )
        if joined:
            findings.append(
                finding(
                    "RCA.3",
                    "roles.next",
                    joined,
                    "Every non-entry role must have exactly one incoming internal handoff",
                    mode=mode,
                )
            )
        if role_mode == "sequential_roles":
            terminals = [
                role_id
                for role_id, role_contract in role_map.items()
                if role_contract.get("next") == []
            ]
            if len(terminals) != 1:
                findings.append(
                    finding(
                        "RCA.3",
                        "roles.next",
                        terminals,
                        "sequential_roles requires exactly one terminal role",
                        mode=mode,
                    )
                )
    return findings


def role_summaries(
    contract: object,
) -> tuple[str | None, str | None, str | None, list[dict[str, Any]]]:
    if not isinstance(contract, dict):
        return None, None, None, []
    if contract.get("schema_version") == "1.1":
        raw_roles = contract.get("roles")
        roles = (
            [
                {
                    "id": item.get("id"),
                    "role": item.get("role"),
                    "next": (
                        item.get("next")
                        if isinstance(item.get("next"), list)
                        else []
                    ),
                }
                for item in raw_roles
                if isinstance(item, dict)
            ]
            if isinstance(raw_roles, list)
            else []
        )
        role_mode = contract.get("role_mode")
        legacy_role = (
            roles[0].get("role")
            if role_mode == "single_role" and len(roles) == 1
            else None
        )
        return (
            legacy_role if isinstance(legacy_role, str) else None,
            role_mode if isinstance(role_mode, str) else None,
            (
                contract.get("entry_role")
                if isinstance(contract.get("entry_role"), str)
                else None
            ),
            roles,
        )
    role = contract.get("role")
    if isinstance(role, str):
        return role, "single_role", None, [{"id": None, "role": role, "next": []}]
    return None, "single_role", None, []


def single_context_audit(
    skill_dir: Path, role_contract_path: Path
) -> dict[str, Any]:
    mode = "single_context"
    if not role_contract_path.is_file():
        reason = role_not_applicable_reason(skill_dir)
        if reason:
            leaks = delegation_leak_findings(
                read_skill_md(skill_dir),
                mode=mode,
                declaration="the workflow N/A declaration",
            )
            return base_report(
                skill_dir,
                mode=mode,
                source=role_contract_path,
                status="needs_work" if leaks else "not_applicable",
                findings=leaks,
                applicability_reason=reason,
            )
        findings = [
            finding(
                "RCA.0",
                "role_contract",
                str(role_contract_path),
                "Single-context Skill has no role contract or reasoned Role contract audit: N/A declaration",
                mode=mode,
            )
        ]
        return base_report(
            skill_dir,
            mode=mode,
            source=role_contract_path,
            status="not_assessed",
            findings=findings,
        )
    try:
        contract = json.loads(role_contract_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        findings = [
            finding(
                "RCA.1",
                "role_contract",
                str(role_contract_path),
                f"Role contract is unreadable or invalid JSON: {exc}",
                mode=mode,
            )
        ]
        return base_report(
            skill_dir,
            mode=mode,
            source=role_contract_path,
            status="needs_work",
            findings=findings,
        )

    findings = validate_contract_shape(contract, mode=mode)
    if isinstance(contract, dict):
        findings.extend(topology_findings(contract, mode=mode))
    skill_md = skill_dir / "SKILL.md"
    try:
        prompt_text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        findings.append(
            finding(
                "RCA.2",
                "SKILL.md",
                str(skill_md),
                f"SKILL.md is unreadable: {exc}",
                mode=mode,
            )
        )
        prompt_text = ""
    normalized_prompt = normalize(prompt_text)
    if isinstance(contract, dict) and contract.get("schema_version") == "1.1":
        roles = contract.get("roles")
        if isinstance(roles, list):
            for index, role_contract in enumerate(roles):
                if not isinstance(role_contract, dict):
                    continue
                for field in (*ROLE_PROMPT_STRING_FIELDS, *ROLE_PROMPT_LIST_FIELDS):
                    raw_value = role_contract.get(field)
                    values = [raw_value] if isinstance(raw_value, str) else raw_value
                    if not isinstance(values, list):
                        continue
                    missing = [
                        item
                        for item in values
                        if isinstance(item, str)
                        and item.strip()
                        and normalize(item) not in normalized_prompt
                    ]
                    if missing:
                        findings.append(
                            finding(
                                "RCA.2",
                                f"roles[{index}].{field}",
                                missing,
                                "Declared role text is not present in SKILL.md",
                                mode=mode,
                            )
                        )
    elif isinstance(contract, dict):
        for field in (*LEGACY_REQUIRED_STRING_FIELDS, *LEGACY_LIST_FIELDS):
            raw_value = contract.get(field)
            values = [raw_value] if isinstance(raw_value, str) else raw_value
            if not isinstance(values, list):
                continue
            missing = [
                item
                for item in values
                if isinstance(item, str)
                and item.strip()
                and normalize(item) not in normalized_prompt
            ]
            if missing:
                findings.append(
                    finding(
                        "RCA.2",
                        field,
                        missing,
                        "Declared role text is not present in SKILL.md",
                        mode=mode,
                    )
                )
    findings.extend(
        delegation_leak_findings(
            prompt_text, mode=mode, declaration="the role contract"
        )
    )
    role, role_mode, entry_role, roles = role_summaries(contract)
    return base_report(
        skill_dir,
        mode=mode,
        source=role_contract_path,
        status="needs_work" if findings else "pass",
        findings=findings,
        role=role,
        role_mode=role_mode,
        entry_role=entry_role,
        roles=roles,
    )


def workflow_role_audit(
    skill_dir: Path, manifest_path: Path
) -> dict[str, Any]:
    report = audit_workflow(skill_dir, manifest_path)
    raw_manifest: dict[str, Any] = {}
    try:
        parsed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(parsed_manifest, dict):
            raw_manifest = parsed_manifest
    except (OSError, UnicodeError, json.JSONDecodeError):
        pass
    raw_nodes = raw_manifest.get("nodes")
    nodes = [
        {
            "id": item.get("id"),
            "role": (
                item.get("role_contract", {}).get("role")
                if isinstance(item.get("role_contract"), dict)
                else None
            ),
            "next": (
                item.get("next")
                if isinstance(item.get("next"), list)
                else []
            ),
        }
        for item in raw_nodes
        if isinstance(item, dict)
    ] if isinstance(raw_nodes, list) else []
    if not nodes:
        nodes = [
            {"id": item.get("id"), "role": item.get("role"), "next": []}
            for item in report.get("nodes", [])
            if isinstance(item, dict)
        ]
    workflow = report.get("workflow")
    entry_role = (
        workflow.get("entry_node")
        if isinstance(workflow, dict)
        and isinstance(workflow.get("entry_node"), str)
        else None
    )
    manifest_schema = report.get("manifest_schema_version")
    if manifest_schema != "1.1":
        findings = [
            finding(
                "RCA.0",
                "schema_version",
                manifest_schema,
                "Workflow role audit requires manifest schema 1.1 role_contract declarations",
                mode="workflow_nodes",
            )
        ]
        return base_report(
            skill_dir,
            mode="workflow_nodes",
            source=manifest_path,
            status="not_assessed",
            findings=findings,
            role_mode="per_model_call",
            entry_role=entry_role,
            roles=nodes,
            nodes=nodes,
        )
    findings = [
        item
        for item in report.get("findings", [])
        if item.get("id") in ROLE_WORKFLOW_FINDING_IDS
    ]
    return base_report(
        skill_dir,
        mode="workflow_nodes",
        source=manifest_path,
        status="needs_work" if findings else "pass",
        findings=findings,
        role_mode="per_model_call",
        entry_role=entry_role,
        roles=nodes,
        nodes=nodes,
    )


def audit(
    skill_dir: Path,
    manifest_path: Path,
    role_contract_path: Path,
) -> dict[str, Any]:
    if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
        findings = [
            finding(
                "RCA.0",
                "target",
                str(skill_dir),
                "Target Skill directory or SKILL.md does not exist",
                mode="undetermined",
            )
        ]
        return base_report(
            skill_dir,
            mode="undetermined",
            source=None,
            status="not_assessed",
            findings=findings,
        )
    if manifest_path.is_file():
        return workflow_role_audit(skill_dir, manifest_path)
    workflow_reason = workflow_not_applicable_reason(skill_dir)
    if not workflow_reason:
        findings = [
            finding(
                "RCA.0",
                "workflow_applicability",
                str(manifest_path),
                "Declare workflow model-call applicability before selecting node-level or single-context role audit",
                mode="undetermined",
            )
        ]
        return base_report(
            skill_dir,
            mode="undetermined",
            source=None,
            status="not_assessed",
            findings=findings,
        )
    report = single_context_audit(skill_dir, role_contract_path)
    report["workflow_applicability_reason"] = workflow_reason
    return report


def main() -> int:
    force_utf8_streams()
    parser = argparse.ArgumentParser(
        description="Audit the applicable functional role contract for a Skill"
    )
    parser.add_argument("target_skill", type=Path)
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Workflow manifest; defaults to references/workflow-prompts.json",
    )
    parser.add_argument(
        "--role-contract",
        type=Path,
        help="Single-context contract; defaults to references/role-contract.json",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    skill_dir = args.target_skill.resolve()
    manifest_path = (
        args.manifest.resolve()
        if args.manifest is not None
        else skill_dir / DEFAULT_MANIFEST
    )
    role_contract_path = (
        args.role_contract.resolve()
        if args.role_contract is not None
        else skill_dir / DEFAULT_ROLE_CONTRACT
    )
    report = audit(skill_dir, manifest_path, role_contract_path)
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None))
    print(
        "role_contract_audit: "
        f"mode={report['mode']} · status={report['status']} · "
        f"errors={report['counts']['error']}",
        file=sys.stderr,
    )
    return 0 if report["status"] in {"pass", "not_applicable"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
