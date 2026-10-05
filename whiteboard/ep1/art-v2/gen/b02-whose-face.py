"""b02-whose-face (104.25-114.9 s, pan down): "Whose face do you carry? ... 'So God created
mankind in his own image; in the image of God he created them.'"

The turn from coin to person: a large silver coin struck like the denarius - beaded border,
legend in the same Roman capitals - but the portrait on it is an ordinary woman in quiet
reflection, face lifted a little toward the light.  The legend reads IMAGO DEI ("image of
God"); the on-screen words "in the image of God" are written beside her.

Word zones kept clear: "Whose face do you carry?" frame (960,190) size 104 -> art x 326..1293
y 118..226; "in the image of God" frame (1381,535) size 72 -> art x 993..1500 y 506..576.
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import kit_awb as K  # noqa: E402
from kit_awb import PB, S, P, el, hatch, sample, BLUE  # noqa: E402
from lib_v2 import L, D, H, svg, write  # noqa: E402

OUT = os.path.join(HERE, "..", "B")
CX, CY, R = 618, 520, 246.0          # coin centre and flan radius (art units)


def U(pts, s=None, dx=None, dy=None):
    """portrait units: coin of radius 100 centred at 0,0 -> art"""
    k = R / 100.0
    return [(CX + x * k, CY + y * k) for (x, y) in pts]


def runs_d(runs, closed=False):
    pb = PB()
    first = U(runs[0])
    pb.M(first[0]).S(first[1:])
    for r in runs[1:]:
        pb.S(U(r))
    if closed:
        pb.Z()
    return str(pb)


def coin():
    o = []
    # flan: hand-struck silver, slightly irregular, light silver wash
    flan = U([(0, -100), (70.5, -71), (100, -1), (71, 70.4), (0.6, 99.6), (-70.4, 70.8), (-99.6, 0.4), (-71, -70.2)])
    o.append(el("line", S(flan, closed=True), fill=BLUE, accent=True, fill_opacity=0.28))
    return "".join(o), flan


def portrait():
    """an ordinary woman in profile facing right: hair swept back into a low knot, a few loose
    strands, gaze lifted; a draped bust truncated like a coin portrait."""
    o = []
    prof = [
        [(28.6, 50.4), (26.4, 42), (26.6, 33.6), (29.4, 26), (33.8, 20.4)],                 # throat
        [(39.4, 17.4), (42.8, 13.2)],                                                        # chin
        [(41.6, 9.6)], [(43.6, 6.6)],                                                         # dimple, lower lip
        [(41.8, 4.4)], [(44.4, 2.6)],                                                         # mouth, upper lip
        [(43.6, -0.8), (45, -3.2)],                                                          # philtrum
        [(50.2, -6.6)],                                                                      # nose tip
        [(46.4, -15), (44.2, -24), (43.6, -28.4)],                                           # bridge, root
        [(44.8, -32.6), (43.8, -40.4), (40.6, -48.2), (35.4, -54.6)],                         # brow, forehead
        [(24, -62.4), (8, -66.6), (-8, -65.4), (-22, -59.4), (-32.4, -48.6), (-37.6, -35)],   # hair over the crown
        [(-41.4, -31.4), (-50.6, -27), (-55, -16.6), (-52.8, -5.8), (-45.4, -0.4), (-37.8, -2.2)],  # the knot
        [(-34.4, 6.6), (-28.6, 16), (-23.8, 30), (-22.8, 44)],                               # nape, neck back
        [(-28.6, 50.6), (-36.6, 58.6), (-40.4, 70.4)],                                        # shoulder, drape
        [(-22, 75.4), (-2, 77.4), (18, 75.6), (34, 70.6), (44.6, 63.4)],                      # bust truncation
        [(39.4, 56.6), (33.4, 52.8), (28.6, 50.4)],                                          # neckline front
    ]
    o.append(el("line", runs_d(prof)))
    # garment: neckline and the fold of the drape over the shoulder
    o.append(el("detail", runs_d([[(-22.8, 44), (-8, 47), (8, 50), (20, 52.4), (28.6, 50.4)]])))
    o.append(el("detail", runs_d([[(-33, 52), (-22, 60), (-6, 66.6), (12, 68.4)]])))
    # face: lifted eye (lids, iris), brow, nostril, smiling mouth corner, jaw; ear under the hair
    o.append(el("detail", runs_d([[(31.4, -27.6), (35.2, -31), (39.6, -31.6), (42.2, -29.4)],
                                   [(39.6, -26.4), (35, -25.8), (31.4, -27.6)]])))
    o.append(el("detail", runs_d([[(29.6, -36.2), (35.6, -38.6), (41.6, -36.8)]])))
    o.append(el("detail", runs_d([[(44.6, -3.6), (41.4, -3.2), (40.4, -6), (42.2, -8.6)]])))
    o.append(el("detail", runs_d([[(41.8, 4.4), (39.4, 4.2), (38.2, 2.6)]])))
    o.append(el("detail", runs_d([[(9.6, -17), (12.8, -11), (12.2, -4), (9.2, -0.6), (6, -1.8)]])))   # ear lobe
    o.append(el("detail", runs_d([[(35.4, -54.6), (26, -46), (19, -34), (14, -23), (10.6, -16.6)]])))   # hairline
    o.append(el("detail", runs_d([[(-37.6, -35), (-34.6, -22), (-31, -10), (-33.4, 1)]])))           # the knot's tie
    hz = []
    # hair swept back from the face into the knot (strands following the form)
    hl = sample(U([(35.4, -54.6), (26, -46), (19, -34), (14, -23), (10.6, -16.6)]), closed=False, n=4)
    crown = sample(U([(28, -60), (10, -64.6), (-8, -63.4), (-22, -57.4), (-32, -46)]), closed=False, n=4)
    knot = U([(-37, -33), (-35.6, -27), (-34, -21), (-32.6, -15), (-31.4, -9)])
    for kk in range(12):
        t = kk / 11.0
        a = crown[min(len(crown) - 1, int(t * 0.55 * (len(crown) - 1)))] if t < 0.35 else hl[min(len(hl) - 1, int((t - 0.35) / 0.65 * (len(hl) - 1)))]
        b = knot[min(4, int(t * 5))]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - (6 - 8 * t) * R / 100)
        hz.append(K.S([a, m, b]))
    for kk in range(7):
        t = kk / 6.0
        hz.append(K.S(U([(-40 - 7 * t, -26 + 3 * t), (-50 + 2 * t, -18 + 6 * t), (-49 + 5 * t, -5 + 4 * t), (-42 + 3 * t, 0)])))
    hz.append(K.S(U([(12, -20), (6, -8), (4, 6), (6, 18)])) + " " + K.S(U([(16, -26), (11, -14), (10, -6)])))   # loose strands
    hz.append(K.S(U([(38.8, -31), (38.2, -26.8)])))                                                     # iris, looking up
    hz.append(" ".join(K.P(U([(32.6 + 2.6 * kk, -30.6 - 0.6 * kk), (31.8 + 2.8 * kk, -33.4 - 0.5 * kk)])) for kk in range(4)))
    hz.append(K.S(U([(23, 13.4), (28.6, 16.6), (33.6, 18.6)])))                                         # jaw
    # relief shading: under the jaw, down the neck, the knot's underside, drapery folds
    hz.append(hatch(U([(16, 18), (29.4, 26), (26.6, 33.6), (26.4, 42), (28.6, 50.4), (18, 52.4), (15, 36)]), 66, 2.4 * R / 100))
    hz.append(hatch(U([(-23.8, 30), (-22.8, 44), (-10, 47), (-10, 36), (-16, 24), (-28.6, 16)]), 66, 2.4 * R / 100))
    hz.append(hatch(U([(-52.8, -5.8), (-45.4, -0.4), (-37.8, -2.2), (-34.4, 6.6), (-42, 8), (-50, 4)]), 30, 2.0 * R / 100))
    hz.append(K.S(U([(-20, 54), (-8, 60), (8, 62.6)])) + " " + K.S(U([(-30, 60), (-18, 68), (0, 72.4)])) + " " + K.S(U([(20, 58), (28, 62), (36, 66.4)])))
    # cast shadow of the relief on the field, lower right of the profile
    sh = U([(43.6, 6.6), (42.8, 13.2), (39.4, 17.4), (33.8, 20.4), (29.4, 26), (26.6, 33.6), (26.4, 42), (28.6, 50.4), (33.4, 52.8),
            (39.4, 56.6), (44.6, 63.4), (48.6, 62), (44, 54), (36, 49), (32.4, 41), (32.4, 32), (35.6, 25.6), (42.6, 20.6), (46.6, 14), (47.4, 8)])
    hz.append(hatch(sh, -40, 2.2 * R / 100))
    o.append(el("hatch", " ".join(hz)))
    return "".join(o)


def rim_and_legend(flan):
    """beaded border (dots), IMAGO DEI in the denarius' Roman capitals, edge and shadow: all
    self-drawn"""
    import roman_caps as rc
    o = []
    k = R / 100.0
    # beads: zero-length dashes with round caps
    circ = K.circle(CX, CY, 90.5 * k)
    o.append(f'  <path class="hatch" style="stroke-width:3.2;stroke-dasharray:0 9.4;opacity:.9" d="{circ}"/>\n')
    letters = rc.on_arc("IMAGO DEI", CX, CY, 74.5 * k, 12.5 * k, -58, 58, squeeze=0.9)
    o.append("".join(el("detail", d) for d in rc.strokes_to_d(letters)))
    # flan thickness on the shadow side and a soft shadow on the board
    edge = U([(97, 26), (90, 46), (75, 66), (55, 82), (30, 94), (4, 101), (-22, 99), (-44, 91)])
    o.append(el("hatch", S(edge)))
    o.append(el("hatch", hatch(sample(edge, closed=False, n=6) + list(reversed(sample(U([(99.6, 4), (93, 36), (71, 70.4), (36, 92), (0.6, 99.6), (-40, 92)]), closed=False, n=6))), 60, 3.2)))
    sh = U([(102, 20), (96, 50), (80, 74), (56, 92), (26, 104), (-6, 108), (-34, 103), (-40, 96), (-6, 101), (30, 95), (60, 80), (84, 56), (99, 22)])
    o.append(el("hatch", hatch(sh, -40, 4.2)))
    return "".join(o)


def light():
    """the coin catching the light: a few short glint ticks off its upper-right rim (self-drawn)"""
    hz = []
    for a in (-62, -48, -34, -20):
        u = (math.cos(math.radians(a)), math.sin(math.radians(a)))
        r0, r1 = R + 14, R + (34 if a in (-48, -34) else 24)
        hz.append(P([(CX + u[0] * r0, CY + u[1] * r0), (CX + u[0] * r1, CY + u[1] * r1)]))
    return el("hatch", " ".join(hz))


def scroll():
    """the first page of the Scriptures: an open scroll under the words "in the image of God"
    (light - the coin is the subject).  Columns of Hebrew-like script are self-drawn."""
    o = []
    x0, x1, y0, y1 = 1060, 1440, 652, 722          # open sheet
    sheet = PB().M(x0, y0 + 2).S([(1180, y0 - 3), (1310, y0 + 1), (x1, y0 - 2)]).L(x1, y1 - 2) \
        .S([(1310, y1 + 2), (1180, y1 - 1), (x0, y1 + 2)]).Z()
    o.append(el("line", str(sheet), fill="#ffffff"))
    # the two rolled ends (wooden rollers with handles)
    for (cx, sgn) in ((x0 - 12, -1), (x1 + 12, 1)):
        roll = PB().M(cx - 13, y0 - 6).S([(cx, y0 - 13), (cx + 13, y0 - 6)]).L(cx + 13, y1 + 6) \
            .S([(cx, y1 + 13), (cx - 13, y1 + 6)]).Z()
        o.append(el("detail", str(roll), fill="#ffffff"))
    hz = [P([(x0 - 12, y0 - 13), (x0 - 12, y0 - 26)]), P([(x0 - 12, y1 + 13), (x0 - 12, y1 + 26)]),
          P([(x1 + 12, y0 - 13), (x1 + 12, y0 - 26)]), P([(x1 + 12, y1 + 13), (x1 + 12, y1 + 26)])]
    for (cx, sgn) in ((x0 - 12, -1), (x1 + 12, 1)):
        hz.append(hatch([(cx - 12, y0 - 5), (cx + 12, y0 - 5), (cx + 12, y1 + 5), (cx - 12, y1 + 5)], 90, 3.6))
    # three columns of script, right to left, the first line of each a little bolder
    for col in range(3):
        cxr = x1 - 22 - col * 122
        for row in range(5):
            yy = y0 + 13 + row * 12
            w = 96 if row < 4 else 58
            pts, xx, k = [], cxr, 0
            while xx > cxr - w:
                pts.append((xx, yy + (-2.6 if k % 3 == 0 else (1.2 if k % 3 == 1 else -0.6))))
                xx -= 3.4
                k += 1
            hz.append(S(pts))
    o.append(el("hatch", " ".join(hz)))
    return "".join(o)


def body():
    c, flan = coin()
    return c + portrait() + rim_and_legend(flan) + light() + scroll()


if __name__ == "__main__":
    write(os.path.join(OUT, "b02-whose-face.svg"),
          svg(body(), "b02 (2.8 s): a silver coin whose portrait is an ordinary person - IMAGO DEI"))
