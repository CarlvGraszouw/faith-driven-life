"""a05-soldiers (38.18-48.3 s): Rome's grip on Jerusalem.  Two legionaries stand guard in the temple court below the
Antonia fortress (sentries on its walls, a red vexillum on its tower, the temple portico and sanctuary behind); an old
man and a mother with her small son pass by, glancing back at them.  Writes art-v2/A/a05-soldiers.svg"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a02a05_tools import *  # noqa
from a02a05_tools import _lines_of
import a02a05_figs as FG
import a02a05_crowd as cr

OUT = os.path.join(EP1, 'art-v2', 'A', 'a05-soldiers.svg')

# camera at eye level in the Court of the Gentiles, looking north at the portico and the Antonia beyond
CAM = dict(pos=(0.0, 0.0, 1.65), az=90.0, f=980.0, cx=800.0, cy=392.0)
cam = Cam(CAM['pos'], CAM['az'], CAM['f'], CAM['cx'], CAM['cy'])
P = cam.p
B = Board(gap=2.0)

Z_SKY, Z_SANCT, Z_ANT, Z_POR, Z_CROWD = -9000, -8000, -7000, -6000, -500

POR_Y, POR_H = 92.0, 14.0          # portico front (columns) and height to the cornice


def G(*Ps):
    return to_poly(cam.poly3(list(Ps)))


def LN(*Ps, n=1):
    return cam.line3(list(Ps), n=n)


def runs(it, cls, rr):
    for r in rr:
        it.add(cls, r)


# ----------------------------------------------------------------------------- the Antonia fortress
def antonia():
    it = B.item(Z_ANT, 'ant', 'antonia')
    Y0, Y1 = 118.0, 160.0
    X0, X1 = -170.0, -24.0
    zb, zw = 1.0, 25.0
    faces = []
    front = G((X0, Y0, zb), (X1, Y0, zb), (X1, Y0, zw), (X0, Y0, zw))
    faces.append(front)
    towers = [(-36.0, Y0 - 1.0, 15.0, 35.0)]
    tower_geo = []
    for (tx, ty, sz, ht) in towers:
        h = sz / 2
        f1 = G((tx - h, ty - h, zb), (tx + h, ty - h, zb), (tx + h, ty - h, ht), (tx - h, ty - h, ht))
        f2 = G((tx + h, ty - h, zb), (tx + h, ty + h, zb), (tx + h, ty + h, ht), (tx + h, ty - h, ht))
        tower_geo.append((f1, f2, tx, ty, sz, ht))
        faces += [f1, f2]
    occ = unary_union(faces)
    it.occlude(occ)
    # merlons along the wall top and on the towers (part of the silhouette)
    mer = []
    for x in np.arange(X0 + 10, X1 - 8, 3.2):
        mer.append(G((x, Y0, zw), (x + 1.6, Y0, zw), (x + 1.6, Y0, zw + 1.8), (x, Y0, zw + 1.8)))
    for (f1, f2, tx, ty, sz, ht) in tower_geo:
        h = sz / 2
        for x in np.arange(tx - h, tx + h - 1.0, 2.6):
            mer.append(G((x, ty - h, ht), (x + 1.4, ty - h, ht), (x + 1.4, ty - h, ht + 1.8), (x, ty - h, ht + 1.8)))
        for y in np.arange(ty - h + 1.3, ty + h - 1.0, 2.6):
            mer.append(G((tx + h, y, ht), (tx + h, y + 1.4, ht), (tx + h, y + 1.4, ht + 1.8), (tx + h, y, ht + 1.8)))
    sil = unary_union([occ] + [m.buffer(0.3) for m in mer]).buffer(0.2).buffer(-0.2)
    it.occlude(sil)
    for m in mer:
        for r in rings(m, 0.5):
            it.H(r)
    sil = occ
    # outline without its base (the base runs behind the people and would shatter into many strokes)
    base_y = P((X0, Y0, zb))[1]
    for r in rings(sil, 40.0):
        ls = LineString(r).difference(sbox(-100, base_y - 3.0, 1700, 1000))
        for ln in sorted(_lines_of(ls), key=lambda q: -plen(q)):
            if plen(ln) > 30:
                it.L(ln)
            else:
                it.H(ln)
    runs(it, 'hatch', LN((X0, Y0, zb), (X1, Y0, zb)))
    # tower edges, string courses, arrow slits, masonry
    for (f1, f2, tx, ty, sz, ht) in tower_geo:
        h = sz / 2
        runs(it, 'detail', LN((tx + h, ty - h, zb), (tx + h, ty - h, ht)))
        runs(it, 'hatch', LN((tx - h, ty - h, ht - 3.0), (tx + h, ty - h, ht - 3.0), (tx + h, ty + h, ht - 3.0)))
        for zz in np.arange(zb + 8.0, ht - 6.0, 7.0):
            runs(it, 'detail', LN((tx, ty - h, zz), (tx, ty - h, zz + 2.4)))
            runs(it, 'hatch', LN((tx + h, ty - 1.5, zz + 1.0), (tx + h, ty - 1.5, zz + 3.0)))
        it.hatch(f2, angle=80, spacing=4.2)
        it.hatch(G((tx - h, ty - h, ht - 3.2), (tx + h, ty - h, ht - 3.2), (tx + h, ty - h, ht - 0.2), (tx - h, ty - h, ht - 0.2)),
                 angle=0, spacing=1.4)
        rng = np.random.default_rng(int(abs(tx)) + 7)
        for zz in np.arange(zb + 2.6, ht - 3.0, 2.6):
            for xx in np.arange(tx - h, tx + h - 1.0, 4.0):
                if rng.random() < 0.35:
                    xo = xx + (2.0 if int(zz / 2.6) % 2 else 0.0)
                    runs(it, 'hatch', LN((xo, ty - h, zz), (min(tx + h, xo + 3.6), ty - h, zz)))
    runs(it, 'hatch', LN((X0, Y0, zw - 2.4), (X1, Y0, zw - 2.4)))
    rng = np.random.default_rng(4)
    for zz in np.arange(zb + 3.0, zw - 3.0, 2.8):
        for xx in np.arange(X0, X1, 5.0):
            if rng.random() < 0.22:
                runs(it, 'hatch', LN((xx, Y0, zz), (xx + 4.0, Y0, zz)))
    it.hatch(G((X0, Y0, zw - 3.2), (X1, Y0, zw - 3.2), (X1, Y0, zw - 0.2), (X0, Y0, zw - 0.2)), angle=0, spacing=1.4)
    it.hatch(G((X0, Y0, zb), (X1, Y0, zb), (X1, Y0, zb + 2.2), (X0, Y0, zb + 2.2)), angle=70, spacing=2.6)
    # gate with a dark arch at the foot of the great tower
    gx = -84.0
    gate = [(gx - 3.0, Y0, zb), (gx - 3.0, Y0, zb + 6.0)] + \
           [(gx + 3.0 * math.cos(a), Y0, zb + 6.0 + 3.0 * math.sin(a)) for a in np.linspace(math.pi, 0, 9)][1:] + [(gx + 3.0, Y0, zb)]
    runs(it, 'detail', cam.line3(gate))
    it.hatch(to_poly(cam.poly3(gate)), angle=80, spacing=1.6, cross=10, cross_spacing=2.0)
    # the vexillum on the great tower (red accent) and sentries on the battlements
    tx, ty, sz, ht = towers[0]
    pole_b = P((tx, ty, ht + 1.8))
    pole_t = P((tx, ty, ht + 12.0))
    vx = B.item(Z_ANT + 5, 'ant', 'vexillum')
    vx.D([pole_b, pole_t])
    cb = P((tx, ty, ht + 11.0))
    bw, bh = 34.0, 26.0
    flag = [(cb[0] - bw / 2, cb[1]), (cb[0] + bw / 2, cb[1]), (cb[0] + bw / 2, cb[1] + bh * 0.82), (cb[0] + bw * 0.3, cb[1] + bh),
            (cb[0] + bw * 0.1, cb[1] + bh * 0.84), (cb[0] - bw * 0.1, cb[1] + bh), (cb[0] - bw * 0.3, cb[1] + bh * 0.84),
            (cb[0] - bw / 2, cb[1] + bh)]
    vx.D([(cb[0] - bw / 2 - 3, cb[1]), (cb[0] + bw / 2 + 3, cb[1])])
    vx.fill(flag + [flag[0]], RUST, cls='detail')
    vx.H([(cb[0] - bw / 2 + 4, cb[1] + 5), (cb[0] + bw / 2 - 4, cb[1] + 5)])
    vx.occlude(to_poly(flag))
    for X in (-120.0, -96.0, -72.0, -48.0 + 30.0):
        sentry(X, Y0 - 0.5, zw)
    sentry(tx - 3.0, ty - sz / 2 - 0.4, ht, z=Z_ANT + 6)


def sentry(X, Y, Zf, z=None):
    """small legionary silhouette on a wall walk: helmet, shield, spear"""
    x, y = P((X, Y, Zf))
    k = 1.75 * cam.scale((X, Y, Zf)) / 100.0
    it = B.item(z if z is not None else Z_ANT + 4, 'ant', 'sentry')
    body = [(x - 4 * k, y), (x - 5 * k, y - 40 * k), (x - 8 * k, y - 62 * k), (x - 7 * k, y - 80 * k), (x - 4 * k, y - 88 * k),
            (x - 6 * k, y - 96 * k), (x - 1 * k, y - 103 * k), (x + 5 * k, y - 100 * k), (x + 9 * k, y - 95 * k), (x + 5 * k, y - 90 * k),
            (x + 8 * k, y - 80 * k), (x + 9 * k, y - 62 * k), (x + 6 * k, y - 40 * k), (x + 5 * k, y)]
    it.H(body + [body[0]])
    it.H([(x + 13 * k, y + 2 * k), (x + 13 * k, y - 128 * k)])
    shield = [(x - 14 * k, y - 30 * k), (x - 14 * k, y - 78 * k), (x - 3 * k, y - 80 * k), (x - 3 * k, y - 28 * k)]
    it.H(shield + [shield[0]])
    it.occlude(to_poly(body))


# ----------------------------------------------------------------------------- the temple portico and the sanctuary
def portico():
    it = B.item(Z_POR, 'por', 'portico')
    X0, X1 = -6.0, 260.0
    zc, ze, zr = 11.2, 13.4, 16.6
    yb = POR_Y + 11.0
    ent = G((X0, POR_Y, zc), (X1, POR_Y, zc), (X1, POR_Y, ze), (X0, POR_Y, ze))
    roof = G((X0, POR_Y, ze), (X1, POR_Y, ze), (X1, yb, zr), (X0, yb, zr))
    upper = unary_union([ent, roof])
    it.occlude(upper)
    for r in rings(upper):
        it.H(r)
    runs(it, 'hatch', LN((X0, POR_Y, zc), (X1, POR_Y, zc)))
    runs(it, 'hatch', LN((X0, POR_Y, zc + 0.7), (X1, POR_Y, zc + 0.7)))
    runs(it, 'hatch', LN((X0, POR_Y, ze - 0.5), (X1, POR_Y, ze - 0.5)))
    for x in np.arange(X0, X1, 2.8):
        runs(it, 'hatch', LN((x, POR_Y + 0.2, ze + 0.15), (x, yb, zr - 0.1)))
    cols = B.item(Z_POR + 1, 'por', 'columns')
    occs = []
    m = []
    for x in np.arange(X0 + 2.0, X1, 5.6):
        r = 0.55
        m += [(x - r, POR_Y, 0.4), (x - r, POR_Y, zc - 1.0), (x - r - 0.4, POR_Y, zc - 0.05), (x + r + 0.4, POR_Y, zc - 0.05),
              (x + r, POR_Y, zc - 1.0), (x + r, POR_Y, 0.4)]
        occs.append(G((x - r - 0.4, POR_Y, 0), (x + r + 0.4, POR_Y, 0), (x + r + 0.4, POR_Y, zc - 0.3), (x - r - 0.4, POR_Y, zc - 0.3)))
        runs(cols, 'hatch', LN((x, POR_Y, 1.0), (x, POR_Y, zc - 1.4)))
    for rr in cam.line3(m):
        cols.add('hatch', rr)
    cols.occlude(unary_union(occs))
    runs(cols, 'hatch', LN((X0, POR_Y, 0.3), (X1, POR_Y, 0.3)))
    shade = B.item(Z_POR - 1, 'por', 'shade')
    shade.hatch(G((X0, POR_Y, 0), (X1, POR_Y, 0), (X1, POR_Y, zc), (X0, POR_Y, zc)), angle=90, spacing=3.6)
    # the sanctuary beyond the portico roof, on the right: facade, portal, half-columns, cornice and gilded spikes
    sn = B.item(Z_SANCT, 'por', 'sanctuary')
    sx0, sx1, sy, zt = 70.0, 126.0, 230.0, 63.0
    fr = G((sx0, sy, 20.0), (sx1, sy, 20.0), (sx1, sy, zt), (sx0, sy, zt))
    sn.occlude(fr)
    for r in rings(fr):
        sn.H(r)
    runs(sn, 'hatch', LN((sx0, sy, zt - 3.0), (sx1, sy, zt - 3.0)))
    runs(sn, 'hatch', LN((sx0, sy, 47.0), (sx1, sy, 47.0)))
    for x in np.arange(sx0 + 1.0, sx1, 2.2):
        runs(sn, 'hatch', LN((x, sy, zt), (x, sy, zt + 1.4)))
    cx_ = (sx0 + sx1) / 2
    runs(sn, 'detail', LN((cx_ - 6.5, sy, 20.0), (cx_ - 6.5, sy, 44.0), (cx_ + 6.5, sy, 44.0), (cx_ + 6.5, sy, 20.0)))
    sn.hatch(G((cx_ - 6.5, sy, 20.0), (cx_ + 6.5, sy, 20.0), (cx_ + 6.5, sy, 44.0), (cx_ - 6.5, sy, 44.0)), angle=80, spacing=2.2)
    for u in (-17.0, -11.0, 11.0, 17.0):
        runs(sn, 'hatch', LN((cx_ + u - 1.0, sy, 20.0), (cx_ + u - 1.0, sy, 45.0)))
        runs(sn, 'hatch', LN((cx_ + u + 1.0, sy, 20.0), (cx_ + u + 1.0, sy, 45.0)))


# ----------------------------------------------------------------------------- crowd in the court
def crowd():
    rng = np.random.default_rng(9)
    placed = []
    for k in range(140):
        X = rng.uniform(-30, 160)
        Y = rng.uniform(22, POR_Y - 2)
        if any((X - a) ** 2 + (Y - b) ** 2 < 4.0 for a, b in placed):
            continue
        x, y = P((X, Y, 0))
        if not (0 < x < 1600):
            continue
        h = 1.7 * cam.scale((X, Y, 0))
        if h > 46:
            continue
        kind = ['walker', 'back', 'talker', 'jar', 'mother', 'elder', 'back', 'walker'][int(rng.integers(8))]
        cr.place(B, kind, x, y, h * rng.uniform(0.94, 1.04), Z_CROWD - cam.depth((X, Y, 0)), group='crowd',
                 flip=bool(rng.integers(2)), cls='hatch', detail_min=40)
        placed.append((X, Y))
    # a couple of legionaries posted under the portico, watching the crowd
    for X in (30.0, 110.0):
        sentry(X, POR_Y - 1.5, 0.0, z=Z_POR + 5)


def ground():
    it = B.item(-9500, 'crowd', 'ground')
    for (x0, x1, y) in [(250, 360, 742), (420, 700, 768), (930, 1090, 764), (1240, 1440, 756)]:
        reg = to_poly([(x0, y - 2), (x1, y - 2), (x1 + 8, y + 5), (x0 + 8, y + 5)])
        it.hatch(reg, angle=0, spacing=2.4)


def tax_table():
    """mid-ground: a toll-collector at his table, a man counting out the tribute coin"""
    X, Y = 0.6, 23.0
    x, y = P((X, Y, 0))
    sc = (1.72 * cam.scale((X, Y, 0))) / 360.0
    z = -cam.depth((X, Y, 0))
    FG.money_changer().place(B, x - 60 * sc, y, sc, z, group='folk', name='toll', sil_cls='detail', edge_cls='hatch',
                             inner_cls='hatch')
    FG.pilgrim_paying().place(B, x - 60 * sc + 238 * sc, y, sc, z + 0.01, group='folk', name='payer', flip=True,
                              sil_cls='detail', edge_cls='hatch', inner_cls='hatch')


def figures():
    def put(fn, x, feet_y, height, z, name, **kw):
        sc = height / 360.0
        fn().place(B, x, feet_y, sc, z, group=kw.pop('group', 'sold'), name=name, **kw)
    put(FG.legionary_b, 292, 742, 372, -6.0, 'legionary-b', sil_cls='detail')
    put(FG.legionary_a, 480, 768, 402, -5.0, 'legionary-a')
    put(FG.elder_glancing, 1000, 764, 392, -5.2, 'elder', group='folk')
    put(FG.mother_and_son, 1372, 756, 384, -5.4, 'mother-son', group='folk')


figures()
tax_table()
antonia()
portico()
crowd()
ground()

if __name__ == '__main__':
    out = B.build(['sold', 'ant', 'folk', 'por', 'crowd'])
    print(timing(out))
    B.write(OUT, "a05-soldiers v2: legionaries on guard below the Antonia; the people glance at them")
