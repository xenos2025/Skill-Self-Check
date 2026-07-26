#!/usr/bin/env python3
"""Create one comparable Agent-platform evidence record.

This helper hashes a stable contract and sanitized fixture. It does not run or
verify a platform by itself. The default status is needs_review; marking a
record verified requires an explicit reviewer attestation note.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def force_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def sha256_id(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def valid_evidence_reference(value: str) -> bool:
    reference = value.strip()
    if not reference:
        return False
    lowered = reference.casefold()
    if lowered.startswith("file://") or reference.startswith(("/", "\\", "~")):
        return False
    if re.match(r"^[a-zA-Z]:[\\/]", reference):
        return False
    path_part = reference.split("#", 1)[0].replace("\\", "/")
    return ".." not in path_part.split("/")


def build_record(
    platform: str,
    contract: Path,
    fixture: Path,
    evidence: str,
    *,
    verified: bool,
    review_note: str,
) -> dict[str, Any]:
    name = " ".join(platform.split())
    if not name:
        raise ValueError("平台名称不能为空")
    if not contract.is_file():
        raise ValueError("契约文件不存在")
    if not fixture.is_file():
        raise ValueError("测试夹具文件不存在")
    if not valid_evidence_reference(evidence):
        raise ValueError("证据必须使用可分享的相对引用或 HTTPS 地址，不能使用本机绝对路径")
    note = " ".join(review_note.split())
    if verified and not note:
        raise ValueError("标记 verified 前必须提供 --review-note 说明谁核对了哪些结果")
    return {
        "name": name,
        "status": "verified" if verified else "needs_review",
        "evidence": evidence.strip(),
        "contract_id": sha256_id(contract),
        "fixture_id": sha256_id(fixture),
        "review": {
            "attested": verified,
            "note": note or "尚未由可信运行器或审核者确认",
        },
        "limitations": [
            "本脚本只计算可比较指纹，不执行 Agent 平台",
            "verified 仍需审核者核对平台调用、隔离边界和验收断言",
        ],
    }


def main() -> int:
    force_utf8_streams()
    parser = argparse.ArgumentParser(
        description="为一次 Agent 平台运行生成可比较证据记录"
    )
    parser.add_argument("--platform", required=True)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--verified", action="store_true")
    parser.add_argument("--review-note", default="")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        record = build_record(
            args.platform,
            args.contract,
            args.fixture,
            args.evidence,
            verified=args.verified,
            review_note=args.review_note,
        )
    except (OSError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "error", "error": str(exc)},
                ensure_ascii=False,
            )
        )
        return 2
    dump = json.dumps(record, ensure_ascii=False, indent=2 if args.pretty else None)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(dump + "\n", encoding="utf-8")
    print(dump)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
