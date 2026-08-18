#!/usr/bin/env python3
"""Deterministically audit declared model-call prompts in a Skill workflow.

The checker reads files only. It does not execute the target Skill or call a
model. Stdout is JSON; stderr carries one short human summary.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
DEFAULT_MANIFEST = Path("references/workflow-prompts.json")
AUDIT_LEVEL = "workflow_prompt_static"
PROMPT_FORMATS = {"text", "markdown", "xml_tags"}
PLACEHOLDER_RE = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
TAG_RE = re.compile(
    r"<\s*(/?)\s*([A-Za-z][A-Za-z0-9_-]*)"
    r"(?:\s+[^<>]*?)?\s*(/?)\s*>"
)
NOT_APPLICABLE_RE = re.compile(
    r"^\s*Workflow prompt audit:\s*N/A\s*(?:—|–|-|:)\s*(\S.*)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
REQUIRED_LIST_FIELDS = (
    "inputs",
    "decision_gates",
    "output_schema",
    "acceptance_tests",
    "stop_conditions",
)
LIMITATIONS = [
    "Static audit only; it does not execute model calls.",
    "Prompt output quality, token use, and latency require runtime evidence.",
]


def force_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def not_assessed_report(
    skill_dir: Path, manifest_path: Path, message: str
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_level": AUDIT_LEVEL,
        "target": str(skill_dir),
        "manifest": str(manifest_path),
        "status": "not_assessed",
        "workflow": {"id": None, "entry_node": None, "node_count": 0},
        "nodes": [],
        "counts": {"error": 1, "warning": 0},
        "findings": [
            {
                "id": "WPA.0",
                "severity": "error",
                "scope": "audit_input",
                "node_id": None,
                "field": "manifest",
                "evidence": str(manifest_path),
                "message": message,
            }
        ],
        "limitations": LIMITATIONS,
    }


def not_applicable_reason(skill_dir: Path) -> str | None:
    try:
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    match = NOT_APPLICABLE_RE.search(skill_text)
    return match.group(1).strip() if match else None


def not_applicable_report(
    skill_dir: Path, manifest_path: Path, reason: str
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_level": AUDIT_LEVEL,
        "target": str(skill_dir),
        "manifest": str(manifest_path),
        "status": "not_applicable",
        "applicability_reason": reason,
        "workflow": {"id": None, "entry_node": None, "node_count": 0},
        "nodes": [],
        "counts": {"error": 0, "warning": 0},
        "findings": [],
        "limitations": LIMITATIONS,
    }


def manifest_findings(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    checks = (
        (
            "schema_version",
            manifest.get("schema_version") == SCHEMA_VERSION,
            f"Manifest schema_version must be {SCHEMA_VERSION}",
        ),
        (
            "workflow_id",
            isinstance(manifest.get("workflow_id"), str)
            and bool(manifest["workflow_id"].strip()),
            "Manifest requires a non-empty workflow_id",
        ),
        (
            "nodes",
            isinstance(manifest.get("nodes"), list) and bool(manifest["nodes"]),
            "Manifest requires a non-empty nodes list",
        ),
    )
    for field, valid, message in checks:
        if not valid:
            findings.append(
                {
                    "id": "WPA.1",
                    "severity": "error",
                    "scope": "manifest_contract",
                    "node_id": None,
                    "field": field,
                    "evidence": manifest.get(field),
                    "message": message,
                }
            )
    nodes = manifest.get("nodes")
    if isinstance(nodes, list):
        seen: set[str] = set()
        duplicates: set[str] = set()
        for node in nodes:
            if not isinstance(node, dict) or not isinstance(node.get("id"), str):
                continue
            node_id = node["id"]
            if node_id in seen:
                duplicates.add(node_id)
            seen.add(node_id)
        if duplicates:
            findings.append(
                {
                    "id": "WPA.1",
                    "severity": "error",
                    "scope": "manifest_contract",
                    "node_id": None,
                    "field": "nodes",
                    "evidence": sorted(duplicates),
                    "message": "Workflow node IDs must be unique",
                }
            )
    return findings


def contract_findings(node: dict[str, Any]) -> list[dict[str, Any]]:
    node_id = node.get("id") if isinstance(node.get("id"), str) else None
    findings: list[dict[str, Any]] = []

    def add(field: str, message: str) -> None:
        findings.append(
            {
                "id": "WPA.2",
                "severity": "error",
                "scope": "node_contract",
                "node_id": node_id,
                "field": field,
                "message": message,
            }
        )

    for field in REQUIRED_LIST_FIELDS:
        value = node.get(field)
        if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            add(field, f"Node requires a non-empty string list: {field}")
    if not isinstance(node.get("id"), str) or not node["id"].strip():
        add("id", "Node requires a non-empty string ID")
    if node.get("prompt_format") not in PROMPT_FORMATS:
        add(
            "prompt_format",
            "prompt_format must be text, markdown, or xml_tags",
        )
    for field in ("variables", "next"):
        value = node.get(field)
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            add(field, f"Node requires a string list: {field}")
    if not isinstance(node.get("uses_untrusted_sources"), bool):
        add(
            "uses_untrusted_sources",
            "uses_untrusted_sources must be true or false",
        )
    if node.get("uses_untrusted_sources") is True and not (
        isinstance(node.get("source_isolation"), str)
        and node["source_isolation"].strip()
    ):
        findings.append(
            {
                "id": "WPA.7",
                "severity": "error",
                "scope": "source_isolation",
                "node_id": node_id,
                "field": "source_isolation",
                "message": (
                    "Node using untrusted sources requires an explicit instruction/data "
                    "isolation rule"
                ),
            }
        )
    return findings


def prompt_file_findings(
    skill_dir: Path, node: dict[str, Any]
) -> list[dict[str, Any]]:
    node_id = node.get("id") if isinstance(node.get("id"), str) else None
    raw_path = node.get("prompt_file")
    if not isinstance(raw_path, str) or not raw_path.strip():
        return [
            {
                "id": "WPA.3",
                "severity": "error",
                "scope": "prompt_resource",
                "node_id": node_id,
                "field": "prompt_file",
                "evidence": raw_path,
                "message": "Node requires a relative prompt_file path",
            }
        ]
    candidate = (skill_dir / raw_path).resolve()
    if not candidate.is_relative_to(skill_dir):
        message = "prompt_file must stay inside the audited Skill"
    elif not candidate.is_file():
        message = "prompt_file does not exist or is not a file"
    else:
        return []
    return [
        {
            "id": "WPA.3",
            "severity": "error",
            "scope": "prompt_resource",
            "node_id": node_id,
            "field": "prompt_file",
            "evidence": raw_path,
            "message": message,
        }
    ]


def prompt_content_findings(
    skill_dir: Path, node: dict[str, Any]
) -> list[dict[str, Any]]:
    node_id = node.get("id") if isinstance(node.get("id"), str) else None
    raw_path = node.get("prompt_file")
    if not isinstance(raw_path, str) or not raw_path.strip():
        return []
    prompt_path = (skill_dir / raw_path).resolve()
    if not prompt_path.is_relative_to(skill_dir) or not prompt_path.is_file():
        return []
    try:
        prompt = prompt_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [
            {
                "id": "WPA.3",
                "severity": "error",
                "scope": "prompt_resource",
                "node_id": node_id,
                "field": "prompt_file",
                "evidence": raw_path,
                "message": f"prompt_file is not readable UTF-8 text: {exc}",
            }
        ]
    findings: list[dict[str, Any]] = []
    normalized_prompt = re.sub(r"\s+", " ", prompt).casefold()
    linked_fields: list[tuple[str, list[str]]] = []
    for field in (
        "decision_gates",
        "output_schema",
        "acceptance_tests",
        "stop_conditions",
    ):
        value = node.get(field)
        if isinstance(value, list):
            linked_fields.append(
                (field, [item for item in value if isinstance(item, str)])
            )
    source_isolation = node.get("source_isolation")
    if node.get("uses_untrusted_sources") is True and isinstance(
        source_isolation, str
    ):
        linked_fields.append(("source_isolation", [source_isolation]))
    for field, rules in linked_fields:
        missing_rules = [
            rule
            for rule in rules
            if re.sub(r"\s+", " ", rule).casefold() not in normalized_prompt
        ]
        if missing_rules:
            findings.append(
                {
                    "id": "WPA.8",
                    "severity": "error",
                    "scope": "prompt_contract_linkage",
                    "node_id": node_id,
                    "field": field,
                    "evidence": missing_rules,
                    "message": "Declared control text is not present in prompt_file",
                }
            )
    placeholders = {match.strip() for match in PLACEHOLDER_RE.findall(prompt)}
    variables = node.get("variables")
    declared = (
        {item.strip() for item in variables if isinstance(item, str) and item.strip()}
        if isinstance(variables, list)
        else set()
    )
    undeclared = sorted(placeholders - declared)
    if undeclared:
        findings.append(
            {
                "id": "WPA.4",
                "severity": "error",
                "scope": "prompt_variables",
                "node_id": node_id,
                "field": "variables",
                "evidence": undeclared,
                "message": "Prompt contains placeholders not declared by the node",
            }
        )
    if node.get("prompt_format") == "xml_tags":
        stack: list[tuple[str, int]] = []
        for match in TAG_RE.finditer(prompt):
            closing, tag, self_closing = match.groups()
            line = prompt.count("\n", 0, match.start()) + 1
            if self_closing:
                continue
            if not closing:
                stack.append((tag, line))
                continue
            expected = stack[-1][0] if stack else None
            if expected != tag:
                findings.append(
                    {
                        "id": "WPA.5",
                        "severity": "error",
                        "scope": "prompt_structure",
                        "node_id": node_id,
                        "field": "prompt_format",
                        "evidence": {
                            "line": line,
                            "expected": expected,
                            "found": tag,
                        },
                        "message": "XML-style prompt tags are not correctly nested",
                    }
                )
                break
            stack.pop()
        else:
            if stack:
                expected, line = stack[-1]
                findings.append(
                    {
                        "id": "WPA.5",
                        "severity": "error",
                        "scope": "prompt_structure",
                        "node_id": node_id,
                        "field": "prompt_format",
                        "evidence": {
                            "line": line,
                            "expected": expected,
                            "found": "end_of_file",
                        },
                        "message": "XML-style prompt tag is not closed",
                    }
                )
    return findings


def graph_findings(
    manifest: dict[str, Any], nodes: list[Any]
) -> list[dict[str, Any]]:
    node_ids = {
        node.get("id")
        for node in nodes
        if isinstance(node, dict)
        and isinstance(node.get("id"), str)
        and node["id"].strip()
    }
    findings: list[dict[str, Any]] = []
    entry_node = manifest.get("entry_node")
    if not isinstance(entry_node, str) or entry_node not in node_ids:
        findings.append(
            {
                "id": "WPA.6",
                "severity": "error",
                "scope": "workflow_graph",
                "node_id": None,
                "field": "entry_node",
                "evidence": entry_node,
                "message": "entry_node must reference a declared node ID",
            }
        )
    for node in nodes:
        if not isinstance(node, dict):
            continue
        next_nodes = node.get("next")
        if not isinstance(next_nodes, list):
            continue
        missing = sorted(
            {
                item
                for item in next_nodes
                if isinstance(item, str) and item not in node_ids
            }
        )
        if missing:
            findings.append(
                {
                    "id": "WPA.6",
                    "severity": "error",
                    "scope": "workflow_graph",
                    "node_id": node.get("id"),
                    "field": "next",
                    "evidence": missing,
                    "message": "Node references next IDs not declared in the workflow",
                }
            )
    if isinstance(entry_node, str) and entry_node in node_ids:
        node_map = {
            node["id"]: node
            for node in nodes
            if isinstance(node, dict) and node.get("id") in node_ids
        }
        reachable: set[str] = set()
        pending = [entry_node]
        while pending:
            current = pending.pop()
            if current in reachable:
                continue
            reachable.add(current)
            next_nodes = node_map[current].get("next")
            if isinstance(next_nodes, list):
                pending.extend(
                    item
                    for item in next_nodes
                    if isinstance(item, str) and item in node_ids
                )
        unreachable = sorted(node_ids - reachable)
        for unreachable_id in unreachable:
            findings.append(
                {
                    "id": "WPA.6",
                    "severity": "error",
                    "scope": "workflow_graph",
                    "node_id": unreachable_id,
                    "field": "reachable_nodes",
                    "evidence": [unreachable_id],
                    "message": "Declared nodes are not reachable from entry_node",
                }
            )
    return findings


def audit(skill_dir: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Workflow prompt manifest top level must be an object")
    raw_nodes = manifest.get("nodes")
    nodes = raw_nodes if isinstance(raw_nodes, list) else []
    findings = manifest_findings(manifest)
    for node in nodes:
        if not isinstance(node, dict):
            continue
        findings.extend(contract_findings(node))
        findings.extend(prompt_file_findings(skill_dir, node))
        findings.extend(prompt_content_findings(skill_dir, node))
    findings.extend(graph_findings(manifest, nodes))
    error_count = sum(
        finding.get("severity") == "error" for finding in findings
    )
    warning_count = sum(
        finding.get("severity") == "warning" for finding in findings
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_level": AUDIT_LEVEL,
        "target": str(skill_dir),
        "manifest": str(manifest_path),
        "status": "needs_work" if error_count else "pass",
        "workflow": {
            "id": manifest.get("workflow_id"),
            "entry_node": manifest.get("entry_node"),
            "node_count": len(nodes),
        },
        "nodes": [
            {
                "id": node.get("id"),
                "status": (
                    "fail"
                    if any(
                        finding.get("node_id") == node.get("id")
                        for finding in findings
                    )
                    else "pass"
                ),
            }
            for node in nodes
            if isinstance(node, dict)
        ],
        "counts": {"error": error_count, "warning": warning_count},
        "findings": findings,
        "limitations": LIMITATIONS,
    }


def main() -> int:
    force_utf8_streams()
    parser = argparse.ArgumentParser(
        description="Audit declared model-call prompts in a Skill workflow"
    )
    parser.add_argument("skill_dir", type=Path, help="Path to the Skill directory")
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Manifest path; defaults to references/workflow-prompts.json",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    skill_dir = args.skill_dir.expanduser().resolve()
    manifest_path = (
        args.manifest.expanduser().resolve()
        if args.manifest is not None
        else skill_dir / DEFAULT_MANIFEST
    )
    if not skill_dir.is_dir():
        report = not_assessed_report(
            skill_dir, manifest_path, "Target Skill directory does not exist"
        )
    elif not manifest_path.is_file():
        reason = not_applicable_reason(skill_dir)
        report = (
            not_applicable_report(skill_dir, manifest_path, reason)
            if reason is not None
            else not_assessed_report(
                skill_dir, manifest_path, "Workflow prompt manifest does not exist"
            )
        )
    else:
        try:
            report = audit(skill_dir, manifest_path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            report = not_assessed_report(
                skill_dir, manifest_path, f"Workflow prompt manifest is unreadable: {exc}"
            )
    print(
        json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None)
    )
    print(
        f"workflow_prompt_audit: status={report['status']} · "
        f"errors={report['counts']['error']} · "
        f"warnings={report['counts']['warning']}",
        file=sys.stderr,
    )
    return 0 if report["status"] in {"pass", "not_applicable"} else 1


if __name__ == "__main__":
    sys.exit(main())
