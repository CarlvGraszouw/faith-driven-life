"""Reusable figure of Jesus for Episode 1 v2 art (reference design, batch A).

    import sys; sys.path.insert(0, "<ep1>/art-v2/gen")      # this folder (also puts <ep1> on sys.path)
    from jesus import jesus, jesus_layers, jesus_anchors, HEIGHT, POSES, LEVELS

    body = jesus(x, y, scale=1.0, pose="teaching", facing="left", level="mid")  # -> "<path .../>..."

API (stable):
  x, y     ground point between his feet (art units, viewBox 1600x900).  For pose "seated" (x, y) is the
           floor point under his feet; the seat top is anchors["seat"] = (x0, x1, y_top) -- draw the
           stone step/bench yourself (he sits on its front edge, knees toward his facing side).
  scale    1.0 = 340 units tall standing (mid-shot adult); seated he is ~265 tall.
  pose     "standing" relaxed, right hand at his side, left hand gathering the mantle at the hip
           "teaching" standing, right hand raised forward with open palm (explaining)
           "coin"     standing, right hand held up high showing a denarius between thumb and finger
           "seated"   sitting on a low step, right hand teaching, left hand resting on his knee
  facing   "left" (canonical, 3/4 view, mantle over his LEFT shoulder nearest the viewer) or "right"
           (mirror image).  Prefer "left"; mirror only when the composition needs it.
  level    "full" | "mid" | "small": same design, fewer hand strokes (line+detail sub-paths).  Hatch
           (shading, hair/beard texture, the mantle colour) is self-drawn and free at every level.
           Use stroke_counts(pose, level) to see the cost.  Rough guide: small ~30, mid ~55, full ~85.
  accent   True -> mantle gets the CLOAK accent (multiply, light).  coin_wash -> light BLUE on the coin.

jesus_layers(...) -> {"line": [...], "detail": [...], "hatch": [...]} lists of <path> strings, so you can
interleave with other figures (all lines first, then details, then hatching).
jesus_anchors(x, y, scale, pose, facing) -> dict of art-coord points: head (eye-line centre), face (front
of face), hand_r, coin (cx, cy, r) for "coin", seat (x0, x1, y) for "seated", bbox, silhouette (polygon).
Clip lines you draw AFTER him and BEHIND him with  a_sketch.clip(d, [anchors["silhouette"]], keep="out").
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import a_sketch as K  # noqa: E402  (puts ep1 on sys.path)
from lib_v2 import tx, circle, f1, CLOAK, BLUE  # noqa: E402

try:
    from shapely.geometry import Polygon as _SPoly
    from shapely.ops import unary_union as _sunion
except Exception:      # shapely is optional (exact accent region / silhouette)
    _SPoly = None

HEIGHT = 340
POSES = ("standing", "teaching", "coin", "seated")
LEVELS = ("small", "mid", "full")
_LV = {"small": 0, "mid": 1, "full": 2}
HEAD_S = 0.45          # head-space (100 units tall) -> figure units
WHITE = "#ffffff"
ACCENT_OPACITY = 0.72  # on a hatch-class path (class opacity .75) -> ~0.55 effective


def _el(cls, d, fill=None, accent=False, opacity=None, evenodd=False):
    f = f' fill="{fill}"' if fill else ""
    o = f' fill-opacity="{opacity}"' if (fill and opacity) else ""
    r = ' fill-rule="evenodd"' if (fill and evenodd) else ""
    st = ' style="mix-blend-mode:multiply"' if accent else ""
    return f'  <path class="{cls}"{f}{o}{r}{st} d="{d}"/>\n'


# =============================================================== part bookkeeping
class Part:
    def __init__(self, name, z, order):
        self.name, self.z, self.order = name, z, order
        self.strokes = []
        self.occ = []           # polygons (figure units) hiding parts with lower z
        self.accent_polys = []  # polygons to colour (minus everything in front)

    def add(self, cls, d, lv="S", fill=None, clip=True):
        if d:
            self.strokes.append(dict(cls=cls, d=d, lv="SMF".index(lv), fill=fill, clip=clip))
        return self


class Fig:
    def __init__(self):
        self.parts = []
        self.coin = None

    def part(self, name, z, order):
        p = Part(name, z, order)
        self.parts.append(p)
        return p

    def render(self, s, x, y, mirror, level, accent=True):
        lv = _LV[level]
        out = {"line": [], "detail": [], "hatch": []}
        T = lambda d: tx(d, sx=(-s if mirror else s), sy=s, dx=x, dy=y)
        for p in sorted(self.parts, key=lambda q: q.order):
            front = [pg for q in self.parts if q.z > p.z for pg in q.occ]
            for st in p.strokes:
                if st["lv"] > lv:
                    continue
                d = K.clip(st["d"], front, keep="out") if (front and st["clip"]) else st["d"]
                if d:
                    out[st["cls"]].append(_el(st["cls"], T(d), st["fill"]))
            if accent and p.accent_polys:
                out["hatch"].append(_el("hatch", T(_region_path(p.accent_polys, front)), CLOAK, accent=True,
                                        opacity=ACCENT_OPACITY, evenodd=True))
        return out


def _region_path(polys, minus):
    """Closed M/L path of union(polys) - union(minus)."""
    if _SPoly is None:
        return " ".join(K.seg(*pg) + " Z" for pg in polys)
    u = _sunion([_SPoly(pg).buffer(0) for pg in polys])
    if minus:
        u = u.difference(_sunion([_SPoly(pg).buffer(0) for pg in minus if len(pg) >= 3]))
    geoms = list(u.geoms) if hasattr(u, "geoms") else [u]
    ds = []
    for g in geoms:
        if g.is_empty or g.area < 4:
            continue
        g = g.simplify(0.3)
        for ring in [g.exterior] + list(g.interiors):
            ds.append(K.seg(*list(ring.coords)[:-1]) + " Z")
    return " ".join(ds)


def HP(hx, hy, rot=0.0, s=HEAD_S):
    return lambda pts: K.xf(pts, s=s, dx=hx, dy=hy, rot=rot)


# =============================================================== head (3/4, facing left, ~35 deg)
def head(fig, hx, hy, rot=0.0, z=70, order=0, gaze=-1.0, shoulder_lock=True):
    """Head-space: 100 tall, origin on the eye line at the skull centre; top -50, chin +50."""
    P = HP(hx, hy, rot)
    sm = lambda pts: K.sm(P(pts))
    ph = fig.part("head", z, order)

    hair_out = [(-40, 87), (-45, 75), (-47.6, 57), (-48.6, 36), (-48, 14), (-46.6, -8), (-43, -26), (-36, -40),
                (-24, -50.5), (-8, -56.6), (8, -57), (24, -52.6), (37, -43), (46, -29), (51, -11), (53, 8),
                (54.6, 27), (57.6, 45), (58.4, 60), (61, 74), (60.6, 86)]
    tips = [(60.6, 86), (55.6, 81.6), (54.4, 92), (48.6, 85), (45.2, 94.6), (40.2, 86.4), (36.6, 90.6)]
    hang = [(36.6, 90.6), (33, 76), (30.6, 60), (29, 46), (27.6, 33)]
    lock_in = [(-40, 87), (-36, 88.6), (-33.6, 80), (-34.8, 66), (-37, 53), (-39, 47)]
    face = [(-38.5, -22), (-40.6, -13), (-39.8, -6.5), (-38.8, -2), (-40.2, 4.5), (-41, 10), (-42.4, 18),
            (-43, 28), (-42, 38), (-39, 48), (-33, 56), (-24, 61.6), (-13, 63), (-2, 61), (9, 56), (18, 48.5),
            (24.5, 39), (27.6, 29), (27.6, 19), (25.6, 11), (21.6, 1), (16.6, -10), (10, -21), (2, -30),
            (-8, -36), (-19, -38.6), (-27, -36.6), (-33.6, -31), (-38.5, -22)]
    head_poly = P(hair_out + tips[1:] + hang[1:] + [(18, 52), (2, 63), (-14, 66), (-30, 60)] + lock_in[::-1][:-1])
    ph.occ.append(head_poly)
    fig.head_poly = head_poly
    ph.add("line", K.chain(P(lock_in[::-1]), P(hair_out), P(tips), P(hang)), "S")
    ph.add("line", sm(face), "S")

    # ---- features (detail)
    g = gaze
    ph.add("detail", sm([(-15, -9), (-9.5, -11.6), (-3, -12.3), (3, -11), (7.6, -8.4)]), "S")          # near brow
    ph.add("detail", sm([(-25, -9.6), (-30, -11.3), (-35, -10.9), (-38.6, -8.6)]), "M")                  # far brow
    ph.add("detail", sm([(-12.4, 0.5), (-9.4, -2.1), (-5.4, -3.2), (-1.4, -2.6), (1.6, -0.6), (2.8, 0.7)]), "S")
    ph.add("detail", sm([(-35.8, 0.3), (-33.8, -1.8), (-30.6, -2.3), (-28.2, -0.3), (-27.4, 0.8)]), "S")
    for (ex, ey, r, lvl) in ((-5.6 + 1.8 * g, -0.4, 1.1, "S"), (-31.6 + 1.2 * g, -0.4, 0.9, "S")):
        (cx, cy), = P([(ex, ey)])
        ph.add("detail", circle(cx, cy, r), lvl)
    ph.add("detail", sm([(-22.4, -0.6), (-24.6, 6), (-28, 12.6), (-30.6, 17.4), (-30.6, 20.8), (-27.6, 22.8),
                         (-23.8, 22.8)]), "S")                                                             # nose
    ph.add("detail", sm([(-19.6, 17.8), (-17.4, 20.4), (-19, 22.8), (-21.6, 23.2)]), "F")                # nostril
    ph.add("detail", sm([(-35, 30.8), (-30, 29.8), (-24.6, 29.6), (-19, 29.8), (-14.6, 30.6), (-11.6, 32)]), "S")
    ph.add("detail", sm([(-26, 34.4), (-22, 35.4), (-18.2, 34.6)]), "M")                                   # lower lip
    ph.add("detail", sm([(-10.6, 2.2), (-5.6, 3.3), (-0.6, 2.4)]), "F")                                   # lower lid
    ph.add("detail", sm([(-19, -38.6), (-8, -47), (6, -53), (20, -51)]), "F")                            # parting
    if shoulder_lock:
        ph.add("detail", sm([(30.6, 58), (31, 72), (29, 86), (26, 98), (22.6, 104)]), "F")             # lock in front

    # ---- hair texture (hatch, free): flowing waved strands
    near_front = [(-14, -40), (-2, -34), (8, -24), (15, -10), (20, 4), (25, 18), (29, 34), (32, 52), (35, 68), (38, 86)]
    near_back = [(-4, -55), (14, -53.6), (30, -45.6), (42, -32), (48.6, -14), (51.2, 6), (52.6, 26), (55.6, 46),
                 (56.6, 62), (59.6, 82)]
    for c in K.between(near_front, near_back, 9, n_pts=18):
        c = [(px + 1.3 * math.sin(i * 0.9), py) for i, (px, py) in enumerate(c)]
        ph.add("hatch", K.sm(P(c)), "S")
    far_a = [(-22, -46), (-34, -38), (-41, -24), (-44, -4), (-45, 20), (-45, 44), (-43, 66), (-40, 84)]
    far_b = [(-14, -54), (-30, -46), (-42, -32), (-46.6, -10), (-47.6, 16), (-47.6, 44), (-46, 68), (-43, 85)]
    for c in K.between(far_a, far_b, 2, n_pts=14):
        ph.add("hatch", K.sm(P(c)), "S")
    ph.add("hatch", K.sm(P([(-36, 52), (-36.6, 66), (-35, 80)])), "S")
    ph.add("hatch", K.hatch(P([(36, -38), (48, -22), (52, 0), (54, 30), (57, 58), (59.6, 82), (52, 84), (46, 60),
                                (42, 30), (40, 0)]), angle=74 + rot, spacing=2.4, seed=3), "S")
    # beard texture following growth, darker under the jaw
    for c in K.between([(25, 12), (26.6, 26), (22, 40), (12, 51), (-2, 57), (-14, 59)],
                       [(-8, 33), (-10, 40), (-14, 47), (-20, 53), (-26, 57), (-30, 57.6)], 6, n_pts=10):
        ph.add("hatch", K.sm(P(c)), "S")
    ph.add("hatch", K.hatch(P([(2, 40), (20, 30), (26, 30), (22, 44), (8, 55), (-10, 61), (-24, 61), (-8, 52)]),
                            angle=-56 + rot, spacing=1.8, seed=5), "S")
    ph.add("hatch", K.hatch(P([(-41.6, 30), (-38, 36), (-34, 47), (-27, 55), (-35, 54), (-40.6, 44)]),
                            angle=-70 + rot, spacing=2.0, seed=6), "S")
    ph.add("hatch", K.sm(P([(-31, 27.6), (-25, 26.4), (-19, 26.8)])), "S")                    # moustache top
    ph.add("hatch", K.sm(P([(-25.6, 39), (-22, 40), (-18.4, 39.2)])), "S")                    # under lip
    # face modelling: near eye socket, side of nose, near cheek, neck under the beard
    ph.add("hatch", K.hatch(P([(-14, -6), (-4, -8.4), (5, -6.4), (4, -3), (-6, -4.6), (-14, -3.4)]),
                            angle=-22 + rot, spacing=1.7, seed=7), "S")
    ph.add("hatch", K.hatch(P([(-20.6, -1), (-18.6, 6), (-18, 15.6), (-21.6, 17.6), (-24, 10), (-23.6, 2)]),
                            angle=70 + rot, spacing=1.8, seed=8), "S")
    ph.add("hatch", K.hatch(P([(10, 6), (18, 2), (22.6, 10), (16, 16), (8, 15)]), angle=62 + rot, spacing=2.0,
                            seed=9), "S")
    ph.add("hatch", K.hatch(P([(-13, 63), (16, 50), (18, 66), (-12, 78)]), angle=-30 + rot, spacing=2.0,
                            seed=10), "S")
    return ph


# =============================================================== hands (local: wrist at 0,0)
def _T(cx, cy, s, rot):
    return lambda pts: K.xf(pts, s=s, dx=cx, dy=cy, rot=rot)


def _sp(pts):
    """smoothed closed outline as a polygon (for occluders)."""
    return K.poly(K.sm(pts, closed=True), 1.0)


def hand_open(part, cx, cy, rot, s=1.0):
    """Right hand open, palm up/forward, fingers along -x, thumb on the -y side.  -> [polygons]"""
    T = _T(cx, cy, s, rot)
    o = [(0, 4.8), (-6, 6.4), (-12, 7.4), (-16.4, 7.8), (-22, 7.8), (-26.6, 6.6), (-27.8, 4.8), (-26.8, 3.4),
         (-30.4, 2.6), (-31.8, 0.8), (-30.8, -0.8), (-33.4, -1.8), (-34.4, -3.6), (-33.2, -5.2), (-31.2, -6.4),
         (-31.6, -8.2), (-29.8, -9.4), (-24, -9), (-17.6, -7.8), (-14.8, -10.2), (-14.4, -14.6), (-15.8, -18.4),
         (-13.6, -19.8), (-10.4, -17.2), (-7.4, -12), (-3.6, -6.8), (0, -4.8)]
    part.add("line", K.sm(T(o)), "S", fill=WHITE, clip=False)
    for f, lv in (([(-26.8, 3.4), (-18.4, 3.6)], "M"), ([(-30.8, -0.8), (-19.4, -0.6)], "M"),
                  ([(-33.2, -5.2), (-19.8, -4.8)], "M"), ([(-17.6, -7.8), (-12.4, -6.4), (-8, -7.2)], "F")):
        part.add("detail", K.sm(T(f)), lv)
    part.add("hatch", K.hatch(T([(-2, 3.6), (-14, 6.4), (-17.6, 2.6), (-12, -1.6), (-4, -1)]), angle=rot + 15,
                              spacing=1.6, seed=21), "S")
    return [_sp(T(o))]


def hand_relaxed(part, cx, cy, rot, s=1.0, lv_out="S"):
    """Hand hanging relaxed, back of the hand seen, thumb in front (toward -x); wrist (0,0), fingers +y."""
    T = _T(cx, cy, s, rot)
    o = [(4.6, 0), (5.8, 7.6), (6.4, 14.6), (6, 20.6), (5, 25.6), (3.2, 29.6), (0.4, 32), (-2.6, 31.6),
         (-4.8, 29.2), (-6.2, 25.6), (-6.8, 21), (-6.6, 15.4), (-5.6, 9), (-4.6, 0)]
    thumb = [(-5.2, 6.4), (-8.6, 10.6), (-10.2, 15.8), (-9.8, 20.2), (-7.6, 21.4), (-6.4, 18.4)]
    part.add("line", K.sm(T(o)), lv_out, fill=WHITE, clip=False)
    part.add("detail", K.sm(T(thumb)), "S", fill=WHITE, clip=False)
    for f, lv in (([(-6.2, 19.4), (-1, 21.2), (5.4, 20)], "M"), ([(-3.6, 21.4), (-2.6, 29.6)], "F"),
                  ([(-0.4, 21.6), (0.4, 31.4)], "M"), ([(2.8, 21.2), (3, 29.2)], "F")):
        part.add("detail", K.sm(T(f)), lv)
    part.add("hatch", K.hatch(T([(1, 3), (5.4, 4), (6.2, 18), (3, 20), (1.4, 12)]), angle=rot + 80, spacing=1.6,
                              seed=23), "S")
    return [_sp(T(o)), _sp(T(thumb + [(-5.6, 9)]))]


def hand_coin(part, cx, cy, rot, s=1.0):
    """Right hand raised, back of the hand to the viewer, fingers curled, thumb and index finger
    pinching the coin above.  Wrist (0,0), knuckles toward -y.  -> ([polygons], coin centre)"""
    T = _T(cx, cy, s, rot)
    o = [(5.4, 0), (6.8, -8), (7.4, -16), (6.6, -21.4), (3.8, -25), (0.4, -27.4), (-1.6, -31.6), (-2.8, -35.6),
         (-5.4, -36.2), (-6.6, -33), (-8.4, -28), (-9.8, -21.4), (-9.2, -14), (-7.4, -7), (-5.6, 0)]
    part.add("line", K.sm(T(o)), "S", fill=WHITE, clip=False)
    for f, lv in (([(6.8, -15), (2.4, -18.4), (-1.6, -17.8)], "M"), ([(6.4, -21), (1.6, -23), (-1.8, -22.4)], "M"),
                  ([(-8.4, -28), (-5.4, -28.6), (-2.6, -28.6)], "F")):
        part.add("detail", K.sm(T(f)), lv)
    part.add("hatch", K.hatch(T([(3, -2), (6.4, -9), (6, -17), (2, -13), (1.4, -4)]), angle=rot + 80,
                              spacing=1.6, seed=22), "S")
    return [_sp(T(o))], T([(-4.2, -43.0)])[0]


def hand_on_knee(part, cx, cy, rot, s=1.0):
    """Left hand resting palm-down over a knee; wrist (0,0), fingers toward -x, tips curling down."""
    T = _T(cx, cy, s, rot)
    o = [(0, -5.4), (-7, -6.8), (-14, -7.4), (-20, -6.8), (-25, -4.8), (-28.6, -1.2), (-30.2, 3.6), (-29.6, 8.2),
         (-27, 9.6), (-25, 7), (-22, 4.4), (-15, 4.6), (-8, 5), (0, 5.4)]
    thumb = [(-13.6, 4.6), (-18.6, 6.4), (-22.6, 9.4), (-21, 11.2), (-16, 9.8), (-10.6, 7.4)]
    part.add("line", K.sm(T(o)), "S", fill=WHITE, clip=False)
    part.add("detail", K.sm(T(thumb)), "M", fill=WHITE, clip=False)
    for f, lv in (([(-20.6, -6.6), (-25.6, -2.4), (-27.2, 3)], "M"), ([(-16.6, -7.2), (-22.4, -2.4), (-24.4, 4)], "F"),
                  ([(-24.6, -5), (-28, 1), (-28.4, 6.6)], "F")):
        part.add("detail", K.sm(T(f)), lv)
    part.add("hatch", K.hatch(T([(-2, -4.6), (-14, -6), (-18, -3), (-12, 1), (-2, 1)]), angle=rot - 10, spacing=1.6,
                              seed=24), "S")
    return [_sp(T(o)), _sp(T(thumb))]


# =============================================================== feet (sandals)
def foot(part, ax, ay, toe, lv_strap="M"):
    """Sandalled foot from the ankle (ax, ay) to the toe point toe=(tx, ty) (figure units), pointing left."""
    tx0, ty0 = toe
    L = math.hypot(tx0 - ax, ty0 - ay)
    ang = math.degrees(math.atan2(ty0 - ay, tx0 - ax)) - 180.0
    T = lambda pts: K.xf(pts, s=L / 28.0, dx=ax, dy=ay, rot=ang)
    # foot: ankle front -> instep -> toes -> sole -> heel -> ankle back (local: ankle (0,0), toes at -28)
    o = [(-2.6, -6.6), (-9, -3.8), (-17, -0.6), (-23.6, 1.4), (-27.4, 3), (-28.4, 5.2), (-26.6, 6.6),
         (-18, 6.8), (-8, 7), (2.6, 6.8), (6.4, 4.6), (6.6, -0.6), (5, -6)]
    sole = [(7.4, 5.8), (6.6, 8.8), (-6, 9.2), (-20, 9), (-28.6, 8.2), (-29.6, 6.4)]
    part.add("line", K.sm(T(o)), "S", fill=WHITE)
    part.add("detail", K.sm(T(sole)), "S")
    part.add("detail", K.sm(T([(-15.6, -1.2), (-16.6, 2.6), (-15.6, 6.6)])), lv_strap)            # toe strap
    part.add("detail", K.sm(T([(1.6, -6.2), (-0.6, 0.4), (0.4, 6.6)])), "F")                      # ankle strap
    part.add("detail", K.sm(T([(-25.2, 2.6), (-24.6, 6.2)])), "F")                                # big toe
    part.occ.append(_sp(T(o + [(6.6, 8.8), (-29.6, 6.4)])))
    return T(o)


def tassel(part, x, y, ang=90, n=3, length=12, lv="M"):
    a = math.radians(ang)
    ex, ey = x + length * math.cos(a), y + length * math.sin(a)
    part.add("detail", K.sm([(x - 1.6, y + 0.8), (x, y + 3.4), (x + 1.6, y + 0.8)]), lv)
    d = []
    for k in range(n):
        off = (k - (n - 1) / 2) * 1.9
        d.append(K.sm([(x + off * 0.3, y + 3.2), (x + off * 0.6 + 0.6 * math.cos(a), y + 3 + (length - 3) * 0.5),
                       (ex + off, ey)]))
    part.add("detail", d[1], lv)
    part.add("hatch", d[0] + " " + d[2], "S")


def limb(part, a_pts, b_pts, cls_a="line", cls_b="detail", lv="S"):
    """two contour strokes of a limb (outer as cls_a, inner as cls_b) + occluder polygon."""
    part.add(cls_a, K.sm(a_pts), lv)
    part.add(cls_b, K.sm(b_pts), lv)
    part.occ.append(a_pts + b_pts[::-1])


# =============================================================== standing figures
def build_standing(pose):
    f = Fig()
    hrot = {"standing": -3.0, "teaching": -4.0, "coin": 2.0}[pose]
    head(f, -7.0, -316.0, rot=hrot, z=70, order=0)

    # ---------------------------------------------------------- tunic (cream)
    tun = f.part("tunic", 10, 1)
    chest = [(-37, -257), (-39, -246), (-38, -232), (-36, -219), (-37.4, -213), (-36.6, -206)]
    skirt_l = [(-36.6, -206), (-38.4, -190), (-40.2, -172), (-41.6, -150), (-43, -126), (-44.6, -106),
               (-46.6, -92), (-46.4, -74), (-46.6, -52), (-47.2, -30), (-48.4, -14)]
    hem = [(-48.4, -14), (-42, -11), (-35, -13.4), (-27, -11), (-18, -12.8), (-9, -10.6), (0, -12), (10, -10.4),
           (20, -12.2), (30, -10.8), (38, -12.6), (43.4, -14.6)]
    skirt_r = [(43.4, -14.6), (43.4, -36), (44, -58), (45, -80), (46.6, -100)]
    tun.add("line", K.chain(chest, skirt_l, hem, skirt_r), "S")
    tun.add("detail", K.sm([(-36.2, -214.6), (-28, -213.4), (-20, -214)]), "M")              # sash
    tun.add("detail", K.sm([(-36.6, -207), (-28, -205.8), (-20, -206.4)]), "F")
    tun.add("detail", K.sm([(-14.6, -287), (-11, -281.6), (-4, -281)]), "F")                 # neckline
    for fl, lv in (([(-31, -100), (-34, -70), (-36.4, -40), (-37, -15)], "M"),
                   ([(-12, -112), (-13, -76), (-13.6, -44), (-12.6, -12)], "M"),
                   ([(12, -86), (13, -60), (14, -36), (14.6, -11)], "F"),
                   ([(-22, -116), (-23.6, -80), (-24.8, -46), (-24.4, -12)], "F")):
        tun.add("detail", K.sm(fl), lv)
    tun.add("hatch", K.hatch([(28, -78), (45, -86), (43.6, -40), (43, -14), (32, -12), (31, -40)], angle=78,
                             spacing=2.4, seed=31), "S")
    tun.add("hatch", K.hatch([(-31, -100), (-25, -112), (-26.4, -60), (-27, -13), (-35, -13), (-35.4, -50)],
                             angle=76, spacing=2.6, seed=32), "S")
    tun.add("hatch", K.hatch([(-14, -110), (-10, -112), (-11.4, -60), (-10.6, -12), (-15, -12), (-15.4, -60)],
                             angle=80, spacing=2.0, seed=33), "S")
    tun.add("hatch", K.hatch([(-37.6, -256), (-30, -262), (-26, -248), (-30, -230), (-36, -219), (-38, -232)],
                             angle=60, spacing=2.4, seed=34), "S")
    tun.occ.append(chest + skirt_l[1:] + hem[1:] + skirt_r[1:] + [(46, -250), (30, -283), (-14, -288), (-36, -276)])

    # ---------------------------------------------------------- mantle (accent region, hatch-class fill)
    man = f.part("mantle", 40, 2)
    top = [(4, -288), (14, -291), (27, -289), (37, -282), (43.6, -270)]
    back = [(43.6, -270), (47.6, -252), (50.4, -228), (52.4, -212), (52.2, -196), (51.6, -170), (51.4, -140),
            (50.6, -112), (49.6, -88), (47, -68)]
    zig = [(47, -68), (42.4, -75.4), (37, -68.6), (31.4, -77), (25.4, -69.4), (19.6, -78), (14, -72)]
    hemd = [(14, -72), (10.4, -86), (4.6, -100), (-3.6, -114), (-13.6, -128), (-24.6, -141), (-33.6, -152.6),
            (-40.6, -160)]
    far = [(-40.6, -160), (-39.6, -172), (-37.6, -186), (-35.4, -197)]
    diag = [(-35.4, -197), (-29, -210), (-21, -226), (-13, -243), (-6, -259), (-1, -273), (2, -283), (4, -288)]
    outline = top + back[1:] + zig[1:] + hemd[1:] + far[1:] + diag[1:]
    man.add("line", K.chain(top, back, zig, hemd, far, diag), "S")
    man.occ.append(outline)
    man.accent_polys.append(outline)
    # the left forearm carried under the cloth (elbow bump at the back, cloth over the forearm)
    man.add("detail", K.sm([(51.6, -214), (40, -207.4), (28, -202.6), (17.4, -200.6)]), "S")
    man.add("detail", K.sm([(48, -201), (36, -196), (25, -193.6)]), "F")
    # rolled upper edge, shoulder folds, hip swag (pulled from the far hip to the forearm), hanging folds
    man.add("detail", K.sm([(-32.6, -193), (-26.6, -206), (-18.6, -222), (-10.8, -239), (-4, -255), (0.6, -268)]), "M")
    man.add("detail", K.sm([(26, -288), (33, -270), (37.6, -246), (40.4, -222)]), "M")
    man.add("detail", K.sm([(14, -280), (8.6, -264), (0.6, -242), (-8, -224), (-16, -208), (-22, -196)]), "F")
    man.add("detail", K.sm([(-37.6, -178), (-25, -176.6), (-11, -178.6), (2, -186), (10, -194)]), "S")
    man.add("detail", K.sm([(-38.6, -166), (-25, -160), (-11, -161), (1, -167), (10, -176), (17, -190)]), "M")
    man.add("detail", K.sm([(-30, -150), (-18, -146.6), (-6, -148.6), (6, -156)]), "F")
    man.add("detail", K.sm([(22, -194), (20, -164), (21.6, -130), (20, -100), (22, -80)]), "S")    # hanging
    man.add("detail", K.sm([(33, -196), (33.6, -156), (34, -116), (34.6, -74)]), "M")
    man.add("detail", K.sm([(43, -200), (44.6, -160), (44.4, -120), (42.6, -76)]), "F")
    tassel(man, 14, -72, ang=97, length=12, lv="M")
    tassel(man, 47, -68, ang=86, length=12, lv="M")
    man.add("hatch", K.hatch([(44, -268), (48, -252), (51, -214), (51.6, -170), (51, -120), (49.6, -88), (47, -70),
                              (45.4, -74), (46.6, -120), (46.6, -170), (45.6, -214), (42, -250)], angle=84,
                             spacing=2.4, seed=41), "S")
    man.add("hatch", K.hatch([(-33.6, -152.6), (-24.6, -141), (-13.6, -128), (-3.6, -114), (4.6, -100), (2, -112),
                              (-8, -128), (-20, -142), (-30, -156)], angle=-36, spacing=2.0, seed=42), "S")
    man.add("hatch", K.hatch([(-35, -194), (-28, -207), (-20, -223), (-12, -239), (-5, -254), (-9, -240),
                              (-17, -222), (-25, -205), (-31, -192)], angle=-62, spacing=1.9, seed=43), "S")
    man.add("hatch", K.hatch([(-37.6, -175), (-24, -172), (-10, -174), (3, -181), (2, -175), (-10, -168),
                              (-24, -166), (-38, -170)], angle=8, spacing=1.8, seed=44), "S")
    man.add("hatch", K.hatch([(24, -192), (30, -195), (31, -150), (31.6, -110), (32.6, -76), (26.4, -70),
                              (25, -110), (24, -150)], angle=84, spacing=2.2, seed=45), "S")
    man.add("hatch", K.hatch([(20, -200), (30, -201.6), (42, -205.6), (50, -210), (48, -201), (36, -196),
                              (25, -194)], angle=10, spacing=1.7, seed=46), "S")

    # ---------------------------------------------------------- left hand emerging from the cloth
    lh = f.part("hand_l", 80, 4)
    lh.occ.extend(hand_relaxed(lh, 17.0, -199.6, rot=56, s=0.94))

    # ---------------------------------------------------------- right (far) arm per pose
    arm = f.part("arm_r", 60, 3)
    shoulder = [(-14, -286.6), (-24, -284.8), (-31, -281.4), (-36.6, -275.4)]
    if pose == "standing":
        sleeve = shoulder + [(-40.4, -266), (-43, -250), (-45.2, -234), (-47.2, -222.4)]
        hemp = [(-47.2, -222.4), (-42, -218.8), (-36.4, -220.6)]
        arm.add("line", K.chain(sleeve, hemp), "S")
        arm.occ.append(sleeve[3:] + hemp[1:] + [(-36.6, -240), (-37.4, -256)])
        limb(arm, [(-46, -220), (-47.6, -201), (-48.2, -184), (-47.8, -172)],
             [(-37.4, -220.4), (-38.8, -201), (-40, -185), (-40.4, -172)])
        arm.occ.extend(hand_relaxed(arm, -44.0, -172.6, rot=4))
        arm.add("detail", K.sm([(-40.6, -262), (-42, -246), (-41.4, -232)]), "F")
        arm.add("hatch", K.hatch([(-46, -218), (-47.6, -198), (-48, -176), (-44, -176), (-43.4, -216)],
                                 angle=80, spacing=2.0, seed=51), "S")
        arm.add("hatch", K.hatch([(-38, -252), (-41.6, -246), (-44.6, -230), (-46, -224), (-41, -222), (-37.6, -234)],
                                 angle=70, spacing=2.0, seed=52), "S")
    elif pose == "teaching":
        sleeve = shoulder + [(-44, -266), (-51, -252), (-56, -238), (-59, -227.6)]
        hemp = [(-59, -227.6), (-55, -222), (-48.6, -220.6), (-44.6, -223.8)]
        under = [(-44.6, -223.8), (-43, -234), (-40.4, -246), (-38, -254)]
        arm.add("line", K.chain(sleeve, hemp, under), "S")
        arm.occ.append(sleeve[3:] + hemp[1:] + under[1:])
        limb(arm, [(-57, -234.6), (-65, -240.4), (-73.4, -244.4), (-81.6, -248.4)],
             [(-50, -222.4), (-60.4, -230.4), (-70.6, -236.6), (-80, -240.6)])
        arm.occ.extend(hand_open(arm, -81.0, -244.4, rot=-16, s=0.94))
        arm.add("detail", K.sm([(-44, -264), (-49.4, -252), (-52.6, -238)]), "F")
        arm.add("hatch", K.hatch([(-44.6, -224), (-43, -234), (-40.4, -246), (-47, -238), (-53, -226)], angle=40,
                                 spacing=1.8, seed=53), "S")
        arm.add("hatch", K.hatch([(-52, -224), (-62, -231), (-74, -238.6), (-74, -242), (-62, -235.6), (-55, -229)],
                                 angle=30, spacing=1.6, seed=54), "S")
    else:  # coin: upper arm raised forward from the shoulder joint, sleeve slid back to the elbow
        sleeve = shoulder[:3] + [(-37.6, -282), (-46, -287.6), (-56, -292.6), (-66, -296.6), (-72.6, -298.6)]
        hemp = [(-72.6, -298.6), (-74.4, -291.4), (-72.4, -284.6), (-67.4, -281.4)]
        under = [(-67.4, -281.4), (-58, -276.6), (-48, -268), (-40.6, -258)]
        arm.add("line", K.chain(sleeve, hemp, under), "S")
        arm.occ.append(sleeve[2:] + hemp[1:] + under[1:])
        limb(arm, [(-76.4, -294.4), (-77.8, -310), (-78.2, -326), (-77.8, -341)],
             [(-65.6, -290.6), (-66.6, -307), (-67.6, -324), (-68.4, -341)])
        polys, coin_c = hand_coin(arm, -72.8, -341.6, rot=-2)
        arm.occ.extend(polys)
        f.coin = coin_c
        arm.add("detail", K.sm([(-44, -285.6), (-53, -289), (-61, -290.6)]), "F")
        arm.add("hatch", K.hatch([(-67, -290), (-74, -293), (-76.4, -310), (-77, -338), (-72.6, -338), (-71, -310)],
                                 angle=84, spacing=1.8, seed=55), "S")
        arm.add("hatch", K.hatch([(-41, -259), (-50, -270), (-60, -279), (-67, -282), (-58, -284), (-48, -276)],
                                 angle=40, spacing=1.8, seed=56), "S")

    # ---------------------------------------------------------- feet
    ft = f.part("feet", 5, 5)
    foot(ft, -32.0, -9.0, (-58.0, -3.0))
    foot(ft, 4.0, -7.6, (-21.0, 2.2))
    sh = f.part("shadow", 0, 9)
    sh.add("hatch", K.cat(K.seg((-68, 8), (-30, 8)), K.seg((-24, 9.6), (34, 9.6)), K.seg((-56, 11.4), (26, 11.6)),
                          K.seg((-38, 13.8), (10, 13.8))), "S", clip=False)
    return f


# =============================================================== seated
SEAT_Y = -88.0


def build_seated():
    f = Fig()
    head(f, -12.0, -243.0, rot=-5.0, z=70, order=0)

    tun = f.part("tunic", 10, 1)
    chest = [(-40.6, -187), (-42.6, -174), (-42, -160), (-40, -148), (-38.4, -140)]
    tun.add("line", K.sm(chest), "S")
    # near shin (front) -> hem -> back of the near calf ; far shin front -> its hem
    shin = [(-59.6, -64), (-61.6, -48), (-62.6, -32), (-63.6, -15)]
    hem = [(-63.6, -15), (-58, -12.6), (-52, -14.4), (-46.6, -13)]
    calf = [(-46.6, -13), (-46.2, -34), (-45.4, -58), (-44.4, -76), (-46.6, -94)]
    tun.add("line", K.chain(shin, hem, calf), "S")
    fshin = [(-78.4, -92), (-79.6, -70), (-80.4, -46), (-81, -24), (-81.4, -16)]
    tun.add("line", K.chain(fshin, [(-81.4, -16), (-75, -14), (-68.6, -15.6), (-64.4, -15)]), "S")
    tun.add("detail", K.sm([(-41.6, -150), (-33, -148.8), (-26, -149.4)]), "M")
    tun.add("detail", K.sm([(-40.6, -143.6), (-32, -142.4), (-25, -143)]), "F")
    for fl, lv in (([(-54, -56), (-54.6, -36), (-55.4, -14)], "M"), ([(-72, -60), (-72.6, -38), (-72.8, -16)], "F")):
        tun.add("detail", K.sm(fl), lv)
    tun.add("hatch", K.hatch([(-52, -60), (-45, -60), (-46, -34), (-47, -14), (-52, -14), (-52.4, -36)], angle=80,
                             spacing=2.2, seed=61), "S")
    tun.add("hatch", K.hatch([(-78, -90), (-70, -80), (-66, -60), (-66, -16), (-80.6, -16), (-80, -50)], angle=82,
                             spacing=2.6, seed=62), "S")
    tun.add("hatch", K.hatch([(-40.6, -187), (-34, -194), (-30, -178), (-34, -160), (-40, -148), (-42.4, -162)],
                             angle=60, spacing=2.4, seed=63), "S")
    tun.occ.append(chest + [(-30, -120), (-46.6, -94)] + calf[::-1][1:] + hem[::-1][1:] + shin[::-1][1:]
                   + [(-60, -80), (-80, -100), (-60, -214), (-20, -214)])
    tun.occ.append(fshin + [(-64.4, -15), (-60, -92)])

    man = f.part("mantle", 40, 2)
    top = [(-2, -211), (10, -214), (24, -211), (33, -203)]
    back = [(33, -203), (38, -190), (41, -168), (42, -140), (42, -112), (41, -96), (38, -90)]
    under = [(38, -90), (20, -89.6), (0, -90.4), (-20, -91.6), (-36, -93.4), (-46.6, -95)]
    drape = [(-46.6, -95), (-49.6, -86), (-52.4, -76), (-55.6, -66), (-59.6, -58.4)]
    front = [(-59.6, -58.4), (-63.4, -64.6), (-68.6, -74), (-73.6, -86), (-77.6, -98), (-79.4, -108), (-76.6, -116)]
    lap = [(-76.6, -116), (-66, -121), (-54, -125), (-44, -130.4), (-38.6, -138)]
    diag = [(-38.6, -138), (-33, -148), (-26, -162), (-19.6, -176), (-13.6, -190), (-8.6, -202), (-4.4, -208), (-2, -211)]
    outline = top + back[1:] + under[1:] + drape[1:] + front[1:] + lap[1:] + diag[1:]
    man.add("line", K.chain(top, back, under, drape, front, lap, diag), "S")
    man.occ.append(outline)
    man.accent_polys.append(outline)
    man.add("detail", K.sm([(-36.2, -142.6), (-30.6, -152.6), (-24, -166), (-18, -180), (-13, -194), (-9.4, -204)]), "M")
    man.add("detail", K.sm([(22, -208), (29, -190), (32.6, -166), (33.6, -136), (33, -110), (31, -94)]), "S")
    man.add("detail", K.sm([(-74.6, -104), (-62, -108.6), (-50, -110.6), (-38, -109)]), "S")      # over the knees
    man.add("detail", K.sm([(-30, -102), (-12, -106.6), (6, -106.6), (22, -102)]), "M")           # lap sag
    man.add("detail", K.sm([(-56, -100), (-60, -88), (-63, -76)]), "F")
    man.add("detail", K.sm([(-68, -112), (-71, -100), (-71.6, -88)]), "F")
    man.add("detail", K.sm([(8, -206), (13, -186), (15.4, -160), (16, -130), (14.6, -104)]), "F")
    tassel(man, -59.6, -58.4, ang=96, length=11, lv="M")
    tassel(man, 38, -90, ang=88, length=11, lv="F")
    man.add("hatch", K.hatch([(30, -205), (36, -194), (40, -152), (41, -106), (38, -92), (33, -96), (33.6, -140),
                              (31, -180)], angle=82, spacing=2.4, seed=64), "S")
    man.add("hatch", K.hatch([(-46, -96), (-30, -94.6), (-4, -93.4), (20, -91.6), (20, -97), (-4, -99.6), (-30, -100.6),
                              (-46, -101)], angle=6, spacing=1.9, seed=65), "S")
    man.add("hatch", K.hatch([(-36.6, -140), (-31, -150), (-25, -164), (-21, -162), (-27, -148), (-33, -138)], angle=-50,
                             spacing=1.8, seed=66), "S")
    man.add("hatch", K.hatch([(-47.6, -94), (-52, -80), (-56.6, -64), (-60, -61), (-62.6, -76), (-56, -94)], angle=70,
                             spacing=2.0, seed=67), "S")

    # left forearm lying along the thigh, hand over the near knee
    lh = f.part("hand_l", 80, 4)
    limb(lh, [(14, -137), (-2, -131), (-18, -126), (-30.6, -124.2)], [(10, -125.6), (-4, -121.4), (-18, -117.4), (-29.4, -116)],
         cls_a="line", cls_b="detail")
    lh.occ.extend(hand_on_knee(lh, -30.6, -120.2, rot=12))
    lh.add("hatch", K.hatch([(10, -126), (-4, -122), (-18, -118), (-28, -117), (-18, -121), (-4, -125)], angle=8,
                            spacing=1.6, seed=69), "S")

    arm = f.part("arm_r", 60, 3)
    shoulder = [(-21, -210.6), (-29, -208.6), (-36, -204.6), (-41.6, -198.4)]
    sleeve = shoulder + [(-48.4, -189), (-53.6, -176), (-57, -163.4), (-58.6, -154)]
    hemp = [(-58.6, -154), (-54, -149.6), (-48, -150.4), (-45.4, -154)]
    under_a = [(-45.4, -154), (-44.6, -164), (-43.6, -176)]
    arm.add("line", K.chain(sleeve, hemp, under_a), "S")
    arm.occ.append(sleeve[3:] + hemp[1:] + under_a[1:])
    limb(arm, [(-57, -162), (-65.6, -169.6), (-74, -175.6), (-82, -180)],
         [(-50.4, -151.6), (-60.4, -160), (-70.4, -167.6), (-80.4, -172.6)])
    arm.occ.extend(hand_open(arm, -81.4, -176.4, rot=-22, s=0.94))
    arm.add("hatch", K.hatch([(-52, -152), (-62, -160), (-76, -170), (-76, -174), (-62, -166), (-55, -160)], angle=30,
                             spacing=1.6, seed=68), "S")

    ft = f.part("feet", 5, 5)
    foot(ft, -76.0, -12.0, (-101.0, -5.4))
    foot(ft, -50.6, -9.0, (-77.4, 1.4))
    sh = f.part("shadow", 0, 9)
    sh.add("hatch", K.cat(K.seg((-108, 7.4), (-70, 7.4)), K.seg((-82, 9.6), (-30, 9.6)), K.seg((-96, 11.8), (-44, 11.8))),
           "S", clip=False)
    return f


def build(pose):
    return build_seated() if pose == "seated" else build_standing(pose)


# =============================================================== anchors / public API
_ANCH_LOCAL = {
    "standing": dict(head=(-7, -316), face=(-24, -316), hand_r=(-45, -152)),
    "teaching": dict(head=(-7, -316), face=(-24, -316), hand_r=(-100, -250)),
    "coin": dict(head=(-7, -316), face=(-24, -316), hand_r=(-74, -360)),
    "seated": dict(head=(-12, -243), face=(-29, -243), hand_r=(-100, -184), seat=(-30, 46, SEAT_Y)),
}
COIN_R = 7.0


def _place(pts, x, y, s, mirror):
    return [((-px if mirror else px) * s + x, py * s + y) for px, py in pts]


def _silhouette_local(f):
    polys = [pg for part in f.parts for pg in part.occ if len(pg) >= 3]
    if _SPoly is not None:
        u = _sunion([_SPoly(pg).buffer(1.2) for pg in polys]).buffer(1.0).buffer(-1.6)
        if u.geom_type == "MultiPolygon":
            u = max(u.geoms, key=lambda g: g.area)
        return list(u.simplify(0.6).exterior.coords)
    return [p for pg in polys for p in pg]


def jesus_anchors(x, y, scale=1.0, pose="standing", facing="left"):
    mirror = facing == "right"
    f = build(pose)
    a = {}
    for k, v in _ANCH_LOCAL[pose].items():
        if k == "seat":
            x0, x1 = sorted(((-v[0] if mirror else v[0]) * scale + x, (-v[1] if mirror else v[1]) * scale + x))
            a[k] = (x0, x1, v[2] * scale + y)
        else:
            a[k] = _place([v], x, y, scale, mirror)[0]
    if f.coin:
        (cx, cy), = _place([f.coin], x, y, scale, mirror)
        a["coin"] = (cx, cy, COIN_R * scale)
    sil = _place(_silhouette_local(f), x, y, scale, mirror)
    a["silhouette"] = sil
    xs = [p[0] for p in sil]; ys = [p[1] for p in sil]
    a["bbox"] = (min(xs), min(ys), max(xs), max(ys))
    return a


def jesus_layers(x, y, scale=1.0, pose="standing", facing="left", level="full", accent=True, coin_wash=False):
    if pose not in POSES:
        raise ValueError(f"pose must be one of {POSES}")
    if level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS}")
    f = build(pose)
    out = f.render(scale, x, y, facing == "right", level, accent)
    if f.coin:
        (cx, cy), = _place([f.coin], x, y, scale, facing == "right")
        r = COIN_R * scale
        out["line"].append(_el("line", circle(cx, cy, r), BLUE if coin_wash else WHITE, accent=coin_wash,
                               opacity=0.6 if coin_wash else None))
        prof = K.sm([(cx - 0.05 * r, cy - 0.52 * r), (cx + 0.24 * r, cy - 0.3 * r), (cx + 0.32 * r, cy - 0.02 * r),
                     (cx + 0.2 * r, cy + 0.22 * r), (cx + 0.04 * r, cy + 0.44 * r)])
        out["hatch"].append(_el("hatch", circle(cx, cy, r * 0.76) + " " + prof))
    return out


def jesus(x, y, scale=1.0, pose="standing", facing="left", level="full", accent=True, coin_wash=False):
    lay = jesus_layers(x, y, scale, pose, facing, level, accent, coin_wash)
    return "".join(lay["line"] + lay["detail"] + lay["hatch"])


def stroke_counts(pose="standing", level="full"):
    """Hand strokes (sub-paths) per class, as the engine counts them."""
    lay = jesus_layers(0, 0, 1.0, pose, "left", level)
    return {k: sum(el.count(" M ") + el.count('d="M') for el in v) for k, v in lay.items()}


if __name__ == "__main__":
    from lib_v2 import svg
    body = ""
    for i, pose in enumerate(POSES):
        body += jesus(200 + i * 400, 770, 1.6, pose)
    out = os.path.join(os.path.dirname(os.path.dirname(HERE)), "preview", "jesus-sheet.svg")
    open(out, "w").write(svg(body, "jesus.py contact sheet (full level)"))
    print("wrote", out)
    for pose in POSES:
        print(pose, {lv: stroke_counts(pose, lv) for lv in LEVELS})
