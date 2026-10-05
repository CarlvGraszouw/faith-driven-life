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


def strand_band(edge_a, edge_b, n, bend=0.0):
    """hair strands between two guide runs (portrait units) - combed lines following the form"""
    A = sample(edge_a, closed=False, n=6)
    B = sample(edge_b, closed=False, n=6)
    m = min(len(A), len(B))
    A = [A[int(i * (len(A) - 1) / (m - 1))] for i in range(m)]
    B = [B[int(i * (len(B) - 1) / (m - 1))] for i in range(m)]
    out = []
    for k in range(n):
        u = (k + 0.5) / n
        row = [K.lerp(A[i], B[i], u) for i in range(m)]
        # taper: start a little late and stop a little early, alternating
        s0 = 1 + (k % 3)
        s1 = m - 1 - ((k + 1) % 3)
        row = row[s0:s1]
        if len(row) > 2:
            out.append(K.S(U(row)))
    return out


def portrait():
    """an ordinary modern woman in profile facing right, hair tied back in a ponytail, ear
    showing with a small stud, calm level gaze; crew-neck top; bust truncated like a coin."""
    o = []
    prof = [
        [(29.6, 52), (27.6, 44), (27.2, 36), (28.6, 28.4), (31.4, 23)],                      # throat
        [(36.4, 21.4), (41.4, 18.4), (43.6, 12.8)],                                           # under the chin, chin
        [(42.4, 8.4)], [(45.2, 5.4)],                                                          # chin dent, lower lip
        [(43.8, 2.8)], [(45.8, 0.8)],                                                          # mouth, upper lip
        [(44.4, -2.2), (44.8, -4.6), (46.6, -5.8)],                                           # philtrum
        [(50, -8.6)],                                                                          # nose tip
        [(46.6, -14.6), (44.2, -22.6), (42, -26.8)],                                          # bridge, root
        [(42.8, -30), (42.6, -36), (39.4, -44.6), (34.2, -51)],                                # brow, forehead
        [(22, -61.6), (4, -66.8), (-16, -64.6), (-31, -56)],                                   # hair over the crown
        [(-40.6, -39.6)],                                                                      # the hair tie
        [(-49.6, -33.8), (-56.2, -21.6), (-57.6, -5), (-54.4, 12.6), (-47.6, 27.4)],           # ponytail
        [(-41.6, 37.6)],                                                                       # its tip
        [(-41.2, 24.6), (-43.6, 8.6), (-42.4, -8.6), (-38.6, -20.6)],                          # its inner edge
        [(-34.8, -6.6), (-28.6, 8), (-22.4, 22), (-19.6, 34), (-19.4, 46)],                    # nape, neck back
        [(-30, 52.6), (-44.6, 59), (-51, 72)],                                                 # shoulder
        [(-28, 76.4), (-4, 78.2), (20, 76.4), (40, 70.6), (48.6, 63.8)],                       # bust truncation
        [(42.6, 57.6), (35.6, 53.8), (29.6, 52)],                                              # shoulder front
    ]
    o.append(el("line", runs_d(prof)))
    # crew neckline of a plain modern top, and its shoulder seam
    o.append(el("detail", runs_d([[(-19.4, 46), (-6, 50.6), (8, 53.6), (20, 54), (29.6, 52)]])))
    # eye: upper lid with its crease, lower lid; brow; nostril; mouth; ear; hairline; tie
    o.append(el("detail", runs_d([[(29.4, -20.4), (33.6, -24.6), (38.6, -25.2), (41.6, -22)],
                                   [(39, -18.8), (34, -18.4), (29.4, -20.4)]])))
    o.append(el("detail", runs_d([[(29, -29.8), (34.8, -32.4), (41.4, -30.8)]])))
    o.append(el("detail", runs_d([[(46.4, -5.8), (43.2, -5.2), (42.2, -8.2), (44, -10.8)]])))
    o.append(el("detail", runs_d([[(43.8, 2.8), (41.2, 3), (39.8, 1.8)]])))
    o.append(el("detail", runs_d([[(12.8, -11.6), (12.6, -20), (10, -25.4), (5.4, -26.2), (2.4, -21.4), (2, -13), (4, -5.4), (7.6, -1.4), (11, -2.6)]])))
    o.append(el("detail", runs_d([[(34.2, -51), (27.4, -46), (21.6, -38.6), (18, -31.6)]])))
    o.append(el("detail", runs_d([[(-38.6, -44.4), (-42.6, -38.6), (-41.4, -33), (-37, -31.2)]])))
    hz = []
    # hair combed back to the tie in strand groups (light on top, closer on the shaded side)
    hz += strand_band([(34.2, -51), (24, -59.4), (6, -64.4), (-14, -62.6), (-30, -54), (-39, -42)],
                      [(30, -46), (18, -50), (2, -52), (-14, -50), (-28, -46), (-38, -40)], 5)
    hz += strand_band([(26.4, -45.4), (14, -48), (-2, -48.6), (-18, -46), (-30, -42), (-38.6, -38.6)],
                      [(15.8, -28.6), (8, -32.6), (-4, -34), (-18, -34.6), (-30, -36.6), (-38.6, -36)], 7)
    hz += strand_band([(2, -27.4), (-8, -30.4), (-20, -32.6), (-30, -34.2), (-38.6, -36)],
                      [(-3, -9), (-13, -3), (-25, -7), (-33.4, -19), (-38.6, -33)], 6)
    # the ponytail: long S-strands from the tie
    hz += strand_band([(-44, -36), (-51.6, -26), (-54.6, -10), (-52.6, 8), (-46.8, 24), (-42.4, 34)],
                      [(-40.4, -34), (-41.4, -20), (-42.6, -6), (-42.6, 10), (-41.6, 22), (-42, 32)], 6)
    hz.append(K.S(U([(16.4, -40), (12, -33), (11.4, -24)])) + " " + K.S(U([(19, -42.6), (16.6, -36), (17.6, -29.4)])))  # flyaways
    # eye detail: lashes, iris, lid crease; ear inner fold and the stud
    hz.append(" ".join(K.P(U([(32.2 + 2.4 * kk, -24.2 - 0.5 * kk), (31.8 + 2.8 * kk, -27 - 0.4 * kk)])) for kk in range(4)))
    hz.append(K.S(U([(39.6, -24.4), (38, -21.6), (39, -19)])) + " " + K.S(U([(31.6, -26.6), (36.4, -28), (40.4, -26.4)])))
    hz.append(K.S(U([(18, -31.6), (15.6, -26.6), (14, -22.6)])))
    hz.append(K.S(U([(9.4, -21.4), (6.6, -16.6), (7.6, -9.6), (10, -7)])) + " " + K.S(U([(10.6, -15), (9, -12.4)])))
    hz.append(K.circle(*U([(9.2, -0.6)])[0], 1.5 * R / 100))
    # soft modelling: cheek, jaw, under the chin, the neck, behind the ear, the ponytail's shade
    hz.append(K.S(U([(24, 15), (29, 18), (34, 19.8)])))
    hz.append(hatch(U([(18, 18), (31.4, 23), (28.6, 28.4), (27.2, 36), (27.6, 44), (29.6, 52), (18, 54), (14, 36)]), 64, 2.3 * R / 100))
    hz.append(hatch(U([(-19.6, 34), (-19.4, 46), (-6, 50.6), (-5, 36), (-11, 22), (-22.4, 22)]), 64, 2.3 * R / 100))
    hz.append(hatch(U([(-41.2, 24.6), (-43.6, 8.6), (-42.4, -8.6), (-46.4, -6), (-48.6, 10), (-46, 26)]), 80, 2.0 * R / 100))
    hz.append(hatch(U([(2, -13), (4, -5.4), (7.6, -1.4), (0, 2), (-4, -8)]), 60, 1.8 * R / 100))
    hz.append(K.S(U([(-20, 56), (-6, 62), (12, 63.6)])) + " " + K.S(U([(-34, 62), (-18, 70), (2, 73.4)])) + " " + K.S(U([(24, 60), (34, 64), (42, 68)])))
    # cast shadow of the relief on the field (lower right of the profile)
    sh = U([(45.2, 5.4), (43.6, 12.8), (41.4, 18.4), (36.4, 21.4), (31.4, 23), (28.6, 28.4), (27.2, 36), (27.6, 44), (29.6, 52), (35.6, 53.8),
            (42.6, 57.6), (48.6, 63.8), (52.6, 62.4), (46.4, 54.4), (37.6, 49.2), (33.4, 41), (33.4, 32), (36.6, 26.6), (43, 22), (47.4, 14.8), (48.2, 8.4)])
    hz.append(hatch(sh, -40, 2.1 * R / 100))
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
