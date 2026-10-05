"""Body rig for batch A figures: a posed 2D mannequin dressed in volumes (shapely), turned into a whiteboard
drawing: one silhouette stroke, visible interior edges (sleeves over the body, near leg over the far one,
belt, hems) as detail strokes, procedural folds, hatch modelling.  Heads come from a_people.head34, hands from
the hand rig, feet from jesus.foot.  Facing LEFT in local units (340 = standing height); mirror to face right.

Joints (dict, local units, y down, ground 0):
  head (eye-line centre of the head), neck (pit of the neck), shf/shn (far/near shoulder), elf/eln, wrf/wrn,
  hipf/hipn, knf/knn, anf/ann (ankles), tof/ton (toe points), waist (centre of the belt line)
"far" = the side away from the viewer (left side of a left-facing 3/4 figure)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from shapely.geometry import Polygon, LineString, Point, MultiPoint, MultiLineString
from shapely.ops import unary_union
import a_sketch as K
from jesus import Fig, rig_hand, foot, tassel, WHITE


def circ(p, r):
    return Point(p).buffer(r, quad_segs=12)


def capsule(a, b, r0, r1=None):
    r1 = r0 if r1 is None else r1
    n = max(2, int(math.dist(a, b) / 3))
    return unary_union([circ(K.lerp(a, b, i / n), r0 + (r1 - r0) * i / n) for i in range(n + 1)]).convex_hull


def hull(*geoms):
    return unary_union(list(geoms)).convex_hull


def as_lines(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type in ("MultiLineString", "GeometryCollection"):
        return [x for x in g.geoms if x.geom_type == "LineString"]
    return []


def ext(g):
    if g.geom_type == "MultiPolygon":
        g = max(g.geoms, key=lambda q: q.area)
    return g.exterior


def smooth_ring(coords, closed=True, tol=0.9):
    pts = list(LineString(coords).simplify(tol).coords)
    if closed and pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 3:
        return K.seg(*pts)
    return K.sm(pts, closed=closed, t=0.45)


class Dressed:
    """Collect garment/body volumes with z (higher = nearer), then produce strokes."""

    def __init__(self):
        self.parts = []      # (z, geom, name, inner_lv)

    def add(self, z, geom, name, inner_lv="S"):
        self.parts.append((z, geom.buffer(0), name, inner_lv))

    def union(self):
        return unary_union([g for _, g, _, _ in self.parts]).buffer(0.6).buffer(-0.6)

    def strokes(self, min_len=6.0, tol=0.9):
        """-> (outline path, [(inner path, lv)], occluder polygon)"""
        u = self.union()
        out = smooth_ring(list(ext(u).coords), True, tol)
        ub = ext(u).buffer(1.2)
        inner = []
        for z, g, name, lv in self.parts:
            if lv is None:
                continue
            front = [gg for zz, gg, _, _ in self.parts if zz > z]
            b = ext(g)
            vis = b.difference(ub)
            if front:
                vis = vis.difference(unary_union(front).buffer(0.2))
            for ln in as_lines(vis):
                if ln.length >= min_len:
                    inner.append((smooth_ring(list(ln.coords), False, tol), lv))
        occ = list(ext(u).simplify(0.6).coords)
        return out, inner, occ, u


def robe_standing(J, hem_y=None, flare=10.0, waist_r=15.0, hip_r=19.0, knee_r=12.0):
    """Long robe (ankle length): torso + skirt hull over hips/knees/hem."""
    hem_y = (max(J["anf"][1], J["ann"][1]) - 8) if hem_y is None else hem_y
    xs = [J["anf"][0], J["ann"][0]]
    hem_l, hem_r = min(xs) - flare - 6, max(xs) + flare
    pelvis = ((J["hipf"][0] + J["hipn"][0]) / 2, (J["hipf"][1] + J["hipn"][1]) / 2)
    skirt = hull(circ(pelvis, hip_r), circ(J["knf"], knee_r), circ(J["knn"], knee_r),
                 Polygon([(hem_l, hem_y - 14), (hem_r, hem_y - 14), (hem_r, hem_y - 12), (hem_l, hem_y - 12)]))
    # folded hem: a band with a gently undulating lower edge
    wav = wavy_hem(hem_l, hem_r, hem_y, n=9, amp=2.4, seed=int(abs(hem_l * 7)) % 97)
    band = Polygon([(hem_l, hem_y - 14)] + wav + [(hem_r, hem_y - 14)])
    return unary_union([skirt, band]).buffer(0), (hem_l, hem_r, hem_y)


def torso(J, chest=17.0, waist=14.0, sh_r=8.5):
    w = J["waist"]
    chestp = K.lerp(J["neck"], w, 0.38)
    return hull(circ(J["shf"], sh_r), circ(J["shn"], sh_r), circ(chestp, chest), circ(w, waist),
                circ(K.lerp(J["neck"], J["shf"], 0.5), 6), circ(K.lerp(J["neck"], J["shn"], 0.5), 6))


def wavy_hem(l, r, y, n=7, amp=2.2, seed=1):
    import random
    rnd = random.Random(seed)
    pts = []
    for i in range(n + 1):
        x = l + (r - l) * i / n
        pts.append((x, y + (amp if i % 2 else -amp * 0.4) + rnd.uniform(-0.6, 0.6)))
    return pts


def place_head(fig, J, rot, **head_opts):
    from a_people import head34
    hx, hy = J["head"]
    return head34(fig, hx, hy, rot=rot, **head_opts)


def robe_seated(J, hem_y=None, drape=12.0):
    """Long robe on a seated body: over the thighs (lap), falling from the knees to the ankles in front of
    the shins (drape), hem a little above the feet."""
    hem_y = (max(J["anf"][1], J["ann"][1]) - 7) if hem_y is None else hem_y
    lap = unary_union([capsule(J["hipf"], J["knf"], 15, 12.5), capsule(J["hipn"], J["knn"], 15, 12.5)])
    xs = [J["anf"][0], J["ann"][0], J["knf"][0], J["knn"][0]]
    hl, hr = min(xs) - drape, max(xs) + drape * 0.6
    fall = hull(circ(J["knf"], 12), circ(J["knn"], 12),
                Polygon([(hl, hem_y - 12), (hr, hem_y - 12), (hr, hem_y - 10), (hl, hem_y - 10)]))
    wav = wavy_hem(hl, hr, hem_y, n=5, amp=2.0, seed=int(abs(hl * 3)) % 89)
    band = Polygon([(hl, hem_y - 12)] + wav + [(hr, hem_y - 12)])
    return unary_union([lap, fall, band]).buffer(0), (hl, hr, hem_y)
