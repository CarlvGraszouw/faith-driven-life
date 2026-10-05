"""a07-coin-hand: "Show me the coin." Close-up: a Herodian's ringed hand presses a silver denarius
into Jesus' open left palm. Jesus' cream tunic sleeve, his mantle (CLOAK) over the forearm with a
tassel; the questioner's fine sleeve with a woven border."""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from lib_v2 import L, D, H, svg, write, BLUE, CLOAK  # noqa: E402
from inkgeom import poly_d, cr_dense, clip_outside, ell_pts, hatch, resample  # noqa: E402
from hands import HandFrame, Finger, outline_chain  # noqa: E402
import denarius as dn  # noqa: E402

OUT = os.path.join(HERE, "..", "A")

# ---------------------------------------------------------------- Jesus' left hand, palm up
JF = HandFrame(wrist=(1080, 505), direction=(-0.96, -0.28), length=470, thumb_side=(-0.28, 0.96), fv=0.8)
J_FING = [  # pinky (v-) ... index (v+)
    Finger((0.52, -0.16), -12, [0.16, 0.10, 0.09], [0.085, 0.078, 0.07, 0.064], bend=4),
    Finger((0.565, -0.06), -5, [0.21, 0.13, 0.10], [0.098, 0.09, 0.082, 0.075], bend=2),
    Finger((0.58, 0.045), 0, [0.22, 0.135, 0.105], [0.105, 0.097, 0.088, 0.08], bend=0),
    Finger((0.555, 0.15), 6, [0.20, 0.12, 0.10], [0.10, 0.092, 0.084, 0.078], bend=-3),
]
J_THUMB = Finger((0.10, 0.17), 28, [0.24, 0.15, 0.12], [0.20, 0.13, 0.11, 0.10], bend=-10)


def jesus_hand():
    F = J_FING
    webs = [(0.53, -0.11), (0.575, -0.008), (0.57, 0.098)]
    pts = outline_chain(F, (0.0, -0.19), (0.45, 0.205), webs)
    # pinky side of the palm (hypothenar) before the pinky
    hyp = cr_dense([(0.0, -0.19), (0.13, -0.218), (0.29, -0.228), (0.44, -0.214), F[0].sides()[0][0]], 5)
    # thumb: inner edge from the web, round the tip, outer edge back to the wrist
    lft, rgt = J_THUMB.sides()
    th = lft[int(len(lft) * 0.55):] + J_THUMB.tip_cap() + list(reversed(rgt))
    th += cr_dense([rgt[0], (0.04, 0.24), (0.0, 0.22)], 4)[1:]
    outline = hyp + pts[1:-1] + th
    return outline


def jesus_details():
    """flexion creases, palm lines, nails hidden (palm side), wrist creases"""
    out = []
    for f in J_FING:
        out.append(f.crease(0, 0.06, 0.2))           # base crease
        out.append(f.crease(1, 0.0, 0.25, 0.7))      # PIP
        out.append(f.crease(2, 0.0, 0.25, 0.6))      # DIP
    # palm: heart, head and life lines
    out.append(cr_dense([(0.47, -0.205), (0.45, -0.12), (0.47, -0.03), (0.52, 0.05)], 6))
    out.append(cr_dense([(0.45, 0.17), (0.40, 0.07), (0.36, -0.04), (0.33, -0.15)], 6))
    out.append(cr_dense([(0.44, 0.18), (0.32, 0.12), (0.18, 0.10), (0.05, 0.12)], 6))
    out.append(cr_dense([(0.02, -0.16), (0.0, 0.0), (0.02, 0.17)], 5))     # wrist crease
    return out


# ---------------------------------------------------------------- the questioner's right hand, palm down
QF = HandFrame(wrist=(560, 230), direction=(0.74, 0.67), length=420, thumb_side=(0.67, -0.74), fv=0.86)
Q_FING = [  # pinky (v-) ... index (v+), seen from the back; 3 curled, index pressing the coin
    Finger((0.40, -0.15), -10, [0.11, 0.06], [0.082, 0.078, 0.07], bend=30, tip_round=0.9),
    Finger((0.45, -0.06), -5, [0.13, 0.065], [0.094, 0.09, 0.082], bend=30, tip_round=0.9),
    Finger((0.47, 0.035), 0, [0.14, 0.07], [0.10, 0.096, 0.088], bend=28, tip_round=0.9),
    Finger((0.45, 0.13), 4, [0.21, 0.13, 0.10], [0.096, 0.088, 0.08, 0.074], bend=-4),
]
Q_THUMB = Finger((0.06, 0.19), 30, [0.25, 0.16, 0.12], [0.18, 0.12, 0.105, 0.096], bend=-24)


def q_hand():
    F = Q_FING
    webs = [(0.43, -0.105), (0.465, -0.012), (0.46, 0.085)]
    pts = outline_chain(F, (0.0, -0.17), (0.40, 0.19), webs)
    side = cr_dense([(0.0, -0.17), (0.14, -0.19), (0.30, -0.19), F[0].sides()[0][0]], 5)
    lft, rgt = Q_THUMB.sides()
    th = lft[int(len(lft) * 0.5):] + Q_THUMB.tip_cap() + list(reversed(rgt))
    th += cr_dense([rgt[0], (0.02, 0.21), (0.0, 0.18)], 4)[1:]
    return side + pts[1:-1] + th


def q_details():
    out = []
    for f in Q_FING[:3]:
        out.append(f.crease(0, 0.0, -0.35, 0.75))     # knuckle
        out.append(f.crease(1, 0.0, -0.4, 0.7))
    idx = Q_FING[3]
    out.append(idx.crease(0, 0.0, -0.35, 0.75))
    out.append(idx.crease(1, 0.0, -0.3, 0.6))
    out.append(idx.crease(2, 0.0, -0.3, 0.5))
    # nail of the index
    a = idx.at(2, 0.55, -0.55); b = idx.at(2, 0.95, -0.45); c = idx.at(2, 0.95, 0.45); d = idx.at(2, 0.55, 0.55)
    out.append(cr_dense([a, b, c, d], 4))
    # tendons on the back of the hand
    for vv in (0.12, 0.03, -0.06):
        out.append(cr_dense([(0.12, vv * 0.7), (0.28, vv * 0.9), (0.42, vv)], 4))
    return out


def body():
    b = ""
    # coin in the palm: a tilted disc lying in the palm plane
    cu, cv = 0.33, 0.0
    coin = [JF.P(cu + 0.078 * math.cos(t), cv + 0.078 * math.sin(t)) for t in [i * 2 * math.pi / 48 for i in range(49)]]
    jh = [JF.P(u, v) for u, v in jesus_hand()]
    qh = [QF.P(u, v) for u, v in q_hand()]
    b += L(poly_d(jh, closed=True))
    b += L(poly_d(qh, closed=True))
    b += f'  <path class="line" fill="{BLUE}" fill-opacity="0.55" style="mix-blend-mode:multiply" d="{poly_d(coin, True)}"/>\n'
    for c in jesus_details():
        b += D(poly_d([JF.P(u, v) for u, v in c]))
    for c in q_details():
        b += D(poly_d([QF.P(u, v) for u, v in c]))
    return b


if __name__ == "__main__":
    write(os.path.join(OUT, "a07-coin-hand.svg"), svg(body(), "a07: a Herodian presses a denarius into Jesus' open palm"))
