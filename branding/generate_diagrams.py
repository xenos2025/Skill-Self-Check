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
            ("第 3 步", "看两盏灯", ["能不能上手用", "有没有说清楚查什么"], False),
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
            ("STEP 3", "Read two lights", ["Usable now?", "Scope clear?"], False),
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


def two_lights(zh: bool) -> str:
    if zh:
        banner = "自检只看两盏灯 — 给老板的读法"
        left = ("绿灯：能不能上手", ["结构过关", "可以先真用", "边用边改细节"], True)
        right = ("黄灯：说清楚了吗", ["查什么写清楚了吗", "什么时候用 / 不用", "验收有没有证据"], False)
        mid = "两盏都亮 → 放心推广\n绿灯亮、黄灯暗 → 能用但容易各做各的\n绿灯不亮 → 先改，别急着推广"
        title = "skill-self-check.app -> docs -> two-lights.svg"
        corner = "05 · 两盏灯"
    else:
        banner = "Two lights for bosses — how to read a self-check"
        left = ("Green: usable now?", ["Structure OK", "Safe to try in real work", "Polish while using"], True)
        right = ("Amber: scope clear?", ["Named check axes", "When / when not", "Proof of done"], False)
        mid = "Both on → ready to share\nGreen only → usable but drift risk\nGreen off → fix before rollout"
        title = "skill-self-check.app -> docs -> two-lights.svg"
        corner = "05 · two lights"

    w, h = 1100, 380
    parts = [
        f'<text x="{w/2}" y="36" text-anchor="middle" class="label-sub" font-size="15">{_esc(banner)}</text>',
        card(280, 170, 320, 160, "BASIC", left[0], left[1], focal=left[2]),
        card(820, 170, 320, 160, "CONTRACT", right[0], right[1], focal=right[2]),
        arrow_h(440, 170, 660),
    ]
    for i, line in enumerate(mid.split("\n")):
        parts.append(
            f'<text x="{w/2}" y="{300 + i * 22}" text-anchor="middle" class="label-tiny" '
            f'font-size="14">{_esc(line)}</text>'
        )
    return svg_shell(w, h, "\n".join(parts), title, corner)


def main() -> None:
    pairs = [
        ("01-how-to-use.svg", how_to_use),
        ("02-pdca.svg", pdca),
        ("03-smart.svg", smart),
        ("04-5w2h.svg", five_w2h),
        ("05-two-lights.svg", two_lights),
    ]
    for name, fn in pairs:
        write(OUT / name, fn(False))
        write(OUT_ZH / name, fn(True))
    print("done")


if __name__ == "__main__":
    main()
