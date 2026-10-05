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
           "C 142 -71 150 -56 158 -41 C 165 -29 171 -18 175 -9 C 178 -3 176 3 170 5 "
           "C 163 7 155 6 148 8 C 148 13 150 17 152 21 C 153 24 151 27 147 28 "
           "C 150 30 150 34 148 38 C 146 42 142 44 141 47 C 144 53 149 60 149 68 "
           "C 149 79 142 86 130 89 C 117 92 105 97 96 104 C 90 112 89 124 90 137 "
           "C 91 149 91 158 87 171 C 82 186 77 200 74 214")
BACK_NECK = "M 74 214 C 28 222 -42 222 -90 206 C -82 184 -74 164 -70 146 C -67 126 -72 104 -84 90"
BACK_HAIR = ("M -84 90 C -88 99 -99 101 -104 90 C -110 99 -121 98 -124 86 C -131 94 -141 90 -143 77 "
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
# hairline: front of the fringe -> temple -> sideburn -> round the ear -> nape
HAIRLINE = [(124, -150), (114, -143), (101, -133), (89, -121), (74, -113), (54, -109), (33, -104), (19, -93),
            (13, -74), (10, -54), (3, -45), (-7, -55), (-11, -78), (-22, -93), (-40, -99), (-57, -93),
            (-67, -79), (-71, -57), (-73, -32), (-76, -6), (-79, 24), (-80, 56), (-84, 90)]
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


def hair_texture(blockers, row_gap=20.0, lock_w=12.0, seed=5):
    """staggered rows of crescent locks on arcs round the crown whorl, each lock combed along
    the flow field (hatch texture). blockers: polygons (wreath leaves) to keep clear of."""
    rnd = random.Random(seed)
    region = hair_region()
    locks = []
    for k in range(1, 22):
        r = 6 + k * row_gap
        n = max(6, int(2 * math.pi * r / lock_w))
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * (k % 2)) / n
            p = (WHORL[0] + r * math.cos(a) + rnd.uniform(-1.5, 1.5), WHORL[1] + r * math.sin(a) + rnd.uniform(-1.5, 1.5))
            if not inside(p, region) or any(inside(p, b) for b in blockers):
                continue
            lx, ly = _n((p[0] + 60, p[1] + 110))
            lit = -0.6 * lx - 0.8 * ly                     # 1 = facing the light (upper left)
            if rnd.random() < 0.55 * max(0.0, lit) ** 1.2:
                continue
            d = flow(p)
            Ln = row_gap * rnd.uniform(1.2, 1.4)
            bend = (0.22 if p[0] > -120 else -0.22) * rnd.uniform(0.7, 1.2)
            c = crescent(p, d, Ln, lock_w * rnd.uniform(0.85, 1.05), bend)
            for run in clip_inside(c, region, step=1.5, min_len=6):
                for r2 in clip_outside(run, blockers, step=1.5, min_len=6):
                    locks.append(r2)
    return locks


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
    r1 = ribbon([(-176, -110), (-188, -84), (-190, -58), (-199, -32), (-197, -6), (-205, 18)], 9.5)
    r2 = ribbon([(-180, -114), (-199, -100), (-211, -80), (-214, -56), (-225, -34)], 8.5)
    return [knot + r1, r2]


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
    trunc = path_pts("M 74 214 C 28 222 -48 222 -100 208", 12)
    S += contour_shadow(list(reversed(trunc)), 9, side=-1, seed=4)
    # under the jaw: strokes hanging from the line of the mandible onto the upper neck
    S += comb([(124, 92), (96, 92), (60, 82), (28, 70), (4, 58), (-8, 44)], _n((0.25, 1)), 34, 4.0, seed=5)
    # front of the neck: a soft band inside the contour
    S += shade_patch([(90, 134), (90, 156), (84, 180), (78, 200), (73, 212), (58, 212), (66, 186), (72, 160),
                      (78, 138)], 72, 4.6, seed=6)
    # under the nape locks the neck sinks into shadow
    S += comb([(-84, 96), (-77, 101), (-71, 108)], _n((0.12, 1)), 36, 3.6, seed=7, taper=0.4)
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
