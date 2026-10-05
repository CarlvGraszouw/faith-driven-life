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
        [(30.6, 50.4), (27.4, 41), (27, 32.6), (29.4, 25.6), (33.8, 20.4)],                 # throat
        [(39.4, 17.4), (42.8, 13.2)],                                                        # chin
        [(41.6, 9.6)], [(43.6, 6.6)],                                                         # dimple, lower lip
        [(41.8, 4.4)], [(44.4, 2.6)],                                                         # mouth, upper lip
        [(43.6, -0.8), (45, -3.2)],                                                          # philtrum
        [(50.2, -6.6)],                                                                      # nose tip
        [(46.4, -15), (44.2, -24), (43.6, -28.4)],                                           # bridge, root
        [(44.8, -32.6), (43.8, -40.4), (40.6, -48.2), (35.4, -54.6)],                         # brow, forehead
        [(24, -62.4), (8, -67.4), (-10, -66.6), (-26.4, -60.4), (-38.4, -49), (-45.4, -35)],   # hair over the crown
        [(-49.4, -30.4), (-58.6, -24.4), (-63.4, -12.6), (-60.8, -0.8), (-52.2, 5.2), (-43.6, 3.2)],  # the knot
        [(-41.2, 10.4), (-35.6, 18.6), (-31.8, 32), (-32, 44)],                              # nape, neck back
        [(-38, 50), (-45.6, 58.6), (-49.4, 70.4)],                                            # shoulder, drape
        [(-30, 75.4), (-8, 77.4), (14, 75.6), (34, 70.4), (46.6, 63)],                        # bust truncation
        [(41, 56.4), (34.6, 52.6), (30.6, 50.4)],                                            # neckline front
    ]
    o.append(el("line", runs_d(prof)))
    # garment: neckline and the fold of the drape over the shoulder
    o.append(el("detail", runs_d([[(-32, 44), (-16, 47), (2, 50), (18, 52.4), (30.6, 50.4)]])))
    o.append(el("detail", runs_d([[(-41, 52), (-30, 60), (-14, 66.6), (6, 68.4)]])))
    # face: lifted eye (lids, iris), brow, nostril, smiling mouth corner, jaw; ear under the hair
    o.append(el("detail", runs_d([[(31.4, -27.6), (35.2, -31), (39.6, -31.6), (42.2, -29.4)],
                                   [(39.6, -26.4), (35, -25.8), (31.4, -27.6)]])))
    o.append(el("detail", runs_d([[(29.6, -36.2), (35.6, -38.6), (41.6, -36.8)]])))
    o.append(el("detail", runs_d([[(44.6, -3.6), (41.4, -3.2), (40.4, -6), (42.2, -8.6)]])))
    o.append(el("detail", runs_d([[(41.8, 4.4), (39.4, 4.2), (38.2, 2.6)]])))
    o.append(el("detail", runs_d([[(8.6, -8), (11.6, -1.6), (11.6, 4.6), (8.6, 8.2), (5.2, 7)]])))   # ear lobe
    o.append(el("detail", runs_d([[(35.4, -54.6), (25, -46), (17.6, -34), (11, -20), (7.6, -10)]])))   # hairline
    o.append(el("detail", runs_d([[(-45.4, -35), (-42, -22), (-37.6, -10), (-40.6, 2)]])))           # the knot's tie
    hz = []
    # hair swept back from the face into the knot (strands following the form)
    for kk in range(11):
        t = kk / 10.0
        a = (32 - 40 * t, -57 + 6 * t)
        hz.append(K.S(U([a, (a[0] - 16, a[1] + 4 + 6 * t), (a[0] - 30 + 8 * t, a[1] + 14 + 10 * t), (-42 + 3 * t, -30 + 18 * t)])))
    for kk in range(7):
        t = kk / 6.0
        hz.append(K.S(U([(-46 - 8 * t, -26 + 3 * t), (-56 + 2 * t, -18 + 6 * t), (-55 + 6 * t, -4 + 4 * t), (-47 + 4 * t, 2)])))
    hz.append(K.S(U([(10, -16), (4, -4), (2, 10), (5, 24)])) + " " + K.S(U([(14, -24), (9, -12), (8, 0)])))   # loose strands
    hz.append(K.S(U([(38.8, -31), (38.2, -26.8)])))                                                     # iris, looking up
    hz.append(" ".join(K.P(U([(32.6 + 2.6 * kk, -30.6 - 0.6 * kk), (31.8 + 2.8 * kk, -33.4 - 0.5 * kk)])) for kk in range(4)))
    hz.append(K.S(U([(34.6, -13), (30, -6), (31.6, 2)])))                                               # cheek
    hz.append(K.S(U([(12, 10), (22, 16.6), (34, 19.4)])))                                               # jaw
    # relief shading: under the jaw, down the neck, the knot's underside, drapery folds
    hz.append(hatch(U([(14, 18), (29.4, 25.6), (27, 32.6), (27.4, 41), (30.6, 50.4), (18, 52.4), (14, 36)]), 66, 2.4 * R / 100))
    hz.append(hatch(U([(-31.8, 32), (-32, 44), (-16, 47), (-15, 36), (-22, 24), (-35.6, 18.6)]), 66, 2.4 * R / 100))
    hz.append(hatch(U([(-60.8, -0.8), (-52.2, 5.2), (-43.6, 3.2), (-41.2, 10.4), (-50, 12), (-58, 8)]), 30, 2.0 * R / 100))
    hz.append(K.S(U([(-26, 54), (-14, 60), (2, 62.6)])) + " " + K.S(U([(-36, 60), (-24, 68), (-6, 72.4)])) + " " + K.S(U([(20, 58), (28, 62), (36, 66.4)])))
    # cast shadow of the relief on the field, lower right of the profile
    sh = U([(43.6, 6.6), (42.8, 13.2), (39.4, 17.4), (33.8, 20.4), (29.4, 25.6), (27, 32.6), (27.4, 41), (30.6, 50.4), (34.6, 52.6),
            (41, 56.4), (46.6, 63), (50.6, 62), (45.6, 54), (37.6, 49), (33.6, 41), (33.4, 32), (36.6, 25.6), (42.6, 20.6), (46.6, 14), (47.4, 8)])
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


def body():
    c, flan = coin()
    return c + portrait() + rim_and_legend(flan) + light()


if __name__ == "__main__":
    write(os.path.join(OUT, "b02-whose-face.svg"),
          svg(body(), "b02 (2.8 s): a silver coin whose portrait is an ordinary person - IMAGO DEI"))
