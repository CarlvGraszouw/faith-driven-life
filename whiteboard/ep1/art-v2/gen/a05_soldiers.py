"""a05-soldiers (38.18-48.3 s): Rome's grip on Jerusalem.  Two legionaries stand guard in the temple court below the
Antonia fortress (sentries on its walls, a red vexillum on its tower, the temple portico and sanctuary behind); an old
man and a mother with her small son pass by, glancing back at them.  Writes art-v2/A/a05-soldiers.svg"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a02a05_tools import *  # noqa
import a02a05_figs as FG
import a02a05_crowd as cr

OUT = os.path.join(EP1, 'art-v2', 'A', 'a05-soldiers.svg')

# camera at eye level in the Court of the Gentiles, looking north at the portico and the Antonia beyond
CAM = dict(pos=(0.0, 0.0, 1.65), az=90.0, f=980.0, cx=800.0, cy=392.0)
cam = Cam(CAM['pos'], CAM['az'], CAM['f'], CAM['cx'], CAM['cy'])
P = cam.p
B = Board(gap=2.0)

Z_SKY, Z_SANCT, Z_ANT, Z_POR, Z_CROWD = -9000, -8000, -7000, -6000, -500

POR_Y, POR_H = 64.0, 14.0          # portico front (columns) and height to the cornice


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
    Y0, Y1 = 96.0, 140.0
    X0, X1 = -150.0, -38.0
    zb, zw = 2.0, 30.0
    faces = []
    front = G((X0, Y0, zb), (X1, Y0, zb), (X1, Y0, zw), (X0, Y0, zw))
    faces.append(front)
    towers = [(X1, Y0, 15.0, 52.0), (X0 + 4.0, Y0, 12.0, 41.0)]
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
    sil = unary_union([occ] + mer)
    it.occlude(sil)
    for r in rings(sil):
        it.L(r)
    # tower edges, string courses, arrow slits, masonry
    for (f1, f2, tx, ty, sz, ht) in tower_geo:
        h = sz / 2
        runs(it, 'detail', LN((tx + h, ty - h, zb), (tx + h, ty - h, ht)))
        runs(it, 'hatch', LN((tx - h, ty - h, ht - 3.0), (tx + h, ty - h, ht - 3.0), (tx + h, ty + h, ht - 3.0)))
        for zz in np.arange(zb + 8.0, ht - 6.0, 7.0):
            runs(it, 'detail', LN((tx, ty - h, zz), (tx, ty - h, zz + 2.4)))
            runs(it, 'hatch', LN((tx + h, ty - 1.5, zz + 1.0), (tx + h, ty - 1.5, zz + 3.0)))
        it.hatch(f2, angle=80, spacing=2.6)
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
    it.hatch(front, angle=72, spacing=6.0)
    # gate with a dark arch at the foot of the great tower
    gx = X1 - 20.0
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
    for X in (-128.0, -104.0, -80.0, -58.0):
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
    it.D(body + [body[0]])
    it.D([(x + 13 * k, y + 2 * k), (x + 13 * k, y - 128 * k)])
    shield = [(x - 14 * k, y - 30 * k), (x - 14 * k, y - 78 * k), (x - 3 * k, y - 80 * k), (x - 3 * k, y - 28 * k)]
    it.H(shield + [shield[0]])
    it.occlude(to_poly(body))


# ----------------------------------------------------------------------------- the temple portico and the sanctuary
def portico():
    it = B.item(Z_POR, 'por', 'portico')
    X0, X1 = -220.0, 260.0
    zc, ze, zr = 11.2, 13.4, 16.6
    yb = POR_Y + 11.0
    ent = G((X0, POR_Y, zc), (X1, POR_Y, zc), (X1, POR_Y, ze), (X0, POR_Y, ze))
    roof = G((X0, POR_Y, ze), (X1, POR_Y, ze), (X1, yb, zr), (X0, yb, zr))
    upper = unary_union([ent, roof])
    it.occlude(upper)
    for r in rings(upper):
        it.L(r)
    runs(it, 'detail', LN((X0, POR_Y, zc), (X1, POR_Y, zc)))
    runs(it, 'hatch', LN((X0, POR_Y, zc + 0.7), (X1, POR_Y, zc + 0.7)))
    runs(it, 'hatch', LN((X0, POR_Y, ze - 0.5), (X1, POR_Y, ze - 0.5)))
    for x in np.arange(X0, X1, 1.6):
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
    runs(cols, 'detail', LN((X0, POR_Y, 0.3), (X1, POR_Y, 0.3)))
    shade = B.item(Z_POR - 1, 'por', 'shade')
    shade.hatch(G((X0, POR_Y, 0), (X1, POR_Y, 0), (X1, POR_Y, zc), (X0, POR_Y, zc)), angle=70, spacing=3.0)
    # the sanctuary's upper storey and gilded spikes beyond the portico roof, on the right
    sn = B.item(Z_SANCT, 'por', 'sanctuary')
    sx0, sx1, sy, zt = 60.0, 116.0, 190.0, 63.0
    fr = G((sx0, sy, 20.0), (sx1, sy, 20.0), (sx1, sy, zt), (sx0, sy, zt))
    sn.occlude(fr)
    for r in rings(fr):
        sn.D(r)
    runs(sn, 'hatch', LN((sx0, sy, zt - 3.0), (sx1, sy, zt - 3.0)))
    runs(sn, 'hatch', LN((sx0, sy, zt - 4.4), (sx1, sy, zt - 4.4)))
    for x in np.arange(sx0 + 1.0, sx1, 2.0):
        runs(sn, 'hatch', LN((x, sy, zt), (x, sy, zt + 1.5)))
    cx_ = (sx0 + sx1) / 2
    runs(sn, 'hatch', LN((cx_ - 6.5, sy, 20.0), (cx_ - 6.5, sy, 50.0), (cx_ + 6.5, sy, 50.0), (cx_ + 6.5, sy, 20.0)))
    for u in (-17.0, -11.0, 11.0, 17.0):
        runs(sn, 'hatch', LN((cx_ + u, sy, 20.0), (cx_ + u, sy, 52.0)))
    sn.hatch(fr, angle=80, spacing=7.0)


# ----------------------------------------------------------------------------- crowd in the court
def crowd():
    rng = np.random.default_rng(9)
    placed = []
    for k in range(140):
        X = rng.uniform(-90, 120)
        Y = rng.uniform(16, POR_Y - 2)
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
    for X in (-60.0, 24.0, 96.0):
        sentry(X, POR_Y - 1.5, 0.0, z=Z_POR + 5)


def ground():
    it = B.item(-9500, 'crowd', 'ground')
    rng = np.random.default_rng(2)
    for Y in (4.2, 5.0, 6.0, 7.4, 9.0, 11.5):
        for X in np.arange(-9.0, 9.0, 1.2):
            if rng.random() < 0.18:
                runs(it, 'hatch', LN((X, Y, 0), (X + rng.uniform(0.3, 0.7), Y, 0)))


def figures():
    def at(xs, depth, grow=1.0):
        y = CAM['cy'] + CAM['f'] * CAM['pos'][2] / depth
        sc = grow * (1.72 * CAM['f'] / depth) / 360.0
        return y, sc
    y, sc = at(300, 5.9)
    FG.legionary_b().place(B, 300, y, sc, -5.9, group='sold', name='legionary-b')
    y, sc = at(480, 5.2)
    FG.legionary_a().place(B, 480, y, sc, -5.2, group='sold', name='legionary-a')
    y, sc = at(1000, 5.5)
    FG.elder_glancing().place(B, 990, y, sc, -5.5, group='folk', name='elder')
    y, sc = at(1350, 5.7)
    FG.mother_and_son().place(B, 1370, y, sc, -5.7, group='folk', name='mother-son')


figures()
antonia()
portico()
crowd()
ground()

if __name__ == '__main__':
    out = B.build(['sold', 'ant', 'folk', 'por', 'crowd'])
    print(timing(out))
    B.write(OUT, "a05-soldiers v2: legionaries on guard below the Antonia; the people glance at them")
