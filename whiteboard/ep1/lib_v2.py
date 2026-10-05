"""Helpers for v2 whiteboard scene SVGs. Absolute path commands only (M L C Q Z)."""
import math, os, re

STYLE = """  <style>
    .line{stroke:#1f1f1f;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}
    .detail{stroke:#1f1f1f;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
    .hatch{stroke:#1f1f1f;stroke-width:0.9;stroke-linecap:round;stroke-linejoin:round;opacity:.75}
    .line:not([fill]),.detail:not([fill]),.hatch:not([fill]){fill:none}
  </style>
"""
GOLD, ORANGE, RUST, CLOAK, BLUE = "#dcb874", "#e3922f", "#c9652f", "#c98a6a", "#9dbad0"


def f1(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def _el(cls, d, fill=None, accent=False):
    f = f' fill="{fill}"' if fill else ""
    st = ' style="mix-blend-mode:multiply"' if accent else ""
    return f'  <path class="{cls}"{f}{st} d="{d}"/>\n'


def L(d, fill=None, accent=False): return _el("line", d, fill, accent)
def D(d, fill=None, accent=False): return _el("detail", d, fill, accent)
def H(d): return _el("hatch", d)


def svg(body, comment=""):
    c = f"  <!-- {comment} -->\n" if comment else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900">\n{c}{STYLE}{body}</svg>\n'


TOK = re.compile(r"[MLCQZ]|-?\d*\.?\d+(?:e-?\d+)?")


def tx(d, s=1.0, dx=0.0, dy=0.0, rot=0.0, sx=None, sy=None, ox=0.0, oy=0.0):
    """scale (sx,sy) about origin after subtracting (ox,oy), rotate rot deg, translate (dx,dy)."""
    sx = s if sx is None else sx
    sy = s if sy is None else sy
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out, nums = [], []
    for t in TOK.findall(d):
        if t.isalpha():
            out.append(t)
        else:
            nums.append(float(t))
            if len(nums) == 2:
                x, y = (nums[0] - ox) * sx, (nums[1] - oy) * sy
                x, y = x * c - y * sn, x * sn + y * c
                out.append(f"{f1(x + dx)} {f1(y + dy)}")
                nums = []
    return " ".join(out)


def ellipse(cx, cy, rx, ry, start_deg=-90, sweep=360, rot=0):
    segs = max(1, int(math.ceil(abs(sweep) / 90.0)))
    da = math.radians(sweep) / segs
    k = 4.0 / 3.0 * math.tan(da / 4)
    a = math.radians(start_deg)
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    R = lambda x, y: (cx + x * cr - y * sr, cy + x * sr + y * cr)
    P = lambda a: (rx * math.cos(a), ry * math.sin(a))
    T = lambda a: (-rx * math.sin(a), ry * math.cos(a))
    x0, y0 = P(a); X0 = R(x0, y0)
    d = f"M {f1(X0[0])} {f1(X0[1])}"
    for _ in range(segs):
        a1 = a + da
        x1, y1 = P(a1); t0 = T(a); t1 = T(a1)
        c1 = R(x0 + k * t0[0], y0 + k * t0[1]); c2 = R(x1 - k * t1[0], y1 - k * t1[1]); e = R(x1, y1)
        d += f" C {f1(c1[0])} {f1(c1[1])} {f1(c2[0])} {f1(c2[1])} {f1(e[0])} {f1(e[1])}"
        a, x0, y0 = a1, x1, y1
    return d


def circle(cx, cy, r, start_deg=-90, sweep=360):
    return ellipse(cx, cy, r, r, start_deg, sweep)


def smooth(pts, closed=False, t=0.5):
    """Catmull-Rom through points -> cubic bezier path."""
    P = list(pts)
    P = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    d = f"M {f1(P[1][0])} {f1(P[1][1])}"
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d += f" C {f1(c1[0])} {f1(c1[1])} {f1(c2[0])} {f1(c2[1])} {f1(p2[0])} {f1(p2[1])}"
    return d + (" Z" if closed else "")


def hatch_lines(x0, y0, x1, y1, n, dx=0, dy=0):
    """n parallel strokes from (x0,y0)-(x1,y1), each offset by (dx,dy)."""
    return " ".join(f"M {f1(x0+i*dx)} {f1(y0+i*dy)} L {f1(x1+i*dx)} {f1(y1+i*dy)}" for i in range(n))


def check_paths(svgtext):
    """Raise if the file breaks the format rules. Returns (n_line, n_detail, n_hatch)."""
    bad = re.findall(r"<(circle|rect|ellipse|text|use|g|polygon|polyline|line|image)\b", svgtext)
    if bad:
        raise ValueError(f"disallowed elements: {set(bad)}")
    for d in re.findall(r' d="([^"]+)"', svgtext):
        if re.search(r"[a-zA-Z]", re.sub(r"[MLCQZe]", "", d)):
            raise ValueError("non M/L/C/Q/Z command in: " + d[:80])
    if "transform=" in svgtext:
        raise ValueError("transform attribute not allowed")
    return tuple(len(re.findall(f'class="{c}"', svgtext)) for c in ("line", "detail", "hatch"))


def write(path, text):
    print(path, "line/detail/hatch =", check_paths(text))
    open(path, "w").write(text)
