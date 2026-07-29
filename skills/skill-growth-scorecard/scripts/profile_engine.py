#!/usr/bin/env python3
"""Compose readiness and Skill audit JSON into a deterministic growth profile.

The generator is intentionally stateless and stdlib-only. It never executes the
audited Skill. HTML is rendered from a local template with the same JSON fact set.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROFILE_SCHEMA_VERSION = "0.6"
RULESET_VERSION = "0.6"
LEVELS = [
    ("Lv0", "灵感草稿"),
    ("Lv1", "初学者 · 起步创作者"),
    ("Lv2", "入门应用 · 实用搭建者"),
    ("Lv3", "中级应用 · 稳定实践者"),
    ("Lv4", "高级审计 · 闭环作者"),
    ("Lv5", "高级审计 · 作者多平台"),
]

ARCHETYPES = [
    {
        "id": "flow-navigator",
        "label": "流程探路者",
        "dimensions": ("intent_contract", "workflow_execution"),
        "summary": "擅长把目标铺成一条完整路线。",
        "growth": "继续把每个承诺连到验收清单和出错时的停手规则。",
    },
    {
        "id": "steady-builder",
        "label": "稳健搭建者",
        "dimensions": ("intent_contract", "tooling_support"),
        "summary": "结构清楚，重视说明和配套材料。",
        "growth": "用一次真实业务试跑检验说明书，缺什么就补什么。",
    },
    {
        "id": "automation-craftsperson",
        "label": "自动化工匠",
        "dimensions": ("workflow_execution", "tooling_support"),
        "summary": "善于把任务做成脚本和可执行工具。",
        "growth": "补强默认关闭和失败停手；别让脚本绕过人工确认。",
    },
    {
        "id": "loop-coach",
        "label": "闭环教练",
        "dimensions": ("verification_learning", "intent_contract"),
        "summary": "重视检查、复盘和持续改进。",
        "growth": "保持验收清楚，同时控制流程不要过长。",
    },
    {
        "id": "safety-guardian",
        "label": "安全守门员",
        "dimensions": ("safety_control", "verification_learning"),
        "summary": "重视权限、确认、证据和风险控制。",
        "growth": "让安全闸门清楚但不过度增加使用成本。",
    },
    {
        "id": "platform-architect",
        "label": "规则适配者",
        "dimensions": ("portability_adaptation", "intent_contract"),
        "summary": "擅长用稳定契约降低换工具时的返工。",
        "growth": "先把业务契约写稳；多平台验证留给高级审计。",
    },
]

DIMENSION_LABELS = {
    "intent_contract": "目标与边界",
    "workflow_execution": "流程与执行",
    "tooling_support": "工具与材料",
    "verification_learning": "验证与复盘",
    "safety_control": "安全与控制",
    "portability_adaptation": "通用与适配",
}

PERSONAL_HEADLINES = {
    "pending": "你正在把经验整理成第一个可检查的 Skill",
    "flow-navigator": "你能把模糊任务梳理成一条可执行路线",
    "steady-builder": "你擅长先把结构搭稳，再让别人照着使用",
    "automation-craftsperson": "你擅长把复杂任务做成可执行工具",
    "loop-coach": "你擅长用检查和复盘让 Skill 越用越稳",
    "safety-guardian": "你会先把权限和风险关进清楚的规则里",
    "platform-architect": "你擅长用稳定规则降低换工具时的返工",
    "balanced": "你已经能把目标、执行、材料、验收和安全连成闭环",
}

PERSONAL_STRENGTHS = {
    "pending": "你已经开始把口头经验转成可复用的工作方法。",
    "flow-navigator": (
        "从这份 Skill 的流程设计看，你已经表现出把目标拆成步骤、"
        "顺序和完成路径的能力。"
    ),
    "steady-builder": (
        "从这份 Skill 的结构和配套材料看，你已经表现出先整理说明、"
        "再搭建执行框架的能力。"
    ),
    "automation-craftsperson": (
        "从这份 Skill 的结构和配套材料看，你已经具备把业务任务拆成步骤、"
        "脚本和执行路径的基础能力。"
    ),
    "loop-coach": (
        "从这份 Skill 的检查与复盘设计看，你已经表现出用证据推动持续改进的能力。"
    ),
    "safety-guardian": (
        "从这份 Skill 的权限与风险设计看，你已经表现出在执行前设置边界和确认机制的能力。"
    ),
    "platform-architect": (
        "从这份 Skill 的契约设计看，你已经表现出用稳定规则降低换工具返工的能力。"
    ),
    "balanced": (
        "从这份 Skill 的完整证据链看，你已经能把目标、执行、工具、"
        "验收和安全连成闭环。"
    ),
}

LEVEL_INTERPRETATIONS = {
    0: "目前还在草稿阶段，重点是先让目标、边界和完成标准可被检查。",
    1: "目前仍处于起步阶段。",
    2: "目前已进入入门应用阶段，静态结构已经达到企业受控试用的基础线。",
    3: "目前已进入中级应用阶段；作者进阶证据开始齐全（高级审计轨道）。",
    4: "目前已进入高级审计阶段，执行、安全和失败恢复证据更完整。",
    5: "目前已进入作者多平台阶段；这是高级审计轨道，不是企业默认合格线。",
}

LEVEL_LEARNING_QUESTS = {
    0: {
        "title": "练习把一个口头任务写成可检查的 Skill",
        "action": "从一个每周都会重复的小任务开始，不追求复杂功能，先练习把工作说清楚。",
        "practice_points": [
            {
                "label": "量化目标",
                "text": "写清输入、预期输出、成功标准和停止条件。",
            },
            {
                "label": "情况判断",
                "text": "至少区分可以继续、资料不足和必须请人决定三种情况。",
            },
            {
                "label": "完成标准",
                "text": "让另一位同事只看说明就能判断任务是否完成。",
            },
        ],
        "acceptance": "完成一个不依赖口头补充也能被他人复述和检查的小型 Skill 草稿。",
    },
    1: {
        "title": "练习把 Skill 写成同事也能照着做的业务说明书",
        "action": "选取当前 Skill 中最小的一条流程，用真实业务语言完成以下四项练习。",
        "practice_points": [
            {
                "label": "量化目标",
                "text": "补齐输入、输出、成功标准、停止条件和升级找谁。",
            },
            {
                "label": "判断流程",
                "text": "分别写清正常、资料不足、无权限和做砸了时该怎么停。",
            },
            {
                "label": "可复用材料",
                "text": "把重复说明、表格或模板放到资料/案例里，正文只留步骤。",
            },
            {
                "label": "业务试跑",
                "text": "用一条脱敏或过期业务样例走完流程，对照验收清单勾选，不触发真实对外发送。",
            },
        ],
        "acceptance": "样例试跑后，验收清单可勾选；缺口已写回说明书。",
    },
    2: {
        "title": "练习用一次真实场景证明能交给人用",
        "action": "选一个本周会发生的真实场景，按说明书走完并人工勾验收。",
        "practice_points": [
            {
                "label": "真实场景",
                "text": "用业务原话写下触发条件，而不是空泛口号。",
            },
            {
                "label": "验收凭据",
                "text": "写清看什么算做对：表格字段、截图、数字或单据状态。",
            },
            {
                "label": "何时不用",
                "text": "写清必须人拍板的事（报价、放行、拒单等）。",
            },
            {
                "label": "失败停手",
                "text": "写清最多试几次、超时或转给谁；禁止开放式打磨。",
            },
        ],
        "acceptance": "一次真实试跑后，验收可勾选，或缺口已改回 SKILL.md。",
    },
    3: {
        "title": "练习让业务 Skill 在越界时停得住",
        "action": "围绕最接近真实风险的一条流程，写清权限、确认和失败停手。",
        "practice_points": [
            {
                "label": "权限边界",
                "text": "写清允许、禁止、必须人工确认的动作。",
            },
            {
                "label": "默认关闭",
                "text": "真实发送或写入默认关闭；先预演再人工确认。",
            },
            {
                "label": "重试上限",
                "text": "失败最多重试几次，到头交给谁，不要原样空转。",
            },
            {
                "label": "异常输入",
                "text": "缺字段、空表、权限不够时要停下并说明原因。",
            },
        ],
        "acceptance": "无授权、重复执行和中途失败都能安全停下，且没有真实副作用。",
    },
    4: {
        "title": "练习把业务说法写稳，少绑死某一个工具",
        "action": "保持同一套业务输入输出不变，把工具差异收成可替换说明。",
        "practice_points": [
            {
                "label": "稳定契约",
                "text": "固定输入、输出、错误状态和验收规则。",
            },
            {
                "label": "工具可替换",
                "text": "步骤写做什么，具体软件名放到资料里备选。",
            },
            {
                "label": "同事可读",
                "text": "让没写过这份 Skill 的同事只看说明书也能判断对错。",
            },
            {
                "label": "改完复检",
                "text": "改完后重新跑结构检查，确认没有改坏基础门槛。",
            },
        ],
        "acceptance": "说明书不依赖单一聊天工具口头习惯，验收仍可独立判断。",
    },
    5: {
        "title": "练习把这份 Skill 交给团队长期用",
        "action": "把关注点从单次跑通提升到同事下周还能用。",
        "practice_points": [
            {
                "label": "回归样例",
                "text": "固定一两个脱敏样例，改版后重新勾验收。",
            },
            {
                "label": "版本说明",
                "text": "记录改了哪条规则、为什么改、谁批准。",
            },
            {
                "label": "使用反馈",
                "text": "收集失败率和需要人工接管的原因，回写说明书。",
            },
            {
                "label": "经验传递",
                "text": "把常见借口和危险信号写成团队能复用的表。",
            },
        ],
        "acceptance": "下一版仍过基础门槛，且能向同事解释关键规则为什么这样写。",
    },
}

# Author / maintainer track — not the enterprise default next step.
ADVANCED_AUDIT_QUESTS = {
    2: {
        "title": "（高级审计）补核心流程行为证据",
        "action": "用脱敏夹具验证核心路径，并保存 PDCA 复盘到行为证据 JSON。",
        "acceptance": "core_flow_tested 和 pdca_evidence 均为 true。",
        "unlocks": {"id": "Lv3", "label": LEVELS[3][1]},
    },
    3: {
        "title": "（高级审计）证明适用的安全边界和失败恢复",
        "action": (
            "有外部动作时验证默认关闭和写回一致性；只读 Skill 则验证不越权写入，"
            "并补齐中断与异常输入的恢复证据。"
        ),
        "acceptance": "适用项有行为证据，不适用项有明确范围，失败场景可以安全停止或恢复。",
        "unlocks": {"id": "Lv4", "label": LEVELS[4][1]},
    },
    4: {
        "title": "（高级审计）完成跨平台可比验证",
        "action": (
            "使用同一份契约和同一套脱敏夹具在至少两个 Agent 平台运行，"
            "分别保存结果证据。"
        ),
        "acceptance": (
            "两个平台记录均为 verified，且 contract_id 与 fixture_id "
            "是相同的 SHA-256 指纹。"
        ),
        "unlocks": {"id": "Lv5", "label": LEVELS[5][1]},
    },
    5: {
        "title": "（高级审计）保持长期运行与多平台证据",
        "action": "记录真实规模、回归和版本变化；平台适配变更不污染业务契约。",
        "acceptance": "下一版本仍通过高级审计门槛。",
        "unlocks": {"id": "Lv5", "label": LEVELS[5][1]},
    },
}


def force_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def load_json(path: Path | None, label: str) -> dict[str, Any] | None:
    if path is None:
        return None
    if not path.is_file():
        raise ValueError(f"{label} file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} top-level JSON must be an object")
    return payload


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def bool_value(data: dict[str, Any] | None, key: str) -> bool:
    return bool(data and data.get(key) is True)


def score_state(score: int, maximum: int) -> int:
    if maximum <= 0 or score <= 0:
        return 0
    ratio = score / maximum
    if ratio < 0.6:
        return 1
    return 2


def sanitize_evidence(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", text) or text.startswith("/"):
        parts = [part for part in text.split("/") if part]
        return "/".join(parts[-3:])
    return text


def clean_subject_name(value: Any) -> str:
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", str(value or ""))
    return re.sub(r"\s+", " ", text).strip()[:120]


def identify_subject(
    readiness_report: dict[str, Any] | None,
    hard_report: dict[str, Any] | None,
    safety_report: dict[str, Any] | None,
    explicit_name: str | None,
) -> dict[str, str]:
    name = clean_subject_name(explicit_name)
    if name:
        kind = "skill" if hard_report or safety_report else "work_process"
        return {
            "kind": kind,
            "label": "Skill" if kind == "skill" else "业务流程",
            "name": name,
            "source": "argument",
        }

    if hard_report:
        frontmatter = (
            hard_report.get("frontmatter")
            if isinstance(hard_report.get("frontmatter"), dict)
            else {}
        )
        name = clean_subject_name(frontmatter.get("name"))
        if name:
            return {
                "kind": "skill",
                "label": "Skill",
                "name": name,
                "source": "hard_gates.frontmatter.name",
            }

    if safety_report:
        target = str(safety_report.get("target") or "").replace("\\", "/").rstrip("/")
        name = clean_subject_name(target.rsplit("/", 1)[-1] if target else "")
        if name:
            return {
                "kind": "skill",
                "label": "Skill",
                "name": name,
                "source": "ship_safety.target_basename",
            }

    if readiness_report:
        report_input = (
            readiness_report.get("input")
            if isinstance(readiness_report.get("input"), dict)
            else {}
        )
        name = clean_subject_name(report_input.get("process_name"))
        if name:
            return {
                "kind": "work_process",
                "label": "业务流程",
                "name": name,
                "source": "readiness.input.process_name",
            }

    return {
        "kind": "unknown",
        "label": "分析对象",
        "name": "未命名分析对象",
        "source": "not_supplied",
    }


def clean_findings(
    findings: Any,
    lane: str,
    default_source: str,
) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for index, finding in enumerate(findings if isinstance(findings, list) else []):
        if not isinstance(finding, dict):
            continue
        cleaned.append(
            {
                "id": str(finding.get("id") or f"{default_source}.{index + 1}"),
                "severity": str(finding.get("severity") or "info"),
                "message": str(finding.get("message") or "未命名问题"),
                "evidence": sanitize_evidence(finding.get("evidence")),
                "source": default_source,
                "lane": lane,
                "scope": str(finding.get("scope") or "audited input"),
                "confidence": str(finding.get("confidence") or "not_recorded"),
                "verification_status": str(
                    finding.get("verification_status") or "not_recorded"
                ),
            }
        )
    return cleaned


def plain_finding_action(finding: dict[str, Any]) -> str:
    """Translate a blocking technical finding into one beginner-facing action."""
    finding_id = str(finding.get("id") or "")
    if finding_id == "CMD.1":
        return "说明书引用了一个找不到的脚本。请补齐脚本，或把说明书里的文件位置改正确。"
    if finding_id == "CMD.2":
        return "说明书承诺了某个命令功能，但对应脚本里还没有实现。请补上功能，或删除这条承诺。"
    if finding_id == "EXT.1":
        return "有脚本可以访问外部网络或账号，但缺少“默认不执行”的保护。请先加入预演模式和人工确认。"
    if finding_id == "EXT.3":
        return "发现可执行的自动化脚本。请人工确认它不会在未授权时发送、写入或修改外部数据。"
    message = str(finding.get("message") or "").strip()
    return message or "修复当前最高优先级问题，并重新运行检查。"


def join_chinese(items: list[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return "、".join(items[:-1]) + "和" + items[-1]


def build_personal_interpretation(
    archetype: dict[str, Any],
    level_ordinal: int,
    dimensions: dict[str, int],
    findings: list[dict[str, Any]],
) -> dict[str, str]:
    """Build a concrete personal capability reading from scored evidence."""
    archetype_id = str(archetype.get("id") or "pending")
    topics: list[str] = []
    if dimensions.get("intent_contract", 0) < 2:
        topics.append("使用边界")
    if any(
        str(finding.get("id") or "") in {"CMD.1", "CMD.2"}
        for finding in findings
    ):
        topics.append("实现一致性")
    if dimensions.get("safety_control", 0) < 2:
        topics.append("安全验证")
    if dimensions.get("workflow_execution", 0) < 2:
        topics.append("流程完整性")
    if dimensions.get("tooling_support", 0) < 2:
        topics.append("工具与配套材料")
    if dimensions.get("verification_learning", 0) < 2:
        topics.append("测试与复盘")
    if dimensions.get("portability_adaptation", 0) < 2:
        topics.append("跨平台适配")
    topics = list(dict.fromkeys(topics))[:3]

    growth = (
        f"当前最值得补强的是{join_chinese(topics)}。"
        if topics
        else "下一步应继续积累真实使用、长期运行和版本变化证据。"
    )
    return {
        "eyebrow": "你的能力画像",
        "headline": PERSONAL_HEADLINES.get(
            archetype_id,
            "你正在形成自己的 Skill 创作方法",
        ),
        "summary": (
            PERSONAL_STRENGTHS.get(
                archetype_id,
                "这份 Skill 已经表现出可继续发展的创作能力。",
            )
            + LEVEL_INTERPRETATIONS.get(level_ordinal, "")
            + growth
        ),
    }


def build_learning_quest(
    archetype: dict[str, Any],
    level_ordinal: int,
    dimensions: dict[str, int],
) -> dict[str, Any]:
    """Build one personal practice quest without leaking project remediation."""
    template = LEVEL_LEARNING_QUESTS.get(
        level_ordinal,
        LEVEL_LEARNING_QUESTS[0],
    )
    title = str(template["title"])
    practice_points = [
        {"label": str(item["label"]), "text": str(item["text"])}
        for item in template["practice_points"]
    ]
    if str(archetype.get("id") or "") == "automation-craftsperson" and level_ordinal == 1:
        title = "练习把自动化脚本做成同事能放心点的业务工具"
        practice_points[2] = {
            "label": "可复用脚本",
            "text": "把重复逻辑整理成可传入参数、可返回状态、失败时给出明确原因的公共命令。",
        }
        practice_points[3] = {
            "label": "业务试跑",
            "text": "用一条脱敏样例跑通脚本，对照验收勾选；默认关闭真实发送或写入。",
        }

    weakest = sorted(
        dimensions,
        key=lambda key: (dimensions[key], list(DIMENSION_LABELS).index(key)),
    )[:3]
    return {
        "lane": "personal_capability",
        "stage": LEVELS[level_ordinal][1],
        "title": title,
        "action": str(template["action"]),
        "practice_points": practice_points,
        "acceptance": str(template["acceptance"]),
        "evidence_dimensions": weakest,
    }


def normalize_readiness(report: dict[str, Any] | None) -> dict[str, Any]:
    if not report:
        return {
            "status": "not_assessed",
            "level": None,
            "gates": [],
            "badges": [],
            "next_quest": None,
            "findings": [],
            "limitations": ["business readiness report was not supplied"],
        }
    level = report.get("level") if isinstance(report.get("level"), dict) else {}
    return {
        "status": "assessed",
        "level": {
            "id": str(level.get("id") or "B0"),
            "label": str(level.get("label") or "口头经验"),
            "ordinal": int_value(level.get("ordinal")),
            "max_ordinal": int_value(level.get("max_ordinal"), 6),
        },
        "process_name": str(
            (report.get("input") or {}).get("process_name")
            if isinstance(report.get("input"), dict)
            else ""
        ),
        "gates": report.get("gates") if isinstance(report.get("gates"), list) else [],
        "badges": report.get("badges") if isinstance(report.get("badges"), list) else [],
        "next_quest": report.get("next_quest"),
        "findings": clean_findings(
            report.get("findings"), "business_readiness", "readiness_gates"
        ),
        "limitations": report.get("limitations")
        if isinstance(report.get("limitations"), list)
        else [],
    }


def valid_evidence_reference(value: Any) -> bool:
    """Accept shareable references while rejecting workstation-local paths."""
    reference = str(value or "").strip()
    if not reference:
        return False
    lowered = reference.casefold()
    if lowered.startswith("file://") or reference.startswith(("/", "\\", "~")):
        return False
    if re.match(r"^[a-zA-Z]:[\\/]", reference):
        return False
    path_part = reference.split("#", 1)[0].replace("\\", "/")
    if ".." in path_part.split("/"):
        return False
    return True


def nonnegative_number(value: Any) -> int | float | None:
    """Return a finite non-negative number without treating booleans as usage."""
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number < 0:
        return None
    return int(number) if number.is_integer() else number


def positive_run_count(value: Any) -> int | None:
    number = nonnegative_number(value)
    if number is None or int(number) != number or number < 1:
        return None
    return int(number)


def nonnegative_integer(value: Any) -> int | None:
    number = nonnegative_number(value)
    if number is None or int(number) != number:
        return None
    return int(number)


def operational_metrics(
    hard: dict[str, Any] | None,
    behavior: dict[str, Any] | None,
) -> dict[str, Any]:
    """Prefer trusted observations, otherwise preserve explicit static limits."""
    hard_metrics = (
        hard.get("operational_metrics")
        if hard and isinstance(hard.get("operational_metrics"), dict)
        else {}
    )
    behavior_metrics = (
        behavior.get("operational_metrics")
        if behavior and isinstance(behavior.get("operational_metrics"), dict)
        else {}
    )
    observed_tokens = (
        behavior_metrics.get("token_consumption")
        if isinstance(behavior_metrics.get("token_consumption"), dict)
        else {}
    )
    token_evidence = str(observed_tokens.get("evidence") or "").strip()
    token_runs = positive_run_count(observed_tokens.get("runs"))
    input_tokens = nonnegative_integer(observed_tokens.get("input_tokens"))
    output_tokens = nonnegative_integer(observed_tokens.get("output_tokens"))
    total_tokens = nonnegative_integer(observed_tokens.get("total_tokens"))
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    token_components_consistent = not (
        total_tokens is not None
        and input_tokens is not None
        and output_tokens is not None
        and total_tokens != input_tokens + output_tokens
    )
    token_observation_valid = (
        str(observed_tokens.get("status") or "").casefold() == "observed"
        and total_tokens is not None
        and token_components_consistent
        and token_runs is not None
        and valid_evidence_reference(token_evidence)
    )
    if token_observation_valid:
        token_metric = {
            "label": "Token 消耗",
            "status": "observed",
            "total_tokens": total_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "runs": token_runs,
            "unit": "tokens",
            "scope": "audited Skill behavior runs",
            "method": "trusted provider or harness usage metadata",
            "confidence": "observed",
            "evidence": token_evidence,
            "source": "behavior",
        }
    else:
        static_tokens = (
            hard_metrics.get("token_consumption")
            if isinstance(hard_metrics.get("token_consumption"), dict)
            else {}
        )
        estimated_tokens = nonnegative_integer(
            static_tokens.get("estimated_input_tokens")
        )
        static_available = (
            str(static_tokens.get("status") or "").casefold() == "estimated"
            and estimated_tokens is not None
        )
        token_metric = {
            "label": "Token 消耗",
            "status": "estimated" if static_available else "not_assessed",
            "estimated_input_tokens": (
                estimated_tokens if static_available else None
            ),
            "unit": "tokens",
            "scope": (
                str(static_tokens.get("scope") or "SKILL.md static instruction text")
                if static_available
                else "audited Skill execution"
            ),
            "method": (
                str(static_tokens.get("method") or "static estimate")
                if static_available
                else None
            ),
            "confidence": (
                str(static_tokens.get("confidence") or "low")
                if static_available
                else "not_assessed"
            ),
            "evidence": (
                sanitize_evidence(static_tokens.get("evidence"))
                if static_available
                else None
            ),
            "source": "hard_gates" if static_available else "not_supplied",
            "observation_rejected": bool(observed_tokens)
            and not token_observation_valid,
        }

    observed_runtime = (
        behavior_metrics.get("runtime_duration")
        if isinstance(behavior_metrics.get("runtime_duration"), dict)
        else {}
    )
    runtime_evidence = str(observed_runtime.get("evidence") or "").strip()
    runtime_runs = positive_run_count(observed_runtime.get("runs"))
    duration_ms = nonnegative_number(observed_runtime.get("duration_ms"))
    runtime_observation_valid = (
        str(observed_runtime.get("status") or "").casefold() == "observed"
        and duration_ms is not None
        and runtime_runs is not None
        and valid_evidence_reference(runtime_evidence)
    )
    runtime_metric = {
        "label": "运行时长",
        "status": "observed" if runtime_observation_valid else "not_measured",
        "duration_ms": duration_ms if runtime_observation_valid else None,
        "runs": runtime_runs if runtime_observation_valid else None,
        "unit": "ms",
        "statistic": (
            str(observed_runtime.get("statistic") or "single_run")
            if runtime_observation_valid
            else None
        ),
        "scope": (
            "audited Skill behavior runs"
            if runtime_observation_valid
            else "audited Skill execution"
        ),
        "evidence": runtime_evidence if runtime_observation_valid else None,
        "source": "behavior" if runtime_observation_valid else "not_supplied",
        "observation_rejected": bool(observed_runtime)
        and not runtime_observation_valid,
    }
    return {
        "token_consumption": token_metric,
        "runtime_duration": runtime_metric,
        "scoring_effect": "informational_only",
    }


def behavior_applicability(
    behavior: dict[str, Any] | None,
    key: str,
) -> dict[str, Any]:
    applicability = behavior.get("applicability") if behavior else None
    record = (
        applicability.get(key)
        if isinstance(applicability, dict)
        and isinstance(applicability.get(key), dict)
        else {}
    )
    requested_status = str(record.get("status") or "applicable").casefold()
    status = (
        "not_applicable"
        if requested_status == "not_applicable"
        else "applicable"
    )
    evidence = str(record.get("evidence") or "").strip()
    return {
        "status": status,
        "evidence": evidence,
        "evidence_valid": valid_evidence_reference(evidence),
    }


def verified_platform_summary(
    behavior: dict[str, Any] | None,
) -> dict[str, Any]:
    platforms = behavior.get("platforms") if behavior else None
    if not isinstance(platforms, list):
        platforms = []
    content_id_pattern = re.compile(r"^sha256:[0-9a-f]{64}$")
    groups: dict[tuple[str, str], dict[str, dict[str, str]]] = {}
    eligible_records = 0
    for item in platforms:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        evidence = str(item.get("evidence") or "").strip()
        contract_id = str(item.get("contract_id") or "").strip().casefold()
        fixture_id = str(item.get("fixture_id") or "").strip().casefold()
        if (
            str(item.get("status") or "").casefold() != "verified"
            or not name
            or not valid_evidence_reference(evidence)
            or not content_id_pattern.fullmatch(contract_id)
            or not content_id_pattern.fullmatch(fixture_id)
        ):
            continue
        eligible_records += 1
        key = (contract_id, fixture_id)
        groups.setdefault(key, {})[name.casefold()] = {
            "name": name,
            "evidence": evidence,
        }

    if not groups:
        return {
            "verified_platform_count": 0,
            "eligible_record_count": eligible_records,
            "contract_id": None,
            "fixture_id": None,
            "platforms": [],
        }
    (contract_id, fixture_id), selected = max(
        groups.items(),
        key=lambda item: (
            len(item[1]),
            item[0][0],
            item[0][1],
        ),
    )
    records = sorted(selected.values(), key=lambda item: item["name"].casefold())
    return {
        "verified_platform_count": len(records),
        "eligible_record_count": eligible_records,
        "contract_id": contract_id,
        "fixture_id": fixture_id,
        "platforms": records,
    }


def behavior_platform_count(behavior: dict[str, Any] | None) -> int:
    return int(verified_platform_summary(behavior)["verified_platform_count"])


def resolve_hard_gate(
    hard: dict[str, Any],
    scores: dict[str, Any],
) -> dict[str, Any]:
    """Prefer the explicit gate contract and fall back to legacy reports."""
    explicit = str(hard.get("gate_verdict") or "").strip().casefold()
    if explicit in {"pass", "fail", "invalid_skill_package"}:
        reasons = (
            hard.get("gate_reasons")
            if isinstance(hard.get("gate_reasons"), list)
            else []
        )
        return {
            "verdict": explicit,
            "source": "gate_verdict",
            "reasons": reasons,
        }

    package_health = (
        hard.get("package_health")
        if isinstance(hard.get("package_health"), dict)
        else {}
    )
    package_status = str(
        package_health.get("status") or "not_assessed"
    ).casefold()
    if package_status == "invalid_skill_package" or (
        package_status != "not_assessed"
        and package_health.get("assessable") is False
    ):
        return {
            "verdict": "invalid_skill_package",
            "source": "package_health",
            "reasons": [
                {
                    "code": "legacy_invalid_skill_package",
                    "message": (
                        "Legacy hard-gates report has invalid package health "
                        "and no explicit gate_verdict"
                    ),
                }
            ],
        }

    legacy_pass = bool(scores.get("ship_floor_met"))
    return {
        "verdict": "pass" if legacy_pass else "fail",
        "source": "scores.ship_floor_met",
        "reasons": [] if legacy_pass else [
            {
                "code": "legacy_ship_floor_failed",
                "message": (
                    "Legacy hard-gates report has no gate_verdict and "
                    "scores.ship_floor_met is false"
                ),
            }
        ],
    }


def engineering_profile(
    hard: dict[str, Any] | None,
    safety: dict[str, Any] | None,
    behavior: dict[str, Any] | None,
) -> dict[str, Any]:
    if not hard:
        return {
            "status": "not_started",
            "level": None,
            "dimensions": {
                key: {"label": label, "state": None, "status": "not_assessed"}
                for key, label in DIMENSION_LABELS.items()
            },
            "archetype": {
                "id": "pending",
                "label": "类型待解锁",
                "summary": "先完成第一个 Skill 草稿和静态检查。",
                "growth": "从明确使用场景、输入、输出和完成标准开始。",
                "evidence_dimensions": [],
            },
            "personal_interpretation": {
                "eyebrow": "你的能力画像",
                "headline": PERSONAL_HEADLINES["pending"],
                "summary": (
                    PERSONAL_STRENGTHS["pending"]
                    + LEVEL_INTERPRETATIONS[0]
                    + "下一步先完成一个能被静态检查的 Skill 草稿。"
                ),
            },
            "learning_quest": build_learning_quest(
                {"id": "pending"},
                0,
                {key: 0 for key in DIMENSION_LABELS},
            ),
            "badges": [],
            "next_quest": {
                "lane": "skill_engineering",
                "title": "生成第一个可检查的 Skill 草稿",
                "action": "把已确认的工作流程写成 SKILL.md。",
                "acceptance": "hard_gates.py 可以读取并输出 JSON。",
                "unlocks": {"id": "Lv1", "label": LEVELS[1][1]},
            },
            "findings": [],
            "scores": None,
            "gate": None,
            "safety": None,
            "operational_metrics": operational_metrics(hard, behavior),
            "package_health": {
                "status": "not_assessed",
                "assessable": None,
                "checks": {},
                "summary": {},
            },
        }

    package_health = (
        hard.get("package_health")
        if isinstance(hard.get("package_health"), dict)
        else {}
    )
    package_status = str(
        package_health.get("status") or "not_assessed"
    ).casefold()
    package_invalid = package_status == "invalid_skill_package" or (
        package_status != "not_assessed"
        and package_health.get("assessable") is False
    )
    if package_invalid:
        hard_scores = (
            hard.get("scores") if isinstance(hard.get("scores"), dict) else {}
        )
        gate = resolve_hard_gate(hard, hard_scores)
        basic = (
            hard_scores.get("basic_usable")
            if isinstance(hard_scores.get("basic_usable"), dict)
            else {}
        )
        contract = (
            hard_scores.get("contract_clarity")
            if isinstance(hard_scores.get("contract_clarity"), dict)
            else {}
        )
        support = (
            hard_scores.get("support_kit")
            if isinstance(hard_scores.get("support_kit"), dict)
            else {}
        )
        raw_findings = clean_findings(
            hard.get("findings") or [],
            "skill_engineering",
            "hard_gates",
        ) + clean_findings(
            safety.get("findings") if safety else [],
            "skill_engineering",
            "ship_safety",
        )
        safety_counts = (
            safety.get("counts")
            if safety and isinstance(safety.get("counts"), dict)
            else {}
        )
        safety_verdict = str(
            safety.get("verdict") if safety else "not_assessed"
        )
        package_summary = (
            package_health.get("summary")
            if isinstance(package_health.get("summary"), dict)
            else {}
        )
        blocking_count = int_value(
            package_summary.get("blocking_check_count")
        )
        return {
            "status": "invalid_package",
            "level": None,
            "dimensions": {
                key: {
                    "label": label,
                    "state": None,
                    "status": "not_assessable",
                }
                for key, label in DIMENSION_LABELS.items()
            },
            "archetype": {
                "id": "structure-pending",
                "label": "结构待整理",
                "summary": "当前目标还不是一个边界清楚、可安装的标准 Skill 包。",
                "growth": "先整理包根、目录、路径和资源，再评价创作成熟度。",
                "evidence_dimensions": [],
            },
            "personal_interpretation": {
                "eyebrow": "当前不可生成能力画像",
                "headline": "先把项目工作区整理成一个标准 Skill 包",
                "summary": (
                    "原始文件检查仍可用于修复，但这些局部信号不能代表 Skill "
                    "创作成熟度。完成包结构前置门后再生成 Lv0–Lv5。"
                ),
            },
            "learning_quest": {
                "lane": "package_health",
                "title": "完成 Skill 包结构整理",
                "action": "先恢复唯一、可安装、可移植的 Skill 包边界。",
                "summary": "把唯一可安装 Skill 根与运行素材、输出产物分开。",
                "practice_points": [
                    {
                        "label": "唯一根",
                        "text": "只保留一个与 frontmatter name 同名的 Skill 根目录。",
                    },
                    {
                        "label": "资源归位",
                        "text": "将固定资源归入 assets/、references/、scripts/ 或 agents/。",
                    },
                    {
                        "label": "路径与产物",
                        "text": "移除本机绝对路径，并把生成结果放到包外。",
                    },
                ],
                "acceptance": (
                    "package_health.status=valid_skill_package，且所有阻断检查清零。"
                ),
            },
            "badges": [],
            "next_quest": {
                "lane": "package_health",
                "title": "先恢复可安装的标准 Skill 结构",
                "action": (
                    "统一根目录与 frontmatter name，整理非标准目录，修复绝对路径和"
                    "缺失资源引用，并把运行输出移出 Skill 包。"
                ),
                "acceptance": (
                    "hard_gates.py 返回 package_health.assessable=true，"
                    "blocking_check_count=0。"
                ),
                "unlocks": {"id": "maturity_assessment", "label": "成熟度评分"},
            },
            "findings": raw_findings,
            "scores": {
                "scoring_effect": "informational_only",
                "basic_usable": {
                    "score": int_value(basic.get("score")),
                    "max": int_value(basic.get("max"), 5),
                },
                "contract_clarity": {
                    "score": int_value(contract.get("score")),
                    "max": int_value(contract.get("max"), 5),
                },
                "support_kit": {
                    "score": int_value(support.get("score")),
                    "max": int_value(support.get("max")),
                },
                "ship_floor_met": bool(hard_scores.get("ship_floor_met")),
                "enterprise_ready": False,
                "interpretation": "partial_file_diagnostics_only",
            },
            "gate": gate,
            "portability": verified_platform_summary(behavior),
            "operational_metrics": operational_metrics(hard, behavior),
            "package_health": {
                "status": "invalid_skill_package",
                "assessable": False,
                "checks": package_health.get("checks") or {},
                "summary": {
                    "blocking_check_count": blocking_count,
                    "warning_check_count": int_value(
                        package_summary.get("warning_check_count")
                    ),
                    "files_scanned": int_value(
                        package_summary.get("files_scanned")
                    ),
                },
                "installability": package_health.get("installability") or {},
            },
            "safety": {
                "verdict": safety_verdict,
                "counts": {
                    "critical": int_value(safety_counts.get("critical")),
                    "should_fix": int_value(
                        safety_counts.get("should_fix")
                    ),
                    "info": int_value(safety_counts.get("info")),
                },
                "execution_status": str(
                    (safety.get("execution") or {}).get("status")
                    if safety and isinstance(safety.get("execution"), dict)
                    else "not_assessed"
                ),
                "interpretation": "secondary_to_invalid_package",
            },
        }

    scores = hard.get("scores") if isinstance(hard.get("scores"), dict) else {}
    basic = scores.get("basic_usable") if isinstance(scores.get("basic_usable"), dict) else {}
    contract = (
        scores.get("contract_clarity")
        if isinstance(scores.get("contract_clarity"), dict)
        else {}
    )
    support = scores.get("support_kit") if isinstance(scores.get("support_kit"), dict) else {}
    basic_score = int_value(basic.get("score"))
    basic_max = int_value(basic.get("max"), 5)
    contract_score = int_value(contract.get("score"))
    contract_max = int_value(contract.get("max"), 5)
    support_score = int_value(support.get("score"))
    support_max = int_value(support.get("max"))
    ship_floor = bool(scores.get("ship_floor_met"))
    gate = resolve_hard_gate(hard, scores)
    gate_pass = gate["verdict"] == "pass"

    safety_verdict = str(safety.get("verdict") if safety else "not_assessed")
    safety_counts = safety.get("counts") if safety and isinstance(safety.get("counts"), dict) else {}
    safety_critical = int_value(safety_counts.get("critical"))
    hard_counts = hard.get("counts") if isinstance(hard.get("counts"), dict) else {}
    hard_critical = int_value(hard_counts.get("critical"))
    static_safety_pass = safety_verdict == "static_pass" and safety_critical == 0
    core_flow_tested = bool_value(behavior, "core_flow_tested")
    pdca_evidence = bool_value(behavior, "pdca_evidence")
    safe_external_actions = bool_value(behavior, "safe_external_actions")
    write_back_integrity = bool_value(behavior, "write_back_integrity")
    failure_recovery = bool_value(behavior, "failure_recovery")
    portable_contract = bool_value(behavior, "portable_contract")
    target_unchanged = bool_value(behavior, "target_unchanged")

    external_applicability = behavior_applicability(
        behavior,
        "external_actions",
    )
    write_back_applicability = behavior_applicability(behavior, "write_back")
    detected_external_actions = (
        safety.get("external_actions")
        if safety and isinstance(safety.get("external_actions"), list)
        else []
    )
    if external_applicability["status"] == "not_applicable":
        external_controls_satisfied = (
            static_safety_pass
            and external_applicability["evidence_valid"]
            and not detected_external_actions
        )
        external_applicability["basis"] = (
            "静态安全通过、未发现外部动作，且不适用范围有证据"
            if external_controls_satisfied
            else "需要静态安全通过、无外部动作，并提供可分享的不适用证据"
        )
    else:
        external_controls_satisfied = safe_external_actions
        external_applicability["basis"] = (
            "适用的外部动作已有可信行为证据"
            if external_controls_satisfied
            else "外部动作适用，仍需默认关闭、授权和失败阻断证据"
        )
    external_applicability["satisfied"] = external_controls_satisfied

    if write_back_applicability["status"] == "not_applicable":
        write_back_controls_satisfied = (
            write_back_applicability["evidence_valid"] and target_unchanged
        )
        write_back_applicability["basis"] = (
            "目标前后指纹一致，且不写回范围有证据"
            if write_back_controls_satisfied
            else "需要可分享的不写回证据，并证明目标前后没有变化"
        )
    else:
        write_back_controls_satisfied = write_back_integrity
        write_back_applicability["basis"] = (
            "适用的写回动作已有一致性证据"
            if write_back_controls_satisfied
            else "写回适用，仍需写入前后的一致性与失败恢复证据"
        )
    write_back_applicability["satisfied"] = write_back_controls_satisfied
    safe_behavior_bundle = (
        external_controls_satisfied
        and write_back_controls_satisfied
        and failure_recovery
    )
    platform_summary = verified_platform_summary(behavior)
    platform_count = int(platform_summary["verified_platform_count"])

    level_ordinal = 0 if basic_score < 3 else 1
    legacy_score_contract = (
        basic_score >= 4 and contract_score >= 3
        if gate["source"] == "scores.ship_floor_met"
        else True
    )
    enterprise_ready = (
        gate_pass
        and legacy_score_contract
        and hard_critical == 0
        and safety_verdict == "static_pass"
        and safety_critical == 0
    )
    if enterprise_ready:
        level_ordinal = 2
    if (
        enterprise_ready
        and core_flow_tested
        and pdca_evidence
    ):
        level_ordinal = 3
    if level_ordinal >= 3 and safe_behavior_bundle:
        level_ordinal = 4
    if (
        level_ordinal >= 4
        and portable_contract
        and platform_count >= 2
    ):
        level_ordinal = 5
    if safety_verdict == "stop_ship":
        level_ordinal = min(level_ordinal, 1)

    points = contract.get("points") if isinstance(contract.get("points"), dict) else {}
    verification_declared = bool(points.get("verification_checkboxes"))
    contract_complete = contract_max > 0 and contract_score == contract_max
    kit_complete = bool(support.get("kit_complete"))
    dimensions = {
        "intent_contract": score_state(contract_score, contract_max),
        "workflow_execution": score_state(basic_score, basic_max),
        "tooling_support": score_state(support_score, support_max),
        "verification_learning": 1 if verification_declared else 0,
        "safety_control": 2 if static_safety_pass else 0,
        "portability_adaptation": 1,
    }
    if core_flow_tested:
        dimensions["workflow_execution"] = max(dimensions["workflow_execution"], 3)
        dimensions["verification_learning"] = max(
            dimensions["verification_learning"], 3
        )
        if kit_complete:
            dimensions["tooling_support"] = max(dimensions["tooling_support"], 3)
    if pdca_evidence:
        dimensions["verification_learning"] = max(
            dimensions["verification_learning"], 3
        )
    if core_flow_tested and failure_recovery:
        dimensions["workflow_execution"] = 4
        if kit_complete:
            dimensions["tooling_support"] = 4
    if core_flow_tested and pdca_evidence:
        dimensions["verification_learning"] = 4
    if static_safety_pass and external_controls_satisfied:
        dimensions["safety_control"] = max(dimensions["safety_control"], 3)
    if static_safety_pass and safe_behavior_bundle:
        dimensions["safety_control"] = 4
    if safe_behavior_bundle:
        dimensions["intent_contract"] = max(dimensions["intent_contract"], 3)
        if contract_complete:
            dimensions["intent_contract"] = 4
    if portable_contract:
        dimensions["portability_adaptation"] = 3
    if portable_contract and platform_count >= 2:
        dimensions["portability_adaptation"] = 4

    if min(dimensions.values()) >= 3 and max(dimensions.values()) - min(dimensions.values()) <= 1:
        archetype = {
            "id": "balanced",
            "label": "六边形选手",
            "summary": "六项能力稳定，没有明显短板。",
            "growth": "继续积累真实规模、长期运行和跨版本证据。",
            "evidence_dimensions": list(DIMENSION_LABELS),
        }
    else:
        ranked = []
        for order, item in enumerate(ARCHETYPES):
            affinity = sum(dimensions[key] for key in item["dimensions"])
            ranked.append((affinity, -order, item))
        _, _, selected = max(ranked, key=lambda row: (row[0], row[1]))
        archetype = {
            "id": selected["id"],
            "label": selected["label"],
            "summary": selected["summary"],
            "growth": selected["growth"],
            "evidence_dimensions": list(selected["dimensions"]),
        }

    badges: list[dict[str, str]] = []
    if basic_score == basic_max and basic_max:
        badges.append({"id": "skill-shaped", "label": "说明书已成型"})
    if contract_score == contract_max and contract_max:
        badges.append({"id": "contract-clear", "label": "边界说清楚"})
    if support.get("kit_complete") is True:
        badges.append({"id": "kit-complete", "label": "工具材料齐全"})
    if safety_verdict == "static_pass":
        badges.append({"id": "static-safe", "label": "静态安全通过"})
    if bool_value(behavior, "core_flow_tested"):
        badges.append({"id": "flow-tested", "label": "核心流程已测试"})
    if bool_value(behavior, "failure_recovery"):
        badges.append({"id": "failure-recovery", "label": "失败可以恢复"})
    verified_not_applicable = [
        item
        for item in (external_applicability, write_back_applicability)
        if item["status"] == "not_applicable" and item["satisfied"]
    ]
    if verified_not_applicable:
        badges.append(
            {"id": "applicability-evidenced", "label": "不适用项有证据"}
        )
    if platform_count >= 2:
        badges.append({"id": "multi-platform", "label": "双平台验证"})

    critical_findings = clean_findings(
        (hard.get("findings") or []), "skill_engineering", "hard_gates"
    ) + clean_findings(
        (safety.get("findings") if safety else []),
        "skill_engineering",
        "ship_safety",
    )
    first_critical = next(
        (item for item in critical_findings if item["severity"] == "critical"), None
    )
    level_id, level_label = LEVELS[level_ordinal]
    if first_critical:
        next_quest = {
            "lane": "skill_engineering",
            "title": "补齐实现与安全控制能力",
            "action": plain_finding_action(first_critical),
            "acceptance": (
                f"重新检查后，问题 {first_critical['id']} 不再属于高风险阻断项。"
            ),
            "unlocks": {"id": "Lv2", "label": LEVELS[2][1]},
        }
    elif basic_score < 4:
        next_quest = {
            "lane": "skill_engineering",
            "title": "补齐可识别的基础结构",
            "action": "补齐元信息、可执行步骤和完成标准。",
            "acceptance": "hard_gates.py 的基础结构达到静态底线。",
            "unlocks": {"id": "Lv1", "label": LEVELS[1][1]},
        }
    elif contract_score < 3:
        next_quest = {
            "lane": "skill_engineering",
            "title": "说清使用边界",
            "action": "补充何时使用、何时不用、检查轴和验证清单。",
            "acceptance": "contract_clarity 至少达到 3/5。",
            "unlocks": {"id": "Lv2", "label": LEVELS[2][1]},
        }
    elif safety_verdict != "static_pass":
        next_quest = {
            "lane": "skill_engineering",
            "title": "完成静态安全检查",
            "action": "修正文档承诺与实现差异，并为外部动作安装默认关闭。",
            "acceptance": "ship_safety.py 返回 static_pass 且 critical=0。",
            "unlocks": {"id": "Lv2", "label": LEVELS[2][1]},
        }
    else:
        # Enterprise mainline once static floor / safety are met.
        kit_complete = bool((support or {}).get("kit_complete"))
        next_quest = enterprise_next_quest_after_floor(
            kit_complete=kit_complete,
            support_max=support_max,
            contract_score=contract_score,
        )

    advanced_audit = build_advanced_audit(
        level_ordinal,
        behavior,
        enterprise_ready=enterprise_ready,
    )

    dimension_payload = {
        key: {
            "label": DIMENSION_LABELS[key],
            "state": value,
            "status": "verified" if value >= 3 else "static" if value >= 1 else "needs_work",
        }
        for key, value in dimensions.items()
    }
    return {
        "status": "assessed",
        "level": {
            "id": level_id,
            "label": level_label,
            "ordinal": level_ordinal,
            "max_ordinal": 5,
            "track_note": (
                "高级审计 · 作者轨道"
                if level_ordinal >= 4
                else "企业主线"
                if level_ordinal >= 2
                else "起步"
            ),
        },
        "dimensions": dimension_payload,
        "archetype": archetype,
        "personal_interpretation": build_personal_interpretation(
            archetype,
            level_ordinal,
            dimensions,
            critical_findings,
        ),
        "learning_quest": build_learning_quest(
            archetype,
            level_ordinal,
            dimensions,
        ),
        "badges": badges,
        "next_quest": next_quest,
        "advanced_audit": advanced_audit,
        "findings": critical_findings,
        "scores": {
            "scoring_effect": "informational_only",
            "basic_usable": {"score": basic_score, "max": basic_max},
            "contract_clarity": {
                "score": contract_score,
                "max": contract_max,
            },
            "support_kit": {"score": support_score, "max": support_max},
            "ship_floor_met": ship_floor,
            "enterprise_ready": enterprise_ready,
        },
        "gate": gate,
        "portability": platform_summary,
        "operational_metrics": operational_metrics(hard, behavior),
        "package_health": (
            package_health
            if package_health
            else {
                "status": "not_assessed",
                "assessable": None,
                "checks": {},
                "summary": {},
            }
        ),
        "safety": {
            "verdict": safety_verdict,
            "counts": {
                "critical": safety_critical,
                "should_fix": int_value(safety_counts.get("should_fix")),
                "info": int_value(safety_counts.get("info")),
            },
            "execution_status": str(
                (safety.get("execution") or {}).get("status")
                if safety and isinstance(safety.get("execution"), dict)
                else "not_assessed"
            ),
            "applicability": {
                "external_actions": external_applicability,
                "write_back": write_back_applicability,
                "target_unchanged": target_unchanged,
            },
        },
    }


def build_advanced_audit(
    level_ordinal: int,
    behavior: dict[str, Any] | None,
    *,
    enterprise_ready: bool,
) -> dict[str, Any]:
    """Author-track next steps; never replaces the enterprise next_quest."""
    quest_key = 2 if level_ordinal <= 2 else min(level_ordinal, 5)
    template = ADVANCED_AUDIT_QUESTS[quest_key]
    has_core = bool_value(behavior, "core_flow_tested") and bool_value(
        behavior, "pdca_evidence"
    )
    if level_ordinal >= 5:
        status = "satisfied"
        note = "高级审计轨道已满足多平台门槛；仍非企业日常必做项。"
    elif level_ordinal >= 3:
        status = "in_progress"
        note = "已有部分作者进阶证据；跨平台与完整闭环仍属高级审计。"
    elif has_core:
        status = "in_progress"
        note = "已附行为证据；继续高级审计可解锁更高作者等级。"
    else:
        status = "available"
        note = (
            "作者进阶证据未附；不影响企业主线「可受控试用」结论。"
            if enterprise_ready
            else "先达到企业主线门槛，再考虑作者进阶证据。"
        )
    return {
        "track": "author_advanced",
        "label": "高级审计 · 作者轨道",
        "status": status,
        "note": note,
        "required_for_enterprise": False,
        "next_quest": {
            "lane": "advanced_audit",
            "title": template["title"],
            "action": template["action"],
            "acceptance": template["acceptance"],
            "unlocks": template["unlocks"],
        },
    }


def enterprise_next_quest_after_floor(
    *,
    kit_complete: bool,
    support_max: int,
    contract_score: int,
) -> dict[str, Any]:
    """Default remediation once the Skill is good enough for controlled business use."""
    if support_max > 0 and not kit_complete:
        return {
            "lane": "enterprise_skill",
            "title": "补齐同事会用到的配套材料",
            "action": "把字段表、样例或话术模板放进资料/案例，正文只留步骤和验收。",
            "acceptance": "support_kit 齐全，或明确标记不适用模块。",
            "unlocks": None,
        }
    if contract_score < 5:
        return {
            "lane": "enterprise_skill",
            "title": "把何时不用和验收凭据说得更清楚",
            "action": "用业务原话补触发场景、必须人拍板的事，以及看什么单据/字段算完成。",
            "acceptance": "同事只看说明书就能判断该不该用、做得对不对。",
            "unlocks": None,
        }
    return {
        "lane": "enterprise_skill",
        "title": "用真实业务场景试跑一单",
        "action": (
            "选一个本周真实会发生的场景，按说明书走完，对照验收清单人工勾选；"
            "缺什么就改回 SKILL.md。"
        ),
        "acceptance": "验收清单可全部勾选，或已记下缺口并改回说明书。",
        "unlocks": None,
    }


def choose_next_quest(
    readiness: dict[str, Any],
    engineering: dict[str, Any],
) -> dict[str, Any]:
    if engineering.get("status") == "invalid_package":
        quest = engineering.get("next_quest")
        if isinstance(quest, dict):
            return quest
    readiness_level = readiness.get("level")
    if readiness_level and int_value(readiness_level.get("ordinal")) < 5:
        quest = readiness.get("next_quest")
        if isinstance(quest, dict):
            return quest
    quest = engineering.get("next_quest")
    if isinstance(quest, dict):
        return quest
    quest = readiness.get("next_quest")
    if isinstance(quest, dict):
        return quest
    return {
        "lane": "profile",
        "title": "补充一个可评估输入",
        "action": "提供 readiness、hard gates 或 ship safety JSON。",
        "acceptance": "profile_engine.py 能识别至少一条成长线。",
        "unlocks": None,
    }


def build_profile(
    readiness_report: dict[str, Any] | None,
    hard_report: dict[str, Any] | None,
    safety_report: dict[str, Any] | None,
    behavior_report: dict[str, Any] | None,
    title: str,
    subject_name: str | None = None,
) -> dict[str, Any]:
    readiness = normalize_readiness(readiness_report)
    engineering = engineering_profile(hard_report, safety_report, behavior_report)
    subject = identify_subject(
        readiness_report,
        hard_report,
        safety_report,
        subject_name,
    )
    all_findings = readiness["findings"] + engineering["findings"]
    counts = {
        "critical": sum(1 for item in all_findings if item["severity"] == "critical"),
        "should_fix": sum(
            1 for item in all_findings if item["severity"] == "should_fix"
        ),
        "info": sum(1 for item in all_findings if item["severity"] == "info"),
        "total": len(all_findings),
    }
    engineering_safety = (
        engineering.get("safety")
        if isinstance(engineering.get("safety"), dict)
        else {}
    )
    engineering_scores = (
        engineering.get("scores")
        if isinstance(engineering.get("scores"), dict)
        else {}
    )
    enterprise_ready = bool(engineering_scores.get("enterprise_ready"))
    # Enterprise mainline: package + contract + static safety must agree.
    # Missing author behavior / multi-platform evidence stays on advanced_audit.
    verdict = (
        "invalid_skill_package"
        if engineering.get("status") == "invalid_package"
        else "stop_ship"
        if engineering_safety.get("verdict") == "stop_ship"
        or counts["critical"] > 0
        else "ready_for_controlled_use"
        if engineering.get("status") == "assessed" and enterprise_ready
        else "needs_evidence"
        if engineering.get("status") == "assessed"
        else "planning"
    )
    advanced_audit = (
        engineering.get("advanced_audit")
        if isinstance(engineering.get("advanced_audit"), dict)
        else None
    )
    if advanced_audit is None and engineering.get("status") == "assessed":
        level_ordinal = int_value(
            (engineering.get("level") or {}).get("ordinal")
        )
        advanced_audit = build_advanced_audit(
            level_ordinal,
            behavior_report,
            enterprise_ready=enterprise_ready,
        )
    limitations: list[str] = []
    limitations.extend(readiness.get("limitations") or [])
    if hard_report:
        limitations.extend(hard_report.get("limitations") or [])
    if safety_report:
        limitations.extend(safety_report.get("limitations") or [])
    if behavior_report:
        limitations.extend(behavior_report.get("limitations") or [])
    limitations.append("growth labels are deterministic explanations, not personality tests")
    limitations = list(dict.fromkeys(str(item) for item in limitations if str(item).strip()))

    strengths = []
    for badge in readiness.get("badges", []):
        if isinstance(badge, dict):
            strengths.append(str(badge.get("label") or badge.get("id")))
    for badge in engineering.get("badges", []):
        if isinstance(badge, dict):
            strengths.append(str(badge.get("label") or badge.get("id")))
    strengths = [item for item in dict.fromkeys(strengths) if item][:3]

    return {
        "profile_schema_version": PROFILE_SCHEMA_VERSION,
        "ruleset_version": RULESET_VERSION,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "title": title,
        "subject": subject,
        "verdict": verdict,
        "verdict_summary": (
            "可受控试用：结构与静态安全已过企业主线门槛"
            if verdict == "ready_for_controlled_use"
            else "存在高风险阻断，先改 Critical"
            if verdict == "stop_ship"
            else "不是标准 Skill 包，先整理包结构"
            if verdict == "invalid_skill_package"
            else "尚未达到企业基础使用门槛"
            if verdict == "needs_evidence"
            else "还在规划，补充可评估输入"
        ),
        "business_readiness": readiness,
        "skill_engineering": engineering,
        "strengths": strengths,
        "next_quest": choose_next_quest(readiness, engineering),
        "advanced_audit": advanced_audit,
        "findings": all_findings,
        "counts": counts,
        "sources": {
            "readiness": "supplied" if readiness_report else "not_supplied",
            "hard_gates": "supplied" if hard_report else "not_supplied",
            "ship_safety": "supplied" if safety_report else "not_supplied",
            "behavior": (
                "not_supplied"
                if not behavior_report
                or str(behavior_report.get("source") or "").casefold()
                == "not_supplied"
                else "supplied"
            ),
        },
        "limitations": limitations,
    }


def render_html(profile: dict[str, Any], template_path: Path) -> str:
    if not template_path.is_file():
        raise ValueError(f"scorecard template not found: {template_path}")
    template = template_path.read_text(encoding="utf-8")
    payload = json.dumps(profile, ensure_ascii=False).replace("<", "\\u003c")
    return template.replace("__PROFILE_JSON__", payload).replace(
        "__DOCUMENT_TITLE__", str(profile.get("title") or "Skill DNA 成长成绩单")
    )


def main() -> int:
    force_utf8_streams()
    parser = argparse.ArgumentParser(description="Compose a Skill growth profile")
    parser.add_argument("--readiness", type=Path, help="readiness_gates JSON")
    parser.add_argument("--hard-gates", type=Path, help="hard_gates JSON")
    parser.add_argument("--ship-safety", type=Path, help="ship_safety JSON")
    parser.add_argument("--behavior", type=Path, help="optional behavior evidence JSON")
    parser.add_argument("--title", default="Skill DNA 成长成绩单")
    parser.add_argument(
        "--subject-name",
        help="explicit analyzed Skill or work-process name; overrides report metadata",
    )
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-html", type=Path)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    if not any((args.readiness, args.hard_gates, args.ship_safety, args.behavior)):
        parser.error("provide at least one input JSON")

    try:
        readiness = load_json(args.readiness, "readiness")
        hard = load_json(args.hard_gates, "hard gates")
        safety = load_json(args.ship_safety, "ship safety")
        behavior = load_json(args.behavior, "behavior")
        profile = build_profile(
            readiness,
            hard,
            safety,
            behavior,
            args.title,
            args.subject_name,
        )
        dump = json.dumps(profile, ensure_ascii=False, indent=2 if args.pretty else None)
        print(dump)
        if args.out_json:
            args.out_json.parent.mkdir(parents=True, exist_ok=True)
            args.out_json.write_text(dump + "\n", encoding="utf-8")
        if args.out_html:
            default_template = (
                Path(__file__).resolve().parents[1] / "assets" / "scorecard-template.html"
            )
            html = render_html(profile, args.template or default_template)
            args.out_html.parent.mkdir(parents=True, exist_ok=True)
            args.out_html.write_text(html, encoding="utf-8")
    except ValueError as exc:
        print(
            json.dumps(
                {
                    "profile_schema_version": PROFILE_SCHEMA_VERSION,
                    "ruleset_version": RULESET_VERSION,
                    "error": str(exc),
                },
                ensure_ascii=False,
            )
        )
        print(f"profile_engine: {exc}", file=sys.stderr)
        return 2

    skill_level = profile["skill_engineering"].get("level")
    skill_text = skill_level["id"] if skill_level else "not_started"
    business_level = profile["business_readiness"].get("level")
    business_text = business_level["id"] if business_level else "not_assessed"
    print(
        f"profile_engine: business={business_text} · skill={skill_text} · "
        f"verdict={profile['verdict']} · findings={profile['counts']['total']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
