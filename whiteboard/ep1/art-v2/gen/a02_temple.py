"""a02-temple (12.14-21.78 s): Jerusalem a few days before Passover - Herod's Temple seen from the
east portico across the Court of the Gentiles: the Royal Stoa receding on the left, the walls and gates of
the inner courts, the sanctuary with its gold portal towering above them, the Antonia beyond, pilgrims
crowding the courtyard.  Writes art-v2/A/a02-temple.svg"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a02a05_tools import *  # noqa

OUT = os.path.join(EP1, 'art-v2', 'A', 'a02-temple.svg')

# ----------------------------------------------------------------------------- camera / world
# world metres: X east, Y north, Z up; origin = centre of the sanctuary's east facade at court level.
CAM = dict(pos=(260.0, -62.0, 9.0), az=174.0, f=1500.0, cx=800.0, cy=385.0)
cam = Cam(CAM['pos'], CAM['az'], CAM['f'], CAM['cx'], CAM['cy'])
P = cam.p
B = Board(gap=2.0)

# z layers (bigger = nearer)
Z_CITY, Z_HILL, Z_ANT, Z_WPOR, Z_SANCT, Z_SMOKE = -6000, -6500, -4000, -3500, -3000, -2950
Z_CI, Z_NIC, Z_CW, Z_TER, Z_SOREG = -2800, -2750, -2700, -2600, -2550
Z_STOA_IN, Z_STOA = -2450, -2300

SS = 1.1
FW, FH, FD = 26.0 * SS, 52.0 * SS, 6.0 * SS        # facade half width, height, depth
BW, BH, BL = 18.0 * SS, 49.0 * SS, 52.0 * SS       # body half width, height, length
SZ = 10.0                                           # sanctuary floor above the plaza
CI = dict(x0=-70.0, x1=40.0, y0=-37.0, y1=37.0, z=24.0)
CW = dict(x0=40.0, x1=110.0, y0=-35.0, y1=35.0, z=20.0)
TER = dict(x0=-76.0, x1=116.0, y0=-43.0, y1=43.0, z=4.0)
RUN = 6.0
STOA_Y, STOA_X0, STOA_X1 = -118.0, 330.0, -300.0
NEAR_COL_X = 60.0


def F(*Ps):
    return cam.poly3(list(Ps))


def G(*Ps):
    return to_poly(F(*Ps))


def LN(*Ps, n=1):
    return cam.line3(list(Ps), n=n)


class Face:
    """planar rectangle in the world with local (u, w) metres"""

    def __init__(self, origin, u_axis, w_axis):
        self.o, self.u, self.w = np.asarray(origin, float), np.asarray(u_axis, float), np.asarray(w_axis, float)

    def W(self, u, w):
        return tuple(self.o + self.u * u + self.w * w)

    def p(self, u, w):
        return P(self.W(u, w))

    def line(self, pts, n=1):
        return cam.line3([self.W(u, w) for u, w in pts], n=n)

    def gpoly(self, pts):
        return to_poly(cam.poly3([self.W(u, w) for u, w in pts]))

    def rect(self, u0, u1, w0, w1):
        return self.gpoly([(u0, w0), (u1, w0), (u1, w1), (u0, w1)])


def runs(it, cls, rr):
    for r in rr:
        it.add(cls, r)


# ----------------------------------------------------------------------------- sanctuary
def sanctuary():
    it = B.item(Z_SANCT, 'sanct', 'sanctuary')
    fr = Face((0, -FW, SZ), (0, 1, 0), (0, 0, 1))                 # east facade, u: 0..2FW south->north
    rt = Face((-FD, -FW, SZ), (1, 0, 0), (0, 0, 1))               # south return of the facade, u: 0..FD
    bd = Face((-FD - BL, -BW, SZ), (1, 0, 0), (0, 0, 1))          # body south face, u: 0..BL
    occ = unary_union([fr.rect(0, 2 * FW, 0, FH), rt.rect(0, FD, 0, FH), bd.rect(0, BL, 0, BH)])
    it.occlude(occ)
    for r in rings(occ):
        it.L(r)
    c = FW
    runs(it, 'detail', fr.line([(0, 0), (0, FH)]))
    runs(it, 'detail', bd.line([(BL, 0), (BL, BH)]))
    # crowning cornice + entablature over the columns (one stroke each)
    runs(it, 'detail', fr.line([(0, FH - 3.2), (2 * FW, FH - 3.2)]))
    runs(it, 'detail', fr.line([(0, 41.8), (2 * FW, 41.8)]))
    # portal and the golden porch inside it
    pw, ph = 7.2, 37.0
    portal = [(c - pw, 0), (c - pw, ph), (c + pw, ph), (c + pw, 0)]
    runs(it, 'detail', fr.line(portal))
    gold = fr.gpoly(portal)
    it.fill(rings(gold)[0], GOLD, cls='detail')
    rec = Face((-6.6, -FW, SZ), (0, 1, 0), (0, 0, 1))             # back wall of the porch
    dw, dh = 4.3, 29.5
    runs(it, 'hatch', rec.line([(c - dw, 0), (c - dw, dh), (c + dw, dh), (c + dw, 0)]))
    runs(it, 'hatch', rec.line([(c, 0), (c, dh)]))
    for w in (7, 14, 21):
        runs(it, 'hatch', rec.line([(c - dw + 0.7, w), (c + dw - 0.7, w)]))
    # north reveal of the portal (we look slightly into it from the south)
    runs(it, 'hatch', [[fr.p(c + pw, ph), rec.p(c + pw, ph)]])
    it.hatch(to_poly([fr.p(c + pw, 0), fr.p(c + pw, ph), rec.p(c + pw, ph), rec.p(c + pw, 0)]), angle=88, spacing=1.6)
    # the golden vine over the inner door
    vine = [rec.W(c - dw - 1.5 + k * (2 * dw + 3.0) / 10, dh + 2.4 + 0.8 * math.sin(k * 1.9)) for k in range(11)]
    vr = [P(q) for q in vine]
    it.H(sp(vr))
    for k, q in enumerate(vr[1:-1]):
        s = 1 if k % 2 else -1
        it.H(sp([(q[0], q[1]), (q[0] + 1.2, q[1] + 2.0 * s), (q[0] + 2.6, q[1] + 1.2 * s), (q[0] + 1.6, q[1])]))
    # engaged half-columns flanking the portal: one meander stroke
    cols = [c - 19.5, c - 12.0, c + 12.0, c + 19.5]
    hw = 1.3
    m = []
    for u in cols:
        m += [(u - hw, 0.6), (u - hw, 37.8), (u - hw - 0.9, 39.8), (u + hw + 0.9, 39.8), (u + hw, 37.8), (u + hw, 0.6)]
    runs(it, 'detail', fr.line(m))
    for u in cols:
        runs(it, 'hatch', fr.line([(u - hw - 0.9, 39.8), (u - 0.7, 38.3), (u, 39.8), (u + 0.7, 38.3), (u + hw + 0.9, 39.8)]))
        for du in (-0.65, 0.0, 0.65):
            runs(it, 'hatch', fr.line([(u + du, 1.4), (u + du, 37.0)]))
        runs(it, 'hatch', fr.line([(u - hw - 0.6, 0.6), (u + hw + 0.6, 0.6)]))
    # attic panels, dentils, gold spikes
    runs(it, 'hatch', fr.line([(0.5, 44.0), (2 * FW - 0.5, 44.0)]))
    for u in np.arange(1.2, 2 * FW, 2.2):
        runs(it, 'hatch', fr.line([(u, 42.4), (u, 43.6)]))
    runs(it, 'hatch', fr.line([(0.5, FH - 6.4), (2 * FW - 0.5, FH - 6.4)]))
    for u in np.arange(0.9, 2 * FW, 1.3):
        runs(it, 'hatch', fr.line([(u, FH - 3.2), (u, FH - 2.1)]))
    for u in np.arange(0.7, 2 * FW, 1.7):
        runs(it, 'hatch', fr.line([(u, FH), (u, FH + 1.3)]))
    for u in np.arange(0.6, BL, 2.0):
        runs(it, 'hatch', bd.line([(u, BH), (u, BH + 1.1)]))
    # shading: return face and body in light shade; shadow under the cornice
    it.hatch(rt.rect(0, FD, 0, FH), angle=76, spacing=2.6)
    it.hatch(bd.rect(0, BL, 0, BH - 0.4), angle=72, spacing=5.0)
    it.hatch(fr.rect(0, 2 * FW, FH - 4.4, FH - 3.2), angle=0, spacing=1.0)
    for w in (BH - 3.0, BH - 8.5):
        runs(it, 'hatch', bd.line([(0.3, w), (BL - 0.3, w)]))
    for k in range(7):                                  # upper-storey windows of the side chambers
        u = 4.0 + k * (BL - 8.0) / 6
        runs(it, 'hatch', bd.line([(u - 0.9, BH - 15.0), (u - 0.9, BH - 11.0), (u + 0.9, BH - 11.0), (u + 0.9, BH - 15.0)]))
    for w in np.arange(5.0, 36.0, 5.0):
        runs(it, 'hatch', fr.line([(0.4, w), (c - 21.3, w)]))
        runs(it, 'hatch', fr.line([(c + 21.3, w), (2 * FW - 0.4, w)]))
    return it


# ----------------------------------------------------------------------------- inner courts
def courses(it, face, u0, u1, w0, w1, step=1.7, holes=()):
    w = w0 + step
    while w < w1 - 0.4:
        segs = [(u0, u1)]
        for a, b, c0, c1 in holes:
            if c0 <= w <= c1:
                segs = [s for seg in segs for s in ((seg[0], min(seg[1], a)), (max(seg[0], b), seg[1])) if s[1] - s[0] > 0.6]
        for a, b in segs:
            runs(it, 'hatch', face.line([(a, w), (b, w)]))
        w += step


def pilasters(it, face, u0, u1, w0, w1, spacing=4.0, holes=()):
    u = u0 + spacing / 2
    while u < u1:
        if not any(a - 1 <= u <= b + 1 for a, b, _, _ in holes):
            runs(it, 'hatch', face.line([(u - 0.5, w0), (u - 0.5, w1)]))
            runs(it, 'hatch', face.line([(u + 0.5, w0), (u + 0.5, w1)]))
        u += spacing


def gate(face, u, width, proj, top, door_w, door_h, z, name, outward):
    it = B.item(z, 'courts', name)
    hw = width / 2
    n = np.asarray(outward, float)
    fr = Face(face.o + n * proj, face.u, face.w)
    sd = Face(face.o + face.u * (u + hw), n, face.w)
    occ = unary_union([fr.rect(u - hw, u + hw, 0, top), sd.rect(0, proj, 0, top)])
    it.occlude(occ)
    OUTLINE.append(occ)
    runs(it, 'detail', fr.line([(u + hw, 0), (u + hw, top)]))
    runs(it, 'detail', fr.line([(u - hw, 0), (u - hw, top)]))
    dl, dr = u - door_w / 2, u + door_w / 2
    runs(it, 'hatch', fr.line([(dl, 0), (dl, door_h), (dr, door_h), (dr, 0)]))
    runs(it, 'hatch', fr.line([(dl - 1.0, door_h + 1.4), (dr + 1.0, door_h + 1.4)]))
    it.hatch(fr.rect(dl, dr, 0, door_h), angle=82, spacing=1.6, cross=8, cross_spacing=2.2)
    runs(it, 'hatch', fr.line([(u - hw, top - 1.7), (u + hw, top - 1.7)]))
    courses(it, fr, u - hw + 0.2, u + hw - 0.2, 0, top - 1.7, 1.9, holes=[(dl - 0.2, dr + 0.2, 0, door_h + 1.8)])
    it.hatch(sd.rect(0, proj, 0, top), angle=80, spacing=2.4)
    return it


OUTLINE = []


def courts():
    zT = TER['z']
    # Court of Israel: south face and the strip of its east face above the Court of Women
    ci = B.item(Z_CI, 'courts', 'court-israel')
    H1, L1 = CI['z'] - zT, CI['x1'] - CI['x0']
    sf = Face((CI['x0'], CI['y0'], zT), (1, 0, 0), (0, 0, 1))
    ef = Face((CI['x1'], CI['y0'], zT), (0, 1, 0), (0, 0, 1))
    occ = unary_union([sf.rect(0, L1, 0, H1), ef.rect(0, CI['y1'] - CI['y0'], 0, H1)])
    ci.occlude(occ)
    OUTLINE.append(occ)
    runs(ci, 'hatch', sf.line([(0, H1 - 1.6), (L1, H1 - 1.6)]))
    ci.hatch(sf.rect(0, L1, H1 - 2.7, H1 - 1.6), angle=0, spacing=1.0)
    gx = [CI['x1'] - 22.0, CI['x1'] - 55.0, CI['x1'] - 88.0]
    holes = [(g - CI['x0'] - 6.5, g - CI['x0'] + 6.5, 0, 99) for g in gx]
    courses(ci, sf, 0.3, L1 - 0.3, 0, H1 - 2.7, 1.8)
    ci.hatch(sf.rect(0, L1, 0, H1 - 2.7), angle=70, spacing=4.6)
    for k, g in enumerate(gx):
        gate(sf, g - CI['x0'], 12.0, 2.4, H1 + 4.2, 5.0, 9.2, Z_CI + 5 + k, f'ci-gate{k}', (0, -1, 0))
    # Nicanor gate rising over the Court of Women
    nic = B.item(Z_NIC, 'courts', 'nicanor')
    nf = Face((CI['x1'] + 1.5, -8.0, zT), (0, 1, 0), (0, 0, 1))
    ng = nf.rect(0, 16, 0, H1 + 2.5)
    nic.occlude(ng)
    OUTLINE.append(ng)
    runs(nic, 'hatch', nf.line([(0.4, H1 + 1.2), (15.6, H1 + 1.2)]))
    nic.hatch(nf.rect(0, 16, H1 - 3.0, H1 + 1.2), angle=84, spacing=2.4)
    # Court of Women: south and east faces
    cw = B.item(Z_CW, 'courts', 'court-women')
    H2, L2, D2 = CW['z'] - zT, CW['x1'] - CW['x0'], CW['y1'] - CW['y0']
    sf2 = Face((CW['x0'], CW['y0'], zT), (1, 0, 0), (0, 0, 1))
    ef2 = Face((CW['x1'], CW['y0'], zT), (0, 1, 0), (0, 0, 1))
    occ = unary_union([sf2.rect(0, L2, 0, H2), ef2.rect(0, D2, 0, H2)])
    cw.occlude(occ)
    OUTLINE.append(occ)
    runs(cw, 'detail', ef2.line([(0, 0), (0, H2)]))
    for face, Lf in ((sf2, L2), (ef2, D2)):
        runs(cw, 'hatch', face.line([(0, H2 - 1.5), (Lf, H2 - 1.5)]))
        cw.hatch(face.rect(0, Lf, H2 - 2.5, H2 - 1.5), angle=0, spacing=1.0)
    sgx = 75.0 - CW['x0']
    bgy = 0.0 - CW['y0']
    courses(cw, sf2, 0.3, L2 - 0.3, 0, H2 - 2.5, 1.8)
    courses(cw, ef2, 0.3, D2 - 0.3, 0, H2 - 2.5, 1.8)
    cw.hatch(sf2.rect(0, L2, 0, H2 - 2.5), angle=70, spacing=4.6)
    gate(sf2, sgx, 12.0, 2.4, H2 + 4.2, 5.0, 9.2, Z_CW + 5, 'cw-gate-s', (0, -1, 0))
    gate(ef2, bgy, 14.0, 3.0, H2 + 5.6, 6.2, 11.0, Z_CW + 6, 'beautiful-gate', (1, 0, 0))
    ol = B.item(Z_CW + 50, 'courts', 'courts-outline')
    for r in rings(unary_union(OUTLINE)):
        ol.L(r)
    # terrace and the flight of steps on its south and east sides
    tr = B.item(Z_TER, 'courts', 'terrace')
    x0, x1, y0, y1, z = TER['x0'], TER['x1'], TER['y0'], TER['y1'], TER['z']
    r = RUN
    s_fl = G((x0, y0, z), (x1, y0, z), (x1 + r, y0 - r, 0), (x0, y0 - r, 0))
    e_fl = G((x1, y0, z), (x1, y1, z), (x1 + r, y1, 0), (x1 + r, y0 - r, 0))
    tr.occlude(unary_union([s_fl, e_fl]))
    runs(tr, 'detail', LN((x0, y0 - r, 0), (x1 + r, y0 - r, 0), (x1 + r, y1, 0)))
    runs(tr, 'hatch', LN((x0, y0, z), (x1, y0, z), (x1, y1, z)))
    runs(tr, 'hatch', LN((x1, y0, z), (x1 + r, y0 - r, 0)))
    for k in range(1, 7):
        t = k / 7
        zz = z * (1 - t)
        runs(tr, 'hatch', LN((x0, y0 - r * t, zz), (x1 + r * t, y0 - r * t, zz), (x1 + r * t, y1, zz)))
    # soreg: low stone lattice at the foot of the steps
    so = B.item(Z_SOREG, 'courts', 'soreg')
    ys, xs = y0 - r - 3.0, x1 + r + 3.0
    runs(so, 'detail', LN((x0, ys, 1.3), (xs, ys, 1.3), (xs, y1, 1.3)))
    ps = G((x0, ys, 0), (xs, ys, 0), (xs, ys, 1.3), (x0, ys, 1.3))
    pe = G((xs, ys, 0), (xs, y1, 0), (xs, y1, 1.3), (xs, ys, 1.3))
    so.occlude(unary_union([ps, pe]))
    so.hatch(unary_union([ps, pe]), angle=60, spacing=3.2)


# ----------------------------------------------------------------------------- Royal Stoa
def stoa():
    y = STOA_Y
    xa, xb = STOA_X0, STOA_X1
    zb, zc, zcap, ze = 0.8, 12.4, 13.8, 16.0
    zr, zc2, zn = 19.0, 30.0, 34.0
    yn, yr = y - 15.0, y - 21.5
    it = B.item(Z_STOA, 'stoa', 'stoa')
    roof1 = G((xa, y, ze), (xb, y, ze), (xb, yn, zr), (xa, yn, zr))
    cler = G((xa, yn, zr), (xb, yn, zr), (xb, yn, zc2), (xa, yn, zc2))
    roof2 = G((xa, yn, zc2), (xb, yn, zc2), (xb, yr, zn), (xa, yr, zn))
    ent = G((xa, y, zcap), (xb, y, zcap), (xb, y, ze), (xa, y, ze))
    upper = unary_union([roof1, cler, roof2, ent])
    it.occlude(upper)
    for r in rings(unary_union([roof1, cler, roof2, ent]).buffer(0.01)):
        it.L(r)
    runs(it, 'detail', LN((xa, y, zcap), (xb, y, zcap)))
    runs(it, 'detail', LN((xa, yn, zr), (xb, yn, zr)))
    runs(it, 'hatch', LN((xa, y, zcap + 0.8), (xb, y, zcap + 0.8)))
    runs(it, 'hatch', LN((xa, y, ze - 0.5), (xb, y, ze - 0.5)))
    runs(it, 'hatch', LN((xa, yn, zc2 - 0.9), (xb, yn, zc2 - 0.9)))
    runs(it, 'hatch', LN((xa, yn, zc2), (xb, yn, zc2)))
    step = 7.0
    for x in np.arange(xa - 3.5, xb, -step):
        runs(it, 'hatch', LN((x, yn, zr + 0.3), (x, yn, zc2 - 1.0)))
        xm = x - step / 2
        win = [(xm + 1.3, yn, zr + 2.2), (xm + 1.3, yn, zr + 6.6)] + \
              [(xm + 1.3 * math.cos(a), yn, zr + 6.6 + 1.3 * math.sin(a)) for a in np.linspace(0, math.pi, 7)][1:] + [(xm - 1.3, yn, zr + 2.2)]
        runs(it, 'hatch', cam.line3(win))
    for x in np.arange(xa, xb, -2.4):                    # roof tiles of the aisle roof
        if x > -120 or int(x) % 3 == 0:
            runs(it, 'hatch', LN((x, y, ze + 0.2), (x, yn, zr - 0.2)))
    for x in np.arange(xa, xb, -2.8):                    # tiles of the nave roof
        if x > -120 or int(x) % 3 == 0:
            runs(it, 'hatch', LN((x, yn, zc2 + 0.2), (x, yr, zn - 0.2)))
    it.hatch(cler, angle=80, spacing=6.0)
    # the colonnade: a single meander stroke through all the columns
    cols = list(np.arange(xa - 3.5, xb, -step))
    r = 0.95
    col = B.item(Z_STOA + 1, 'stoa', 'stoa-columns')
    near = [x for x in cols if x > NEAR_COL_X]
    far = [x for x in cols if x <= NEAR_COL_X]
    for group, cls in ((near, 'detail'), (far, 'hatch')):
        m = []
        for x in group:
            m += [(x + r, y, zb), (x + r, y, zc), (x + r + 0.55, y, zcap - 0.15), (x - r - 0.55, y, zcap - 0.15), (x - r, y, zc), (x - r, y, zb)]
        for rr in cam.line3(m):
            col.add(cls, rr)
    occs = []
    for x in cols:
        g = G((x + r + 0.55, y, 0), (x - r - 0.55, y, 0), (x - r - 0.55, y, zcap - 0.4), (x + r + 0.55, y, zcap - 0.4))
        if not g.is_empty:
            occs.append(g)
        for dx in (-0.4, 0.4):
            runs(col, 'hatch', LN((x + dx, y, zb + 0.6), (x + dx, y, zc - 0.4)))
        runs(col, 'hatch', LN((x - r - 0.55, y, zcap - 0.6), (x, y, zc + 0.3), (x + r + 0.55, y, zcap - 0.6)))
        runs(col, 'hatch', LN((x - r - 0.3, y, zb + 0.5), (x + r + 0.3, y, zb + 0.5)))
    col.occlude(unary_union(occs))
    runs(col, 'hatch', LN((xa, y + 0.8, 0), (xb, y + 0.8, 0)))
    inner = B.item(Z_STOA_IN, 'stoa', 'stoa-inner')
    shade = G((xa, y, 0), (xb, y, 0), (xb, y, zcap), (xa, y, zcap))
    near_shade = shade.intersection(sbox(-10, -10, P((NEAR_COL_X - 80, y, 0))[0], 910))
    inner.hatch(shade, angle=68, spacing=2.4)
    inner.hatch(near_shade, angle=-20, spacing=3.6)


# ----------------------------------------------------------------------------- Antonia, west portico, city
def antonia():
    it = B.item(Z_ANT, 'bg', 'antonia')
    X0, X1, Y0, Y1, zb, zw = -185.0, -95.0, 145.0, 195.0, 6.0, 38.0
    towers = [(X1, Y0, 12.0, 66.0), (X0, Y0, 10.0, 54.0), (X1, Y1, 10.0, 54.0)]
    gs = [G((X0, Y0, zb), (X1, Y0, zb), (X1, Y0, zw), (X0, Y0, zw)), G((X1, Y0, zb), (X1, Y1, zb), (X1, Y1, zw), (X1, Y0, zw))]
    for (tx, ty, s, ht) in towers:
        h = s / 2
        gs.append(G((tx - h, ty - h, zb), (tx + h, ty - h, zb), (tx + h, ty - h, ht), (tx - h, ty - h, ht)))
        gs.append(G((tx + h, ty - h, zb), (tx + h, ty + h, zb), (tx + h, ty + h, ht), (tx + h, ty - h, ht)))
    occ = unary_union(gs)
    it.occlude(occ)
    for r in rings(occ):
        it.H(r)
    for (tx, ty, s, ht) in towers:
        h = s / 2
        runs(it, 'hatch', LN((tx + h, ty - h, zb), (tx + h, ty - h, ht)))
        for k in range(5):                                # merlons
            yy = ty - h + (k + 0.5) * s / 5
            runs(it, 'hatch', LN((tx + h, yy - 0.6, ht), (tx + h, yy - 0.6, ht + 1.6), (tx + h, yy + 0.6, ht + 1.6), (tx + h, yy + 0.6, ht)))
        for zz in (ht - 6, ht - 14):                     # arrow slits
            runs(it, 'hatch', LN((tx + h, ty, zz), (tx + h, ty, zz - 2.2)))
        it.hatch(G((tx - h, ty - h, zb), (tx + h, ty - h, zb), (tx + h, ty - h, ht), (tx - h, ty - h, ht)), angle=78, spacing=1.6)
    it.hatch(gs[0], angle=78, spacing=2.0)
    # a Roman standard on the great tower
    tx, ty, s, ht = towers[0]
    runs(it, 'hatch', LN((tx, ty, ht), (tx, ty, ht + 9)))
    runs(it, 'hatch', [sp([P((tx, ty, ht + 8.6)), P((tx, ty + 3.5, ht + 8.2)), P((tx, ty + 6.5, ht + 8.8))])])


def west_portico():
    it = B.item(Z_WPOR, 'bg', 'west-portico')
    xw = STOA_X1 - 12.0
    f1 = G((xw, STOA_Y, 0), (xw, 150, 0), (xw, 150, 13), (xw, STOA_Y, 13))
    it.occlude(f1)
    runs(it, 'hatch', LN((xw, STOA_Y, 13), (xw, 150, 13)))
    for yy in np.arange(STOA_Y + 3, 150, 6.0):
        runs(it, 'hatch', LN((xw, yy, 0), (xw, yy, 11.6)))
    runs(it, 'hatch', LN((xw, STOA_Y, 11.6), (xw, 150, 11.6)))
    it.hatch(f1, angle=72, spacing=2.0)


def city():
    rng = np.random.default_rng(11)
    houses = []
    for k in range(90):
        X = -340 - rng.uniform(0, 520)
        Y = rng.uniform(-520, 120)
        g0 = 12 + 0.045 * max(0, -Y) + 0.02 * (-X - 340)       # the western hill rises to the south-west
        hgt = g0 + rng.uniform(5, 9)
        w, d = rng.uniform(7, 15), rng.uniform(7, 13)
        g = unary_union([G((X, Y, g0), (X, Y + w, g0), (X, Y + w, hgt), (X, Y, hgt)),
                         G((X, Y, g0), (X - d, Y, g0), (X - d, Y, hgt), (X, Y, hgt))])
        if not g.is_empty:
            houses.append((cam.depth((X, Y, 0)), g, (X, Y, w, d, g0, hgt)))
    houses.sort(key=lambda t: -t[0])
    for k, (dep, g, (X, Y, w, d, g0, hgt)) in enumerate(houses):
        h = B.item(Z_CITY + k, 'bg', f'house{k}')
        h.occlude(g)
        for r in rings(g, 0.5):
            h.H(r)
        if k % 3 == 0:
            runs(h, 'hatch', LN((X, Y + w * 0.4, g0), (X, Y + w * 0.4, g0 + 2.2)))
    # Herod's palace towers on the western skyline
    for k, (Y, ht) in enumerate([(-150, 92), (-128, 80), (-112, 74)]):
        X = -900 - k * 8
        g = unary_union([G((X, Y, 40), (X, Y + 11, 40), (X, Y + 11, ht), (X, Y, ht)), G((X, Y, 40), (X - 11, Y, 40), (X - 11, Y, ht), (X, Y, ht))])
        t = B.item(Z_CITY + 500 + k, 'bg', f'tower{k}')
        t.occlude(g)
        for r in rings(g, 0.5):
            t.H(r)
        t.hatch(g, angle=80, spacing=1.6)
    # the hill line behind the city
    hill = B.item(Z_HILL, 'bg', 'hills')
    pts = []
    for k in range(40):
        a = -48 + k * 1.7
        az = math.radians(CAM['az'] + a)
        dist = 1400 + 300 * math.sin(k * 0.5)
        X = CAM['pos'][0] + math.cos(az) * dist
        Y = CAM['pos'][1] + math.sin(az) * dist
        Zh = 55 + 25 * math.sin(k * 0.37 + 1.0) + 10 * math.sin(k * 1.3)
        pts.append(P((X, Y, Zh)))
    hill.H(sp(pts))


# ----------------------------------------------------------------------------- the crowd
import a02a05_crowd as cr  # noqa: E402

KINDS = ['walker', 'back', 'talker', 'jar', 'lamb', 'elder', 'mother', 'porter', 'walker', 'back', 'back', 'walker']


def person(kind, X, Y, Zf=0.0, flip=False, hm=1.72, z=None, cls=None, lean=0.0, group='crowd'):
    x, y = P((X, Y, Zf))
    if not (-30 < x < 1630 and 300 < y < 778):
        return None
    sc = cam.scale((X, Y, Zf))
    h = hm * sc
    zz = z if z is not None else -cam.depth((X, Y, Zf))
    kw = {}
    return cr.place(B, kind, x, y, h, zz, group=group, flip=flip, lean=lean, cls=cls,
                    detail_min=26.0, inner_cls='hatch', prop_cls='hatch')


def ground_from_screen(x, y):
    """back-project a screen point to the plaza (Z=0)"""
    depth = CAM['f'] * CAM['pos'][2] / (y - CAM['cy'])
    lat = (x - CAM['cx']) * depth / CAM['f']
    W = cam.pos + cam.fwd * depth + cam.right * lat
    return float(W[0]), float(W[1])


def on_plaza(X, Y):
    if -116.0 <= Y <= -53.0 and X <= 236.0:
        return True
    if X >= 126.0 and -53.0 <= Y <= 48.0 and X <= 236.0:
        return True
    return False


def crowd():
    rng = np.random.default_rng(5)
    taken = []                     # screen discs (x, y, r) of placed figures

    def free(x, y, r):
        return all((x - a) ** 2 + ((y - b) * 2.2) ** 2 > (r + c) ** 2 for a, b, c in taken)

    def put(kind, X, Y, hero=False, **kw):
        x, y = P((X, Y, kw.get('Zf', 0.0)))
        h = 1.72 * cam.scale((X, Y, kw.get('Zf', 0.0)))
        it = person(kind, X, Y, cls=('detail' if hero else 'hatch'), **kw)
        if it is not None:
            taken.append((x, y, 0.16 * h))
        return it

    # ---- hero groups near the viewer (detail strokes), framing the bottom of the picture
    put('lamb', 236.0, -79.0, hero=True, flip=True)
    put('child', 235.6, -76.4, hero=True, flip=True)
    put('sheep', 234.0, -82.6, hero=True, hm=2.8, flip=True)
    put('back', 236.6, -45.0, hero=True)
    put('back', 235.6, -42.2, hero=True, hm=1.58)
    put('jar', 229.0, -33.0, hero=True, flip=True)
    put('elder', 231.0, -94.0, hero=True)
    put('talker', 228.0, -57.0, hero=True)
    put('walker', 226.6, -60.4, hero=True, flip=True)
    # ---- people on the steps of the terrace (ascending)
    for X in np.arange(-60, 110, 7.5):
        t = rng.uniform(0.15, 0.85)
        put(str(rng.choice(['back', 'walker', 'back', 'jar'])), X + rng.uniform(-2, 2), TER['y0'] - RUN * t,
            Zf=TER['z'] * (1 - t), flip=bool(rng.integers(2)))
    for Yv in np.arange(-36, 40, 5.0):
        t = rng.uniform(0.15, 0.85)
        put(str(rng.choice(['back', 'walker', 'back'])), TER['x1'] + RUN * t, Yv + rng.uniform(-1.5, 1.5),
            Zf=TER['z'] * (1 - t), flip=True)
    # ---- the plaza crowd: clusters of 1-5 people with gaps between them
    centres = []
    tries = 0
    while tries < 6000 and len(centres) < 150:
        tries += 1
        y = CAM['cy'] + 12 + (rng.random() ** 1.6) * (690 - CAM['cy'] - 12)
        x = rng.uniform(-20, 1620)
        X, Y = ground_from_screen(x, y)
        if not on_plaza(X, Y):
            continue
        h = 1.72 * cam.scale((X, Y, 0))
        if all((x - a) ** 2 + ((y - b) * 2.6) ** 2 > (1.9 * max(h, hb)) ** 2 for a, b, hb in centres):
            centres.append((x, y, h))
    for (x, y, h) in centres:
        X, Y = ground_from_screen(x, y)
        n = int(rng.choice([1, 1, 2, 2, 3, 3, 4, 5]))
        heading = bool(rng.integers(2))
        talk = n == 2 and rng.random() < 0.4
        for j in range(n):
            if talk:
                kind, fl = ('talker', j == 1)
                XX, YY = X, Y + (j - 0.5) * 1.6
            else:
                kind = KINDS[int(rng.integers(len(KINDS)))]
                fl = heading if kind != 'back' else False
                XX, YY = X + rng.normal(0, 1.2), Y + rng.normal(0, 1.3)
            if not on_plaza(XX, YY):
                continue
            put(kind, XX, YY, flip=fl, hm=rng.uniform(1.6, 1.8))
            if kind in ('mother', 'walker', 'jar') and rng.random() < 0.25:
                put('child', XX + 0.8, YY - 0.5, flip=heading)
            if kind == 'lamb' and rng.random() < 0.6:
                put('sheep', XX + 1.2, YY + 0.3, hm=2.8, flip=heading)
    # ---- money-changers and dove sellers inside the Royal Stoa (behind the columns)
    for X in np.arange(-40, 250, 9.0):
        Yt = STOA_Y - 6.0
        zin = Z_STOA_IN + 60 - cam.depth((X, Yt, 0)) * 0.01
        if person('seated', X, Yt, z=zin, flip=True, cls='hatch') is not None:
            tx, ty = P((X - 1.6, Yt, 0.9))
            sc = cam.scale((X, Yt, 0))
            tb = B.item(zin + 0.005, 'crowd', 'table')
            tw = 1.1 * sc
            tbl = [(tx - tw, ty), (tx + tw, ty), (tx + tw * 0.9, ty + 0.9 * sc), (tx - tw * 0.9, ty + 0.9 * sc)]
            tb.H(tbl + [tbl[0]])
            tb.occlude(to_poly(tbl))
        for j in range(int(rng.integers(1, 4))):
            Xb = X + rng.uniform(-4, 4)
            Yb = STOA_Y - rng.uniform(1.5, 4.5)
            person(KINDS[int(rng.integers(len(KINDS)))], Xb, Yb, z=Z_STOA_IN + 80 - cam.depth((Xb, Yb, 0)) * 0.01,
                   flip=bool(rng.integers(2)), cls='hatch')


def paving():
    it = B.item(-9000, 'crowd', 'paving')
    for Y in np.arange(-114.0, -54.0, 4.5):
        runs(it, 'hatch', LN((238.0, Y, 0), (150.0, Y, 0), n=4))
    for X in np.arange(238.0, 150.0, -4.5):
        runs(it, 'hatch', LN((X, -114.0, 0), (X, -54.0, 0), n=3))
    for X in np.arange(238.0, 150.0, -4.5):
        runs(it, 'hatch', LN((X, -54.0, 0), (X, 44.0, 0), n=3))
    for Y in np.arange(-54.0, 44.0, 4.5):
        runs(it, 'hatch', LN((238.0, Y, 0), (150.0, Y, 0), n=3))


sanctuary()
courts()
stoa()
antonia()
west_portico()
city()
crowd()
paving()

if __name__ == '__main__':
    out = B.build(['sanct', 'courts', 'stoa', 'bg', 'crowd'])
    print(timing(out))
    B.write(OUT, "a02-temple v2: Herod's Temple from the east portico, a few days before Passover")
