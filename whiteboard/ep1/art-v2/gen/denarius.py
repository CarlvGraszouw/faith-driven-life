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
# Front profile: forehead (under the fringe) -> brow -> nose -> lips -> chin -> throat -> neck -> truncation
PROFILE = ("M 110 -127 C 116 -113 121 -99 123 -86 C 124 -77 122 -71 118 -66 "
           "C 122 -58 128 -45 135 -33 C 141 -22 147 -12 151 -4 C 153 1 151 6 146 8 "
           "C 140 10 133 9 128 10 C 128 14 130 18 133 21 C 134 23 132 26 128 27 "
           "C 131 29 132 33 130 37 C 128 41 123 42 121 45 C 123 50 127 56 127 62 "
           "C 127 70 121 76 112 78 C 101 80 90 83 82 89 C 75 96 72 108 72 120 "
           "C 72 130 76 137 76 145 C 76 153 71 161 69 172 C 67 184 66 196 66 207")
# skull above the wreath: from just above the wreath's front leaves, over the crown, to the knot
CROWN = "M 84 -176 C 66 -198 34 -213 -6 -214 C -54 -215 -98 -194 -122 -160 C -132 -146 -138 -130 -140 -116"
# back of the head below the wreath (lumpy locks) -> nape -> back of neck -> truncation -> front of neck
BACK = ("M -150 -96 C -160 -78 -163 -56 -158 -36 C -156 -24 -150 -16 -152 -4 C -151 10 -142 20 -136 30 "
        "C -128 42 -116 46 -104 46 C -100 70 -97 110 -96 150 C -96 175 -96 192 -97 207 "
        "C -60 214 30 214 66 207")
EAR = ("M -8 -55 C -18 -68 -40 -68 -49 -52 C -57 -38 -53 -14 -45 2 C -41 11 -33 15 -25 11 "
       "C -19 8 -16 2 -15 -5")
EAR_IN = ("M -17 -47 C -32 -52 -41 -40 -38 -24 C -36 -14 -31 -8 -26 -11 "
          "M -11 -27 C -6 -22 -6 -15 -10 -11")
EYE = "M 89 -57 C 95 -63 105 -63 112 -59 C 111 -56 110 -54 109 -52 C 103 -51 96 -52 91 -54"
BROW = "M 88 -71 C 98 -75 112 -77 122 -77 M 93 -64 C 100 -68 108 -68 114 -64"
IRIS = "M 106 -61 C 104 -58 104 -55 106 -53"
NOSE = "M 140 7 C 133 6 127 2 127 -4 C 127 -10 133 -12 138 -8"
MOUTH = "M 128 27 C 124 27 119 28 114 31 M 121 46 C 118 47 115 47 112 46"
CHEEK = "M 124 5 C 118 12 114 20 113 27 M 103 77 C 80 72 40 60 10 48 C 2 44 -4 30 -8 14"
NECK = "M -40 22 C -20 70 15 140 46 200"


def _band(t):
    """laurel band centre line, t=0 at the knot (back) .. 1 at the front"""
    return bez3((-140, -102), (-78, -170), (30, -190), (98, -160), 1)[0] if False else _bandpt(t)


def _bandpt(t):
    p0, p1, p2, p3 = (-140, -102), (-76, -172), (34, -190), (99, -160)
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])


def wreath_rows(n_up=9, n_dn=8):
    """two continuous strokes: the upper and lower rows of laurel leaves on the band."""
    rows = []
    for side, n, off, ang, ln, w in (("up", n_up, -2.5, 38, 42, 9.5), ("dn", n_dn, 3.0, 40, 38, 8.5)):
        pts = []
        ts = [0.04 + 0.93 * i / (n - 1) for i in range(n)]
        if side == "dn":
            ts = [t + 0.035 for t in ts[:-1]] + [min(0.995, ts[-1] + 0.01)]
        prev_t = 0.0
        for i, t in enumerate(ts):
            # band from prev_t to t
            seg = [_bandpt(prev_t + (t - prev_t) * k / 6) for k in range(7)]
            tang = _n((_bandpt(min(1, t + 0.01))[0] - _bandpt(max(0, t - 0.01))[0],
                       _bandpt(min(1, t + 0.01))[1] - _bandpt(max(0, t - 0.01))[1]))
            nup = (tang[1], -tang[0])                       # outward (up) normal
            sgn = 1 if side == "up" else -1
            shift = (nup[0] * off * -1, nup[1] * off * -1)
            seg = [(x + shift[0], y + shift[1]) for x, y in seg]
            A = seg[-1]
            a = math.radians(ang)
            d = (tang[0] * math.cos(a) + sgn * nup[0] * math.sin(a), tang[1] * math.cos(a) + sgn * nup[1] * math.sin(a))
            k = 1.0 - 0.25 * (i / max(1, n - 1)) ** 2        # leaves a little smaller toward the front
            leaf = leaf_loop(A, d, ln * k, w * k, bend=-sgn * 2.0)
            pts += (seg if not pts else seg[1:]) + leaf[1:]
            prev_t = t
        rows.append(pts)
    return rows


def ties():
    """the two ribbon ends of the wreath, hanging from the knot behind the head (one stroke each)."""
    r1 = cr_dense([(-142, -98), (-150, -70), (-147, -40), (-156, -10), (-152, 18), (-160, 40)], 8)
    r1b = cr_dense([(-160, 40), (-150, 44), (-142, 38), (-138, 14), (-141, -12), (-134, -42), (-136, -72), (-134, -96)], 8)
    r2 = cr_dense([(-146, -96), (-166, -80), (-180, -56), (-178, -30), (-190, -6)], 8)
    r2b = cr_dense([(-190, -6), (-181, -2), (-170, -14), (-168, -36), (-160, -60), (-150, -84)], 8)
    knot = ell_pts(-140, -100, 7, 9, 200, 560, 16)
    return [knot + r1 + r1b[1:], r2 + r2b[1:]]


def hair_rows():
    """crescent locks, one continuous stroke per row (roots tucked under the wreath)."""
    rows = []
    # fringe over the forehead: locks combed forward/down, tips hooking forward
    fr = [((60, -150), (70, -152), (82, -128), (8, 3)),
          ((72, -153), (83, -156), (98, -128), (8, 2)),
          ((85, -157), (95, -158), (111, -130), (6, 1))]
    # temple and side, in front of and above the ear
    sd = [((-6, -150), (6, -152), (12, -94), (9, 4)),
          ((8, -152), (20, -153), (32, -98), (9, 3)),
          ((22, -154), (34, -154), (52, -104), (9, 2)),
          ((36, -155), (48, -155), (66, -114), (8, 1)),
          ((14, -96), (24, -98), (24, -52), (7, 4))]
    # back of the head below the wreath, down to the nape
    bk = [((-128, -110), (-118, -118), (-150, -58), (-6, 10)),
          ((-112, -124), (-100, -130), (-136, -30), (-6, 10)),
          ((-94, -134), (-82, -138), (-118, -4), (-4, 10)),
          ((-76, -142), (-64, -146), (-92, -64), (-2, 9)),
          ((-58, -147), (-46, -150), (-62, -76), (2, 9)),
          ((-40, -150), (-28, -152), (-30, -82), (5, 8)),
          ((-120, -40), (-110, -44), (-124, 26), (-4, 9)),
          ((-100, -30), (-90, -36), (-104, 34), (-2, 9))]
    # crown above the wreath, radiating from the whorl toward the brow
    cr = [((-70, -188), (-62, -194), (-14, -200), (8, 6)),
          ((-56, -182), (-48, -186), (8, -192), (8, 7)),
          ((-40, -176), (-32, -180), (30, -186), (8, 8)),
          ((-24, -170), (-16, -173), (52, -177), (8, 8)),
          ((-90, -176), (-82, -183), (-60, -207), (6, -2)),
          ((-104, -162), (-98, -170), (-108, -196), (-4, -4))]
    for group, bow in ((fr, 4), (sd, 4), (bk, -5), (cr, 3)):
        pts = []
        for b0, b1, tip, curl in group:
            t = tuft(b0, b1, tip, curl, bow)
            pts += t if not pts else t
        rows.append(pts)
    return rows


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
