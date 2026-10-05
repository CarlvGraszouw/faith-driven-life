"""a11-amazed (92.75-97.75 s, camera hold on the a10 board; hand window ~3.4 s).
"The men who had come to trap him were amazed. They left him and went away."
Drawn in the left part of the a10 board (x < ~560; a10 keeps Jesus holding up the coin on the right): the
questioners walk away to the left, out of the scene.  The lead Pharisee, last to go, glances back over his
shoulder, stunned, a hand half-raised; ahead of him the Herodian presses a hand to his brow; the old Pharisee,
furthest ahead, strokes his beard (drawn light, as background).  a10's ground line is continued; a few
motion strokes trail behind them."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a_sketch as K                                   # noqa: E402
import a_people as PP                                   # noqa: E402
import a_questioners as Q                               # noqa: E402
from lib_v2 import svg, write, L, D, H                  # noqa: E402

OUT = os.path.join(HERE, "..", "A", "a11-amazed.svg")
GROUND_Y = 771.0                     # a10's ground line (hatch) starts at x=600 on this line
W1 = (478.0, 772.0, 0.98)            # lead Pharisee glancing back (nearest Jesus)
W2 = (306.0, 768.0, 0.94)            # Herodian, hand to his brow
W3 = (138.0, 763.0, 0.9)             # old Pharisee, furthest ahead (background)


def demote(lay, max_len=260.0, short=72.0):
    keep = []
    for el in lay["line"]:
        d = el.split(' d="')[1]; d = d[:d.rindex('"')]
        Ln = K.length(d)
        if ('fill="#ffffff"' in el and Ln < max_len) or Ln < short:
            lay["detail"].insert(0, el.replace('class="line"', 'class="detail"'))
            continue
        keep.append(el)
    lay["line"] = keep


def soften(lay, neck_y):
    keep = []
    for el in lay["detail"]:
        d = el.split(' d="')[1]; d = d[:d.rindex('"')]
        ys = [p[1] for pl in K.flatten(d, 2.0) for p in pl]
        if 'fill="#ffffff"' in el or (ys and max(ys) < neck_y):
            keep.append(el)
        else:
            lay["hatch"].append(el.replace('class="detail"', 'class="hatch"'))
    lay["detail"] = keep


def ghost(lay):
    out = []
    for el in lay["line"] + lay["detail"] + lay["hatch"]:
        el = re.sub(r' fill(-opacity|-rule)?="[^"]*"', '', el)
        out.append(el.replace('class="line"', 'class="hatch"').replace('class="detail"', 'class="hatch"'))
    lay["line"], lay["detail"], lay["hatch"] = [], [], out


def clip_lay(lay, sils):
    for cls in ("line", "detail", "hatch"):
        out = []
        for el in lay[cls]:
            head, d = el.split(' d="'); d = d[:d.rindex('"')]
            if 'fill="#ffffff"' in head:
                out.append(el); continue
            dd = K.clip(d, sils, keep="out")
            if dd:
                out.append(head + ' d="' + dd + '"/>\n')
        lay[cls] = out


def build(levels=("mid", "small")):
    f1, _ = Q.pharisee_walk_back()
    f2, _ = Q.herodian_walk()
    f3, _ = Q.pharisee_old_walk()
    l1 = f1.render(W1[2], W1[0], W1[1], False, levels[0])
    l2 = f2.render(W2[2], W2[0], W2[1], False, levels[1])
    l3 = f3.render(W3[2], W3[0], W3[1], False, "mid")
    s1 = PP.silhouette(f1, W1[2], W1[0], W1[1], False)
    s2 = PP.silhouette(f2, W2[2], W2[0], W2[1], False)
    s3 = PP.silhouette(f3, W3[2], W3[0], W3[1], False)
    clip_lay(l2, s1)
    clip_lay(l3, s1 + s2)
    demote(l1); demote(l2)
    soften(l1, W1[1] - 282 * W1[2])
    ghost(l3)
    sils = s1 + s2 + s3
    hat = []
    # ground continuing a10's line, a little paving
    hat.append(K.seg((28, GROUND_Y + 1.4), (300, GROUND_Y + 0.8), (600, GROUND_Y)))
    for k in range(5):
        px = 80 + k * 110
        hat.append(K.clip(K.seg((px, GROUND_Y + 1), (px - 10, GROUND_Y + 8.6)), sils))
    hat.append(K.seg((60, GROUND_Y + 8.6), (560, GROUND_Y + 8)))
    # motion strokes trailing behind the walkers (to the right of each, low)
    for (x, y, s) in (W1, W2, W3):
        for k, (dy, l) in enumerate(((-26, 34), (-14, 46), (-2, 30))):
            x0 = x + 58 * s + k * 4
            hat.append(K.sm([(x0, y + dy * s), (x0 + l * 0.5 * s, y + dy * s - 1.5), (x0 + l * s, y + dy * s)]))
        hat.append(K.hatch([(x - 76 * s, y + 3), (x + 50 * s, y + 3), (x + 40 * s, y + 9), (x - 66 * s, y + 9)], angle=0,
                           spacing=2.4, seed=int(x)))
    body = ""
    body += "".join(l1["line"] + l1["detail"])
    body += "".join(l2["line"] + l2["detail"])
    body += "".join(l1["hatch"] + l2["hatch"] + l3["hatch"])
    body += "".join(H(h) for h in hat if h)
    return svg(body, "a11 amazed (drawn on the a10 board, left part x<560): the questioners walk away; the lead "
                     "Pharisee glances back, stunned")


if __name__ == "__main__":
    write(OUT, build())
