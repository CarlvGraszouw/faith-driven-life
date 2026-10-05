"""b03-image-belongs: "If the coin with Caesar's image belongs to Caesar, then the person with God's
image belongs to God. That means you, every part of you, on every day of the week."

part a (0.3 s): the two images: the denarius with Caesar's head (top row) and an ordinary person
                with a hand on her heart (middle row).
part b (3.8 s): a short arrow from the coin toward the written word "Caesar" (frame 1228,226).
part c (6.2 s): a short arrow from the person toward the written word "God" (frame 1180,478),
                and a soft radiance round her (hatch).
part d (7.3 s): a week strip M T W T F S S in Roman capitals, every day ticked.
The word zones (art x 900-1260 / y 150-300 and x 920-1140 / y 410-560) stay empty."""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from lib_v2 import L, D, H, svg, write, BLUE  # noqa: E402
from inkgeom import poly_d, cr_dense, clip_outside, path_pts, hatch, ell_pts  # noqa: E402
import denarius as dn  # noqa: E402
import roman_caps as rc  # noqa: E402

OUT = os.path.join(HERE, "..", "B")
COIN = dn.Coin(585, 232, 92)
CAESAR_Y, GOD_Y = 236, 500          # word baselines/centres in art units (frame 226 / 478)


def C(pts, n=6, closed=False):
    return cr_dense(pts, n, closed=closed)


# ---------------------------------------------------------------- part a: the coin
def coin_svg():
    c = COIN
    b = ""
    flan = c.flan_pts(seed=8)
    b += f'  <path class="line" fill="{BLUE}" fill-opacity="0.32" style="mix-blend-mode:multiply" d="{c.pd(flan, True)}"/>\n'
    wr, leaves, ribs = dn.wreath(n=9)
    b += L(c.d(dn.PROFILE)) + L(c.d(dn.BACK))
    for run in clip_outside(path_pts(dn.CROWN, 14), leaves, step=1.5, min_len=6):
        b += L(c.pd(run))
    b += D(c.pd(wr)) + D(c.d(dn.EAR)) + D(c.d(dn.EYE + " " + dn.BROW))
    return b


def coin_hatch():
    c = COIN
    out = [c.pd(r) for r in dn.hair_texture(dn.wreath(n=9)[1], row_gap=30, lock_w=18)]
    out += [c.pd(s, eps=0) for s in dn.obverse_shading()]
    for d in rc.strokes_to_d(rc.on_arc("TI CAESAR DIVI AVG F AVGVSTVS", c.cx, c.cy, 258 * c.s, 50 * c.s, -147, 147,
                                       squeeze=0.86)):
        out.append(d)
    contour, band = c.edge(c.flan_pts(seed=8))
    out += [c.pd(s, eps=0) for s in dn.hatch(band, 70, 3.0 / c.s, seed=19, min_len=1.0)]
    beads = ell_pts(c.cx, c.cy, 330 * c.s, 330 * c.s, -90, 270, 120)
    out.append(" ".join(poly_d([beads[i], beads[i + 1]], eps=0) for i in range(0, 120, 2)))
    return out, contour


# ---------------------------------------------------------------- part a: the person (God's image)
# A living face beside the coin's portrait: a young woman of today, three-quarter view toward the
# right, looking a little upward. Local units: head centre (0,0), head 96 tall.
BUST_AT, BUST_ROT, BUST_S = (556, 470), -7, 1.0
B = {
    # hair falling behind the shoulder, over the crown, then the far side of the face down to the chin
    # and back along the near jaw to the ear: ONE stroke
    "head": [(-62, 100), (-50, 72), (-46, 44), (-44, 12), (-41, -22), (-29, -43), (-8, -54), (14, -53),
             (25, -46), (31, -35), (34, -23), (35, -14), (33, -7), (36, 2), (35, 12), (32, 24), (28, 34),
             (22, 42), (14, 47), (4, 46), (-6, 41), (-15, 32), (-21, 21), (-24, 10), (-25, 2)],
    "neck_near": [(-104, 132), (-86, 108), (-56, 98), (-30, 90), (-22, 74), (-20, 30)],
    "neck_far": [(12, 50), (14, 70), (24, 84), (52, 92), (84, 108), (98, 132)],
    # the back of her left hand laid over her heart, fingers toward her right shoulder
    "hand": [(84, 136), (66, 132), (48, 127), (30, 122), (16, 118), (8, 113), (10, 106), (22, 104), (34, 101),
             (40, 96), (36, 90), (42, 86), (52, 90), (62, 99), (74, 110), (88, 120)],
}
B_DET = [
    [(-11, -3), (-6, -8), (1, -9), (7, -6), (8, -4), (2, -1), (-5, -1), (-11, -3)],     # near eye
    [(-3, -8), (-4, -4), (-1, -2), (2, -4), (2, -8)],                                   # iris, lifted
    [(17, -5), (21, -9), (27, -9), (30, -6), (25, -3), (19, -3), (17, -5)],             # far eye
    [(22, -9), (22, -5), (25, -4)],                                                     # far iris
    [(-13, -15), (-6, -19), (4, -18)], [(18, -18), (25, -19), (31, -16)],               # brows
    [(10, -10), (13, 0), (16, 10), (21, 15), (18, 19), (14, 19), (11, 17)],             # nose
    [(2, 29), (8, 27), (12, 28), (16, 27), (24, 29)], [(3, 30), (14, 31), (23, 30)],    # upper lip, mouth line
    [(8, 34), (14, 36), (20, 34)],                                                      # lower lip
    [(-25, -6), (-31, -4), (-32, 6), (-28, 13), (-23, 12)],                             # ear
    [(25, -46), (10, -42), (-6, -36), (-18, -24), (-26, -12)],                          # hairline swept back
    [(-24, 78), (-6, 90), (14, 88), (24, 80)],                                          # neckline of her tunic
]


def bust(pts):
    c, sn = math.cos(math.radians(BUST_ROT)), math.sin(math.radians(BUST_ROT))
    return [(BUST_AT[0] + BUST_S * (x * c - y * sn), BUST_AT[1] + BUST_S * (x * sn + y * c)) for x, y in pts]


def person_svg():
    b = L(poly_d(bust(C(B["head"], 6))))
    b += L(poly_d(bust(C(B["neck_near"], 6)))) + L(poly_d(bust(C(B["neck_far"], 6))))
    for d in B_DET:
        b += D(poly_d(bust(C(d, 4))))
    return b


def person_hatch():
    S = []
    # hair strands falling behind the shoulder, and over the crown
    for k in range(7):
        S.append(bust(C([(-36 + 3 * k, -36 + k), (-38 + 2 * k, -10), (-40 + 2 * k, 20), (-44 + 2 * k, 50), (-50 + 2 * k, 84)], 4)))
    for k in range(5):
        S.append(bust(C([(20 - 6 * k, -48 + k), (2 - 6 * k, -44 + 2 * k), (-16 - 4 * k, -34 + 3 * k)], 4)))
    # shadow under the jaw on the neck, the far cheek, and the near shoulder
    S += hatch(bust(C([(-20, 34), (-8, 44), (12, 50), (12, 62), (-20, 64)], 4, True)), 70, 3.0, seed=4, min_len=1.5)
    S += hatch(bust(C([(30, 4), (36, 14), (30, 33), (24, 28), (26, 12)], 4, True)), 60, 2.6, seed=5, min_len=1.5)
    S += hatch(bust(C([(-100, 126), (-86, 110), (-60, 102), (-70, 118)], 4, True)), 60, 3.4, seed=6, min_len=2)
    return S


# ---------------------------------------------------------------- arrows (parts b and c)
def arrow(p0, p1, bow=-14, head=17):
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + bow)
    p = cr_dense([p0, mid, p1], 10)
    a = math.atan2(p1[1] - p[-3][1], p1[0] - p[-3][0])
    h1 = (p1[0] - head * math.cos(a - 0.5), p1[1] - head * math.sin(a - 0.5))
    h2 = (p1[0] - head * math.cos(a + 0.5), p1[1] - head * math.sin(a + 0.5))
    return poly_d(p + [h1, p1, h2])


def glint(cx, cy, r0, r1, n=10, a0=0):
    return " ".join(poly_d([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], eps=0)
                    for a in [math.radians(a0 + 360 * k / n) for k in range(n)])


def radiance():
    """soft rays round her head: she bears God's image (hatch, self-drawn)"""
    out = []
    cx, cy = bust([(0, -4)])[0]
    for k in range(22):
        a = math.radians(-200 + 220 * k / 21)
        rx0, ry0 = 74, 80
        rx1, ry1 = 92, 98
        if -125 < math.degrees(a) < -55:                   # leave the space under the coin clear
            continue
        out.append(poly_d([(cx + rx0 * math.cos(a), cy + ry0 * math.sin(a)), (cx + rx1 * math.cos(a), cy + ry1 * math.sin(a))], eps=0))
    return " ".join(out)


# ---------------------------------------------------------------- part d: the week strip
WEEK = "MTWTFSS"
X0, Y0, CW, CH = 296, 676, 144, 78


def week_svg():
    b = ""
    # the strip and its dividers, ONE stroke (the dividers zig-zag along the top and bottom edges)
    x1 = X0 + CW * 7
    pts = [(X0 + 10, Y0), (x1 - 10, Y0), (x1, Y0 + 10), (x1, Y0 + CH - 10), (x1 - 10, Y0 + CH), (X0 + 10, Y0 + CH),
           (X0, Y0 + CH - 10), (X0, Y0 + 10), (X0 + 10, Y0)]
    zig = [(X0 + 10, Y0)]
    for k in range(1, 7):
        x = X0 + CW * k
        if k % 2:
            zig += [(x, Y0), (x, Y0 + CH)]
        else:
            zig += [(x, Y0 + CH), (x, Y0)]
    b += L(poly_d(pts) + " " + poly_d(zig[1:]))
    # day letters
    for k, ch in enumerate(WEEK):
        cx = X0 + CW * k + CW * 0.36
        for d in rc.strokes_to_d(rc.on_line(ch, cx, Y0 + CH * 0.68, 30, align="center", heavy=1.3)):
            b += D(d)
    # ticks, drawn one by one
    for k in range(7):
        x = X0 + CW * k + CW * 0.62
        y = Y0 + CH * 0.52
        b += L(poly_d(cr_dense([(x - 10, y - 2), (x - 2, y + 10), (x + 22, y - 22)], 4)))
    return b


def week_hatch():
    S = []
    for k in range(7):
        S += hatch([(X0 + CW * k + 4, Y0 + CH + 3), (X0 + CW * (k + 1) + 4, Y0 + CH + 3),
                    (X0 + CW * (k + 1) + 4, Y0 + CH + 7), (X0 + CW * k + 4, Y0 + CH + 7)], -45, 3.0, seed=k, min_len=1.5)
    return S


# ---------------------------------------------------------------- parts
def part_a():
    b = coin_svg()
    b += person_svg()
    hat, contour = coin_hatch()
    b += D(COIN.pd(contour))
    b += H(" ".join(hat))
    b += H(" ".join(poly_d(s, eps=0) for s in person_hatch()))
    return b


def part_b():
    g = " ".join(poly_d([(COIN.cx + 104 * math.cos(a), COIN.cy + 104 * math.sin(a)),
                         (COIN.cx + 122 * math.cos(a), COIN.cy + 122 * math.sin(a))], eps=0)
                 for a in [math.radians(d) for d in (-150, -132, -114)])
    return L(arrow((700, CAESAR_Y - 6), (868, CAESAR_Y - 6))) + H(g)


def part_c():
    return L(arrow((676, GOD_Y + 6), (874, GOD_Y + 6), bow=-12)) + H(radiance())


def part_d():
    return week_svg() + H(" ".join(poly_d(s, eps=0) for s in week_hatch()))


if __name__ == "__main__":
    for k, f in zip("abcd", (part_a, part_b, part_c, part_d)):
        write(os.path.join(OUT, f"b03-image-belongs-{k}.svg"), svg(f(), f"b03 {k}"))
