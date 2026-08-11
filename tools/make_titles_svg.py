"""
Lecture note TITLE generator (SVG)
----------------------------------
Builds cover and unit-header graphics. Edit CONFIG, run, get .svg files.
Runs in Colab as-is. No external packages.
"""

import os

# ============================================================
# CONFIG
# ============================================================

OUT_DIR = "."
FONT = "Roboto, Arial, Helvetica, sans-serif"
WIDTH = 900

C_COURSE = "#0C447C"
C_WEEK   = "#0F6E56"
C_WEEK_BG= "#E1F5EE"
C_UNIT   = "#0C447C"
C_UNIT_BG= "#E6F1FB"
C_UNIT_TX= "#185FA5"
C_META   = "#8A8880"
C_RULE   = "#E3E3E0"

COVER = dict(
    course="AI Programming Fundamentals",
    week_no="W01",
    week_title="Course Overview",
    meta="youngah2026@iscu.ac.kr",
    filename="w01_cover.svg",
)

UNITS = [
    (1, "Course Plan",                       "w01_unit1.svg"),
    (2, "Introduction to Python and Colab",  "w01_unit2.svg"),
    (3, "Getting Started with Colab",        "w01_unit3.svg"),
    (4, "Key Takeaways",                     "w01_unit4.svg"),
]

# Latin ~0.55, Hangul ~0.98. Raise this if your titles are in Korean.
CHAR_W = 0.55


# ============================================================
# BUILDERS
# ============================================================

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def width_of(s, size):
    w = 0.0
    for ch in s:
        w += size * (0.98 if ord(ch) > 0x1100 else CHAR_W)
    return w


def warn(s, size, box, where):
    est = width_of(s, size)
    if est > box:
        print(f"  ! overflows: {where!r} (~{int(est)}px of {int(box)}px)")


def txt(x, y, s, size, fill, weight="400", spacing=None, anchor=None):
    a = f' font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}"'
    if spacing:
        a += f' letter-spacing="{spacing}"'
    if anchor:
        a += f' text-anchor="{anchor}"'
    return f'<text x="{x}" y="{y}"{a}>{esc(s)}</text>'


def build_cover(cfg, w=WIDTH, h=190):
    course, wk, wt, meta = cfg["course"], cfg["week_no"], cfg["week_title"], cfg["meta"]
    warn(course, 40, w - 40, course)

    badge_w = width_of(wk, 17) + 30
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    p.append(f'<rect x="0" y="0" width="{w}" height="6" fill="{C_COURSE}"/>')
    p.append(txt(0, 78, course, 40, C_COURSE, "700"))
    p.append(f'<rect x="0" y="102" width="{badge_w:.0f}" height="32" rx="4" fill="{C_WEEK}"/>')
    p.append(txt(badge_w / 2, 124, wk, 17, "#FFFFFF", "700", anchor="middle"))
    p.append(txt(badge_w + 14, 126, wt, 26, C_WEEK, "700"))
    p.append(txt(w - 6, 168, meta, 14, C_META, anchor="end"))
    p.append(f'<rect x="0" y="182" width="{w}" height="1" fill="{C_RULE}"/>')
    p.append('</svg>')
    return "\n".join(p)


def build_unit(n, title, w=WIDTH, h=76):
    badge = 52
    warn(title, 27, w - badge - 30, title)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    p.append(f'<rect x="0" y="0" width="{w}" height="{h - 6}" fill="{C_UNIT_BG}"/>')
    p.append(f'<rect x="0" y="0" width="{badge}" height="{h - 6}" fill="{C_UNIT}"/>')
    p.append(txt(badge / 2, 46, str(n), 30, "#FFFFFF", "700", anchor="middle"))
    p.append(txt(badge + 22, 46, title, 27, C_UNIT_TX, "700"))
    p.append(f'<rect x="0" y="{h - 6}" width="{w}" height="4" fill="{C_UNIT}"/>')
    p.append('</svg>')
    return "\n".join(p)


def write(name, svg):
    path = os.path.join(OUT_DIR, name)
    open(path, "w", encoding="utf-8").write(svg)
    print(f"wrote {path}  ({len(svg)} bytes)")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"[{COVER['filename']}]")
    write(COVER["filename"], build_cover(COVER))
    for n, title, fname in UNITS:
        print(f"[{fname}]")
        write(fname, build_unit(n, title))
    print("\ndone. In Colab:  from google.colab import files; files.download('w01_cover.svg')")
