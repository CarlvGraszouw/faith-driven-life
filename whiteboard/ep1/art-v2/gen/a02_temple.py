"""a02-temple (12.14-21.78 s): Jerusalem a few days before Passover - Herod's Temple seen from the
Court of the Gentiles: the Royal Stoa receding on the left, the walls and gates of the inner courts on the
right, the sanctuary with its gold portal towering above them, pilgrims crowding the courtyard.
Writes art-v2/A/a02-temple.svg"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a02a05_tools import *  # noqa

OUT = os.path.join(EP1, 'art-v2', 'A', 'a02-temple.svg')

# ----------------------------------------------------------------------------- camera / world
# world metres: X east, Y north, Z up; camera stands on the steps of the east portico.
CAM = dict(pos=(0.0, 0.0, 8.0), az=170.0, f=1300.0, cx=800.0, cy=450.0)
cam = Cam(CAM['pos'], CAM['az'], CAM['f'], CAM['cx'], CAM['cy'])
P = cam.p

B = Board(gap=2.0)

# sanctuary
SX, SY, SZ, SS = -189.0, 62.0, 10.0, 1.1          # east face x, axis y, base z, scale
FW, FH, FD = 26.0 * SS, 52.0 * SS, 6.0 * SS       # facade half-width, height, depth
BW, BH, BL = 18.0 * SS, 49.0 * SS, 52.0 * SS      # body half-width, height, length
# courts
CW = dict(x0=-145.0, x1=-75.0, y0=30.0, y1=100.0, z=20.0)   # Court of Women
CI = dict(x0=-262.0, x1=-145.0, y0=27.0, y1=103.0, z=24.0)  # Court of Israel / Priests
TER = dict(x0=-272.0, x1=-66.0, y0=19.0, y1=111.0, z=4.0)   # Hel terrace
STEP_RUN = 6.0                                               # depth of the flight of steps
# Royal Stoa
STOA_Y = -36.0


def quad(*Ps):
    return [P(q) for q in Ps]


def poly2(pts):
    return to_poly(pts)


# ----------------------------------------------------------------------------- sanctuary
def sanctuary():
    it = B.item(-300, 'sanct', 'sanctuary')
    xF, xB = SX, SX - FD
    yl, yr = SY - FW, SY + FW
    zt = SZ + FH
    # facade front (east face) and its south return; body south face and roofline
    front = quad((xF, yl, SZ), (xF, yr, SZ), (xF, yr, zt), (xF, yl, zt))
    side = quad((xB, yl, SZ), (xF, yl, SZ), (xF, yl, zt), (xB, yl, zt))
    byl = SY - BW
    bzt = SZ + BH
    body = quad((xB - BL, byl, SZ), (xB, byl, SZ), (xB, byl, bzt), (xB - BL, byl, bzt))
    body_top = quad((xB - BL, byl, bzt), (xB, byl, bzt), (xB, SY + BW, bzt), (xB - BL, SY + BW, bzt))
    occ = unary_union([poly2(front), poly2(side), poly2(body), poly2(body_top)])
    it.occlude(occ)
    # silhouette: one continuous contour
    it.L(list(occ.exterior.coords))
    # facade edge where front meets the south return
    it.D([P((xF, yl, SZ)), P((xF, yl, zt))])
    # body/facade junction line
    it.D([P((xB, byl, SZ)), P((xB, byl, bzt))])
    return it


# ----------------------------------------------------------------------------- inner courts
def courts():
    items = []
    # Court of Israel south face + top strip of its east face (above the Court of Women)
    ci = B.item(-200, 'courts', 'court-israel')
    s_face = quad((CI['x0'], CI['y0'], TER['z']), (CI['x1'], CI['y0'], TER['z']), (CI['x1'], CI['y0'], CI['z']), (CI['x0'], CI['y0'], CI['z']))
    e_face = quad((CI['x1'], CI['y0'], TER['z']), (CI['x1'], CI['y1'], TER['z']), (CI['x1'], CI['y1'], CI['z']), (CI['x1'], CI['y0'], CI['z']))
    occ = unary_union([poly2(s_face), poly2(e_face)])
    ci.occlude(occ)
    ci.L(list(occ.exterior.coords))
    items.append(ci)
    # Court of Women
    cw = B.item(-150, 'courts', 'court-women')
    s_face = quad((CW['x0'], CW['y0'], TER['z']), (CW['x1'], CW['y0'], TER['z']), (CW['x1'], CW['y0'], CW['z']), (CW['x0'], CW['y0'], CW['z']))
    e_face = quad((CW['x1'], CW['y0'], TER['z']), (CW['x1'], CW['y1'], TER['z']), (CW['x1'], CW['y1'], CW['z']), (CW['x1'], CW['y0'], CW['z']))
    occ = unary_union([poly2(s_face), poly2(e_face)])
    cw.occlude(occ)
    cw.L(list(occ.exterior.coords))
    cw.D([P((CW['x1'], CW['y0'], TER['z'])), P((CW['x1'], CW['y0'], CW['z']))])
    items.append(cw)
    # terrace with steps (south and east faces)
    tr = B.item(-120, 'courts', 'terrace')
    x0, x1, y0, y1, z = TER['x0'], TER['x1'], TER['y0'], TER['y1'], TER['z']
    r = STEP_RUN
    s_top = quad((x0, y0, z), (x1, y0, z), (x1 + r, y0 - r, 0), (x0, y0 - r, 0))
    e_top = quad((x1, y0, z), (x1, y1, z), (x1 + r, y1, 0), (x1 + r, y0 - r, 0))
    occ = unary_union([poly2(s_top), poly2(e_top)])
    tr.occlude(occ)
    tr.D(list(occ.exterior.coords))
    items.append(tr)
    return items


# ----------------------------------------------------------------------------- Royal Stoa
def stoa():
    it = B.item(-260, 'stoa', 'stoa')
    y = STOA_Y
    xa, xb = 30.0, -480.0
    zc, ze, zr, zc2, zn = 14.0, 16.0, 19.0, 30.0, 34.0
    yn = y - 15.0           # clerestory wall
    yr = yn - 6.5           # ridge
    front = quad((xa, y, 0), (xb, y, 0), (xb, y, ze), (xa, y, ze))
    roof1 = quad((xa, y, ze), (xb, y, ze), (xb, yn, zr), (xa, yn, zr))
    cler = quad((xa, yn, zr), (xb, yn, zr), (xb, yn, zc2), (xa, yn, zc2))
    roof2 = quad((xa, yn, zc2), (xb, yn, zc2), (xb, yr, zn), (xa, yr, zn))
    occ = unary_union([poly2(front), poly2(roof1), poly2(cler), poly2(roof2)]).intersection(sbox(-50, -50, 1650, 950))
    it.occlude(occ)
    it.L(list(occ.exterior.coords))
    it.D([P((xa, y, ze)), P((xb, y, ze))])
    it.D([P((xa, yn, zr)), P((xb, yn, zr))])
    it.D([P((xa, yn, zc2)), P((xb, yn, zc2))])
    return it


def ground():
    it = B.item(-2000, 'ground', 'ground')
    # horizon guide (temporary)
    it.H([(0, CAM['cy']), (1600, CAM['cy'])])
    return it


sanctuary()
courts()
stoa()
ground()

if __name__ == '__main__':
    out = B.build(['sanct', 'courts', 'stoa', 'ground'])
    print(timing(out))
    B.write(OUT, 'a02-temple v2: Herod\'s Temple from the Court of the Gentiles, a few days before Passover')
