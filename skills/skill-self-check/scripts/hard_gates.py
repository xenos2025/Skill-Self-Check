#!/usr/bin/env python3
"""Deterministic hard-gate checks and scores for an Agent Skill directory.

Usage:
  python hard_gates.py <skill-dir>

Stdout: JSON report
Stderr: human one-line summary
Exit: 0 if basic_usable >= 4 and no critical hard-gate fails; else 1
"""

from __future__ import annotations

import argparse
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
    r"when asked|when reviewing|when implementing|triggers?:|"
    r"run after|after you)\b"
)
# Chinese has no word boundaries, so these are matched without \b.
WHEN_TRIGGER_ZH_RE = re.compile(
    r"(用于|适用|适合|用来|当用户|当需要|需要.{0,6}时|使用场景|适用场景|触发条件)"
)
WHAT_SIGNAL_RE = re.compile(
    r"(?i)\b(generates?|reviews?|extracts?|analyzes?|guides?|checks?|"
    r"validates?|writes?|creates?|processes?|helps agents?|audits?)\b"
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
NOOP_RE = re.compile(
    r"(?i)\b(be careful|think step by step|write good code|always be thorough)\b"
)
NEGATION_RE = re.compile(r"(?i)\b(don't|do not|never|avoid)\b")
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
    r"\.py\b|\.ps1\b|\.sh\b|automation|codeact|calendar script|"
    r"python\s+\S+\.py)"
)
EXAMPLE_HEADING_RE = re.compile(
    r"(?im)^(#{1,6})\s+.*(example|examples|案例|示例|样例|worked example)\s*$"
)


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

    Ship floor is unaffected — failures are should_fix only.
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
        short = re.split(r"\s*[—–:\-|]\s*", item, maxsplit=1)[0].strip()
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
        )

    text, fallback_encoding = read_skill_text(skill_md)
    fm, body, has_fm = parse_frontmatter(text)
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)

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

    if not contract["when_to_use"] and not disable_model:
        fail("3.2", "should_fix", "Missing 'When to Use' (or equivalent) heading")
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
    )


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
    critical = [f for f in findings if f["severity"] == "critical"]
    should = [f for f in findings if f["severity"] == "should_fix"]
    nice = [f for f in findings if f["severity"] == "nice"]
    ship_floor = basic >= 4 and len(critical) == 0
    return {
        "skill_dir": str(skill_dir),
        "skill_md": str(skill_dir / "SKILL.md"),
        "frontmatter": fm or {},
        "disable_model_invocation": disable_model,
        "line_count": line_count,
        "scores": {
            "basic_usable": {"score": basic, "max": 5, "points": points},
            "contract_clarity": {
                "score": contract_score,
                "max": 5,
                "points": contract,
                "detected_axes": axes or [],
            },
            "support_kit": support_kit,
            "ship_floor_met": ship_floor,
        },
        "counts": {
            "critical": len(critical),
            "should_fix": len(should),
            "nice": len(nice),
        },
        "findings": [f for f in findings if f["severity"] != "info"],
        "notes": [f for f in findings if f["severity"] == "info"],
        "llm_passes_remaining": ["predictability_qualitative", "anatomy_qualitative", "prune_qualitative"],
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
                    "error": f"path not found: {args.skill_dir}",
                    "scores": {
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
                }
            ),
            flush=True,
        )
        print("hard_gates: path not found", file=sys.stderr)
        return 1

    report = check_skill(args.skill_dir)
    dump = json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None)
    print(dump)
    scores = report["scores"]
    kit = scores.get("support_kit") or {}
    kit_max = kit.get("max", 0)
    kit_score = kit.get("score", 0)
    kit_txt = (
        f"support_kit {kit_score}/{kit_max}"
        if kit_max
        else "support_kit n/a"
    )
    print(
        f"hard_gates: basic_usable {scores['basic_usable']['score']}/5 · "
        f"contract_clarity {scores['contract_clarity']['score']}/5 · "
        f"{kit_txt} · "
        f"ship_floor={'yes' if scores['ship_floor_met'] else 'no'} · "
        f"critical={report['counts']['critical']}",
        file=sys.stderr,
    )
    return 0 if scores["ship_floor_met"] else 1


if __name__ == "__main__":
    sys.exit(main())
