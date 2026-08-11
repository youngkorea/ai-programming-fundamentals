"""
Lecture note FIGURE generator (SVG)
-----------------------------------
Body-content graphics: card grids, numbered steps, side-by-side comparisons.
Text wraps automatically, so you edit copy without touching coordinates.

    cd img && python ../tools/make_figures_svg.py
"""

import os

OUT_DIR = "."
FONT = "Roboto, Arial, Helvetica, sans-serif"
W = 900

NAVY   = "#0C447C"
BLUE   = "#185FA5"
MID    = "#378ADD"
PALE   = "#E6F1FB"
TINT   = "#F4F9FE"
BODY   = "#3D3D3A"
MUTED  = "#73726C"
RULE   = "#D6E4F3"
GREEN  = "#3B6D11"
RED    = "#A32D2D"

CHAR_W = 0.55        # latin; hangul handled separately


# ---------------- text helpers ----------------

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def width_of(s, size):
    return sum(size * (0.98 if ord(c) > 0x1100 else CHAR_W) for c in s)


def txt(x, y, s, size, fill, weight="400", anchor=None, spacing=None):
    a = f' font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}"'
    if anchor:
        a += f' text-anchor="{anchor}"'
    if spacing:
        a += f' letter-spacing="{spacing}"'
    return f'<text x="{x:.0f}" y="{y:.0f}"{a}>{esc(s)}</text>'


def wrap(s, size, max_w):
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if width_of(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(x, y, s, size, fill, max_w, leading=None, weight="400"):
    """Wrapped paragraph. Returns (svg, bottom_y)."""
    leading = leading or size * 1.5
    lines = wrap(s, size, max_w)
    out = [f'<text x="{x:.0f}" y="{y:.0f}" font-family="{FONT}" font-size="{size}" '
           f'font-weight="{weight}" fill="{fill}">']
    for i, ln in enumerate(lines):
        dy = "0" if i == 0 else f"{leading:.0f}"
        out.append(f'<tspan x="{x:.0f}" dy="{dy}">{esc(ln)}</tspan>')
    out.append('</text>')
    return "\n".join(out), y + leading * (len(lines) - 1)


def svg(w, h, parts):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h:.0f}" '
            f'viewBox="0 0 {w} {h:.0f}">\n' + "\n".join(parts) + "\n</svg>")


# ---------------- figure builders ----------------

def cards(items, cols=3, numbered=False, w=W):
    """items: list of (title, body). Returns svg string."""
    gap, pad = 14, 18
    cw = (w - gap * (cols - 1)) / cols
    rows = (len(items) + cols - 1) // cols
    inner = cw - pad * 2

    heights = []
    for t, b in items:
        n_t = len(wrap(t, 17, inner))
        n_b = len(wrap(b, 14, inner)) if b else 0
        heights.append(pad + (28 if numbered else 0) + n_t * 24 + (8 if b else 0) + n_b * 21 + pad)
    row_h = [max(heights[r * cols:(r + 1) * cols]) for r in range(rows)]

    parts, y = [], 0.0
    for r in range(rows):
        h = row_h[r]
        for c in range(cols):
            i = r * cols + c
            if i >= len(items):
                break
            t, b = items[i]
            x = c * (cw + gap)
            parts.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{cw:.0f}" height="{h:.0f}" '
                         f'rx="6" fill="{TINT}" stroke="{RULE}" stroke-width="1"/>')
            ty = y + pad + 18
            if numbered:
                parts.append(f'<circle cx="{x + pad + 12:.0f}" cy="{y + pad + 10:.0f}" r="12" fill="{BLUE}"/>')
                parts.append(txt(x + pad + 12, y + pad + 15, str(i + 1), 14, "#FFFFFF", "700", anchor="middle"))
                ty = y + pad + 48
            s, ty = block(x + pad, ty, t, 17, NAVY, inner, 24, "700")
            parts.append(s)
            if b:
                s, _ = block(x + pad, ty + 25, b, 14, BODY, inner, 21)
                parts.append(s)
        y += h + gap
    return svg(w, y - gap, parts)


def steps(items, w=W):
    """items: list of (title, body) rendered as a numbered vertical flow."""
    pad, gap, badge = 18, 12, 44
    inner = w - badge - pad * 3
    parts, y = [], 0.0
    for i, (t, b) in enumerate(items, 1):
        n_t = len(wrap(t, 18, inner))
        n_b = len(wrap(b, 14, inner)) if b else 0
        h = pad + n_t * 25 + (6 if b else 0) + n_b * 21 + pad
        parts.append(f'<rect x="0" y="{y:.0f}" width="{w}" height="{h:.0f}" rx="6" fill="{TINT}" '
                     f'stroke="{RULE}" stroke-width="1"/>')
        parts.append(f'<rect x="0" y="{y:.0f}" width="{badge}" height="{h:.0f}" rx="6" fill="{BLUE}"/>')
        parts.append(f'<rect x="{badge - 8}" y="{y:.0f}" width="8" height="{h:.0f}" fill="{BLUE}"/>')
        parts.append(txt(badge / 2, y + h / 2 + 8, str(i), 24, "#FFFFFF", "700", anchor="middle"))
        ty = y + pad + 18
        s, ty = block(badge + pad, ty, t, 18, NAVY, inner, 25, "700")
        parts.append(s)
        if b:
            s, _ = block(badge + pad, ty + 25, b, 14, BODY, inner, 21)
            parts.append(s)
        y += h + gap
    return svg(w, y - gap, parts)


def compare(left, right, rows, w=W):
    """left/right: (title, badge_text or None). rows: (label, left_ok, left_txt, right_ok, right_txt)."""
    gap = 14
    cw = (w - gap) / 2
    head_h, row_h, pad = 54, 46, 18
    h = head_h + row_h * len(rows) + 10

    parts = []
    for idx, (col, (title, badge)) in enumerate([(0, left), (1, right)]):
        x = idx * (cw + gap)
        fill = PALE if idx == 1 else TINT
        parts.append(f'<rect x="{x:.0f}" y="0" width="{cw:.0f}" height="{h:.0f}" rx="6" '
                     f'fill="{fill}" stroke="{RULE}" stroke-width="1"/>')
        parts.append(f'<rect x="{x:.0f}" y="0" width="{cw:.0f}" height="4" '
                     f'fill="{BLUE if idx == 1 else MUTED}"/>')
        parts.append(txt(x + pad, 36, title, 20, NAVY if idx == 1 else BODY, "700"))
        if badge:
            bw = width_of(badge, 12) + 22
            parts.append(f'<rect x="{x + cw - pad - bw:.0f}" y="18" width="{bw:.0f}" height="22" rx="11" fill="{BLUE}"/>')
            parts.append(txt(x + cw - pad - bw / 2, 34, badge, 12, "#FFFFFF", "700", anchor="middle"))

    for r, (label, lok, ltxt, rok, rtxt) in enumerate(rows):
        y = head_h + r * row_h
        for idx, (ok, val) in enumerate([(lok, ltxt), (rok, rtxt)]):
            x = idx * (cw + gap)
            parts.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{cw:.0f}" height="1" fill="{RULE}"/>')
            mark, colour = ("\u2713", GREEN) if ok else ("\u2715", RED)
            parts.append(txt(x + pad, y + 30, mark, 15, colour, "700"))
            parts.append(txt(x + pad + 22, y + 22, label, 12, MUTED, "700"))
            parts.append(txt(x + pad + 22, y + 38, val, 14, BODY))
    return svg(w, h, parts)


# ---------------- figures ----------------

FIGURES = {}

FIGURES["w01_python_stack.svg"] = cards([
    ("NumPy", "High-performance numerical computing. Arrays and vectorised maths underneath almost every "
              "data library."),
    ("Pandas", "Data processing and analysis. Tables, filtering, grouping, joining, and reading files."),
    ("Matplotlib / Seaborn", "Data visualization. Charts for exploring data and for presenting results."),
], cols=3)

FIGURES["w01_why_python.svg"] = cards([
    ("Readable syntax", "Concise and intuitive. A variable is named total_price rather than x."),
    ("Versatility", "Web development, data analysis, artificial intelligence, game development, and more."),
    ("Strong community", "A vast set of open-source libraries and active support."),
    ("High productivity", "Students accomplish a great deal with little code."),
    ("Industry demand", "Employers ask for Python across many roles, including data scientist and "
                        "software developer."),
], cols=3)

FIGURES["w01_objectives.svg"] = cards([
    ("Explain", "Why Python is the dominant language in data analysis and artificial intelligence."),
    ("Identify", "The equipment required for coursework and exams."),
    ("Compare", "Jupyter Notebook and Colab, and select Colab as the practice environment."),
    ("Create", "A Colab notebook, then write, run, and comment a first Python program."),
], cols=4, numbered=True)

FIGURES["w01_getting_started.svg"] = steps([
    ("Create a Google account",
     "Go to accounts.google.com and click Create account. Skip this step if you already have one."),
    ("Open the Google Colab website",
     "colab.google"),
    ("Create or open a notebook",
     "Click + New notebook to start fresh. Or click Upload, then Browse, to select a notebook file such "
     "as AIProgrammingFundamentals_Week01.ipynb."),
])

FIGURES["w01_jupyter_vs_colab.svg"] = compare(
    ("Jupyter Notebook", None),
    ("Google Colab", "WE USE THIS"),
    [("Installation", False, "Required", True, "Not required"),
     ("Internet connection", True, "Works offline", False, "Required"),
     ("Computing resources", False, "Local machine only", True, "GPU and TPU, free or paid"),
     ("Environment setup", False, "Version management", True, "Not required by default")],
)

FIGURES["w01_takeaways.svg"] = cards([
    ("Course goals", "Learn basic Python syntax and concepts for data analysis and AI modeling, and build "
                     "hands-on programming skills."),
    ("Requirements", "A computer that runs Python. Mobile devices are not recommended, and a separate "
                     "coding computer is required for the exams."),
    ("Why Python", "A rich library ecosystem, readable syntax, a strong community, and compatibility with "
                   "machine learning frameworks."),
    ("Why Colab", "No installation, free access to GPU and TPU resources, and the same environment for "
                  "every student."),
    ("First steps", "Create a notebook, run a cell, add cells, declare variables, run arithmetic, and "
                    "comment code."),
], cols=3)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, s in FIGURES.items():
        path = os.path.join(OUT_DIR, name)
        open(path, "w", encoding="utf-8").write(s)
        print(f"wrote {path}  ({len(s)} bytes)")
