"""People for batch A scenes (a03 listeners, a04/a11 Pharisees & Herodians).
Built on jesus.py's Part/Fig machinery (z-order clipping, levels, hatch-free shading).
All figures are designed FACING LEFT in local units (origin = ground point under the figure, 340 = standing
height at scale 1); render with mirror=True to face right."""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import a_sketch as K  # noqa: E402
from jesus import Fig, Part, rig_hand, foot, tassel, limb, HP, HEAD_S, WHITE, _el  # noqa: E402
from hands_data import HANDS  # noqa: E402
from lib_v2 import circle  # noqa: E402


# =============================================================== heads (head-space: 100 tall, eye line y=0)
FACE_FAR = [(-36.6, -25.6), (-39.4, -16), (-40.6, -10), (-39.4, -4), (-38.8, 0), (-40.4, 5), (-41.4, 11), (-42, 16.6)]
JAW = {   # continuation of the far face contour around the chin to the near ear / sideburn
    "none": [(-42, 16.6), (-41.6, 27), (-38.6, 38), (-32.6, 46.6), (-24, 51), (-15, 51.4), (-5, 48.6), (5, 43),
             (13.6, 35), (19.6, 25), (22.6, 14), (23, 6)],
    "short": [(-42, 16.6), (-42.6, 28), (-40.4, 40), (-34, 49.6), (-25, 55), (-15, 55.6), (-4, 52), (6.6, 45.4),
              (15, 36.4), (21, 26), (23.6, 15), (24, 7)],
    "full": [(-42, 16.6), (-43.4, 24), (-43.8, 33), (-42.4, 42), (-39.6, 50), (-35, 56.6), (-29.6, 60.6), (-25, 63.6),
             (-19.4, 65.6), (-13.4, 64.6), (-8, 63.4), (-2, 61), (5, 57.8), (11.4, 53), (18.6, 45.4), (23.8, 36),
             (26.6, 26.6), (26.6, 17), (24.6, 8.6)],
    "long": [(-42, 16.6), (-45, 30), (-47, 46), (-46.4, 62), (-43, 78), (-37, 92), (-29, 102.6), (-20, 107),
             (-11.6, 104.6), (-3.6, 96.6), (4, 85), (11.6, 69), (18, 53), (23, 37), (25.6, 22), (25, 9)],
}
SHADE = {"none": None, "short": 0.6, "full": 1.0, "long": 1.0}


def eyes(ph, P, expr, gaze, lv_far="S"):
    """brows, lids, pupils for an expression.  gaze: -1 looks left (facing), +1 toward the viewer side."""
    sm = lambda pts: K.sm(P(pts))
    g = gaze
    if expr == "smile":        # ingratiating: brows lifted in the middle, eyes narrowed by the cheeks
        nb = [(-15.6, -11.6), (-9.6, -14.4), (-3, -14.6), (3.6, -12.6), (8, -9.4)]
        fb = [(-25.6, -11.6), (-30.4, -13.4), (-35.4, -12.4), (-38.8, -9.6)]
        nl = [(-12.4, 0.6), (-8.6, -1.4), (-4.4, -2.2), (-0.6, -1.6), (2.4, 0.6)]
        fl = [(-35.6, 0.4), (-33, -1.2), (-29.8, -1.4), (-27.6, 0.4)]
        nlo = [(-11.2, 2.4), (-6, 1.2), (-0.8, 2.2)]
        pr, ps = (-6.2 + 1.4 * g, -0.1), 0.95
    elif expr == "sly":        # one brow low, narrowed eyes, sideways look
        nb = [(-15.6, -8.6), (-9.6, -11), (-3, -11.6), (3.6, -10.2), (8, -7.6)]
        fb = [(-25.6, -10.2), (-30.4, -12.2), (-35.4, -11.8), (-38.8, -9.4)]
        nl = [(-12.4, 0.6), (-8.6, -0.6), (-4.4, -1.2), (-0.6, -0.8), (2.4, 0.6)]
        fl = [(-35.6, 0.6), (-33, -0.6), (-29.8, -0.8), (-27.6, 0.6)]
        nlo = [(-11.2, 2.2), (-6, 2.8), (-0.8, 2)]
        pr, ps = (-8.8 + 1.0 * g, 0.4), 0.9
    elif expr == "stunned":    # brows high, eyes wide open, white around the pupils
        nb = [(-15.6, -15.6), (-9.2, -19.6), (-2.6, -20.4), (4, -18), (8.6, -13.6)]
        fb = [(-25.6, -15), (-30.4, -18.6), (-35.6, -18), (-39, -13.6)]
        nl = [(-12.6, 0.4), (-9.6, -3.6), (-5.4, -5), (-1.2, -4.2), (2, -1.4), (2.8, 0.6)]
        fl = [(-35.8, 0.2), (-33.8, -3), (-30.4, -3.6), (-27.8, -1.2), (-27.4, 0.6)]
        nlo = [(-11.4, 2.8), (-6, 4.2), (-0.6, 3)]
        pr, ps = (-5.4 + 0.8 * g, -0.6), 0.85
    elif expr == "frown":      # skeptical, brows knitted low
        nb = [(-15.6, -7.6), (-10, -10.4), (-3, -11.2), (3.6, -10.6), (8, -8)]
        fb = [(-25.6, -8), (-30.4, -10.6), (-35.4, -11), (-38.8, -9)]
        nl = [(-12.4, 0.4), (-8.6, -1.8), (-4.4, -2.6), (-0.6, -2.2), (2.4, 0.2)]
        fl = [(-35.6, 0.2), (-33, -1.6), (-29.8, -2), (-27.6, 0.2)]
        nlo = [(-11.2, 2), (-6, 2.6), (-0.8, 2)]
        pr, ps = (-6.6 + 1.6 * g, -0.4), 1.0
    else:                      # calm / listening
        nb = [(-15.4, -9.4), (-9.6, -12), (-3, -12.6), (3.4, -11.2), (7.8, -8.6)]
        fb = [(-25.4, -10), (-30.2, -11.6), (-35, -11), (-38.6, -8.8)]
        nl = [(-12.6, 0.4), (-9.4, -2.2), (-5.4, -3.2), (-1.4, -2.6), (1.6, -0.6), (2.8, 0.6)]
        fl = [(-35.8, 0.2), (-33.8, -1.8), (-30.6, -2.3), (-28.2, -0.3), (-27.4, 0.8)]
        nlo = [(-10.6, 2.2), (-5.6, 3.3), (-0.6, 2.4)]
        pr, ps = (-5.6 + 1.8 * g, -0.4), 1.1
    ph.add("detail", sm(nb), "S")
    ph.add("detail", sm(fb), lv_far)
    ph.add("detail", sm(nl), "S")
    ph.add("detail", sm(fl), "S")
    ph.add("detail", sm(nlo), "F" if expr != "smile" else "M")
    (cx, cy), = P([pr])
    ph.add("detail", circle(cx, cy, ps), "S")
    (cx, cy), = P([(pr[0] - 26.2 + 0.4 * g, pr[1])])
    ph.add("detail", circle(cx, cy, ps * 0.82), "S")


def mouth(ph, P, expr, beard):
    sm = lambda pts: K.sm(P(pts))
    if expr == "smile":
        ph.add("detail", sm([(-33.6, 31.4), (-28, 34.6), (-21, 35.6), (-14.4, 33.6), (-10.4, 29.6)]), "S")
        ph.add("detail", sm([(-12.6, 22), (-9.6, 27), (-9, 32)]), "M")                        # cheek fold
        ph.add("detail", sm([(-25.6, 38.4), (-20.6, 39.2), (-16.6, 38)]), "F")
    elif expr == "sly":
        ph.add("detail", sm([(-32, 33.6), (-26, 34.4), (-19, 33.6), (-13.4, 31), (-10.4, 27.6)]), "S")
        ph.add("detail", sm([(-11.6, 23), (-9, 28.6)]), "M")
    elif expr == "stunned":
        ph.add("detail", sm([(-28.6, 32), (-25, 30.4), (-20.6, 30.4), (-17.6, 32.4), (-17.6, 37.6), (-21.4, 41.4),
                             (-25.6, 41.2), (-28.6, 37.6), (-28.6, 32)]), "S")                  # open mouth
    elif expr == "frown":
        ph.add("detail", sm([(-32.6, 34.8), (-26, 33.2), (-19, 33.4), (-13, 35.4)]), "S")
    else:
        ph.add("detail", sm([(-31.6, 33.2), (-26, 32.6), (-19.6, 33), (-14, 34)]), "S")
    if beard in ("full", "long", "short") and expr != "stunned":
        ph.add("detail", sm([(-37, 31), (-33.4, 27.6), (-27, 26), (-20, 26.4), (-14, 28.6), (-10, 32.6)]), "M")


def nose(ph, P, kind="straight"):
    sm = lambda pts: K.sm(P(pts))
    if kind == "hooked":
        ph.add("detail", sm([(-22.4, -0.6), (-25.6, 5), (-30, 11), (-33.2, 16.6), (-32.6, 21), (-28.6, 23.2),
                             (-24, 22.6)]), "S")
    else:
        ph.add("detail", sm([(-22.4, -0.6), (-24.6, 6), (-28, 12.6), (-30.6, 17.4), (-30.6, 20.8), (-27.6, 22.8),
                             (-23.8, 22.8)]), "S")
    ph.add("detail", sm([(-19.6, 17.8), (-17.4, 20.4), (-19, 22.8), (-21.6, 23.2)]), "F")


def head34(fig, hx, hy, rot=0.0, s=HEAD_S, beard="full", cover="none", expr="calm", gaze=-1.0, z=70, order=0,
           nose_kind="straight", age=0, beard_dark=True, phylactery=False):
    """3/4 head facing left.  cover: none (short cropped hair) | curly (Herodian) | turban (Pharisee head-cloth)
    | hood (cloth/mantle over the head, falls to the shoulders) | veil (woman's head mantle)."""
    P = HP(hx, hy, rot, s)
    sm = lambda pts: K.sm(P(pts))
    ph = fig.part("head", z, order)
    jaw = JAW[beard]
    face = FACE_FAR + jaw[1:]
    ph.add("line", sm(face), "S")
    occ = list(face)

    if cover == "turban":
        # Pharisee: a cloth wound round the head (bands), a tail falling behind; phylactery box on the brow
        top = [(-37.6, -21), (-44, -34), (-42, -50), (-30, -63), (-10, -71), (12, -70.6), (31, -63), (45, -50),
               (52, -32), (54.6, -12), (56, 8), (59, 30), (62.6, 56), (66, 82), (69, 100), (60, 102.6), (51, 100),
               (43, 97), (37, 80), (32, 60), (28.6, 42), (26, 26)]
        front = [(-37.6, -21), (-30, -30), (-16, -34.6), (0, -33.4), (12.6, -27), (20.6, -15), (24, 0), (25, 7)]
        ph.add("line", K.chain(P(top), P([(26, 26), (25, 14), (25, 7)])), "S")
        ph.add("detail", sm(front), "S")
        for pts, lv in (([(-42, -40), (-22, -50), (4, -53), (30, -47), (48, -34)], "M"),
                        ([(-36, -56), (-14, -63), (12, -63), (34, -55)], "M"),
                        ([(-40, -30), (-24, -38), (0, -42), (26, -37), (46, -24)], "F"),
                        ([(50, 8), (54, 32), (57.6, 60), (60, 90)], "M"), ([(40, 30), (44, 56), (48, 86)], "F")):
            ph.add("detail", sm(pts), lv)
        ph.add("hatch", K.hatch(P([(30, -60), (46, -48), (52.4, -30), (53, -6), (52, 10), (44, 8), (40, -20), (32, -46)]),
                                angle=60 + rot, spacing=2.2, seed=101), "S")
        ph.add("hatch", K.hatch(P([(48, 10), (56, 28), (61, 56), (65, 84), (66, 98), (56, 100), (50, 80), (44, 52),
                                    (40, 30)]), angle=72 + rot, spacing=2.2, seed=102), "S")
        occ = top + [(25, 7)] + jaw[::-1][1:]
        if phylactery:
            box = [(-27.6, -37), (-26.6, -47.4), (-17.6, -48.6), (-17.2, -38.2)]
            ph.add("detail", sm(box + [box[0]]), "S")
            ph.add("detail", sm([(-26.6, -47.4), (-23.4, -51), (-14.6, -51.6), (-17.6, -48.6)]), "M")
            ph.add("hatch", K.hatch(P([(-27, -38), (-26.4, -47), (-17.8, -48), (-17.6, -38.6)]), angle=10 + rot,
                                    spacing=1.3, seed=103), "S")
            ph.add("detail", sm([(-17.2, -40), (-4, -39.6), (10, -34)]), "F")                     # strap
    elif cover in ("hood", "veil"):
        if cover == "hood":
            out = [(-37, -24), (-44.6, -36), (-42, -54), (-28, -67), (-6, -73.6), (16, -71.6), (35, -62), (49, -44),
                   (56, -20), (60, 10), (66, 44), (72, 80)]
            edge = [(-37, -24), (-41.6, -10), (-44.6, 8), (-46.6, 30), (-47.4, 52), (-46, 76)]
        else:
            out = [(-35, -24), (-41, -38), (-38, -56), (-24, -67), (-4, -72), (16, -70), (33, -61), (46, -44), (53, -22),
                   (57, 8), (62, 40), (66, 76)]
            edge = [(-35, -24), (-40.6, -12), (-44.4, 6), (-46, 28), (-46, 52), (-44, 74)]
        front_in = [(-37, -24), (-30, -32), (-16, -36.6), (-2, -35.4), (10, -28.6), (18.6, -16), (23, 0), (24.6, 12),
                    (25, 24)]
        ph.add("line", K.chain(P(edge[::-1]), P(out)), "S")
        ph.add("detail", sm(front_in), "S")
        ph.add("detail", sm([(26, 22), (28, 40), (32, 58), (37, 76)]), "M")                       # fold by the cheek
        ph.add("detail", sm([(4, -64), (24, -56), (40, -38), (48, -12)]), "F")
        ph.add("hatch", K.hatch(P([(30, -56), (46, -40), (54, -16), (58, 14), (63, 48), (68, 76), (40, 76), (34, 50),
                                    (30, 20), (26, -10)]), angle=70 + rot, spacing=2.4, seed=104), "S")
        occ = edge[::-1] + out + [(24, 76), (25, 24)] + jaw[::-1][1:]
    elif cover == "curly":
        hair = [(-37.6, -22), (-41, -34), (-37, -46), (-26, -54.6), (-10, -58.6), (8, -58), (24, -52.6), (37, -42.6),
                (45, -28), (48, -12), (46.6, 4), (41, 16), (33, 20)]
        line = [(-37.6, -22), (-30, -32), (-18, -36.6), (-5, -35.4), (5, -30), (12, -20), (15.6, -8), (17, 4), (20, 10)]
        ph.add("line", K.scallop(P(hair), step=5.2 * s / HEAD_S * 0.45, amp=0.9 * s / HEAD_S * 0.45, side=1), "S")
        ph.add("detail", K.scallop(P(line), step=4.6 * s / HEAD_S * 0.45, amp=0.6 * s / HEAD_S * 0.45, side=-1), "S")
        ear = [(21, -4), (27, -8.6), (31.4, -3), (31, 8), (27.6, 17), (22, 18)]
        ph.add("detail", sm(ear), "S")
        ph.add("detail", sm([(26.6, -2), (24, 4), (26.6, 10)]), "F")
        for (cx, cy) in ((-26, -44), (-12, -50), (4, -51), (20, -46), (33, -36), (41, -20), (42, -4), (-30, -32),
                         (-16, -40), (2, -42), (18, -36), (30, -24), (34, -8), (-4, -45), (11, -45), (26, -31)):
            ph.add("hatch", K.sm(P([(cx - 2.6, cy + 2), (cx - 2.4, cy - 1.6), (cx + 0.6, cy - 2.8), (cx + 2.8, cy - 0.6),
                                    (cx + 1.6, cy + 1.6), (cx - 0.2, cy + 0.6)])), "S")
        ph.add("hatch", K.hatch(P([(20, -50), (38, -40), (46, -22), (46, 2), (38, 14), (30, 4), (32, -20), (24, -40)]),
                                angle=58 + rot, spacing=2.2, seed=105), "S")
        occ = hair + [(20, 10)] + jaw[::-1][1:]
    else:  # cropped short hair
        hair = [(-37.6, -22), (-41, -34), (-36, -47), (-24, -55), (-8, -58.6), (10, -57.6), (26, -51.6), (39, -40.6),
                (46, -24), (48, -6), (45, 10), (38, 18)]
        line = [(-37.6, -22), (-28, -33), (-14, -37), (0, -34), (10, -26), (16, -12), (18, 4), (20, 10)]
        ph.add("line", sm(hair), "S")
        ph.add("detail", sm(line), "S")
        ph.add("detail", sm([(21, -4), (27, -8.6), (31.4, -3), (31, 8), (27.6, 17), (22, 18)]), "S")
        ph.add("hatch", K.hatch(P([(-30, -46), (-8, -56), (20, -54), (40, -40), (47, -20), (46, 4), (38, 14), (28, -10),
                                    (10, -32), (-14, -40)]), angle=64 + rot, spacing=2.0, seed=106), "S")
        occ = hair + [(20, 10)] + jaw[::-1][1:]

    # beard texture / tone
    if beard != "none":
        top_line = {"short": [(23.6, 10), (14, 16), (4, 21), (-6, 25), (-12, 29)],
                    "full": [(24.6, 8.6), (16, 14), (6, 19.4), (-4, 23.4), (-12, 28)],
                    "long": [(25, 9), (16, 15), (6, 20), (-4, 24), (-12, 28.6)]}[beard]
        ph.add("detail", sm(top_line), "M")
        ends = {"short": [(-6, 50), (-16, 54), (-26, 53)], "full": [(-2, 58), (-14, 61), (-26, 58)],
                "long": [(-12, 96), (-20, 104), (-26, 100)]}[beard]
        for c in K.between([top_line[0], (25, 26), (20, 40), (8, 50), ends[0]],
                           [top_line[-1], (-12, 38), (-16, 46), (-22, 52), ends[2]], 6 if beard != "short" else 4, n_pts=10):
            ph.add("hatch", K.sm(P(c)), "S")
        if beard == "long":
            for pts in ([(4, 54), (-2, 72), (-10, 90)], [(-24, 52), (-24, 70), (-21, 92)], [(14, 40), (8, 56), (0, 74)]):
                ph.add("detail", sm(pts), "M")
            ph.add("hatch", K.hatch(P([(20, 36), (12, 56), (2, 76), (-10, 96), (-20, 106), (-20, 92), (-10, 76), (2, 56)]),
                                    angle=-62 + rot, spacing=2.0 if beard_dark else 3.2, seed=107), "S")
        else:
            ph.add("hatch", K.hatch(P([(2, 38), (20, 28), (26, 30), (22, 44), (8, 55), (-10, 62), (-24, 63), (-8, 52)]),
                                    angle=-56 + rot, spacing=1.7 if beard_dark else 2.8, seed=108), "S")
    else:
        ph.add("hatch", K.hatch(P([(10, 30), (20, 22), (22, 30), (14, 40), (4, 46)]), angle=-50 + rot, spacing=2.2,
                                seed=109), "S")
    eyes(ph, P, expr, gaze)
    nose(ph, P, nose_kind)
    mouth(ph, P, expr, beard)
    # modelling
    ph.add("hatch", K.hatch(P([(-14, -6), (-4, -8.4), (5, -6.4), (4, -3), (-6, -4.6), (-14, -3.4)]),
                            angle=-22 + rot, spacing=1.7, seed=110), "S")
    ph.add("hatch", K.hatch(P([(-20.6, -1), (-18.6, 6), (-18, 15.6), (-21.6, 17.6), (-24, 10), (-23.6, 2)]),
                            angle=70 + rot, spacing=1.8, seed=111), "S")
    if age:
        for pts in ([(-12, -18), (-4, -19.6), (4, -18)], [(4, 4), (8, 8)], [(-14, -22), (-2, -24), (8, -21)]):
            ph.add("detail" if age > 1 else "hatch", sm(pts), "F" if age > 1 else "S")
        ph.add("hatch", sm([(3, 3), (7.6, 6.6), (9, 11)]), "S")
    ph.occ.append(K.poly(K.sm(P(occ), closed=True), 1.0))
    return ph


def head_back(fig, hx, hy, rot=0.0, s=HEAD_S, z=70, order=0, cover="hood", beard="full"):
    """Back three-quarter head (face turned away to the LEFT), covered by a hood/mantle that falls on the back.
    Only the far cheek contour, brow and beard edge peek out on the left."""
    P = HP(hx, hy, rot, s)
    sm = lambda pts: K.sm(P(pts))
    ph = fig.part("head", z, order)
    out = [(-30, -38), (-20, -58), (0, -70), (24, -70), (42, -60), (54, -40), (60, -12), (63, 22), (68, 60), (76, 100),
           (82, 140)]
    edge = [(-30, -38), (-36, -22), (-38, -4), (-36, 18), (-30, 40), (-22, 62), (-14, 90), (-8, 120)]
    ph.add("line", K.chain(P(edge[::-1]), P(out)), "S")
    face = [(-35, -16), (-41.6, -10), (-44.6, -3), (-43.4, 4), (-46.6, 11), (-45, 16), (-46, 24), (-45, 34), (-41, 44),
            (-34, 50)]
    ph.add("detail", sm(face), "S")                                         # cheek/brow/beard peeking out
    ph.add("detail", sm([(-43, -6), (-39.6, -5), (-37, -4)]), "M")          # eyelashes of the far eye
    ph.add("detail", sm([(-12, -54), (12, -60), (34, -52), (48, -34)]), "M")
    ph.add("detail", sm([(30, -2), (40, 30), (52, 70), (62, 110)]), "M")
    ph.add("hatch", K.hatch(P([(-26, -36), (-8, -56), (20, -62), (40, -52), (52, -30), (57, 0), (60, 30), (66, 70),
                                (74, 110), (56, 110), (44, 70), (34, 40), (20, 20), (0, 10), (-20, 10), (-30, -10)]),
                            angle=74 + rot, spacing=2.4, seed=112), "S")
    ph.add("hatch", K.hatch(P([(-44, 14), (-40, 30), (-34, 44), (-38, 46), (-44, 34)]), angle=-60 + rot, spacing=1.6,
                            seed=113), "S")
    ph.occ.append(K.poly(K.sm(P(edge[::-1] + out + [(20, 140)]), closed=True), 1.0))
    return ph


if __name__ == "__main__":
    from lib_v2 import svg
    body = ""
    specs = [dict(beard="long", cover="turban", expr="smile", phylactery=True, nose_kind="hooked", age=1),
             dict(beard="short", cover="curly", expr="sly"),
             dict(beard="long", cover="turban", expr="frown", phylactery=True, age=2, beard_dark=False),
             dict(beard="full", cover="hood", expr="calm"),
             dict(beard="none", cover="veil", expr="calm", gaze=-1.0),
             dict(beard="long", cover="turban", expr="stunned", phylactery=True, nose_kind="hooked", age=1)]
    for i, sp in enumerate(specs):
        f = Fig()
        head34(f, 0, 0, s=1.0, **sp)
        lay = f.render(1.25, 130 + i * 260, 330, False, "full")
        body += "".join(lay["line"] + lay["detail"] + lay["hatch"])
    f = Fig()
    head_back(f, 0, 0, s=1.0)
    lay = f.render(1.25, 200, 720, False, "full")
    body += "".join(lay["line"] + lay["detail"] + lay["hatch"])
    open(os.path.join(HERE, "..", "..", "preview", "a-heads.svg"), "w").write(svg(body))
    print("ok")
