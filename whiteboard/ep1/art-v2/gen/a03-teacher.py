"""a03-teacher (21.78-26.28 s, camera zoom 1.5x toward the right; hand window ~2.9 s).
"A teacher from Galilee named Jesus is sitting among them, and people have gathered to listen."
Jesus sits on the lowest step of the Royal Stoa, right of centre, teaching with an open hand; a veiled woman on
the step beside him and a hooded man on the ground (seen from behind, in front of us) listen.  The left ~40% of
the board stays empty: a04 (camera hold) draws the questioners there on the same board.
Lean hand strokes; the setting (colonnade, stylobate, paving) and all shading are hatch (self-drawn)."""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a_sketch as K                                   # noqa: E402
from jesus import jesus_layers, jesus_anchors          # noqa: E402
import a_people as PP                                   # noqa: E402
from a_layout import *                                  # noqa: E402,F401
from lib_v2 import svg, write, L, D, H                  # noqa: E402

OUT = os.path.join(HERE, "..", "A", "a03-teacher.svg")


def demote(lay, max_len=260.0, short=72.0):
    """move short filled line paths (hands, feet) and short contours to the detail pen."""
    keep = []
    for el in lay["line"]:
        d = el.split(' d="')[1].rstrip('"/>\n')
        Ln = K.length(d)
        if ('fill="#ffffff"' in el and Ln < max_len) or Ln < short:
            lay["detail"].insert(0, el.replace('class="line"', 'class="detail"'))
            continue
        keep.append(el)
    lay["line"] = keep


def soften(lay, neck_y):
    """secondary figure: keep silhouette lines, face details (above the neck) and filled hands as hand strokes;
    body interior lines become self-drawn hatch."""
    keep = []
    for el in lay["detail"]:
        d = el.split(' d="')[1]; d = d[:d.rindex('"')]
        pls = K.flatten(d, 2.0)
        ys = [p[1] for pl in pls for p in pl]
        if 'fill="#ffffff"' in el or (ys and max(ys) < neck_y):
            keep.append(el)
        else:
            lay["hatch"].append(el.replace('class="detail"', 'class="hatch"'))
    lay["detail"] = keep


def ghost(lay):
    """background figure: everything self-drawn as light hatch (no hand time); fills dropped."""
    import re as _re
    allp = lay["line"] + lay["detail"] + lay["hatch"]
    out = []
    for el in allp:
        el = _re.sub(r' fill="[^"]*"', '', el)
        el = _re.sub(r' fill-opacity="[^"]*"', '', el)
        el = _re.sub(r' fill-rule="[^"]*"', '', el)
        el = el.replace('class="line"', 'class="hatch"').replace('class="detail"', 'class="hatch"')
        out.append(el)
    lay["line"], lay["detail"], lay["hatch"] = [], [], out


def clipout(d, sils):
    return K.clip(d, sils, keep="out") if d else ""


def build():
    rnd = random.Random(3)
    # ------------------------------------------------------------ figures
    lay_j = jesus_layers(JX, JY, JS, "seated", "left", level="small")
    sil_j = jesus_anchors(JX, JY, JS, "seated", "left")["silhouette"]
    wx, wy, ws = WOMAN
    fw = PP.listener_woman_standing()
    lay_w = PP.layers(fw, ws, wx, wy, False, "small")
    sil_w = PP.silhouette(fw, ws, wx, wy, False)
    bx, by, bs = ELDER
    fb = PP.listener_elder_staff()
    lay_b = PP.layers(fb, bs, bx, by, False, "small")
    sil_b = PP.silhouette(fb, bs, bx, by, False)
    # the woman stands in front of the elder: clip him by her
    for cls in ("line", "detail", "hatch"):
        out = []
        for el in lay_b[cls]:
            head, d = el.split(' d="'); d = d[:d.rindex('"')]
            dd = K.clip(d, sil_w, keep="out")
            if dd:
                out.append(head + ' d="' + dd + '"/>\n')
        lay_b[cls] = out
    sils = [sil_j] + sil_w + sil_b

    # ------------------------------------------------------------ the step he sits on (hand-drawn, lean)
    top, x0, x1 = STEP_TOP, STEP_X0, 1612.0
    jit = lambda: rnd.uniform(-0.7, 0.7)
    step_front = K.sm([(x1, top + 1)] + [(x, top + jit()) for x in range(int(x1) - 40, int(x0) + 10, -60)]
                      + [(x0 + 5, top + 0.4), (x0, top + 4.6), (x0 - 0.6, top + 30), (x0 + 0.6, FLOOR_Y - 20), (x0, FLOOR_Y)])
    step_line = clipout(step_front, sils)
    step_det = clipout(K.sm([(x0 + 4, top + 3.4)] + [(x, top + 3.6 + jit() * 0.6) for x in range(int(x0) + 60, int(x1), 70)]), sils)
    step_det += " " + clipout(K.sm([(x0, top + 4.6), (x0 + 9, top - 6.6), (STEP2_X0 - 4, top - 7.6)]), sils)

    # ------------------------------------------------------------ hatch: setting
    hat = []
    # upper step (stylobate) and its edge, behind the figures
    s2 = K.seg((STEP2_X0, STEP2_TOP), (1612, STEP2_TOP)) + " " + K.seg((STEP2_X0, STEP2_TOP), (STEP2_X0, top - 8))
    s2 += " " + K.seg((STEP2_X0 + 6, STEP2_TOP - 7), (1612, STEP2_TOP - 7)) + " " + K.seg((STEP2_X0, STEP2_TOP), (STEP2_X0 + 6, STEP2_TOP - 7))
    hat.append(clipout(s2, sils))
    hat.append(clipout(K.hatch([(STEP2_X0 + 2, STEP2_TOP + 2), (1612, STEP2_TOP + 2), (1612, top - 9), (STEP2_X0 + 2, top - 9)],
                               angle=0, spacing=6.0, seed=301), sils))
    # columns of the Royal Stoa (base, fluted shaft, Corinthian capital)
    import a_arch
    for cx in COLS:
        lines, shade = a_arch.corinthian_column(cx, STEP2_TOP - 7, COL_TOP, COL_W)
        hat.append(clipout(lines, sils))
        hat.append(clipout(shade, sils))
    # architrave/roof line of the stoa above the columns (right of the text band)
    hat.append(clipout(K.seg((1226, COL_TOP - 6), (1612, COL_TOP - 6)) + " " + K.seg((1226, COL_TOP - 22), (1612, COL_TOP - 22))
                       + " " + K.seg((1226, COL_TOP - 30), (1612, COL_TOP - 30)), sils))
    hat.append(K.hatch([(1226, COL_TOP - 22), (1612, COL_TOP - 22), (1612, COL_TOP - 6), (1226, COL_TOP - 6)], angle=90,
                       spacing=7.0, seed=302))
    # shaded front of the lowest step, joints, and the paving in front
    hat.append(clipout(K.hatch([(x0 + 2, top + 8), (1612, top + 8), (1612, FLOOR_Y - 2), (x0 + 2, FLOOR_Y - 2)], angle=-80,
                               spacing=3.4, seed=303, every=lambda k: k % 3 != 1), sils))
    joints = " ".join(K.seg((jx, top + 6), (jx + 1, FLOOR_Y - 3)) for jx in (1188, 1402, 1560))
    hat.append(clipout(joints, sils))
    pav = []
    for k, yy in enumerate((FLOOR_Y + 1, FLOOR_Y + 22, FLOOR_Y + 48)):
        pav.append(K.seg((690 + k * 12, yy), (1612, yy)))
    for k in range(9):
        px = 820 + k * 92
        pav.append(K.seg((px, FLOOR_Y + 1), (px - 28 - k * 3, FLOOR_Y + 60)))
    hat.append(clipout(" ".join(pav), sils))
    # ground shadows
    hat.append(K.hatch([(x0 - 30, FLOOR_Y + 3), (x0 + 150, FLOOR_Y + 3), (x0 + 120, FLOOR_Y + 10), (x0 - 20, FLOOR_Y + 10)],
                       angle=0, spacing=2.4, seed=304))

    # budget: small closed shapes (hands, feet) are drawn with the finer detail pen (quick hops)
    demote(lay_j); demote(lay_w); demote(lay_b)
    soften(lay_w, WOMAN[1] - 262 * WOMAN[2])
    ghost(lay_b)
    body = ""
    body += "".join(lay_j["line"] + lay_j["detail"])
    body += "".join(lay_w["line"] + lay_w["detail"])
    body += "".join(lay_b["line"] + lay_b["detail"])
    body += "".join(lay_j["hatch"] + lay_w["hatch"] + lay_b["hatch"])
    body += H(step_line) + H(step_det)          # the step is setting: self-drawn with the background
    body += "".join(H(h) for h in hat if h)
    return svg(body, "a03 teacher: Jesus seated on the stoa step, teaching; two listeners. Left 40% left empty for a04.")


if __name__ == "__main__":
    write(OUT, build())
