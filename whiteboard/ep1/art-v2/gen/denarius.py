"""The 'tribute penny': silver denarius of Tiberius (Lugdunum mint, c. AD 15-37, RIC I 26/30).

Obverse: TI CAESAR DIVI AVG F AVGVSTVS, laureate head of Tiberius right.
Reverse: PONTIF MAXIM, female figure (Livia as Pax) seated right on a chair with ornamented legs,
         feet on a footstool, holding a long sceptre and an olive branch.

All geometry is designed in COIN units: centre (0, 0), y down, die (bead circle) radius 330.
`Coin(cx, cy, R)` maps it onto the board (R = die radius in art units) and returns lib_v2
elements, so the same drawing serves the big close-ups (a08/a09) and the small coins (b01/b03).
Each group is ONE continuous pen stroke where possible (the engine lifts the pen at every M).
"""
import math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from lib_v2 import L, D, H, f1, tx, BLUE  # noqa: E402
from inkgeom import (bez3, cr_dense, ell_pts, poly_d, path_pts, xf, hatch, segs_d, inside,  # noqa: E402
                     clip_outside, clip_inside, resample, lerp)
import roman_caps  # noqa: E402

R0 = 330.0          # die radius in coin units


# ------------------------------------------------------------------ helpers in coin units
def _n(u):
    L_ = math.hypot(*u) or 1.0
    return (u[0] / L_, u[1] / L_)


def leaf_loop(A, d, length, width, bend=0.0):
    """lanceolate leaf from attachment A along unit direction d: out on one edge, back on the other."""
    nx, ny = -d[1], d[0]
    T = (A[0] + d[0] * length + nx * bend, A[1] + d[1] * length + ny * bend)
    def P(a, w):
        return (A[0] + d[0] * length * a + nx * (w + bend * a * a), A[1] + d[1] * length * a + ny * (w + bend * a * a))
    e1 = bez3(A, P(0.22, width * 1.15), P(0.68, width * 0.85), T, 10)
    e2 = bez3(T, P(0.68, -width * 0.85), P(0.22, -width * 1.15), A, 10)
    return e1 + e2[1:]


def tuft(b0, b1, tip, curl, bow=0.0):
    """crescent lock of hair: from root b0 out to the tip (with a curl hook) and back to root b1.
    curl: vector of the hook at the tip. bow: sideways belly of the lock."""
    mid0 = lerp(b0, tip, 0.5); mid1 = lerp(b1, tip, 0.55)
    dx, dy = tip[0] - b0[0], tip[1] - b0[1]
    Ln = math.hypot(dx, dy) or 1
    nx, ny = -dy / Ln, dx / Ln
    c0 = (mid0[0] + nx * bow, mid0[1] + ny * bow)
    c1 = (mid1[0] + nx * bow * 0.6, mid1[1] + ny * bow * 0.6)
    hook = (tip[0] + curl[0], tip[1] + curl[1])
    out = cr_dense([b0, c0, tip, hook], 8)
    back = cr_dense([hook, (tip[0] - curl[0] * 0.15 + (b1[0] - tip[0]) * 0.12, tip[1] - curl[1] * 0.15 + (b1[1] - tip[1]) * 0.12),
                     c1, b1], 8)
    return out + back[1:]


# ------------------------------------------------------------------ OBVERSE: laureate head of Tiberius right
# Proportions (coin units): crown -246, brow -96, eye -70, nose tip x174, chin 88, truncation ~228.
PROFILE = ("M 124 -150 C 130 -136 138 -119 143 -104 C 146 -96 145 -88 138 -81 "
           "C 143 -73 150 -62 155 -52 C 160 -42 164 -33 168 -24 C 172 -15 177 -9 177 -3 C 177 3 173 6 167 6 "
           "C 161 7 154 6 148 8 C 148 13 150 17 152 21 C 153 24 151 27 147 28 "
           "C 150 30 150 34 148 38 C 146 42 142 44 141 48 C 145 55 151 62 151 72 "
           "C 151 84 144 94 130 97 C 117 100 105 103 95 110 C 89 118 89 128 90 140 "
           "C 91 152 92 160 89 174 C 84 190 79 202 76 214")
BACK_NECK = "M 76 214 C 28 223 -46 223 -100 207 C -94 186 -86 166 -82 146 C -79 126 -82 104 -90 90"
BACK_HAIR = ("M -90 90 C -93 99 -102 101 -106 90 C -112 99 -122 98 -125 86 C -131 94 -141 90 -143 77 "
             "C -151 83 -159 73 -162 58 C -173 38 -180 14 -182 -14 "
             "C -184 -42 -182 -72 -176 -98 C -174 -106 -173 -112 -171 -118")
BACK = BACK_NECK + " " + BACK_HAIR[BACK_HAIR.index("C"):]     # one continuous stroke
CROWN = "M -164 -134 C -148 -178 -96 -228 -14 -246 C 40 -251 86 -233 107 -203"
EAR = ("M -14 -84 C -23 -96 -46 -98 -56 -82 C -64 -68 -61 -44 -54 -26 C -49 -13 -40 -6 -31 -9 "
       "C -25 -11 -21 -17 -20 -23")
EAR_IN = ("M -21 -77 C -35 -83 -47 -74 -47 -58 C -47 -46 -42 -37 -35 -34 C -31 -32 -27 -35 -26 -39 "
          "M -15 -55 C -10 -50 -10 -41 -14 -36")
EYE = "M 98 -68 C 106 -78 120 -81 128 -76 C 131 -72 130 -66 127 -62 C 118 -59 108 -61 100 -66"
IRIS = "M 123 -77 C 119 -73 119 -65 122 -61"
LID = "M 99 -80 C 108 -88 122 -89 132 -84"
BROW = "M 94 -94 C 109 -101 128 -104 145 -99"
NOSTRIL = "M 160 5 C 154 4 150 0 150 -5 C 150 -10 154 -12 158 -10"
MOUTH = "M 146 28 C 142 28 138 29 133 32"
JAW = "M 112 96 C 84 92 46 82 14 66 C 0 58 -8 46 -12 30"
# hairline: front of the fringe -> temple -> sideburn -> round the ear -> nape
HAIRLINE = [(124, -150), (114, -143), (101, -133), (89, -121), (74, -113), (54, -109), (33, -104), (19, -93),
            (13, -74), (10, -54), (3, -45), (-7, -55), (-11, -78), (-22, -93), (-40, -99), (-57, -93),
            (-67, -79), (-71, -57), (-73, -32), (-77, -6), (-82, 24), (-86, 56), (-90, 90)]
FRONT_TOP = [(107, -203), (114, -188), (119, -170), (124, -150)]
BAND = ((-172, -114), (-110, -196), (24, -226), (116, -186))   # wreath band: knot -> front
WHORL = (-84, -222)


def bandpt(t, off=0.0):
    p0, p1, p2, p3 = BAND
    u = 1 - t
    x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
    y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
    if off:
        tx_, ty_ = bandtan(t)
        x, y = x + ty_ * off, y - tx_ * off            # off > 0 moves outward (up)
    return (x, y)


def bandtan(t):
    a, b = max(0.0, t - 0.005), min(1.0, t + 0.005)
    p, q = bandpt(a), bandpt(b)
    return _n((q[0] - p[0], q[1] - p[1]))


def leaf_outline(A, d, length, width, bend=0.0):
    """closed polygon of a laurel leaf (for clipping), same shape as leaf_loop"""
    return leaf_loop(A, d, length, width, bend)


def wreath(n=15, t0=0.06, t1=0.975, ang=30, ln=(48, 36), w=(15.5, 12.0)):
    """ONE stroke: the band runs from the knot to the brow and throws a leaf to alternate sides
    at each node, every leaf pointing forward (herringbone laurel).
    Returns (stroke points, leaf polygons, midribs)."""
    pts, polys, ribs = [bandpt(0.0)], [], []
    tprev = 0.0
    for i in range(n):
        t = t0 + (t1 - t0) * i / (n - 1)
        k = i / (n - 1)
        pts += [bandpt(tprev + (t - tprev) * j / 5) for j in range(1, 6)]
        A = pts[-1]
        T_ = bandtan(t)
        up = (T_[1], -T_[0])
        sgn = 1 if i % 2 == 0 else -1
        a = math.radians(ang + (5 if sgn < 0 else 0))
        d = (T_[0] * math.cos(a) + sgn * up[0] * math.sin(a), T_[1] * math.cos(a) + sgn * up[1] * math.sin(a))
        Ln = ln[0] + (ln[1] - ln[0]) * k
        W = w[0] + (w[1] - w[0]) * k
        leaf = leaf_loop(A, d, Ln, W, bend=-sgn * 2.0)
        pts += leaf[1:]
        polys.append(leaf)
        ribs.append(cr_dense([A, (A[0] + d[0] * Ln * 0.45 - sgn * up[0] * 0.8, A[1] + d[1] * Ln * 0.45 - sgn * up[1] * 0.8),
                              (A[0] + d[0] * Ln * 0.82, A[1] + d[1] * Ln * 0.82)], 4))
        tprev = t
    pts += [bandpt(tprev + (1 - tprev) * j / 3) for j in range(1, 4)]
    return pts, polys, ribs


def comma(root, d, length, width, curl=1, bow=0.25):
    """one crescent lock: out along the outer edge to a hooked tip, back along the inner edge.
    d: unit direction root->tip; curl=+1 hooks to the left of d (image coords), -1 to the right."""
    nx, ny = d[1] * curl, -d[0] * curl
    def P(u, v):
        return (root[0] + d[0] * u + nx * v, root[1] + d[1] * u + ny * v)
    Lr, W = length, width
    b = bow * W
    out = cr_dense([P(0, -0.55 * W), P(0.4 * Lr, -0.45 * W + b), P(0.8 * Lr, -0.1 * W + 1.4 * b),
                    P(1.0 * Lr, 0.45 * W + 1.2 * b), P(0.96 * Lr, 1.05 * W + b)], 6)
    back = cr_dense([P(0.96 * Lr, 1.05 * W + b), P(0.82 * Lr, 0.62 * W + b), P(0.45 * Lr, 0.42 * W + 0.7 * b),
                     P(0.08 * Lr, 0.5 * W)], 6)
    return out + back[1:]


def lock_row(roots, dirs, lengths, width, curl=1, bow=0.25):
    """continuous stroke through a row of crescent locks (roots in drawing order)."""
    pts = []
    for r, d, Ln in zip(roots, dirs, lengths):
        pts += comma(r, _n(d), Ln, width, curl, bow)
    return pts


def _spread(p0, p1, n):
    return [lerp(p0, p1, i / (n - 1)) for i in range(n)]


def hair_region():
    back = path_pts(BACK_HAIR, 8)                     # nape -> knot
    crown = path_pts(CROWN, 10)                        # knot side -> front top
    return HAIRLINE[:-1] + back + crown + FRONT_TOP[1:-1]


def flow(p):
    """hair direction at p: radial from the crown whorl, combed forward on top/front, down at the back."""
    rx, ry = _n((p[0] - WHORL[0], p[1] - WHORL[1]))
    t = min(1.0, max(0.0, (p[0] + 175) / 260))
    bx, by = (-0.15 + 0.85 * t, 0.75 - 0.55 * t)
    return _n((rx + bx, ry + by))


def crescent(root, d, length, width, bend=0.25, hook=0.35):
    """crescent lock, root end open: outer edge out to a hooked tip, inner edge back.
    bend > 0 curves the lock to the LEFT of d (image coords); hook curls the tip the same way."""
    nx, ny = d[1], -d[0]
    def P(u, v):
        bb = bend * length * (u / length) ** 2
        return (root[0] + d[0] * u + nx * (v + bb), root[1] + d[1] * u + ny * (v + bb))
    Ln, W = length, width
    outer = [P(Ln * a, -0.5 * W * (1 - a) ** 0.75) for a in (0, 0.25, 0.5, 0.75, 0.97)]
    tip = [P(Ln * 1.04, hook * W), P(Ln * 0.97, (0.25 + 1.6 * hook) * W)]
    inner = [P(Ln * a, 0.5 * W * (1 - a) ** 1.1 + 0.15 * W) for a in (0.82, 0.6, 0.38, 0.16, 0.03)]
    return cr_dense(outer + tip + inner, 4)


def comma_lock(root, d, length, width, bend=0.3, curl=1):
    """a comma-shaped lock: a tapering S-spine from the root that swells into a hooked head; the
    inner edge returns only part way, so the root is a single tail, never a closed U."""
    nx, ny = d[1] * curl, -d[0] * curl
    def P(u, v):
        s = u / length
        bb = bend * length * (s * s - 0.14 * math.sin(math.pi * s))
        return (root[0] + d[0] * u + nx * (v + bb), root[1] + d[1] * u + ny * (v + bb))
    Ln, W = length, width
    spine = [P(Ln * a, -0.12 * W - 0.38 * W * a ** 1.4) for a in (0.0, 0.3, 0.55, 0.78, 0.94)]
    head = [P(Ln * 1.02, 0.05 * W), P(Ln * 0.98, 0.55 * W), P(Ln * 0.86, 0.62 * W)]
    back = [P(Ln * a, 0.42 * W * (1 - (0.9 - a) * 0.6)) for a in (0.72, 0.55, 0.42)]
    return cr_dense(spine + head + back, 4)


def hair_texture(blockers, row_gap=21.0, lock_w=12.0, seed=5):
    """comma locks filling the hair mass in rows that follow the skull, combed along the flow field:
    large over the crown, smaller and tighter at the nape and round the ear (hatch texture).
    blockers: polygons (wreath leaves) that sit over the hair."""
    rnd = random.Random(seed)
    region = hair_region()
    locks = []
    EAR_C = (-38, -45)
    for k in range(1, 28):
        r = 4 + k * row_gap * 0.86
        n = max(6, int(2 * math.pi * r / (lock_w * 1.05)))
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * (k % 2) + rnd.uniform(-0.25, 0.25)) / n
            p = (WHORL[0] + r * math.cos(a) + rnd.uniform(-3, 3), WHORL[1] + r * math.sin(a) + rnd.uniform(-3, 3))
            if not inside(p, region) or any(inside(p, b) for b in blockers):
                continue
            f = 1.25 - 0.55 * min(1.0, max(0.0, (p[1] + 230) / 300))
            de = math.dist(p, EAR_C)
            if de < 80:
                f *= 0.7 + 0.3 * de / 80
            lx, ly = _n((p[0] + 60, p[1] + 110))
            lit = -0.6 * lx - 0.8 * ly
            if rnd.random() < 0.45 * max(0.0, lit) ** 1.2:
                continue
            if math.dist(p, (8, -128)) < 34 and rnd.random() < 0.75:      # worn smooth over the temple
                continue
            d = flow(p)
            Ln = row_gap * 1.9 * f * rnd.uniform(0.8, 1.15)
            W = lock_w * f * rnd.uniform(0.85, 1.1)
            curl = 1 if p[0] > -120 else -1
            c = comma_lock(p, d, Ln, W, bend=rnd.uniform(0.18, 0.34), curl=curl)
            for run in clip_inside(c, region, step=1.5, min_len=6):
                for r2 in clip_outside(run, blockers, step=1.5, min_len=6):
                    locks.append(r2)
    return locks


def stray_locks():
    """a few locks breaking the outline of the hair (detail strokes)"""
    out = []
    for (x, y), (dx, dy), Ln in (((-150, -158), (-0.5, -0.9), 24), ((-178, -60), (-0.9, 0.3), 22),
                                  ((-112, -200), (-0.4, -0.9), 18), ((-152, 42), (-0.7, 0.7), 22)):
        d = _n((dx, dy))
        out.append(comma_lock((x, y), d, Ln, 9, bend=0.3, curl=1 if dx > 0 else -1))
    return out


def hairline_edge(step=17.0, bulge=5.0, seed=21):
    """the hair's boundary against the skin as ONE scalloped stroke: lock tips along the
    temple, the sideburn, round the ear and down to the nape (skin lies left of travel)."""
    rnd = random.Random(seed)
    pts = resample(cr_dense(HAIRLINE, 6), step)
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ln = math.hypot(dx, dy) or 1
        nx, ny = dy / Ln, -dx / Ln                # left normal (toward the skin)
        fd = flow(a)
        k = bulge * rnd.uniform(0.6, 1.25)
        m1 = (a[0] + dx * 0.35 + nx * k * 0.8 + fd[0] * 2, a[1] + dy * 0.35 + ny * k * 0.8 + fd[1] * 2)
        m2 = (a[0] + dx * 0.78 + nx * k + fd[0] * 3, a[1] + dy * 0.78 + ny * k + fd[1] * 3)
        q = (b[0] + nx * 0.6, b[1] + ny * 0.6)
        out += bez3(a, m1, m2, q, 8)[1:]
    return out


def fringe():
    """the fringe over the brow: five comma locks combed forward, tips hooking up (ONE stroke)."""
    roots = [(78, -168), (96, -172)]
    dirs = [(0.62, 0.78), (0.5, 0.86)]
    lens = [36, 30]
    pts = []
    for r, d, Ln in zip(roots, dirs, lens):
        pts += crescent(r, _n(d), Ln, 12, bend=0.26, hook=0.45)
    return pts


def nape_locks():
    """the long Claudian locks curling over the nape (ONE stroke)."""
    roots = [(-168, 4), (-153, 16), (-138, 26), (-122, 34), (-107, 42)]
    dirs = [(-0.28, 1), (-0.2, 1), (-0.12, 1), (-0.04, 1), (0.04, 1)]
    lens = [44, 46, 44, 40, 34]
    pts = []
    for r, d, Ln in zip(roots, dirs, lens):
        pts += crescent(r, _n(d), Ln, 12, bend=0.32, hook=0.7)
    return pts


def ribbon(cl, w=9.0, cut=True):
    """flat wavy ribbon round a centre line, ONE stroke: down one edge, across a V-cut end, up the other."""
    c = resample(cr_dense(cl, 8), 3.0)
    left, right = [], []
    for i, p in enumerate(c):
        a = c[max(0, i - 1)]; b = c[min(len(c) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ln = math.hypot(dx, dy) or 1
        k = w / 2 * (0.75 + 0.25 * math.cos(i / len(c) * 9.0))       # slight twist
        left.append((p[0] + dy / Ln * k, p[1] - dx / Ln * k))
        right.append((p[0] - dy / Ln * k, p[1] + dx / Ln * k))
    end = c[-1]; pre = c[-4]
    notch = (end[0] - (end[0] - pre[0]) * 0.9, end[1] - (end[1] - pre[1]) * 0.9) if cut else end
    return left + [notch] + list(reversed(right))


def ties():
    """the knot and the two ribbon ends of the wreath, hanging behind the head."""
    knot = ell_pts(-172, -116, 8, 10, 200, 560, 16)
    r1 = ribbon([(-176, -110), (-190, -84), (-194, -56), (-202, -28), (-200, 4), (-206, 36), (-198, 70), (-188, 100)], 9.5)
    r2 = ribbon([(-180, -114), (-200, -100), (-214, -78), (-218, -50), (-228, -22), (-226, 12), (-232, 40)], 8.5)
    return [knot + r1, r2]


# ------------------------------------------------------------------ REVERSE: Livia as Pax seated right
# coin units; ground (exergue) line y=165, head top y=-192 (8 heads), sceptre at x=128.
def _cr(pts, closed=False):
    return smooth_d(pts, closed)


def smooth_d(pts, closed=False):
    from lib_v2 import smooth
    return smooth(pts, closed=closed)


RV_PTS = {
    # seat -> back -> nape -> hair bun -> crown -> face profile -> chin -> throat -> chest -> bust -> waist
    "body_upper": [(-70, 36), (-58, 6), (-48, -36), (-44, -80), (-42, -120), (-34, -150), (-22, -170),
                   (-27, -175), (-37, -178), (-41, -190), (-33, -201), (-21, -200), (-17, -213), (-5, -227),
                   (11, -229), (21, -223), (25, -214), (27, -208), (29, -203), (33, -198), (35, -195), (32, -193),
                   (30, -192), (31, -189), (30, -187), (29, -184), (27, -181), (22, -178), (16, -177), (14, -170),
                   (20, -159), (30, -143), (33, -132), (28, -121), (21, -104), (22, -86), (30, -70), (50, -60)],
    # lap -> knee -> drapery down the shins -> hem -> sandalled foot on the stool
    "body_lower": [(50, -60), (80, -56), (106, -54), (118, -47), (122, -34), (122, 0), (123, 50), (125, 100),
                   (127, 138), (129, 151), (139, 154), (151, 157), (154, 161), (146, 163), (124, 163), (104, 162)],
    # far (right) arm reaching to the sceptre (clipped where it passes behind the breast)
    "arm": [(6, -168), (30, -163), (56, -156), (88, -163), (118, -172), (138, -178), (147, -182), (157, -181),
            (160, -175), (156, -169), (146, -166), (136, -166), (110, -158), (82, -148), (62, -140), (40, -142),
            (24, -148), (18, -152)],
    # near (left) arm wrapped in the mantle; forearm across the lap; the hand holds the branch
    "near_arm": [(-20, -101), (4, -93), (30, -83), (50, -76), (60, -76), (66, -70), (62, -63), (52, -61),
                 (32, -65), (6, -75), (-18, -85), (-27, -92), (-20, -101)],
    # back edge of the drapery falling from the knees, and the hem
    "shins": [(30, 50), (52, 40), (70, 28), (80, 34), (82, 70), (83, 110), (86, 150), (104, 154), (128, 152)],
}
RV = {
    "sceptre": "M 154 -258 L 154 198",
    "finial": "M 154 -258 C 148 -261 148 -269 154 -275 C 160 -269 160 -261 154 -258 M 147 -255 L 161 -255",
    "seat": "M -110 38 C -70 34 -10 34 34 37 C 38 40 38 46 34 50 C -10 51 -70 51 -110 50 C -114 47 -114 41 -110 38",
    # turned (baluster) chair legs, each ONE stroke down one side and up the other, and a stretcher
    "ground": "M -150 198 L 150 198",
    "stool": "M 92 163 L 168 163 L 168 176 L 92 176 Z M 98 176 L 96 198 M 162 176 L 164 198",
    "eye": "M 17 -203 C 19 -206 23 -206 26 -203 C 23 -201 20 -201 17 -203",
    "brow": "M 15 -209 C 19 -211 24 -211 28 -209",
    "mouth": "M 30 -187 C 28 -187 25 -187 23 -186 M 28 -192 C 26 -191 25 -190 25 -189",
    "ear": "M 1 -201 C -5 -202 -6 -194 -3 -189 C -1 -186 2 -187 3 -189",
    # hair: waves over the brow, and the coil of the bun at the nape
    "hair": ("M 24 -219 C 20 -216 22 -212 18 -210 C 14 -208 16 -204 12 -202 "
             "M -30 -186 C -37 -186 -38 -194 -32 -197 C -26 -199 -22 -192 -27 -189"),
    # the palla: its edge across the breast, the folds over the lap, the cascade over the shins,
    # the fall over the near arm, and the folds swept round the hips
    "mantle": ("M -16 -166 C -6 -148 4 -126 10 -104 C 14 -90 12 -80 4 -72 "
               "M 30 -48 C 56 -42 86 -40 116 -36 "
               "M 26 -36 C 52 -24 84 -18 120 -16 "
               "M 98 -18 C 100 20 100 60 100 100 "
               "M 112 -14 C 114 30 114 70 114 102 "
               "M 84 100 C 90 110 96 98 102 106 C 108 114 114 102 122 108 "
               "M -14 -166 C -24 -150 -28 -124 -25 -100 "
               "M -44 -24 C -22 -40 4 -50 30 -54 "
               "M -52 4 C -24 -14 10 -26 44 -30"),
    # sleeve of the chiton on the arm that reaches to the sceptre
    "sleeve": ("M 40 -158 C 36 -150 38 -142 44 -136 M 28 -162 C 28 -156 30 -150 34 -146 "
               "M 52 -156 C 50 -150 52 -144 56 -140"),
    "fist": "M 147 -183 C 151 -179 151 -172 147 -168 M 141 -181 C 144 -177 144 -171 141 -167",
}


def baluster(x, y0, y1, w=3.6, rings=(0.08, 0.36, 0.64, 0.9)):
    """turned chair leg, ONE stroke: down the left side with its rings, across the foot, up the right."""
    def side(sgn):
        pts = [(x + sgn * w * 1.3, y0)]
        for t in rings:
            y = y0 + (y1 - y0) * t
            pts += [(x + sgn * w, y - 5), (x + sgn * (w + 2.6), y - 2), (x + sgn * (w + 2.6), y + 2), (x + sgn * w, y + 5)]
        pts += [(x + sgn * w * 0.9, y1 - 6), (x + sgn * (w + 1.5), y1)]
        return pts
    left = side(-1)
    right = list(reversed(side(1)))
    return left + right


def hair_waves():
    """strands combed back from the brow over the dome of the head, converging into the bun (hatch)"""
    S = [[(22, -220), (12, -227), (-4, -228), (-17, -220), (-25, -206), (-29, -195)],
         [(21, -215), (10, -222), (-6, -221), (-19, -212), (-27, -200)],
         [(19, -210), (8, -216), (-7, -214), (-19, -205), (-28, -196)],
         [(16, -205), (6, -209), (-6, -206), (-18, -199), (-28, -192)]]
    return [cr_dense(s, 5) for s in S]


def branch(base=(62, -70), tip=(110, -126), n=4, seed=3):
    """olive branch held up from the hand: stem with paired narrow leaves, ONE stroke."""
    d = _n((tip[0] - base[0], tip[1] - base[1]))
    Ln = math.dist(base, tip)
    pts = [base]
    for i in range(n):
        t = (i + 1) / (n + 0.6)
        A = (base[0] + d[0] * Ln * t, base[1] + d[1] * Ln * t)
        pts.append(A)
        for sgn in (1, -1):
            a = math.radians(40 * sgn)
            dd = (d[0] * math.cos(a) - d[1] * math.sin(a), d[0] * math.sin(a) + d[1] * math.cos(a))
            pts += leaf_loop(A, dd, 16 - 1.2 * i, 4.0, 0)[1:]
    pts.append(tip)
    pts += leaf_loop(tip, d, 14, 3.8, 0)[1:]
    return pts


def reverse_shading():
    """relief modelling on the seated figure (hatch, coin units)."""
    S = []
    front = cr_dense(RV_PTS["body_upper"][28:] + RV_PTS["body_lower"][1:], 8)
    S += contour_shadow(front, 9, side=1, seed=31)
    S += contour_shadow(cr_dense(RV_PTS["arm"][8:14], 8), 7, side=-1, seed=32)
    S += contour_shadow(cr_dense(RV_PTS["body_upper"][:7], 8), 5, side=-1, seed=40)
    # under the thighs, the inner side of the lower legs, the far side of the bust
    S += comb([(34, 50), (54, 40), (72, 30)], _n((0.15, -1)), 9, 3.6, seed=33)
    S += comb([(84, 24), (85, 70), (86, 120)], _n((1, 0.12)), 10, 4.0, seed=34, taper=0.6)
    S += comb([(-38, -130), (-40, -96), (-43, -60), (-50, -24)], _n((1, 0.3)), 12, 5.0, seed=35)
    # folds over the lap and down the legs
    S += comb([(40, -48), (70, -40), (100, -34)], _n((0.3, 1)), 10, 4.2, seed=36)
    S += comb([(106, -6), (108, 50), (110, 100), (112, 146)], _n((1, 0.05)), 8, 5.0, seed=37, taper=0.5)
    # the seat cushion, the stool and the chair legs in shadow
    S += hatch(cr_dense([(-110, 50), (34, 50), (30, 56), (-108, 56)], 2, closed=True), 60, 3.0, seed=38, min_len=1.5)
    S += hatch([(92, 176), (168, 176), (168, 181), (92, 181)], 60, 3.0, seed=39, min_len=1.5)
    S += comb([(-95, 56), (-96, 110), (-96, 190)], _n((1, 0.1)), 6, 4.0, seed=41, taper=0.3)
    S += comb([(29, 56), (28, 110), (29, 190)], _n((1, 0.1)), 6, 4.0, seed=42, taper=0.3)
    # chiton folds on the breast, hair
    S += comb([(-6, -150), (2, -130), (8, -112)], _n((-0.6, 0.8)), 14, 5.0, seed=43)
    S += hair_waves()
    # fine folds of the chiton falling from under the palla to the feet
    S += [cr_dense([(x, 112), (x + 1, 130), (x + 2, 148)], 3) for x in (88, 96, 104, 112, 120)]
    # folds of the palla over the back and the hips
    S += [cr_dense([(-40 + 4 * k, -130 + 6 * k), (-46 + 4 * k, -90 + 6 * k), (-50 + 4 * k, -50 + 6 * k)], 4) for k in range(3)]
    return S


LIGHT_AWAY = _n((0.55, 0.83))        # light from the upper left: shadows fall down-right


def contour_shadow(pts, w0, side=1, spacing=3.4, angle=-38, min_w=1.2, seed=2):
    """cast shadow of a raised edge on the field: a band outside the contour, wide where the edge
    faces away from the light. side=+1 puts the band to the LEFT of travel (image coords)."""
    P = resample(pts, 3.0)
    outer = []
    for i, p in enumerate(P):
        a = P[max(0, i - 1)]; b = P[min(len(P) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ln = math.hypot(dx, dy) or 1
        nx, ny = side * dy / Ln, -side * dx / Ln
        k = max(0.0, nx * LIGHT_AWAY[0] + ny * LIGHT_AWAY[1])
        w = w0 * k ** 1.3
        outer.append((p[0] + nx * w, p[1] + ny * w, w))
    # keep only the stretches where the band is wider than min_w
    segs, cur = [], []
    for p, o in zip(P, outer):
        if o[2] >= min_w:
            cur.append((p, (o[0], o[1])))
        else:
            if len(cur) > 3:
                segs.append(cur)
            cur = []
    if len(cur) > 3:
        segs.append(cur)
    out = []
    for sg in segs:
        poly = [p for p, _ in sg] + [o for _, o in reversed(sg)]
        out += hatch(poly, angle, spacing, jitter=0.25, seed=seed, min_len=1.5)
    return out


def shade_patch(poly, angle, spacing, seed=4, shorten=0.12, fade=0.32):
    """soft hatch patch: rounded outline, ragged ends, rows dissolving toward the patch ends."""
    soft = cr_dense(poly, 6, closed=True)
    return hatch(soft, angle, spacing, jitter=0.35, seed=seed, min_len=2.5, shorten=shorten, fade=fade)


def comb(guide, d, length, spacing=4.2, seed=1, taper=0.85, jitter=0.25):
    """strokes hanging from a guide line in direction d (unit), longest mid-guide and tapering
    toward both ends: the hatching an engraver lays under a jaw or a brow."""
    rnd = random.Random(seed)
    G = resample(cr_dense(guide, 6), spacing)
    out = []
    n = len(G)
    for i, p in enumerate(G):
        f = math.sin(math.pi * (i + 0.5) / n) ** taper
        Ln = length * f * rnd.uniform(0.75, 1.1)
        if Ln < 2.5:
            continue
        a = rnd.uniform(-jitter, jitter)
        dx = d[0] * math.cos(a) - d[1] * math.sin(a); dy = d[0] * math.sin(a) + d[1] * math.cos(a)
        out.append([p, (p[0] + dx * Ln, p[1] + dy * Ln)])
    return out


def obverse_shading():
    """relief modelling on the head (hatch polylines, coin units)."""
    S = []
    # the field shadow along the face, chin, throat and neck front, and under the truncation
    prof = path_pts(PROFILE, 12)
    S += contour_shadow(prof, 11, side=1, seed=3)
    trunc = path_pts("M 76 214 C 28 223 -46 223 -100 207", 12)
    S += contour_shadow(list(reversed(trunc)), 9, side=-1, seed=4)
    # under the jaw: strokes hanging from the line of the mandible onto the upper neck
    S += comb([(126, 100), (98, 100), (62, 90), (30, 78), (6, 64), (-8, 48)], _n((0.25, 1)), 36, 4.0, seed=5)
    # front of the neck: a soft band inside the contour
    S += shade_patch([(91, 136), (91, 158), (86, 182), (80, 200), (76, 212), (60, 212), (68, 186), (74, 160),
                      (80, 140)], 72, 4.6, seed=6)
    # under the nape locks the neck sinks into shadow
    S += comb([(-90, 96), (-84, 102), (-78, 110)], _n((0.12, 1)), 36, 3.6, seed=7, taper=0.4)
    # the long neck muscle, softly, from behind the ear toward the pit of the throat
    S += comb([(-24, 30), (0, 80), (24, 130), (44, 182)], _n((0.95, 0.3)), 12, 6.0, seed=14, taper=1.0)
    # eye socket: short strokes under the brow
    S += comb([(100, -91), (116, -95), (132, -95), (140, -92)], _n((0.25, 1)), 9, 3.0, seed=8)
    # temple hollow
    S += comb([(66, -100), (80, -102), (94, -96)], _n((0.4, 1)), 14, 3.8, seed=9)
    # cheek: a few soft strokes under the cheekbone
    S += comb([(92, -34), (104, -24), (114, -8), (118, 8)], _n((-0.55, 0.85)), 22, 5.0, seed=10, taper=1.2)
    # under the nose and below the lower lip
    S += shade_patch([(150, 8), (160, 7), (168, 6), (160, 11), (152, 12)], 20, 2.6, seed=11, fade=0.1)
    S += shade_patch([(137, 46), (143, 46), (141, 54), (135, 56)], 10, 2.6, seed=12, fade=0.1)
    # behind the ear lobe
    S += comb([(-16, -32), (-12, -16), (-16, 0)], _n((0.7, 0.7)), 10, 3.2, seed=13)
    return S


class Coin:
    """maps coin units onto the board: centre (cx, cy), die radius R."""

    def __init__(self, cx, cy, R, seed=7):
        self.cx, self.cy, self.R = cx, cy, R
        self.s = R / R0
        self.rnd = random.Random(seed)

    # transforms ---------------------------------------------------------
    def P(self, pts):
        return [(self.cx + x * self.s, self.cy + y * self.s) for x, y in pts]

    def d(self, d):
        return tx(d, self.s, self.cx, self.cy)

    def pd(self, pts, closed=False, eps=0.2):
        return poly_d(self.P(pts), closed, eps)

    # flan and die -------------------------------------------------------
    def flan_pts(self, r=345.0, wobble=7.0, seed=11, off=(0, 0)):
        """slightly irregular hammered-silver flan outline (coin units)."""
        rnd = random.Random(seed)
        k = [rnd.uniform(-1, 1) for _ in range(5)]
        ph = [rnd.uniform(0, 6.28) for _ in range(5)]
        pts = []
        for i in range(73):
            a = 2 * math.pi * i / 72
            rr = r + wobble * (0.55 * k[0] * math.cos(2 * a + ph[0]) + 0.35 * k[1] * math.cos(3 * a + ph[1])
                               + 0.2 * k[2] * math.cos(5 * a + ph[2]))
            pts.append((off[0] + rr * math.cos(a), off[1] + rr * math.sin(a)))
        return pts

    def edge(self, flan, depth=(5.0, 9.0), a0=-25, a1=165):
        """the visible thickness of the flan on the shadow side: an offset contour joined to the flan
        (coin units in, coin units out). Returns (contour, band polygon)."""
        n = len(flan) - 1
        def ang(p):
            return math.degrees(math.atan2(p[1], p[0]))
        idx = [i for i in range(n) if a0 <= ang(flan[i]) <= a1]
        seg = [flan[i] for i in sorted(idx, key=lambda i: ang(flan[i]))]
        m = len(seg)
        off = []
        for j, p in enumerate(seg):
            k = math.sin(math.pi * j / (m - 1)) ** 0.6
            off.append((p[0] + depth[0] * k, p[1] + depth[1] * k))
        contour = cr_dense(off, 6)
        band = cr_dense(seg, 6) + list(reversed(contour))
        return contour, band

    def board_shadow(self, contour, w=16.0):
        """soft cast shadow on the board below the coin's edge (hatch polylines, coin units)."""
        P = resample(contour, 3.0)
        m = len(P)
        outer = []
        for j, p in enumerate(P):
            k = math.sin(math.pi * j / (m - 1)) ** 1.4
            r = math.hypot(*p) or 1
            outer.append((p[0] + p[0] / r * w * k + 3 * k, p[1] + p[1] / r * w * k + 6 * k))
        poly = P + list(reversed(outer))
        return hatch(poly, -50, 4.2, jitter=0.4, seed=17, min_len=2.0, shorten=0.15, fade=0.3)

    def wear(self, seed=23):
        """light scratches and nicks on the field, and a small flan crack at the edge (coin units)."""
        rnd = random.Random(seed)
        out = []
        for (cx_, cy_, a0, n) in ((-232, 150, 30, 2), (214, -146, 60, 2), (-30, 150, -40, 2), (176, 150, 10, 2)):
            a = math.radians(a0)
            for k in range(n):
                o = (k - n / 2) * 4.0
                p0 = (cx_ - math.cos(a) * 16 - math.sin(a) * o, cy_ - math.sin(a) * 16 + math.cos(a) * o)
                p1 = (cx_ + math.cos(a) * 16 - math.sin(a) * o + rnd.uniform(-2, 2), cy_ + math.sin(a) * 16 + math.cos(a) * o)
                mid = ((p0[0] + p1[0]) / 2 + rnd.uniform(-2, 2), (p0[1] + p1[1]) / 2 + rnd.uniform(-2, 2))
                out.append(cr_dense([p0, mid, p1], 4))
        # a hairline crack running in from the edge (common on hammered silver)
        a = math.radians(-128)
        c0 = (345 * math.cos(a), 345 * math.sin(a))
        out.append([c0, (c0[0] + 9, c0[1] + 6), (c0[0] + 13, c0[1] + 15), (c0[0] + 21, c0[1] + 19)])
        return out

    def beads(self, r=330.0, dia=7.0, gap=13.5):
        """beaded border as ONE dashed pen stroke (zero-length dashes with round caps = dots)."""
        R = r * self.s
        circ = 2 * math.pi * R
        n = max(12, int(round(circ / gap)))
        g = circ / n
        d = tx(_circle_d(r), self.s, self.cx, self.cy)
        sw = max(2.4, dia * self.s)
        return (f'  <path class="detail" style="stroke-width:{f1(sw)};stroke-dasharray:0 {f1(g)}" d="{d}"/>\n')


def _circle_d(r):
    from lib_v2 import circle
    return circle(0, 0, r, start_deg=-90)
