#!/usr/bin/env python3
"""Compose readiness and Skill audit JSON into a deterministic growth profile.

The generator is intentionally stateless and stdlib-only. It never executes the
audited Skill. HTML is rendered from a local template with the same JSON fact set.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROFILE_SCHEMA_VERSION = "0.2"
RULESET_VERSION = "0.2"
LEVELS = [
    ("Lv0", "灵感草稿"),
    ("Lv1", "初学者 · 起步创作者"),
    ("Lv2", "入门应用 · 实用搭建者"),
    ("Lv3", "中级应用 · 稳定实践者"),
    ("Lv4", "高级应用 · 闭环工程师"),
    ("Lv5", "专家级 · 跨平台架构师"),
]

ARCHETYPES = [
    {
        "id": "flow-navigator",
        "label": "流程探路者",
        "dimensions": ("intent_contract", "workflow_execution"),
        "summary": "擅长把目标铺成一条完整路线。",
        "growth": "继续把每个承诺连接到验证和安全证据。",
    },
    {
        "id": "steady-builder",
        "label": "稳健搭建者",
        "dimensions": ("intent_contract", "tooling_support"),
        "summary": "结构清楚，重视说明和配套材料。",
        "growth": "把静态结构推进到可重复运行的行为证据。",
    },
    {
        "id": "automation-craftsperson",
        "label": "自动化工匠",
        "dimensions": ("workflow_execution", "tooling_support"),
        "summary": "善于把任务做成脚本和可执行工具。",
        "growth": "补强默认关闭和失败恢复；适用时验证写回一致性，只读边界也要留下证据。",
    },
    {
        "id": "loop-coach",
        "label": "闭环教练",
        "dimensions": ("verification_learning", "intent_contract"),
        "summary": "重视检查、复盘和持续改进。",
        "growth": "保持验证质量，同时控制流程复杂度。",
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
        "label": "跨平台架构师",
        "dimensions": ("portability_adaptation", "intent_contract"),
        "summary": "擅长用稳定契约降低平台迁移成本。",
        "growth": "用真实平台证据控制抽象复杂度。",
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
    "platform-architect": "你擅长用稳定规则适配不同 Agent 平台",
    "balanced": "你已经能把六项 Skill 能力连成完整闭环",
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
        "从这份 Skill 的契约与适配设计看，你已经表现出用稳定规则降低平台迁移成本的能力。"
    ),
    "balanced": (
        "从这份 Skill 的完整证据链看，你已经能把目标、执行、工具、"
        "验证、安全和平台适配连成闭环。"
    ),
}

LEVEL_INTERPRETATIONS = {
    0: "目前还在草稿阶段，重点是先让目标、边界和完成标准可被检查。",
    1: "目前仍处于起步阶段。",
    2: "目前已进入入门应用阶段，静态结构已经达到受控试用的基础线。",
    3: "目前已进入中级应用阶段，测试与复盘开始形成稳定习惯。",
    4: "目前已进入高级应用阶段，已经能够同时处理执行、安全和失败恢复。",
    5: "目前已进入专家阶段，已经具备用同一套规则服务多个 Agent 平台的能力。",
}

LEVEL_LEARNING_QUESTS = {
    0: {
        "title": "练习把一个口头任务写成可检查的 Skill",
        "action": "从一个每周都会重复的小任务开始，不追求复杂功能，先练习把工作说清楚。",
        "practice_points": [
            {
                "label": "量化目标",
                "text": "写清输入、预期输出、成功阈值和停止条件。",
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
        "title": "练习把 Skill 做成可判断、可复用、可验证的工程单元",
        "action": "选取当前 Skill 中最小的一条流程，用脱敏材料完成以下四项练习。",
        "practice_points": [
            {
                "label": "量化目标",
                "text": "补齐输入、输出、成功阈值、停止条件和升级条件。",
            },
            {
                "label": "判断流程",
                "text": "分别设计正常、资料不足、无权限和执行失败时的处理路径。",
            },
            {
                "label": "可复用组件",
                "text": "把重复说明、模板或脚本整理成可传入参数、可返回状态的独立模块。",
            },
            {
                "label": "Harness 位置",
                "text": "把 Harness（测试驱动器）放在目标 Skill 外部，用脱敏输入调用它、记录结果并检查规则；Harness 不负责真实业务发送。",
            },
        ],
        "acceptance": "用一个脱敏案例跑通 Harness，四类判断都有可复核结果，且不触发真实发送或外部写入。",
    },
    2: {
        "title": "练习用行为证据替代“应该能用”",
        "action": "为一条已经达到静态底线的核心流程建立可重复测试。",
        "practice_points": [
            {
                "label": "脱敏夹具",
                "text": "准备固定输入、预期输出和不会影响真实业务的数据。",
            },
            {
                "label": "核心与异常",
                "text": "同时测试正常路径、缺少数据和执行失败路径。",
            },
            {
                "label": "结果断言",
                "text": "让测试自动判断输出、状态和停止条件是否正确。",
            },
            {
                "label": "复盘记录",
                "text": "保存问题、修改和回归结果，说明下一版改变了什么。",
            },
        ],
        "acceptance": "核心路径与至少一条异常路径可以重复测试，并留下测试结果和一次改进记录。",
    },
    3: {
        "title": "练习让 Agent 在越界和失败时正确停下",
        "action": (
            "围绕最接近真实风险的一条流程练习边界与恢复；如有外部动作就检查权限、"
            "确认和写回，只读 Skill 则检查越权写入、异常输入和中断恢复。"
        ),
        "practice_points": [
            {
                "label": "权限矩阵",
                "text": "写清允许、禁止、必须人工确认、只读和需要升级的动作。",
            },
            {
                "label": "默认预演",
                "text": "真实发送或写入默认关闭；只读 Skill 还要验证不会暗中修改目标文件。",
            },
            {
                "label": "写回一致性",
                "text": "适用时验证失败或重试不重复写入；不适用时留下只读范围证据。",
            },
            {
                "label": "失败恢复",
                "text": "用 Harness 模拟中断、超时和无权限，验证 Agent 会停止并留下证据。",
            },
        ],
        "acceptance": (
            "无授权、重复执行和中途失败三类测试都能安全停止或恢复；不适用项有"
            "明确范围和证据，且没有真实副作用。"
        ),
    },
    4: {
        "title": "练习把业务契约与 Agent 平台分开",
        "action": "保持同一套业务输入输出不变，把平台差异收进独立适配层。",
        "practice_points": [
            {
                "label": "稳定契约",
                "text": "固定输入、输出、错误状态和验收规则，不写入单一模型特性。",
            },
            {
                "label": "平台适配",
                "text": "把工具调用、目录、权限和消息格式放进平台适配器。",
            },
            {
                "label": "双平台测试",
                "text": "使用同一脱敏夹具在至少两个 AI 或 Agent 平台运行。",
            },
            {
                "label": "差异记录",
                "text": "记录哪些差异由适配层解决，哪些必须升级给人工判断。",
            },
        ],
        "acceptance": "同一契约和夹具在两个平台得到可比较结果，平台差异没有污染核心流程。",
    },
    5: {
        "title": "练习维护一个可以长期演进的 Agent 工程",
        "action": "把关注点从单次通过提升到规模、版本和长期回归。",
        "practice_points": [
            {
                "label": "回归基线",
                "text": "固定关键场景、性能边界和安全门槛，版本变化后自动复查。",
            },
            {
                "label": "版本迁移",
                "text": "记录契约、适配层和依赖变化，并提供兼容或迁移说明。",
            },
            {
                "label": "规模证据",
                "text": "观察真实任务量下的失败率、恢复时间和人工接管比例。",
            },
            {
                "label": "经验传递",
                "text": "把设计理由、常见错误和验证方法整理成团队可以复用的规范。",
            },
        ],
        "acceptance": "下一版本仍通过回归、安全和跨平台门槛，并能解释关键设计为什么这样做。",
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
        title = "练习把自动化脚本接入可验证的工程闭环"
        practice_points[2] = {
            "label": "可复用脚本",
            "text": "把重复逻辑整理成可传入参数、可返回状态、失败时给出明确原因的公共命令。",
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
            "safety": None,
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
    static_ready = (
        basic_score >= 4
        and contract_score >= 3
        and ship_floor
        and hard_critical == 0
        and safety_verdict == "static_pass"
        and safety_critical == 0
    )
    if static_ready:
        level_ordinal = 2
    if (
        static_ready
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
    elif level_ordinal == 2:
        next_quest = {
            "lane": "skill_engineering",
            "title": "补核心流程行为证据",
            "action": "用脱敏夹具验证核心路径，并保存 PDCA 复盘。",
            "acceptance": "core_flow_tested 和 pdca_evidence 均有可信证据。",
            "unlocks": {"id": "Lv3", "label": LEVELS[3][1]},
        }
    elif level_ordinal == 3:
        next_quest = {
            "lane": "skill_engineering",
            "title": "证明适用的安全边界和失败恢复",
            "action": (
                "有外部动作时验证默认关闭和写回一致性；只读 Skill 则验证不越权写入，"
                "并补齐中断与异常输入的恢复证据。"
            ),
            "acceptance": "适用项有行为证据，不适用项有明确范围，失败场景可以安全停止或恢复。",
            "unlocks": {"id": "Lv4", "label": LEVELS[4][1]},
        }
    elif level_ordinal == 4:
        next_quest = {
            "lane": "skill_engineering",
            "title": "完成跨平台验证",
            "action": (
                "使用同一份契约和同一套脱敏夹具在至少两个 Agent 平台运行，"
                "分别保存结果证据。"
            ),
            "acceptance": (
                "两个平台记录均为 verified，且 contract_id 与 fixture_id "
                "是相同的 SHA-256 指纹。"
            ),
            "unlocks": {"id": "Lv5", "label": LEVELS[5][1]},
        }
    else:
        next_quest = {
            "lane": "skill_engineering",
            "title": "保持长期运行证据",
            "action": "记录真实规模、回归和版本变化。",
            "acceptance": "下一版本仍通过全部门槛。",
            "unlocks": {"id": "Lv5", "label": LEVELS[5][1]},
        }

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
        "findings": critical_findings,
        "scores": {
            "basic_usable": {"score": basic_score, "max": basic_max},
            "contract_clarity": {
                "score": contract_score,
                "max": contract_max,
            },
            "support_kit": {"score": support_score, "max": support_max},
            "ship_floor_met": ship_floor,
        },
        "portability": platform_summary,
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


def choose_next_quest(
    readiness: dict[str, Any],
    engineering: dict[str, Any],
) -> dict[str, Any]:
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
    verdict = (
        "stop_ship"
        if engineering_safety.get("verdict") == "stop_ship"
        or counts["critical"] > 0
        else "needs_evidence"
        if engineering.get("status") == "assessed"
        and engineering.get("level", {}).get("ordinal", 0) < 4
        else "ready_for_controlled_use"
        if engineering.get("status") == "assessed"
        else "planning"
    )
    limitations: list[str] = []
    limitations.extend(readiness.get("limitations") or [])
    if hard_report:
        limitations.extend(hard_report.get("limitations") or [])
    if safety_report:
        limitations.extend(safety_report.get("limitations") or [])
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
        "business_readiness": readiness,
        "skill_engineering": engineering,
        "strengths": strengths,
        "next_quest": choose_next_quest(readiness, engineering),
        "findings": all_findings,
        "counts": counts,
        "sources": {
            "readiness": "supplied" if readiness_report else "not_supplied",
            "hard_gates": "supplied" if hard_report else "not_supplied",
            "ship_safety": "supplied" if safety_report else "not_supplied",
            "behavior": "supplied" if behavior_report else "not_supplied",
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
