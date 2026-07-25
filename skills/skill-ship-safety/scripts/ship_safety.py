#!/usr/bin/env python3
"""ship_safety.py — deterministic checks for "safe to actually send".

Answers two script-ownable questions about a target skill:

1. Promise inventory — does every command documented in SKILL.md (and
   references/*.md) point at a script that exists, with a subcommand the
   script actually implements?
2. External-action scan — which scripts can act on the outside world
   (SMTP / IMAP / HTTP / browser / subprocess), and do they carry a
   dry-run guard?

Gate-bypass sandbox tests and compliance wording stay model-owned; see
the skill's references/gate-bypass.md.

Usage:
  python ship_safety.py /path/to/target-skill [--exec] [--pretty]

  --exec    Also probe each documented (script, subcommand) pair by
            running it with no extra args in a temp working directory
            with sanitized env (creds stripped, DRY_RUN=1). Opt-in.
  --pretty  Indent the JSON output.

Output: JSON on stdout (UTF-8). One-line summary on stderr.
Exit code: 1 when verdict is stop_ship, else 0. Stdlib only.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PY_CMD_RE = re.compile(
    r"(?:python3?|py\s+-3)\s+"
    r"(?:\"(?P<dq>[^\"]+?\.py)\"|'(?P<sq>[^']+?\.py)'|(?P<bare>[^\s\"'`]+?\.py))"
    r"(?P<rest>[^\n`]*)"
)
SUB_TOKEN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
UNKNOWN_CMD_RE = re.compile(r"(?i)unknown command|未知命令|unrecognized command")

def _import_re(*mods: str) -> re.Pattern:
    """Match `import a, b, mod` and `from mod import ...` lines."""
    alt = "|".join(mods)
    return re.compile(
        rf"(?m)^\s*(?:import\s+[^\n#]*\b(?:{alt})\b|from\s+(?:{alt})\b)"
    )


# Capability -> (regex, severity when no dry-run guard is present)
CAPABILITIES = {
    "smtp": (_import_re("smtplib"), "critical"),
    "imap": (_import_re("imaplib", "poplib"), "critical"),
    "network": (
        re.compile(
            r"(?m)urllib\.request|http\.client"
            r"|^\s*(?:import\s+[^\n#]*\b(?:requests|socket)\b|from\s+(?:requests|socket)\b)"
        ),
        "should_fix",
    ),
    "browser_or_shell": (
        re.compile(
            r"(?m)webbrowser|selenium|playwright"
            r"|^\s*(?:import\s+[^\n#]*\bsubprocess\b|from\s+subprocess\b)"
        ),
        "should_fix",
    ),
}
GUARD_RE = re.compile(r"(?i)dry[_-]?run|--preview\b")
CRED_ENV_RE = re.compile(r"(?i)(smtp|imap|api[_-]?key|token|secret|passw|_pass\b|_pw\b)")


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
    rel = raw.replace("\\", "/").lstrip("./")
    candidates = [target / rel, target / "scripts" / Path(rel).name]
    for cand in candidates:
        if cand.is_file():
            return cand
    hits = [p for p in target.rglob(Path(rel).name) if p.is_file()]
    return hits[0] if hits else None


def _extract_commands(target: Path) -> list[dict]:
    """Collect documented (script, subcommand) pairs, deduped."""
    seen: dict[tuple[str, str], dict] = {}
    for doc in _doc_files(target):
        for lineno, line in enumerate(_read(doc).splitlines(), start=1):
            for m in PY_CMD_RE.finditer(line):
                raw = m.group("dq") or m.group("sq") or m.group("bare") or ""
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
    src = _read(script_path)
    return bool(
        re.search(rf"(?<![A-Za-z0-9_-]){re.escape(sub)}(?![A-Za-z0-9_-])", src)
    )


def _probe(sandbox_root: Path, script_rel: Path, sub: str) -> dict:
    """Run `python script sub` inside a sandbox copy of the target skill.

    The whole skill directory is copied beforehand, so scripts that write
    next to themselves (generated .ps1, __pycache__, reports) touch only
    the sandbox, never the user's real files.
    """
    env = {k: v for k, v in os.environ.items() if not CRED_ENV_RE.search(k)}
    env["DRY_RUN"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        proc = subprocess.run(
            [sys.executable, str(sandbox_root / script_rel)] + ([sub] if sub else []),
            cwd=sandbox_root,
            env=env,
            capture_output=True,
            timeout=20,
        )
        text = (proc.stdout + proc.stderr).decode("utf-8", errors="replace")
        return {
            "ran": True,
            "exit_code": proc.returncode,
            "unknown_command": bool(UNKNOWN_CMD_RE.search(text)),
            "first_line": text.strip().splitlines()[0][:160] if text.strip() else "",
        }
    except subprocess.TimeoutExpired:
        return {"ran": True, "exit_code": None, "unknown_command": False,
                "first_line": "timeout after 20s (long-running entrypoint?)"}
    except OSError as exc:
        return {"ran": False, "exit_code": None, "unknown_command": False,
                "first_line": f"probe error: {exc}"}


def _scan_external_actions(target: Path) -> list[dict]:
    results = []
    for py in sorted(target.rglob("*.py")):
        if "__pycache__" in py.parts:
            continue
        src = _read(py)
        caps = [name for name, (rx, _sev) in CAPABILITIES.items() if rx.search(src)]
        if caps:
            results.append(
                {
                    "file": py.relative_to(target).as_posix(),
                    "capabilities": caps,
                    "has_dry_run_guard": bool(GUARD_RE.search(src)),
                }
            )
    for ps1 in sorted(target.rglob("*.ps1")):
        results.append(
            {
                "file": ps1.relative_to(target).as_posix(),
                "capabilities": ["powershell"],
                "has_dry_run_guard": bool(GUARD_RE.search(_read(ps1))),
            }
        )
    return results


def audit(target: Path, do_exec: bool = False) -> dict:
    findings: list[dict] = []
    commands = _extract_commands(target)

    sandbox = None
    sandbox_root = None
    if do_exec:
        sandbox = tempfile.mkdtemp(prefix="ship_safety_")
        sandbox_root = Path(sandbox) / target.name
        shutil.copytree(target, sandbox_root)

    for cmd in commands:
        script_path = _resolve_script(target, cmd["script"])
        cmd["script_exists"] = script_path is not None
        cmd["subcommand_implemented"] = None
        cmd["probe"] = None
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
        if do_exec:
            script_rel = script_path.relative_to(target)
            cmd["probe"] = _probe(sandbox_root, script_rel, cmd["subcommand"])
            if cmd["probe"]["unknown_command"]:
                findings.append(
                    {
                        "id": "CMD.3",
                        "severity": "critical",
                        "message": (
                            f'probe: {cmd["script"]} rejected documented subcommand '
                            f'`{cmd["subcommand"]}` (Unknown command)'
                        ),
                        "evidence": cmd["probe"]["first_line"],
                        "source": "script",
                    }
                )

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

    if sandbox:
        shutil.rmtree(sandbox, ignore_errors=True)

    counts = {
        "critical": sum(1 for f in findings if f["severity"] == "critical"),
        "should_fix": sum(1 for f in findings if f["severity"] == "should_fix"),
        "info": sum(1 for f in findings if f["severity"] == "info"),
    }
    verdict = "stop_ship" if counts["critical"] else "pass_with_watchlist"
    return {
        "target": str(target),
        "exec_probe": do_exec,
        "commands": commands,
        "external_actions": external,
        "counts": counts,
        "findings": findings,
        "verdict": verdict,
        "model_passes_remaining": [
            "gate_bypass_sandbox_test",
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
            "target": str(target),
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
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    report = audit(target, do_exec="--exec" in argv)
    indent = 2 if "--pretty" in argv else None
    print(json.dumps(report, ensure_ascii=False, indent=indent))
    print(
        f"ship_safety: {report['verdict']} · commands={len(report['commands'])} · "
        f"critical={report['counts']['critical']} "
        f"should_fix={report['counts']['should_fix']}",
        file=sys.stderr,
    )
    return 1 if report["verdict"] == "stop_ship" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
