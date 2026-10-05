"""a10-whose-image (84.25-92.75 s): "Whose image is this? And whose inscription?" ...
"Then give back to Caesar what is Caesar's, and to God what is God's."

Jesus stands on the right holding the denarius up toward the questioners (off to the left: the
next scene a11 holds on this board and draws them walking away in the left ~35%, so art x < 560
stays empty).  Between him and them the coin itself, shown big - the same tribute penny as the
a08 close-up (shared denarius.py design) - with CAESAR lettered round its edge.

Word zones kept clear: "Whose image?" frame (1141,327) size 96 -> art x 749..1248 y 268..364;
"Give back" frame (1081,674) size 96 -> art x 764..1098 y 636..714.
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import kit_awb as K  # noqa: E402
from kit_awb import S, P, el, hatch, BLUE  # noqa: E402
from lib_v2 import L, D, H, svg, write  # noqa: E402

OUT = os.path.join(HERE, "..", "A")

JX, JY, JS = 1462, 768, 1.4         # Jesus' ground point and scale (coin pose, facing left)
CX, CY, CR = 1196, 506, 80.0        # the magnified coin: centre and die radius (flan ~ CR * 345/330)
RING = 98.0                         # magnifier ring round it


def jesus_part(level="small"):
    import importlib
    import jesus as J
    importlib.reload(J)
    return J.jesus(JX, JY, scale=JS, pose="coin", facing="left", level=level, coin_wash=True)


def coin_anchor():
    import jesus as J
    return J.jesus_anchors(JX, JY, JS, "coin", "left")["coin"]


def big_coin():
    """the tribute penny, obverse, small enough to sit between the two words"""
    import denarius as dn
    import roman_caps as rc
    from inkgeom import path_pts, clip_outside
    C = dn.Coin(CX, CY, CR)
    b = ""
    flan = C.flan_pts()
    b += K.el("line", C.pd(flan, True), fill=BLUE, accent=True, fill_opacity=0.32)
    wr, leaves, ribs = dn.wreath()
    # small object -> the head's contours at detail weight (thinner, and quick for the hand)
    b += D(C.d(dn.PROFILE)) + D(C.d(dn.BACK))
    for run in clip_outside(path_pts(dn.CROWN, 14), leaves, step=1.5, min_len=6):
        b += D(C.pd(run))
    b += D(C.d(dn.EAR))
    b += D(C.pd(wr))
    # legend: CAESAR lettered by hand (the answer they give), the rest self-drawn
    letters = rc.on_arc("TI CAESAR DIVI AVG F AVGVSTVS", C.cx, C.cy, 258 * C.s, 50 * C.s, -147, 147, squeeze=0.86)
    rest = []
    for i, lt in enumerate(letters):
        ds = rc.strokes_to_d([lt])
        if 2 <= i <= 7:
            for d in ds:
                b += D(d)
        else:
            rest += ds
    # self-drawn: rest of the legend, beads, hair, wreath ribs, ties, small features, relief shade
    hz = list(rest)
    hz.append(" ".join(C.pd(r) for r in dn.hair_texture(leaves)))
    hz.append(" ".join(C.pd(r) for r in ribs))
    hz.append(C.pd(dn.fringe()))
    hz += [C.d(dn.EYE), C.d(dn.BROW), C.d(dn.IRIS), C.d(dn.LID), C.d(dn.NOSTRIL), C.d(dn.MOUTH), C.d(dn.EAR_IN)]
    hz += [C.pd(t) for t in dn.ties()]
    hz.append(" ".join(C.pd(s, eps=0) for s in dn.obverse_shading()))
    contour, band = C.edge(flan)
    hz.append(C.pd(contour))
    hz.append(" ".join(C.pd(s, eps=0) for s in dn.hatch(band, 70, 3.2, jitter=0.3, seed=19, min_len=1.5)))
    b += H(" ".join(h for h in hz if h))
    # beaded border: zero-length dashes, self-drawn
    beads = C.beads()
    b += beads.replace('class="detail"', 'class="hatch"').replace("stroke-width:2.4", "stroke-width:2.2")
    return b


def callout():
    """a fine magnifier callout: a small ring round the coin in his fingers, a leader line, and a
    ring round the magnified coin (drawn by hand, thin)"""
    cx, cy, r = coin_anchor()
    rs = r + 7
    dx, dy = cx - CX, cy - CY
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    a = (CX + ux * RING, CY + uy * RING)
    b = (cx - ux * rs, cy - uy * rs)
    o = el("detail", K.circle(cx, cy, rs, start_deg=math.degrees(math.atan2(-uy, -ux))) + " " + P([b, a]).replace("M", "L", 1))
    o += el("detail", K.circle(CX, CY, RING, start_deg=math.degrees(math.atan2(uy, ux))))
    return o


def setting():
    """self-drawing hint of the temple court, right side only: paving under him, the base and
    fluted foot of a colonnade column behind him, the ground line (a11 may continue it)"""
    hz = []
    hz.append(S([(600, 771), (900, 770), (1200, 771), (1600, 769)]))
    # paving joints in perspective, fading to the left
    for k, xx in enumerate((1250, 1330, 1410, 1490, 1570)):
        hz.append(P([(xx, 771), (xx + 26 + 6 * k, 789)]))
    hz.append(P([(1300, 781), (1600, 780)]))
    # column: square plinth, torus, fluted shaft rising behind him (cut by the board edge)
    hz.append(P([(1532, 769), (1532, 746), (1600, 746)]) + " " + P([(1538, 746), (1540, 734), (1600, 734)]))
    hz.append(S([(1540, 734), (1546, 726), (1552, 722), (1600, 722)]))
    for xx in (1556, 1568, 1580, 1592):
        hz.append(P([(xx, 722), (xx, 330)]))
    hz.append(P([(1552, 722), (1552, 330)]))
    hz.append(hatch([(1582, 722), (1600, 722), (1600, 330), (1582, 330)], 90, 3.0))
    # his shadow on the paving
    sh = [(JX - 80 + 160 * k / 18, JY + 4 + 6 * math.sin(math.pi * k / 18)) for k in range(19)]
    hz.append(hatch(sh + [(JX + 80, JY + 1), (JX - 80, JY + 1)], 0, 2.4))
    # a glint on the coin he holds up
    cx, cy, r = coin_anchor()
    for a in (200, 240, 280, 320):
        u = (math.cos(math.radians(a)), math.sin(math.radians(a)))
        hz.append(P([(cx + u[0] * (r + 11), cy + u[1] * (r + 11)), (cx + u[0] * (r + 19), cy + u[1] * (r + 19))]))
    return el("hatch", " ".join(hz))


def body(level="small"):
    return setting() + jesus_part(level) + callout() + big_coin()


if __name__ == "__main__":
    lv = sys.argv[1] if len(sys.argv) > 1 else "small"
    write(os.path.join(OUT, "a10-whose-image.svg"),
          svg(body(lv), "a10 (1.7 s): Jesus holds up the denarius - whose image? - the coin shown big between the words"))
