"""a08-obverse: the big obverse of the tribute penny.
part a (0.2 s): flan + laureate head of Tiberius right.
part b (3.75 s): beaded border, legend TI CAESAR DIVI AVG F AVGVSTVS in struck Roman capitals,
                 edge thickness, wear and relief hatching."""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from lib_v2 import L, D, H, svg, write, BLUE  # noqa: E402
from inkgeom import poly_d, path_pts, clip_outside  # noqa: E402
import denarius as dn  # noqa: E402
import roman_caps as rc  # noqa: E402

OUT = os.path.join(HERE, "..", "A")
C = dn.Coin(800, 402, 330)


def part_a():
    b = ""
    flan = C.flan_pts()
    b += f'  <path class="line" fill="{BLUE}" fill-opacity="0.32" style="mix-blend-mode:multiply" d="{C.pd(flan, True)}"/>\n'
    wr, leaves, ribs = dn.wreath()
    b += L(C.d(dn.PROFILE)) + L(C.d(dn.BACK))
    for run in clip_outside(path_pts(dn.CROWN, 14), leaves, step=1.5, min_len=6):
        b += L(C.pd(run))
    b += L(C.d(dn.EAR))
    b += D(C.pd(wr))
    b += D(C.pd(dn.fringe())) + D(C.pd(dn.hairline_edge()))
    b += D(C.d(dn.EYE)) + D(C.d(dn.IRIS)) + D(C.d(dn.LID)) + D(C.d(dn.BROW)) + D(C.d(dn.NOSTRIL)) + D(C.d(dn.MOUTH))
    b += D(C.d(dn.EAR_IN))
    for t in dn.ties():
        b += D(C.pd(t))
    # hatch (self-drawn texture): hair locks, leaf midribs, relief shading
    tex = dn.hair_texture(leaves)
    b += H(" ".join(C.pd(r) for r in tex))
    b += H(" ".join(C.pd(r) for r in ribs))
    b += H(" ".join(C.pd(s, eps=0) for s in dn.obverse_shading()))
    return b


def part_b():
    b = ""
    for d in rc.strokes_to_d(rc.on_arc("TI CAESAR DIVI AVG F AVGVSTVS", C.cx, C.cy, 258 * C.s, 50 * C.s,
                                       -147, 147, squeeze=0.86, heavy=1.35)):
        b += D(d)
    b += C.beads()
    contour, band = C.edge(C.flan_pts())
    b += L(C.pd(contour))
    # hatch: the edge band, the coin's shadow on the board, wear on the field
    b += H(" ".join(C.pd(s, eps=0) for s in dn.hatch(band, 70, 3.2, jitter=0.3, seed=19, min_len=1.5)))
    b += H(" ".join(C.pd(s, eps=0) for s in C.board_shadow(contour)))
    b += H(" ".join(C.pd(s) for s in C.wear()))
    return b


if __name__ == "__main__":
    write(os.path.join(OUT, "a08-obverse-a.svg"), svg(part_a(), "a08 a: flan and laureate head of Tiberius right"))
    write(os.path.join(OUT, "a08-obverse-b.svg"), svg(part_b(), "a08 b: beaded border, legend, wear"))
