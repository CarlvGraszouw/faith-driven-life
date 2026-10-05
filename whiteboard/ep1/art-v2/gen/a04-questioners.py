"""a04-questioners (26.28-38.18 s, camera hold on the a03 board; art must finish before "Taxes to Caesar?"
is written at 8.85 s at frame (960,190)).
"A group of men make their way to the front. They call him Teacher ... Is it right to pay taxes to Caesar?"
Drawn in the empty left part of the a03 board: the lead Pharisee leans in toward Jesus with a flattering smile,
one hand on his heart, the other held out palm-up (asking); behind him a Herodian courtier, arms folded, smirks
and watches for the answer; an older Pharisee strokes his beard, skeptical.  Pharisees: turban-cloth,
phylactery, long beard, tasselled mantle; Herodian: cropped curls, trimmed beard, short tunic, cloak and brooch.
Keeps x 400-1200 / y 100-270 clear for the words.  Setting continues in hatch (paving, two stoa columns)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a_sketch as K                                   # noqa: E402
import a_people as PP                                   # noqa: E402
import a_questioners as Q                               # noqa: E402
from a_layout import *                                  # noqa: E402,F401
from lib_v2 import svg, write, L, D, H                  # noqa: E402

OUT = os.path.join(HERE, "..", "A", "a04-questioners.svg")
# placements (x, y = ground point, scale) -- they face right (mirrored)
Q1 = (606.0, 760.0, 1.06)      # lead Pharisee, nearest to Jesus
Q2 = (424.0, 748.0, 1.02)      # Herodian
Q3 = (246.0, 738.0, 1.0)       # old Pharisee


def build(level=("full", "mid", "mid")):
    figs = [(Q.pharisee_asking()[0], Q1, level[0]), (Q.herodian_folded()[0], Q2, level[1]),
            (Q.pharisee_old()[0], Q3, level[2])]
    lays, sils = [], []
    for f, (x, y, s), lv in figs:
        lays.append(f.render(s, x, y, True, lv))
        sils += PP.silhouette(f, s, x, y, True)
    # nearer figures occlude the ones behind: Q1 in front of Q2 in front of Q3
    def occlude(lay, front_sils):
        for cls in ("line", "detail", "hatch"):
            out = []
            for el in lay[cls]:
                head, d = el.split(' d="')
                d = d[:d.rindex('"')]
                if 'fill=' in head and cls != "hatch":
                    out.append(el)
                    continue
                dd = K.clip(d, front_sils, keep="out")
                if dd:
                    out.append(head + ' d="' + dd + '"/>\n')
            lay[cls] = out
    s1 = PP.silhouette(figs[0][0], Q1[2], Q1[0], Q1[1], True)
    s2 = PP.silhouette(figs[1][0], Q2[2], Q2[0], Q2[1], True)
    occlude(lays[1], s1)
    occlude(lays[2], s1 + s2)

    # ------------------------------------------------------------ hatch setting on the left
    hat = []
    for k, yy in enumerate((FLOOR_Y + 1, FLOOR_Y + 22, FLOOR_Y + 48)):
        hat.append(K.seg((30 + k * 10, yy + (k * 2)), (700 + k * 12, yy)))
    for k in range(8):
        px = 60 + k * 92
        hat.append(K.seg((px, FLOOR_Y + 1), (px - 22 - k * 2, FLOOR_Y + 60)))
    import a_arch
    for cx in (92.0, 292.0):
        lines, shade = a_arch.corinthian_column(cx, STEP2_TOP - 7, COL_TOP, COL_W)
        hat.append(lines)
        hat.append(shade)
    hat.append(K.seg((20, STEP2_TOP - 7), (360, STEP2_TOP - 7)) + " " + K.seg((20, STEP2_TOP), (360, STEP2_TOP)))
    hat.append(K.seg((20, COL_TOP - 6), (372, COL_TOP - 6)) + " " + K.seg((20, COL_TOP - 22), (372, COL_TOP - 22)))
    hat = [K.clip(h, sils, keep="out") for h in hat]
    # ground shadows under the questioners
    for (x, y, s) in (Q1, Q2, Q3):
        hat.append(K.hatch([(x - 70 * s, y + 4), (x + 50 * s, y + 4), (x + 40 * s, y + 11), (x - 60 * s, y + 11)], angle=0,
                           spacing=2.4, seed=int(x)))

    body = ""
    for lay in lays:
        body += "".join(lay["line"] + lay["detail"])
    for lay in lays:
        body += "".join(lay["hatch"])
    body += "".join(H(h) for h in hat if h)
    return svg(body, "a04 questioners (drawn on the a03 board): Pharisees and a Herodian approach Jesus with "
                     "flattering smiles; x400-1200/y100-270 left clear for 'Taxes to Caesar?'")


if __name__ == "__main__":
    write(OUT, build())
