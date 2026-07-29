#!/usr/bin/env python3
"""Deterministic hard-gate checks and informational scores for an Agent Skill.

Usage:
  python hard_gates.py <skill-dir>

Stdout: JSON report
Stderr: human one-line summary
Exit: 0 when the explicit deterministic gate passes; else 1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIRST_SECOND_PERSON_RE = re.compile(
    r"(?i)\b(i can|i'll|i will|you can|you should|i help|let me)\b"
)
WHEN_TRIGGER_RE = re.compile(
    r"(?i)\b(use when|when the user|when users?|when working with|"
    r"when asked|when reviewing|when implementing|triggers?:)\b"
)
# Chinese has no word boundaries, so these are matched without \b.
WHEN_TRIGGER_ZH_RE = re.compile(
    r"(用于|适用|适合|用来|当用户|当需要|需要.{0,6}时|使用场景|适用场景|触发条件)"
)
WHAT_SIGNAL_RE = re.compile(
    r"(?i)\b(generates?|reviews?|extracts?|analyzes?|guides?|checks?|"
    r"validates?|writes?|creates?|processes?|helps agents?|audits?|"
    r"routes?|orchestrates?)\b"
)
WHAT_SIGNAL_ZH_RE = re.compile(
    r"(生成|审查|评审|检查|自检|校验|验证|分析|提取|编排|路由|创建|"
    r"整理|规划|输出|审计|拆解|归档)"
)
COMPLETION_RE = re.compile(
    r"(?i)\b(done when|completion criterion|exit criteria|verify that|"
    r"\*\*done when\*\*)\b"
)
COMPLETION_ZH_RE = re.compile(r"(完成标准|完成条件|出口标准|验收标准|完成于|判定完成)")
TIME_SENSITIVE_RE = re.compile(
    r"(?i)\bbefore (january|february|march|april|may|june|july|august|"
    r"september|october|november|december|\d{4})\b"
)
WINDOWS_PATH_RE = re.compile(r"(?i)(?:^|[\s`])[a-z0-9_\-./]+\\[a-z0-9_\-.\\]+")
ABSOLUTE_WINDOWS_PATH_RE = re.compile(
    r"(?i)(?<![a-z0-9])(?:[a-z]:[\\/]|\\\\[^\\\s]+\\[^\\\s]+)"
    r"[^\s`\"'<>|]*"
)
ABSOLUTE_POSIX_PATH_RE = re.compile(
    r"(?<![\w.])/(?:Users|home|tmp|var|opt|mnt|Volumes)/"
    r"[^\s`\"'<>|]*"
)
RESOURCE_PATH_RE = re.compile(
    r"(?i)(?<![a-z0-9_.-])"
    r"((?:agents|assets|references|scripts)/[^\s`\"'()<>\[\]{}]+)"
)
NOOP_RE = re.compile(
    r"(?i)\b(be careful|think step by step|write good code|always be thorough)\b"
)
NEGATION_RE = re.compile(r"(?i)\b(don't|do not|never|avoid)\b")
# Efficiency guards: loop directives must carry an explicit stop condition,
# otherwise an agent can burn tokens in an open-ended fix/retry cycle.
LOOP_DIRECTIVE_RE = re.compile(
    r"(?i)\b(retry|retries|retrying|re-?run(ning)?|run (it |them )?again|"
    r"try again|repeat(ing)?|iterate|iterating|loop (until|over|through|back)|"
    r"keep looping)\b"
    r"|(重试|重跑|再试|重新运行|重新执行|重复执行|重复运行|再来一遍|"
    r"循环执行|再检查一遍|改完再跑|再跑一次)"
)
LOOP_NEGATION_RE = re.compile(
    r"(?i)\b(don't|do not|never|avoid|instead of)\b"
    r"|(不要|不得|避免|禁止|勿|无需|不用|不必|别再)"
)
LOOP_STOP_RE = re.compile(
    r"(?i)\b(max(imum)?\s+(attempts?|retries|iterations?|tries)|at most|"
    r"no more than|only once|once|twice|one more time|up to \d+|"
    r"\d+\s+(times|attempts?|retries)|timeout|time limit|"
    r"stop (when|if|after)|then stop|give up|abort|escalate|"
    r"ask the user|hand (it )?back|mark (it )?as failed|"
    r"report (the )?(error|failure))\b"
    r"|(最多|上限|不超过|为限|[一两二三四五六七八九十\d]+\s*次|超时|时限|"
    r"停止|中止|终止|放弃|升级|转人工|人工(处理|介入|判断|决定)|报错|"
    r"标记(为)?失败|记录失败)"
)
UNBOUNDED_LOOP_RE = re.compile(
    r"(?i)\b(until (it( is|'s)? )?(perfect|satisfied|happy|good enough)|"
    r"keep (refining|polishing|improving|trying)|"
    r"as many times as (needed|necessary)|repeat as needed)\b"
    r"|(直到满意|直到完美|直到没有问题|不断(优化|打磨|重试|重复)|"
    r"反复(打磨|优化|重试)|无限(次|循环)|一直(改|试|重试|优化))"
)
TOKEN_BUDGET_INPUT_TOKENS = 8000
SCHEMA_VERSION = "1.4"
GATE_POLICY_ID = "explicit-required-checks-v1"
REQUIRED_GATE_POINTS = (
    "file_and_frontmatter",
    "name_valid_and_matched",
    "description_voice_and_triggers",
    "body_actionable",
)
NUMBERED_STEP_RE = re.compile(r"(?m)^\s*\d+\.\s+\S")
CHECKBOX_RE = re.compile(r"(?m)^\s*[-*]\s*\[[ xX]\]\s+")
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+(.+?)\s*$")
# Explicit N/A for support-kit modules (table row or "资料: N/A").
SUPPORT_NA_RES = {
    "references": re.compile(
        r"(?im)(?:^\s*\|\s*)?(资料|references?)\s*(?:\||[:：=])\s*"
        r"(N/?A|不适用|不需要|无|跳过)"
    ),
    "examples": re.compile(
        r"(?im)(?:^\s*\|\s*)?(案例|examples?|示例|样例)\s*(?:\||[:：=])\s*"
        r"(N/?A|不适用|不需要|无|跳过)"
    ),
    "memory": re.compile(
        r"(?im)(?:^\s*\|\s*)?(落地记忆|业务记忆|memory(?:\s*contract)?|状态落盘|"
        r"run.?log)\s*(?:\||[:：=])\s*(N/?A|不适用|不需要|无|跳过)"
    ),
    "scripts": re.compile(
        r"(?im)(?:^\s*\|\s*)?(脚本|scripts?|自动化脚本)\s*(?:\||[:：=])\s*"
        r"(N/?A|不适用|不需要|无|跳过)"
    ),
}
MEMORY_SIGNAL_RE = re.compile(
    r"(?i)(发送记录|回写|冷却期|落表|查重源|MEMORY\.md|run-log|evidence-log|"
    r"score-rules|source-register|持久化|状态库|\.db\b|写入.{0,12}(json|csv|记录)|"
    r"sent_at|跨次|下次启动)"
)
MEMORY_SCHEMA_RE = re.compile(
    r"(?i)(sent_at|字段|结构|schema|ISO.?8601|status\s*=|\"[a-z_]+\"\s*:|"
    r"必填|回写.{0,8}(json|记录)|落表)"
)
SCRIPT_CLAIM_RE = re.compile(
    r"(?i)(scripts/|自动化脚本|脚本目录|脚本索引|调用脚本|"
    r"\.py\b|\.ps1\b|\.sh\b|automation\s+(?:script|tool|runner|command)|"
    r"automates?|codeact|calendar script|"
    r"python\s+\S+\.py)"
)
EXAMPLE_HEADING_RE = re.compile(
    r"(?im)^(#{1,6})\s+.*(example|examples|案例|示例|样例|worked example)\s*$"
)
STANDARD_PACKAGE_DIRS = {"agents", "assets", "examples", "references", "scripts"}
RUNTIME_DIR_NAMES = {
    "build",
    "dist",
    "export",
    "exports",
    "generated",
    "output",
    "outputs",
    "results",
    "生成结果",
    "生成的图片",
    "生成的图像",
    "生成的模特图",
}
RESIDUE_NAMES = {
    ".ds_store",
    "desktop.ini",
    "thumbs.db",
}
RESIDUE_SUFFIXES = {
    ".7z",
    ".bak",
    ".gz",
    ".rar",
    ".tar",
    ".tmp",
    ".zip",
}
TEXT_RESOURCE_SUFFIXES = {
    ".json",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
}
HASH_MIN_BYTES = 64 * 1024
HASH_MAX_FILE_BYTES = 25 * 1024 * 1024
HASH_MAX_FILES = 500


def read_skill_text(path: Path) -> tuple[str, str | None]:
    """Read SKILL.md, tolerating non-UTF-8 files.

    Returns (text, fallback_encoding). fallback_encoding is None for clean
    UTF-8; otherwise it names what was used so the caller can raise a finding.
    Agent tooling expects UTF-8, but Windows editors still emit GBK, and a
    decode crash would leave the model with no JSON at all.
    """
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(enc), None
        except UnicodeDecodeError:
            pass
    for enc in ("gb18030", "big5", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8 with invalid bytes replaced"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, bool]:
    if not text.startswith("---"):
        return {}, text, False
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text, False
    raw = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    data: dict[str, str] = {}
    key = None
    buf: list[str] = []
    for line in raw.splitlines():
        if key and (line.startswith("  ") or line.startswith("\t") or line.startswith("|")):
            buf.append(line.strip().lstrip("|").strip())
            continue
        if key:
            data[key] = " ".join(buf).strip()
            key, buf = None, []
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", ">-", "|", "|-"):
            buf = []
            continue
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        data[key] = val
        key = None
    if key:
        data[key] = " ".join(buf).strip()
    return data, body, True


def package_finding(
    item_id: str,
    severity: str,
    message: str,
    evidence: str = "",
    scope: str = "skill package",
) -> dict:
    return {
        "id": item_id,
        "severity": severity,
        "message": message,
        "evidence": evidence,
        "source": "script",
        "scope": scope,
        "confidence": "high",
        "verification_status": "verified",
    }


def iter_package_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(skill_dir)
        if any(
            part in {".git", ".playwright-cli", "__pycache__"}
            for part in relative.parts
        ):
            continue
        files.append(path)
    return files


def read_text_resource(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def is_path_placeholder(value: str) -> bool:
    lowered = value.casefold()
    return any(
        marker in lowered
        for marker in (
            "<",
            ">",
            "${",
            "$env:",
            "%userprofile%",
            "/absolute/path",
            "/path/to",
            "\\path\\to",
            "your-",
            "your_",
        )
    )


def collect_absolute_path_evidence(
    skill_dir: Path, files: list[Path]
) -> list[str]:
    evidence: list[str] = []
    candidates = [
        path
        for path in files
        if path.name == "SKILL.md"
        or (
            path.suffix.casefold() in TEXT_RESOURCE_SUFFIXES
            and path.relative_to(skill_dir).parts[0]
            in {"agents", "references"}
        )
    ]
    for path in candidates:
        text = read_text_resource(path)
        if text is None:
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            hits = [
                match.group(0)
                for pattern in (
                    ABSOLUTE_WINDOWS_PATH_RE,
                    ABSOLUTE_POSIX_PATH_RE,
                )
                for match in pattern.finditer(line)
            ]
            if any(not is_path_placeholder(hit) for hit in hits):
                relative = path.relative_to(skill_dir).as_posix()
                evidence.append(f"{relative}:{line_number}")
    return sorted(set(evidence))


def clean_resource_token(token: str) -> str:
    return token.rstrip(".,;:!?，。；：！？、）】》")


def collect_resource_link_evidence(
    skill_dir: Path, source_text: str
) -> tuple[list[str], int]:
    missing: list[str] = []
    references = {
        clean_resource_token(match.group(1)).replace("\\", "/")
        for match in RESOURCE_PATH_RE.finditer(source_text)
    }
    for reference in sorted(references):
        target = skill_dir.joinpath(*reference.split("/"))
        if not target.exists():
            missing.append(reference)
    return missing, len(references)


def collect_duplicate_groups(
    skill_dir: Path, files: list[Path]
) -> tuple[list[dict], bool]:
    eligible = []
    for path in files:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if HASH_MIN_BYTES <= size <= HASH_MAX_FILE_BYTES:
            eligible.append((path, size))
    eligible.sort(key=lambda item: item[0].as_posix().casefold())
    truncated = len(eligible) > HASH_MAX_FILES
    groups: dict[tuple[int, str], list[str]] = {}
    for path, size in eligible[:HASH_MAX_FILES]:
        digest = hashlib.sha256()
        try:
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        except OSError:
            continue
        key = (size, digest.hexdigest())
        groups.setdefault(key, []).append(path.relative_to(skill_dir).as_posix())
    duplicates = [
        {
            "file_count": len(paths),
            "bytes_each": size,
            "paths": paths[:8],
        }
        for (size, _), paths in groups.items()
        if len(paths) > 1
    ]
    duplicates.sort(key=lambda item: (-item["bytes_each"], item["paths"][0]))
    return duplicates[:10], truncated


def assess_package_health(
    skill_dir: Path,
    frontmatter: dict[str, str] | None,
    source_text: str,
) -> tuple[dict, list[dict]]:
    """Assess whether the target is one installable Skill package.

    Content scores remain useful diagnostics, but maturity scoring must only
    consume them when this preflight is assessable.
    """
    findings: list[dict] = []
    files = iter_package_files(skill_dir)
    declared_name = str((frontmatter or {}).get("name") or "").strip()
    skill_md_present = (skill_dir / "SKILL.md").is_file()
    nested_roots = sorted(
        path.parent.relative_to(skill_dir).as_posix()
        for path in files
        if path.name == "SKILL.md"
        and path.parent != skill_dir
        and path.relative_to(skill_dir).parts[0] != "examples"
    )
    named_child = (
        skill_dir / declared_name
        if declared_name and declared_name != skill_dir.name
        else None
    )
    pseudo_root = bool(named_child and named_child.is_dir())
    single_root_ok = skill_md_present and not nested_roots and not pseudo_root
    if not skill_md_present:
        findings.append(
            package_finding(
                "PKG.1",
                "critical",
                "Target is not a Skill package root because SKILL.md is missing",
                "SKILL.md",
                "package root",
            )
        )
    if nested_roots:
        findings.append(
            package_finding(
                "PKG.1b",
                "critical",
                "Multiple non-fixture Skill roots were found under one target",
                f"nested_roots={len(nested_roots)}",
                "package root",
            )
        )
    if pseudo_root:
        findings.append(
            package_finding(
                "PKG.1c",
                "critical",
                "A child directory repeats the declared Skill name, so the package root is ambiguous",
                f"declared-name child directory exists; contains_SKILL.md={bool((named_child / 'SKILL.md').is_file())}",
                "package root",
            )
        )

    name_matches = bool(declared_name) and declared_name == skill_dir.name
    if declared_name and not name_matches:
        findings.append(
            package_finding(
                "PKG.2",
                "critical",
                "Declared Skill name does not match the package root directory",
                "frontmatter name and root basename differ",
                "package identity",
            )
        )

    top_dirs = sorted(
        path.name for path in skill_dir.iterdir() if path.is_dir()
    )
    runtime_dirs = [
        name for name in top_dirs if name.casefold() in RUNTIME_DIR_NAMES
    ]
    nonstandard_dirs = [
        name
        for name in top_dirs
        if name.casefold() not in STANDARD_PACKAGE_DIRS
        and name not in runtime_dirs
        and not (declared_name and name == declared_name)
    ]
    populated_runtime_dirs = [
        name
        for name in runtime_dirs
        if _dir_has_files(skill_dir / name)
    ]
    if populated_runtime_dirs:
        findings.append(
            package_finding(
                "PKG.3",
                "critical",
                "Runtime or generated output files are mixed into the installable Skill package",
                f"populated_output_dirs={len(populated_runtime_dirs)}",
                "package topology",
            )
        )
    elif runtime_dirs:
        findings.append(
            package_finding(
                "PKG.3",
                "should_fix",
                "Runtime/output directories should live outside the installable Skill package",
                f"output_dirs={len(runtime_dirs)}",
                "package topology",
            )
        )
    if nonstandard_dirs:
        findings.append(
            package_finding(
                "PKG.3b",
                "should_fix",
                "Non-standard top-level content directories need consolidation into assets/, references/, scripts/, agents/, or examples/",
                f"nonstandard_dirs={len(nonstandard_dirs)}",
                "package topology",
            )
        )

    absolute_path_evidence = collect_absolute_path_evidence(skill_dir, files)
    if absolute_path_evidence:
        findings.append(
            package_finding(
                "PKG.4",
                "critical",
                "Machine-specific absolute paths make the Skill package non-portable",
                "; ".join(absolute_path_evidence[:12]),
                "path portability",
            )
        )

    missing_resources, resource_reference_count = collect_resource_link_evidence(
        skill_dir, source_text
    )
    if missing_resources:
        findings.append(
            package_finding(
                "PKG.5",
                "critical",
                "One or more explicitly referenced package resources do not exist",
                f"missing_references={len(missing_resources)}",
                "resource links",
            )
        )

    residue_files = [
        path.relative_to(skill_dir).as_posix()
        for path in files
        if path.name.casefold() in RESIDUE_NAMES
        or path.suffix.casefold() in RESIDUE_SUFFIXES
    ]
    irregular_names = [
        path.relative_to(skill_dir).as_posix()
        for path in files
        if len(path.name) > 120
        or path.name != path.name.strip()
        or re.search(r"[<>:\"|?*]", path.name)
    ]
    if residue_files:
        findings.append(
            package_finding(
                "PKG.6",
                "should_fix",
                "Archive, temporary, or operating-system residue files are present",
                f"residue_files={len(residue_files)}",
                "file hygiene",
            )
        )
    if irregular_names:
        findings.append(
            package_finding(
                "PKG.6b",
                "should_fix",
                "One or more filenames are non-portable or excessively long",
                f"irregular_names={len(irregular_names)}",
                "filename health",
            )
        )

    duplicate_groups, hash_scan_truncated = collect_duplicate_groups(
        skill_dir, files
    )
    if duplicate_groups:
        findings.append(
            package_finding(
                "PKG.7",
                "should_fix",
                "Duplicate large resources increase package ambiguity and size",
                f"duplicate_groups={len(duplicate_groups)}",
                "resource uniqueness",
            )
        )

    checks = {
        "single_skill_root": {
            "status": "pass" if single_root_ok else "fail",
            "blocking": not single_root_ok,
            "nested_root_count": len(nested_roots),
            "declared_name_child": pseudo_root,
        },
        "name_matches_root": {
            "status": "pass" if name_matches else "fail",
            "blocking": not name_matches,
            "declared_name": declared_name or None,
            "root_name": skill_dir.name,
        },
        "standard_topology": {
            "status": (
                "fail"
                if populated_runtime_dirs
                else "warn"
                if runtime_dirs or nonstandard_dirs
                else "pass"
            ),
            "blocking": bool(populated_runtime_dirs),
            "top_level_directory_count": len(top_dirs),
            "nonstandard_directory_count": len(nonstandard_dirs),
            "runtime_directory_count": len(runtime_dirs),
            "populated_runtime_directory_count": len(populated_runtime_dirs),
        },
        "portable_paths": {
            "status": "fail" if absolute_path_evidence else "pass",
            "blocking": bool(absolute_path_evidence),
            "absolute_path_reference_count": len(absolute_path_evidence),
        },
        "resource_links": {
            "status": "fail" if missing_resources else "pass",
            "blocking": bool(missing_resources),
            "reference_count": resource_reference_count,
            "missing_count": len(missing_resources),
        },
        "file_hygiene": {
            "status": "warn" if residue_files or irregular_names else "pass",
            "blocking": False,
            "residue_count": len(residue_files),
            "irregular_name_count": len(irregular_names),
        },
        "resource_uniqueness": {
            "status": "warn" if duplicate_groups else "pass",
            "blocking": False,
            "duplicate_group_count": len(duplicate_groups),
            "scan_truncated": hash_scan_truncated,
            "groups": duplicate_groups,
        },
    }
    blocking_checks = [
        key for key, record in checks.items() if record.get("blocking")
    ]
    warning_checks = [
        key for key, record in checks.items() if record.get("status") == "warn"
    ]
    assessable = not blocking_checks
    return {
        "status": (
            "valid_skill_package" if assessable else "invalid_skill_package"
        ),
        "assessable": assessable,
        "checks": checks,
        "installability": {
            "status": "pass" if assessable else "fail",
            "static_only": True,
            "blocking_checks": blocking_checks,
        },
        "summary": {
            "blocking_check_count": len(blocking_checks),
            "warning_check_count": len(warning_checks),
            "files_scanned": len(files),
        },
    }, findings


def heading_map(body: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for m in HEADING_RE.finditer(body):
        title = m.group(2).strip().lower()
        found[title] = m.group(2).strip()
    return found


def has_heading_containing(headings: dict[str, str], *needles: str) -> bool:
    for h in headings:
        if all(n in h for n in needles):
            return True
        if any(n == h or n in h for n in needles):
            return True
    return False


def _dir_has_files(path: Path, suffixes: set[str] | None = None) -> bool:
    if not path.is_dir():
        return False
    for f in path.rglob("*"):
        if not f.is_file():
            continue
        if f.name.startswith("."):
            continue
        if suffixes is None or f.suffix.lower() in suffixes:
            return True
    return False


def _example_section_present(body: str) -> bool:
    for m in EXAMPLE_HEADING_RE.finditer(body):
        rest = body[m.end() : m.end() + 400]
        # Next heading cuts the section; require a bit of substance.
        next_h = HEADING_RE.search(rest)
        chunk = rest[: next_h.start()] if next_h else rest
        if len(re.sub(r"\s+", "", chunk)) >= 40:
            return True
    return False


def assess_support_kit(
    skill_dir: Path, body: str, has_steps: bool
) -> tuple[dict, list[dict]]:
    """Score references / examples / memory / scripts. N/A does not dock.

    The core gate is unaffected — failures are should_fix only.
    """
    findings: list[dict] = []
    modules: dict[str, dict] = {}

    def mark(key: str, status: str, reason: str) -> None:
        modules[key] = {"status": status, "reason": reason}

    na = {k: bool(rx.search(body)) for k, rx in SUPPORT_NA_RES.items()}

    # --- references (资料) ---
    refs_dir = skill_dir / "references"
    refs_present = _dir_has_files(refs_dir)
    refs_linked = bool(re.search(r"(?i)references/", body))
    if na["references"]:
        mark("references", "na", "explicit N/A in SKILL.md")
    elif refs_present:
        mark(
            "references",
            "pass",
            "references/ present"
            + (" and linked" if refs_linked else " (link from SKILL.md recommended)"),
        )
        if not refs_linked:
            findings.append(
                {
                    "id": "6.1b",
                    "severity": "nice",
                    "message": "references/ exists but SKILL.md does not link to it",
                    "evidence": "",
                    "source": "script",
                }
            )
    elif has_steps or refs_linked:
        mark("references", "fail", "workflow skill needs references/ (or mark 资料 N/A)")
        findings.append(
            {
                "id": "6.1",
                "severity": "should_fix",
                "message": "Missing references/ materials pack (资料); add files or mark 资料 N/A",
                "evidence": "",
                "source": "script",
            }
        )
    else:
        mark("references", "na", "short/non-workflow skill; no references/ required")

    # --- examples (案例) ---
    examples_dir = skill_dir / "examples"
    examples_present = _dir_has_files(examples_dir) or _example_section_present(body)
    if na["examples"]:
        mark("examples", "na", "explicit N/A in SKILL.md")
    elif examples_present:
        mark("examples", "pass", "examples/ or in-body example section present")
    elif has_steps:
        mark("examples", "fail", "workflow skill needs examples/ or ## 案例 (or mark 案例 N/A)")
        findings.append(
            {
                "id": "6.2",
                "severity": "should_fix",
                "message": "Missing examples/ case pack (案例); add a fixture/example or mark 案例 N/A",
                "evidence": "",
                "source": "script",
            }
        )
    else:
        mark("examples", "na", "non-workflow skill; no examples/ required")

    # --- memory (落地记忆) ---
    memory_claimed = bool(MEMORY_SIGNAL_RE.search(body))
    memory_schema = bool(MEMORY_SCHEMA_RE.search(body))
    if na["memory"]:
        mark("memory", "na", "explicit N/A in SKILL.md")
    elif memory_claimed and memory_schema:
        mark("memory", "pass", "persistent state path/fields described")
    elif memory_claimed:
        mark("memory", "fail", "mentions logs/state but no field/path contract")
        findings.append(
            {
                "id": "6.3",
                "severity": "should_fix",
                "message": "落地记忆 claimed without path/fields (e.g. sent_at, JSON shape); "
                "document the record schema or mark 落地记忆 N/A",
                "evidence": "",
                "source": "script",
            }
        )
    else:
        mark("memory", "na", "no cross-run state/log signals detected")

    # --- scripts ---
    scripts_dir = skill_dir / "scripts"
    script_files = []
    if scripts_dir.is_dir():
        script_files = [
            p
            for p in scripts_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in {".py", ".sh", ".ps1", ".js", ".ts"}
        ]
    scripts_on_disk = bool(script_files)
    scripts_claimed = bool(SCRIPT_CLAIM_RE.search(body)) or scripts_on_disk
    scripts_documented = False
    if script_files:
        names = {p.name for p in script_files}
        scripts_documented = any(name in body for name in names) or bool(
            re.search(r"(?i)scripts/\S+", body)
        )
    if na["scripts"]:
        mark("scripts", "na", "explicit N/A in SKILL.md")
    elif scripts_on_disk and scripts_documented:
        mark("scripts", "pass", "scripts/ present and named in SKILL.md")
    elif scripts_on_disk and not scripts_documented:
        mark("scripts", "fail", "scripts/ exists but SKILL.md does not document when to run")
        findings.append(
            {
                "id": "6.4",
                "severity": "should_fix",
                "message": "scripts/ present but not documented in SKILL.md (when to run / output)",
                "evidence": ", ".join(sorted(p.name for p in script_files)[:6]),
                "source": "script",
            }
        )
    elif scripts_claimed and not scripts_on_disk:
        mark("scripts", "fail", "body claims scripts/automation but scripts/ missing")
        findings.append(
            {
                "id": "6.4b",
                "severity": "should_fix",
                "message": "Skill claims scripts/automation but has no scripts/ directory",
                "evidence": "",
                "source": "script",
            }
        )
    else:
        mark("scripts", "na", "no script/automation claim detected")

    applicable = [k for k, v in modules.items() if v["status"] != "na"]
    passed = [k for k in applicable if modules[k]["status"] == "pass"]
    score = len(passed)
    max_score = len(applicable)
    kit = {
        "score": score,
        "max": max_score,
        "modules": modules,
        "kit_complete": score == max_score,
    }
    return kit, findings


def assess_efficiency(
    body: str, body_line_offset: int, estimated_tokens: int | None
) -> tuple[dict, list[dict]]:
    """Static loop-guard and token-budget signals (EFF.*).

    Deterministic proxies only: a static scan cannot prove a run terminates,
    but it catches loop/retry instructions that ship without a stop condition
    and instruction files whose baseline token load is already oversized.
    Findings are should_fix — they warn and do not block gate_verdict.
    """
    findings: list[dict] = []
    lines = body.splitlines()
    directive_lines: list[int] = []
    unguarded_lines: list[int] = []
    unbounded_lines: list[int] = []
    for idx, line in enumerate(lines):
        file_lineno = idx + 1 + body_line_offset
        if UNBOUNDED_LOOP_RE.search(line):
            unbounded_lines.append(file_lineno)
        match = LOOP_DIRECTIVE_RE.search(line)
        if not match:
            continue
        # An anti-loop instruction ("do not rerun for the same evidence") is a
        # guard, not a loop. Negations may sit on the previous wrapped line.
        negation_scope = (lines[idx - 1] if idx else "") + " " + line[: match.start()]
        if LOOP_NEGATION_RE.search(negation_scope):
            continue
        directive_lines.append(file_lineno)
        window = " ".join(lines[max(0, idx - 1) : idx + 3])
        if not LOOP_STOP_RE.search(window):
            unguarded_lines.append(file_lineno)
    if unguarded_lines:
        findings.append(
            package_finding(
                "EFF.1",
                "should_fix",
                "Loop/retry instruction has no nearby stop condition; add max "
                "attempts, a timeout, or an escalate-to-human exit",
                "SKILL.md lines "
                + ", ".join(str(n) for n in unguarded_lines[:8]),
                "loop guard",
            )
        )
    if unbounded_lines:
        findings.append(
            package_finding(
                "EFF.2",
                "should_fix",
                "Unbounded refinement phrasing ('until perfect' / 直到满意 / "
                "不断优化); give the loop a run-bound exit criterion",
                "SKILL.md lines "
                + ", ".join(str(n) for n in unbounded_lines[:8]),
                "loop guard",
            )
        )
    over_budget = (
        estimated_tokens is not None
        and estimated_tokens > TOKEN_BUDGET_INPUT_TOKENS
    )
    if over_budget:
        findings.append(
            package_finding(
                "EFF.3",
                "should_fix",
                f"Static instruction load is ~{estimated_tokens} tokens "
                f"(> {TOKEN_BUDGET_INPUT_TOKENS} recommended); move long "
                "material into references/ to cut per-run cost",
                "SKILL.md",
                "token budget",
            )
        )
    efficiency = {
        "loop_guard": {
            "label": "循环护栏",
            "status": (
                "warn"
                if unguarded_lines or unbounded_lines
                else "pass"
                if directive_lines
                else "not_applicable"
            ),
            "loop_directive_count": len(directive_lines),
            "guarded_count": len(directive_lines) - len(unguarded_lines),
            "unguarded_lines": unguarded_lines[:12],
            "unbounded_phrase_lines": unbounded_lines[:12],
            "scope": "SKILL.md static instruction text",
            "method": "line-window scan for loop directives, stop signals, and unbounded phrasing",
            "evidence": "SKILL.md",
        },
        "token_budget": {
            "max_recommended_input_tokens": TOKEN_BUDGET_INPUT_TOKENS,
            "status": (
                "not_assessed"
                if estimated_tokens is None
                else "exceeded"
                if over_budget
                else "within"
            ),
        },
    }
    return efficiency, findings


def detect_check_axes(body: str) -> tuple[bool, list[str]]:
    """Heuristic: a list of 2+ short axis-like bullets under check/review/axis headings."""
    axes: list[str] = []
    lines = body.splitlines()
    in_axis_section = False
    for line in lines:
        hm = HEADING_RE.match(line)
        if hm:
            title = hm.group(2).lower()
            in_axis_section = any(
                k in title
                for k in (
                    "check axis",
                    "check axes",
                    "review axis",
                    "维度",
                    "检查轴",
                    "检查项",
                    "what to inspect",
                    "inspection axes",
                )
            ) or title in {"check axes", "axes", "checklist axes"}
            # Broader: heading is exactly/starts with checklist used as axis list
            if not in_axis_section and (
                title.startswith("check axes") or title.startswith("检查")
            ):
                in_axis_section = True
            continue
        if not in_axis_section:
            continue
        # Stay in section until the next heading; prose between heading and bullets is OK
        bm = re.match(r"^\s*[-*]\s+(.+)$", line)
        if not bm:
            continue
        item = bm.group(1).strip()
        # Skip checkbox verification lines
        if item.startswith("[") and "]" in item[:4]:
            continue
        item = re.sub(r"\*\*(.+?)\*\*", r"\1", item)
        short = re.split(r"\s*(?:—|–|:|\|)\s*", item, maxsplit=1)[0].strip()
        if 2 <= len(short) <= 48:
            axes.append(short)
    if len(axes) < 2:
        for m in re.finditer(
            r"(?im)^\s*[-*]\s+(\*\*)?(color|colors|构图|composition|copy|文案|"
            r"typography|layout|accessibility|无障碍|contrast|spacing|hierarchy|"
            r"security|performance|tests?)(\*\*)?\b",
            body,
        ):
            label = re.sub(r"\*\*", "", m.group(0))
            label = re.sub(r"^\s*[-*]\s+", "", label).strip()[:40]
            axes.append(label)
    seen: set[str] = set()
    uniq: list[str] = []
    for a in axes:
        k = a.lower()
        if k not in seen:
            seen.add(k)
            uniq.append(a)
    return len(uniq) >= 2, uniq[:12]


def check_skill(skill_dir: Path) -> dict:
    skill_dir = skill_dir.resolve()
    skill_md = skill_dir / "SKILL.md"
    findings: list[dict] = []
    points = {
        "file_and_frontmatter": False,
        "name_valid_and_matched": False,
        "description_voice_and_triggers": False,
        "body_actionable": False,
        "verification_or_done_when": False,
    }
    contract = {
        "when_to_use": False,
        "when_not": False,
        "check_axes_named": False,
        "verification_checkboxes": False,
        "rationalizations_or_red_flags": False,
    }

    def fail(item_id: str, severity: str, message: str, evidence: str = "") -> None:
        findings.append(
            {
                "id": item_id,
                "severity": severity,
                "message": message,
                "evidence": evidence,
                "source": "script",
            }
        )

    def ok_note(item_id: str, message: str) -> None:
        findings.append(
            {
                "id": item_id,
                "severity": "info",
                "message": message,
                "evidence": "",
                "source": "script",
            }
        )

    if not skill_md.is_file():
        fail("1.1", "critical", "Missing SKILL.md in skill directory")
        package_health, package_findings = assess_package_health(
            skill_dir, None, ""
        )
        findings.extend(package_findings)
        return finalize(
            skill_dir,
            None,
            "",
            findings,
            points,
            contract,
            0,
            support_kit={
                "score": 0,
                "max": 0,
                "modules": {},
                "kit_complete": False,
            },
            package_health=package_health,
        )

    text, fallback_encoding = read_skill_text(skill_md)
    fm, body, has_fm = parse_frontmatter(text)
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    package_health, package_findings = assess_package_health(
        skill_dir, fm, text
    )
    findings.extend(package_findings)

    if fallback_encoding:
        fail(
            "1.11",
            "should_fix",
            "SKILL.md is not UTF-8; re-save as UTF-8 so every agent tool reads it",
            f"decoded as {fallback_encoding}",
        )

    if not has_fm:
        fail("1.2", "critical", "Missing YAML frontmatter delimited by ---")
    else:
        if "name" in fm and "description" in fm:
            points["file_and_frontmatter"] = True
            ok_note("1.2", "Frontmatter has name and description")
        else:
            missing = [k for k in ("name", "description") if k not in fm]
            fail("1.2", "critical", f"Frontmatter missing fields: {', '.join(missing)}")

    name = fm.get("name", "")
    desc = fm.get("description", "")
    disable_model = str(fm.get("disable-model-invocation", "")).lower() in {
        "true",
        "yes",
        "1",
    }

    name_ok = bool(name) and bool(NAME_RE.match(name)) and len(name) <= 64
    dir_ok = name == skill_dir.name
    if not name:
        fail("1.3", "critical", "name is empty")
    elif not NAME_RE.match(name) or len(name) > 64:
        fail(
            "1.3",
            "critical",
            "name must be lowercase letters/numbers/hyphens only, max 64 chars",
            name,
        )
    if name and not dir_ok:
        fail(
            "1.4",
            "critical",
            "name does not match directory name",
            f"name={name!r} dir={skill_dir.name!r}",
        )
    if name_ok and dir_ok:
        points["name_valid_and_matched"] = True

    if not desc.strip():
        fail("1.5", "critical", "description is empty")
    elif len(desc) > 1024:
        fail("1.5", "critical", "description exceeds 1024 characters", str(len(desc)))

    if desc.strip():
        if FIRST_SECOND_PERSON_RE.search(desc):
            fail(
                "1.6",
                "critical",
                "description uses first/second person; use third person",
                desc[:160],
            )
            voice_ok = False
        else:
            voice_ok = True

        has_when = bool(WHEN_TRIGGER_RE.search(desc) or WHEN_TRIGGER_ZH_RE.search(desc))
        has_what = bool(WHAT_SIGNAL_RE.search(desc) or WHAT_SIGNAL_ZH_RE.search(desc))
        if disable_model:
            # User-invoked: human-facing one-liner allowed; still prefer non-empty
            triggers_ok = True
            if not has_when and not has_what:
                fail(
                    "1.9",
                    "should_fix",
                    "user-invoked description is very thin; add a one-line human summary of purpose",
                    desc[:160],
                )
        else:
            if not has_when:
                fail(
                    "1.7",
                    "critical",
                    "model-invoked description lacks WHEN triggers (e.g. 'Use when...')",
                    desc[:160],
                )
            if not has_what:
                fail(
                    "1.7b",
                    "should_fix",
                    "description lacks a clear WHAT verb (generates/reviews/...)",
                    desc[:160],
                )
            triggers_ok = has_when
            if has_when and not has_what:
                # still count partial for basic score if when present and voice ok
                pass

        if voice_ok and (triggers_ok if not disable_model else True) and desc.strip() and len(desc) <= 1024:
            if disable_model or has_when:
                points["description_voice_and_triggers"] = voice_ok and (
                    disable_model or has_when
                )
                if not disable_model and voice_ok and has_when:
                    points["description_voice_and_triggers"] = True
            if disable_model and voice_ok and desc.strip() and len(desc) <= 1024:
                points["description_voice_and_triggers"] = True

    headings = heading_map(body)
    has_steps = bool(NUMBERED_STEP_RE.search(body))
    has_boxes = bool(CHECKBOX_RE.search(body))
    has_rules_heading = (
        has_heading_containing(headings, "rule")
        or has_heading_containing(headings, "checklist")
        or any(
            k in h for h in headings for k in ("规则", "清单", "步骤", "流程", "做法")
        )
    )
    if has_steps or has_boxes or has_rules_heading:
        points["body_actionable"] = True
        ok_note("1.8", "Body has numbered steps, checkboxes, and/or rules")
    else:
        fail(
            "1.8",
            "critical",
            "Body is not actionable: need numbered steps, checkboxes, or clear rules list",
        )

    has_verification = any(
        "verification" in h
        or "verify" == h
        or h.endswith(" verification")
        or any(k in h for k in ("出口", "验收", "验证", "校验"))
        for h in headings
    ) or bool(re.search(r"(?im)^##\s+verification\b", body))
    has_done = bool(COMPLETION_RE.search(body) or COMPLETION_ZH_RE.search(body))
    if has_verification or has_done:
        points["verification_or_done_when"] = True
    else:
        fail(
            "1.10",
            "should_fix",
            "No Verification section and no 'Done when' / completion criteria markers",
        )

    # Contract clarity signals
    contract["when_to_use"] = any(
        "when to use" in h
        or h == "when"
        or any(k in h for k in ("何时使用", "什么时候用", "使用场景", "适用场景"))
        for h in headings
    )
    contract["when_not"] = (
        any(
            "when not" in h
            or "not to use" in h
            or "exclusions" in h
            or "out of scope" in h
            or any(
                k in h
                for k in ("不要用", "何时不用", "不适用", "不用于", "超出范围", "范围外")
            )
            for h in headings
        )
        or bool(re.search(r"(?i)when not to use", body))
    )
    axes_ok, axes = detect_check_axes(body)
    contract["check_axes_named"] = axes_ok
    contract["verification_checkboxes"] = has_verification and has_boxes
    contract["rationalizations_or_red_flags"] = any(
        "rationalization" in h
        or "red flag" in h
        or any(k in h for k in ("借口", "红旗", "危险信号", "常见误区"))
        for h in headings
    )

    if not contract["when_to_use"]:
        message = "Missing 'When to Use' (or equivalent) heading"
        if disable_model:
            message += " — user-invoked skills still need a human-readable usage section"
        fail("3.2", "should_fix", message)
    if not contract["when_not"]:
        fail("3.3", "should_fix", "Missing 'When NOT to use' / exclusions")
    review_like = bool(
        re.search(
            r"(?i)\b(code review|design review|design QA|视觉|设计稿|"
            r"audit (the|a|for)|inspect(s|ing)? (the|a)|评审|验收检查)\b",
            desc + "\n" + "\n".join(list(headings)[:20]),
        )
    ) or bool(
        re.search(r"(?i)\b(color|构图|composition|文案|typography)\b", body[:3000])
    )
    if not axes_ok:
        fail(
            "3.10",
            "critical" if review_like else "should_fix",
            "Check axes not clearly named (e.g. color / composition / copy). "
            "Review/audit skills must list what is in scope under a "
            "'Check axes' (or 检查轴) heading.",
            f"detected_axes={axes}",
        )
    else:
        ok_note("3.10", f"Named check axes: {', '.join(axes)}")

    if not contract["verification_checkboxes"]:
        fail(
            "3.5",
            "should_fix",
            "Verification section with checkbox evidence list not detected",
        )
    if not contract["rationalizations_or_red_flags"] and has_steps:
        fail(
            "3.6",
            "should_fix",
            "Workflow skill missing Common Rationalizations and/or Red Flags",
        )

    # Extra deterministic prune signals
    if line_count > 500:
        fail("4.1", "should_fix", f"SKILL.md has {line_count} lines (>500)")
    if TIME_SENSITIVE_RE.search(body):
        fail("4.4", "should_fix", "Possible time-sensitive 'before <date>' guidance")
    if WINDOWS_PATH_RE.search(body):
        fail("4.6", "nice", "Windows-style paths detected; prefer forward slashes")
    noop_hits = NOOP_RE.findall(body)
    if noop_hits:
        fail(
            "2.6",
            "should_fix",
            "Possible no-op phrasing detected",
            ", ".join(sorted(set(noop_hits)))[:160],
        )
    neg_count = len(NEGATION_RE.findall(body))
    if neg_count >= 3:
        fail(
            "2.5",
            "should_fix",
            f"High negation density ({neg_count} don't/never/avoid hits); prefer positive targets",
        )

    estimated_tokens = (len(text.encode("utf-8")) + 3) // 4
    body_line_offset = len(text.splitlines()) - len(body.splitlines())
    efficiency, efficiency_findings = assess_efficiency(
        body, body_line_offset, estimated_tokens
    )
    findings.extend(efficiency_findings)

    support_kit, kit_findings = assess_support_kit(skill_dir, body, has_steps)
    findings.extend(kit_findings)

    basic = sum(1 for v in points.values() if v)
    contract_score = sum(1 for v in contract.values() if v)
    return finalize(
        skill_dir,
        fm,
        body,
        findings,
        points,
        contract,
        line_count,
        axes,
        basic,
        contract_score,
        disable_model,
        support_kit,
        text,
        package_health,
        efficiency,
    )


def evaluate_gate(
    points: dict,
    findings: list[dict],
    package_health: dict,
) -> tuple[str, list[dict], dict]:
    """Evaluate the blocking gate from named checks, never from a score."""
    required_checks = {
        check: {
            "status": "pass" if bool(points.get(check)) else "fail",
            "evidence": f"scores.basic_usable.points.{check}",
        }
        for check in REQUIRED_GATE_POINTS
    }
    reasons: list[dict] = []
    package_status = str(
        package_health.get("status") or "not_assessed"
    )
    package_assessable = package_health.get("assessable")
    package_invalid = (
        package_status == "invalid_skill_package"
        or package_assessable is False
    )
    if package_invalid:
        reasons.append(
            {
                "code": "invalid_skill_package",
                "message": (
                    "Package health must be valid and assessable before the "
                    "deterministic gate can pass"
                ),
            }
        )
    elif package_status != "valid_skill_package" or package_assessable is not True:
        reasons.append(
            {
                "code": "package_not_assessed",
                "message": (
                    "Package health was not confirmed as a valid assessable "
                    "Skill package"
                ),
            }
        )

    for check, result in required_checks.items():
        if result["status"] == "fail":
            reasons.append(
                {
                    "code": "required_check_failed",
                    "check": check,
                    "message": f"Required gate check failed: {check}",
                }
            )

    critical_ids = sorted(
        {
            str(finding.get("id") or "unknown")
            for finding in findings
            if finding.get("severity") == "critical"
        }
    )
    if critical_ids:
        reasons.append(
            {
                "code": "critical_findings",
                "finding_ids": critical_ids,
                "message": "Deterministic Critical findings must be resolved",
            }
        )

    verdict = (
        "invalid_skill_package"
        if package_invalid
        else "pass"
        if not reasons
        else "fail"
    )
    policy = {
        "id": GATE_POLICY_ID,
        "required_checks": required_checks,
        "critical_findings_block": True,
        "package_health_required": True,
        "scoring_effect": "none",
    }
    return verdict, reasons, policy


def finalize(
    skill_dir: Path,
    fm: dict | None,
    body: str,
    findings: list[dict],
    points: dict,
    contract: dict,
    line_count: int,
    axes: list[str] | None = None,
    basic: int | None = None,
    contract_score: int | None = None,
    disable_model: bool = False,
    support_kit: dict | None = None,
    source_text: str | None = None,
    package_health: dict | None = None,
    efficiency: dict | None = None,
) -> dict:
    if basic is None:
        basic = sum(1 for v in points.values() if v)
    if contract_score is None:
        contract_score = sum(1 for v in contract.values() if v)
    if support_kit is None:
        support_kit = {
            "score": 0,
            "max": 0,
            "modules": {},
            "kit_complete": False,
        }
    if package_health is None:
        package_health = {
            "status": "not_assessed",
            "assessable": False,
            "checks": {},
            "installability": {
                "status": "not_assessed",
                "static_only": True,
                "blocking_checks": [],
            },
            "summary": {
                "blocking_check_count": 0,
                "warning_check_count": 0,
                "files_scanned": 0,
            },
        }
    critical = [f for f in findings if f["severity"] == "critical"]
    should = [f for f in findings if f["severity"] == "should_fix"]
    nice = [f for f in findings if f["severity"] == "nice"]
    gate_verdict, gate_reasons, gate_policy = evaluate_gate(
        points,
        findings,
        package_health,
    )
    legacy_ship_floor = gate_verdict == "pass"
    estimated_tokens = (
        (len(source_text.encode("utf-8")) + 3) // 4
        if source_text is not None
        else None
    )
    if efficiency is None:
        efficiency = {
            "loop_guard": {
                "label": "循环护栏",
                "status": "not_assessed",
                "loop_directive_count": 0,
                "guarded_count": 0,
                "unguarded_lines": [],
                "unbounded_phrase_lines": [],
                "scope": "SKILL.md static instruction text",
                "method": "line-window scan for loop directives, stop signals, and unbounded phrasing",
                "evidence": None,
            },
            "token_budget": {
                "max_recommended_input_tokens": TOKEN_BUDGET_INPUT_TOKENS,
                "status": "not_assessed",
            },
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_level": "static_contract_check",
        "skill_dir": str(skill_dir),
        "skill_md": str(skill_dir / "SKILL.md"),
        "target_platform": "generic",
        "frontmatter": fm or {},
        "disable_model_invocation": disable_model,
        "line_count": line_count,
        "gate_verdict": gate_verdict,
        "gate_reasons": gate_reasons,
        "gate_policy": gate_policy,
        "scores": {
            "scoring_effect": "informational_only",
            "basic_usable": {"score": basic, "max": 5, "points": points},
            "contract_clarity": {
                "score": contract_score,
                "max": 5,
                "points": contract,
                "detected_axes": axes or [],
            },
            "support_kit": support_kit,
            "ship_floor_met": legacy_ship_floor,
        },
        "deprecated_fields": {
            "scores.ship_floor_met": {
                "deprecated": True,
                "replacement": "gate_verdict",
                "compatibility": "true only when gate_verdict=pass",
                "planned_removal": "next major schema version",
            }
        },
        "counts": {
            "critical": len(critical),
            "should_fix": len(should),
            "nice": len(nice),
        },
        "operational_metrics": {
            "token_consumption": {
                "status": (
                    "estimated" if estimated_tokens is not None else "not_assessed"
                ),
                "estimated_input_tokens": estimated_tokens,
                "scope": "SKILL.md static instruction text",
                "method": "ceil(UTF-8 byte length / 4)",
                "confidence": "low",
                "evidence": "SKILL.md" if estimated_tokens is not None else None,
                "budget": efficiency["token_budget"],
            },
            "runtime_duration": {
                "status": "not_measured",
                "duration_ms": None,
                "scope": "audited Skill execution",
                "evidence": None,
            },
            "loop_guard": efficiency["loop_guard"],
        },
        "package_health": package_health,
        "findings": [f for f in findings if f["severity"] != "info"],
        "notes": [f for f in findings if f["severity"] == "info"],
        "limitations": [
            "scores are informational and do not affect gate_verdict or exit status",
            "behavioral correctness and safe execution require separate evidence",
        ],
        "optional_model_review": {
            "status": "not_run",
            "blocking": False,
            "passes": [
                "predictability_qualitative",
                "anatomy_qualitative",
                "prune_qualitative",
            ],
        },
        "llm_passes_remaining": [
            "predictability_qualitative",
            "anatomy_qualitative",
            "prune_qualitative",
        ],
    }


def force_utf8_streams() -> None:
    """Keep JSON readable when the console codepage is not UTF-8 (e.g. cp936)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def main() -> int:
    force_utf8_streams()
    parser = argparse.ArgumentParser(description="Hard-gate skill checker")
    parser.add_argument("skill_dir", type=Path, help="Path to skill directory")
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON"
    )
    args = parser.parse_args()
    if not args.skill_dir.exists():
        print(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "audit_level": "static_contract_check",
                    "target_platform": "generic",
                    "error": f"path not found: {args.skill_dir}",
                    "gate_verdict": "fail",
                    "gate_reasons": [
                        {
                            "code": "target_path_not_found",
                            "message": "Target path was not available for static checks",
                        }
                    ],
                    "gate_policy": {
                        "id": GATE_POLICY_ID,
                        "required_checks": {},
                        "critical_findings_block": True,
                        "package_health_required": True,
                        "scoring_effect": "none",
                    },
                    "scores": {
                        "scoring_effect": "informational_only",
                        "basic_usable": {"score": 0, "max": 5},
                        "contract_clarity": {"score": 0, "max": 5},
                        "support_kit": {
                            "score": 0,
                            "max": 0,
                            "modules": {},
                            "kit_complete": False,
                        },
                        "ship_floor_met": False,
                    },
                    "deprecated_fields": {
                        "scores.ship_floor_met": {
                            "deprecated": True,
                            "replacement": "gate_verdict",
                            "compatibility": "true only when gate_verdict=pass",
                            "planned_removal": "next major schema version",
                        }
                    },
                    "limitations": ["target path was not available for static checks"],
                }
            ),
            flush=True,
        )
        print("hard_gates: path not found", file=sys.stderr)
        return 1

    report = check_skill(args.skill_dir)
    dump = json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None)
    print(dump)
    print(
        f"hard_gates: gate={report['gate_verdict']} · "
        f"critical={report['counts']['critical']} · "
        f"should_fix={report['counts']['should_fix']}",
        file=sys.stderr,
    )
    return 0 if report["gate_verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
