"""a09-reverse: the other side of the tribute penny.
part a (0.2 s): flan + Livia as Pax seated right, long sceptre, olive branch, chair.
part b (2.4 s): PONTIF MAXIM ('highest priest'), beaded border, drapery, chair ornament, footstool,
                exergue line, edge thickness and relief hatching."""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from lib_v2 import L, D, H, svg, write, BLUE  # noqa: E402
from inkgeom import poly_d, path_pts, clip_outside, cr_dense  # noqa: E402
import denarius as dn  # noqa: E402
import roman_caps as rc  # noqa: E402

OUT = os.path.join(HERE, "..", "A")
C = dn.Coin(800, 402, 330)
RV = dn.RV
RV_PTS = dn.RV_PTS


def part_a():
    b = ""
    flan = C.flan_pts(seed=31)
    b += f'  <path class="line" fill="{BLUE}" fill-opacity="0.32" style="mix-blend-mode:multiply" d="{C.pd(flan, True)}"/>\n'
    near = cr_dense(RV_PTS["near_arm"], 6, closed=True)
    torso = cr_dense(RV_PTS["body_upper"][3:], 6, closed=True)
    for run in clip_outside(cr_dense(RV_PTS["body_upper"], 8), [near], step=1.2, min_len=4):
        b += L(C.pd(run))
    b += L(C.pd(cr_dense(RV_PTS["body_lower"], 8)))
    b += L(C.d(RV["sceptre"]))
    for run in clip_outside(cr_dense(RV_PTS["arm"], 8), [torso], step=1.2, min_len=4):
        b += D(C.pd(run))
    b += D(C.pd(cr_dense(RV_PTS["near_arm"], 8)))
    b += D(C.pd(dn.branch()))
    return b


def part_b():
    b = ""
    for d in rc.strokes_to_d(rc.on_arc("PONTIF", C.cx, C.cy, 258 * C.s, 52 * C.s, -132, -56, squeeze=0.92, heavy=1.35)):
        b += D(d)
    for d in rc.strokes_to_d(rc.on_arc("MAXIM", C.cx, C.cy, 258 * C.s, 52 * C.s, 56, 132, squeeze=0.92, heavy=1.35)):
        b += D(d)
    b += C.beads()
    b += D(C.d(RV["seat"]))
    b += D(C.pd(dn.baluster(-99, 50, 198))) + D(C.pd(dn.baluster(25, 50, 198))) + D(C.d("M -95 150 L 21 150"))
    b += D(C.d(RV["stool"])) + D(C.d(RV["ground"])) + D(C.d(RV["finial"])) + D(C.d(RV["fist"]))
    b += D(C.d(dn.smooth_d(RV_PTS["shins"]))) + D(C.d(RV["mantle"]))
    b += D(C.d(RV["eye"])) + D(C.d(RV["mouth"])) + D(C.d(RV["ear"]))
    contour, band = C.edge(C.flan_pts(seed=31))
    b += L(C.pd(contour))
    b += H(" ".join(C.pd(s, eps=0) for s in dn.reverse_shading()))
    b += H(" ".join(C.pd(s, eps=0) for s in dn.hatch(band, 70, 3.2, jitter=0.3, seed=19, min_len=1.5)))
    b += H(" ".join(C.pd(s, eps=0) for s in C.board_shadow(contour)))
    return b


if __name__ == "__main__":
    write(os.path.join(OUT, "a09-reverse-a.svg"), svg(part_a(), "a09 a: flan, Livia as Pax seated right with sceptre and branch"))
    write(os.path.join(OUT, "a09-reverse-b.svg"), svg(part_b(), "a09 b: PONTIF MAXIM, beads, drapery and details"))
