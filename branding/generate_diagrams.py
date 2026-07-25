#!/usr/bin/env python3
"""Generate Swiss International (blue / white) SVG diagrams for README.

Plain-language copy for bosses and non-technical readers.
Accent: #0B3D91.

Usage:
  python branding/generate_diagrams.py
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "diagrams"
OUT_ZH = OUT / "zh"
OUT.mkdir(parents=True, exist_ok=True)
OUT_ZH.mkdir(parents=True, exist_ok=True)

ACCENT = "#0B3D91"
ACCENT_BRIGHT = "#0050B3"
CANVAS = "#FFFFFF"
BOX = "#FFFFFF"
BOX_BORDER = "#D0D7E2"
BOX_FOCAL = "#F0F4FA"
TEXT = "#1A1A1A"
TEXT_MUTED = "#4A5568"
TEXT_TINY = "#6B7280"
TITLE_H = 48


def _esc(s: str) -> str:
    return escape(s, {"'": "&apos;", '"': "&quot;"})


def window_chrome(w: float, title: str) -> str:
    cy = TITLE_H / 2
    return f'''
  <rect x="0" y="0" width="{w}" height="{TITLE_H}" fill="{CANVAS}"/>
  <rect x="0" y="0" width="4" height="{TITLE_H}" fill="{ACCENT}"/>
  <line x1="0" y1="{TITLE_H}" x2="{w}" y2="{TITLE_H}" stroke="{ACCENT}" stroke-width="1.5"/>
  <text x="20" y="{cy + 5}" fill="{TEXT_MUTED}" font-size="13"
        font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">{_esc(title)}</text>
  <rect x="{w - 36}" y="{cy - 6}" width="16" height="12" fill="{ACCENT}"/>
'''


def svg_shell(w: int, h: int, body: str, win_title: str, corner: str) -> str:
    total_h = h + TITLE_H
    return dedent(f"""\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {total_h}"
     width="{w}" height="{total_h}" role="img"
     aria-label="{_esc(win_title)}">
  <defs>
    <style>
      .label {{ fill: {TEXT}; font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", "Segoe UI", system-ui, sans-serif; font-weight: 600; }}
      .label-sub {{ fill: {TEXT_MUTED}; font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", "Segoe UI", system-ui, sans-serif; font-weight: 400; }}
      .label-tiny {{ fill: {TEXT_TINY}; font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", "Segoe UI", system-ui, sans-serif; font-weight: 400; }}
      .label-accent {{ fill: {ACCENT}; font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", "Segoe UI", system-ui, sans-serif; font-weight: 600; }}
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Microsoft YaHei", monospace; }}
    </style>
  </defs>
  <rect width="{w}" height="{total_h}" rx="2" fill="{CANVAS}" stroke="{BOX_BORDER}" stroke-width="1"/>
  {window_chrome(w, win_title)}
  <g transform="translate(0, {TITLE_H})">
{body}
    <text x="{w - 20}" y="{h - 16}" text-anchor="end" class="label-tiny mono">{_esc(corner)}</text>
  </g>
</svg>
""")


def card(cx, cy, w, h, eyebrow, title, lines, *, focal=False) -> str:
    x, y = cx - w / 2, cy - h / 2
    fill = BOX_FOCAL if focal else BOX
    stroke = ACCENT if focal else BOX_BORDER
    sw = 1.6 if focal else 1
    parts = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="2" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>',
        f'<text x="{cx:.1f}" y="{y + 26:.1f}" text-anchor="middle" '
        f'class="label-tiny" font-size="11" letter-spacing="0.08em">{_esc(eyebrow)}</text>',
        f'<text x="{cx:.1f}" y="{y + 52:.1f}" text-anchor="middle" '
        f'class="label" font-size="18">{_esc(title)}</text>',
    ]
    for i, ln in enumerate(lines):
        parts.append(
            f'<text x="{cx:.1f}" y="{y + 78 + i * 18:.1f}" text-anchor="middle" '
            f'class="label-tiny" font-size="13">{_esc(ln)}</text>'
        )
    return "\n".join(parts)


def arrow_h(x1, y, x2) -> str:
    return (
        f'<line x1="{x1}" y1="{y}" x2="{x2 - 10}" y2="{y}" '
        f'stroke="{BOX_BORDER}" stroke-width="2"/>'
        f'<polygon points="{x2},{y} {x2 - 12},{y - 5} {x2 - 12},{y + 5}" fill="{ACCENT}"/>'
    )


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


# --- diagrams ----------------------------------------------------------------


def how_to_use(zh: bool) -> str:
    if zh:
        banner = "一句话：像验货一样，验「AI 工作说明书」能不能用"
        steps = [
            ("第 1 步", "写好说明书", ["把做事步骤写清楚", "（也叫 Skill）"], False),
            ("第 2 步", "一键自检", ["电脑先打分", "再给修改意见"], True),
            ("第 3 步", "看三盏灯", ["能不能上手用", "说清了吗", "配套齐了吗"], False),
            ("第 4 步", "改完再用", ["先过门槛再真用", "边用边观察"], False),
            ("可选", "先访谈客户", ["把事情问清楚", "再决定写哪些说明书"], False),
        ]
        title = "skill-self-check.app -> docs -> how-to-use.svg"
        corner = "01 · 怎么用"
    else:
        banner = "In plain words: inspect an AI playbook before you trust it"
        steps = [
            ("STEP 1", "Write the playbook", ["Clear steps for the AI", "(called a Skill)"], False),
            ("STEP 2", "Run self-check", ["Script scores first", "Then fix suggestions"], True),
            ("STEP 3", "Read three lights", ["Usable?", "Clear?", "Kit complete?"], False),
            ("STEP 4", "Fix, then use", ["Pass the floor first", "Learn while using"], False),
            ("OPTIONAL", "Interview first", ["Ask until clear", "Then decide which playbooks"], False),
        ]
        title = "skill-self-check.app -> docs -> how-to-use.svg"
        corner = "01 · how to use"

    w, h = 1480, 360
    n = len(steps)
    gap = w / (n + 0.4)
    y_line = 200
    parts = [
        f'<text x="{w/2}" y="36" text-anchor="middle" class="label-sub" font-size="15">{_esc(banner)}</text>',
        f'<line x1="{gap*0.55:.1f}" y1="{y_line}" x2="{gap*(n-0.45)+gap*0.55:.1f}" y2="{y_line}" '
        f'stroke="{BOX_BORDER}" stroke-width="2"/>',
    ]
    for i, (eye, title_s, lines, focal) in enumerate(steps):
        cx = gap * (i + 0.55)
        cy = 150 if i % 2 == 0 else 250
        parts.append(f'<circle cx="{cx:.1f}" cy="{y_line}" r="8" fill="{ACCENT if not focal else ACCENT_BRIGHT}"/>')
        parts.append(card(cx, cy, 240, 120, eye, title_s, lines, focal=focal))
        if cy < y_line:
            parts.append(
                f'<line x1="{cx:.1f}" y1="{y_line - 8}" x2="{cx:.1f}" y2="{cy + 60}" '
                f'stroke="{BOX_BORDER}" stroke-width="1.4"/>'
            )
        else:
            parts.append(
                f'<line x1="{cx:.1f}" y1="{y_line + 8}" x2="{cx:.1f}" y2="{cy - 60}" '
                f'stroke="{BOX_BORDER}" stroke-width="1.4"/>'
            )
    return svg_shell(w, h, "\n".join(parts), title, corner)


def pdca(zh: bool) -> str:
    if zh:
        banner = "PDCA：做事要闭环 — 计划 → 执行 → 检查 → 改进（缺一环就容易瞎忙）"
        boxes = [
            ("P 计划", "先说清楚", ["什么时候用", "查什么 / 不查什么", "怎样算成功"]),
            ("D 执行", "按步骤做", ["一步一步来", "每步怎样算做完", "留下痕迹"]),
            ("C 检查", "拿证据验收", ["对照清单勾选", "有输出才算过", "不能只说「好像行」"]),
            ("A 改进", "错了知道怎么改", ["常见借口对照", "红灯信号", "改完再跑一轮"]),
        ]
        foot = "用在：写说明书、自检报告、客户访谈都会走这一圈"
        title = "skill-self-check.app -> docs -> pdca.svg"
        corner = "02 · PDCA"
    else:
        banner = "PDCA: close the loop — Plan → Do → Check → Act"
        boxes = [
            ("P Plan", "Decide first", ["When to use", "What is in / out of scope", "What success looks like"]),
            ("D Do", "Follow steps", ["One step at a time", "Done-when for each step", "Leave a trail"]),
            ("C Check", "Prove it", ["Checkbox with evidence", "No “seems fine”", "Pass or fail clearly"]),
            ("A Act", "Fix the path", ["Common excuses", "Red flags", "Retry after fix"]),
        ]
        foot = "Used in: writing playbooks, self-check reports, and client interviews"
        title = "skill-self-check.app -> docs -> pdca.svg"
        corner = "02 · PDCA"

    w, h = 1320, 420
    parts = [
        f'<text x="{w/2}" y="36" text-anchor="middle" class="label-sub" font-size="15">{_esc(banner)}</text>',
    ]
    xs = [180, 480, 780, 1080]
    for i, ((eye, t, lines), cx) in enumerate(zip(boxes, xs)):
        parts.append(card(cx, 180, 260, 160, eye, t, lines, focal=(i == 2)))
        if i < 3:
            parts.append(arrow_h(cx + 130, 180, xs[i + 1] - 130))
    # loop back hint
    parts.append(
        f'<path d="M 1080 270 C 1080 340, 180 340, 180 270" fill="none" '
        f'stroke="{ACCENT}" stroke-width="1.6" stroke-dasharray="6 4"/>'
    )
    parts.append(
        f'<text x="{w/2}" y="360" text-anchor="middle" class="label-tiny" font-size="13">{_esc(foot)}</text>'
    )
    parts.append(
        f'<text x="{w/2}" y="385" text-anchor="middle" class="label-accent" font-size="13">'
        f'{_esc("再来一轮 →" if zh else "loop again →")}</text>'
    )
    return svg_shell(w, h, "\n".join(parts), title, corner)


def smart(zh: bool) -> str:
    if zh:
        banner = "SMART：目标要说人话 — 老板能听懂、员工能验收"
        items = [
            ("S 具体", "Specific", "别说「做好运营」", "要说「每周出询盘复盘表」"),
            ("M 可衡量", "Measurable", "别说「质量高一点」", "要说「对照清单全勾完」"),
            ("A 可做到", "Achievable", "别一次包圆全公司", "一本说明书只办一类事"),
            ("R 相关", "Relevant", "步骤要对上真实工作", "别写成百科文章"),
            ("T 有终点", "Time-bound", "不是硬编季度口号", "是「这次跑完就算结束」"),
        ]
        title = "skill-self-check.app -> docs -> smart.svg"
        corner = "03 · SMART"
    else:
        banner = "SMART: goals a boss can understand and a team can verify"
        items = [
            ("S Specific", "Specific", "Not “do ops better”", "Say the exact deliverable"),
            ("M Measurable", "Measurable", "Not “higher quality”", "Checklist / number / proof"),
            ("A Achievable", "Achievable", "Not boil the ocean", "One playbook, one job"),
            ("R Relevant", "Relevant", "Steps match real work", "Not an encyclopedia"),
            ("T Bound exit", "Time-bound", "Not fake OKR dates", "Each run has a finish line"),
        ]
        title = "skill-self-check.app -> docs -> smart.svg"
        corner = "03 · SMART"

    w, h = 1400, 400
    parts = [
        f'<text x="{w/2}" y="36" text-anchor="middle" class="label-sub" font-size="15">{_esc(banner)}</text>',
    ]
    card_w = 240
    gap = (w - 80 - card_w * 5) / 4
    for i, (eye, t, bad, good) in enumerate(items):
        cx = 40 + card_w / 2 + i * (card_w + gap)
        x = cx - card_w / 2
        y = 70
        parts.append(
            f'<rect x="{x:.1f}" y="{y}" width="{card_w}" height="260" rx="2" '
            f'fill="{BOX}" stroke="{BOX_BORDER}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y + 32}" text-anchor="middle" class="label-accent" '
            f'font-size="14">{_esc(eye)}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y + 62}" text-anchor="middle" class="label" '
            f'font-size="16">{_esc(t)}</text>'
        )
        parts.append(
            f'<rect x="{x + 16:.1f}" y="{y + 90}" width="{card_w - 32}" height="64" rx="2" '
            f'fill="#F8FAFC" stroke="{BOX_BORDER}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y + 115}" text-anchor="middle" class="label-tiny" '
            f'font-size="12">{_esc(("别这样" if zh else "Avoid"))}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y + 138}" text-anchor="middle" class="label-sub" '
            f'font-size="13">{_esc(bad)}</text>'
        )
        parts.append(
            f'<rect x="{x + 16:.1f}" y="{y + 170}" width="{card_w - 32}" height="64" rx="2" '
            f'fill="{BOX_FOCAL}" stroke="{ACCENT}" stroke-width="1.4"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y + 195}" text-anchor="middle" class="label-tiny" '
            f'font-size="12">{_esc(("要这样" if zh else "Prefer"))}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y + 218}" text-anchor="middle" class="label" '
            f'font-size="13">{_esc(good)}</text>'
        )
    return svg_shell(w, h, "\n".join(parts), title, corner)


def five_w2h(zh: bool) -> str:
    if zh:
        banner = "5W2H：跟客户谈话时，七问问清再动手（一次只问一句）"
        cells = [
            ("What 做什么", "结果是什么？", "别接受：「日常运营」"),
            ("Why 为什么", "为了哪个数字？", "别接受：「领导要的」"),
            ("Who 谁来做", "谁动手谁审批？", "别接受：「我们团队」"),
            ("When 何时", "什么时候触发？", "别接受：「有空就做」"),
            ("Where 在哪", "在哪个系统里？", "别接受：「电脑上」"),
            ("How 怎么做", "步骤和例外？", "别接受：「看着办」"),
            ("How much 多少", "量 / 钱 / 时效？", "别接受：「不少」"),
        ]
        foot = "问清 → 画流程 → 再决定写哪些 AI 说明书"
        title = "skill-self-check.app -> docs -> 5w2h.svg"
        corner = "04 · 5W2H"
    else:
        banner = "5W2H: ask until clear in client interviews (one question at a time)"
        cells = [
            ("What", "What deliverable?", "Reject: “daily ops”"),
            ("Why", "Which KPI / risk?", "Reject: “boss wants it”"),
            ("Who", "Doer / approver?", "Reject: “our team”"),
            ("When", "What triggers it?", "Reject: “when free”"),
            ("Where", "Which system?", "Reject: “on the computer”"),
            ("How", "Steps & exceptions?", "Reject: “figure it out”"),
            ("How much", "Volume / money / SLA?", "Reject: “a lot”"),
        ]
        foot = "Clear answers → workflow map → then decide which playbooks to write"
        title = "skill-self-check.app -> docs -> 5w2h.svg"
        corner = "04 · 5W2H"

    w, h = 1480, 380
    parts = [
        f'<text x="{w/2}" y="36" text-anchor="middle" class="label-sub" font-size="15">{_esc(banner)}</text>',
    ]
    row1, row2 = cells[:4], cells[4:]
    for row_i, row in enumerate((row1, row2)):
        n = len(row)
        card_w = 300 if row_i == 0 else 320
        total = n * card_w + (n - 1) * 24
        start = (w - total) / 2
        cy = 130 if row_i == 0 else 280
        for j, (eye, ask, reject) in enumerate(row):
            cx = start + card_w / 2 + j * (card_w + 24)
            parts.append(card(cx, cy, card_w, 110, eye, ask, [reject], focal=(j == 0 and row_i == 0)))
    parts.append(
        f'<text x="{w/2}" y="355" text-anchor="middle" class="label-accent" font-size="14">{_esc(foot)}</text>'
    )
    return svg_shell(w, h, "\n".join(parts), title, corner)


def fix_loop(zh: bool) -> str:
    """Write → check → report → pass/fail → fix & retry or ready to use."""
    ok = "#1B7A4E"
    bad = "#B42318"
    ok_bg = "#F0Faf4"
    bad_bg = "#FFF5F5"
    if zh:
        banner = "自检闭环：写好 → 跑检查 → 看报告 → 不过就改，改完再检"
        steps = [
            ("1", "写好 Skill", "按自己的流程先写", False),
            ("2", "交给 AI / 安装", "把仓库地址发给写 Skill 的 AI", False),
            ("3", "跑硬门槛", "python hard_gates.py …", True),
            ("4", "出报告", "分数 + 修改意见", False),
        ]
        decision = ("过门槛了吗？", "看 ship floor / Critical")
        fix = ("按意见改", "先改 Critical，再说「按意见改」")
        ship = ("可以真用了", "绿灯过了再推广")
        bottom = [
            ("结构过关", "basic_usable ≥ 4", "绿灯"),
            ("说清楚查什么", "contract_clarity", "黄灯"),
            ("有出口证据", "Verification / Done when", "验收"),
        ]
        legend = [("主流程", ACCENT), ("通过", ok), ("改完再检", bad)]
        title = "skill-self-check.app -> docs -> fix-loop.svg"
        corner = "06 · 改完再检"
    else:
        banner = "Self-check loop: write → run gates → report → fix & retry or ship"
        steps = [
            ("1", "Write Skill", "Your usual drafting flow", False),
            ("2", "Hand to AI / install", "Paste the GitHub URL to your AI", False),
            ("3", "Run hard gates", "python hard_gates.py …", True),
            ("4", "Read report", "Scores + ranked fixes", False),
        ]
        decision = ("Ship floor met?", "Critical count → zero?")
        fix = ("Apply fixes", "Fix Criticals, then say “apply fixes”")
        ship = ("Ready to use", "Both lights on before rollout")
        bottom = [
            ("Structure OK", "basic_usable ≥ 4", "green light"),
            ("Scope clear", "contract_clarity", "amber light"),
            ("Exit evidence", "Verification / Done when", "proof"),
        ]
        legend = [("Main flow", ACCENT), ("Success", ok), ("Fix & retry", bad)]
        title = "skill-self-check.app -> docs -> fix-loop.svg"
        corner = "06 · fix & retry"

    w, h = 1480, 560
    parts = [
        f'<text x="{w/2}" y="32" text-anchor="middle" class="label-sub" font-size="15">{_esc(banner)}</text>',
    ]

    # Top row of 4 steps (slightly left so the decision row has room)
    card_w, card_h = 240, 100
    gap = 28
    total = 4 * card_w + 3 * gap
    start = 80
    y1 = 110
    centers = []
    for i, (eye, t, sub, focal) in enumerate(steps):
        cx = start + card_w / 2 + i * (card_w + gap)
        centers.append(cx)
        parts.append(card(cx, y1, card_w, card_h, eye, t, [sub], focal=focal))
        if i < 3:
            x1 = cx + card_w / 2
            x2 = start + card_w / 2 + (i + 1) * (card_w + gap) - card_w / 2
            parts.append(
                f'<line x1="{x1:.1f}" y1="{y1}" x2="{x2 - 10:.1f}" y2="{y1}" '
                f'stroke="{BOX_BORDER}" stroke-width="2"/>'
                f'<polygon points="{x2:.1f},{y1} {x2 - 12:.1f},{y1 - 5} {x2 - 12:.1f},{y1 + 5}" fill="{ACCENT}"/>'
            )

    # Decision under step 4, then Fix left / Ship right (no overlap)
    dx, dy = centers[3], 280
    size = 64
    parts.append(
        f'<line x1="{centers[3]:.1f}" y1="{y1 + card_h / 2:.1f}" x2="{dx}" y2="{dy - size}" '
        f'stroke="{BOX_BORDER}" stroke-width="2"/>'
    )
    parts.append(
        f'<polygon points="{dx},{dy - size} {dx + size},{dy} {dx},{dy + size} {dx - size},{dy}" '
        f'fill="{BOX_FOCAL}" stroke="{ACCENT}" stroke-width="1.6"/>'
    )
    parts.append(
        f'<text x="{dx}" y="{dy - 6}" text-anchor="middle" class="label" font-size="13">{_esc(decision[0])}</text>'
    )
    parts.append(
        f'<text x="{dx}" y="{dy + 14}" text-anchor="middle" class="label-tiny" font-size="11">{_esc(decision[1])}</text>'
    )

    fix_cx, fix_cy = 300, 280
    fix_w, fix_h = 280, 96
    parts.append(
        f'<rect x="{fix_cx - fix_w / 2:.1f}" y="{fix_cy - fix_h / 2:.1f}" width="{fix_w}" height="{fix_h}" rx="2" '
        f'fill="{bad_bg}" stroke="{bad}" stroke-width="1.6"/>'
    )
    parts.append(
        f'<text x="{fix_cx}" y="{fix_cy - 10:.1f}" text-anchor="middle" class="label" font-size="17" '
        f'fill="{bad}">{_esc(fix[0])}</text>'
    )
    parts.append(
        f'<text x="{fix_cx}" y="{fix_cy + 18:.1f}" text-anchor="middle" class="label-tiny" font-size="12">{_esc(fix[1])}</text>'
    )
    no_label = "否 / 有 Critical" if zh else "No / Criticals"
    fix_right = fix_cx + fix_w / 2
    parts.append(
        f'<line x1="{dx - size}" y1="{dy}" x2="{fix_right + 12:.1f}" y2="{fix_cy}" '
        f'stroke="{bad}" stroke-width="2"/>'
        f'<polygon points="{fix_right:.1f},{fix_cy} {fix_right + 12:.1f},{fix_cy - 5} '
        f'{fix_right + 12:.1f},{fix_cy + 5}" fill="{bad}"/>'
    )
    parts.append(
        f'<text x="{(dx - size + fix_right) / 2:.1f}" y="{dy - 14}" text-anchor="middle" '
        f'fill="{bad}" font-size="12" class="label-tiny">{_esc(no_label)}</text>'
    )
    # dashed retry back to step 3
    parts.append(
        f'<path d="M {fix_cx} {fix_cy - fix_h / 2:.1f} '
        f'C {fix_cx} 175, {centers[2]:.1f} 175, {centers[2]:.1f} {y1 + card_h / 2:.1f}" '
        f'fill="none" stroke="{bad}" stroke-width="1.6" stroke-dasharray="6 4"/>'
    )
    retry = "再跑一遍 →" if zh else "run again →"
    parts.append(
        f'<text x="{(fix_cx + centers[2]) / 2:.1f}" y="172" text-anchor="middle" fill="{bad}" '
        f'font-size="12" class="label-tiny">{_esc(retry)}</text>'
    )

    ship_cx, ship_cy = 1320, 280
    ship_w, ship_h = 260, 96
    parts.append(
        f'<rect x="{ship_cx - ship_w / 2:.1f}" y="{ship_cy - ship_h / 2:.1f}" width="{ship_w}" height="{ship_h}" rx="2" '
        f'fill="{ok_bg}" stroke="{ok}" stroke-width="1.6"/>'
    )
    parts.append(
        f'<text x="{ship_cx}" y="{ship_cy - 10:.1f}" text-anchor="middle" class="label" font-size="17" '
        f'fill="{ok}">{_esc(ship[0])}</text>'
    )
    parts.append(
        f'<text x="{ship_cx}" y="{ship_cy + 18:.1f}" text-anchor="middle" class="label-tiny" font-size="12">{_esc(ship[1])}</text>'
    )
    yes_label = "是 / 无 Critical" if zh else "Yes / clear"
    ship_left = ship_cx - ship_w / 2
    parts.append(
        f'<line x1="{dx + size}" y1="{dy}" x2="{ship_left - 12:.1f}" y2="{ship_cy}" '
        f'stroke="{ok}" stroke-width="2"/>'
        f'<polygon points="{ship_left:.1f},{ship_cy} {ship_left - 12:.1f},{ship_cy - 5} '
        f'{ship_left - 12:.1f},{ship_cy + 5}" fill="{ok}"/>'
    )
    parts.append(
        f'<text x="{(dx + size + ship_left) / 2:.1f}" y="{dy - 14}" text-anchor="middle" '
        f'fill="{ok}" font-size="12" class="label-tiny">{_esc(yes_label)}</text>'
    )

    parts.append(
        f'<text x="{w/2}" y="400" text-anchor="middle" class="label-tiny" font-size="13">'
        f'{_esc("报告里重点看这三项" if zh else "Three things the report always covers")}</text>'
    )
    bw, bgap = 360, 40
    btotal = 3 * bw + 2 * bgap
    bstart = (w - btotal) / 2
    for i, (t, sub, tag) in enumerate(bottom):
        cx = bstart + bw / 2 + i * (bw + bgap)
        x = cx - bw / 2
        y = 420
        parts.append(
            f'<rect x="{x:.1f}" y="{y}" width="{bw}" height="72" rx="2" '
            f'fill="{BOX}" stroke="{BOX_BORDER}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y + 28}" text-anchor="middle" class="label" font-size="15">{_esc(t)}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y + 52}" text-anchor="middle" class="label-tiny mono" font-size="12">'
            f'{_esc(sub)} · {_esc(tag)}</text>'
        )

    for i, (lab, color) in enumerate(legend):
        x = 40 + i * 160
        parts.append(f'<line x1="{x}" y1="530" x2="{x + 28}" y2="530" stroke="{color}" stroke-width="3"/>')
        parts.append(
            f'<text x="{x + 36}" y="534" class="label-tiny" font-size="12">{_esc(lab)}</text>'
        )

    return svg_shell(w, h, "\n".join(parts), title, corner)


def three_lights(zh: bool) -> str:
    if zh:
        banner = "自检看三盏灯 — 给老板的读法"
        cards = [
            (190, "BASIC", "绿灯：能不能上手", ["结构过关", "可以先真用"], True),
            (550, "CONTRACT", "黄灯：说清楚了吗", ["何时用 / 不用", "检查轴 + 验收"], False),
            (910, "KIT", "蓝灯：配套齐了吗", ["资料 / 案例", "落地记忆 / 脚本"], False),
        ]
        mid = (
            "绿灯不亮 → 先改，别推广\n"
            "绿灯亮、黄/蓝暗 → 能用，但容易各做各的或不好交接\n"
            "三盏都亮 → 可以放心推广\n"
            "蓝灯 N/A 不算缺（声明不适用即可）"
        )
        title = "skill-self-check.app -> docs -> three-lights.svg"
        corner = "05 · 三盏灯"
    else:
        banner = "Three lights for bosses — how to read a self-check"
        cards = [
            (190, "BASIC", "Green: usable now?", ["Structure OK", "Safe to try"], True),
            (550, "CONTRACT", "Amber: scope clear?", ["When / when not", "Axes + proof"], False),
            (910, "KIT", "Blue: kit complete?", ["Refs / examples", "Memory / scripts"], False),
        ]
        mid = (
            "Green off → fix before rollout\n"
            "Green on, amber/blue dim → usable but drift/handoff risk\n"
            "All three on → ready to share\n"
            "Blue N/A does not dock (declare when not applicable)"
        )
        title = "skill-self-check.app -> docs -> three-lights.svg"
        corner = "05 · three lights"

    w, h = 1100, 420
    parts = [
        f'<text x="{w/2}" y="36" text-anchor="middle" class="label-sub" font-size="15">{_esc(banner)}</text>',
    ]
    for cx, eyebrow, title_txt, lines, focal in cards:
        parts.append(card(cx, 160, 300, 150, eyebrow, title_txt, lines, focal=focal))
    parts.append(arrow_h(340, 160, 400))
    parts.append(arrow_h(700, 160, 760))
    for i, line in enumerate(mid.split("\n")):
        parts.append(
            f'<text x="{w/2}" y="{290 + i * 22}" text-anchor="middle" class="label-tiny" '
            f'font-size="13">{_esc(line)}</text>'
        )
    return svg_shell(w, h, "\n".join(parts), title, corner)


def main() -> None:
    pairs = [
        ("01-how-to-use.svg", how_to_use),
        ("02-pdca.svg", pdca),
        ("03-smart.svg", smart),
        ("04-5w2h.svg", five_w2h),
        ("05-three-lights.svg", three_lights),
        ("06-fix-loop.svg", fix_loop),
    ]
    for name, fn in pairs:
        write(OUT / name, fn(False))
        write(OUT_ZH / name, fn(True))
    print("done")


if __name__ == "__main__":
    main()
