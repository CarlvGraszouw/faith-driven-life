"""a08-obverse: the big obverse of the tribute penny.
part a (0.2 s): flan + laureate head of Tiberius right.
part b (3.75 s): beaded border, legend TI CAESAR DIVI AVG F AVGVSTVS in struck Roman capitals,
                 edge thickness, wear and relief hatching."""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from lib_v2 import L, D, H, svg, write, BLUE  # noqa: E402
from inkgeom import poly_d  # noqa: E402
import denarius as dn  # noqa: E402
import roman_caps as rc  # noqa: E402

OUT = os.path.join(HERE, "..", "A")
C = dn.Coin(800, 402, 330)


def part_a():
    b = ""
    flan = C.flan_pts()
    b += f'  <path class="line" fill="{BLUE}" fill-opacity="0.32" style="mix-blend-mode:multiply" d="{C.pd(flan, True)}"/>\n'
    b += L(C.d(dn.PROFILE))
    b += L(C.d(dn.CROWN))
    b += L(C.d(dn.BACK))
    b += L(C.d(dn.EAR))
    for row in dn.wreath_rows():
        b += D(C.pd(row))
    for row in dn.hair_rows():
        b += D(C.pd(row))
    b += D(C.d(dn.EYE)) + D(C.d(dn.BROW)) + D(C.d(dn.IRIS)) + D(C.d(dn.NOSE)) + D(C.d(dn.MOUTH))
    b += D(C.d(dn.EAR_IN)) + D(C.d(dn.CHEEK)) + D(C.d(dn.NECK))
    for t in dn.ties():
        b += D(C.pd(t))
    return b


def part_b():
    b = C.beads()
    for d in rc.strokes_to_d(rc.on_arc("TI CAESAR DIVI AVG F AVGVSTVS", C.cx, C.cy, 252 * C.s, 50 * C.s,
                                       -147, 147, squeeze=0.86, heavy=1.35)):
        b += D(d)
    return b


if __name__ == "__main__":
    write(os.path.join(OUT, "a08-obverse-a.svg"), svg(part_a(), "a08 a: flan and laureate head of Tiberius right"))
    write(os.path.join(OUT, "a08-obverse-b.svg"), svg(part_b(), "a08 b: beaded border, legend, wear"))
