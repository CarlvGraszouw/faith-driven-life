"""a07-coin-hand: "Show me the coin." Close-up seen from above: a silver denarius lies in Jesus'
open left palm; a Herodian's ringed right hand presses it in with the forefinger. Jesus' cream
tunic sleeve with his mantle (CLOAK) draped over the forearm and a tassel at its corner; the
questioner's fine sleeve with a woven border.

Both hands are hand-designed 'glyphs' in local units (wrist centre at 0,0) built from anatomical
landmarks and placed with a rotation and scale. Strokes are merged so the pen lifts rarely:
each hand + forearm is one outline, and each finger's creases chain along its edge."""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from lib_v2 import L, D, H, svg, write, BLUE, CLOAK  # noqa: E402
from inkgeom import poly_d, cr_dense, clip_outside, ell_pts, hatch, clip_frame, clip_poly_rect  # noqa: E402
import denarius as dn  # noqa: E402

OUT = os.path.join(HERE, "..", "A")


def place(pts, rot, s, T):
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(T[0] + s * (x * c - y * sn), T[1] + s * (x * sn + y * c)) for x, y in pts]


def C(pts, n=6, closed=False):
    return cr_dense(pts, n, closed=closed)


# ---------------------------------------------------------------- Jesus' left hand: palm up, fingers to the left
# local units: wrist centre (0,0); fingers toward -x; little-finger side (far) at -y, thumb (near) at +y.
# Fingers: base centre, tip centre, half widths at base and tip (little finger ... forefinger).
J_FINGERS = [((-196, -62), (-326, -57), 15.5, 10.5),
             ((-206, -22), (-374, -19), 18.0, 12.5),
             ((-210, 18), (-392, 17), 19.0, 13.0),
             ((-204, 58), (-362, 51), 18.0, 12.5)]
TOUCH = 0.52          # adjacent fingers touch up to this fraction of their length


def _fpt(f, t, side):
    """point on finger f at fraction t along it, side=-1 far edge (-y), +1 near edge (+y), 0 axis"""
    (bx, by), (tx_, ty_), w0, w1 = f
    w = (w0 + (w1 - w0) * t) * (1 + 0.06 * math.sin(math.pi * t))
    dx, dy = tx_ - bx, ty_ - by
    Ln = math.hypot(dx, dy)
    nx, ny = dy / Ln, -dx / Ln              # for fingers pointing -x this is (0, +1)... normalised below
    if ny < 0:
        nx, ny = -nx, -ny                   # make n point to +y (near side)
    return (bx + dx * t + nx * w * side, by + dy * t + ny * w * side)


def _edge(f, t0, t1, side, n=10):
    return [_fpt(f, t0 + (t1 - t0) * i / n, side) for i in range(n + 1)]


def _tip(f, n=10):
    (bx, by), (tx_, ty_), w0, w1 = f
    dx, dy = tx_ - bx, ty_ - by
    Ln = math.hypot(dx, dy)
    ux, uy = dx / Ln, dy / Ln
    t = 1 - w1 / Ln
    c = _fpt(f, t, 0)
    nx, ny = -uy, ux
    if ny < 0:
        nx, ny = -nx, -ny
    w = w1 * 1.04
    # from the far edge (-n) round the tip to the near edge (+n)
    return [(c[0] - nx * w * math.cos(math.pi * i / n) + ux * w * 1.2 * math.sin(math.pi * i / n),
             c[1] - ny * w * math.cos(math.pi * i / n) + uy * w * 1.2 * math.sin(math.pi * i / n)) for i in range(n + 1)]


def _soften(pts, it=2):
    """light Laplacian smoothing (keeps the ends) to round the points where fingers part"""
    P = list(pts)
    for _ in range(it):
        P = [P[0]] + [((P[i - 1][0] + 2 * P[i][0] + P[i + 1][0]) / 4, (P[i - 1][1] + 2 * P[i][1] + P[i + 1][1]) / 4)
                      for i in range(1, len(P) - 1)] + [P[-1]]
    return P


def jesus_outline_pts():
    F = J_FINGERS
    pts = [(64, -74), (30, -70), (0, -64), (-34, -74), (-80, -79), (-128, -79), (-170, -77)]
    pts = cr_dense(pts, 5)
    for k, f in enumerate(F):
        (bx, by), (tx_, ty_), w0, w1 = f
        Ln = math.hypot(tx_ - bx, ty_ - by)
        tt = 1 - w1 / Ln
        start = 0.0 if k == 0 else TOUCH
        if k > 0:      # round the point where this finger parts from the previous one
            q = _fpt(f, start, -1)
            pts += [((pts[-1][0] * 0.6 + q[0] * 0.4) + 6, (pts[-1][1] * 0.6 + q[1] * 0.4)),
                    ((pts[-1][0] + q[0]) / 2 + 9, (pts[-1][1] + q[1]) / 2),
                    ((pts[-1][0] * 0.4 + q[0] * 0.6) + 6, (pts[-1][1] * 0.4 + q[1] * 0.6))]
        pts += _edge(f, start, tt, -1)[1:] + _tip(f)[1:] + list(reversed(_edge(f, TOUCH if k < 3 else 0.0, tt, +1)))[1:]
    pts = _soften(pts, 4)
    pts += cr_dense([pts[-1], (-189, 87), (-186, 97)], 4)[1:]
    pts += cr_dense([(-186, 97), (-200, 108), (-216, 116), (-232, 122), (-246, 128), (-256, 133), (-263, 141),
                     (-264, 151), (-258, 159), (-248, 163), (-232, 166), (-212, 167), (-190, 165), (-164, 161), (-132, 156),
                     (-96, 146), (-62, 131), (-32, 113), (-10, 98), (0, 90), (34, 96), (70, 104)], 6)[1:]
    return pts


def jesus_creases():
    F = J_FINGERS
    out = []
    for f in F:
        for t, frac, dbl in ((0.46, 0.7, True), (0.73, 0.6, False)):
            a = _fpt(f, t, -frac); b = _fpt(f, t, frac); m = _fpt(f, t - 0.012, 0)
            out.append(cr_dense([a, m, b], 4))
            if dbl:
                a = _fpt(f, t + 0.03, -frac); b = _fpt(f, t + 0.03, frac); m = _fpt(f, t + 0.018, 0)
                out.append(cr_dense([a, m, b], 4))
    # separations: from where the fingers part, back to the web
    for f, g in zip(F, F[1:]):
        p = _fpt(f, TOUCH, +1); q = _fpt(g, TOUCH, -1)
        m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        a = _fpt(f, 0.02, +1); b = _fpt(g, 0.02, -1)
        out.append(cr_dense([m, ((m[0] + (a[0] + b[0]) / 2) / 2, (m[1] + (a[1] + b[1]) / 2) / 2),
                             ((a[0] + b[0]) / 2 + 6, (a[1] + b[1]) / 2)], 4))
    return out


JH_COIN = (-112, 14)      # the coin rests in the hollow of the palm
JH_LINES = [
    [(-224, 119), (-227, 143), (-223, 167)],                                                   # thumb joint
    [(-254, 158), (-246, 161), (-238, 162)],                                                   # edge of the thumbnail
    [(-128, -79), (-150, -54), (-178, -22), (-196, 18)],                                       # heart line
    [(-186, 92), (-150, 60), (-112, 26), (-86, -10)],                                          # head line
    [(-184, 97), (-150, 112), (-108, 118), (-66, 110), (-30, 88)],                             # life line
    [(-8, -60), (-16, 14), (-8, 84)],                                                          # wrist crease
]
JH_COIN = (-112, 14)      # the coin rests in the hollow of the palm


# Jesus' sleeve (cream tunic) and mantle, local units of the same frame.
# The sleeve: from the mantle's edge along the top of the arm, round the loose open hem, and back
# along the sagging underside to the mantle's edge (one stroke).
J_SLEEVE = [(176, -106), (130, -100), (90, -94), (58, -88),
            (50, -62), (47, -24), (50, 18), (58, 60), (70, 98), (84, 122),
            (118, 136), (160, 146), (198, 150)]
J_SLEEVE_FOLDS = [[(70, -88), (90, -46), (94, 4), (88, 52), (80, 104)],
                  [(150, -100), (130, -60), (124, -10), (134, 46), (144, 136)]]
# the mantle: thrown over the forearm; its edge falls diagonally in an S to a tasselled corner
J_MANTLE = [(480, -152), (400, -136), (320, -122), (248, -112), (180, -106),
            (184, -70), (200, -30), (214, 14), (226, 64), (238, 112), (250, 150), (262, 172),
            (290, 160), (330, 146), (380, 140), (430, 134), (480, 128)]
J_MANTLE_FOLDS = [[(270, -114), (262, -60), (272, 0), (282, 70), (276, 150)],
                  [(340, -124), (328, -50), (338, 20), (346, 90), (336, 142)],
                  [(410, -134), (404, -60), (412, 20), (420, 132)]]
J_TASSEL = [[(262, 172), (258, 182), (265, 188), (258, 194)], [(259, 192), (252, 208), (260, 194), (262, 210), (262, 194), (270, 208)]]

# ---------------------------------------------------------------- the questioner's right hand: back view, pressing
# local units: wrist centre (0,0); fingers toward +y; thumb at +x. Outline starts and ends at the cuff.
QH_OUT = [
    (-62, -44), (-60, -20), (-58, 0),                                                          # forearm
    (-62, 34), (-66, 74), (-70, 112), (-73, 146),                                              # little-finger edge
    (-76, 170), (-74, 192), (-67, 207), (-57, 213), (-47, 210), (-41, 200), (-40, 184),       # curled little finger
    (-42, 204), (-40, 220), (-32, 230), (-20, 233), (-9, 227), (-6, 207), (-4, 190),          # curled ring finger
    (-6, 212), (-4, 228), (4, 238), (16, 241), (27, 235), (31, 216), (32, 197),               # curled middle finger
    (33, 230), (36, 262), (39, 290), (42, 316), (45, 340), (48, 354),                          # forefinger, inner side
    (53, 363), (60, 366), (67, 361), (70, 351),                                                # fingertip
    (71, 334), (70, 314), (70, 288), (69, 262), (67, 232), (66, 205),                          # forefinger, outer side
    (68, 192), (74, 206), (79, 222), (82, 238), (83, 252),                                     # thumb, inner side
    (86, 262), (94, 266), (101, 258), (103, 244),                                              # thumb tip
    (104, 222), (104, 196), (102, 168), (98, 138), (90, 100), (80, 62), (68, 28), (62, 0),    # thumb outer edge
    (64, -22), (66, -46),                                                                      # forearm
]
QH_KNUCKLES = [(-58, 158), (-50, 152), (-40, 156), (-26, 168), (-16, 162), (-4, 166), (10, 172), (20, 166),
               (32, 170), (40, 168), (50, 162), (62, 168)]           # one wavy stroke over the four knuckles
QH_DETAILS = [
    [(-66, 200), (-58, 196), (-48, 200)], [(-35, 216), (-24, 212), (-12, 216)],               # curled joints
    [(0, 223), (12, 219), (25, 223)],
    [(40, 258), (52, 254), (66, 258), (66, 264), (52, 261), (40, 264)],                        # forefinger joints
    [(43, 312), (55, 309), (68, 312)],
    [(46, 332), (51, 352), (58, 358), (66, 352), (68, 332), (57, 328), (46, 332)],            # nail
    [(88, 236), (91, 252), (97, 256), (101, 248), (100, 234), (93, 230), (88, 236)],          # thumbnail
    [(-50, 30), (-50, 90), (-48, 146)], [(-16, 34), (-18, 100), (-20, 160)],                  # tendons
    [(14, 36), (16, 100), (18, 164)], [(42, 34), (44, 100), (48, 160)],
    # signet ring on the ring finger: band and oval bezel
    [(-44, 199), (-30, 202), (-14, 203), (-5, 200), (-6, 207), (-16, 210), (-30, 209), (-43, 206)],
    [(-30, 199), (-26, 192), (-18, 192), (-14, 199)],
]
Q_SLEEVE = {
    "cuff": [(-82, -44), (-40, -40), (0, -38), (40, -40), (88, -46), (90, -62), (40, -56), (0, -54),
             (-40, -56), (-84, -60)],                                                           # woven border band
    "left": [(-84, -60), (-92, -100), (-100, -150), (-108, -200)],
    "right": [(90, -62), (100, -104), (110, -150), (120, -200)],
}
Q_SLEEVE_FOLDS = [[(-50, -62), (-40, -110), (-36, -160)], [(30, -60), (24, -110), (20, -170)],
                  [(64, -64), (70, -110), (78, -160)]]

J_POSE = dict(rot=-8, s=1.42, T=(945, 458))
Q_POSE = dict(rot=-35, s=1.2, T=(458, 140))


def coin_geom():
    cx, cy = place([JH_COIN], **J_POSE)[0]
    return (cx, cy), ell_pts(cx, cy, 56, 49, -90, 270, 64, rot=-8)


def coin_head(cx, cy, s=0.138):
    """the laureate head of the obverse, small, squashed to the coin's tilt (one stroke per group)"""
    def T(pts):
        c, sn = math.cos(math.radians(-8)), math.sin(math.radians(-8))
        return [(cx + s * (x * c - 0.88 * y * sn), cy + s * (x * sn + 0.88 * y * c)) for x, y in pts]
    out = [T(dn.path_pts(dn.PROFILE, 6) + dn.path_pts(dn.BACK_NECK, 6)[1:]),
           T(dn.path_pts(dn.BACK_HAIR, 6) + dn.path_pts(dn.CROWN, 6)),
           T(dn.wreath(n=9)[0])]
    return out


def shading(qh):
    S = []
    (cx, cy), _ = coin_geom()
    # palm hollow (light from the upper left)
    S += hatch(place(C([(-160, -30), (-90, -44), (-56, 10), (-70, 66), (-136, 80), (-176, 34)], 5, True), **J_POSE),
               -35, 6.0, jitter=0.4, seed=4, min_len=3, shorten=0.2, fade=0.55)
    # the coin's shadow in the palm
    sh = ell_pts(cx + 8, cy + 10, 57, 50, -20, 150, 20, rot=-8) + list(reversed(ell_pts(cx, cy, 56, 49, -20, 150, 20, rot=-8)))
    S += hatch(sh, -40, 3.0, seed=5, min_len=1.5)
    # shadow of the pressing hand falling across the palm and fingers
    S += hatch(place(C([(-206, -78), (-150, -78), (-118, -40), (-104, -14), (-150, -46), (-206, -60)], 5, True), **J_POSE),
               -30, 4.2, seed=6, min_len=2, shorten=0.15, fade=0.3)
    # ball of the thumb and the edge of the palm
    S += hatch(place(C([(-40, 112), (-100, 146), (-160, 158), (-150, 142), (-90, 130)], 5, True), **J_POSE),
               60, 4.5, seed=7, min_len=2, fade=0.3)
    # questioner: the little-finger side of the hand and the curled fingers in shade
    S += hatch(place(C([(-60, 20), (-66, 80), (-72, 150), (-74, 192), (-64, 206), (-58, 150), (-52, 80), (-50, 20)], 5, True),
                     **Q_POSE), 25, 4.0, seed=8, min_len=2, fade=0.25)
    S += hatch(place(C([(70, 240), (71, 330), (64, 352), (62, 300), (63, 250)], 5, True), **Q_POSE), 70, 3.2, seed=10, min_len=2)
    # sleeve and mantle folds
    S += hatch(place(C([(60, 60), (84, 122), (130, 140), (176, 148), (150, 110), (100, 80)], 5, True), **J_POSE), 70, 4.0, seed=11, min_len=2, fade=0.3)
    S += hatch(place(C([(186, -100), (212, 14), (240, 112), (262, 168), (280, 150), (250, 40), (226, -60)], 5, True), **J_POSE),
               60, 3.6, seed=12, min_len=2, fade=0.25)
    S += hatch(place(C([(-84, -62), (-100, -150), (-80, -150), (-66, -62)], 5, True), **Q_POSE), 20, 4.0, seed=13, min_len=2)
    return S


def _fit(d_list):
    return d_list


def Lc(pts):
    return "".join(L(poly_d(r)) for r in clip_frame(pts))


def Dc(pts):
    return "".join(D(poly_d(r)) for r in clip_frame(pts))


def body():
    b = ""
    (cx, cy), coin = coin_geom()
    jh = place(jesus_outline_pts(), **J_POSE)
    qh = place(C(QH_OUT, 6), **Q_POSE)
    # ---- the open palm (focus), the coin in it, then the hand pressing it
    for run in clip_outside(jh, [qh], step=1.2, min_len=4):
        b += L(poly_d(run))
    b += f'  <path class="line" fill="{BLUE}" fill-opacity="0.5" style="mix-blend-mode:multiply" d="{poly_d(coin, True)}"/>\n'
    b += Lc(qh)
    # ---- sleeves: Jesus' tunic and the mantle over it; the questioner's bordered sleeve
    b += Lc(place(C(J_SLEEVE, 5), **J_POSE))
    mantle = place(C(J_MANTLE, 6), **J_POSE)
    close = place([(520, 128), (520, -160)], **J_POSE)
    shape = clip_poly_rect(mantle + close)
    # the pen draws the mantle's edge (not the frame side); its colour fills the clipped shape
    b += f'  <path class="line" fill="{CLOAK}" fill-opacity="0.45" style="mix-blend-mode:multiply" d="{poly_d([p for p in shape if p[0] < 1599.5] , False)}"/>\n'
    b += Lc(place(C(Q_SLEEVE["cuff"], 5), **Q_POSE))
    b += Lc(place(C(Q_SLEEVE["left"], 5), **Q_POSE)) + Lc(place(C(Q_SLEEVE["right"], 5), **Q_POSE))
    # ---- details: coin head, creases, knuckles, nails, ring, folds, tassel
    for pts in coin_head(cx, cy):
        for run in clip_outside(pts, [qh], step=0.8, min_len=2):
            b += D(poly_d(run, eps=0.1))
    occl = [qh, coin]
    for c in jesus_creases():
        for run in clip_outside(place(c, **J_POSE), occl, step=1.0, min_len=3):
            b += D(poly_d(run))
    for c in JH_LINES:
        for run in clip_outside(place(C(c, 5), **J_POSE), occl, step=1.0, min_len=3):
            b += D(poly_d(run))
    b += D(poly_d(place(C(QH_KNUCKLES, 4), **Q_POSE)))
    for c in QH_DETAILS:
        b += D(poly_d(place(C(c, 5), **Q_POSE)))
    for f in J_SLEEVE_FOLDS + J_MANTLE_FOLDS:
        b += Dc(place(C(f, 5), **J_POSE))
    for t in J_TASSEL:
        b += Dc(place(C(t, 4), **J_POSE))
    for f in Q_SLEEVE_FOLDS:
        b += Dc(place(C(f, 5), **Q_POSE))
    # ---- hatch: shading, the coin's bead ring and the woven border pattern
    sh = []
    for s in shading(qh):
        for r in clip_outside(s, [coin], step=1.0, min_len=1.5):
            sh += clip_frame(r)
    b += H(" ".join(poly_d(s, eps=0) for s in sh))
    ring = ell_pts(cx, cy, 49, 43, -90, 270, 52, rot=-8)
    b += H(" ".join(poly_d([ring[i], ring[i + 1]], eps=0) for i in range(0, 52, 2)))
    pat = []
    for k in range(9):
        x = -72 + k * 19
        pat.append(place([(x, -48), (x + 8, -55), (x, -60), (x - 8, -53), (x, -48)], **Q_POSE))
    b += H(" ".join(poly_d(p, eps=0) for p in pat))
    return b


if __name__ == "__main__":
    write(os.path.join(OUT, "a07-coin-hand.svg"), svg(body(), "a07: a Herodian presses a denarius into Jesus' open palm"))
