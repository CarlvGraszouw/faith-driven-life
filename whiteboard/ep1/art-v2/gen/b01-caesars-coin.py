"""b01-caesars-coin: "The coin carried Caesar's face, so it belonged to Caesar, and he could have it back."
Left: the denarius with Tiberius' laureate head. A curved arrow carries it back to the right, where
Tiberius himself (the same profile, mirrored) stands in the toga with the laurel wreath, his open
hand held out to receive what is his."""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from lib_v2 import L, D, H, svg, write, BLUE, tx  # noqa: E402
from inkgeom import poly_d, cr_dense, clip_outside, path_pts, hatch, resample, ell_pts  # noqa: E402
import denarius as dn  # noqa: E402
import roman_caps as rc  # noqa: E402

OUT = os.path.join(HERE, "..", "B")
COIN = dn.Coin(452, 418, 150)
FIG_DX = -64


# ---------------------------------------------------------------- the coin (medium size)
def coin_parts():
    C = COIN
    line, det, hat = [], [], []
    flan = C.flan_pts(seed=5)
    fill = f'  <path class="line" fill="{BLUE}" fill-opacity="0.32" style="mix-blend-mode:multiply" d="{C.pd(flan, True)}"/>\n'
    wr, leaves, ribs = dn.wreath(n=11)
    line.append(C.d(dn.PROFILE + " " + dn.BACK_NECK[dn.BACK_NECK.index("C"):] if False else dn.PROFILE))
    line.append(C.d(dn.BACK))
    for run in clip_outside(path_pts(dn.CROWN, 14), leaves, step=1.5, min_len=6):
        line.append(C.pd(run))
    det.append(C.d(dn.EAR))
    det.append(C.pd(wr))
    det.append(C.d(dn.EYE + " " + dn.BROW.replace("M", "M", 1)))
    det.append(C.d(dn.NOSTRIL + " " + dn.MOUTH))
    det.append(C.pd(dn.hairline_edge()))
    hat += [C.pd(r) for r in dn.hair_texture(leaves, row_gap=26, lock_w=16)]
    hat += [C.pd(s, eps=0) for s in dn.obverse_shading()]
    # the legend, finely engraved (hatch weight, drawn with the texture)
    for d in rc.strokes_to_d(rc.on_arc("TI CAESAR DIVI AVG F AVGVSTVS", C.cx, C.cy, 258 * C.s, 50 * C.s,
                                       -147, 147, squeeze=0.86)):
        hat.append(d)
    contour, band = C.edge(flan)
    line.append(C.pd(contour))
    hat += [C.pd(s, eps=0) for s in dn.hatch(band, 70, 3.2 / C.s, jitter=0.3, seed=19, min_len=1.5)]
    return fill, line, det, hat


# ---------------------------------------------------------------- Tiberius in the toga, facing left
HEAD_S = 0.262              # coin units -> art units for the portrait head (head 88 tall, figure ~600)
HEAD_AT = (1130, 206)       # where the coin's (0,0) lands (mirrored head)


def head_pts(d, n=10):
    """coin-unit path -> mirrored (facing left) art coordinates for the figure's head"""
    return [(HEAD_AT[0] - x * HEAD_S, HEAD_AT[1] + y * HEAD_S) for x, y in path_pts(d, n)]


def head_xy(pts):
    return [(HEAD_AT[0] - x * HEAD_S, HEAD_AT[1] + y * HEAD_S) for x, y in pts]


FIG = {
    # back: nape, the far shoulder heaped with the toga, the toga over the bent left arm, its fall
    "back": [(1152, 230), (1170, 244), (1200, 254), (1230, 268), (1248, 294), (1254, 340), (1258, 392),
             (1260, 440), (1254, 500), (1248, 570), (1244, 640), (1242, 700), (1238, 738)],
    # front: throat, neckline, chest under the raised arm, the columnar front fall to the hem
    "front": [(1104, 236), (1100, 250), (1084, 258), (1064, 266), (1050, 282), (1072, 300), (1082, 330), (1084, 360), (1082, 400),
              (1078, 460), (1078, 520), (1080, 590), (1082, 660), (1086, 738)],
    "hem": [(1086, 738), (1120, 744), (1164, 745), (1206, 743), (1238, 738)],
    "feet": [(1096, 742), (1080, 748), (1064, 754), (1072, 760), (1116, 760), (1120, 746)],
    "foot2": [(1178, 746), (1170, 754), (1186, 760), (1222, 758), (1218, 746)],
    # right arm out of the short tunic sleeve, reaching forward; open hand, palm up, thumb raised
    "arm": [(1050, 282), (1036, 296), (1022, 314), (1002, 328), (982, 336), (966, 340),
            (958, 331), (950, 323), (943, 318), (938, 321), (941, 329), (948, 338),
            (930, 340), (914, 341), (902, 343), (896, 348), (900, 353), (914, 355), (932, 357), (950, 361),
            (966, 362), (988, 360), (1014, 350), (1036, 334), (1056, 318), (1072, 300)],
    "sleeve": [(1050, 270), (1036, 288), (1044, 304), (1060, 306)],
    "fingers": [(948, 344), (930, 346), (912, 348), (946, 351), (928, 352), (910, 353)],
}
TOGA_FOLDS = [
    # the balteus: the toga's band from the left shoulder diagonally down to the right hip
    [(1196, 252), (1168, 290), (1140, 330), (1112, 370), (1084, 410)],
    [(1228, 266), (1198, 312), (1168, 354), (1138, 396), (1108, 436)],
    # the umbo: the pouch of toga pulled out over the band
    [(1170, 318), (1150, 322), (1136, 338), (1142, 356), (1162, 360), (1176, 348)],
    # the sinus: the deep curve of the toga from the right hip round the thighs up to the left forearm
    [(1082, 420), (1090, 482), (1112, 530), (1152, 554), (1200, 550), (1236, 520), (1254, 470)],
    [(1080, 446), (1092, 510), (1118, 556), (1162, 578), (1212, 572), (1248, 540)],
    # the left forearm across the waist, wrapped in the toga; the hand holds a scroll
    [(1258, 418), (1238, 426), (1216, 436), (1200, 442)],
    [(1256, 446), (1236, 454), (1218, 460), (1204, 464)],
    [(1200, 442), (1190, 446), (1186, 456), (1192, 466), (1204, 464)],
]
SCROLL = [(1188, 444), (1168, 450), (1172, 466), (1192, 460), (1188, 444), (1184, 452), (1188, 458)]
LOWER_FOLDS = [[(1104, 590), (1108, 650), (1106, 734)], [(1142, 598), (1146, 662), (1144, 742)],
               [(1184, 594), (1188, 660), (1186, 742)], [(1222, 586), (1224, 656), (1222, 738)],
               [(1206, 262), (1230, 300), (1240, 344)], [(1180, 254), (1204, 292), (1220, 336)]]


def figure_parts():
    line, det, hat = [], [], []
    # head: the coin portrait, mirrored to face the coin
    prof = head_pts("M 124 -150 " + dn.PROFILE.split(" ", 3)[3].split(" C 90 112")[0])
    line.append(poly_d(prof))
    line.append(poly_d(head_pts(dn.BACK_HAIR)))
    crown = head_pts(dn.CROWN)
    wr, leaves, ribs = dn.wreath(n=11)
    leaves_m = [head_xy(lf) for lf in leaves]
    for run in clip_outside(crown, leaves_m, step=0.8, min_len=3):
        line.append(poly_d(run))
    det.append(poly_d(head_xy(wr), eps=0.1))
    det.append(poly_d(head_pts(dn.EAR), eps=0.1))
    det.append(poly_d(head_pts(dn.EYE + " " + dn.IRIS + " " + dn.BROW), eps=0.1))
    det.append(poly_d(head_pts(dn.NOSTRIL + " " + dn.MOUTH), eps=0.1))
    det.append(poly_d(head_xy(dn.hairline_edge()), eps=0.1))
    hat += [poly_d(head_xy(r), eps=0.1) for r in dn.hair_texture(leaves, row_gap=28, lock_w=17)]
    hat += [poly_d(head_xy(r), eps=0.1) for r in ribs]
    # body
    for k in ("back", "front", "arm"):
        line.append(poly_d(cr_dense(FIG[k], 6)))
    det.append(poly_d(cr_dense(FIG["hem"], 5)))
    det.append(poly_d(cr_dense(FIG["feet"], 4)) + " " + poly_d(cr_dense(FIG["foot2"], 4)))
    det.append(poly_d(cr_dense(FIG["sleeve"], 4)))
    f = FIG["fingers"]
    det.append(poly_d(f[:3]) + " " + poly_d(f[3:]))
    for f in TOGA_FOLDS:
        det.append(poly_d(cr_dense(f, 5)))
    det.append(poly_d(cr_dense(SCROLL, 4)))
    hat += [poly_d(cr_dense(f, 5)) for f in LOWER_FOLDS]
    # shading: the far side of the toga, under the sinus, the folds, the ground shadow
    def H_(poly, ang, sp, seed, **k):
        return " ".join(poly_d(s, eps=0) for s in hatch(cr_dense(poly, 5, True), ang, sp, seed=seed, min_len=2, **k))
    hat.append(H_([(1248, 292), (1258, 392), (1258, 470), (1248, 570), (1242, 700), (1226, 690), (1232, 560),
                   (1240, 470), (1238, 380), (1230, 310)], 70, 4.0, 3, fade=0.2))
    hat.append(H_([(1092, 510), (1118, 556), (1162, 578), (1212, 572), (1248, 540), (1244, 566), (1206, 594),
                   (1156, 598), (1104, 570)], 30, 3.4, 4))
    hat.append(H_([(1112, 370), (1084, 410), (1082, 428), (1108, 436), (1138, 396)], 60, 3.2, 6))
    hat.append(H_([(1022, 314), (1002, 328), (1014, 350), (1036, 334)], 60, 3.0, 7))
    hat.append(H_([(950, 361), (966, 362), (988, 360), (1004, 354), (978, 352), (956, 355)], 20, 2.6, 8))
    hat.append(" ".join(poly_d(s, eps=0) for s in hatch(ell_pts(1162, 760, 104, 9, 0, 360, 30), -12, 3.2, seed=5,
                                                         min_len=2, shorten=0.15)))
    return line, det, hat


def arrow():
    """the coin goes back to its owner: an arc from the coin to the open hand, with an arrowhead"""
    p = cr_dense([(600, 300), (668, 214), (764, 182), (832, 206), (862, 262), (866, 322)], 8)
    tip = p[-1]
    a = math.atan2(tip[1] - p[-4][1], tip[0] - p[-4][0])
    l = 22
    h1 = (tip[0] - l * math.cos(a - 0.45), tip[1] - l * math.sin(a - 0.45))
    h2 = (tip[0] - l * math.cos(a + 0.45), tip[1] - l * math.sin(a + 0.45))
    return poly_d(p + [h1, tip, h2])


def body():
    fill, cl, cd, ch = coin_parts()
    fl, fd, fh = figure_parts()
    b = fill
    b += "".join(L(d) for d in cl)
    b += C_beads()
    b += "".join(D(d) for d in cd)
    b += "".join(L(tx(d, 1, FIG_DX, 0)) for d in fl)
    b += "".join(D(tx(d, 1, FIG_DX, 0)) for d in fd)
    b += L(arrow())
    b += "".join(H(d) for d in ch)
    b += "".join(H(tx(d, 1, FIG_DX, 0)) for d in fh)
    return b


def C_beads():
    return COIN.beads(dia=7.0 / COIN.s * 0.75, gap=13.0)


if __name__ == "__main__":
    write(os.path.join(OUT, "b01-caesars-coin.svg"), svg(body(), "b01: the coin bears Caesar's face, so it goes back to Caesar"))
