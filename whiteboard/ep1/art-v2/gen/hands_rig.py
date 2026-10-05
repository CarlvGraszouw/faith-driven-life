"""Hand rig: palm block + jointed finger/thumb capsules -> union outline + inner (finger) lines.
Run:  python3 hands_rig.py   -> writes hands_data.py (pure data, imported by jesus.py / scene generators)
Needs shapely (generation only).  Local coords: wrist at (0, 0); angles in degrees (0 = +x, 90 = +y down)."""
import math, os, pprint
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))


def chain(base, angles, lengths):
    """angles: first absolute, then relative bends.  -> list of joint points."""
    pts = [base]
    a = 0.0
    for i, (da, L) in enumerate(zip(angles, lengths)):
        a = da if i == 0 else a + da
        x, y = pts[-1]
        pts.append((x + L * math.cos(math.radians(a)), y + L * math.sin(math.radians(a))))
    return pts


def capsule(pts, r0, r1):
    """tapered chain: union of per-segment round buffers."""
    n = len(pts) - 1
    parts = []
    for i in range(n):
        r = r0 + (r1 - r0) * (i / max(1, n - 1))
        parts.append(LineString([pts[i], pts[i + 1]]).buffer(r, quad_segs=10))
    return unary_union(parts)


def build(spec):
    """spec: dict(palm=[pts], items=[dict(kind, base, angles, lengths, r0, r1, z)], extra={...})
    items with higher z are in front.  Returns dict(outline=[pts], inner=[[pts],...], **extra)."""
    palm = Polygon(spec["palm"]).buffer(0.6, quad_segs=6).buffer(-0.3)
    shapes = [(0, palm, "palm")]
    for it in spec["items"]:
        pts = chain(it["base"], it["angles"], it["lengths"])
        shapes.append((it["z"], capsule(pts, it["r0"], it["r1"]), it.get("name", "f")))
    union = unary_union([s for _, s, _ in shapes]).buffer(0.25).buffer(-0.25)
    if union.geom_type == "MultiPolygon":
        union = max(union.geoms, key=lambda g: g.area)
    outline = list(union.simplify(0.12).exterior.coords)
    ub = union.exterior.buffer(0.45)
    inner = []
    for z, shp, name in shapes:
        if name == "palm" or name in spec.get("no_inner", ()):
            continue
        front = [s for zz, s, _ in shapes if zz > z]
        b = shp.exterior if shp.geom_type == "Polygon" else max(shp.geoms, key=lambda g: g.area).exterior
        vis = b.difference(ub)
        if front:
            vis = vis.difference(unary_union(front).buffer(0.05))
        geoms = getattr(vis, "geoms", [vis])
        for g in geoms:
            if g.is_empty or g.length < spec.get("min_inner", 2.2):
                continue
            inner.append([(round(x, 2), round(y, 2)) for x, y in g.simplify(0.12).coords])
    res = dict(outline=[(round(x, 2), round(y, 2)) for x, y in outline], inner=inner)
    res.update(spec.get("extra", {}))
    return res


# ------------------------------------------------------------------ poses
SPECS = {}

# open hand, palm toward the viewer, fingers up (-y), thumb on the right (+x).  (right hand)
SPECS["open"] = dict(
    palm=[(-4.4, 0), (4.6, 0), (6.6, -6), (6.6, -12.8), (2, -13.6), (-3, -13.2), (-6.4, -11.6), (-5.8, -5)],
    items=[
        dict(name="little", base=(-4.9, -11.4), angles=[-103, -4, -5], lengths=[5.4, 3.4, 2.8], r0=1.55, r1=1.3, z=1),
        dict(name="ring", base=(-1.8, -12.8), angles=[-95, -3, -4], lengths=[7.0, 4.4, 3.4], r0=1.7, r1=1.45, z=1),
        dict(name="middle", base=(1.5, -13.2), angles=[-88, -2, -4], lengths=[7.6, 4.8, 3.6], r0=1.78, r1=1.5, z=1),
        dict(name="index", base=(4.6, -12.6), angles=[-80, -3, -6], lengths=[7.0, 4.4, 3.4], r0=1.75, r1=1.5, z=1),
        dict(name="thumb", base=(3.4, -2.6), angles=[-40, -10, -18], lengths=[6.6, 4.8, 3.8], r0=2.2, r1=1.75, z=2),
    ],
    no_inner=(),
)
# relaxed hanging hand, side view from the thumb side: fingers down (+y), palm side toward -x
SPECS["relaxed"] = dict(
    palm=[(-3.2, 0), (3.4, 0), (4.8, 6), (5.0, 12.8), (1, 14), (-3.8, 13.2), (-5, 8), (-4.2, 3)],
    items=[
        dict(name="little", base=(3.8, 12.2), angles=[86, 30, 24], lengths=[5.4, 3.6, 3.0], r0=1.5, r1=1.3, z=1),
        dict(name="ring", base=(2.8, 12.8), angles=[89, 24, 20], lengths=[7.0, 4.4, 3.4], r0=1.65, r1=1.4, z=2),
        dict(name="middle", base=(1.6, 13.2), angles=[92, 18, 16], lengths=[7.6, 4.8, 3.6], r0=1.75, r1=1.5, z=3),
        dict(name="index", base=(0.2, 12.8), angles=[96, 14, 12], lengths=[7.0, 4.4, 3.4], r0=1.75, r1=1.5, z=4),
        dict(name="thumb", base=(-2.6, 2.6), angles=[110, -4, 8], lengths=[6.0, 4.4, 3.4], r0=2.2, r1=1.7, z=5),
    ],
)
# fist gripping a cloth edge, side view; knuckles toward -x, fingers curl down/back (+y, +x); thumb on top
SPECS["grip"] = dict(
    palm=[(0, -4.6), (0, 4.6), (-5, 5.4), (-10.6, 5), (-12.4, 1), (-12, -3.8), (-6, -5.8)],
    items=[
        dict(name="little", base=(-9.8, 4.2), angles=[178, -84, -80], lengths=[4.4, 3.2, 2.6], r0=1.5, r1=1.3, z=1),
        dict(name="ring", base=(-11, 2.0), angles=[180, -82, -78], lengths=[5.4, 3.8, 3.0], r0=1.65, r1=1.4, z=2),
        dict(name="middle", base=(-11.6, -0.6), angles=[181, -78, -74], lengths=[5.8, 4.0, 3.2], r0=1.75, r1=1.5, z=3),
        dict(name="index", base=(-11.4, -3.2), angles=[184, -72, -70], lengths=[5.4, 3.8, 3.0], r0=1.75, r1=1.5, z=4),
        dict(name="thumb", base=(-2.6, -4.2), angles=[200, -10, 26], lengths=[5.6, 4.4, 3.4], r0=2.1, r1=1.7, z=5),
    ],
)
# hand resting palm-down on a knee: back of the hand seen, fingers bend down over the knee (thumb hidden)
SPECS["knee"] = dict(
    palm=[(0, -4.6), (0, 4.4), (-6, 5.2), (-12.2, 4.6), (-13.4, 0), (-12.6, -4.4), (-6, -5.6)],
    items=[
        dict(name="little", base=(-11.6, 3.6), angles=[166, -36, -26], lengths=[4.8, 3.4, 2.8], r0=1.45, r1=1.25, z=1),
        dict(name="ring", base=(-12.6, 1.6), angles=[172, -40, -30], lengths=[6.0, 4.2, 3.2], r0=1.6, r1=1.4, z=2),
        dict(name="middle", base=(-13.0, -0.8), angles=[176, -44, -32], lengths=[6.6, 4.4, 3.4], r0=1.7, r1=1.45, z=3),
        dict(name="index", base=(-12.6, -3.2), angles=[180, -46, -32], lengths=[6.0, 4.2, 3.2], r0=1.7, r1=1.45, z=4),
    ],
)
# raised hand seen from the back, fingers up (-y); thumb (viewer's left) and index pinch a coin above;
# middle/ring/little curled (short, knuckles only)
SPECS["coin"] = dict(
    palm=[(-4.6, 0), (4.4, 0), (6.4, -6), (6.6, -12.6), (2, -13.8), (-3, -13.4), (-6.6, -10.4), (-6.2, -4)],
    items=[
        dict(name="little", base=(4.8, -11.8), angles=[-82, 40], lengths=[4.4, 2.6], r0=1.55, r1=1.4, z=1),
        dict(name="ring", base=(2.2, -13.0), angles=[-88, 42], lengths=[5.0, 2.8], r0=1.65, r1=1.5, z=2),
        dict(name="middle", base=(-0.6, -13.4), angles=[-92, 44], lengths=[5.4, 3.0], r0=1.75, r1=1.55, z=3),
        dict(name="index", base=(-3.6, -12.8), angles=[-96, -35, -50], lengths=[6.6, 4.4, 3.4], r0=1.75, r1=1.5, z=4),
        dict(name="thumb", base=(-4.0, -2.6), angles=[-112, 6, 8], lengths=[7.2, 5.4, 5.6], r0=2.2, r1=1.75, z=5),
    ],
)


def finger_tip(spec, name):
    it = [i for i in spec["items"] if i["name"] == name][0]
    return chain(it["base"], it["angles"], it["lengths"])[-1]


if __name__ == "__main__":
    data = {}
    for k, sp in SPECS.items():
        d = build(sp)
        if k == "coin":
            ti = finger_tip(sp, "index"); tt = finger_tip(sp, "thumb")
            px, py = (ti[0] + tt[0]) / 2, (ti[1] + tt[1]) / 2
            d["pinch"] = (round(px, 2), round(py, 2))
        data[k] = d
    with open(os.path.join(HERE, "hands_data.py"), "w") as fo:
        fo.write('"""Baked hand shapes (generated by hands_rig.py; do not edit).  wrist at (0,0)."""\n')
        fo.write("HANDS = " + pprint.pformat(data, width=120, compact=True) + "\n")
    for k, d in data.items():
        print(k, len(d["outline"]), "outline pts,", len(d["inner"]), "inner lines", d.get("pinch", ""))
