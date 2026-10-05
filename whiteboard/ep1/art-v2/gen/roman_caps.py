"""Roman capitals as pen strokes, laid out on a straight baseline or around a coin.

Letters are designed in a y-UP unit box (cap height 1, x from 0 to the letter width) as one to
three continuous strokes each. Serifs are built INTO the strokes (a short bar with a tiny
retrace), so a letter costs the pen very few lifts (the engine pauses at every M).

Thick/thin: the strokes that are thick in inscriptional capitals (stems, down-right diagonals,
the flanks of bowls, the spine of S) are marked; with `heavy=<art units>` they get an extra
pass offset by that amount, so with the 1.5 `detail` pen a thick stroke reads ~2.8 wide and a
thin one 1.5 wide, still without a pen lift.

    from roman_caps import on_arc, on_line, strokes_to_d
    letters = on_arc("TI CAESAR DIVI AVG F AVGVSTVS", cx, cy, r_base, cap, -146, 146, heavy=1.3)
    for d in strokes_to_d(letters): body += D(d)

`on_arc` bends every point onto the circle with the letters' feet toward the centre, reading
clockwise: the way legends were struck on Roman coins.
"""
import math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkgeom import cr_dense, resample, poly_d  # noqa: E402

S_ = 0.06       # serif half-length (cap heights)


def _L(*xy, thick=False):
    return ("L", [(xy[i], xy[i + 1]) for i in range(0, len(xy), 2)], thick)


def _T(*xy):
    return _L(*xy, thick=True)


def _A(cx, cy, rx, ry, a0, a1, thick=False, n=None):
    n = n or max(4, int(abs(a1 - a0) / 6))
    return ("L", [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                   cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)], thick)


def _S(pts, thick_from=None, thick_to=None):
    """smooth curve; thick between control-point indices thick_from..thick_to"""
    return ("S", pts, (thick_from, thick_to) if thick_from is not None else False)


def _glyphs(s=S_):
    G = {}

    def stem_I(x):
        return [_L(x - s, 1, x + s, 1, x, 1), _T(x, 1, x, 0), _L(x, 0, x - s, 0, x + s, 0)]

    G["I"] = (0.12, [stem_I(0.06)])
    G["T"] = (0.70, [[_L(0.0, 0.90, 0.0, 1.0, 0.70, 1.0, 0.70, 0.90)],
                     [_T(0.35, 1, 0.35, 0), _L(0.35, 0, 0.35 - s, 0, 0.35 + s, 0)]])
    G["E"] = (0.52, [[_L(0.50, 0.88, 0.50, 1.0, -s, 1.0, 0, 1.0), _T(0, 1, 0, 0),
                      _L(0, 0, -s, 0, 0.52, 0, 0.52, 0.12)],
                     [_L(0, 0.52, 0.40, 0.52, 0.40, 0.58, 0.40, 0.46)]])
    G["F"] = (0.50, [[_L(0.50, 0.88, 0.50, 1.0, -s, 1.0, 0, 1.0), _T(0, 1, 0, 0), _L(0, 0, -s, 0, s, 0)],
                     [_L(0, 0.50, 0.38, 0.50, 0.38, 0.56, 0.38, 0.44)]])
    G["L"] = (0.50, [[_L(-s, 1, s, 1, 0, 1), _T(0, 1, 0, 0), _L(0, 0, -s, 0, 0.50, 0, 0.50, 0.13)]])
    G["H"] = (0.74, [[_L(-s, 0, s, 0, 0, 0), _T(0, 0, 0, 1), _L(0, 1, -s, 1, s, 1)],
                     [_L(0, 0.52, 0.74, 0.52)], stem_I(0.74)])
    G["V"] = (0.74, [[_L(-s, 1, s, 1, 0, 1), _T(0, 1, 0.37, 0), _L(0.37, 0, 0.74, 1, 0.74 - s, 1, 0.74 + s, 1)]])
    G["A"] = (0.78, [[_L(-s, 0, s, 0, 0, 0, 0.39, 1), _T(0.39, 1, 0.78, 0), _L(0.78, 0, 0.78 - s, 0, 0.78 + s, 0)],
                     [_L(0.18, 0.35, 0.60, 0.35)]])
    G["M"] = (0.94, [[_L(-s, 0, s, 0, 0, 0, 0.07, 1), _T(0.07, 1, 0.47, 0.02), _L(0.47, 0.02, 0.87, 1),
                      _T(0.87, 1, 0.94, 0), _L(0.94, 0, 0.94 - s, 0, 0.94 + s, 0)]])
    G["N"] = (0.78, [[_L(-s, 0, s, 0, 0, 0, 0, 1, -s, 1, 0, 1), _T(0, 1, 0.78, 0),
                      _L(0.78, 0, 0.78, 1, 0.78 - s, 1, 0.78 + s, 1)]])
    G["W"] = (1.10, [[_L(-s, 1, s, 1, 0, 1), _T(0, 1, 0.28, 0), _L(0.28, 0, 0.55, 0.95), _T(0.55, 0.95, 0.82, 0),
                      _L(0.82, 0, 1.10, 1, 1.10 - s, 1, 1.10 + s, 1)]])
    G["X"] = (0.70, [[_L(-s, 1, s, 1, 0, 1), _T(0, 1, 0.70, 0), _L(0.70, 0, 0.70 - s, 0, 0.70 + s, 0)],
                     [_L(0.70 - s, 1, 0.70 + s, 1, 0.70, 1, 0, 0, -s, 0, s, 0)]])
    G["Y"] = (0.72, [[_L(-s, 1, s, 1, 0, 1), _T(0, 1, 0.36, 0.5), _L(0.36, 0.5, 0.72, 1, 0.72 - s, 1, 0.72 + s, 1)],
                     [_T(0.36, 0.5, 0.36, 0), _L(0.36, 0, 0.36 - s, 0, 0.36 + s, 0)]])
    G["K"] = (0.70, [stem_I(0.0), [_L(0.66 - s, 1, 0.66 + s, 1, 0.66, 1, 0.03, 0.48), _T(0.03, 0.48, 0.68, 0),
                                   _L(0.68, 0, 0.75, 0)]])
    # bowls (angles CCW, y up)
    G["O"] = (0.84, [[_A(0.42, 0.5, 0.42, 0.5, 90, 140), _A(0.42, 0.5, 0.42, 0.5, 140, 220, True),
                      _A(0.42, 0.5, 0.42, 0.5, 220, 320), _A(0.42, 0.5, 0.42, 0.5, 320, 400, True),
                      _A(0.42, 0.5, 0.42, 0.5, 400, 450)]])
    G["C"] = (0.70, [[_L(0.655, 0.74, 0.65, 0.86), _A(0.38, 0.5, 0.38, 0.5, 47, 140),
                      _A(0.38, 0.5, 0.38, 0.5, 140, 220, True), _A(0.38, 0.5, 0.38, 0.5, 220, 315),
                      _L(0.649, 0.146, 0.655, 0.25)]])
    G["G"] = (0.74, [[_L(0.68, 0.74, 0.67, 0.86), _A(0.39, 0.5, 0.39, 0.5, 47, 140),
                      _A(0.39, 0.5, 0.39, 0.5, 140, 220, True), _A(0.39, 0.5, 0.39, 0.5, 220, 320),
                      _L(0.689, 0.179, 0.70, 0.47, 0.58, 0.47)]])
    G["D"] = (0.74, [[_L(0.30, 0, -s, 0, s, 0, 0, 0), _T(0, 0, 0, 1), _L(0, 1, -s, 1, 0.30, 1),
                      _A(0.30, 0.5, 0.44, 0.5, 90, 35), _A(0.30, 0.5, 0.44, 0.5, 35, -35, True),
                      _A(0.30, 0.5, 0.44, 0.5, -35, -90)]])
    G["P"] = (0.58, [[_L(-s, 0, s, 0, 0, 0), _T(0, 0, 0, 1), _L(0, 1, -s, 1, 0.30, 1),
                      _A(0.30, 0.755, 0.27, 0.245, 90, 30), _A(0.30, 0.755, 0.27, 0.245, 30, -30, True),
                      _A(0.30, 0.755, 0.27, 0.245, -30, -90), _L(0.30, 0.51, 0, 0.51)]])
    G["R"] = (0.62, [[_L(-s, 0, s, 0, 0, 0), _T(0, 0, 0, 1), _L(0, 1, -s, 1, 0.30, 1),
                      _A(0.30, 0.755, 0.27, 0.245, 90, -90), _L(0.30, 0.51, 0, 0.51, 0.22, 0.51),
                      _T(0.22, 0.51, 0.58, 0), _L(0.58, 0, 0.68, 0)]])
    G["B"] = (0.60, [[_L(-s, 0, s, 0, 0, 0), _T(0, 0, 0, 1), _L(0, 1, -s, 1, 0.28, 1),
                      _A(0.28, 0.765, 0.24, 0.235, 90, -90), _L(0.28, 0.53, 0.0, 0.53, 0.31, 0.53),
                      _A(0.31, 0.265, 0.29, 0.265, 90, -90), _L(0.31, 0.0, 0.0, 0.0)]])
    G["U"] = (0.74, [[_L(-s, 1, s, 1, 0, 1), _T(0, 1, 0, 0.32), _A(0.37, 0.32, 0.37, 0.32, 180, 360),
                      _L(0.74, 0.32, 0.74, 1, 0.74 - s, 1, 0.74 + s, 1)]])
    G["S"] = (0.52, [[_L(0.47, 0.75, 0.47, 0.87),
                      _S([(0.47, 0.87), (0.40, 0.96), (0.25, 1.0), (0.09, 0.95), (0.03, 0.80), (0.10, 0.64),
                          (0.27, 0.54), (0.43, 0.43), (0.50, 0.27), (0.44, 0.08), (0.27, 0.0), (0.10, 0.03),
                          (0.02, 0.13)], 5, 8),
                      _L(0.02, 0.13, 0.02, 0.26)]])
    return G


GLYPHS = _glyphs()
SPACE = 0.40


def _dense(stroke):
    """-> (points, thick flag per edge)"""
    pts, flags = [], []
    for kind, P, thick in stroke:
        if kind == "S":
            n = 8
            seg = cr_dense(P, n)
            if thick:
                a, b = thick
                f = [a * n <= i < b * n for i in range(len(seg) - 1)]
            else:
                f = [False] * (len(seg) - 1)
        else:
            seg = list(P)
            f = [bool(thick)] * (len(seg) - 1)
        if pts and math.dist(pts[-1], seg[0]) < 1e-6:
            seg = seg[1:]
        else:
            if pts:
                f = [False] + f            # connector edge from the previous point
        pts += seg
        flags += f
    return pts, flags[: max(0, len(pts) - 1)]


def _offset(run, k):
    """run of points shifted k to the LEFT of their travel direction; curved runs (more than
    two points) swell in and out smoothly, like a broad-pen bowl."""
    out, n = [], len(run)
    for i, p in enumerate(run):
        a = run[max(0, i - 1)]; b = run[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        kk = k if n <= 2 else k * max(0.0, math.sin(math.pi * i / (n - 1))) ** 0.6
        out.append((p[0] - dy / L * kk, p[1] + dx / L * kk))
    return out


def _thicken(pts, flags, k):
    """insert extra passes over thick runs (2 passes at stroke ends, 3 in the middle)"""
    if not k or not any(flags):
        return pts
    runs, i = [], 0
    while i < len(flags):
        if flags[i]:
            j = i
            while j < len(flags) and flags[j]:
                j += 1
            runs.append((i, j))          # points i..j
            i = j
        else:
            i += 1
    out, last = [], 0
    for (i, j) in runs:
        run = pts[i: j + 1]
        if i == 0:                       # thick start: lay the offset pass first, backwards
            out += list(reversed(_offset(run, k))) + run
        elif j == len(pts) - 1:          # thick end: come back along the offset
            out += pts[last: i] + run + list(reversed(_offset(run, k)))
        else:                            # middle: forward, back offset, forward half offset
            out += pts[last: i] + run + list(reversed(_offset(run, k))) + _offset(run, k * 0.5)
        last = j + 1
    out += pts[last:]
    return out


def layout(text, squeeze=1.0, tracking=0.16, space=SPACE, heavy=0.0):
    """-> list of (x_offset, glyph_width, polylines in unit coords) and the total advance.
    heavy is in cap units here."""
    out, x = [], 0.0
    for ch in text.upper():
        if ch == " ":
            x += space
            continue
        w, strokes = GLYPHS[ch]
        polys = []
        for st in strokes:
            p, fl = _dense(st)
            p = [(px * squeeze, py) for px, py in p]
            p = _thicken(p, fl, heavy)
            polys.append([(px + x, py) for px, py in p])
        out.append((x, w * squeeze, polys))
        x += w * squeeze + tracking
    return out, x - tracking


def on_line(text, x0, y0, cap, squeeze=1.0, tracking=0.16, align="left", slant=0.0, space=SPACE, heavy=0.0):
    """letters on a straight baseline (y DOWN art coords). Returns letters, each a list of polylines."""
    L, adv = layout(text, squeeze, tracking, space, heavy / cap)
    shift = {"left": 0.0, "center": -adv / 2, "right": -adv}[align]
    return [[[(x0 + (px + shift + py * slant) * cap, y0 - py * cap) for px, py in p] for p in polys]
            for _, _, polys in L]


def on_arc(text, cx, cy, r_base, cap, a_start, a_end=None, squeeze=1.0, tracking=0.16, space=SPACE,
           heavy=0.0, step=None):
    """letters around a circle, reading clockwise, feet toward the centre.
    Angles in degrees clockwise from 12 o'clock. With a_end the spacing is stretched (or shrunk)
    so the text spans a_start..a_end exactly. Returns letters (lists of polylines)."""
    L, adv = layout(text, squeeze, tracking, space, heavy / cap)
    if a_end is not None:
        span = math.radians(a_end - a_start) * r_base / cap
        n_gaps = len(text.strip()) - 1
        extra = (span - adv) / max(1, n_gaps)
        L, adv = layout(text, squeeze, tracking + extra, space + extra, heavy / cap)
    res = []
    for _, _, polys in L:
        letter = []
        for p in polys:
            q = []
            for px, py in p:
                phi = math.radians(a_start) + px * cap / r_base
                r = r_base + py * cap
                q.append((cx + r * math.sin(phi), cy - r * math.cos(phi)))
            letter.append(resample(q, step) if step else q)
        res.append(letter)
    return res


def advance(text, cap, squeeze=1.0, tracking=0.16, space=SPACE):
    return layout(text, squeeze, tracking, space)[1] * cap


def strokes_to_d(letters, eps=0.15):
    """letters -> list of path-data strings (one per stroke)."""
    return [poly_d(p, eps=eps) for letter in letters for p in letter]
