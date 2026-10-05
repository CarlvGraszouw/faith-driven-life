"""Drawing kit for scenes a06-trap, a10-whose-image, b02-whose-face (v2 art).

Pure-python helpers on top of lib_v2 (absolute M/L/C/Q/Z paths only):
  * PB          - path builder (moves, lines, Catmull-Rom runs, cubic curves)
  * hatch()     - parallel hatching clipped to a polygon, drawn as continuous
                  back-and-forth strokes (few pen lifts -> fast to animate)
  * sample()    - turn a smooth point run into a polygon (for clipping)
  * legend()    - capital letters laid around a circle (coin legends)
  * beads()     - a coin's beaded border as one continuous scalloped stroke
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import lib_v2 as lib  # noqa: E402
from lib_v2 import f1, L, D, H, svg, write, circle, ellipse, tx, GOLD, ORANGE, RUST, CLOAK, BLUE  # noqa: E402,F401


def fmt(p):
    return f"{f1(p[0])} {f1(p[1])}"


def _cr(p0, p1, p2, p3, t=0.5):
    c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
    c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
    return c1, c2


class PB:
    """Path builder. pb.M(x,y).L(x,y).S([(x,y),...]).C(c1,c2,p).Z(); str(pb)"""

    def __init__(self):
        self.d = []
        self.cur = None
        self.start = None

    def M(self, x, y=None):
        if y is None:
            x, y = x
        self.d.append(f"M {f1(x)} {f1(y)}")
        self.cur = self.start = (x, y)
        return self

    def L(self, x, y=None):
        if y is None:
            x, y = x
        self.d.append(f"L {f1(x)} {f1(y)}")
        self.cur = (x, y)
        return self

    def C(self, c1, c2, p):
        self.d.append(f"C {fmt(c1)} {fmt(c2)} {fmt(p)}")
        self.cur = p
        return self

    def Q(self, c, p):
        self.d.append(f"Q {fmt(c)} {fmt(p)}")
        self.cur = p
        return self

    def S(self, pts, t=0.5, tin=None, tout=None):
        """Catmull-Rom run from the current point through pts. tin/tout: optional
        phantom points that set the entry/exit tangents."""
        P = [self.cur] + list(pts)
        A = [tin if tin else P[0]] + P + [tout if tout else P[-1]]
        for i in range(1, len(A) - 2):
            c1, c2 = _cr(A[i - 1], A[i], A[i + 1], A[i + 2], t)
            self.d.append(f"C {fmt(c1)} {fmt(c2)} {fmt(A[i + 1])}")
        self.cur = P[-1]
        return self

    def Z(self):
        self.d.append("Z")
        self.cur = self.start
        return self

    def __str__(self):
        return " ".join(self.d)


def S(pts, closed=False, t=0.5):
    """smooth run through pts (open or closed) -> d"""
    return lib.smooth(pts, closed, t)


def P(pts, closed=False):
    d = "M " + " L ".join(fmt(p) for p in pts)
    return d + (" Z" if closed else "")


# ------------------------------------------------------------------ sampling

def bez(p0, c1, c2, p1, n=10):
    out = []
    for k in range(1, n + 1):
        u = k / n
        a, b, c, e = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
        out.append((a * p0[0] + b * c1[0] + c * c2[0] + e * p1[0], a * p0[1] + b * c1[1] + c * c2[1] + e * p1[1]))
    return out


def sample(pts, closed=True, t=0.5, n=8):
    """polygon approximating the Catmull-Rom curve through pts"""
    Pp = list(pts)
    A = [Pp[-1]] + Pp + [Pp[0], Pp[1]] if closed else [Pp[0]] + Pp + [Pp[-1]]
    out = [A[1]]
    for i in range(1, len(A) - 2):
        c1, c2 = _cr(A[i - 1], A[i], A[i + 1], A[i + 2], t)
        out += bez(A[i], c1, c2, A[i + 1], n)
    return out


def lerp(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def rot(p, deg, o=(0, 0)):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    x, y = p[0] - o[0], p[1] - o[1]
    return (o[0] + x * c - y * s, o[1] + x * s + y * c)


def place(pts, s=1.0, dx=0.0, dy=0.0, flip=False, deg=0.0):
    """scale (and optionally mirror in x), rotate, translate a point list"""
    out = []
    for (x, y) in pts:
        x = -x if flip else x
        x, y = x * s, y * s
        if deg:
            x, y = rot((x, y), deg)
        out.append((x + dx, y + dy))
    return out


# ------------------------------------------------------------------ hatching

def _clip_scan(poly, y):
    xs = []
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 <= y < y1) or (y1 <= y < y0):
            xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    xs.sort()
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]


def hatch(poly, angle=45, gap=7, inset=0, zig=False, start=0.5, jitter=0.0, maxlink=None, minlen=4):
    """Parallel hatch strokes inside polygon `poly` at `angle` degrees, spaced `gap`.
    zig=True joins neighbouring strokes end-to-end (back-and-forth shading in one pen
    movement) whenever the turn is short. Returns a d string."""
    if maxlink is None:
        maxlink = gap * 2.6
    a = math.radians(angle)
    # rotate polygon so hatch lines become horizontal
    R = [(x * math.cos(-a) - y * math.sin(-a), x * math.sin(-a) + y * math.cos(-a)) for (x, y) in poly]
    ys = [p[1] for p in R]
    y0, y1 = min(ys), max(ys)
    rows = []
    k = 0
    y = y0 + gap * start
    while y < y1:
        segs = [(sa + inset, sb - inset) for (sa, sb) in _clip_scan(R, y) if sb - sa - 2 * inset > minlen]
        rows.append((y, segs))
        y += gap
        k += 1
    back = lambda x, yy: (x * math.cos(a) - yy * math.sin(a), x * math.sin(a) + yy * math.cos(a))
    strokes = []  # list of point lists
    cur = None
    flip = False
    for (yy, segs) in rows:
        if not segs:
            cur = None
            continue
        # one segment per row continues the zigzag (the widest); others start new strokes
        segs = sorted(segs, key=lambda s: s[0])
        for j, (sa, sb) in enumerate(segs):
            jj = (math.sin(yy * 12.9898 + sa * 78.233) * 43758.5453) % 1.0 if jitter else 0
            sa2, sb2 = sa + jitter * (jj - 0.5), sb - jitter * (((jj * 7.31) % 1.0) - 0.5)
            pa, pb = back(sa2, yy), back(sb2, yy)
            if zig and cur is not None and j == 0:
                last = cur[-1]
                nxt = (pb, pa) if flip else (pa, pb)
                if math.hypot(nxt[0][0] - last[0], nxt[0][1] - last[1]) <= maxlink:
                    cur += list(nxt)
                    flip = not flip
                    continue
                # try the other direction
                nxt2 = (pa, pb) if flip else (pb, pa)
                if math.hypot(nxt2[0][0] - last[0], nxt2[0][1] - last[1]) <= maxlink:
                    cur += list(nxt2)
                    continue
            cur = [pa, pb]
            flip = True
            strokes.append(cur)
            if not zig:
                cur = None
    return " ".join(P(s) for s in strokes)


def hatch_curve(pts, angle=45, gap=7, closed=True, **kw):
    return hatch(sample(pts, closed), angle, gap, **kw)


def contour_hatch(run_a, run_b, n, closed_ends=False):
    """strokes interpolated between two point runs (follow-the-form hatching), joined zig-zag"""
    A = sample(run_a, closed=False, n=6)
    B = sample(run_b, closed=False, n=6)
    m = min(len(A), len(B))
    A = [A[int(i * (len(A) - 1) / (m - 1))] for i in range(m)]
    B = [B[int(i * (len(B) - 1) / (m - 1))] for i in range(m)]
    pts = []
    for k in range(n):
        u = (k + 0.5) / n
        row = [lerp(A[i], B[i], u) for i in range(m)]
        pts += row if k % 2 == 0 else row[::-1]
    return P(pts)


# ------------------------------------------------------------------ coins

def beads(cx, cy, r, n, size=None, phase=0.0):
    """beaded border: one continuous stroke of small loops around a circle"""
    size = size or (2 * math.pi * r / n) * 0.42
    pb = PB()
    for i in range(n):
        a = math.radians(phase + 360.0 * i / n)
        c = (cx + r * math.cos(a), cy + r * math.sin(a))
        # a small loop drawn as a circle starting on its inner side
        ux, uy = math.cos(a), math.sin(a)
        p0 = (c[0] - ux * size, c[1] - uy * size)
        if i == 0:
            pb.M(p0)
        else:
            pb.L(p0)
        k = 0.5523 * size
        vx, vy = -uy, ux
        q1 = (c[0] + vx * size, c[1] + vy * size)
        q2 = (c[0] + ux * size, c[1] + uy * size)
        q3 = (c[0] - vx * size, c[1] - vy * size)
        pb.C((p0[0] + vx * k, p0[1] + vy * k), (q1[0] - ux * k, q1[1] - uy * k), q1)
        pb.C((q1[0] + ux * k, q1[1] + uy * k), (q2[0] + vx * k, q2[1] + vy * k), q2)
        pb.C((q2[0] - vx * k, q2[1] - vy * k), (q3[0] + ux * k, q3[1] + uy * k), q3)
        pb.C((q3[0] - ux * k, q3[1] - uy * k), (p0[0] - vx * k, p0[1] - vy * k), p0)
    return str(pb)


def bead_dots(cx, cy, r, n, size, phase=0.0):
    """beaded border as one continuous wavy stroke (lighter than loops)"""
    pts = []
    for i in range(n * 4 + 1):
        a = math.radians(phase + 360.0 * i / (n * 4))
        rr = r + (size if i % 4 == 1 else (-size if i % 4 == 3 else 0))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return S(pts)


# single-stroke capitals in a 0..1 (w) x 0..1 (h, y down) box; each letter one pen stroke
_LET = {
    "A": ([(0, 1), (0.5, 0), (1, 1), (0.78, 0.56), (0.24, 0.56)], 0.8),
    "C": ("curve", [(0.95, 0.18), (0.55, 0.0), (0.1, 0.2), (0.0, 0.5), (0.1, 0.8), (0.55, 1.0), (0.95, 0.82)], 0.75),
    "D": ([(0, 1), (0, 0), (0.45, 0.02), (0.85, 0.25), (0.95, 0.5), (0.85, 0.75), (0.45, 0.98), (0, 1)], 0.8),
    "E": ([(0.85, 0), (0, 0), (0, 0.5), (0.7, 0.5), (0, 0.5), (0, 1), (0.85, 1)], 0.65),
    "F": ([(0.85, 0), (0, 0), (0, 0.5), (0.7, 0.5), (0, 0.5), (0, 1)], 0.6),
    "G": ("curve", [(0.95, 0.2), (0.55, 0.0), (0.1, 0.2), (0.0, 0.5), (0.1, 0.8), (0.55, 1.0), (0.95, 0.82), (0.95, 0.55), (0.6, 0.55)], 0.8),
    "I": ([(0, 0), (0, 1)], 0.15),
    "M": ([(0, 1), (0.05, 0), (0.5, 0.75), (0.95, 0), (1, 1)], 0.95),
    "N": ([(0, 1), (0, 0), (0.85, 1), (0.85, 0)], 0.8),
    "O": ("closed", [(0.5, 0), (0.92, 0.25), (0.98, 0.55), (0.75, 0.92), (0.4, 0.98), (0.05, 0.75), (0.05, 0.3)], 0.85),
    "P": ([(0, 1), (0, 0), (0.55, 0.02), (0.82, 0.25), (0.55, 0.5), (0, 0.5)], 0.7),
    "R": ([(0, 1), (0, 0), (0.55, 0.02), (0.82, 0.25), (0.55, 0.5), (0, 0.5), (0.8, 1)], 0.75),
    "S": ("curve", [(0.85, 0.12), (0.45, 0.0), (0.08, 0.2), (0.3, 0.45), (0.75, 0.6), (0.85, 0.85), (0.45, 1.0), (0.0, 0.88)], 0.7),
    "T": ([(0, 0), (0.9, 0), (0.45, 0), (0.45, 1)], 0.8),
    "V": ([(0, 0), (0.42, 1), (0.84, 0)], 0.8),
    "X": ([(0, 0), (0.8, 1), (0.4, 0.5), (0.8, 0), (0, 1)], 0.8),
}


def _glyph(ch):
    g = _LET[ch]
    if g[0] in ("curve", "closed"):
        return g[0], g[1], g[2]
    return "poly", g[0], g[1]


def legend(text, cx, cy, r, a_start, a_end, h, upright_out=True):
    """Letters around a circle from angle a_start to a_end (degrees, 0 = +x, clockwise on
    screen). Letter feet sit on radius r, tops point outward (as on the denarius)."""
    widths = []
    for ch in text:
        widths.append(0.45 if ch == " " else _glyph(ch)[2])
    total = sum(widths) + 0.22 * (len(text) - 1)
    span = math.radians(a_end - a_start)
    unit = (r * span) / total  # arc length per unit width
    out = []
    pos = 0.0
    for ch, w in zip(text, widths):
        if ch != " ":
            kind, pts, gw = _glyph(ch)
            loc = []
            for (u, v) in pts:
                ang = math.radians(a_start) + (pos + u * gw) * unit / r
                rr = r + (1 - v) * h if upright_out else r - (1 - v) * h
                loc.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
            if kind == "poly":
                out.append(P(loc))
            elif kind == "curve":
                out.append(S(loc))
            else:
                out.append(S(loc, closed=True))
        pos += w + 0.22
    return out


def arc_pts(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def path_d(*ds):
    return " ".join(d for d in ds if d)


def el(cls, d, fill=None, accent=False, fill_opacity=None):
    f = f' fill="{fill}"' if fill else ""
    fo = f' fill-opacity="{fill_opacity}"' if fill_opacity is not None else ""
    st = ' style="mix-blend-mode:multiply"' if accent else ""
    return f'  <path class="{cls}"{f}{fo}{st} d="{d}"/>\n'


# ------------------------------------------------------------------ denarius of Tiberius
def _u(pts, cx, cy, k):
    return [(cx + x * k, cy + y * k) for (x, y) in pts]


def leaf_chain(stems, length, width, k=1.0, side_alt=True, lean=0.0):
    """laurel leaves along a run of stem points: one continuous stroke drawing each leaf
    (pointed oval) and gliding to the next stem. stems: list of (point, direction(deg))."""
    pb = PB()
    for i, ((x, y), ang) in enumerate(stems):
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        ln, w = length * k, width * k
        tip = (x + ux * ln, y + uy * ln)
        m1 = (x + ux * ln * 0.45 + nx * w, y + uy * ln * 0.45 + ny * w)
        m2 = (x + ux * ln * 0.45 - nx * w, y + uy * ln * 0.45 - ny * w)
        if i == 0:
            pb.M(x, y)
        else:
            pb.L(x, y)
        pb.C((x + nx * w * 0.9, y + ny * w * 0.9), (m1[0] - ux * ln * 0.2, m1[1] - uy * ln * 0.2), m1)
        pb.C((m1[0] + ux * ln * 0.25, m1[1] + uy * ln * 0.25), (tip[0] - ux * ln * 0.15 + nx * w * 0.3, tip[1] - uy * ln * 0.15 + ny * w * 0.3), tip)
        pb.C((tip[0] - ux * ln * 0.15 - nx * w * 0.3, tip[1] - uy * ln * 0.15 - ny * w * 0.3), (m2[0] + ux * ln * 0.25, m2[1] + uy * ln * 0.25), m2)
        pb.C((m2[0] - ux * ln * 0.2, m2[1] - uy * ln * 0.2), (x - nx * w * 0.9, y - ny * w * 0.9), (x, y))
    return str(pb)


def tiberius_head(cx, cy, r, hatch_on=True):
    """laureate head of Tiberius facing right; unit design on a coin of radius 100"""
    k = r / 100.0
    U = lambda pts: _u(pts, cx, cy, k)
    out = []
    # profile: neck front -> throat -> chin -> mouth -> nose -> brow -> forehead -> crown ->
    # back of skull -> nape -> neck back (one confident contour)
    prof = U([
        (14, 55), (16, 44), (22, 36.5), (31, 32.5), (37.5, 29),   # throat, under-chin
        (40.5, 23), (38, 17.5),                                   # chin, chin dent
        (40, 14), (37.5, 11.5), (40.5, 8.5), (40, 5), (42, 2.5),  # lips, philtrum
        (47.5, 0.5),                                              # nose tip
        (39.5, -15), (37.5, -18.5), (39, -23),                    # bridge, root, brow ridge
        (36.5, -33), (31, -43), (20, -52.5),                      # forehead
        (2, -59), (-20, -56.5), (-36, -45),                       # crown
        (-45, -27), (-45, -8), (-39, 7), (-31, 17),               # back of skull, occiput, nape
        (-27, 31), (-27.5, 55),                                   # neck back
    ])
    pb = PB().M(prof[0])
    pb.S(prof[1:12])
    pb.L(prof[12])            # crisp nose tip
    pb.L(prof[13])            # straight bridge
    pb.S(prof[14:])
    out.append(el("line", str(pb), fill="#ffffff" if False else None))
    # bust truncation
    out.append(el("detail", S(U([(-27.5, 55), (-12, 60.5), (4, 60), (14, 55)]))))
    # ear (helix + inner fold), eye, brow, nostril, mouth corner, jaw, neck muscle
    out.append(el("detail", S(U([(3, -14), (9, -18), (13.5, -11), (12, -1), (8, 7), (2.5, 8), (1, 4)]))))
    out.append(el("detail", S(U([(7, -9), (9, -5), (6, 1)]))))
    out.append(el("detail", S(U([(25.5, -23), (31, -24.5), (36, -22.5)]))))
    out.append(el("detail", P(U([(25.5, -16), (30.5, -19.5), (35, -17.5), (31, -13.8), (25.5, -16)]))))
    out.append(el("detail", S(U([(40.5, -6), (37, -2.5), (38.5, 0.5)]))))
    out.append(el("detail", S(U([(37.5, 11.5), (34, 12.5)]))))
    out.append(el("detail", S(U([(9, 13), (18, 23), (29, 28.5)]))))
    # laurel wreath: band seen from the side (front at the hairline, back at the occiput),
    # leaves pointing forward, ties fluttering behind the neck
    band = U([(31, -42), (14, -45), (-6, -44), (-26, -38), (-43, -27)])
    out.append(el("detail", S(band)))
    bpts = sample(band, closed=False, n=8)
    stems = []
    for j, i in enumerate(range(len(bpts) - 2, 1, -3)):
        (x0, y0), (x1, y1) = bpts[i + 1], bpts[i - 1]
        base = math.degrees(math.atan2(y0 - y1, x0 - x1))  # direction toward the front
        stems.append((bpts[i], base + (-38 if j % 2 == 0 else 34)))
    out.append(el("detail", leaf_chain(stems, 17, 4.2, k)))
    out.append(el("detail", S(U([(-43, -27), (-50, -14), (-55, 2), (-52, 16), (-56, 30)]))))
    out.append(el("detail", S(U([(-43, -25), (-46, -8), (-44, 8), (-48, 24), (-46, 36)]))))
    # hair: short locks over the temple and down the nape (two light strokes)
    out.append(el("detail", S(U([(22, -40), (17, -34), (22, -30), (16, -25), (19, -21)]))))
    out.append(el("detail", S(U([(-30, -30), (-36, -20), (-31, -12), (-37, -3), (-31, 5), (-34, 12)]))))
    if hatch_on:
        out.append(el("hatch", hatch(U([(-27, 26), (-27.5, 55), (-16, 59), (-11, 50), (-15, 36), (-22, 24)]), 62, 3.0 * k)))
        out.append(el("hatch", hatch(U([(16, 44), (22, 36.5), (30, 33), (24, 41), (18, 52)]), 62, 3.0 * k)))
    return "".join(out)


def tiberius_obverse(cx, cy, r, legend_on=True, wash=True, hatch_on=True, rim="loops"):
    """Obverse of the 'tribute penny': laureate head of Tiberius right, beaded border,
    legend TI CAESAR DIVI AVG F AVGVSTVS (clockwise from 7 o'clock)."""
    k = r / 100.0
    U = lambda pts: _u(pts, cx, cy, k)
    out = []
    edge = U([(0, -100), (71, -70.5), (100, 1.5), (69.5, 71.5), (-1, 99.5), (-71, 70), (-99.5, -1), (-70, -71)])
    out.append(el("line", S(edge, closed=True), fill=BLUE if wash else None, accent=wash,
                  fill_opacity=0.3 if wash else None))
    if rim == "loops":
        out.append(el("detail", beads(cx, cy, 91 * k, 44, 1.9 * k)))
    elif rim:
        out.append(el("detail", bead_dots(cx, cy, 91 * k, 44, 1.6 * k)))
    out.append(tiberius_head(cx + 2 * k, cy + 4 * k, r * 1.07, hatch_on))
    if legend_on:
        for d in legend("TI CAESAR DIVI AVG F AVGVSTVS", cx, cy, 74 * k, 122, 418, 11.5 * k):
            out.append(el("detail", d))
    return "".join(out)


# ------------------------------------------------------------------ figure helpers
def tube(center, widths, cap0=0.6, cap1=0.6):
    """closed outline around a centre line (limb / sleeve). widths = half-widths per point.
    cap0/cap1 bulge of the end caps (0 = flat)."""
    n = len(center)
    left, right = [], []
    for i in range(n):
        p = center[i]
        a = center[max(0, i - 1)]
        b = center[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = widths[i]
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    # end caps
    def cap(p, q, c, bulge):
        dx, dy = c[0] - (p[0] + q[0]) / 2, c[1] - (p[1] + q[1]) / 2
        return [((p[0] + q[0]) / 2 + dx * bulge * 2, (p[1] + q[1]) / 2 + dy * bulge * 2)] if bulge else []
    e = center[-1]; pe = center[-2]
    ext = (e[0] + (e[0] - pe[0]) * 0.001, e[1] + (e[1] - pe[1]) * 0.001)
    dxe, dye = e[0] - pe[0], e[1] - pe[1]; lne = math.hypot(dxe, dye) or 1
    capE = [(e[0] + dxe / lne * widths[-1] * cap1, e[1] + dye / lne * widths[-1] * cap1)] if cap1 else []
    s0 = center[0]; s1 = center[1]
    dxs, dys = s0[0] - s1[0], s0[1] - s1[1]; lns = math.hypot(dxs, dys) or 1
    capS = [(s0[0] + dxs / lns * widths[0] * cap0, s0[1] + dys / lns * widths[0] * cap0)] if cap0 else []
    return left + capE + right[::-1] + capS


def fig_els(items, s=1.0, dx=0.0, dy=0.0, flip=False):
    """items: list of (cls, kind, pts|d, fill) with kind in {'S','SC','P','PC','D'} in local
    figure units -> placed svg string"""
    out = []
    for it in items:
        cls, kind, data = it[0], it[1], it[2]
        fill = it[3] if len(it) > 3 else None
        acc = it[4] if len(it) > 4 else False
        if kind == "D":
            d = tx(data, s=s, dx=dx, dy=dy, sx=(-s if flip else s), sy=s)
        else:
            pts = place(data, s, dx, dy, flip)
            if kind == "S":
                d = S(pts)
            elif kind == "SC":
                d = S(pts, closed=True)
            elif kind == "P":
                d = P(pts)
            elif kind == "PC":
                d = P(pts, closed=True)
            elif kind == "H":  # hatch polygon: data = (pts, angle, gap)
                pass
        out.append(el(cls, d, fill=fill, accent=acc))
    return "".join(out)
