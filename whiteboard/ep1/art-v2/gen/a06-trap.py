"""a06-trap (48.3-58.05 s): the trap.  Three parts on one board.

  a (0.2 s)  Jesus at the centre where the path forks.
  b (2.9 s)  under YES (left): the crowd turns its back on him and walks away, one man
             glancing back with a scowl, one shaking his fist.
  c (5.2 s)  under NO (right): Roman legionaries a short walk away, the Antonia tower behind
             them; one holds open manacles toward Jesus.

Word zones kept empty: YES frame (500,300) size 110 -> art x 233..421 y 233..323,
NO frame (1420,250) -> art x 1217..1360 y 177..273.
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit_awb as K  # noqa: E402
from kit_awb import PB, S, P, el, place, hatch, sample, tube, lerp, RUST, CLOAK  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "A")


# ============================================================== helpers
def mk(x, y, s, flip=False):
    """local figure units (feet at y=0, x right) -> art coords"""
    return lambda pts: place(pts, s, x, y, flip)


def pb_runs(T, runs, closed=True):
    """runs: list of point lists; consecutive runs meet at corners. -> d"""
    pb = PB()
    first = T(runs[0])
    pb.M(first[0])
    pb.S(first[1:])
    for r in runs[1:]:
        pb.S(T(r))
    if closed:
        pb.Z()
    return str(pb)


# ============================================================== part b: the crowd
def man_glancing(x, y, s):
    """Nearest man: striding away up-left, twisting back to shake his fist at Jesus with a
    scowl; headcloth, full beard, mantle over the tunic."""
    T = mk(x, y, s)
    o = []
    # ---- robe + mantle silhouette (seen from behind, mid-stride, leaning into the step)
    body_runs = [
        [(-8, -199.5), (-21, -197), (-28.5, -191.5), (-29, -178), (-26.5, -158), (-24.5, -140),
         (-27, -112), (-31.5, -88), (-35.5, -66), (-39, -46), (-43.5, -31)],
        [(-30, -27.5), (-14, -26), (1, -28), (14, -31), (27.5, -37.5)],
        [(28, -56), (24.5, -84), (19.5, -112), (17.5, -136), (21.5, -160), (25.5, -181), (23, -193.5), (8, -199.5)],
    ]
    o.append(el("line", pb_runs(T, body_runs), fill="#ffffff"))
    # ---- legs: forward leg (left, foot planted, heel to us) and back leg (heel up, sole to us)
    o.append(el("line", S(T([(-35.5, -28), (-34, -16), (-32.5, -9)]))))
    o.append(el("line", S(T([(-35.5, -10.5), (-28.5, -9), (-26.5, -3.5), (-30.5, 0.4), (-41, 0.6), (-47, -1.8), (-42, -6), (-35.5, -10.5)]), closed=False), fill="#ffffff"))
    o.append(el("line", S(T([(11.5, -30), (15, -22.5), (19, -17)]))))
    o.append(el("line", S(T([(14, -19.5), (22.5, -19.5), (25, -12.5), (21, -2), (14.5, -1.5), (12, -8.5), (14, -19.5)])), fill="#ffffff"))
    o.append(el("detail", S(T([(15.5, -12.5), (22.5, -11.5)])) + " " + S(T([(-41, -3.5), (-31, -4.5)]))))
    # ---- near (left) arm swinging forward: sleeve to the elbow, bare forearm, relaxed hand
    sleeve = tube(T([(-26, -190), (-30.5, -172), (-33, -154)]), [8.2 * s, 7.6 * s, 7 * s], 0.15, 0.05)
    o.append(el("line", S(sleeve, closed=True), fill="#ffffff"))
    fore = tube(T([(-33, -151), (-37.5, -137), (-41.5, -125)]), [4.6 * s, 4.1 * s, 3.4 * s], 0, 0)
    o.append(el("line", S(fore[:3]) + " " + S(fore[3:])))
    hand = T([(-38, -127.5), (-44.5, -126), (-48.5, -118.5), (-47.2, -111.5), (-43.4, -110.8), (-41.2, -116.5), (-37.4, -121.5)])
    o.append(el("line", S(hand, closed=True), fill="#ffffff"))
    o.append(el("detail", S(T([(-46.2, -117.2), (-42.4, -116)]))))
    # ---- far (right) arm raised back toward Jesus, fist shaking at shoulder height
    upper = tube(T([(21, -186), (29.5, -176), (37, -167)]), [7.6 * s, 7.2 * s, 6.6 * s], 0.1, 0.25)
    o.append(el("line", S(upper, closed=True), fill="#ffffff"))
    fa = tube(T([(37.5, -169), (40.5, -181), (42.5, -192)]), [4.8 * s, 4.3 * s, 3.8 * s], 0, 0)
    o.append(el("line", S(fa[:3]) + " " + S(fa[3:])))
    fist = T([(37.5, -191.5), (39.5, -199.5), (46.5, -201), (50.5, -195.5), (48.5, -189), (41.5, -188)])
    o.append(el("line", S(fist, closed=True), fill="#ffffff"))
    o.append(el("detail", S(T([(41.5, -197.5), (48.2, -197)])) + " " + S(T([(41.5, -193.3), (48.6, -192.8)]))))
    # ---- head: headcloth falling down his back; face in profile, twisted back to Jesus
    cloth = [[(14.5, -234.5), (8, -243.5), (-5, -243.5), (-13.5, -235.5), (-17, -221), (-19.5, -204), (-16, -195.5)],
             [(-3, -197)],
             [(1, -205), (3, -215), (5.5, -225), (9.5, -232), (14.5, -234.5)]]
    o.append(el("line", pb_runs(T, cloth), fill="#ffffff"))
    face = PB().M(T([(14.5, -234.5)])[0])
    face.S(T([(18.2, -230), (19.6, -227.2)]))          # forehead -> brow ridge (frowning bulge)
    face.S(T([(19.2, -225.6)]))                          # root of nose
    face.S(T([(21.8, -221.6), (24.6, -218.2)]))         # nose
    face.S(T([(21.4, -216.8), (20.2, -216.4)]))         # under nose
    face.S(T([(21.8, -214.4), (22.6, -209.8), (21.6, -204.8), (17.6, -200.2), (11, -199.2), (4.5, -201.6)]))  # beard
    o.append(el("line", str(face)))
    o.append(el("detail", P(T([(12.6, -225.6), (15.2, -226.8), (17.4, -225.6), (15.4, -224.4), (12.6, -225.6)]))))  # eye
    o.append(el("detail", S(T([(10.6, -229.8), (14.6, -229.6), (18.8, -227.2)]))))                               # brow, knitted down
    o.append(el("detail", S(T([(16.6, -212.8), (18, -213.8), (20.8, -213.6)]))))                               # mouth, turned down
    o.append(el("detail", S(T([(-1, -242.5), (-9.5, -228), (-12.5, -210)]))))                                    # cloth fold
    # ---- mantle: diagonal edge across the back, hem above the tunic, folds, tassel
    o.append(el("detail", S(T([(-20.5, -196), (-7, -181), (8, -164), (19.5, -146)]))))
    o.append(el("detail", S(T([(-37.5, -58), (-22, -53.5), (-5, -55.5), (12, -60), (27.5, -67)]))))
    o.append(el("detail", S(T([(-26, -170), (-11, -149), (3, -126), (13, -106)]))))
    o.append(el("detail", S(T([(-25.5, -134), (-13, -111), (-2, -90), (7, -73)]))))
    o.append(el("detail", S(T([(-30, -92), (-33, -76), (-34.5, -61)]))))
    o.append(el("detail", S(T([(-24, -27), (-22.5, -36)])) + " " + S(T([(4, -28.5), (5.5, -38)]))))
    # ---- hatching (self-drawing)
    o.append(el("hatch", hatch(T([(8, -164), (19.5, -146), (18, -134), (20, -112), (24.5, -84), (27.5, -67), (12, -60), (13, -106)]), 62, 3.3 * s)))
    o.append(el("hatch", hatch(T([(-24.5, -140), (-27, -112), (-31.5, -88), (-27, -100), (-23, -128)]), 62, 3.3 * s)))
    o.append(el("hatch", hatch(T([(11, -216), (21.8, -214.4), (22.6, -209.8), (21.6, -204.8), (17.6, -200.2), (11, -199.2), (5.5, -202), (8, -210)]), 78, 2.2 * s)))
    o.append(el("hatch", hatch(T([(-13.5, -235.5), (-17, -221), (-19.5, -204), (-16, -195.5), (-12.5, -210), (-9.5, -228)]), 70, 2.8 * s)))
    o.append(el("hatch", hatch(T([(-10, -55), (12, -60), (27.5, -67), (27.5, -37.5), (14, -31), (1, -28)]), 62, 3.3 * s)))
    o.append(el("hatch", hatch(T([(22, -181), (30, -170), (36, -164), (30, -176)]), 30, 2.6 * s)))
    o.append(el("hatch", K.P(T([(27.4, -67), (26.6, -58.5)])) + " " + K.P(T([(28.4, -67), (29.6, -58.8)])) + " " + K.P(T([(27.9, -67), (28, -57.6)]))))
    return "".join(o)


def part_b():
    return man_glancing(470, 690, 1.04)


if __name__ == "__main__":
    pass
