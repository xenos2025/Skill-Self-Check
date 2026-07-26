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
import json
import re
import sys
from pathlib import Path

PY_CMD_RE = re.compile(
    r"(?:python3?|py\s+-3)\s+"
    r"(?:\"(?P<dq>[^\"]+?\.py)\"|'(?P<sq>[^']+?\.py)'|(?P<bare>[^\s\"'`]+?\.py))"
    r"(?P<rest>[^\n`]*)"
)
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


def _resolve_script(target: Path, raw: str) -> Path | None:
    normalized = raw.replace("\\", "/")
    rel = Path(normalized)
    if rel.is_absolute() or rel.drive or ".." in rel.parts:
        return None
    candidates = [target / rel, target / "scripts" / rel.name]
    target_resolved = target.resolve()
    for cand in candidates:
        resolved = cand.resolve()
        try:
            resolved.relative_to(target_resolved)
        except ValueError:
            continue
        if resolved.is_file():
            return resolved
    hits = [
        p
        for p in target.rglob(rel.name)
        if p.is_file()
        and not any(part.lower() in IGNORED_SCAN_DIRS for part in p.relative_to(target).parts)
    ]
    return hits[0] if hits else None


def _extract_commands(target: Path) -> list[dict]:
    """Collect documented (script, subcommand) pairs, deduped."""
    seen: dict[tuple[str, str], dict] = {}
    for doc in _doc_files(target):
        for lineno, line in enumerate(_read(doc).splitlines(), start=1):
            for m in PY_CMD_RE.finditer(line):
                raw = m.group("dq") or m.group("sq") or m.group("bare") or ""
                if any(mark in raw for mark in ("<", ">", "{", "}")):
                    continue
                rest = (m.group("rest") or "").strip()
                sub = ""
                if rest:
                    token = rest.split()[0]
                    if SUB_TOKEN_RE.match(token):
                        sub = token
                key = (raw.replace("\\", "/"), sub)
                if key not in seen:
                    seen[key] = {
                        "script": raw.replace("\\", "/"),
                        "subcommand": sub,
                        "doc_file": doc.name,
                        "doc_line": lineno,
                    }
    return list(seen.values())


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
    return results


def audit(target: Path, exec_requested: bool = False) -> dict:
    findings: list[dict] = []
    commands = _extract_commands(target)

    for cmd in commands:
        script_path = _resolve_script(target, cmd["script"])
        cmd["script_exists"] = script_path is not None
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
        if cmd["subcommand"]:
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
    for entry in external:
        severities = [CAPABILITIES[c][1] for c in entry["capabilities"] if c in CAPABILITIES]
        worst = "critical" if "critical" in severities else "should_fix"
        if entry["capabilities"] == ["powershell"]:
            findings.append(
                {
                    "id": "EXT.3",
                    "severity": "should_fix",
                    "message": f'PowerShell automation present: {entry["file"]} — model must review send path',
                    "evidence": "",
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
                    "evidence": "",
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
                    "evidence": "",
                    "source": "script",
                }
            )

    if not commands:
        findings.append(
            {
                "id": "DOC.1",
                "severity": "info",
                "message": "no python commands documented in SKILL.md / references — nothing to inventory",
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
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    target = Path(args[0]).resolve()
    if not target.is_dir() or not (target / "SKILL.md").is_file():
        report = {
            "schema_version": "1.0",
            "audit_level": "static_safety_scan",
            "target": str(target),
            "target_platform": "generic",
            "execution": {
                "requested": "--exec" in argv,
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

    report = audit(target, exec_requested="--exec" in argv)
    indent = 2 if "--pretty" in argv else None
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
