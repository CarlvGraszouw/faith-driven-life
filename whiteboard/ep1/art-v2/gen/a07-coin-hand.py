"""a07-coin-hand: "Show me the coin." Close-up seen from above: a silver denarius lies in Jesus'
open left palm; a Herodian's ringed right hand presses it in with the forefinger. Jesus' cream
tunic sleeve with his mantle (CLOAK) over the forearm and a tassel at its corner; the
questioner's fine sleeve with a woven border.

Both hands are hand-designed 'glyphs' in local units (wrist centre at 0,0) built from anatomical
landmarks, then placed with a rotation and scale (`place`)."""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from lib_v2 import L, D, H, svg, write, BLUE, CLOAK  # noqa: E402
from inkgeom import poly_d, cr_dense, clip_outside, clip_inside, ell_pts, hatch, resample, inside  # noqa: E402
import denarius as dn  # noqa: E402

OUT = os.path.join(HERE, "..", "A")


def place(pts, rot, s, T):
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(T[0] + s * (x * c - y * sn), T[1] + s * (x * sn + y * c)) for x, y in pts]


def C(pts, n=6, closed=False):
    return cr_dense(pts, n, closed=closed)


# ---------------------------------------------------------------- Jesus' left hand: palm up, fingers to the left
# local units: wrist centre (0,0); fingers toward -x; pinky side (far) at -y, thumb (near) at +y.
# Fingers held together: one outline with small notches between the tips; separations are details.
JH_OUT = [
    (0, -64), (-34, -74), (-80, -79), (-128, -79), (-170, -77),                                # heel, pinky side
    (-200, -77), (-232, -79), (-262, -79), (-288, -76),                                        # little finger
    (-302, -72), (-311, -65), (-313, -57), (-309, -50),
    (-300, -47), (-303, -43),                                                                  # notch
    (-318, -42), (-333, -40), (-345, -35), (-351, -27), (-352, -19), (-347, -11),              # ring finger tip
    (-337, -8), (-340, -4),                                                                    # notch
    (-353, -2), (-362, 4), (-367, 12), (-366, 21), (-360, 28),                                 # middle finger tip
    (-349, 32), (-351, 36),                                                                    # notch
    (-339, 39), (-343, 45), (-343, 53), (-337, 60), (-326, 64),                                # index tip
    (-304, 66), (-278, 68), (-250, 70), (-224, 72), (-202, 77),                                # index, near edge
    (-189, 87), (-186, 97),                                                                    # web of the thumb
    (-200, 106), (-218, 115), (-236, 122), (-250, 128),                                        # thumb, upper edge
    (-261, 134), (-267, 145), (-265, 157), (-255, 165),                                        # thumb tip
    (-238, 169), (-216, 169), (-192, 166), (-164, 161),                                        # thumb, lower edge
    (-132, 156), (-96, 146), (-62, 131), (-32, 113), (-10, 98), (0, 90),                       # ball of the thumb
]
JH_DETAILS = [
    # separations between the fingers, from the notch back to the palm
    [(-302, -45), (-270, -47), (-236, -46), (-206, -42)],
    [(-339, -6), (-300, -6), (-260, -5), (-214, -1)],
    [(-350, 34), (-310, 35), (-266, 37), (-214, 41)],
    # the creases where the fingers join the palm
    [(-186, -76), (-194, -60), (-198, -44)], [(-204, -42), (-210, -24), (-212, -2)],
    [(-214, 0), (-218, 20), (-214, 40)], [(-214, 42), (-212, 58), (-204, 75)],
    # middle joints (double) and end joints
    [(-250, -78), (-254, -62), (-252, -47)], [(-256, -78), (-260, -62), (-258, -47)],
    [(-268, -44), (-272, -26), (-270, -6)], [(-274, -44), (-278, -26), (-276, -6)],
    [(-278, -4), (-282, 16), (-280, 36)], [(-284, -4), (-288, 16), (-286, 36)],
    [(-264, 38), (-268, 54), (-266, 69)], [(-270, 38), (-274, 54), (-272, 69)],
    [(-286, -76), (-289, -62), (-287, -48)], [(-314, -40), (-317, -24), (-315, -7)],
    [(-326, -3), (-329, 15), (-327, 33)], [(-306, 38), (-309, 52), (-307, 66)],
    [(-226, 119), (-230, 144), (-226, 168)],                                                   # thumb joint
    # palm lines: heart, head, life; wrist crease
    [(-128, -79), (-150, -54), (-178, -22), (-196, 18)],
    [(-186, 92), (-150, 60), (-112, 26), (-86, -10)],
    [(-184, 97), (-150, 112), (-108, 118), (-66, 110), (-30, 88)],
    [(-8, -60), (-16, 14), (-8, 84)],
]


def jesus_outline():
    return C(JH_OUT, 6)


def jesus_creases():
    return [C(c, 5) for c in JH_DETAILS]


JH_COIN = (-112, 14)      # the coin rests in the hollow of the palm


# ---------------------------------------------------------------- the questioner's right hand: back view, pressing
# local units: wrist centre (0,0); fingers toward +y; thumb at +x
QH_OUT = [
    (-58, 0), (-62, 34), (-66, 74), (-70, 112), (-73, 146),                                    # ulnar edge
    (-76, 170), (-74, 192), (-67, 207), (-57, 213), (-47, 210), (-41, 200), (-40, 184),       # curled little finger
    (-42, 204), (-40, 220), (-32, 230), (-20, 233), (-9, 227), (-6, 207), (-4, 190),          # curled ring finger
    (-6, 212), (-4, 228), (4, 238), (16, 241), (27, 235), (31, 216), (32, 197),               # curled middle finger
    (33, 230), (36, 262), (39, 290), (42, 316), (45, 340), (48, 354),                          # forefinger, inner side
    (53, 363), (60, 366), (67, 361), (70, 351),                                                # fingertip
    (71, 334), (70, 314), (70, 288), (69, 262), (67, 232), (66, 205),                          # forefinger, outer side
    (68, 192), (74, 206), (79, 222), (82, 238), (83, 252),                                     # thumb, inner side
    (86, 262), (94, 266), (101, 258), (103, 244),                                              # thumb tip
    (104, 222), (104, 196), (102, 168), (98, 138), (90, 100), (80, 62), (68, 28), (60, 0),    # thumb outer edge -> wrist
]
QH_DETAILS = [
    [(-58, 158), (-50, 152), (-40, 156)], [(-26, 168), (-16, 162), (-4, 166)],                # knuckles
    [(10, 172), (20, 166), (32, 170)], [(40, 168), (50, 162), (62, 168)],
    [(-66, 200), (-58, 196), (-48, 200)], [(-35, 216), (-24, 212), (-12, 216)],               # middle joints, curled
    [(0, 223), (12, 219), (25, 223)],
    [(40, 258), (52, 254), (66, 258)], [(40, 264), (52, 261), (66, 264)],                     # forefinger joints
    [(43, 312), (55, 309), (68, 312)],
    [(46, 332), (51, 352), (58, 358), (66, 352), (68, 332), (57, 328), (46, 332)],            # forefinger nail
    [(88, 236), (91, 252), (97, 256), (101, 248), (100, 234), (93, 230), (88, 236)],          # thumbnail
    [(-50, 30), (-50, 90), (-48, 146)], [(-16, 34), (-18, 100), (-20, 160)],                  # tendons
    [(14, 36), (16, 100), (18, 164)], [(42, 34), (44, 100), (48, 160)],
    [(-44, 196), (-36, 200), (-26, 198), (-12, 202), (-6, 200)],                              # signet ring band
    [(-44, 204), (-36, 208), (-26, 206), (-12, 210), (-6, 208)],
    [(-34, 194), (-28, 188), (-20, 188), (-15, 194), (-20, 200), (-28, 200), (-34, 194)],     # its bezel
]

# ---------------------------------------------------------------- sleeves and the mantle
# Jesus: forearm to the right; cream tunic sleeve from just above the wrist; the mantle over it
J_ARM = {
    "forearm": [(0, -64), (30, -70), (62, -76)],                       # top of the wrist into the sleeve
    "forearm_lo": [(0, 90), (34, 96), (70, 104)],
    # the sleeve's open hem round the forearm, then its upper and lower contours
    "hem": [(64, -80), (54, -60), (52, -20), (58, 30), (70, 80), (84, 116), (96, 126)],
    "sleeve_top": [(64, -80), (110, -96), (170, -110), (240, -118), (320, -126), (420, -136), (520, -148)],
    "sleeve_lo": [(96, 126), (140, 132), (190, 134)],
    # mantle draped over the forearm, falling in folds to a corner with a tassel
    "mantle": [(190, -120), (176, -80), (170, -30), (176, 30), (190, 86), (200, 134), (214, 196), (226, 236),
               (244, 248), (268, 226), (300, 196), (350, 186), (410, 190), (470, 186), (520, 176)],
}
J_ARM_FOLDS = [
    [(78, -86), (96, -40), (100, 10), (96, 60), (90, 110)],             # sleeve folds toward the cuff
    [(110, -98), (128, -50), (134, 10), (130, 70), (140, 126)],
    [(150, -106), (160, -60), (164, 0), (160, 60), (170, 132)],
    [(204, -116), (220, -60), (232, 10), (240, 90), (236, 170), (232, 226)],   # mantle folds
    [(260, -120), (268, -50), (276, 30), (282, 110), (270, 196)],
    [(318, -126), (326, -40), (330, 60), (334, 150), (330, 186)],
    [(380, -132), (386, -30), (392, 80), (396, 188)],
    [(446, -140), (450, -30), (456, 90), (460, 186)],
]
TASSEL = [(244, 248), (240, 262), (246, 272), (238, 296), (244, 318)]
TASSEL2 = [[(242, 270), (232, 300), (228, 322)], [(248, 272), (252, 300), (256, 320)],
           [(245, 274), (242, 304), (243, 326)]]
# the questioner: forearm up-left out of frame, fine sleeve with a woven border
Q_ARM = {
    "fore_l": [(-58, 0), (-62, -40), (-66, -70)],
    "fore_r": [(60, 0), (66, -40), (70, -70)],
    "cuff": [(-84, -70), (-30, -60), (30, -60), (88, -72)],
    "cuff2": [(-86, -86), (-30, -76), (30, -76), (90, -88)],
    "sleeve_l": [(-84, -70), (-90, -110), (-96, -150)],
    "sleeve_r": [(88, -72), (96, -112), (104, -152)],
}

J_POSE = dict(rot=-6, s=1.15, T=(1010, 505))
Q_POSE = dict(rot=-12, s=1.15, T=(732, 108))


def coin_pts():
    cx, cy = place([JH_COIN], **J_POSE)[0]
    return (cx, cy), ell_pts(cx, cy, 39, 34, -90, 270, 56, rot=-6)


def coin_head(cx, cy, s=0.105):
    """tiny laureate head on the coin, from the obverse design, squashed to the coin's tilt"""
    out = []
    for d in (dn.PROFILE, dn.BACK, dn.CROWN):
        pts = [(cx + x * s, cy + y * s * 0.87) for x, y in dn.path_pts(d, 6)]
        out.append(pts)
    wr = dn.wreath(n=9)[0]
    out.append([(cx + x * s, cy + y * s * 0.87) for x, y in wr])
    return out


def shading(coin_poly, qh):
    S = []
    # palm hollow and the shadow of the coin on it (light from the upper left)
    S += hatch(place(C([(-150, -30), (-80, -40), (-50, 20), (-70, 70), (-140, 80), (-170, 30)], 5, True), **J_POSE),
               -35, 5.5, jitter=0.4, seed=4, min_len=3, shorten=0.2, fade=0.5)
    cx, cy = place([JH_COIN], **J_POSE)[0]
    sh = ell_pts(cx + 8, cy + 9, 40, 34, -10, 160, 20, rot=-6) + list(reversed(ell_pts(cx, cy, 39, 34, -10, 160, 20, rot=-6)))
    S += hatch(sh, -40, 3.0, seed=5, min_len=1.5)
    # shadow of the pressing forefinger falling across the palm
    S += hatch(place(C([(-196, -76), (-150, -76), (-110, -20), (-100, -6), (-150, -40)], 5, True), **J_POSE),
               -30, 4.0, seed=6, min_len=2, shorten=0.15, fade=0.3)
    # ball of the thumb and the side of the hand
    S += hatch(place(C([(-40, 112), (-100, 146), (-160, 158), (-150, 140), (-90, 128)], 5, True), **J_POSE),
               60, 4.5, seed=7, min_len=2, fade=0.3)
    # undersides of the curled fingers and the shadowed side of the questioner's hand
    S += hatch(place(C([(-74, 150), (-72, 190), (-60, 212), (-74, 205), (-80, 170)], 5, True), **Q_POSE),
               20, 3.5, seed=8, min_len=2)
    S += hatch(place(C([(-60, 20), (-66, 80), (-70, 140), (-58, 140), (-50, 80), (-48, 20)], 5, True), **Q_POSE),
               20, 4.5, seed=9, min_len=2, fade=0.3)
    S += hatch(place(C([(70, 240), (71, 330), (64, 352), (62, 300), (63, 250)], 5, True), **Q_POSE),
               70, 3.2, seed=10, min_len=2)
    return S


def body():
    b = ""
    (cx, cy), coin = coin_pts()
    jh = place(jesus_outline(), **J_POSE)
    qh = place(C(QH_OUT, 6), **Q_POSE)
    finger = qh                                          # occluder: the questioner's hand
    # --- Jesus' hand first (the focus), then the coin, then the giver's hand over it
    for run in clip_outside(jh, [finger], step=1.2, min_len=4):
        b += L(poly_d(run))
    b += f'  <path class="line" fill="{BLUE}" fill-opacity="0.5" style="mix-blend-mode:multiply" d="{poly_d(coin, True)}"/>\n'
    b += L(poly_d(qh, closed=True))
    # --- sleeves
    for k in ("forearm", "forearm_lo"):
        b += L(poly_d(place(C(J_ARM[k], 5), **J_POSE)))
    b += L(poly_d(place(C(J_ARM["hem"], 5), **J_POSE)))
    b += L(poly_d(place(C(J_ARM["sleeve_top"], 5), **J_POSE)))
    b += L(poly_d(place(C(J_ARM["sleeve_lo"], 5), **J_POSE)))
    mantle = place(C(J_ARM["mantle"], 6), **J_POSE)
    b += f'  <path class="line" fill="{CLOAK}" fill-opacity="0.55" style="mix-blend-mode:multiply" d="{poly_d(mantle + [mantle[-1], place([(520, -150)], **J_POSE)[0], place([(190, -120)], **J_POSE)[0]], True)}"/>\n'
    for k in ("fore_l", "fore_r", "cuff", "sleeve_l", "sleeve_r"):
        b += L(poly_d(place(C(Q_ARM[k], 5), **Q_POSE)))
    # --- details
    for c in jesus_creases():
        for run in clip_outside(place(c, **J_POSE), [finger, coin], step=1.0, min_len=3):
            b += D(poly_d(run))
    for c in QH_DETAILS:
        b += D(poly_d(place(C(c, 5), **Q_POSE)))
    for pts in coin_head(cx, cy):
        for run in clip_outside(pts, [finger], step=0.8, min_len=2):
            b += D(poly_d(run, eps=0.1))
    b += D(poly_d(place(C(Q_ARM["cuff2"], 5), **Q_POSE)))
    for f in J_ARM_FOLDS:
        b += D(poly_d(place(C(f, 5), **J_POSE)))
    b += D(poly_d(place(C(TASSEL, 5), **J_POSE)))
    for t in TASSEL2:
        b += D(poly_d(place(C(t, 5), **J_POSE)))
    # --- hatch
    b += H(" ".join(poly_d(s, eps=0) for s in shading(coin, qh)))
    beads = ell_pts(cx, cy, 34, 29.6, -90, 270, 40, rot=-6)
    b += H(" ".join(poly_d([beads[i], beads[i + 1]], eps=0) for i in range(0, 40, 2)))
    return b


if __name__ == "__main__":
    write(os.path.join(OUT, "a07-coin-hand.svg"), svg(body(), "a07: a Herodian presses a denarius into Jesus' open palm"))
