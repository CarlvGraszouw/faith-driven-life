"""Roman capitals as pen strokes, laid out on a straight baseline or around a coin.

Letters are designed in a y-UP unit box (cap height 1, x from 0 to the letter width) as a few
continuous strokes each; serifs are built INTO the strokes (a short bar with a tiny retrace) so a
letter costs the pen only 1-3 lifts. `on_arc` bends every point onto the circle (letters' feet
toward the centre, reading clockwise) the way legends are struck on Roman coins.

    from roman_caps import on_arc, on_line, strokes_to_d
    polys = on_arc("TI CAESAR DIVI AVG F AVGVSTVS", cx, cy, r_base, cap, -146, 146)
    d = strokes_to_d(polys)            # one path element per letter stroke list

Optional `heavy=True` doubles the thick strokes (verticals and down-right diagonals) with a
narrow return pass, giving the thick/thin contrast of inscriptional capitals without extra lifts.
"""
import math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkgeom import cr_dense, resample, poly_d  # noqa: E402

SER = 0.075     # serif half-length (cap heights)


def _stem(x, y0=0.0, y1=1.0, s=SER, top=True, bot=True):
    """vertical stem with bar serifs, one stroke: top-left -> top-right -> centre -> down -> feet."""
    pts = []
    if top:
        pts += [(x - s, y1), (x + s, y1)]
    pts += [(x, y1), (x, y0)]
    if bot:
        pts += [(x - s, y0), (x + s, y0)]
    return [("L", pts)]


def _arc(cx, cy, rx, ry, a0, a1, n=28):
    """elliptic arc in the y-up letter box, angles in degrees CCW from +x."""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# Each glyph: (advance width, [stroke, ...]); stroke = list of ("L"|"S"|"P", points)
#   L = straight polyline, S = smooth Catmull-Rom through points, P = pre-sampled points.
# Thick strokes for heavy mode are marked by listing their (start, end) in the 3rd tuple item.
def _glyphs(s=SER):
    G = {}
    G["I"] = (0.16, [_stem(0.08, s=s)])
    G["T"] = (0.70, [[("L", [(0.0, 0.90), (0.0, 1.0), (0.70, 1.0), (0.70, 0.90)])],
                     _stem(0.35, top=False, s=s)])
    G["E"] = (0.52, [[("L", [(0.50, 0.89), (0.50, 1.0), (-0.06, 1.0), (0.0, 1.0), (0.0, 0.0),
                             (-0.06, 0.0), (0.52, 0.0), (0.52, 0.12)])],
                     [("L", [(0.0, 0.52), (0.40, 0.52), (0.40, 0.58), (0.40, 0.46)])]])
    G["F"] = (0.50, [[("L", [(0.50, 0.89), (0.50, 1.0), (-0.06, 1.0), (0.0, 1.0), (0.0, 0.0),
                             (-0.075, 0.0), (0.075, 0.0)])],
                     [("L", [(0.0, 0.50), (0.38, 0.50), (0.38, 0.56), (0.38, 0.44)])]])
    G["L"] = (0.50, [[("L", [(-0.075, 1.0), (0.075, 1.0), (0.0, 1.0), (0.0, 0.0), (-0.06, 0.0),
                             (0.50, 0.0), (0.50, 0.13)])]])
    G["H"] = (0.74, [[("L", [(-0.075, 0.0), (0.075, 0.0), (0.0, 0.0), (0.0, 1.0), (-0.075, 1.0), (0.075, 1.0)])],
                     [("L", [(0.0, 0.52), (0.74, 0.52)])],
                     _stem(0.74, s=s)])
    G["V"] = (0.74, [[("L", [(-0.075, 1.0), (0.075, 1.0), (0.0, 1.0), (0.37, 0.0), (0.74, 1.0),
                             (0.665, 1.0), (0.815, 1.0)])]])
    G["A"] = (0.78, [[("L", [(-0.075, 0.0), (0.075, 0.0), (0.0, 0.0), (0.39, 1.0), (0.78, 0.0),
                             (0.705, 0.0), (0.855, 0.0)])],
                     [("L", [(0.17, 0.36), (0.61, 0.36)])]])
    G["M"] = (0.94, [[("L", [(-0.075, 0.0), (0.075, 0.0), (0.0, 0.0), (0.07, 1.0), (0.47, 0.02),
                             (0.87, 1.0), (0.94, 0.0), (0.865, 0.0), (1.015, 0.0)])]])
    G["N"] = (0.78, [[("L", [(-0.075, 0.0), (0.075, 0.0), (0.0, 0.0), (0.0, 1.0), (-0.07, 1.0),
                             (0.0, 1.0), (0.78, 0.0), (0.78, 1.0), (0.705, 1.0), (0.855, 1.0)])]])
    G["W"] = (1.10, [[("L", [(-0.075, 1.0), (0.075, 1.0), (0.0, 1.0), (0.28, 0.0), (0.55, 0.95),
                             (0.82, 0.0), (1.10, 1.0), (1.025, 1.0), (1.175, 1.0)])]])
    G["X"] = (0.70, [[("L", [(-0.075, 1.0), (0.075, 1.0), (0.0, 1.0), (0.70, 0.0), (0.625, 0.0), (0.775, 0.0)])],
                     [("L", [(0.625, 1.0), (0.775, 1.0), (0.70, 1.0), (0.0, 0.0), (-0.075, 0.0), (0.075, 0.0)])]])
    G["Y"] = (0.72, [[("L", [(-0.075, 1.0), (0.075, 1.0), (0.0, 1.0), (0.36, 0.5), (0.72, 1.0),
                             (0.645, 1.0), (0.795, 1.0)])], _stem(0.36, 0.0, 0.5, top=False, s=s)])
    # bowls
    G["O"] = (0.82, [[("P", _arc(0.41, 0.5, 0.41, 0.5, 90, 450, 48))]])
    G["C"] = (0.70, [[("L", [(0.655, 0.74), (0.655, 0.86)]), ("P", _arc(0.38, 0.5, 0.38, 0.5, 46, 316, 40)),
                      ("L", [(0.655, 0.14), (0.655, 0.26)])]])
    G["G"] = (0.74, [[("L", [(0.68, 0.74), (0.68, 0.86)]), ("P", _arc(0.38, 0.5, 0.38, 0.5, 46, 322, 40)),
                      ("L", [(0.68, 0.19), (0.70, 0.46), (0.58, 0.46)])]])
    G["D"] = (0.74, [[("L", [(0.30, 0.0), (-0.075, 0.0), (0.075, 0.0), (0.0, 0.0), (0.0, 1.0), (-0.07, 1.0), (0.30, 1.0)]),
                      ("P", _arc(0.30, 0.5, 0.44, 0.5, 90, -90, 30))]])
    G["P"] = (0.58, [[("L", [(-0.075, 0.0), (0.075, 0.0), (0.0, 0.0), (0.0, 1.0), (-0.07, 1.0), (0.30, 1.0)]),
                      ("P", _arc(0.30, 0.755, 0.27, 0.245, 90, -90, 22)), ("L", [(0.30, 0.51), (0.0, 0.51)])]])
    G["B"] = (0.60, [[("L", [(-0.075, 0.0), (0.075, 0.0), (0.0, 0.0), (0.0, 1.0), (-0.07, 1.0), (0.28, 1.0)]),
                      ("P", _arc(0.28, 0.765, 0.24, 0.235, 90, -90, 20)), ("L", [(0.28, 0.53), (0.0, 0.53), (0.31, 0.53)]),
                      ("P", _arc(0.31, 0.265, 0.29, 0.265, 90, -90, 22)), ("L", [(0.31, 0.0), (0.0, 0.0)])]])
    G["R"] = (0.62, [[("L", [(-0.075, 0.0), (0.075, 0.0), (0.0, 0.0), (0.0, 1.0), (-0.07, 1.0), (0.30, 1.0)]),
                      ("P", _arc(0.30, 0.755, 0.27, 0.245, 90, -90, 22)),
                      ("L", [(0.30, 0.51), (0.0, 0.51), (0.22, 0.51), (0.58, 0.0), (0.68, 0.0)])]])
    G["S"] = (0.52, [[("L", [(0.47, 0.76), (0.47, 0.87)]),
                      ("S", [(0.47, 0.87), (0.40, 0.96), (0.25, 1.0), (0.09, 0.95), (0.03, 0.80), (0.10, 0.64),
                             (0.27, 0.54), (0.43, 0.43), (0.50, 0.27), (0.44, 0.08), (0.27, 0.0), (0.10, 0.03),
                             (0.02, 0.12)]),
                      ("L", [(0.02, 0.12), (0.02, 0.25)])]])
    G["U"] = (0.74, [[("L", [(-0.075, 1.0), (0.075, 1.0), (0.0, 1.0), (0.0, 0.32)]),
                      ("P", _arc(0.37, 0.32, 0.37, 0.32, 180, 360, 24)),
                      ("L", [(0.74, 0.32), (0.74, 1.0), (0.665, 1.0), (0.815, 1.0)])]])
    G["K"] = (0.70, [_stem(0.0, s=s), [("L", [(0.62, 1.0), (0.70, 1.0), (0.66, 1.0), (0.02, 0.48), (0.66, 0.0),
                                              (0.74, 0.0)])]])
    return G


GLYPHS = _glyphs()
SPACE = 0.42


def _dense(stroke):
    out = []
    for kind, pts in stroke:
        if kind == "S":
            seg = cr_dense(pts, 8)
        else:
            seg = list(pts)
        if out and seg and math.dist(out[-1], seg[0]) < 1e-6:
            seg = seg[1:]
        out += seg
    return out


def _heavy(poly, k):
    """narrow return pass along a polyline: thickens the stroke without a pen lift."""
    back = [(x + k, y) for x, y in reversed(poly)]
    return poly + back


def layout(text, squeeze=1.0, tracking=0.16, space=SPACE):
    """-> list of (x_offset, glyph_width, strokes in unit coords) and the total advance."""
    out, x = [], 0.0
    for ch in text.upper():
        if ch == " ":
            x += space
            continue
        w, strokes = GLYPHS[ch]
        polys = [[(px * squeeze + x, py) for px, py in _dense(st)] for st in strokes]
        out.append((x, w * squeeze, polys))
        x += w * squeeze + tracking
    return out, x - tracking


def on_line(text, x0, y0, cap, squeeze=1.0, tracking=0.16, align="left", slant=0.0, space=SPACE):
    """letters on a straight baseline (y DOWN art coords). Returns list of letters, each a list of polylines."""
    L, adv = layout(text, squeeze, tracking, space)
    shift = {"left": 0.0, "center": -adv / 2, "right": -adv}[align]
    res = []
    for _, _, polys in L:
        res.append([[(x0 + (px + shift + py * slant) * cap, y0 - py * cap) for px, py in p] for p in polys])
    return res


def on_arc(text, cx, cy, r_base, cap, a_start, a_end=None, squeeze=1.0, tracking=0.16, space=SPACE,
           outward=True, step=None):
    """letters around a circle, reading clockwise, feet toward the centre (outward=True).
    Angles in degrees measured clockwise from 12 o'clock. If a_end is given the tracking is
    stretched so the text spans a_start..a_end exactly. Returns list of letters (lists of polylines)."""
    L, adv = layout(text, squeeze, tracking, space)
    if a_end is not None and len(L) > 1:
        span = math.radians(a_end - a_start) * r_base / cap           # in cap units
        n_gaps = len([c for c in text.strip()]) - 1
        extra = (span - adv) / max(1, n_gaps)
        L, adv = layout(text, squeeze, tracking + extra, space + extra)
    res = []
    for _, _, polys in L:
        letter = []
        for p in polys:
            q = []
            for px, py in p:
                phi = math.radians(a_start) + px * cap / r_base
                r = r_base + py * cap if outward else r_base - py * cap
                q.append((cx + r * math.sin(phi), cy - r * math.cos(phi)))
            letter.append(resample(q, step) if step else q)
        res.append(letter)
    return res


def strokes_to_d(letters, eps=0.2):
    """list of letters -> list of path-data strings (one per stroke)."""
    return [poly_d(p, eps=eps) for letter in letters for p in letter]
