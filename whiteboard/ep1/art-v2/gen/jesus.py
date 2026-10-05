"""Reusable figure of Jesus for Episode 1 v2 art (reference design, batch A).  API FROZEN.

    import sys; sys.path.insert(0, "<ep1>/art-v2/gen")      # this folder (also puts <ep1> on sys.path)
    from jesus import jesus, jesus_layers, jesus_anchors, stroke_counts, HEIGHT, POSES, LEVELS

    body = jesus(x, y, scale=1.0, pose="teaching", facing="left", level="mid")  # -> "<path .../>..."

API (stable):
  x, y     ground point between his feet (art units, viewBox 1600x900).  For pose "seated" (x, y) is the
           floor point under his feet; the seat top is anchors["seat"] = (x0, x1, y_top) -- draw the
           stone step/bench yourself (he sits on its front edge, knees toward his facing side), e.g. with
           stone_step(x, y, scale, facing) -> (line_d, detail_d, hatch_d).
  scale    1.0 = 340 units tall standing (mid-shot adult); seated he is ~265 tall.
  pose     "standing" relaxed, right arm hanging, left hand holding the mantle's edge at his chest
           "teaching" standing, right hand raised forward with open palm (explaining), head inclined
           "coin"     standing, right hand held up high showing a denarius between thumb and finger
           "seated"   sitting on a low step, right hand teaching, left hand resting on his knee
  facing   "left" (canonical, 3/4 view, mantle over his LEFT shoulder nearest the viewer) or "right"
           (mirror image).  Prefer "left"; mirror only when the composition needs it.
  level    "full" | "mid" | "small": same design, fewer hand strokes (line+detail sub-paths).  Hatch
           (shading, hair/beard texture, the mantle colour) is self-drawn and free at every level.
           stroke_counts(pose, level) gives the cost.
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
from hands_data import HANDS  # noqa: E402

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
SEAT_Y = -88.0
COIN_R = 7.0


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
        u = u.difference(_sunion([_SPoly(pg).buffer(0) for pg in minus if len(pg) >= 3]).buffer(0.6))
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
def head(fig, hx, hy, rot=0.0, z=70, order=0, gaze=-1.0):
    """Head-space: 100 tall, origin on the eye line at the skull centre; top -50, chin +50.
    Centre-parted dark hair in soft waves to the shoulders (one lock falls in front of the far
    shoulder), full short beard with moustache."""
    P = HP(hx, hy, rot)
    sm = lambda pts: K.sm(P(pts))
    ph = fig.part("head", z, order)

    lock_in = [(-40.2, 50), (-38.2, 60), (-36, 72), (-34.6, 84), (-35.6, 94), (-38.8, 99)]
    hair_sil = [(-38.8, 99), (-43.8, 88), (-46.8, 72), (-48.4, 57), (-47.4, 43), (-48.8, 28), (-48.4, 10),
                (-46.6, -12), (-42.6, -29), (-35, -42.4), (-23.6, -51.4), (-11, -55.6), (-4.6, -54.2), (3.6, -57.6),
                (18, -56.2), (31.6, -48.8), (43, -36), (49.6, -18), (52.4, 2), (54.4, 19), (57.6, 34), (56.4, 49),
                (59.4, 65), (61.6, 81), (58.8, 88)]
    tips = [(58.8, 88), (55.4, 84), (54.8, 93.4), (49.6, 86.8), (46.2, 95), (41.2, 87.8), (37.6, 92)]
    hang = [(37.6, 92), (33.6, 76), (30.6, 60), (28.6, 44), (27, 32), (26.6, 24)]
    face_far = [(-36.6, -25.6), (-39.4, -16), (-40.6, -10), (-39.4, -4), (-38.8, 0), (-40.4, 5), (-41.4, 11),
                (-42, 16.6)]
    beard = [(-42, 16.6), (-43.4, 24), (-43.8, 33), (-42.4, 42), (-39.6, 50), (-35, 56.6), (-29.6, 60.6),
             (-25, 63.6), (-19.4, 65.6), (-13.4, 64.6), (-8, 63.4), (-2, 61), (5, 57.8), (11.4, 53), (18.6, 45.4),
             (23.8, 36), (26.6, 26.6), (26.6, 17), (24.6, 8.6)]
    hairline = [(24.6, 8.6), (22.2, -2), (17.4, -13.6), (10.4, -24.6), (1.4, -32.8), (-8.6, -37.4), (-14.6, -38.8),
                (-19, -41.2), (-23, -38.8), (-28, -36.6), (-32.6, -32.2), (-36.6, -25.6)]
    head_poly = P(lock_in + hair_sil[1:] + tips[1:] + hang[1:] + [(26.6, 24), (26.6, 17), (24.6, 8.6)]
                  + beard[::-1][3:] + [(-40.2, 50)])
    ph.occ.append(K.poly(K.sm(head_poly, closed=True), 1.0))
    fig.head_poly = head_poly
    ph.add("line", K.chain(P(lock_in), P(hair_sil), P(tips), P(hang)), "S")
    ph.add("line", K.chain(P(face_far), P(beard)), "S")
    ph.add("detail", sm(hairline), "S")

    # ---- features
    g = gaze
    ph.add("detail", sm([(-15.4, -9.4), (-9.6, -12), (-3, -12.6), (3.4, -11.2), (7.8, -8.6)]), "S")     # near brow
    ph.add("detail", sm([(-25.4, -10), (-30.2, -11.6), (-35, -11), (-38.6, -8.8)]), "M")                # far brow
    ph.add("detail", sm([(-12.6, 0.4), (-9.4, -2.2), (-5.4, -3.2), (-1.4, -2.6), (1.6, -0.6), (2.8, 0.6)]), "S")
    ph.add("detail", sm([(-35.8, 0.2), (-33.8, -1.8), (-30.6, -2.3), (-28.2, -0.3), (-27.4, 0.8)]), "S")
    for (ex, ey, r) in ((-5.6 + 1.8 * g, -0.4, 1.1), (-31.6 + 1.2 * g, -0.4, 0.9)):
        (cx, cy), = P([(ex, ey)])
        ph.add("detail", circle(cx, cy, r), "S")
    ph.add("detail", sm([(-22.4, -0.6), (-24.6, 6), (-28, 12.6), (-30.6, 17.4), (-30.6, 20.8), (-27.6, 22.8),
                         (-23.8, 22.8)]), "S")                                                             # nose
    ph.add("detail", sm([(-19.6, 17.8), (-17.4, 20.4), (-19, 22.8), (-21.6, 23.2)]), "F")                # nostril
    ph.add("detail", sm([(-37, 35.4), (-34.8, 30.8), (-30.4, 27.8), (-25.4, 26.6), (-20, 27), (-14.6, 29.4),
                         (-11, 34.4)]), "S")                                                               # moustache
    ph.add("detail", sm([(-28.6, 34.6), (-23.4, 35.8), (-18, 34.8)]), "M")                                # lower lip
    ph.add("detail", sm([(-19, -41.2), (-11, -48), (-1, -53.4), (10, -55.4)]), "M")                       # parting
    for pts, lv in (([(21.6, 27), (20, 35), (16, 42)], "M"), ([(5, 45), (2, 52), (-1.6, 58)], "M"),
                    ([(-23, 49), (-23.6, 56), (-22, 62)], "M"), ([(-34, 45), (-35, 51)], "F"),
                    ([(12, 40), (9.6, 47)], "F")):
        ph.add("detail", sm(pts), lv)                                                                      # beard
    for pts in ([(-12, -46), (2, -47), (18, -42), (32, -30), (40, -12), (44, 8)],
                [(41, 18), (46, 34), (45, 48), (49, 64), (50, 80)]):
        ph.add("detail", sm(pts), "F")                                                                     # hair waves
    ph.add("detail", sm([(-10.6, 2.2), (-5.6, 3.3), (-0.6, 2.4)]), "F")                                   # lower lid

    # ---- hair texture (hatch, free): waved strands
    near_front = [(-14, -40), (-2, -34), (8, -24), (15, -10), (20, 4), (25, 18), (29, 34), (32, 52), (35, 68),
                  (38, 86)]
    near_back = [(-4, -55), (14, -53.6), (30, -45.6), (42, -32), (48.6, -14), (51.4, 6), (53.2, 22), (56, 38),
                 (55.4, 52), (59.2, 82)]
    for c in K.between(near_front, near_back, 10, n_pts=18):
        c = [(px + 1.4 * math.sin(i * 0.95), py) for i, (px, py) in enumerate(c)]
        ph.add("hatch", K.sm(P(c)), "S")
    far_a = [(-22, -46), (-34, -38), (-41, -24), (-44, -4), (-45, 20), (-44.6, 44), (-42.6, 66), (-39.6, 88)]
    far_b = [(-14, -54), (-30, -46), (-42, -32), (-46.6, -10), (-47.6, 16), (-47.2, 44), (-45.8, 68), (-42.6, 90)]
    for c in K.between(far_a, far_b, 3, n_pts=14):
        ph.add("hatch", K.sm(P(c)), "S")
    ph.add("hatch", K.hatch(P([(36, -38), (48, -22), (52, 0), (54, 30), (57, 58), (59.6, 82), (52, 84), (46, 60),
                                (42, 30), (40, 0)]), angle=74 + rot, spacing=2.2, seed=3), "S")
    ph.add("hatch", K.hatch(P([(-46, -12), (-42, -28), (-38, -24), (-40, 0), (-41.4, 30), (-40, 50), (-44, 50),
                                (-45.4, 20)]), angle=80 + rot, spacing=2.0, seed=13), "S")
    # beard tone: growth strokes + darker under the jaw and on the cheek, moustache
    for c in K.between([(25, 12), (26.6, 26), (22, 40), (12, 51), (-2, 58), (-14, 61)],
                       [(-8, 33), (-10, 41), (-14, 48), (-20, 54), (-26, 58), (-30, 58)], 7, n_pts=10):
        ph.add("hatch", K.sm(P(c)), "S")
    ph.add("hatch", K.hatch(P([(2, 38), (20, 28), (26, 30), (22, 44), (8, 55), (-10, 62), (-24, 63), (-8, 52)]),
                            angle=-56 + rot, spacing=1.6, seed=5), "S")
    ph.add("hatch", K.hatch(P([(-42.4, 22), (-38, 30), (-34, 44), (-27, 56), (-35, 56), (-41, 46), (-43, 34)]),
                            angle=-70 + rot, spacing=1.8, seed=6), "S")
    ph.add("hatch", K.hatch(P([(24, 9), (16, 14), (6, 19.4), (-4, 23.4), (-12, 28), (-8, 31), (4, 25), (16, 19),
                                (25, 14)]), angle=-75 + rot, spacing=1.7, seed=11), "S")
    ph.add("hatch", K.hatch(P([(-35, 31), (-30, 28.6), (-25, 27.6), (-20, 28), (-15, 30.6), (-20, 31.4), (-28, 31)]),
                            angle=80 + rot, spacing=1.5, seed=12), "S")
    ph.add("hatch", K.sm(P([(-25.6, 39), (-22, 40), (-18.4, 39.2)])), "S")                    # under lip
    # face modelling: near eye socket, side of nose, near cheek, neck under the beard
    ph.add("hatch", K.hatch(P([(-14, -6), (-4, -8.4), (5, -6.4), (4, -3), (-6, -4.6), (-14, -3.4)]),
                            angle=-22 + rot, spacing=1.7, seed=7), "S")
    ph.add("hatch", K.hatch(P([(-20.6, -1), (-18.6, 6), (-18, 15.6), (-21.6, 17.6), (-24, 10), (-23.6, 2)]),
                            angle=70 + rot, spacing=1.8, seed=8), "S")
    ph.add("hatch", K.hatch(P([(10, 4), (18, 0), (22.6, 8), (16, 13), (8, 12)]), angle=62 + rot, spacing=2.0,
                            seed=9), "S")
    ph.add("hatch", K.hatch(P([(-14, 64), (16, 50), (18, 70), (-12, 80)]), angle=-30 + rot, spacing=2.0,
                            seed=10), "S")
    return ph


# =============================================================== hands (rigged, baked in hands_data.py)
def rig_hand(part, name, cx, cy, rot, s=1.0, flip=False, lv_inner=("M", "M", "F", "F", "F", "F", "F"), flipx=False):
    """Place a baked hand: wrist at (cx, cy).  flip mirrors the hand across its own x axis (y -> -y),
    flipx across its y axis (x -> -x).  -> (occluder polygon, transform)"""
    h = HANDS[name]

    def T(pts):
        if flip:
            pts = [(px, -py) for px, py in pts]
        if flipx:
            pts = [(-px, py) for px, py in pts]
        return K.xf(pts, s=s, dx=cx, dy=cy, rot=rot)
    o = T(h["outline"])
    part.add("line", K.seg(*o) + " Z", "S", fill=WHITE, clip=False)
    for i, pl in enumerate(sorted(h["inner"], key=lambda q: -sum(math.dist(a, b) for a, b in zip(q, q[1:])))):
        part.add("detail", K.seg(*T(pl)), lv_inner[min(i, len(lv_inner) - 1)], clip=False)
    part.occ.append(o)
    return o, T


# =============================================================== feet (sandals)
def _sp(pts):
    return K.poly(K.sm(pts, closed=True), 1.0)


def foot(part, ax, ay, toe, lv_strap="M"):
    """Sandalled foot from the ankle (ax, ay) to the toe point toe=(tx, ty) (figure units), pointing left."""
    tx0, ty0 = toe
    L = math.hypot(tx0 - ax, ty0 - ay)
    ang = math.degrees(math.atan2(ty0 - ay, tx0 - ax)) - 180.0
    T = lambda pts: K.xf(pts, s=L / 28.0, dx=ax, dy=ay, rot=ang)
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
    """Contrapposto: weight on his left (near) leg -> near hip up, near shoulder down; free (far) knee
    forward.  Mantle: over the left shoulder, down the back, diagonally across the chest to the right
    hip, round the hips; its hem slants down to the near shin; the left hand holds its rolled edge."""
    f = Fig()
    hx, hy, hrot = {"standing": (-7.0, -316.0, -3.0), "teaching": (-8.6, -315.0, -8.0),
                    "coin": (-7.0, -316.0, 2.0)}[pose]
    head(f, hx, hy, rot=hrot, z=70, order=0)

    # ---------------------------------------------------------- tunic (cream)
    tun = f.part("tunic", 10, 1)
    chest = [(-37.6, -259), (-39.6, -247), (-38.6, -233), (-36.6, -219), (-37.8, -212.6), (-36.8, -205.4)]
    skirt_l = [(-36.8, -205.4), (-38.8, -190), (-40.8, -172), (-42.8, -150), (-44.8, -128), (-47.2, -110),
               (-49.4, -96), (-49, -80), (-48.4, -60), (-48.8, -38), (-49.8, -14)]
    hem = [(-49.8, -14), (-43, -10.6), (-35, -13.2), (-27, -10.8), (-18, -12.6), (-9, -10.6), (0, -12), (10, -10.4),
           (20, -12.2), (30, -10.8), (38, -12.8), (43.4, -15)]
    skirt_r = [(43.4, -15), (43.4, -36), (44, -58), (45, -80), (46.6, -100)]
    tun.add("line", K.chain(chest, skirt_l, hem, skirt_r), "S")
    tun.add("detail", K.sm([(-37.4, -213.6), (-29, -214.6), (-20, -216.4)]), "M")            # sash (tilted)
    tun.add("detail", K.sm([(-36.8, -206), (-28.6, -207), (-19.6, -208.8)]), "F")
    tun.add("detail", K.sm([(-14.6, -288), (-11, -282.6), (-4, -282)]), "F")                 # neckline
    for fl, lv in (([(-40, -104), (-37.4, -76), (-36.4, -44), (-37, -14)], "M"),             # from the free knee
                   ([(-12, -112), (-13, -76), (-13.6, -44), (-12.6, -12)], "M"),
                   ([(12, -86), (13, -60), (14, -36), (14.6, -11)], "F"),
                   ([(-24, -118), (-25, -84), (-25.6, -48), (-25, -12)], "F"),
                   ([(-46, -94), (-42, -88), (-38.6, -86)], "F")):
        tun.add("detail", K.sm(fl), lv)
    tun.add("hatch", K.hatch([(28, -78), (45, -86), (43.6, -40), (43, -14), (32, -12), (31, -40)], angle=78,
                             spacing=2.4, seed=31), "S")
    tun.add("hatch", K.hatch([(-36, -96), (-28, -112), (-28, -60), (-28.6, -13), (-36, -13), (-36, -50)],
                             angle=76, spacing=2.6, seed=32), "S")
    tun.add("hatch", K.hatch([(-14, -110), (-10, -112), (-11.4, -60), (-10.6, -12), (-15, -12), (-15.4, -60)],
                             angle=80, spacing=2.0, seed=33), "S")
    tun.add("hatch", K.hatch([(-38, -258), (-30, -263), (-26, -248), (-30, -230), (-36.6, -219), (-38.6, -233)],
                             angle=60, spacing=2.4, seed=34), "S")
    tun.add("hatch", K.hatch([(-48.6, -92), (-44, -96), (-40, -80), (-42, -50), (-48.4, -50), (-48.8, -76)],
                             angle=74, spacing=2.6, seed=35), "S")
    tun.occ.append(chest + skirt_l[1:] + hem[1:] + skirt_r[1:] + [(46, -250), (30, -283), (-14, -289), (-37, -278)])

    # ---------------------------------------------------------- mantle (accent region, hatch-class fill)
    man = f.part("mantle", 40, 2)
    top = [(4, -288.6), (14, -289.6), (27, -286.6), (37, -279), (43.6, -266.6)]
    back = [(43.6, -266.6), (47.6, -249), (50.4, -226), (52.4, -210), (52.2, -194), (51.6, -168), (51.4, -138),
            (50.6, -110), (49.6, -88), (47.4, -70)]
    hemb = [(47.4, -70), (41.4, -73.2), (34, -72.4), (27, -75), (20, -74), (14, -72.6)]
    hemd = [(14, -72.6), (10.4, -86), (4.6, -100), (-3.6, -114), (-13.6, -128), (-24.6, -141), (-33.6, -152.6),
            (-40.6, -160)]
    far = [(-40.6, -160), (-39.6, -172), (-37.6, -186), (-35.4, -197)]
    diag = [(-35.4, -197), (-29, -210), (-21, -226), (-13, -243), (-6, -259), (-1, -273), (2, -283), (4, -288.6)]
    outline = top + back[1:] + hemb[1:] + hemd[1:] + far[1:] + diag[1:]
    man.add("line", K.chain(top, back, hemb, hemd, far, diag), "S")
    man.occ.append(outline)
    man.accent_polys.append(outline)
    # rolled upper edge, shoulder folds, hip folds (tension from the far hip), hanging folds to the hem
    man.add("detail", K.sm([(-32.6, -193), (-26.6, -206), (-18.6, -222), (-10.8, -239), (-4, -255), (0.6, -268)]), "S")
    man.add("detail", K.sm([(26, -286), (33, -268), (37.6, -244), (40.4, -220)]), "M")
    man.add("detail", K.sm([(14, -279), (8.6, -263), (0.6, -241), (-8, -223), (-16, -207), (-22, -195)]), "F")
    man.add("detail", K.sm([(-37.6, -178), (-25, -177.6), (-11, -181), (2, -189), (12, -199), (20, -212)]), "S")
    man.add("detail", K.sm([(-38.6, -166), (-25, -161), (-11, -163), (2, -170), (14, -180), (24, -192)]), "M")
    man.add("detail", K.sm([(-30, -150), (-18, -146.6), (-6, -149), (6, -156), (16, -164)]), "F")
    man.add("detail", K.sm([(26, -196), (25, -160), (25.6, -124), (24.4, -96), (22.4, -76)]), "S")    # hanging
    man.add("detail", K.sm([(36, -212), (36.6, -170), (37, -126), (36, -90), (35, -74)]), "M")
    man.add("detail", K.sm([(45, -230), (46.6, -180), (46.4, -130), (44.6, -86)]), "F")
    man.add("detail", K.sm([(14.6, -170), (12, -130), (9, -100), (13, -80)]), "F")
    tassel(man, 14, -72.6, ang=97, length=12, lv="M")
    tassel(man, 47.4, -70, ang=86, length=12, lv="M")
    man.add("hatch", K.hatch([(44, -266), (48, -249), (51, -212), (51.6, -168), (51, -120), (49.6, -88), (47.4, -72),
                              (45.4, -74), (46.6, -120), (46.6, -170), (45.6, -212), (42, -248)], angle=84,
                             spacing=2.4, seed=41), "S")
    man.add("hatch", K.hatch([(-33.6, -152.6), (-24.6, -141), (-13.6, -128), (-3.6, -114), (4.6, -100), (2, -112),
                              (-8, -128), (-20, -142), (-30, -156)], angle=-36, spacing=2.0, seed=42), "S")
    man.add("hatch", K.hatch([(-35, -194), (-28, -207), (-20, -223), (-12, -239), (-5, -254), (-9, -240),
                              (-17, -222), (-25, -205), (-31, -192)], angle=-62, spacing=1.9, seed=43), "S")
    man.add("hatch", K.hatch([(-37.6, -175), (-24, -173), (-10, -177), (3, -185), (2, -178), (-10, -170),
                              (-24, -168), (-38, -170)], angle=8, spacing=1.8, seed=44), "S")
    man.add("hatch", K.hatch([(28, -196), (34, -206), (35, -150), (35.6, -110), (34.6, -76), (28.4, -76),
                              (28, -110), (28, -150)], angle=84, spacing=2.2, seed=45), "S")
    man.add("hatch", K.hatch([(16, -74), (27, -76.4), (34, -74), (41.4, -74.6), (47, -72), (41, -80), (30, -82),
                              (20, -80)], angle=4, spacing=1.6, seed=46), "S")

    # ---------------------------------------------------------- left hand holding the mantle's rolled edge
    lh = f.part("hand_l", 80, 4)
    rig_hand(lh, "hook", -0.6, -246.6, rot=-66, s=1.05, flipx=True)
    # the cloth bunches above the hand: folds pulled toward the grip from the shoulder
    man.add("detail", K.sm([(0, -259), (6, -268), (13, -276), (22, -283)]), "M")
    man.add("detail", K.sm([(5, -255), (12, -262), (20, -270), (30, -278)]), "F")
    man.add("hatch", K.hatch([(1, -259), (7, -268), (15, -277), (24, -283), (30, -279), (18, -268), (8, -257)],
                             angle=-40, spacing=1.8, seed=47), "S")

    # ---------------------------------------------------------- right (far) arm per pose
    arm = f.part("arm_r", 60, 3)
    shoulder = [(-14, -287.6), (-24, -286), (-31, -282.6), (-36.6, -276.6)]
    if pose == "standing":
        # hangs relaxed with a slight elbow bend, fingers curled
        sleeve = shoulder + [(-40.4, -267), (-42.6, -251), (-44, -235), (-45, -223.4)]
        hemp = [(-45, -223.4), (-39.6, -219.4), (-34.4, -221.4)]
        arm.add("line", K.chain(sleeve, hemp), "S")
        arm.occ.append(sleeve[3:] + hemp[1:] + [(-35.6, -240), (-37.4, -257)])
        limb(arm, [(-44.2, -221), (-46.6, -203), (-49, -186), (-50.6, -172)],
             [(-35.4, -221.2), (-38.4, -203), (-41.4, -187), (-43.4, -173)])
        rig_hand(arm, "relaxed", -46.8, -172.6, rot=10, s=1.05)
        arm.add("detail", K.sm([(-40.6, -262), (-41.8, -246), (-41, -232)]), "F")
        arm.add("hatch", K.hatch([(-44.4, -219), (-47, -200), (-49.8, -176), (-45.6, -176), (-42, -219)],
                                 angle=78, spacing=2.0, seed=51), "S")
        arm.add("hatch", K.hatch([(-38, -254), (-41.6, -246), (-43.6, -232), (-44.4, -225), (-39, -222), (-36.6, -236)],
                                 angle=70, spacing=2.0, seed=52), "S")
    elif pose == "teaching":
        sleeve = shoulder + [(-44, -267), (-51, -253), (-56, -239), (-59, -228.6)]
        hemp = [(-59, -228.6), (-55, -223), (-48.6, -221.6), (-44.6, -224.8)]
        under = [(-44.6, -224.8), (-43, -235), (-40.4, -247), (-38, -255)]
        arm.add("line", K.chain(sleeve, hemp, under), "S")
        arm.occ.append(sleeve[3:] + hemp[1:] + under[1:])
        limb(arm, [(-57, -235.6), (-65, -241.4), (-73.4, -245.4), (-81.6, -249.4)],
             [(-50, -223.4), (-60.4, -231.4), (-70.6, -237.6), (-80, -241.6)])
        rig_hand(arm, "open", -81.6, -245.6, rot=-74, s=1.05)
        arm.add("detail", K.sm([(-44, -265), (-49.4, -253), (-52.6, -239)]), "F")
        arm.add("hatch", K.hatch([(-44.6, -225), (-43, -235), (-40.4, -247), (-47, -239), (-53, -227)], angle=40,
                                 spacing=1.8, seed=53), "S")
        arm.add("hatch", K.hatch([(-52, -225), (-62, -232), (-74, -239.6), (-74, -243), (-62, -236.6), (-55, -230)],
                                 angle=30, spacing=1.6, seed=54), "S")
    else:  # coin: upper arm raised forward from the shoulder joint, sleeve slid back to the elbow
        sleeve = shoulder[:3] + [(-37.6, -283), (-46, -288.6), (-56, -293.6), (-66, -297.6), (-72.6, -299.6)]
        hemp = [(-72.6, -299.6), (-74.4, -292.4), (-72.4, -285.6), (-67.4, -282.4)]
        under = [(-67.4, -282.4), (-58, -277.6), (-48, -269), (-40.6, -259)]
        arm.add("line", K.chain(sleeve, hemp, under), "S")
        arm.occ.append(sleeve[2:] + hemp[1:] + under[1:])
        limb(arm, [(-76.4, -295.4), (-77.8, -311), (-78.2, -327), (-77.8, -342)],
             [(-65.6, -291.6), (-66.6, -308), (-67.6, -325), (-68.4, -342)])
        o, T = rig_hand(arm, "coin", -72.8, -342.4, rot=0, s=1.05)
        px, py = T([HANDS["coin"]["pinch"]])[0]
        f.coin = (px, py - COIN_R * 0.92)
        arm.add("detail", K.sm([(-44, -286.6), (-53, -290), (-61, -291.6)]), "F")
        arm.add("hatch", K.hatch([(-67, -291), (-74, -294), (-76.4, -311), (-77, -339), (-72.6, -339), (-71, -311)],
                                 angle=84, spacing=1.8, seed=55), "S")
        arm.add("hatch", K.hatch([(-41, -260), (-50, -271), (-60, -280), (-67, -283), (-58, -285), (-48, -277)],
                                 angle=40, spacing=1.8, seed=56), "S")

    # ---------------------------------------------------------- feet: free foot forward, weight foot under him
    ft = f.part("feet", 5, 5)
    foot(ft, -35.0, -9.4, (-61.0, -2.6))
    foot(ft, 4.0, -7.6, (-21.0, 2.2))
    sh = f.part("shadow", 0, 9)
    sh.add("hatch", K.cat(K.seg((-70, 8), (-30, 8)), K.seg((-24, 9.6), (34, 9.6)), K.seg((-58, 11.4), (26, 11.6)),
                          K.seg((-40, 13.8), (10, 13.8))), "S", clip=False)
    return f


# =============================================================== seated
def build_seated():
    """On a low step (top 88 above the floor): thighs forward to the knees, shins vertical, feet flat;
    robe hanging from the knees with a valley between the legs; mantle over the lap and the near knee."""
    f = Fig()
    head(f, -12.0, -244.0, rot=-6.0, z=70, order=0)

    tun = f.part("tunic", 10, 1)
    chest = [(-40.6, -188), (-42.6, -175), (-42, -161), (-40, -149), (-38.4, -141)]
    tun.add("line", K.sm(chest), "S")
    # near leg: knee -> shin front (vertical) -> hem -> back of the calf ; far leg shin front -> hem
    near = [(-60, -98), (-61.6, -80), (-61.8, -56), (-61.6, -34), (-62, -15)]
    hem = [(-62, -15), (-56, -12.8), (-50, -14.2), (-44.6, -12.6)]
    calf = [(-44.6, -12.6), (-44.8, -34), (-44.4, -58), (-43, -76), (-41, -92)]
    tun.add("line", K.chain(near, hem, calf), "S")
    farl = [(-71.6, -104), (-74.6, -92), (-75.6, -70), (-76, -46), (-76.4, -24), (-77, -16)]
    tun.add("line", K.chain(farl, [(-77, -16), (-72, -13.6), (-66.6, -15.2), (-62, -15)]), "S")
    # robe between the knees: a sagging valley, hanging folds
    tun.add("detail", K.sm([(-72.6, -100), (-69, -90), (-65.6, -86), (-62.6, -88)]), "S")
    tun.add("detail", K.sm([(-67.6, -86), (-68.4, -60), (-68.6, -36), (-69, -16)]), "M")
    tun.add("detail", K.sm([(-41.6, -150.6), (-33, -149.4), (-26, -150)]), "M")
    tun.add("detail", K.sm([(-40.6, -144.2), (-32, -143), (-25, -143.6)]), "F")
    for fl, lv in (([(-53, -86), (-53.4, -56), (-53.2, -34), (-53.6, -14)], "M"),
                   ([(-49, -80), (-48.6, -50), (-49, -14)], "F")):
        tun.add("detail", K.sm(fl), lv)
    tun.add("hatch", K.hatch([(-52, -84), (-44, -88), (-44.4, -40), (-45, -14), (-52, -14), (-52.6, -40)], angle=80,
                             spacing=2.2, seed=61), "S")
    tun.add("hatch", K.hatch([(-70, -96), (-63, -88), (-62.6, -60), (-62.6, -16), (-75, -16), (-74.6, -60)],
                             angle=82, spacing=2.4, seed=62), "S")
    tun.add("hatch", K.hatch([(-40.6, -188), (-34, -195), (-30, -179), (-34, -161), (-40, -149), (-42.4, -163)],
                             angle=60, spacing=2.4, seed=63), "S")
    tun.occ.append(chest + [(-30, -120), (-41, -92)] + calf[::-1][1:] + hem[::-1][1:] + near[::-1][1:]
                   + [(-60, -98), (-70, -104), (-60, -215), (-20, -215)])
    tun.occ.append(farl + [(-62, -15), (-60, -98)])

    man = f.part("mantle", 40, 2)
    top = [(-2, -212), (10, -215), (24, -212), (33, -204)]
    back = [(33, -204), (38, -191), (41, -169), (42, -141), (42, -113), (41, -97), (38, -91)]
    under = [(38, -91), (20, -90.6), (0, -91.4), (-16, -93), (-30, -95.6), (-40, -98.6)]
    drape = [(-40, -98.6), (-44, -90), (-48, -80), (-52.6, -71), (-57.4, -64.6)]
    front = [(-57.4, -64.6), (-60.6, -70.6), (-62.6, -82), (-63.6, -94), (-64.2, -104), (-62, -111), (-56, -115.6)]
    lap = [(-56, -115.6), (-48, -119), (-42, -124.4), (-38.6, -132)]
    diag = [(-38.6, -132), (-33, -144), (-26, -159), (-19.6, -174), (-13.6, -189), (-8.6, -201), (-4.4, -208), (-2, -212)]
    outline = top + back[1:] + under[1:] + drape[1:] + front[1:] + lap[1:] + diag[1:]
    man.add("line", K.chain(top, back, under, drape, front, lap, diag), "S")
    man.occ.append(outline)
    man.accent_polys.append(outline)
    man.add("detail", K.sm([(-36.2, -137), (-30.6, -149), (-24, -164), (-18, -179), (-13, -193), (-9.4, -204)]), "S")
    man.add("detail", K.sm([(22, -209), (29, -191), (32.6, -167), (33.6, -137), (33, -111), (31, -95)]), "S")
    man.add("detail", K.sm([(-34, -104), (-20, -108.6), (-4, -110), (12, -108), (26, -103)]), "M")          # lap sag
    man.add("detail", K.sm([(-46, -104), (-50, -94), (-54, -80), (-56.4, -70)]), "M")                       # knee drape
    man.add("detail", K.sm([(-58.6, -108), (-59, -94), (-60, -80)]), "F")
    man.add("detail", K.sm([(8, -207), (13, -187), (15.4, -161), (16, -131), (14.6, -105)]), "F")
    tassel(man, -57.4, -64.6, ang=96, length=11, lv="M")
    tassel(man, 38, -91, ang=88, length=11, lv="F")
    man.add("hatch", K.hatch([(30, -206), (36, -195), (40, -153), (41, -107), (38, -93), (33, -97), (33.6, -141),
                              (31, -181)], angle=82, spacing=2.4, seed=64), "S")
    man.add("hatch", K.hatch([(-40, -99), (-30, -96.6), (-4, -94.4), (20, -92.6), (20, -98), (-4, -100.6), (-30, -102.6),
                              (-40, -103)], angle=6, spacing=1.9, seed=65), "S")
    man.add("hatch", K.hatch([(-36.6, -134), (-31, -146), (-25, -160), (-21, -158), (-27, -144), (-33, -132)],
                             angle=-50, spacing=1.8, seed=66), "S")
    man.add("hatch", K.hatch([(-41, -97), (-45, -88), (-50, -76), (-55, -67), (-58.6, -72), (-56, -90), (-50, -100)],
                             angle=70, spacing=2.0, seed=67), "S")

    # left forearm lying along the thigh, hand resting over the near knee
    lh = f.part("hand_l", 80, 4)
    limb(lh, [(12, -136), (-4, -130.4), (-20, -125.2), (-33.6, -122.6)],
         [(9, -124.6), (-6, -120.4), (-20, -116.4), (-32.4, -114.4)], cls_a="line", cls_b="detail")
    rig_hand(lh, "knee", -32.6, -118.4, rot=8, s=1.05)
    lh.add("hatch", K.hatch([(9, -125), (-6, -121), (-20, -117), (-30, -115.4), (-20, -120), (-6, -124)], angle=8,
                            spacing=1.6, seed=69), "S")

    arm = f.part("arm_r", 60, 3)
    shoulder = [(-21, -211.6), (-29, -209.6), (-36, -205.6), (-41.6, -199.4)]
    sleeve = shoulder + [(-48.4, -190), (-53.6, -177), (-57, -164.4), (-58.6, -155)]
    hemp = [(-58.6, -155), (-54, -150.6), (-48, -151.4), (-45.4, -155)]
    under_a = [(-45.4, -155), (-44.6, -165), (-43.6, -177)]
    arm.add("line", K.chain(sleeve, hemp, under_a), "S")
    arm.occ.append(sleeve[3:] + hemp[1:] + under_a[1:])
    limb(arm, [(-57, -163), (-65.6, -170.6), (-74, -176.6), (-82, -181)],
         [(-50.4, -152.6), (-60.4, -161), (-70.4, -168.6), (-80.4, -173.6)])
    rig_hand(arm, "open", -81.8, -177.6, rot=-70, s=1.05)
    arm.add("hatch", K.hatch([(-52, -153), (-62, -161), (-76, -171), (-76, -175), (-62, -167), (-55, -161)], angle=30,
                             spacing=1.6, seed=68), "S")

    ft = f.part("feet", 5, 5)
    foot(ft, -72.6, -12.4, (-98.4, -5.6))
    foot(ft, -52.6, -9.0, (-79.4, 1.6))
    sh = f.part("shadow", 0, 9)
    sh.add("hatch", K.cat(K.seg((-106, 7.4), (-68, 7.4)), K.seg((-82, 9.6), (-34, 9.6)), K.seg((-96, 11.8), (-44, 11.8))),
           "S", clip=False)
    return f


def build(pose):
    return build_seated() if pose == "seated" else build_standing(pose)


# =============================================================== anchors / public API
_ANCH_LOCAL = {
    "standing": dict(head=(-7, -316), face=(-24, -316), hand_r=(-48, -158)),
    "teaching": dict(head=(-8.6, -315), face=(-25.6, -315), hand_r=(-104, -250)),
    "coin": dict(head=(-7, -316), face=(-24, -316), hand_r=(-76, -362)),
    "seated": dict(head=(-12, -244), face=(-29, -244), hand_r=(-104, -183), seat=(-30, 46, SEAT_Y)),
}


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
        sgn = -1 if facing == "right" else 1
        prof = K.sm([(cx - 0.05 * r * sgn, cy - 0.52 * r), (cx + 0.24 * r * sgn, cy - 0.3 * r),
                     (cx + 0.32 * r * sgn, cy - 0.02 * r), (cx + 0.2 * r * sgn, cy + 0.22 * r),
                     (cx + 0.04 * r * sgn, cy + 0.44 * r)])
        out["hatch"].append(_el("hatch", circle(cx, cy, r * 0.76) + " " + prof))
    return out


def jesus(x, y, scale=1.0, pose="standing", facing="left", level="full", accent=True, coin_wash=False):
    lay = jesus_layers(x, y, scale, pose, facing, level, accent, coin_wash)
    return "".join(lay["line"] + lay["detail"] + lay["hatch"])


def stroke_counts(pose="standing", level="full"):
    """Hand strokes (sub-paths) per class, as the engine counts them (hatch is free)."""
    lay = jesus_layers(0, 0, 1.0, pose, "left", level)
    return {k: sum(el.count(" M ") + el.count('d="M') for el in v) for k, v in lay.items()}


def stone_step(x, y, scale=1.0, facing="left", x0=None, x1=None, sil=None, seed=5):
    """A low, wide, rough-cut stone step for the seated pose (dressed block with chamfered top edge,
    chipped corners, joints, hatch on the shaded end) -> (line_d, detail_d, hatch_d), clipped to his
    silhouette.  x0/x1: block extent (default: from just in front of his knees to well behind him)."""
    import random
    rnd = random.Random(seed)
    a = jesus_anchors(x, y, scale, "seated", facing)
    sx0, sx1, top = a["seat"]
    x0 = sx0 - 14 * scale if x0 is None else x0
    x1 = sx1 + 120 * scale if x1 is None else x1
    dep = 14 * scale                       # receding top face (3/4 view)
    ch = 3.2 * scale                       # chamfer
    rough = lambda p, q, n=6, amp=0.8: [(p[0] + (q[0] - p[0]) * i / n + (rnd.uniform(-amp, amp) * scale if 0 < i < n else 0),
                                         p[1] + (q[1] - p[1]) * i / n + (rnd.uniform(-amp, amp) * scale if 0 < i < n else 0))
                                        for i in range(n + 1)]
    # front face outline with chipped corners (one continuous stroke)
    fl = (rough((x0 + 3 * scale, top), (x1 - 5 * scale, top), 10)
          + [(x1 - 2 * scale, top + 2.4 * scale), (x1, top + 6 * scale)]
          + rough((x1, top + 6 * scale), (x1 + 0.6 * scale, y), 6)[1:]
          + rough((x1 + 0.6 * scale, y), (x0, y), 10)[1:]
          + rough((x0, y), (x0 - 0.6 * scale, top + 4 * scale), 6)[1:] + [(x0 + 3 * scale, top)])
    line = K.sm(fl)
    # top face (receding) + chamfer line + the shaded end face
    det = K.sm(rough((x0 + 3 * scale, top), (x0 + dep, top - dep * 0.62), 3, 0.4)
               + rough((x0 + dep, top - dep * 0.62), (x1 + dep - 3 * scale, top - dep * 0.62), 10)[1:]
               + [(x1 + dep, top - dep * 0.62 + 3 * scale)]
               + rough((x1 + dep, top - dep * 0.62 + 3 * scale), (x1 + dep, y - dep * 0.62), 6)[1:] + [(x1 + 0.6 * scale, y)])
    det += " " + K.sm(rough((x0 + 4 * scale, top + ch), (x1 - 4 * scale, top + ch), 10, 0.5))
    jx = x0 + (x1 - x0) * 0.58
    det += " " + K.sm([(jx, top + ch + 1), (jx + 0.8 * scale, (top + y) / 2), (jx, y - 1)])
    det += " " + K.sm([(jx + dep * 0.4, top - dep * 0.25), (jx + dep * 0.75, top - dep * 0.55)])
    hat = K.hatch([(x1, top + 6 * scale), (x1 + dep, top - dep * 0.62 + 3 * scale), (x1 + dep, y - dep * 0.62), (x1, y)],
                  angle=78, spacing=2.4 * scale, seed=91)
    hat += " " + K.hatch([(x0 + 4 * scale, y - 18 * scale), (x1 - 2 * scale, y - 14 * scale), (x1, y - 2), (x0 + 2, y - 2)],
                         angle=-12, spacing=3.2 * scale, seed=92)
    for k in range(5):                     # pitting / tooling marks
        px = x0 + (x1 - x0) * rnd.uniform(0.1, 0.9); py = top + (y - top) * rnd.uniform(0.25, 0.75)
        hat += " " + K.seg((px, py), (px + 3 * scale, py + 0.8 * scale))
    sil = sil or a["silhouette"]
    return (K.clip(line, [sil]), K.clip(det, [sil]), K.clip(hat, [sil]))


if __name__ == "__main__":
    from lib_v2 import svg, L as _L, D as _D, H as _H
    body = ""
    for i, pose in enumerate(POSES):
        body += jesus(190 + i * 395, 775, 1.6, pose)
    ln, dt, ht = stone_step(190 + 3 * 395, 775, 1.6)
    body += _L(ln) + _D(dt) + _H(ht)
    out = os.path.join(os.path.dirname(os.path.dirname(HERE)), "preview", "jesus-sheet.svg")
    open(out, "w").write(svg(body, "jesus.py contact sheet (full level); seated shown on a stone step"))
    print("wrote", out)
    for pose in POSES:
        print(pose, {lv: stroke_counts(pose, lv) for lv in LEVELS})
