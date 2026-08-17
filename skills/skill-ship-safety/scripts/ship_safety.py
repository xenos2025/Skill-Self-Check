#!/usr/bin/env python3
"""ship_safety.py — deterministic static checks before external actions.

Answers two script-ownable questions about a target skill without executing it:

1. Promise inventory — does every command documented in SKILL.md (and
   references/*.md) point at a script that exists, with a subcommand the
   script actually implements?
2. External-action scan — which scripts can act on the outside world
   (SMTP / IMAP / HTTP / browser / subprocess), and do they carry a
   dry-run guard?

Behavioral gate-bypass tests require a separately supplied trusted isolation
runner. A temporary directory and sanitized environment are not a security
sandbox, so this stdlib-only script never executes target code.

Usage:
  python ship_safety.py /path/to/target-skill [--exec] [--pretty]

  --exec    Compatibility flag. Target code is NOT executed. The report
            returns execution_unverified and explains that a trusted runner
            is required.
  --pretty  Indent the JSON output.

Output: JSON on stdout (UTF-8). One-line summary on stderr.
Exit code: 0 for static_pass; 1 for stop_ship or execution_unverified.
Stdlib only.
"""

from __future__ import annotations

import ast
import argparse
import json
import re
import sys
from pathlib import Path

PY_CMD_RE = re.compile(
    r"(?:python3?|py\s+-3)\s+"
    r"(?:\"(?P<dq>[^\"]+?\.py)\"|'(?P<sq>[^']+?\.py)'|(?P<bare>[^\s\"'`]+?\.py))"
    r"(?P<rest>[^\n`]*)"
)
NODE_CMD_RE = re.compile(
    r"\bnode\s+(?:\"(?P<dq>[^\"]+?\.(?:mjs|cjs|js|mts|cts|ts))\"|'(?P<sq>[^']+?\.(?:mjs|cjs|js|mts|cts|ts))'|(?P<bare>[^\s\"'`]+?\.(?:mjs|cjs|js|mts|cts|ts)))(?P<rest>[^\n`]*)",
    re.IGNORECASE,
)
SHELL_CMD_RE = re.compile(
    r"\b(?:bash|sh)\s+(?:\"(?P<dq>[^\"]+?\.sh)\"|'(?P<sq>[^']+?\.sh)'|(?P<bare>[^\s\"'`]+?\.sh))(?P<rest>[^\n`]*)",
    re.IGNORECASE,
)
POWERSHELL_CMD_RE = re.compile(
    r"\b(?:pwsh|powershell)(?:\.exe)?\s+(?:-File\s+)?(?:\"(?P<dq>[^\"]+?\.ps1)\"|'(?P<sq>[^']+?\.ps1)'|(?P<bare>[^\s\"'`]+?\.ps1))(?P<rest>[^\n`]*)",
    re.IGNORECASE,
)
SHOPIFY_CLI_RE = re.compile(
    r"\bshopify\s+(?P<operation>store\s+auth|(?:store|app)\s+(?:bulk\s+)?execute)\b"
    r"(?P<rest>[^\n`]*)",
    re.IGNORECASE,
)
GRAPHQL_MUTATION_RE = re.compile(r"(?im)^\s*mutation(?:\s|\{|\()")
GRAPHQL_QUERY_RE = re.compile(r"(?im)^\s*(?:query(?:\s|\{|\()|\{)")
SUB_TOKEN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
IGNORED_SCAN_DIRS = {
    ".git",
    "__pycache__",
    "examples",
    "fixtures",
    "tests",
}

# Capability -> (imported module names, severity without a dry-run guard)
CAPABILITIES = {
    "smtp": ({"smtplib"}, "critical"),
    "imap": ({"imaplib", "poplib"}, "critical"),
    "network": ({"urllib.request", "http.client", "requests", "socket"}, "should_fix"),
    "browser_or_shell": (
        {"webbrowser", "selenium", "playwright", "subprocess"},
        "should_fix",
    ),
}
CAPABILITY_SEVERITY = {
    "smtp": "critical",
    "imap": "critical",
    "business_data_write": "critical",
    "network": "should_fix",
    "browser_or_shell": "should_fix",
    "powershell": "should_fix",
    "shell": "should_fix",
    "shopify_cli": "should_fix",
    "graphql_mutation_definition": "info",
}
GUARD_RE = re.compile(r"(?i)dry[_-]?run|--preview\b")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _doc_files(target: Path) -> list[Path]:
    docs = []
    skill_md = target / "SKILL.md"
    if skill_md.is_file():
        docs.append(skill_md)
    refs = target / "references"
    if refs.is_dir():
        docs.extend(sorted(refs.glob("*.md")))
    return docs


def _nearest_repo_root(target: Path) -> Path | None:
    target_resolved = target.resolve()
    for candidate in target_resolved.parents:
        try:
            relative = target_resolved.relative_to(candidate)
        except ValueError:
            continue
        if relative.parts and relative.parts[0].casefold() == "skills" and (candidate / ".git").exists():
            return candidate
    return None


def _approved_repo_root(target: Path, repo_root: Path | None) -> Path | None:
    selected = repo_root.resolve() if repo_root else _nearest_repo_root(target)
    if selected is None or not selected.is_dir():
        return None
    try:
        relative = target.resolve().relative_to(selected)
    except ValueError:
        return None
    if not relative.parts or relative.parts[0].casefold() != "skills":
        return None
    return selected


def _resolve_script(target: Path, raw: str, repo_root: Path | None = None) -> tuple[Path | None, str | None]:
    normalized = raw.replace("\\", "/")
    rel = Path(normalized)
    if rel.is_absolute() or rel.drive or ".." in rel.parts:
        return None, None

    if rel.parts and rel.parts[0].casefold() == "skills":
        selected_repo = _approved_repo_root(target, repo_root)
        if selected_repo is None:
            return None, None
        candidate = (selected_repo / rel).resolve()
        try:
            candidate.relative_to(selected_repo)
        except ValueError:
            return None, None
        return (candidate, "repo") if candidate.is_file() else (None, None)

    candidates = [target / rel, target / "scripts" / rel.name]
    target_resolved = target.resolve()
    for cand in candidates:
        resolved = cand.resolve()
        try:
            resolved.relative_to(target_resolved)
        except ValueError:
            continue
        if resolved.is_file():
            return resolved, "target"
    hits = [
        p
        for p in target.rglob(rel.name)
        if p.is_file()
        and not any(part.lower() in IGNORED_SCAN_DIRS for part in p.relative_to(target).parts)
    ]
    if hits:
        return hits[0], "target"
    return None, None


def _extract_commands(target: Path) -> list[dict]:
    """Collect documented (script, subcommand) pairs, deduped."""
    seen: dict[tuple[str, str, str], dict] = {}
    for doc in _doc_files(target):
        for lineno, line in enumerate(_read(doc).splitlines(), start=1):
            for kind, command_re in (
                ("python", PY_CMD_RE),
                ("node", NODE_CMD_RE),
                ("shell", SHELL_CMD_RE),
                ("powershell", POWERSHELL_CMD_RE),
            ):
              for m in command_re.finditer(line):
                raw = m.group("dq") or m.group("sq") or m.group("bare") or ""
                if any(mark in raw for mark in ("<", ">", "{", "}")):
                    continue
                rest = (m.group("rest") or "").strip()
                sub = ""
                if rest:
                    token = rest.split()[0]
                    if SUB_TOKEN_RE.match(token):
                        sub = token
                key = (kind, raw.replace("\\", "/"), sub)
                if key not in seen:
                    seen[key] = {
                        "kind": kind,
                        "script": raw.replace("\\", "/"),
                        "subcommand": sub,
                        "doc_file": doc.name,
                        "doc_line": lineno,
                    }
            command_line = line.lstrip(" \t-*>`")
            if not command_line.casefold().startswith("shopify "):
                continue
            for m in SHOPIFY_CLI_RE.finditer(command_line):
                operation = " ".join(m.group("operation").lower().split())
                command = " ".join(m.group(0).strip().split())
                key = ("shopify_cli", operation, command)
                if key not in seen:
                    seen[key] = {
                        "kind": "shopify_cli",
                        "script": "shopify",
                        "subcommand": operation,
                        "command": command,
                        "doc_file": doc.name,
                        "doc_line": lineno,
                    }
    return list(seen.values())


def _command_flag_value(command: str, *flags: str) -> str | None:
    names = "|".join(re.escape(flag) for flag in sorted(flags, key=len, reverse=True))
    match = re.search(
        rf"(?:^|\s)(?:{names})(?:=|\s+)"
        r'(?:"(?P<dq>[^"]*)"|\'(?P<sq>[^\']*)\'|(?P<bare>[^\s`]+))',
        command,
        re.IGNORECASE,
    )
    if not match:
        return None
    return match.group("dq") or match.group("sq") or match.group("bare") or ""


def _resolve_documented_file(
    target: Path,
    raw: str,
    repo_root: Path | None,
) -> tuple[Path | None, str | None]:
    rel = Path(raw.replace("\\", "/"))
    if rel.is_absolute() or rel.drive or ".." in rel.parts:
        return None, None
    if rel.parts and rel.parts[0].casefold() == "skills":
        selected_repo = _approved_repo_root(target, repo_root)
        if selected_repo is None:
            return None, None
        candidate = (selected_repo / rel).resolve()
        try:
            candidate.relative_to(selected_repo)
        except ValueError:
            return None, None
        return (candidate, "repo") if candidate.is_file() else (None, None)
    candidate = (target / rel).resolve()
    try:
        candidate.relative_to(target.resolve())
    except ValueError:
        return None, None
    return (candidate, "target") if candidate.is_file() else (None, None)


def _shopify_command_analysis(
    target: Path,
    command: dict,
    repo_root: Path | None,
) -> dict:
    raw_command = str(command.get("command") or "")
    operation = str(command.get("subcommand") or "")
    query_file = _command_flag_value(raw_command, "--query-file")
    inline_query = _command_flag_value(raw_command, "--query", "-q")
    query_path: Path | None = None
    query_scope: str | None = None
    query_text = inline_query
    if query_file:
        query_path, query_scope = _resolve_documented_file(
            target,
            query_file,
            repo_root,
        )
        if query_path is not None:
            query_text = _read(query_path)

    operation_type = "unknown"
    if query_text:
        if GRAPHQL_MUTATION_RE.search(query_text):
            operation_type = "mutation"
        elif GRAPHQL_QUERY_RE.search(query_text):
            operation_type = "query"

    mutations_enabled = bool(
        re.search(r"(?:^|\s)--allow-mutations(?:\s|$)", raw_command, re.IGNORECASE)
    )
    store_execute = operation in {"store execute", "store bulk execute"}
    guard_status = (
        "mutations_disabled_by_default"
        if store_execute and operation_type == "mutation" and not mutations_enabled
        else "none"
    )
    can_write = operation_type == "mutation" and guard_status == "none"
    if mutations_enabled and operation_type == "unknown":
        can_write = True
    return {
        "operation_type": operation_type,
        "query_file": query_file,
        "query_resolution_scope": query_scope,
        "query_resolved": query_path is not None if query_file else None,
        "mutations_enabled": mutations_enabled,
        "guard_status": guard_status,
        "can_write_business_data": can_write,
    }


def _subcommand_implemented(script_path: Path, sub: str) -> bool:
    try:
        tree = ast.parse(_read(script_path), filename=str(script_path))
    except SyntaxError:
        return False

    docstring_values: set[int] = set()
    owners = [tree, *ast.walk(tree)]
    for owner in owners:
        body = getattr(owner, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            docstring_values.add(id(body[0].value))

    return any(
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value == sub
        and id(node) not in docstring_values
        for node in ast.walk(tree)
    )


def _iter_source_files(target: Path, pattern: str) -> list[Path]:
    files = []
    for path in sorted(target.rglob(pattern)):
        rel_parts = tuple(part.lower() for part in path.relative_to(target).parts[:-1])
        if any(part in IGNORED_SCAN_DIRS for part in rel_parts):
            continue
        files.append(path)
    return files


def _imported_modules(src: str) -> set[str]:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
            modules.update(f"{node.module}.{alias.name}" for alias in node.names)
    return modules


def _scan_external_actions(target: Path) -> list[dict]:
    results = []
    for py in _iter_source_files(target, "*.py"):
        src = _read(py)
        imported = _imported_modules(src)
        caps = [
            name
            for name, (modules, _sev) in CAPABILITIES.items()
            if imported.intersection(modules)
        ]
        if caps:
            results.append(
                {
                    "file": py.relative_to(target).as_posix(),
                    "capabilities": caps,
                    "has_dry_run_guard": bool(GUARD_RE.search(src)),
                }
            )
    for ps1 in _iter_source_files(target, "*.ps1"):
        results.append(
            {
                "file": ps1.relative_to(target).as_posix(),
                "capabilities": ["powershell"],
                "has_dry_run_guard": bool(GUARD_RE.search(_read(ps1))),
            }
        )
    node_patterns = (
        "*.js",
        "*.mjs",
        "*.cjs",
        "*.ts",
        "*.mts",
        "*.cts",
    )
    for pattern in node_patterns:
        for node_file in _iter_source_files(target, pattern):
            src = _read(node_file)
            caps = []
            if re.search(r"(?i)\b(?:fetch|axios|https?\.|node:https|node:http)\b", src):
                caps.append("network")
            if re.search(r"(?i)\b(?:child_process|execFile|execSync|spawnSync|spawn)\b", src):
                caps.append("browser_or_shell")
            if re.search(r"(?i)\b(?:playwright|puppeteer|selenium)\b", src):
                caps.append("browser_or_shell")
            if caps:
                results.append(
                    {
                        "file": node_file.relative_to(target).as_posix(),
                        "capabilities": sorted(set(caps)),
                        "has_dry_run_guard": bool(GUARD_RE.search(src)),
                    }
                )
    for sh in _iter_source_files(target, "*.sh"):
        results.append(
            {
                "file": sh.relative_to(target).as_posix(),
                "capabilities": ["shell"],
                "has_dry_run_guard": bool(GUARD_RE.search(_read(sh))),
            }
        )
    for pattern in ("*.graphql", "*.gql"):
        for graphql_file in _iter_source_files(target, pattern):
            src = _read(graphql_file)
            if GRAPHQL_MUTATION_RE.search(src):
                results.append(
                    {
                        "file": graphql_file.relative_to(target).as_posix(),
                        "capabilities": ["graphql_mutation_definition"],
                        "has_dry_run_guard": False,
                    }
                )
    return results


def audit(target: Path, exec_requested: bool = False, repo_root: Path | None = None) -> dict:
    findings: list[dict] = []
    commands = _extract_commands(target)

    for cmd in commands:
        if cmd.get("kind") == "shopify_cli":
            cmd["shopify_analysis"] = _shopify_command_analysis(
                target,
                cmd,
                repo_root,
            )
            cmd["script_exists"] = True
            cmd["resolution_scope"] = "external_cli"
            cmd["subcommand_implemented"] = None
            cmd["probe"] = {
                "status": "not_run",
                "reason": "Shopify CLI and store behavior require trusted isolation and authenticated target verification",
            }
            continue
        script_path, resolution_scope = _resolve_script(target, cmd["script"], repo_root=repo_root)
        cmd["script_exists"] = script_path is not None
        cmd["resolution_scope"] = resolution_scope
        cmd["subcommand_implemented"] = None
        cmd["probe"] = {
            "status": "not_run",
            "reason": "target execution requires a separately supplied trusted isolation runner",
        }
        where = f'{cmd["doc_file"]}:{cmd["doc_line"]}'
        if script_path is None:
            findings.append(
                {
                    "id": "CMD.1",
                    "severity": "critical",
                    "message": f'documented script not found: {cmd["script"]}',
                    "evidence": where,
                    "source": "script",
                }
            )
            continue
        if cmd["subcommand"] and script_path.suffix.casefold() == ".py":
            ok = _subcommand_implemented(script_path, cmd["subcommand"])
            cmd["subcommand_implemented"] = ok
            if not ok:
                findings.append(
                    {
                        "id": "CMD.2",
                        "severity": "critical",
                        "message": (
                            f'documented subcommand `{cmd["subcommand"]}` not found in '
                            f'{cmd["script"]} — promise without implementation'
                        ),
                        "evidence": where,
                        "source": "script",
                    }
                )
                continue
    external = _scan_external_actions(target)
    for cmd in commands:
        if cmd.get("kind") == "shopify_cli":
            analysis = cmd.get("shopify_analysis") or {}
            capabilities = ["shopify_cli"]
            if (
                analysis.get("operation_type") == "mutation"
                or analysis.get("can_write_business_data") is True
            ):
                capabilities.append("business_data_write")
            external.append(
                {
                    "file": f'{cmd["doc_file"]}:{cmd["doc_line"]}',
                    "capabilities": capabilities,
                    "has_dry_run_guard": bool(GUARD_RE.search(cmd.get("command", ""))),
                    "operation": cmd["subcommand"],
                    "guard_status": analysis.get("guard_status") or "none",
                    "operation_type": analysis.get("operation_type") or "unknown",
                    "query_file": analysis.get("query_file"),
                }
            )
    for entry in external:
        severities = [CAPABILITY_SEVERITY.get(c, "should_fix") for c in entry["capabilities"]]
        worst = "critical" if "critical" in severities else "should_fix"
        if entry.get("guard_status") == "mutations_disabled_by_default":
            findings.append(
                {
                    "id": "EXT.5",
                    "severity": "info",
                    "message": (
                        f'{entry["file"]} references a GraphQL mutation, but '
                        "Shopify store execute blocks mutations without --allow-mutations"
                    ),
                    "evidence": entry["file"],
                    "source": "script",
                }
            )
        elif entry["capabilities"] == ["graphql_mutation_definition"]:
            findings.append(
                {
                    "id": "EXT.4",
                    "severity": "info",
                    "message": (
                        f'{entry["file"]} defines a GraphQL mutation; '
                        "write risk depends on a documented execution entrypoint"
                    ),
                    "evidence": entry["file"],
                    "source": "script",
                }
            )
        elif entry["capabilities"] == ["powershell"]:
            findings.append(
                {
                    "id": "EXT.3",
                    "severity": "should_fix",
                    "message": f'PowerShell automation present: {entry["file"]} — model must review send path',
                    "evidence": entry["file"],
                    "source": "script",
                }
            )
        elif not entry["has_dry_run_guard"]:
            findings.append(
                {
                    "id": "EXT.1",
                    "severity": worst,
                    "message": (
                        f'{entry["file"]} can act externally '
                        f'({"/".join(entry["capabilities"])}) with no dry-run guard'
                    ),
                    "evidence": entry["file"],
                    "source": "script",
                }
            )
        else:
            findings.append(
                {
                    "id": "EXT.2",
                    "severity": "info",
                    "message": (
                        f'{entry["file"]} has a dry-run guard — model must verify '
                        "real send is OFF by default"
                    ),
                    "evidence": entry["file"],
                    "source": "script",
                }
            )

    if not commands:
        findings.append(
            {
                "id": "DOC.1",
                "severity": "info",
                "message": "no supported script or Shopify CLI commands documented in SKILL.md / references — nothing to inventory",
                "evidence": "",
                "source": "script",
            }
        )

    if exec_requested:
        findings.append(
            {
                "id": "EXEC.0",
                "severity": "should_fix",
                "message": (
                    "--exec was requested, but target code was not run: a temporary "
                    "copy is not a security sandbox; supply a trusted isolated runner"
                ),
                "evidence": "",
                "source": "script",
            }
        )

    counts = {
        "critical": sum(1 for f in findings if f["severity"] == "critical"),
        "should_fix": sum(1 for f in findings if f["severity"] == "should_fix"),
        "info": sum(1 for f in findings if f["severity"] == "info"),
    }
    if counts["critical"]:
        verdict = "stop_ship"
    elif exec_requested:
        verdict = "execution_unverified"
    else:
        verdict = "static_pass"
    return {
        "schema_version": "1.0",
        "audit_level": "static_safety_scan",
        "target": str(target),
        "target_platform": "generic",
        "execution": {
            "requested": exec_requested,
            "performed": False,
            "isolation": "unavailable",
            "status": "not_safely_verified",
        },
        "commands": commands,
        "external_actions": external,
        "counts": counts,
        "findings": findings,
        "verdict": verdict,
        "limitations": [
            "target code was not executed",
            "external-action and dry-run detection are static heuristics",
            "final ship approval requires trusted isolated behavior tests",
        ],
        "model_passes_remaining": [
            "gate_bypass_isolated_test",
            "default_off_verification",
            "write_back_integrity",
            "claims_and_compliance_wording",
        ],
    }


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Deterministic static safety scan without executing target code.")
    parser.add_argument("target_skill", type=Path)
    parser.add_argument("--repo-root", type=Path, help="Approved multi-skill repository root for documented skills/... paths.")
    parser.add_argument("--exec", action="store_true", help="Compatibility flag; target code is still not executed.")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    target = args.target_skill.resolve()
    repo_root = args.repo_root.resolve() if args.repo_root else None
    if not target.is_dir() or not (target / "SKILL.md").is_file():
        report = {
            "schema_version": "1.0",
            "audit_level": "static_safety_scan",
            "target": str(target),
            "target_platform": "generic",
            "execution": {
                "requested": args.exec,
                "performed": False,
                "isolation": "unavailable",
                "status": "not_safely_verified",
            },
            "commands": [],
            "external_actions": [],
            "counts": {"critical": 1, "should_fix": 0, "info": 0},
            "findings": [
                {
                    "id": "CMD.0",
                    "severity": "critical",
                    "message": "target is not a skill directory (no SKILL.md)",
                    "evidence": str(target),
                    "source": "script",
                }
            ],
            "verdict": "stop_ship",
            "limitations": ["target is not a skill directory"],
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    report = audit(target, exec_requested=args.exec, repo_root=repo_root)
    indent = 2 if args.pretty else None
    print(json.dumps(report, ensure_ascii=False, indent=indent))
    print(
        f"ship_safety: {report['verdict']} · commands={len(report['commands'])} · "
        f"critical={report['counts']['critical']} "
        f"should_fix={report['counts']['should_fix']}",
        file=sys.stderr,
    )
    return 0 if report["verdict"] == "static_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
