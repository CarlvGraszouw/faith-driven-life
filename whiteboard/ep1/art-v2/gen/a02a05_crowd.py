"""Small 1st-century Judean figures for crowds (a02-temple, a05-soldiers background).

Figures are built from a tiny rig at height 100 (feet at y=0, top of head near y=-100, facing right):
tapered capsules for limbs, ellipses for heads, smooth polygons for tunics, mantles and veils.  The union
of the parts is the silhouette (and occluder); edges of 'front' parts that fall inside the silhouette become
interior lines (an arm across the body, the edge of a mantle, a veil around the face)."""
import math
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
from shapely import affinity
from a02a05_tools import sp, to_poly, rings, _lines_of

C = 1


def cap(a, b, ra, rb):
    return unary_union([Point(a).buffer(ra, 16), Point(b).buffer(rb, 16)]).convex_hull


def ell(c, rx, ry, rot=0.0):
    e = affinity.scale(Point(c).buffer(1.0, 32), rx, ry, origin=c)
    return affinity.rotate(e, rot, origin=c) if rot else e


def sm(pts):
    return to_poly(sp(pts, closed=True, step=0.7))


class Fig:
    def __init__(self):
        self.parts = []          # (geom, front, inner_lines_allowed)
        self.props = []          # open strokes drawn separately (staff, rope)
        self.extra_in = []       # explicit interior strokes

    def add(self, g, front=False):
        self.parts.append((g, front))
        return self

    def line(self, pts):
        self.extra_in.append(sp(pts, step=0.7))
        return self

    def prop(self, pts):
        self.props.append(sp(pts, step=0.7))
        return self

    def build(self):
        allg = unary_union([g for g, _ in self.parts]).buffer(0.35).buffer(-0.35)
        inner = []
        for i, (g, front) in enumerate(self.parts):
            if not front:
                continue
            behind = unary_union([h for j, (h, _) in enumerate(self.parts) if j < i])
            if behind.is_empty:
                continue
            edge = g.exterior.intersection(behind.buffer(-0.45))
            inner += [l for l in _lines_of(edge) if LineString(l).length > 2.0]
        return allg, inner + self.extra_in, self.props


# ----------------------------------------------------------------------------- body parts
def head_side(f, cx, cy, tilt=0.0, beard=True, hood=None, veil=False, hair=True):
    """profile head facing right; hood: None or mantle-over-head outline extension"""
    f.add(ell((cx, cy), 5.3, 6.4, tilt))
    nose = Polygon([(cx + 4.4, cy - 1.8), (cx + 6.6, cy + 1.6), (cx + 4.2, cy + 2.4)])
    f.add(affinity.rotate(nose, tilt, origin=(cx, cy)))
    if beard:
        f.add(ell((cx + 2.6, cy + 5.6), 3.3, 3.0, 25 + tilt))
    else:
        f.add(ell((cx + 3.0, cy + 4.6), 2.2, 2.0, tilt))
    return f


def hood_side(f, cx, cy, back=-9.0, down=-78.0):
    """mantle drawn over the head: covers the crown and falls behind the neck to the shoulders"""
    g = sm([(cx - 1.0, cy - 7.6), (cx + 3.6, cy - 6.8), (cx + 5.4, cy - 3.4), (cx + 3.8, cy - 0.4),
            (cx + 2.4, cy + 4.0), (cx + 1.8, cy + 8.0), (cx + 4.0, down + 2.0), (back, down),
            (back + 1.0, cy + 6.0), (cx - 5.6, cy + 1.0), (cx - 5.4, cy - 4.4)])
    f.add(g, front=True)
    return f


def robe_side(f, top_front, top_back, hem_front, hem_back, belly=1.0, back_bulge=0.0):
    """ankle-length tunic seen from the side; points are (x, y)"""
    (fx, fy), (bx, by), (hfx, hfy), (hbx, hby) = top_front, top_back, hem_front, hem_back
    g = sm([(fx, fy), (fx + 2.0 * belly, fy + 9), (fx + 1.6 * belly, fy + 22), (fx + 1.4, fy + 34),
            ((fx + hfx) / 2 + 1.5, (fy + hfy) / 2 + 12), (hfx, hfy - 3), (hfx + 0.8, hfy, C), ((hfx + hbx) / 2, hfy + 0.6, C),
            (hbx, hby, C), (hbx + 0.4, hby - 4), ((bx + hbx) / 2 - back_bulge, (by + hby) / 2), (bx - 1.0, by + 16), (bx, by)])
    f.add(g)
    return f


def leg(f, hip, knee, ankle, toe, r=(4.2, 3.0, 2.0), front=False):
    f.add(cap(hip, knee, r[0], r[1]), front)
    f.add(cap(knee, ankle, r[1], r[2]), front)
    f.add(cap(ankle, toe, 1.8, 1.25), front)
    return f


def arm(f, sh, el, wr, hand, r=(2.6, 2.1, 1.6), hr=(2.0, 2.3), front=False, sleeve=None, side=1):
    f.add(cap(sh, el, r[0], r[1]))
    f.add(cap(el, wr, r[1], r[2]))
    f.add(ell(hand, hr[0], hr[1]))
    if front:
        # one stroke along the arm's outer edge: shoulder -> elbow -> wrist (side = which side of the bone)
        import math as _m
        def off(a, b, d):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = _m.hypot(dx, dy) or 1
            return (-dy / L * d * side, dx / L * d * side)
        o1 = off(sh, el, r[0] * 0.95); o2 = off(el, wr, r[1] * 0.95); o3 = off(el, wr, r[2] * 0.95)
        f.line([(sh[0] + o1[0], sh[1] + o1[1]), (el[0] + (o1[0] + o2[0]) / 2, el[1] + (o1[1] + o2[1]) / 2),
                (wr[0] + o3[0], wr[1] + o3[1])])
    return f


# ----------------------------------------------------------------------------- poses
def walker(staff=True, hood=True, beard=True):
    """walking right; mantle over the head; staff in the forward hand"""
    f = Fig()
    hx, hy = 2.2, -93.0
    leg(f, (-1.0, -50.0), (-4.6, -27.0), (-9.4, -5.0), (-6.0, -1.2))
    arm(f, (-1.0, -79.5), (-5.2, -64.0), (-7.2, -50.5), (-7.2, -47.0))
    f.add(sm([(5.4, -81.0), (8.0, -73.0), (7.8, -60.0), (6.4, -51.0), (-6.8, -50.0), (-7.8, -62.0), (-6.8, -75.0), (-3.8, -81.6)]))
    f.add(cap((1.2, -86.5), (0.8, -80.0), 2.7, 3.3))
    head_side(f, hx, hy, beard=beard)
    robe_side(f, (6.0, -80.0), (-6.0, -80.0), (13.6, -4.2), (-12.6, -5.0))
    leg(f, (1.0, -50.0), (6.8, -28.0), (10.4, -4.2), (14.8, -1.2))
    if hood:
        f.add(sm([(hx - 1.4, hy - 7.6), (hx + 3.4, hy - 7.2), (hx + 5.4, hy - 3.6), (hx + 4.0, hy - 1.0), (hx + 2.6, hy + 3.4),
                  (hx + 2.2, hy + 7.4), (4.6, -78.0), (7.0, -68.0), (7.6, -52.0), (6.6, -36.0), (-2.0, -32.0), (-13.0, -29.0),
                  (-13.0, -48.0), (-11.4, -66.0), (-9.2, -79.0), (hx - 6.0, hy + 1.0), (hx - 5.6, hy - 4.6)]), front=True)
    arm(f, (0.8, -78.0), (4.2, -63.0), (11.0, -58.6), (12.8, -58.0))
    f.line([(-0.2, -76.0), (2.6, -63.0), (5.0, -60.6), (10.4, -57.0)])
    if staff:
        f.prop([(15.4, -89.0), (13.0, -58.0), (10.6, -0.5)])
    return f


def talker(raise_hand=True):
    """three-quarter front, weight on one leg, one hand raised in conversation"""
    f = Fig()
    leg(f, (-4.0, -50.0), (-4.8, -27.0), (-5.6, -4.2), (-8.2, -1.0))
    leg(f, (4.0, -50.0), (5.0, -27.0), (5.8, -4.2), (8.8, -1.2))
    f.add(sm([(-10.6, -81.0), (-12.4, -72.0), (-11.4, -60.0), (-12.2, -48.0), (-14.0, -24.0), (-15.0, -4.6, C), (-1.0, -3.8),
              (15.0, -4.6, C), (14.2, -24.0), (12.4, -48.0), (11.6, -60.0), (12.4, -72.0), (11.0, -81.0), (4.0, -83.6), (-4.0, -83.6)]))
    f.add(cap((0.0, -86.6), (0.0, -81.0), 2.8, 3.4))
    f.add(ell((0.4, -93.0), 5.0, 6.5))
    f.add(ell((1.2, -87.4), 3.6, 3.2, 10))
    f.add(sm([(-5.2, -96.0), (-1.0, -100.0), (4.4, -98.8), (5.6, -94.0), (4.0, -95.6), (-3.4, -96.4), (-5.0, -90.0)]))
    arm(f, (-10.6, -79.0), (-12.8, -63.0), (-12.0, -48.0), (-11.6, -44.6))
    f.add(sm([(-12.4, -82.0), (-4.0, -84.6), (2.4, -80.0), (0.4, -66.0), (-2.0, -48.0), (-3.4, -30.0), (-15.4, -28.0),
              (-15.0, -50.0), (-14.6, -66.0)]), front=True)
    if raise_hand:
        arm(f, (10.6, -79.0), (16.0, -68.0), (20.0, -79.0), (21.0, -82.6))
    else:
        arm(f, (10.6, -79.0), (12.4, -63.0), (8.0, -54.0), (6.0, -53.0))
        f.line([(9.6, -74.0), (10.4, -62.0), (6.0, -56.0)])
    return f


def back_view():
    """walking away toward the temple; striped prayer mantle over the head"""
    f = Fig()
    leg(f, (-4.0, -50.0), (-4.6, -27.0), (-5.4, -5.0), (-5.6, -1.0))
    leg(f, (4.0, -50.0), (4.4, -27.0), (5.0, -2.6), (5.2, -0.4))
    f.add(sm([(-11.4, -80.0), (-13.2, -66.0), (-13.6, -40.0), (-14.4, -6.0, C), (14.4, -6.0, C), (13.6, -40.0), (13.2, -66.0),
              (11.4, -80.0), (4.0, -84.0), (-4.0, -84.0)]))
    f.add(ell((0.0, -93.0), 5.2, 6.6))
    f.add(sm([(-1.0, -100.4), (5.6, -98.0), (8.4, -90.0), (12.8, -80.0), (15.0, -64.0), (15.2, -42.0), (-15.2, -42.0), (-15.0, -64.0),
              (-12.8, -80.0), (-8.4, -90.0), (-5.6, -98.0)]), front=True)
    arm(f, (-11.4, -78.0), (-13.8, -62.0), (-13.4, -48.0), (-13.0, -44.6))
    arm(f, (11.4, -78.0), (13.8, -62.0), (13.4, -48.0), (13.0, -44.6))
    f.line([(-14.8, -50.0), (-6.0, -51.6), (6.0, -51.6), (14.8, -50.0)])
    f.line([(-14.8, -47.0), (-6.0, -48.6), (6.0, -48.6), (14.8, -47.0)])
    f.line([(0.0, -84.0), (0.6, -70.0), (0.0, -54.0)])
    return f


def lamb_carrier():
    """walking right with a lamb across his shoulders, holding its legs at his chest"""
    f = Fig()
    hx, hy = 2.6, -92.0
    leg(f, (-1.0, -50.0), (-4.0, -27.0), (-9.0, -5.0), (-5.6, -1.2))
    f.add(sm([(5.4, -81.0), (8.0, -73.0), (7.8, -60.0), (6.4, -51.0), (-6.8, -50.0), (-7.8, -62.0), (-6.8, -75.0), (-3.8, -81.6)]))
    f.add(cap((1.4, -85.6), (0.8, -80.0), 2.7, 3.3))
    head_side(f, hx, hy, beard=True)
    f.add(sm([(-2.6, -99.4), (2.6, -99.6), (6.0, -97.0), (3.0, -96.2), (-3.0, -95.0), (-6.4, -90.0), (-6.6, -95.6)]))
    robe_side(f, (6.0, -80.0), (-6.0, -80.0), (12.6, -4.2), (-11.6, -5.0))
    leg(f, (1.0, -50.0), (6.2, -28.0), (9.6, -4.2), (14.0, -1.2))
    lamb = sm([(-15.0, -83.0), (-14.0, -88.6), (-9.0, -91.4), (-3.0, -90.0), (2.0, -87.4), (6.4, -86.4), (10.4, -87.8),
               (13.4, -89.4), (15.4, -87.0), (14.0, -83.6), (10.4, -81.4), (4.0, -79.6), (-4.0, -79.0), (-11.0, -79.6)])
    f.add(lamb)
    f.add(ell((16.0, -88.4), 3.2, 2.4, -15))
    f.add(ell((14.4, -91.0), 1.6, 1.0, -35))
    f.add(cap((-13.0, -80.4), (-8.0, -77.2), 1.1, 0.9))
    f.add(cap((-11.0, -80.0), (-12.0, -74.4), 1.1, 0.9))
    arm(f, (0.8, -78.0), (6.4, -70.0), (10.6, -80.0), (11.4, -82.0))
    f.line([(0.2, -76.0), (5.2, -69.0), (9.0, -77.4)])
    f.line([(-12.4, -87.0), (-9.6, -88.4), (-7.0, -86.6), (-4.4, -88.0), (-1.6, -86.0)])
    return f


def jar_woman():
    """walking right, veil, steadying a water jar on her head with a raised arm"""
    f = Fig()
    hx, hy = 2.0, -91.0
    leg(f, (-1.0, -50.0), (-3.6, -27.0), (-8.0, -4.6), (-4.6, -1.2), r=(3.8, 2.8, 1.8))
    f.add(sm([(4.8, -79.0), (7.4, -72.0), (6.6, -62.0), (5.4, -52.0), (-6.0, -50.0), (-6.6, -62.0), (-5.8, -74.0), (-3.4, -80.0)]))
    f.add(cap((1.0, -85.0), (0.6, -79.0), 2.4, 3.0))
    head_side(f, hx, hy, beard=False)
    f.add(sm([(4.8, -78.0), (7.6, -66.0), (9.2, -46.0), (11.4, -20.0), (12.4, -4.2, C), (-10.6, -4.8, C), (-11.2, -22.0), (-10.2, -46.0),
              (-8.8, -66.0), (-5.6, -78.0)]))
    leg(f, (1.0, -50.0), (4.6, -28.0), (8.6, -4.2), (12.8, -1.2), r=(3.8, 2.8, 1.8))
    f.add(sm([(hx - 1.0, hy - 7.4), (hx + 3.6, hy - 6.8), (hx + 5.2, hy - 3.6), (hx + 3.6, hy - 1.0), (hx + 2.4, hy + 4.0),
              (hx + 2.0, hy + 8.0), (3.0, -76.0), (-1.0, -66.0), (-8.6, -56.0), (-10.2, -66.0), (-8.4, -78.0), (hx - 5.6, hy + 1.0),
              (hx - 5.6, hy - 4.6)]), front=True)
    jy = hy - 7.2
    f.add(sm([(hx - 4.4, jy), (hx - 6.6, jy - 4.0), (hx - 5.8, jy - 9.6), (hx - 2.6, jy - 12.6), (hx - 2.0, jy - 15.4, C),
              (hx + 2.0, jy - 15.4, C), (hx + 2.6, jy - 12.6), (hx + 5.8, jy - 9.6), (hx + 6.6, jy - 4.0), (hx + 4.4, jy)]))
    arm(f, (1.0, -77.0), (8.6, -86.0), (7.2, -97.6), (6.0, -100.4), r=(2.3, 1.9, 1.5), hr=(1.7, 2.0))
    f.line([(hx - 5.6, jy - 4.0), (hx, jy - 3.0), (hx + 5.6, jy - 4.0)])
    return f


def child():
    f = Fig()
    leg(f, (-1.0, -31.0), (-2.6, -17.0), (-6.0, -3.6), (-3.4, -0.7), r=(2.8, 2.1, 1.5))
    f.add(sm([(3.4, -48.0), (4.6, -44.0), (4.4, -36.0), (3.6, -31.0), (-4.0, -30.0), (-4.6, -38.0), (-4.0, -45.0), (-2.4, -49.0)]))
    f.add(ell((1.0, -55.0), 4.4, 5.0))
    f.add(ell((4.6, -54.0), 1.2, 1.4))
    f.add(sm([(3.6, -47.0), (5.4, -38.0), (6.8, -22.0), (7.8, -4.2, C), (-7.0, -4.6, C), (-7.0, -22.0), (-6.0, -38.0), (-3.6, -47.0)]))
    leg(f, (0.6, -31.0), (3.0, -17.0), (5.4, -3.6), (8.8, -0.8), r=(2.8, 2.1, 1.5))
    arm(f, (-2.0, -46.0), (-6.0, -54.0), (-7.6, -62.0), (-7.8, -64.4), r=(1.7, 1.4, 1.2), hr=(1.4, 1.6))
    f.add(sm([(-3.6, -58.0), (0.0, -60.6), (4.4, -59.0), (5.0, -56.0), (1.0, -57.6), (-3.8, -55.0)]))
    return f


def elder():
    """old man bent over a cane, walking right"""
    f = Fig()
    hx, hy = 9.0, -85.0
    leg(f, (-1.0, -48.0), (-3.0, -26.0), (-7.4, -4.6), (-4.0, -1.2))
    f.add(sm([(8.0, -75.0), (9.6, -66.0), (7.6, -56.0), (5.0, -49.0), (-6.8, -48.0), (-7.0, -60.0), (-3.6, -72.0), (2.4, -79.0)]))
    f.add(cap((6.8, -80.0), (5.0, -75.0), 2.6, 3.0))
    head_side(f, hx, hy, tilt=12, beard=True)
    f.add(sm([(8.0, -74.0), (9.8, -62.0), (10.0, -44.0), (11.4, -20.0), (12.4, -4.4, C), (-10.0, -5.0, C), (-10.4, -24.0), (-9.6, -46.0),
              (-7.6, -62.0), (-2.0, -73.0)]))
    leg(f, (1.0, -48.0), (5.0, -27.0), (8.4, -4.2), (12.6, -1.2))
    f.add(sm([(hx - 2.0, hy - 7.4), (hx + 3.0, hy - 7.4), (hx + 5.6, hy - 3.6), (hx + 3.8, hy - 0.4), (hx + 2.2, hy + 4.4),
              (hx + 1.2, hy + 8.0), (8.0, -66.0), (9.4, -50.0), (8.0, -36.0), (-11.0, -34.0), (-10.6, -54.0), (-6.0, -68.0),
              (-0.6, -78.0), (hx - 5.8, hy + 0.4), (hx - 5.6, hy - 4.6)]), front=True)
    arm(f, (5.0, -74.0), (9.0, -60.0), (15.4, -54.0), (16.8, -53.6))
    f.line([(4.6, -71.0), (7.4, -60.0), (14.6, -52.6)])
    f.prop([(17.2, -56.4), (17.0, -40.0), (18.6, -0.5)])
    return f


def mother():
    """three-quarter front, veil, a swaddled baby held in her arms"""
    f = Fig()
    leg(f, (-3.6, -50.0), (-4.2, -27.0), (-5.0, -4.2), (-7.8, -1.0), r=(3.8, 2.8, 1.8))
    leg(f, (3.6, -50.0), (4.4, -27.0), (5.0, -4.2), (8.0, -1.2), r=(3.8, 2.8, 1.8))
    f.add(sm([(-10.0, -79.0), (-11.6, -68.0), (-10.6, -56.0), (-11.8, -40.0), (-13.4, -20.0), (-14.0, -4.6, C), (13.6, -4.6, C),
              (13.0, -20.0), (11.6, -40.0), (10.4, -56.0), (11.2, -68.0), (10.0, -79.0), (3.0, -82.0), (-3.0, -82.0)]))
    f.add(cap((0.0, -85.6), (0.0, -80.0), 2.4, 3.0))
    f.add(ell((0.4, -91.6), 4.8, 6.2))
    f.add(sm([(-0.6, -99.4), (5.2, -97.6), (7.4, -92.0), (7.6, -84.0), (11.8, -78.0), (13.2, -58.0), (-13.2, -58.0), (-11.8, -78.0),
              (-7.6, -84.0), (-6.8, -92.0), (-5.4, -97.4)]), front=True)
    f.add(ell((5.0, -68.0), 7.4, 3.6, -18), front=True)
    f.add(ell((10.6, -71.0), 2.6, 2.4), front=True)
    arm(f, (-9.0, -77.0), (-8.0, -64.0), (2.0, -63.0), (4.0, -62.6))
    f.line([(-6.4, -74.0), (-6.4, -64.8), (2.4, -64.4)])
    return f


def seated():
    """money-changer seated on a low stool, facing right, hands on his table"""
    f = Fig()
    hx, hy = 1.0, -67.0
    f.add(sm([(4.8, -55.0), (7.0, -47.0), (6.6, -36.0), (4.6, -28.0), (-6.6, -27.4), (-7.6, -38.0), (-6.6, -50.0), (-3.6, -56.0)]))
    f.add(cap((0.6, -61.0), (0.2, -55.0), 2.6, 3.0))
    head_side(f, hx, hy, beard=True)
    f.add(sm([(-3.6, -74.0), (1.4, -74.6), (4.8, -71.6), (2.0, -71.0), (-3.0, -70.0), (-5.6, -64.0), (-5.8, -70.0)]))
    f.add(cap((-2.0, -28.0), (14.0, -27.0), 4.4, 3.4))
    f.add(cap((14.0, -27.0), (15.4, -4.0), 3.2, 2.0))
    f.add(cap((15.0, -2.0), (19.4, -0.8), 1.8, 1.3))
    f.add(sm([(5.0, -54.0), (7.4, -44.0), (8.6, -34.0), (16.6, -32.0), (18.0, -24.0), (17.4, -8.0, C), (13.0, -8.0, C), (11.0, -22.0),
              (-7.4, -22.0, C), (-8.0, -38.0), (-6.4, -52.0)]))
    arm(f, (0.4, -53.0), (6.0, -42.0), (14.0, -41.0), (16.0, -41.0))
    f.line([(0.0, -50.0), (4.6, -41.6), (13.0, -39.6)])
    f.add(sm([(-8.0, -30.0), (-8.0, -22.0), (4.0, -22.0), (4.0, -30.0)]))
    return f


def sheep():
    f = Fig()
    wool = []
    for k in range(14):
        a = math.radians(180 + k * 180 / 13)
        wool.append((-2.0 + 14.0 * math.cos(a), -17.0 + 8.4 * math.sin(a)))
    body = sm(wool + [(12.0, -14.0), (8.0, -9.6), (-8.0, -9.6), (-15.0, -13.0)])
    f.add(body)
    for x in (-10.0, -6.0, 6.0, 9.6):
        f.add(cap((x, -11.0), (x + 0.4, -0.6), 1.2, 0.9))
    f.add(ell((14.8, -22.0), 3.6, 2.6, 25))
    f.add(ell((12.6, -24.0), 1.6, 1.0, -30))
    f.line([(-12.0, -20.0), (-9.0, -22.0), (-6.0, -20.0), (-3.0, -22.0), (0.0, -20.0)])
    return f


def porter():
    """walking right with a basket of doves on his shoulder"""
    f = walker(staff=False, hood=False)
    f.add(sm([(-3.2, -99.6), (2.6, -100.2), (6.0, -97.2), (3.0, -96.4), (-3.0, -95.0), (-6.6, -90.0), (-7.0, -95.6)]))
    f.add(sm([(-14.0, -98.0, C), (-14.6, -110.0, C), (-1.0, -112.0, C), (-0.4, -100.0, C)]))
    f.line([(-11.0, -99.0), (-11.4, -110.6)])
    f.line([(-7.6, -99.4), (-7.8, -111.2)])
    f.line([(-4.2, -99.8), (-4.2, -111.6)])
    arm(f, (0.0, -79.0), (-5.0, -88.0), (-6.0, -98.0), (-6.0, -100.0), r=(2.4, 2.0, 1.6), hr=(1.8, 2.1))
    return f


POSES = dict(walker=walker, talker=talker, back=back_view, lamb=lamb_carrier, jar=jar_woman, child=child, elder=elder,
             mother=mother, seated=seated, sheep=sheep, porter=porter)
_CACHE = {}


def figure(name, **kw):
    key = (name, tuple(sorted(kw.items())))
    if key not in _CACHE:
        _CACHE[key] = POSES[name](**kw).build()
    return _CACHE[key]


def _tf(g, x, y, s, flip, lean):
    sx = -s if flip else s
    g = affinity.skew(g, xs=-lean, origin=(0, 0)) if lean else g
    return affinity.affine_transform(g, [sx, 0, 0, s, x, y])


def place(board, name, x, y, h, z, group='crowd', flip=False, lean=0.0, cls=None, detail_min=34.0, inner_cls='hatch',
          prop_cls='hatch', kw=None):
    """Add a figure (feet at x, y; height h) as its own occluding item."""
    sil, inner, props = figure(name, **(kw or {}))
    s = h / 100.0
    silt = _tf(sil, x, y, s, flip, lean)
    it = board.item(z, group, f'{name}@{x:.0f},{y:.0f}')
    c = cls or ('detail' if h >= 30 else 'hatch')
    for r in rings(silt, 0.2):
        it.add(c, r)
    if h >= detail_min:
        for ln in inner:
            g = _tf(LineString(ln), x, y, s, flip, lean)
            it.add(inner_cls, list(g.coords))
    for ln in props:
        g = _tf(LineString(ln), x, y, s, flip, lean)
        it.add(prop_cls, list(g.coords))
    it.occlude(silt)
    return it
