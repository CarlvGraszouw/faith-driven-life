"""b01-caesars-coin: "The coin carried Caesar's face, so it belonged to Caesar, and he could have it back."
Left: the denarius with Tiberius' laureate head. A curved arrow carries it back to the right, where
Tiberius himself stands, half length, in the toga of the early Empire: the SAME face as the coin
(the coin portrait, mirrored, at the same size), laurel wreath with ribbons, short-sleeved tunic,
the toga's rolled balteus across the chest with the umbo pulled over it, the sinus sweeping from
the right hip to the left forearm, a scroll in the left fist; the right hand held out, palm up,
to take back what is his."""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from lib_v2 import L, D, H, svg, write, BLUE  # noqa: E402
from inkgeom import poly_d, cr_dense, clip_outside, path_pts, path_subpaths, hatch, ell_pts  # noqa: E402
import denarius as dn  # noqa: E402
import roman_caps as rc  # noqa: E402

OUT = os.path.join(HERE, "..", "B")
COIN = dn.Coin(452, 418, 150)


# ---------------------------------------------------------------- the coin (medium size)
def coin_parts():
    C = COIN
    line, det, hat = [], [], []
    flan = C.flan_pts(seed=5)
    fill = f'  <path class="line" fill="{BLUE}" fill-opacity="0.32" style="mix-blend-mode:multiply" d="{C.pd(flan, True)}"/>\n'
    wr, leaves, ribs = dn.wreath(n=9)
    line.append(C.d(dn.PROFILE))
    line.append(C.d(dn.BACK))
    for run in clip_outside(path_pts(dn.CROWN, 14), leaves, step=1.5, min_len=6):
        line.append(C.pd(run))
    det.append(C.d(dn.EAR))
    det.append(C.pd(wr))
    det.append(C.d(dn.EYE + " " + dn.BROW))
    hat.append(C.d(dn.NOSTRIL + " " + dn.MOUTH))
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


# ---------------------------------------------------------------- Tiberius, half length, facing the coin
HEAD_S = 0.45               # the coin's own scale (150/330): the man and the coin show the same face
HEAD_AT = (1180, 262)       # where the coin's (0,0) lands (mirrored: he faces left, toward the coin)


def hx(pts):
    return [(HEAD_AT[0] - x * HEAD_S, HEAD_AT[1] + y * HEAD_S) for x, y in pts]


def hp(d, n=10):
    return hx(path_pts(d, n))


def hpd(d, n=10, eps=0.12):
    """coin-unit path data (several sub-paths) -> mirrored art path data, one M per sub-path"""
    return " ".join(poly_d(hx(sp), eps=eps) for sp in path_subpaths(d, n))


def S(pts, n=6, closed=False):
    return cr_dense(pts, n, closed)


# --- the front silhouette, ONE stroke: far shoulder, sleeve, arm, open hand, forearm, elbow, hip
SHOULDER = [(1141, 338), (1118, 345), (1094, 355), (1072, 368), (1055, 384), (1043, 404), (1036, 432),
            (1033, 460), (1030, 479)]
ARM_FRONT = [(1030, 479), (1036, 484), (1033, 504), (1030, 526), (1029, 541)]            # biceps to the crook
FOREARM_TOP = [(1029, 541), (1010, 537), (984, 531), (957, 527), (931, 524), (908, 522)]
HAND = [(908, 522),
        (898, 516), (889, 510), (880, 503),                                              # ball of the thumb
        (872, 495), (864, 487), (856, 480), (849, 475.5), (844, 474), (840.5, 476.5), (841.5, 481.5),  # thumb
        (845, 487), (848.5, 493), (850, 499),                                            # inner thumb to web
        (838, 501.5), (824, 501), (811, 498.5), (802, 496),                              # forefinger, rising
        (796.5, 496), (795, 500), (797, 502.5),                                          # forefinger tip
        (791, 503), (789, 507.5), (792, 510.5),                                          # middle tip
        (788.5, 513), (789, 517.5), (793.5, 519.5),                                      # ring tip
        (792, 523), (795, 527), (800, 528.5),                                            # little tip
        (810, 533.5), (824, 538.5), (840, 542), (857, 546), (873, 550.5), (890, 552.5), (908, 549)]  # little finger, heel
FOREARM_BOT = [(908, 549), (931, 555), (960, 562), (992, 569), (1024, 575), (1050, 580), (1064, 580),
               (1072, 574), (1077, 562)]
HIP = [(1077, 562), (1081, 578), (1083, 602), (1080, 642), (1079, 684), (1082, 724), (1085, 758)]

# --- the near side: the toga heaped on the left shoulder, over the wrapped left arm, falling to the cut
TOGA_BACK = [(1216, 340), (1238, 331), (1264, 332), (1291, 342), (1317, 361), (1337, 388), (1348, 425),
             (1352, 470), (1354, 520), (1357, 566), (1360, 598), (1356, 640), (1357, 700), (1360, 758)]
NECK_BACK = [(1219, 339), (1216, 328), (1216.5, 316), (1220.5, 302.5)]

# --- inner contours
HEM_CHEST = [(1030, 479), (1040, 486), (1054, 487), (1066, 489), (1078, 482), (1085, 470),   # sleeve hem
             (1087, 490), (1088, 520), (1085, 548), (1079, 562)]                            # chest before the arm
NECKLINE = [(1145, 355), (1160, 366), (1180, 370), (1200, 365), (1216, 352)]
# the balteus (the toga's rolled upper edge) with the umbo, a loop of cloth pulled out over it: ONE stroke
# top edge -> round the umbo -> top edge to the arm -> (down the chest line) -> bottom edge, retracing the
# umbo's lower rim where the band passes behind it -> bottom edge to the shoulder
BALTEUS_TOP_A = [(1308, 354), (1282, 366), (1246, 384), (1208, 403)]
UMBO = [(1208, 403), (1214, 424), (1212, 452), (1201, 478), (1182, 494), (1163, 492), (1151, 477), (1146, 456),
        (1149, 435)]
BALTEUS_TOP_B = [(1149, 435), (1122, 447), (1087, 463)]
BALTEUS_BOT_A = [(1087, 463), (1087, 482), (1089, 500), (1110, 492), (1130, 484), (1147, 470)]
UMBO_RIM = [(1147, 470), (1151, 477), (1163, 492), (1182, 494), (1201, 478), (1210, 455), (1212, 446)]
BALTEUS_BOT_B = [(1212, 446), (1254, 421), (1296, 401), (1326, 390), (1346, 400)]
FOLDS = [[(1092, 516), (1118, 530), (1150, 543), (1180, 549), (1204, 545)],
         [(1090, 552), (1110, 575), (1140, 594), (1176, 605), (1214, 603), (1238, 596)],
         [(1150, 601), (1172, 624), (1204, 638), (1232, 640)],
         [(1098, 620), (1122, 652), (1156, 674), (1196, 682), (1232, 674)]]
SINUS = [(1083, 602), (1093, 660), (1118, 708), (1160, 737), (1208, 740), (1243, 714), (1258, 670)]
SHOULDER_FOLD = [(1316, 382), (1322, 422), (1326, 478), (1330, 534), (1334, 572)]
# the toga over the left forearm (pointing at us), the fist with the scroll, the hanging end (lacinia)
DRAPE = [(1357, 566), (1330, 576), (1302, 588), (1282, 596),
         (1268, 594), (1254, 596), (1245, 602), (1241, 611), (1241, 621), (1245, 629), (1254, 635), (1268, 636),
         (1281, 632), (1279, 660), (1283, 690), (1279, 724), (1282, 756)]
THUMB = [(1275, 604), (1261, 603), (1251, 608)]
SCROLL_TOP = [(1250, 598), (1252, 580), (1271, 580.5), (1270, 595)]
SCROLL_BOT = [(1247, 636), (1244, 650), (1261, 652.5), (1264, 637)]
LACINIA = [[(1304, 604), (1308, 660), (1306, 712), (1309, 750)], [(1330, 590), (1334, 650), (1333, 700), (1336, 744)]]
LOWER = [[(1112, 712), (1114, 756)], [(1152, 737), (1154, 760)], [(1206, 736), (1207, 758)],
         [(1240, 716), (1242, 754)]]
FINGERS = [[(797, 502.5), (814, 505.5), (832, 508)], [(792, 510.5), (812, 514), (832, 517)],
           [(793.5, 519.5), (814, 524), (836, 529)]]


def head_parts():
    line, det, hat = [], [], []
    wr, leaves, ribs = dn.wreath(n=9)
    leaves_m = [hx(lf) for lf in leaves]
    line.append(poly_d(hp(dn.PROFILE)))
    line.append(poly_d(S(NECK_BACK, 4) + hp(dn.BACK_HAIR)[1:]))
    for run in clip_outside(hp(dn.CROWN, 14), leaves_m, step=1.0, min_len=4):
        line.append(poly_d(run))
    det.append(poly_d(hx(wr), eps=0.12))
    det.append(hpd(dn.EAR))
    det.append(hpd(dn.EYE) + " " + hpd(dn.IRIS) + " " + hpd(dn.BROW))
    det.append(hpd(dn.NOSTRIL) + " " + hpd(dn.MOUTH))
    det.append(poly_d(hx(dn.hairline_edge()), eps=0.12))
    for t in dn.ties():
        det.append(poly_d(hx(t), eps=0.12))
    hat.append(hpd(dn.EAR_IN) + " " + hpd(dn.LID))
    hat += [poly_d(hx(r), eps=0.12) for r in dn.hair_texture(leaves, row_gap=24, lock_w=15)]
    hat += [poly_d(hx(r), eps=0.12) for r in ribs]
    # modelling of the face and neck: the coin's engraving without the field shadows
    sh = []
    n_ = dn._n
    sh += dn.shade_patch([(112, 106), (92, 110), (60, 104), (30, 94), (14, 104), (40, 120), (76, 124)],
                         -62, 8.0, seed=5, shorten=0.1, fade=0.35)
    sh += dn.comb([(-90, 96), (-84, 106), (-80, 122), (-80, 140)], n_((-0.9, 0.3)), 18, 4.4, seed=7, taper=0.5)
    sh += dn.comb([(-24, 30), (0, 80), (24, 130), (44, 182)], n_((0.95, 0.3)), 12, 6.5, seed=14, taper=1.0)
    sh += dn.comb([(100, -91), (116, -95), (132, -95), (140, -92)], n_((0.25, 1)), 9, 3.4, seed=8)
    sh += dn.comb([(66, -100), (80, -102), (94, -96)], n_((0.4, 1)), 14, 4.2, seed=9)
    sh += dn.comb([(92, -34), (104, -24), (114, -8), (118, 8)], n_((-0.55, 0.85)), 22, 5.5, seed=10, taper=1.2)
    sh += dn.shade_patch([(150, 8), (160, 7), (168, 6), (160, 11), (152, 12)], 20, 3.0, seed=11, fade=0.1)
    sh += dn.comb([(-16, -32), (-12, -16), (-16, 0)], n_((0.7, 0.7)), 10, 3.6, seed=13)
    hat += [poly_d(hx(s), eps=0) for s in sh]
    return line, det, hat


def body_parts():
    line, det, hat = [], [], []
    front = (S(SHOULDER) + S(ARM_FRONT, 4)[1:] + S(FOREARM_TOP)[1:] + S(HAND, 3)[1:] + S(FOREARM_BOT)[1:]
             + S(HIP)[1:])
    line.append(poly_d(front))
    line.append(poly_d(S(TOGA_BACK)))
    det.append(poly_d(S(HEM_CHEST, 4)))
    det.append(poly_d(S(NECKLINE, 4)))
    det.append(poly_d(S(BALTEUS_TOP_A) + S(UMBO, 4)[1:] + S(BALTEUS_TOP_B)[1:] + S(BALTEUS_BOT_A, 4)[1:]
                      + UMBO_RIM[1:] + S(BALTEUS_BOT_B)[1:]))
    det.append(" ".join(poly_d(S(f)) for f in FOLDS))
    det.append(poly_d(S(SINUS)))
    det.append(poly_d(S(SHOULDER_FOLD)))
    det.append(poly_d(S(DRAPE, 4)))
    det.append(poly_d(S(THUMB, 3)))
    det.append(poly_d(S(SCROLL_TOP, 3)) + " " + poly_d(S(SCROLL_BOT, 3)))
    det.append(" ".join(poly_d(S(f, 3)) for f in FINGERS))
    # hatch: secondary folds and lines
    hat.append(" ".join(poly_d(S(f, 4)) for f in LACINIA))
    hat.append(" ".join(poly_d(S(f, 3)) for f in LOWER))
    umbo_poly = S(UMBO, 4)
    hat.append(" ".join(poly_d(r) for r in clip_outside(S([(1098, 482), (1146, 461), (1196, 434), (1246, 406),
                                                            (1290, 386)]), [umbo_poly], step=1.0)))    # balteus' inner roll
    hat.append(" ".join(poly_d(S(f, 4)) for f in ([(1156, 446), (1160, 466), (1170, 484)],
                                                    [(1172, 430), (1176, 456), (1184, 482)],
                                                    [(1192, 418), (1196, 440), (1198, 466)])))           # umbo's gathers
    hat.append(" ".join(poly_d(S(f, 4)) for f in (
        [(1060, 401), (1053, 438), (1052, 474)], [(1074, 404), (1072, 440), (1069, 478)],      # sleeve folds
        [(1112, 372), (1126, 400), (1134, 430)], [(1150, 382), (1166, 404), (1174, 418)],      # tunic folds
        [(850, 501), (860, 512), (874, 524), (894, 534)])))                                     # palm crease
    hat.append(poly_d(ell_pts(1261.5, 580.5, 9.5, 3.0, 0, 360, 24)) + " " + poly_d(ell_pts(1262, 580.7, 5.5, 1.6, 30, 340, 16)))

    def Hp(poly, ang, sp, seed, **k):
        k.setdefault("min_len", 2.0)
        return " ".join(poly_d(s, eps=0) for s in hatch(S(poly, 5, True), ang, sp, seed=seed, **k))

    def under(guide, w, ang, sp, seed, **k):
        """a shadow band hanging under a fold line, thickest mid-fold"""
        G = S(guide, 6)
        m = len(G)
        low = [(x, y + w * math.sin(math.pi * i / (m - 1)) ** 0.8) for i, (x, y) in enumerate(G)]
        return Hp(G + list(reversed(low)), ang, sp, seed, **k)
    # light from the upper left: the near side of the toga, under the balteus, umbo and folds, the arm's underside
    hat.append(Hp([(1337, 391), (1348, 425), (1352, 470), (1354, 520), (1357, 566), (1360, 598), (1356, 640),
                   (1357, 700), (1359, 744), (1344, 740), (1342, 660), (1338, 600), (1336, 520), (1330, 450),
                   (1318, 404)], 80, 4.4, 3, fade=0.3, jitter=0.3))
    hat.append(under([(1089, 500), (1130, 484), (1147, 470)], 9, 60, 3.2, 4))
    hat.append(under([(1212, 446), (1254, 421), (1296, 401), (1326, 390)], 10, 60, 3.2, 12))
    hat.append(under([(1151, 477), (1163, 492), (1182, 494), (1201, 478), (1210, 455)], 9, 30, 3.0, 5))
    hat.append(Hp([(1214, 424), (1212, 452), (1201, 478), (1196, 470), (1204, 448), (1206, 424)], 70, 2.8, 15))
    for i, f in enumerate(FOLDS):
        hat.append(under(f, 13 - 2 * i, 35, 3.4, 20 + i, fade=0.2))
    hat.append(under(SINUS[:-1], 14, 35, 3.4, 7, fade=0.2))
    hat.append(under([(1357, 566), (1330, 576), (1302, 588), (1282, 596)], 16, 75, 3.4, 6, fade=0.2))
    hat.append(Hp([(1036, 486), (1062, 489), (1080, 482), (1082, 502), (1062, 499), (1036, 494)], 20, 3.0, 8))
    hat.append(Hp([(931, 555), (960, 562), (992, 569), (1024, 575), (1050, 580), (1064, 580), (1060, 570),
                   (1024, 566), (990, 559), (958, 553), (932, 548)], 15, 2.8, 9))
    hat.append(" ".join(poly_d(S(f, 4)) for f in ([(866, 511), (878, 522), (892, 531)], [(872, 506), (886, 518), (899, 527)])))
    return line, det, hat


def arrow():
    """the coin goes back to its owner: an arc from the coin to the open palm, with an arrowhead"""
    p = cr_dense([(600, 326), (654, 262), (726, 230), (796, 240), (846, 290), (868, 360), (874, 452)], 8)
    tip = p[-1]
    a = math.atan2(tip[1] - p[-4][1], tip[0] - p[-4][0])
    l = 20
    h1 = (tip[0] - l * math.cos(a - 0.45), tip[1] - l * math.sin(a - 0.45))
    h2 = (tip[0] - l * math.cos(a + 0.45), tip[1] - l * math.sin(a + 0.45))
    return poly_d(p + [h1, tip, h2])


def body():
    fill, cl, cd, ch = coin_parts()
    hl, hd, hh = head_parts()
    bl, bd, bh = body_parts()
    b = fill
    b += "".join(L(d) for d in cl)
    b += COIN.beads(dia=7.0 / COIN.s * 0.75, gap=13.0)
    b += "".join(D(d) for d in cd)
    b += "".join(L(d) for d in hl)
    b += "".join(D(d) for d in hd)
    b += "".join(L(d) for d in bl)
    b += "".join(D(d) for d in bd)
    b += L(arrow())
    b += H(" ".join(ch)) + H(" ".join(hh)) + H(" ".join(bh))
    return b


if __name__ == "__main__":
    write(os.path.join(OUT, "b01-caesars-coin.svg"), svg(body(), "b01: the coin bears Caesar's face, so it goes back to Caesar"))
