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


def ground_shadow(T, x0, x1, y, h=5.0, gap=2.2):
    """soft cast shadow: short horizontal hatch strokes in a flat ellipse (self-drawing)"""
    cx, rx = (x0 + x1) / 2, (x1 - x0) / 2
    poly = [(cx + rx * math.cos(a / 20 * math.pi * 2), y + h * math.sin(a / 20 * math.pi * 2)) for a in range(20)]
    return el("hatch", hatch(T(poly), 0, gap, start=0.3))


def band(T, run, width, gap=1.7, n=None):
    """a woven border stripe along a run (parallel strokes) - self-drawing texture"""
    pts = sample(run, closed=False, n=6)
    out = []
    n = n or max(2, int(width / gap))
    for k in range(n):
        off = (k + 0.5) * width / n
        row = []
        for a in range(len(pts)):
            p0 = pts[max(0, a - 1)]; p1 = pts[min(len(pts) - 1, a + 1)]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            ln = math.hypot(dx, dy) or 1
            row.append((pts[a][0] - dy / ln * off, pts[a][1] + dx / ln * off))
        out.append(K.P(T(row)))
    return " ".join(out)


# ============================================================== part b: the crowd turns on him
def head_runs(hx, hy, k, wear="cloth", beard="full", mouth="open", old=False):
    """profile head facing right (toward Jesus). Returns (contour runs over the head and face
    from the back/top round to the throat, detail strokes, hatch strokes) in local units.
    (hx, hy) = head centre, k = head scale (1 = 34 units crown to chin)."""
    H_ = lambda pts: [(hx + x * k, hy + y * k) for (x, y) in pts]
    det, hz = [], []
    face = [[(8.6, -14.6), (11.4, -10.4), (12.8, -7)],                       # forehead, brow (frowning bulge)
            [(11.8, -5)], [(14.6, -1.6), (17.8, 1.8)],                          # nose root, nose
            [(14.2, 3.6), (13.4, 4)], [(15, 5.6), (15.4, 6.6)]]                 # under nose, moustache/lip
    if mouth == "open":
        face += [[(12.2, 7.6)], [(14.8, 9.6)]]
    else:
        face += [[(13.8, 7.6), (14.6, 8.8)]]
    if beard == "full":
        face += [[(16.2, 12), (16.6, 16.4), (13.6, 21.2)], [(8, 20.6), (3, 17.4)]]
    elif beard == "long":
        face += [[(16.4, 13), (17.4, 20), (15.8, 28), (12, 33.6)], [(7, 28), (3, 19)]]
    elif beard == "short":
        face += [[(15.6, 11.6), (15, 15.2), (11.6, 17.6)], [(6.6, 17.2), (2.6, 15.6)]]
    else:
        face += [[(14.4, 11.4), (13.6, 14.4)], [(9.6, 16.2), (5, 16.4), (2.6, 18)]]
    if wear in ("cloth", "veil"):
        long_ = 30 if wear == "veil" else 24
        back = [[(-14, -15), (-19.4, -2), (-21.4, 12), (-21, long_)]]
        top = [[(-6, -21.4), (4, -20.6)], [(8.6, -14.6)]]
        det.append(H_([(8.6, -14.6), (4.6, -8), (2.2, 2), (1.6, 12), (2.6, 17.6)]))      # cloth edge round the face
        hz.append(H_([(-12, -16), (-17, -2), (-19, 14), (-18.6, long_ - 2)]))
        hz.append(H_([(-4, -20), (-10, -6), (-12.6, 8), (-12.4, long_ - 4)]))
    elif wear == "curly":
        back = [[(-11.6, -12.6), (-14.6, -2.6), (-12.6, 7.6), (-8.4, 14.6)]]
        top = [[(-7, -19.6), (-2.6, -21.6)], [(1.6, -20.6), (5.6, -19.8)], [(8.6, -14.6)]]
        det.append(H_([(-2, -2.6), (-4.4, -1), (-4, 3.4), (-1.6, 4.6)]))                  # ear
        for (a, b) in ((-8, -16), (-2, -18), (4, -16.6), (-12, -8), (-12.6, 2)):
            hz.append(H_([(a, b), (a + 2.6, b - 1.6), (a + 4, b + 0.6), (a + 2, b + 2.6)]))
    else:  # white hair, balding elder
        back = [[(-11.6, -12.6), (-14.6, -2.6), (-12.6, 7.6), (-8.4, 14.6)]]
        top = [[(-5, -20.4), (3, -20)], [(8.6, -14.6)]]
        det.append(H_([(-2, -2.6), (-4.4, -1), (-4, 3.4), (-1.6, 4.6)]))
        hz.append(H_([(-12, -11), (-9, -6), (-12.4, -1), (-9, 4)]))
    # eye + knitted brow (one stroke), mouth corner
    det.append(H_([(9.8, -3.4), (8.2, -4.4), (6.4, -3.6), (8.2, -2.6), (9.8, -3.4)]) + H_([(5.4, -7.8), (8.6, -8.4), (12.4, -6.4)]))
    if mouth == "open":
        hz.append(("mouth", H_([(12.4, 7.6), (14.8, 6.8), (14.6, 9.4)])))
    else:
        hz.append(H_([(13.8, 7.6), (11, 8.4)]))
    if beard in ("full", "long", "short"):
        bb = {"full": [(12, 4), (15.4, 6.6), (16.2, 12), (16.6, 16.4), (13.6, 21.2), (8, 20.6), (5, 14), (7, 8)],
              "long": [(12, 4), (15.4, 6.6), (16.4, 13), (17.4, 20), (15.8, 28), (12, 33.6), (7, 28), (5, 16), (7, 8)],
              "short": [(12, 5), (15.4, 6.6), (15.6, 11.6), (15, 15.2), (11.6, 17.6), (6.6, 17.2), (6, 10)]}[beard]
        hz.append(("beard", H_(bb), old))
    return back, top, face, det, hz


def crowd_figure(x, y, s, wear="cloth", beard="full", mouth="open", old=False, gesture="point",
                 lean=0.0, hs=1.0, stripe=True, girth=1.0, stripes=0):
    """one member of the crowd, facing right toward Jesus, ~250 units tall at s=1.
    gesture: point | fist | staff | chest | crossed.  Returns svg string."""
    def T(pts):
        out = []
        for (px, py) in pts:
            px = px + lean * (-py) / 250.0          # lean the upper body toward Jesus
            out.append((x + px * s, y + py * s))
        return out
    hx, hy = 3, -226
    back, top, face, det, hz = head_runs(hx, hy, hs, wear, beard, mouth, old)
    # contour, clockwise from the back of the head: head top -> face -> throat -> (gesture arm) ->
    # chest/front -> hem -> feet -> back -> shoulders -> back of head.  The gesturing arm is part
    # of the one contour, so each person is a single confident pen stroke.
    if gesture == "point":
        front = [[(10, -201), (16, -196)],
                 [(28, -191.6), (40, -187), (54, -183)], [(64.6, -181.6)],            # top of the arm -> fingertip
                 [(65, -178.6), (58, -178.2)], [(57.4, -175.4), (52, -173.6)],       # finger, curled fingers
                 [(41, -174.4), (30, -174.4), (24.6, -170)],                         # under the arm
                 [(24.4, -152), (22.2, -134)]]
        hz.append([(46, -186.6), (45.6, -176)])
    elif gesture == "fist":
        front = [[(10, -201), (16, -193)],
                 [(23, -205), (28.2, -221), (30.6, -236.6)],                         # arm up
                 [(29.8, -238.6), (30.8, -247), (36.8, -249.6), (41.8, -246.4), (41.6, -238.4), (38.2, -235)],
                 [(38.8, -222), (35.2, -205), (29.6, -188)],
                 [(26.6, -172), (24.4, -152), (22.2, -134)]]
        hz.append([(31.8, -244), (38.8, -243.4)])
        hz.append([(27.6, -216.4), (35, -217.6)])
    elif gesture == "staff":
        front = [[(10, -201), (19, -197.6), (25.6, -189)],
                 [(31, -176), (42, -165)], [(52, -168.6), (57, -164.4), (55.4, -157)],   # arm forward, hand on the staff
                 [(47.6, -155.6), (40, -157), (29.6, -164)],
                 [(25.4, -150), (22.2, -134)]]
    elif gesture == "crossed":
        front = [[(10, -201), (19, -197.6), (25.6, -189)], [(29, -174), (30, -156), (26.4, -140)]]
        det.append([(-14, -170), (6, -164), (26, -160)])
        hz.append([(-10, -152), (10, -150), (28, -152)])
    else:
        front = [[(10, -201), (19, -197.6), (25.6, -189)], [(26.6, -172), (24.4, -152), (22.2, -134)]]
    front += [[(25.6, -112), (28.6, -80), (31.4, -50), (33.4, -16)],          # robe front
              [(36.4, -12.4), (43, -5.4), (44.6, -0.6)], [(23.6, -0.4)],          # front sandal
              [(22.8, -8.4), (20.4, -14.4)], [(12, -13.6), (4, -15.2), (-6, -13.4)],  # hem
              [(-8.6, -8.4), (-6.4, -3.4)], [(-8, 0.2)], [(-26.6, 0.2)], [(-27, -4.6), (-22.6, -12.6)],  # back sandal
              [(-29.6, -15.4), (-30.4, -50), (-28, -86), (-26.6, -116), (-24.6, -134), (-26.6, -154), (-27.4, -176), (-24.6, -192)],
              [(-16, -199.4), (-6, -202.6)]]
    runs = [[(hx + px * hs, hy + py * hs) for (px, py) in r] for r in (top + face)]
    runs += [[(px * girth if py > -200 else px, py) for (px, py) in r] for r in front]
    runs += [[(hx + px * hs, hy + py * hs) for (px, py) in r[::-1]] for r in back[::-1]]
    o = [el("line", pb_runs(T, runs), fill="#ffffff")]
    if gesture == "staff":
        o.append(el("detail", pb_runs(T, [[(50, 1)], [(56, -262)]], closed=False)))
    # girdle at the waist, and the mantle over the left shoulder (light, self-drawn)
    hz.append([(-24.6, -136), (-8, -132.6), (8, -132.6), (22.4, -135.4)])
    hz.append([(-24.6, -131), (-8, -127.6), (8, -127.6), (22.4, -130.4)])
    hz.append([(-24.6, -192), (-12, -178), (-2, -160), (6, -142)])
    o += [el("detail", S(T(d))) if len(d) > 2 else el("detail", P(T(d))) for d in det]
    hzs = []
    for h in hz:
        if isinstance(h, tuple):
            kind = h[0]
            pts = T(h[1])
            if kind == "mouth":
                hzs.append(hatch(pts, 0, 0.8 * s, minlen=0.3))
            else:
                hzs.append(hatch(pts, 84, (2.6 if h[2] else 2.0) * s))
        else:
            hzs.append(K.S(T(h)))
    # shading on the back (light from the upper left falls on their faces), folds, border stripe
    hzs.append(hatch(T([(-24.6, -192), (-10, -176), (-14, -150), (-18, -118), (-22, -80), (-26, -40), (-29.6, -15.4), (-30.4, -50), (-28, -86), (-25.6, -118), (-26.6, -150), (-27.4, -176)]), 72, 3.0 * s))
    hzs.append(K.S(T([(4, -150), (8, -110), (12, -70), (14, -20)])) + " " + K.S(T([(-12, -140), (-14, -90), (-16, -40)])))
    if stripe:
        hzs.append(band(T, [(-29.4, -60), (-12, -56), (8, -58), (30, -62)], 4.2, n=3))
    for k in range(stripes):
        # woven vertical stripes down the mantle (Tissot-style abayas), following the drape
        x0 = -16 + k * 12
        hzs.append(band(T, [(x0 - 4, -186 + k * 4), (x0, -140), (x0 + 3, -96), (x0 + 6, -64)], 3.0, n=2))
    o.append(el("hatch", " ".join(hzs)))
    o.append(ground_shadow(T, -34, 48, 1.4))
    return "".join(o)


def part_b():
    # back to front so the white fills overlap correctly
    return (crowd_figure(236, 654, 0.98, wear="white", beard="long", old=True, gesture="staff", lean=-6, hs=1.22, girth=1.0, stripes=2)
            + crowd_figure(398, 688, 1.1, wear="curly", beard="short", gesture="fist", lean=8, hs=1.22, girth=1.22)
            + crowd_figure(306, 716, 0.72, wear="curly", beard=None, mouth="closed", gesture="crossed", hs=1.4, stripe=False, girth=1.1)
            + crowd_figure(522, 704, 1.13, wear="cloth", beard="full", gesture="point", lean=12, hs=1.2, girth=1.18, stripes=3))


# ============================================================== part c: Roman soldiers
def mail_texture(T, poly, gap=3.2, amp=0.9, step=2.6):
    """lorica hamata: rows of tiny scallops clipped to the shirt (self-drawing)"""
    pg = T(poly)
    ys = [p[1] for p in pg]
    xs = [p[0] for p in pg]
    out = []
    yy = min(ys) + gap * 0.6
    row = 0
    while yy < max(ys):
        for (a, b) in K._clip_scan(pg, yy):
            if b - a < 4:
                continue
            pts = []
            xx = a + (row % 2) * step * 0.5
            k = 0
            while xx <= b:
                pts.append((xx, yy + (amp if k % 2 else -amp * 0.3)))
                xx += step / 2
                k += 1
            if len(pts) > 2:
                out.append(K.S(pts))
        yy += gap
        row += 1
    return " ".join(out)


def soldier_head(T, dx=0.0):
    """galea (Imperial-Gallic): bowl, brow ridge, deep neck guard, hinged cheek guard set back over
    the ear so the stern face shows. Facing left. Returns svg (line contour, details, hatch)."""
    U_ = lambda pts: T([(x + dx, y) for (x, y) in pts])
    o = []
    head = [
        [(-19.8, -233.4)],
        [(-15.4, -241), (-8, -249), (0, -251.6), (9, -248.6), (14.8, -242), (16.6, -233.6), (18, -229.6)],
        [(25.4, -226.2), (26.4, -222.6)], [(16.4, -221.2)],                                   # neck guard
        [(12.6, -216), (11.6, -206), (10, -202)],
        [(-8.6, -203.6)],
        [(-13.2, -206.2), (-17.4, -208.2), (-18.4, -211.6)],                                  # square chin
        [(-18.6, -214.6), (-17.8, -216.4), (-18.8, -217.8)],                                  # lips, firm mouth
        [(-19, -219.4)], [(-22.8, -220.8)],                                                   # under the nose, tip
        [(-20, -224), (-17.6, -228)], [(-18.6, -230)], [(-17.6, -231.4)], [(-19.8, -233.4)],  # bridge, brow, rim
    ]
    o.append(el("line", pb_runs(U_, head, closed=False), fill="#ffffff"))
    o.append(el("detail", S(U_([(-19.8, -233.4), (-12, -234.4), (-2, -234), (8, -232.6), (17.4, -231.4)]))))
    o.append(el("detail", S(U_([(-3.4, -233.8), (-6, -226.4), (-4.6, -219), (-6.8, -212), (-2, -206.8), (4.6, -211.4), (5, -223), (3.4, -232.6)]))))
    o.append(el("detail", P(U_([(-15.8, -227.2), (-13.2, -228.6), (-10.8, -227.4), (-13, -226.2), (-15.6, -227.2)]))
                + " " + S(U_([(-17, -230.2), (-12.6, -230.6), (-9.6, -229.4)])).replace("M", "L", 1)))
    hz = [hatch(U_([(-14.2, -228.2), (-12.6, -228.6), (-12.4, -226.6), (-14, -226.6)]), 0, 0.7, minlen=0.2),
          S(U_([(-17.6, -216.4), (-14.2, -216)])), S(U_([(-17, -221.4), (-15.4, -218.4)])),
          hatch(U_([(-17.6, -231.4), (-12, -234.4), (-3.4, -233.8), (-4, -231.6), (-12, -232.2)]), 0, 1.1),
          hatch(U_([(-3.4, -233.8), (-6, -226.4), (-4.6, -219), (-6.8, -212), (-2, -206.8), (4.6, -211.4), (5, -223), (3.4, -232.6)]), 80, 2.2),
          hatch(U_([(16.4, -221.2), (26.4, -222.6), (25.4, -226.2), (18, -229.6)]), 70, 1.8),
          S(U_([(-4, -249.6), (0, -253.4), (4, -249.6)]))]                                    # crest knob
    o.append(el("hatch", " ".join(hz)))
    return "".join(o)


def legionary_front(x, y, s):
    """Front soldier, facing left toward Jesus: galea with cheek guards and neck guard, mail with
    shoulder doubling, belt and apron, gladius; scutum on his left arm; open manacles held out."""
    T = mk(x, y, s)
    o = []
    o.append(soldier_head(T))
    body = [
        [(-9.6, -203.4), (-19, -200.6), (-25.4, -195.6), (-31, -186), (-34.6, -176), (-38.6, -166.4)],
        [(-46, -170.8), (-53.8, -174.2)],
        [(-56.2, -178.6), (-62.8, -179), (-66.4, -173.4), (-65.4, -166.6), (-59.4, -164.2)],      # fist
        [(-53.4, -165.4), (-45.2, -160.8), (-39.6, -151.4)],
        [(-33.4, -161.6), (-27.6, -170)],
        [(-27.6, -152), (-26.4, -134), (-27.4, -127), (-29.6, -118), (-30.4, -104), (-31.6, -84)],
        [(-22, -81.6), (-12, -83.4), (-2, -81), (8, -83), (16.6, -84)],
        [(16, -110), (19.6, -130), (24.6, -160), (27, -184), (24.6, -194), (17.4, -200.6), (10, -202.6)],
    ]
    o.append(el("line", pb_runs(T, body), fill="#ffffff"))
    o.append(el("line", pb_runs(T, [[(-27.6, -82.4), (-30.4, -70), (-34, -48), (-36.2, -24), (-37.6, -14)],
                                     [(-43.6, -9), (-50.4, -4.4), (-51.6, -0.6)], [(-29.6, -0.4)],
                                     [(-27.4, -3.6), (-26.6, -12), (-25.2, -24), (-21.4, -50), (-17.6, -70), (-15.6, -82.6)]], closed=False), fill="#ffffff"))
    o.append(el("line", pb_runs(T, [[(6, -29), (5.6, -16), (2, -9), (-4, -4), (-6, -0.6)], [(13.6, -0.4)], [(16, -4), (16.4, -16), (16, -29)]], closed=False), fill="#ffffff"))
    # scutum on his left arm, face turned toward Jesus
    shield = [[(0.6, -177.8), (12, -181.6), (24, -182.6), (36, -180.4), (43.6, -173)],
              [(43.8, -100), (43.6, -27)],
              [(36, -24.6), (24, -23.6), (12, -25.4), (0.6, -30)],
              [(0.4, -100), (0.6, -177.8)]]
    sd = pb_runs(T, shield)
    o.append(el("line", sd, fill="#ffffff"))
    o.append(el("hatch", sd, fill=RUST, accent=True))
    o.append(el("detail", pb_runs(T, [[(4.4, -173.4), (14, -176.6), (24, -177.4), (34.4, -175.6), (39.8, -169.6)],
                                       [(40, -100), (39.8, -31.4)], [(34, -29), (24, -28), (13, -29.4), (4.4, -33.4)], [(4.2, -100), (4.4, -173.4)]])))
    o.append(el("detail", K.circle(T([(22.4, -101.6)])[0][0], T([(22.4, -101.6)])[0][1], 8.6 * s)))                 # boss
    o.append(el("detail", P(T([(22.4, -110.6), (22.4, -176.6)])) + " " + P(T([(22.4, -92.6), (22.4, -28.4)]))))     # spina (two strokes)
    # manacles: iron cuffs on a short chain, dangling from his fist
    cx1, cy1 = T([(-70.4, -134.6)])[0]
    cx2, cy2 = T([(-54.6, -131.2)])[0]
    o.append(el("detail", S(T([(-61.6, -164.4), (-63.6, -159.4), (-60.8, -155.4), (-63.4, -150.6), (-61, -146.6), (-63.2, -142.6)]))))
    o.append(el("detail", K.circle(cx1, cy1, 7.4 * s, start_deg=-60) + " " + K.circle(cx2, cy2, 7.4 * s, start_deg=-120).replace("M", "L", 1)))
    o.append(el("detail", K.circle(cx1, cy1, 4.2 * s) + " " + K.circle(cx2, cy2, 4.2 * s).replace("M", "L", 1)))
    # mail doubling, belt, apron, gladius
    o.append(el("detail", S(T([(-27, -186), (-17, -180), (-6, -178.6), (6, -180.4), (14, -184), (22, -190)]))))
    o.append(el("detail", S(T([(-36.6, -177), (-32.6, -168)]))))
    o.append(el("detail", S(T([(-26.6, -131.4), (-12, -130), (2, -130.4)])) + " " + S(T([(-27.2, -125.4), (-12, -124), (2, -124.4)]))))
    o.append(el("detail", pb_runs(T, [[(-18.6, -124.4), (-19.4, -97.4)], [(-6.4, -97)], [(-6.6, -124)]], closed=False)))
    o.append(el("detail", pb_runs(T, [[(-23.6, -131.6), (-27.2, -91)], [(-31, -91.6)], [(-27.4, -132)]], closed=False)))
    hz = []
    hz.append(mail_texture(T, [(-25, -195), (-31, -186), (-35, -176), (-28, -170), (-27.6, -152), (-26.4, -134), (2, -132), (2, -178), (-6, -178.6), (-17, -180)]))
    hz.append(mail_texture(T, [(-27, -186), (-17, -200), (-9.6, -203.4), (2, -203), (10, -202.6), (17.4, -200.6), (22, -190), (14, -184), (6, -180.4), (-6, -178.6), (-17, -180)], gap=3.0))
    hz.append(K.S(T([(-14.4, -124), (-14.8, -98)])) + " " + K.S(T([(-10.4, -124), (-10.6, -97.6)])))
    hz.append(" ".join(K.P(T([(xx - 0.6, -118 + k * 6), (xx + 0.6, -118 + k * 6)])) for xx in (-16.6, -12.6, -8.6) for k in range(4)))
    hz.append(K.S(T([(-24, -131), (-23.4, -140), (-22.6, -144)])) + " " + K.S(T([(-26, -131.2), (-25.4, -140)])))
    hz.append(K.S(T([(-63.2, -142.6), (-66.4, -140.4)])) + " " + K.S(T([(-63.2, -142.6), (-59.6, -138.4)])))
    hz.append(hatch(T([(-38.6, -166.4), (-46, -170.8), (-53.8, -174.2), (-53.4, -165.4), (-45.2, -160.8), (-39.6, -151.4)]), 20, 2.2 * s))
    hz.append(K.S(T([(-58.4, -176.4), (-58.8, -167.4)])) + " " + K.S(T([(-62.2, -176.6), (-62.4, -168)])))
    hz.append(hatch(T([(-30.4, -118), (-31.6, -84), (-22, -81.6), (-20, -100), (-26, -118)]), 80, 2.6 * s))
    hz.append(K.S(T([(-14, -119), (-15, -86)])) + " " + K.S(T([(-2, -119), (-1, -84)])))
    hz.append(hatch(T([(-26.6, -12), (-25.2, -24), (-21.4, -50), (-17.6, -70), (-21, -70), (-26, -40), (-30, -14)]), 70, 2.4 * s))
    hz.append(" ".join(K.P(T([(-37 + k * 0.6, -16 + k * 4.2), (-27, -17.2 + k * 4.2)])) for k in range(3)))
    hz.append(" ".join(K.P(T([(4.8, -24 + k * 6), (15.6, -24.8 + k * 6)])) for k in range(3)))
    hz.append(hatch(T([(30, -177), (36, -180.4), (43.6, -173), (43.8, -100), (43.6, -27), (36, -24.6), (30, -26)]), 90, 2.4 * s))
    hz.append(K.S(T([(14.6, -110), (8, -126), (12, -134), (5, -152)])) + " " + K.S(T([(30.2, -93), (37, -78), (33, -70), (40, -52)])))
    hz.append(K.S(T([(13.4, -101.6), (6, -98), (8, -94), (4, -90)])) + " " + K.S(T([(31.4, -101.6), (38, -106), (36, -110), (40, -114)])))
    o.append(el("hatch", " ".join(hz)))
    o.append(ground_shadow(T, -50, 30, 1.4))
    return "".join(o)


def legionary_back(x, y, s):
    """Second soldier, a step behind: pilum upright, scutum, watching."""
    T = mk(x, y, s)
    o = []
    # pilum first (behind him): wooden shaft, lead weight, long iron shank, pyramidal point
    o.append(el("line", pb_runs(T, [[(-34, 2), (-34.4, -170)], [(-36.4, -174), (-34.6, -184), (-32.6, -174)], [(-34.4, -170)],
                                     [(-34.6, -186), (-34.8, -262)], [(-36.4, -264), (-34.8, -276), (-33.2, -264)], [(-34.8, -262)]], closed=False)))
    o.append(soldier_head(T, dx=2))
    body = [
        [(-7.6, -203.4), (-18, -200.4), (-26, -195), (-31.6, -184), (-33.6, -168)],
        [(-36.8, -166.2), (-38.6, -160), (-36, -154.6), (-31.6, -154.4)],                   # hand on the shaft
        [(-29, -150), (-27.6, -134), (-29, -124), (-30.4, -104), (-31.4, -84)],
        [(-22, -82), (-12, -83.4), (-2, -81.4), (8, -83), (16.6, -84)],
        [(16, -110), (19.6, -130), (24.6, -160), (27, -184), (24.6, -194), (17.4, -200.6), (12, -202.6)],
    ]
    o.append(el("line", pb_runs(T, body), fill="#ffffff"))
    o.append(el("line", pb_runs(T, [[(-26.8, -82.6), (-26.6, -60), (-27, -30), (-28, -14)], [(-34, -9.4), (-40.4, -4), (-41.4, -0.6)], [(-20.4, -0.4)],
                                     [(-18.8, -3.6), (-18.6, -14), (-17.4, -40), (-16.6, -70), (-16.4, -82.8)]], closed=False), fill="#ffffff"))
    shield = [[(2.6, -176.8), (14, -180.6), (26, -181.6), (38, -179.4), (45.6, -172)],
              [(45.8, -100), (45.6, -26)],
              [(38, -23.6), (26, -22.6), (14, -24.4), (2.6, -29)],
              [(2.4, -100), (2.6, -176.8)]]
    sd = pb_runs(T, shield)
    o.append(el("line", sd, fill="#ffffff"))
    o.append(el("hatch", sd, fill=RUST, accent=True))
    o.append(el("detail", K.circle(T([(24.4, -100.6)])[0][0], T([(24.4, -100.6)])[0][1], 8.4 * s)))
    o.append(el("detail", S(T([(-26.4, -131.4), (-12, -130), (2, -130.4)]))))
    hz = []
    hz.append(mail_texture(T, [(-25, -195), (-31.6, -184), (-33.6, -168), (-29, -150), (-27.6, -134), (2, -132), (2, -190), (-8, -203), (-18, -200.4)]))
    hz.append(pb_runs(T, [[(6.4, -172.4), (16, -175.6), (26, -176.4), (36.4, -174.6), (41.8, -168.6)], [(42, -100), (41.8, -30.4)],
                           [(36, -28), (26, -27), (15, -28.4), (6.4, -32.4)], [(6.2, -100), (6.4, -172.4)]]))
    hz.append(P(T([(24.4, -110), (24.4, -175.6)])) + " " + P(T([(24.4, -91.6), (24.4, -27.4)])))
    hz.append(hatch(T([(32, -176), (38, -179.4), (45.6, -172), (45.8, -100), (45.6, -26), (38, -23.6), (32, -25)]), 90, 2.4 * s))
    hz.append(K.S(T([(-12, -124), (-13, -98)])) + " " + K.S(T([(-6, -124), (-6.6, -98)])) + " " + K.S(T([(-18, -124), (-18.6, -98)])))
    hz.append(hatch(T([(-30.4, -118), (-31.4, -84), (-22, -82), (-20, -100), (-26, -118)]), 80, 2.6 * s))
    o.append(el("hatch", " ".join(hz)))
    o.append(ground_shadow(T, -48, 34, 1.4))
    return "".join(o)


def antonia_tower():
    """The Antonia fortress tower beyond the soldiers - background, so drawn light: one detail
    contour, everything else self-drawing hatch (drafted Herodian ashlar, window band, gate)."""
    o = []
    x0, x1, top, base = 1432, 1552, 262, 608
    pb = PB().M(x0, base).L(x0, top + 22)
    pb.L(x0 - 5, top + 22).L(x0 - 5, top + 12)
    cx = x0 - 5
    w = (x1 + 5 - cx) / 11
    for k in range(11):
        if k % 2 == 0:
            pb.L(cx, top).L(cx + w, top).L(cx + w, top + 12)
        else:
            pb.L(cx + w, top + 12)
        cx += w
    pb.L(x1 + 5, top + 22).L(x1, top + 22).L(x1, base)
    o.append(el("detail", str(pb), fill="#ffffff"))
    hz = []
    hz.append(P([(x0 - 5, top + 22), (x1 + 5, top + 22)]))
    # window band under the parapet
    for wx in (1452, 1478, 1504, 1530):
        hz.append(P([(wx, top + 58), (wx, top + 40), (wx + 4, top + 35), (wx + 8, top + 40), (wx + 8, top + 58)]))
        hz.append(hatch([(wx + 1, top + 41), (wx + 4, top + 37), (wx + 7, top + 41), (wx + 7, top + 57), (wx + 1, top + 57)], 0, 1.6))
    hz.append(P([(x0, top + 66), (x1, top + 66)]))
    # drafted-margin ashlar courses (Herodian masonry), shaded side denser
    yy, k = top + 82, 0
    while yy < base - 6:
        hz.append(P([(x0 + (10 if k % 2 else 0), yy), (x1, yy)]))
        for xx in ((1466, 1510) if k % 2 else (1488, 1532)):
            hz.append(P([(xx, yy - 22), (xx, yy)]))
        yy += 22
        k += 1
    hz.append(hatch([(1522, top + 68), (x1, top + 68), (x1, base), (1522, base)], 90, 3.4))
    # gate where the path arrives
    hz.append(P([(1474, base), (1474, 560), (1478, 546), (1490, 539), (1502, 546), (1506, 560), (1506, base)]))
    hz.append(hatch([(1476, 562), (1480, 549), (1490, 543), (1500, 549), (1504, 562), (1504, base), (1476, base)], 0, 2.4))
    o.append(el("hatch", " ".join(hz)))
    return "".join(o)


def part_c():
    return antonia_tower() + legionary_back(1292, 668, 0.99) + legionary_front(1156, 690, 1.1)


# ============================================================== part a: Jesus at the fork
JX, JY, JS = 800, 738, 1.0          # Jesus' ground point and scale


def fork_road():
    """A paved path that comes toward us and forks behind Jesus: left toward the crowd (YES),
    right toward the soldiers and the Antonia gate (NO).  Background -> self-drawing hatch."""
    left_near = [(712, 780), (690, 752), (600, 734), (474, 716), (362, 690), (258, 664), (160, 640)]
    far = [(170, 618), (258, 630), (362, 652), (474, 676), (590, 696), (690, 708), (796, 714),
           (920, 704), (1040, 690), (1156, 668), (1292, 650), (1400, 628), (1472, 612)]
    right_near = [(1504, 616), (1420, 642), (1292, 684), (1156, 708), (1040, 722), (940, 738), (900, 756), (888, 780)]
    hz = [S(left_near), S(far), S(right_near)]
    # flagstone joints on the near part of the path, fading with distance
    joints = [[(724, 768), (868, 768)], [(732, 752), (862, 752)], [(612, 744), (676, 748)], [(520, 728), (566, 732)],
              [(940, 724), (1004, 718)], [(1060, 708), (1110, 702)], [(780, 768), (776, 780)], [(828, 752), (832, 768)],
              [(752, 752), (748, 768)], [(640, 734), (636, 746)], [(980, 721), (984, 733)]]
    hz += [P(j) for j in joints]
    return el("hatch", " ".join(hz))


def jesus_figure(level="small"):
    import importlib
    import jesus as J
    importlib.reload(J)
    kw = dict(scale=JS, pose="standing", facing="left")
    try:
        return J.jesus(JX, JY, level=level, **kw)
    except TypeError:
        return J.jesus(JX, JY, **kw)


def part_a(level="small"):
    return fork_road() + jesus_figure(level)


def build(level="small"):
    parts = {"a06-trap-a.svg": (part_a(level), "a06 part a (0.2 s): Jesus stands where the path forks"),
             "a06-trap-b.svg": (part_b(), "a06 part b (2.9 s), under YES: the crowd turns its back and walks away"),
             "a06-trap-c.svg": (part_c(), "a06 part c (5.2 s), under NO: legionaries a short walk away, Antonia tower")}
    for name, (body, note) in parts.items():
        K.write(os.path.join(OUT, name), K.svg(body, note))


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "small")
