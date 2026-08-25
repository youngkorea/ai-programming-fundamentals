"""Week cover + unit banner SVGs, matching the Week 01 files byte-for-byte in style.

    cd img && python ../tools/make_week_svg.py
"""

import os

OUT_DIR = "."
FONT = "Roboto, Arial, Helvetica, sans-serif"
W = 900

NAVY   = "#0C447C"
BADGE  = "#0F6E56"
PALEBL = "#E6F1FB"
MIDBL  = "#185FA5"
SUBTL  = "#B5D4F4"
META   = "#85B7EB"
WHITE  = "#FFFFFF"

COURSE = "AI Programming Fundamentals"
EMAIL  = "youngah2026@iscu.ac.kr"
BOLD   = 1.14          # bold glyphs run wider than the plain estimate
CHAR_W = 0.55          # latin; hangul handled separately

# ---- edit below -------------------------------------------------------------

WEEKS = {
    "w02": ("W02", "Data Types and Variables", [
        (1, "Python Objects and Basic Data Types"),
        (2, "Boolean Type and Expressions"),
        (3, "Variables and Type Conversion"),
        (4, "Key Takeaways"),
    ]),
}

# -----------------------------------------------------------------------------


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def width_of(s, size):
    return sum(size * (0.98 if ord(c) > 0x1100 else CHAR_W) for c in s)


def fit(text, target, box):
    size = target
    while size > 12 and width_of(text, size) * BOLD > box:
        size -= 1
    if size < target:
        print(f"  ~ shrunk to {size}px to fit: {text!r}")
    return size


def txt(x, y, s, size, fill, weight="400", anchor=None):
    a = f' font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}"'
    if anchor:
        a += f' text-anchor="{anchor}"'
    return f'<text x="{x}" y="{y}"{a}>{esc(s)}</text>'


def build_cover(week_no, week_title, w=W, h=222):
    size = fit(COURSE, 49, w - 68)
    badge_w = width_of(week_no, 17) + 30
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
         f'<rect x="0" y="0" width="{w}" height="{h}" rx="8" fill="{NAVY}"/>',
         txt(34, 104, COURSE, size, WHITE, "700"),
         f'<rect x="34" y="134" width="{badge_w:.0f}" height="32" rx="4" fill="{BADGE}"/>',
         txt(34 + badge_w / 2, 156, week_no, 17, WHITE, "700", "middle"),
         txt(34 + badge_w + 14, 160, week_title, fit(week_title, 32, w - 200), SUBTL, "700"),
         txt(w - 34, 200, EMAIL, 14, META, anchor="end"),
         '</svg>']
    return "\n".join(p)


def unit_size(titles, w=W, badge=68):
    """One size for every banner in a week, so the set reads as a set."""
    return min(fit(t, 48, w - badge - 40) for t in titles)


def build_unit(n, title, size, w=W, h=96):
    badge, r = 68, 6
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
         f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="{PALEBL}"/>',
         f'<rect x="1" y="1" width="{badge}" height="{h - 2}" rx="{r}" fill="{NAVY}"/>',
         f'<rect x="{badge - r + 1}" y="1" width="{r}" height="{h - 2}" fill="{NAVY}"/>',
         txt(badge / 2 + 1, h / 2 + 17, str(n), 46, WHITE, "700", "middle"),
         txt(badge + 26, h / 2 + 17, title, size, MIDBL, "700"),
         f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="none" '
         f'stroke="{NAVY}" stroke-width="1.5"/>',
         '</svg>']
    return "\n".join(p)


def write(name, svg):
    path = os.path.join(OUT_DIR, name)
    open(path, "w", encoding="utf-8").write(svg)
    print(f"wrote {path}  ({len(svg)} bytes)")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for prefix, (no, title, units) in WEEKS.items():
        print(f"[{prefix}_cover.svg]")
        write(f"{prefix}_cover.svg", build_cover(no, title))
        size = unit_size([u[1] for u in units])
        print(f"  banner title size for {prefix}: {size}px (uniform)")
        for n, ut in units:
            print(f"[{prefix}_unit{n}.svg]")
            write(f"{prefix}_unit{n}.svg", build_unit(n, ut, size))
