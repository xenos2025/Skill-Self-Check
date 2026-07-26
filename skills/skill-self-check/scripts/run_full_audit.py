#!/usr/bin/env python3
"""Run the installed audit pack once and create two private offline scorecards.

The runner performs deterministic checks only. It never executes the audited
Skill, never performs a network action, and refuses to store real reports
inside the audited Skill or its source repository.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


IGNORED_PARTS = {"__pycache__", ".git"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
# This product entry is permanently a read-only DRY_RUN with respect to the
# audited Skill and external systems. It may launch only the installed local
# checker scripts listed in audit(); there is no flag that enables target code.
READ_ONLY_DRY_RUN = True


def force_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def nearest_repo_root(path: Path) -> Path | None:
    current = path.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def ensure_private_output(target: Path, output: Path) -> None:
    resolved_target = target.resolve()
    resolved_output = output.resolve()
    repo_root = nearest_repo_root(resolved_target)
    if (
        resolved_output == resolved_target
        or is_relative_to(resolved_output, resolved_target)
    ):
        raise ValueError("成绩单目录不能放在被检查的 Skill 里面")
    if repo_root and (
        resolved_output == repo_root
        or is_relative_to(resolved_output, repo_root)
    ):
        raise ValueError("真实审计报告必须保存在源码仓库外，避免被同步到 GitHub")
    if resolved_output.exists() and any(resolved_output.iterdir()):
        raise ValueError("成绩单目录已经存在且不是空目录，请换一个新目录")


def target_fingerprint(target: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    file_count = 0
    for path in sorted(target.rglob("*"), key=lambda item: item.as_posix()):
        if (
            not path.is_file()
            or any(part in IGNORED_PARTS for part in path.parts)
            or path.suffix.casefold() in IGNORED_SUFFIXES
        ):
            continue
        relative = path.relative_to(target).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        digest.update(b"\0")
        file_count += 1
    return {
        "algorithm": "sha256",
        "digest": digest.hexdigest(),
        "file_count": file_count,
        "ignored": ["**/__pycache__/**", "**/*.pyc", "**/*.pyo", ".git/**"],
    }


def run_json_script(script: Path, target: Path) -> dict[str, Any]:
    if not READ_ONLY_DRY_RUN:
        raise ValueError("一键审计入口必须保持只读预演模式")
    result = subprocess.run(
        [sys.executable, str(script), str(target)],
        cwd=script.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{script.name} 没有返回可读取的 JSON：{exc}") from exc
    report["_command_exit_code"] = result.returncode
    return report


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 JSON：{path.name}：{exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON 顶层必须是对象：{path.name}")
    return value


def load_profile_engine(script: Path) -> Any:
    spec = importlib.util.spec_from_file_location("skill_growth_profile_engine", script)
    if spec is None or spec.loader is None:
        raise ValueError("无法加载成长成绩单引擎")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None) + "\n",
        encoding="utf-8",
    )


def audit(
    target: Path,
    output: Path,
    *,
    work_package: Path | None,
    behavior_path: Path | None,
    subject_name: str | None,
    pretty: bool,
) -> dict[str, Any]:
    if not target.is_dir() or not (target / "SKILL.md").is_file():
        raise ValueError("被检查目录必须存在，并且包含 SKILL.md")
    ensure_private_output(target, output)

    skill_root = Path(__file__).resolve().parents[1]
    skills_root = skill_root.parent
    hard_script = skill_root / "scripts" / "hard_gates.py"
    safety_script = (
        skills_root / "skill-ship-safety" / "scripts" / "ship_safety.py"
    )
    readiness_script = (
        skills_root
        / "agent-work-readiness"
        / "scripts"
        / "readiness_gates.py"
    )
    profile_script = (
        skills_root
        / "skill-growth-scorecard"
        / "scripts"
        / "profile_engine.py"
    )
    template = (
        skills_root
        / "skill-growth-scorecard"
        / "assets"
        / "scorecard-template.html"
    )
    required = [hard_script, safety_script, profile_script, template]
    if work_package is not None:
        required.append(readiness_script)
    missing = [path.name for path in required if not path.is_file()]
    if missing:
        raise ValueError(
            "缺少完整审计包，请重新安装四个正式 Skill："
            + "、".join(sorted(missing))
        )

    before = target_fingerprint(target)
    hard = run_json_script(hard_script, target)
    safety = run_json_script(safety_script, target)
    readiness = (
        run_json_script(readiness_script, work_package)
        if work_package is not None
        else None
    )
    behavior = (
        load_json(behavior_path)
        if behavior_path is not None
        else {
            "schema_version": "1.0",
            "source": "not_supplied",
            "platforms": [],
            "limitations": [
                "本次只运行静态检查；没有把静态声明当作行为验证"
            ],
        }
    )
    after = target_fingerprint(target)
    unchanged = before["digest"] == after["digest"]
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    manifest = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "audit_mode": "read_only_static",
        "target": {
            "name": target.name,
            "path_disclosure": "omitted",
            "before": before,
            "after": after,
            "unchanged": unchanged,
        },
        "checks": {
            "hard_gates": "completed",
            "ship_safety": "completed",
            "business_readiness": (
                "completed" if readiness is not None else "not_supplied"
            ),
            "behavior_evidence": (
                "supplied" if behavior_path is not None else "not_supplied"
            ),
        },
        "limitations": [
            "没有执行被检查的 Skill",
            "目标未变化只证明审计过程只读，不证明 Skill 运行时不会写入",
            "跨平台能力必须由可信行为记录单独证明",
        ],
    }
    if not unchanged:
        raise ValueError("审计前后目标文件指纹发生变化，已停止生成成绩单")

    engine = load_profile_engine(profile_script)
    title_name = subject_name or str(
        ((hard.get("frontmatter") or {}).get("name")) or target.name
    )
    base_profile = engine.build_profile(
        readiness,
        hard,
        safety,
        behavior,
        "Skill 成长与项目成绩单",
        title_name,
    )
    personal = dict(base_profile)
    personal["title"] = f"{title_name} · 个人能力成绩单"
    personal["default_view"] = "growth"
    personal["report_kind"] = "personal_capability"
    personal["audit_manifest"] = {
        "target_unchanged": unchanged,
        "evidence": "audit-manifest.json#target",
    }
    project = dict(base_profile)
    project["title"] = f"{title_name} · 项目成绩单"
    project["default_view"] = "detection"
    project["report_kind"] = "project_delivery"
    project["audit_manifest"] = personal["audit_manifest"]

    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "hard-gates.json", hard, pretty)
    write_json(output / "ship-safety.json", safety, pretty)
    write_json(output / "behavior.json", behavior, pretty)
    if readiness is not None:
        write_json(output / "readiness.json", readiness, pretty)
    write_json(output / "audit-manifest.json", manifest, pretty)
    write_json(output / "personal-profile.json", personal, pretty)
    write_json(output / "project-profile.json", project, pretty)
    (output / "personal-scorecard.html").write_text(
        engine.render_html(personal, template),
        encoding="utf-8",
    )
    (output / "project-scorecard.html").write_text(
        engine.render_html(project, template),
        encoding="utf-8",
    )
    return {
        "status": "completed",
        "subject": title_name,
        "project_verdict": project["verdict"],
        "personal_level": (
            ((personal.get("skill_engineering") or {}).get("level") or {}).get("id")
        ),
        "target_unchanged": unchanged,
        "output_directory": str(output),
        "artifacts": sorted(path.name for path in output.iterdir()),
    }


def main() -> int:
    force_utf8_streams()
    parser = argparse.ArgumentParser(
        description="一键运行静态审计，并生成个人能力与项目两份离线成绩单"
    )
    parser.add_argument("target_skill", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--work-package", type=Path)
    parser.add_argument("--behavior", type=Path)
    parser.add_argument("--subject-name")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        result = audit(
            args.target_skill.resolve(),
            args.out_dir.resolve(),
            work_package=(
                args.work_package.resolve() if args.work_package else None
            ),
            behavior_path=args.behavior.resolve() if args.behavior else None,
            subject_name=args.subject_name,
            pretty=args.pretty,
        )
    except (OSError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "error", "error": str(exc)},
                ensure_ascii=False,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
