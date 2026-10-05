"""Detailed figures for a02-temple (foreground vignettes) and a05-soldiers.

A FigDraw is a list of Pieces from back to front, authored at height ~360 (feet at y=0, head top near
y=-360, profile figures face right).  When placed on a Board:
  * the union of all pieces is the silhouette -> ONE continuous `line` stroke (cheap for the hand),
  * each piece's outline where it lies inside the silhouette and in front of earlier pieces -> `detail`,
  * explicit inner strokes (face, fingers, belts) -> `detail`; texture/folds -> `hatch`,
  * shade regions -> zig-zag `hatch`; optional accent fill per piece.
"""
import math
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely import affinity
from a02a05_tools import sp, to_poly, rings, _lines_of, _polys_of, plen, zigzag

C = 1


class Piece:
    def __init__(self, name, outline, inner=(), hatch=(), shade=(), fill=None, edge=True, sil=True):
        self.name = name
        self.outline = outline            # dense closed polyline
        self.inner = list(inner)          # detail strokes
        self.hatch = list(hatch)          # hatch strokes
        self.shade = list(shade)          # (polygon pts, angle, spacing[, cross])
        self.fill = fill
        self.edge = edge                  # draw its outline where it overlaps earlier pieces
        self.sil = sil                    # contributes to the silhouette


class FigDraw:
    def __init__(self):
        self.pieces = []
        self.extra_detail = []            # free detail strokes drawn last (not clipped inside the figure)
        self.extra_hatch = []

    def piece(self, name, pts, **kw):
        outline = sp(pts, closed=True, step=0.9)
        p = Piece(name, outline, **kw)
        self.pieces.append(p)
        return p

    # ------------------------------------------------------------------ placement
    def place(self, board, x, y, s, z, group='fig', flip=False, sil_cls='line', edge_cls='detail', inner_cls='detail',
              gap=1.6, name='fig', accent=None):
        sx = -s if flip else s

        def T(pts):
            return [(x + p[0] * sx, y + p[1] * s) for p in pts]

        polys = [to_poly(T(p.outline)) for p in self.pieces]
        sil = unary_union([g for g, p in zip(polys, self.pieces) if p.sil]).buffer(0.25).buffer(-0.25)
        it = board.item(z, group, name)
        it.occlude(sil)
        for r in rings(sil, 2.0):
            it.add(sil_cls, r)
        silb = sil.exterior.buffer(gap * 0.9) if hasattr(sil, 'exterior') else unary_union([q.exterior for q in _polys_of(sil)]).buffer(gap * 0.9)
        n = len(self.pieces)
        fronts = []
        acc = None
        for i in range(n - 1, -1, -1):
            fronts.append(acc)
            acc = polys[i] if acc is None else acc.union(polys[i])
        fronts = fronts[::-1]        # fronts[i] = union of pieces in front of i
        for i, (p, g) in enumerate(zip(self.pieces, polys)):
            fr = fronts[i]
            frb = fr.buffer(gap) if fr is not None else None
            if p.edge and i > 0:
                behind = unary_union(polys[:i])
                e = LineString(list(g.exterior.coords)).intersection(behind.buffer(-0.6))
                e = e.difference(silb)
                if frb is not None:
                    e = e.difference(frb)
                for ln in _lines_of(e):
                    if plen(ln) > 3:
                        it.add(edge_cls, ln)
            for q in p.inner:
                ls = LineString(T(q))
                if frb is not None:
                    ls = ls.difference(frb)
                for ln in _lines_of(ls):
                    if plen(ln) > 1.5:
                        it.add(inner_cls, ln)
            for q in p.hatch:
                ls = LineString(T(q))
                if frb is not None:
                    ls = ls.difference(fr)
                for ln in _lines_of(ls):
                    if plen(ln) > 1.0:
                        it.add('hatch', ln)
            for sh in p.shade:
                reg = to_poly(T(sh[0])).intersection(g)
                if fr is not None:
                    reg = reg.difference(fr.buffer(gap * 0.6))
                if not reg.is_empty:
                    it.hatch(reg, angle=(sh[1] if not flip else 180 - sh[1]), spacing=sh[2] * s / 1.0,
                             cross=((sh[3] if not flip else 180 - sh[3]) if len(sh) > 3 and sh[3] is not None else None),
                             cross_spacing=sh[2] * s * 1.3, group=None)
            if p.fill or (accent and p.name in accent):
                reg = g if fr is None else g.difference(fr)
                for q in _polys_of(reg):
                    if q.area > 6:
                        it.fill(list(q.exterior.coords), p.fill or accent[p.name], cls='hatch')
        for q in self.extra_detail:
            it.add(inner_cls, T(q))
        for q in self.extra_hatch:
            it.add('hatch', T(q))
        return it


# ============================================================================ figures
def scallop(cx, cy, rx, ry, n, amp, a0=0.0, a1=360.0, rot=0.0, phase=0.0):
    """points of a woolly (scalloped) ellipse arc"""
    pts = []
    m = n * 6
    for k in range(m + 1):
        a = math.radians(a0 + (a1 - a0) * k / m)
        b = 1.0 + amp * abs(math.sin((k / 6.0) * math.pi + phase))
        x, y = rx * math.cos(a) * b, ry * math.sin(a) * b
        cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return pts


def lean_pts(pts, lean, pivot_y=-180.0):
    """shear points above pivot_y forward by `lean` (units per 100 of height)"""
    return [((p[0] + max(0.0, (pivot_y - p[1])) * lean / 100.0), p[1]) + tuple(p[2:]) for p in pts]


def father_with_lamb():
    """Pilgrim walking right toward the temple, a young Passover lamb cradled against his chest."""
    F = FigDraw()
    LE = 5.0                                  # forward lean of the upper body (per 100 units)
    Lp = lambda pts: lean_pts(pts, LE)
    # back (left) leg below the tunic, heel lifted as he pushes off
    F.piece('back_leg', [(-6, -78), (-12, -58), (-24, -38), (-34, -24), (-36, -14, C), (-24, -6), (-14, -3), (-11, 0, C),
                         (-34, 0), (-48, -5), (-58, -12, C), (-57, -20), (-49, -26), (-40, -42), (-31, -62), (-27, -80)],
            inner=[[(-37, -17), (-28, -9)], [(-46, -11), (-39, -5)]],
            shade=[([(-28, -80), (-8, -80), (-30, -32), (-48, -26)], 70, 3.2)])
    # tunic: shoulders to the shins
    F.piece('tunic', Lp([(-20, -296), (-6, -302), (8, -300), (18, -290), (24, -272), (26, -250), (25, -226), (27, -200),
                         (33, -160), (40, -120), (46, -88), (48, -74, C), (30, -68), (8, -66), (-14, -68), (-32, -74, C),
                         (-32, -110), (-31, -160), (-29, -205), (-28, -236), (-30, -262), (-28, -284)]),
            hatch=[Lp([(34, -112), (40, -92), (44, -78)]), Lp([(22, -112), (26, -92), (27, -72)]), Lp([(-18, -112), (-21, -92), (-23, -72)])])
    # himation hanging from both shoulders like a shawl: long folds down the back, front edge falling past the arm
    F.piece('mantle', Lp([(-22, -300), (-8, -304), (4, -300), (8, -288), (6, -270), (8, -250), (12, -228), (16, -200),
                          (18, -170), (16, -140), (14, -118, C), (2, -112), (-14, -106), (-30, -100), (-40, -96, C),
                          (-42, -120), (-41, -160), (-38, -200), (-37, -236), (-36, -262), (-32, -284)]),
            inner=[Lp([(-28, -270), (-30, -230), (-31, -190), (-32, -150), (-36, -108)]),
                   Lp([(-12, -262), (-14, -220), (-14, -180), (-16, -140), (-20, -110)]),
                   Lp([(4, -250), (2, -210), (0, -170), (-2, -132)])],
            hatch=[Lp([(-40, -98), (-43, -86)]), Lp([(-41, -97), (-40, -85)]), Lp([(-39, -98), (-37, -87)]), Lp([(-42, -98), (-46, -89)]),
                   Lp([(-20, -268), (-22, -226), (-23, -186), (-24, -146), (-28, -108)]),
                   Lp([(-4, -262), (-6, -216), (-7, -176), (-8, -136)])],
            shade=[(Lp([(-42, -270), (-30, -268), (-32, -104), (-41, -98)]), 78, 2.8),
                   (Lp([(-14, -250), (-6, -250), (-10, -110), (-18, -108)]), 80, 3.6)])
    # front (right) leg striding forward, foot flat in a sandal
    F.piece('front_leg', [(18, -74), (38, -74), (40, -52), (41, -30), (43, -18), (50, -12), (63, -7), (74, -3), (76, 0, C),
                          (31, 0, C), (29, -8), (27, -26), (22, -52)],
            inner=[[(43, -13), (51, -4)], [(35, -9), (37, -1)], [(56, -8), (66, -4)]],
            shade=[([(18, -74), (27, -74), (31, -10), (29, 0), (23, -40)], 75, 3.0)])
    F.piece('neck', Lp([(-12, -314), (8, -316), (12, -298), (0, -290), (-16, -294)]), edge=False)
    profile_head(F, -18 + 0.05 * 180, -364, 1.0, beard='full', hair='long', tilt=5, name='head')
    # the lamb, curled against his chest: woolly body, head raised, legs folded
    body = Lp(scallop(26, -258, 34, 22, 9, 0.07, a0=0, a1=360, rot=-8))
    F.piece('lamb', body,
            hatch=[Lp([(4, -268), (10, -272), (16, -267), (22, -272), (28, -267), (34, -272), (40, -267)]),
                   Lp([(2, -254), (8, -258), (14, -253), (20, -258), (26, -253), (32, -258), (38, -253), (46, -257)]),
                   Lp([(8, -242), (14, -246), (20, -241), (26, -246), (32, -241), (40, -245)])],
            shade=[(Lp([(-10, -252), (60, -252), (50, -236), (0, -236)]), 15, 2.4)])
    F.piece('lamb_head', Lp([(46, -276), (52, -290), (58, -298), (66, -301), (72, -299), (78, -292), (82, -284, C),
                             (80, -279), (74, -277), (66, -276), (58, -272), (52, -266)]),
            inner=[Lp([(66, -293.6), (67.8, -293.0), (66.8, -291.6)]), Lp([(80, -282.6), (78.6, -281.4)]),
                   Lp([(76.4, -278.4), (72.6, -278.2)])])
    F.piece('lamb_ear', Lp([(58, -294), (50, -300), (42, -302), (40, -298), (48, -293), (55, -290)]))
    F.piece('lamb_legs', Lp([(30, -240), (38, -238), (40, -226), (42, -214, C), (36, -213, C), (34, -224), (30, -232)]),
            inner=[Lp([(36.4, -217), (41.6, -217)])])
    # near arm: sleeve from under the mantle, forearm cradling the lamb, hand under its rump
    F.piece('arm', Lp([(-10, -276), (4, -278), (8, -262), (6, -244), (14, -238), (32, -236), (46, -238), (54, -242),
                       (58, -236), (52, -229), (40, -226), (20, -224), (2, -222), (-10, -226), (-14, -242), (-14, -260)]),
            inner=[Lp([(-12, -244), (-2, -240), (8, -246)]), Lp([(48, -238), (51, -231)]), Lp([(52, -240), (56, -234)])],
            hatch=[Lp([(-8, -260), (-9, -244)]), Lp([(-4, -262), (-5, -246)])])
    # far hand on the lamb's back
    F.piece('far_hand', Lp([(20, -280), (28, -286), (38, -286), (44, -282), (40, -276), (30, -274), (22, -274)]),
            inner=[Lp([(30, -284), (34, -278)]), Lp([(35, -285), (39, -279)])])
    return F


def son_walking():
    """Boy of about eight walking right beside his father, looking up, a dove cupped in his hands."""
    F = FigDraw()
    F.piece('far_leg', [(-8, -60), (2, -58), (-4, -36), (-14, -16), (-18, -8), (-8, -4, C), (-8, 0, C), (-26, -1, C), (-32, -6),
                        (-28, -14), (-20, -36), (-16, -58)])
    F.piece('tunic', [(-14, -184), (-2, -190), (10, -186), (16, -176), (17, -150), (16, -124), (20, -96), (26, -66, C),
                      (10, -58), (-6, -58), (-22, -62, C), (-20, -100), (-17, -130), (-17, -160)],
            inner=[[(-17, -128), (0, -125), (16, -127)]],
            hatch=[[(4, -120), (10, -94), (18, -70)], [(-8, -120), (-10, -90), (-14, -66)]],
            shade=[([(-22, -124), (-4, -124), (-8, -62), (-23, -62)], 70, 3.6)])
    F.piece('near_leg', [(6, -62), (16, -62), (18, -36), (22, -16), (24, -8), (34, -4), (36, 0, C), (14, 0, C), (14, -8), (10, -30)],
            inner=[[(20, -8), (27, -3)]])
    F.piece('neck', [(-8, -198), (6, -200), (8, -186), (-8, -184)], edge=False)
    F.piece('head', [(0, -238), (10, -236), (16, -230), (19, -222), (21, -218), (25, -212, C), (21, -209), (21, -205),
                     (19, -201), (12, -196), (2, -195), (-8, -198), (-15, -205), (-19, -216), (-18, -228), (-11, -236)],
            inner=[[(11, -222), (14, -223.6), (16.6, -222)], [(12, -218.2), (15.4, -219.0), (17.0, -217.8), (14.8, -216.8), (12.4, -217.4)],
                   [(15.4, -218.4), (15.2, -217.4)], [(19.0, -205.4), (16.6, -205.0)],
                   [(-3, -220), (-1, -223), (2, -220), (2, -215), (-1, -213), (-3, -215)], [(18.6, -211.6), (20.4, -210.0)]],
            hatch=[[(-16, -226), (-6, -233), (6, -234)], [(-17, -216), (-8, -226), (2, -230)], [(-16, -206), (-10, -214)]])
    F.piece('arms', [(-10, -184), (4, -186), (8, -170), (16, -156), (26, -158), (32, -164), (34, -156), (28, -146),
                     (14, -142), (2, -150), (-6, -164)],
            inner=[[(-4, -176), (6, -158), (16, -150)]])
    F.piece('dove', [(22, -164), (28, -172), (36, -174), (42, -170, C), (46, -171), (42, -166), (38, -160), (28, -156)],
            inner=[[(30, -166), (36, -167), (40, -164)], [(41.6, -170.4), (41.6, -170.0)]])
    return F


# ============================================================================ heads
def profile_head(F, ox, oy, s=1.0, beard='full', hair='long', cover=None, age=0.0, tilt=0.0, mouth=0.0, brow=0.0,
                 name='head', hat=None, lod=2):
    """Adds a profile head facing right.  (ox, oy) = top of the skull, s = head height / 48.
    beard: None | 'full' | 'long';  hair: 'long' | 'short' | None;  cover: None | 'mantle' | 'veil'
    age 0..1 deepens lines; mouth -1..1 (frown..smile); brow -1..1 (worried..calm)."""
    def T(pts):
        out = []
        ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        for p in pts:
            x, y = p[0] * s, p[1] * s
            xr, yr = x * ca - y * sa, x * sa + y * ca
            out.append((ox + xr, oy + yr) + tuple(p[2:]))
        return out
    # skull + face contour (x: back of skull 0 -> nose tip ~44; y: top 0 -> chin 48)
    face = [(22, 0), (31, 2), (37, 7), (39.4, 13), (40.4, 18), (40.9, 20.2), (39.9, 22.0, C), (41.6, 26.5), (44.6, 31.2, C),
            (42.4, 32.6), (40.4, 33.0, C), (41.3, 35.0), (41.6, 36.2), (40.0, 37.4, C), (40.8, 38.6), (40.0, 40.2),
            (38.4, 41.4, C), (39.6, 44.0), (38.8, 46.6), (35.4, 48.4), (29.0, 48.6), (23.0, 46.4), (18.0, 42.6),
            (12.0, 39.0), (6.0, 36.0), (1.6, 28.0), (0.0, 18.0), (2.6, 9.0), (9.0, 3.0)]
    pts = list(face)
    inner, hatch = [], []
    # ear
    inner.append([(19.6, 21.0), (16.8, 20.0), (14.6, 22.6), (14.8, 27.4), (17.2, 31.6), (19.8, 33.6), (21.0, 31.8)])
    inner.append([(17.6, 23.4), (16.8, 26.6), (18.4, 29.6)])
    # eye: upper lid, lower lid, iris; brow
    inner.append([(33.0, 22.6), (35.2, 21.4), (37.6, 22.2), (38.6, 23.6)])
    inner.append([(34.0, 24.6), (36.4, 25.0), (38.4, 23.8)])
    inner.append([(36.6, 22.0), (36.3, 24.6)])
    inner.append([(31.0, 19.2 - brow), (34.6, 17.8 - brow * 0.6), (38.0, 18.0), (40.0, 19.0)])
    # nostril wing and the cheek line
    inner.append([(39.0, 31.0), (38.0, 32.6), (39.6, 33.2)])
    inner.append([(37.6, 26.0), (35.6, 30.6), (36.0, 33.6)])
    # mouth
    inner.append([(40.2, 37.6), (37.6, 37.8 - mouth), (35.4, 37.2 - mouth * 1.6)])
    if age > 0:
        inner.append([(33.2, 26.6), (33.6, 28.4)])
        hatch.append([(32.6, 15.0), (37.4, 14.4)])
        hatch.append([(32.0, 13.0), (36.4, 12.0)])
    if beard:
        L = 55 if beard == 'full' else 64
        # beard replaces the jaw line; its lower edge is wavy (locks of hair)
        pts = [(22, 0), (31, 2), (37, 7), (39.4, 13), (40.4, 18), (40.9, 20.2), (39.9, 22.0, C), (41.6, 26.5), (44.6, 31.2, C),
               (42.4, 32.6), (40.4, 33.0, C), (42.2, 34.6), (42.8, 37.2), (41.2, 38.8), (42.6, 41.6), (42.8, 45.4),
               (41.0, L - 6.0), (40.6, L - 3.0, C), (37.6, L - 2.4), (36.0, L, C), (32.6, L - 1.4), (30.0, L - 0.2, C),
               (27.0, L - 2.6), (24.6, L - 2.0, C), (22.6, L - 5.6), (20.0, 44.4), (18.0, 38.4), (12.0, 37.0), (6.0, 35.0),
               (1.6, 28.0), (0.0, 18.0), (2.6, 9.0), (9.0, 3.0)]
        inner[-1] = [(40.8, 37.9), (38.6, 38.1 - mouth), (37.0, 37.7 - mouth * 1.6)]
        inner.append([(36.2, 33.8), (38.8, 34.8), (42.0, 35.2)])                  # moustache
        hatch += [[(24.6, 35.0), (25.4, 40.0), (27.6, 46.0), (27.0, L - 3.6)], [(28.6, 35.2), (30.0, 41.0), (32.2, 47.0), (32.6, L - 2.0)],
                  [(33.0, 38.6), (34.6, 44.0), (37.4, L - 3.0)], [(21.2, 38.0), (22.4, 44.0), (23.0, L - 7.0)],
                  [(37.8, 41.6), (39.6, 46.0), (40.0, L - 6.0)]]
        inner.append([(20.4, 33.4), (24.6, 31.6), (30.0, 31.6), (34.2, 33.2)])     # beard line on the cheek
    hh = []
    if hair == 'long':
        # hair from a slightly receding hairline, over the ear, falling in waves to the nape
        hpts = [(22, -1.4), (31.6, 0.8), (37.4, 6.0), (39.2, 10.4), (35.6, 9.4), (31.0, 10.2), (27.0, 11.0), (24.0, 13.6),
                (22.6, 17.4), (23.6, 22.0), (23.0, 27.0), (21.8, 33.0), (21.4, 38.0, C), (19.6, 44.0), (21.0, 50.0, C),
                (17.4, 54.0), (16.6, 60.0, C), (12.0, 61.4), (8.4, 64.6, C), (4.6, 60.4), (0.6, 58.6, C), (-0.6, 50.0),
                (-1.8, 40.0), (-2.4, 28.0), (-1.6, 16.0), (1.8, 7.0), (10.0, 1.0)]
        hh = [[(30.0, 3.6), (22.0, 6.0), (14.0, 11.4), (9.0, 20.0), (7.0, 32.0)],
              [(34.6, 6.6), (27.0, 8.0), (19.0, 13.0), (15.6, 24.0), (14.4, 38.0), (12.6, 50.0)],
              [(22.0, 2.0), (12.0, 5.6), (4.6, 14.0), (2.0, 26.0), (2.4, 42.0), (4.0, 54.0)],
              [(19.6, 30.0), (17.4, 40.0), (16.0, 52.0)], [(9.0, 40.0), (8.6, 52.0), (10.0, 60.0)]]
    elif hair == 'short':
        hpts = [(22, -1.2), (31.4, 0.8), (37.0, 6.0), (38.8, 10.2), (34.0, 9.4), (28.0, 10.0), (23.6, 12.6), (21.0, 17.0),
                (20.0, 21.6, C), (15.0, 21.0), (10.0, 24.0), (6.0, 30.0), (2.6, 33.4), (-0.8, 25.0), (-0.6, 14.0), (3.0, 6.0),
                (10.0, 0.8)]
        hh = [[(28.0, 3.4), (18.0, 7.0), (10.0, 14.0), (6.0, 24.0)], [(20.0, 2.0), (10.0, 6.0), (3.0, 16.0), (1.4, 26.0)],
              [(34.0, 6.0), (26.0, 7.6), (19.0, 12.6), (16.0, 19.0)]]
    else:
        hpts = None
    if cover == 'mantle':
        # prayer mantle drawn over the head: frames the face and falls behind to the shoulders
        hpts = [(20, -3.0), (30.0, -1.6), (37.0, 3.6), (40.2, 10.6), (36.6, 12.6), (35.0, 16.0), (33.0, 22.0), (31.0, 30.0),
                (29.0, 38.0), (27.0, 50.0), (26.0, 62.0), (10.0, 70.0), (-6.0, 66.0), (-6.0, 46.0), (-5.0, 26.0),
                (-2.4, 10.0), (6.0, 1.0)]
        hh = [[(22.0, 2.0), (12.0, 10.0), (4.0, 28.0), (2.0, 50.0)], [(28.0, 4.0), (18.0, 14.0), (12.0, 32.0), (12.0, 56.0)],
              [(16.0, 1.0), (4.0, 12.0), (-2.0, 30.0), (-2.0, 52.0)], [(34.0, 8.0), (29.0, 18.0), (26.0, 34.0), (22.0, 54.0)]]
    if cover == 'veil':
        hpts = [(20, -2.6), (30.0, -1.2), (36.4, 3.6), (39.0, 10.0), (35.6, 12.0), (33.8, 18.0), (32.0, 28.0), (30.0, 40.0),
                (28.0, 56.0), (12.0, 64.0), (-4.0, 60.0), (-4.0, 40.0), (-3.0, 22.0), (-1.0, 9.0), (6.0, 1.0)]
        hh = [[(24.0, 2.0), (14.0, 10.0), (6.0, 30.0), (4.0, 52.0)], [(16.0, 1.0), (6.0, 12.0), (0.0, 30.0)],
              [(30.0, 6.0), (25.0, 20.0), (22.0, 40.0)]]
    if lod < 2:
        # keep: ear outline, upper lid+iris, brow, mouth; demote the rest to hatch
        keep_idx = {0, 2, 5}
        mouth_stroke = inner[8] if len(inner) > 8 else None
        kept = [q for i, q in enumerate(inner) if i in keep_idx]
        demoted = [q for i, q in enumerate(inner) if i not in keep_idx and q is not mouth_stroke]
        eye = inner[2] + inner[3][::-1]
        kept = [inner[0], eye, inner[5]] + ([mouth_stroke] if mouth_stroke else [])
        demoted = [q for i, q in enumerate(inner) if i not in (0, 2, 3, 5, 8)]
        inner, hatch = kept, hatch + demoted
    head = F.piece(name, T(pts), inner=[T(q) for q in inner], hatch=[T(q) for q in hatch])
    if hpts:
        F.piece(name + '_hair', T(hpts), edge=True, inner=[], hatch=[T(q) for q in hh])
    return head


# ============================================================================ hands, feet, lamb
def _place(pts, x, y, ang, s, mirror=False):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    out = []
    for p in pts:
        px, py = p[0] * s, p[1] * s * (-1 if mirror else 1)
        out.append((x + px * ca - py * sa, y + px * sa + py * ca) + tuple(p[2:]))
    return out


HANDS = {
    # wrist at (0,0), fingers toward +x; y+ is the palm/little-finger side
    'grip': dict(out=[(0, -7.5), (6, -9.5), (13, -10.6), (19, -10.0), (23.4, -7.2), (25.0, -2.0), (24.0, 4.0), (20.4, 8.6),
                      (14.0, 9.8), (8.0, 9.0), (2.0, 8.0)],
                 inner=[[(12.6, -10.2), (16.0, -6.6), (21.0, -5.2)], [(20.6, -1.0), (24.2, -0.6)], [(19.6, 3.6), (23.2, 3.8)],
                        [(17.0, 7.4), (21.2, 7.8)]]),
    'open': dict(out=[(0, -7.0), (8, -8.2), (13.0, -9.0), (15.6, -15.2), (19.0, -17.4), (20.6, -15.0), (18.6, -9.6),
                      (26.0, -9.0), (34.0, -9.6), (38.6, -8.4), (37.6, -6.0), (30.0, -4.6), (35.6, -3.6), (36.0, -1.2),
                      (28.0, 0.2), (33.0, 1.6), (32.4, 3.8), (24.0, 4.0), (18.0, 6.6), (8.0, 7.6), (1.0, 7.0)],
                 inner=[[(18.0, -9.6), (14.0, -6.4)], [(24.0, -5.0), (29.6, -4.8)], [(23.0, 0.0), (27.6, 0.2)]]),
    'rest': dict(out=[(0, -7.0), (8, -8.6), (16.0, -9.0), (24.0, -8.0), (30.0, -5.4), (33.0, -1.0), (31.0, 3.0), (26.0, 5.6),
                      (18.0, 7.6), (9.0, 8.0), (1.0, 7.0)],
                 inner=[[(16.0, -8.6), (14.0, -4.0), (16.6, -1.0)], [(22.0, -2.6), (30.6, -1.6)], [(20.0, 2.0), (28.0, 3.0)]]),
}


def hand(F, name, kind, x, y, ang, s=1.0, mirror=False):
    h = HANDS[kind]
    return F.piece(name, _place(h['out'], x, y, ang, s, mirror), inner=[_place(q, x, y, ang, s, mirror) for q in h['inner']])


def sandal_foot(F, name, x, y, s=1.0, push=False, mirror=False, shade=True):
    """profile foot facing +x with its heel at (x, y) on the ground; push=True lifts the heel (toes on the ground)"""
    if not push:
        pts = [(-2, -15), (4, -18), (14, -16), (24, -12), (36, -7), (46, -4), (50, -1.5), (50, 0, C), (2, 0, C), (-3, -4)]
        inner = [[(10, -14), (14, -3)], [(24, -11), (30, -2)], [(-1, -4), (48, -1.8)]]
    else:
        pts = [(-3, -26), (4, -27), (13, -20), (24, -12), (36, -5), (44, -2), (46, 0, C), (26, 0, C), (12, -6), (2, -12, C),
               (-6, -16)]
        inner = [[(8, -21), (16, -8)], [(22, -12), (28, -4)]]
    P = [((x + p[0] * s * (-1 if mirror else 1)), y + p[1] * s) + tuple(p[2:]) for p in pts]
    I = [[(x + p[0] * s * (-1 if mirror else 1), y + p[1] * s) for p in q] for q in inner]
    return F.piece(name, P, inner=I)


def lamb_side(F, x, y, s=1.0, name='lamb', head_up=0.0):
    """young sheep trotting right; (x, y) = ground under its chest; height ~110*s"""
    def T(pts):
        return [(x + p[0] * s, y + p[1] * s) + tuple(p[2:]) for p in pts]
    F.piece(name + '_farlegs', T([(-42, -48), (-32, -48), (-31, -30), (-34, -16), (-30, -3), (-28, 0, C), (-36, 0, C),
                                  (-40, -14), (-38, -30), (-44, -44)]))
    F.piece(name + '_farleg2', T([(22, -48), (32, -48), (32, -30), (36, -14), (42, -3), (41, 0, C), (34, 0, C), (29, -14),
                                  (25, -30)]))
    body = scallop(-6, -64, 46, 24, 11, 0.06, a0=0, a1=360, rot=-3)
    curls = []
    for (cx, cy) in [(-36, -74), (-22, -78), (-8, -79), (6, -77), (-42, -62), (-28, -64), (-14, -66), (0, -65), (14, -63),
                     (-32, -51), (-18, -52), (-4, -53), (10, -52)]:
        curls.append(T([(cx - 3, cy + 1), (cx - 1.5, cy - 2.5), (cx + 2, cy - 2.5), (cx + 3, cy + 0.5)]))
    F.piece(name, T(body), hatch=curls, shade=[(T([(-52, -54), (36, -54), (30, -42), (-46, -42)]), 15, 2.8)])
    F.piece(name + '_leg1', T([(-32, -50), (-20, -50), (-19, -32), (-22, -16), (-18, -3), (-16, 0, C), (-25, 0, C), (-28, -14),
                               (-27, -30), (-32, -42)]),
            hatch=[T([(-26.0, -4.0), (-17.6, -4.0)])])
    F.piece(name + '_leg2', T([(26, -52), (38, -50), (37, -32), (40, -16), (47, -4), (47, 0, C), (38, 0, C), (34, -14),
                               (31, -30)]),
            hatch=[T([(38.4, -4.4), (46.4, -4.4)])])
    hu = head_up
    F.piece(name + '_head', T([(28, -76), (36, -90 - hu), (46, -100 - hu), (56, -104 - hu), (64, -100 - hu), (70, -92 - hu),
                               (73, -86 - hu, C), (69, -82 - hu), (60, -80 - hu), (52, -74 - hu), (44, -64), (34, -58)]),
            inner=[T([(57.6, -94.6 - hu), (59.6, -94.0 - hu), (58.4, -92.6 - hu)])],
            hatch=[T([(71.0, -88.0 - hu), (69.0, -86.6 - hu)]), T([(68.0, -83.6 - hu), (63.4, -83.4 - hu)])])
    F.piece(name + '_ear', T([(50, -99 - hu), (42, -98 - hu), (34, -94 - hu), (33, -90 - hu), (40, -91 - hu), (48, -94 - hu)]))
    F.piece(name + '_tail', T([(-52, -72), (-58, -70), (-60, -62), (-56, -58), (-51, -62)]))


def family_with_lamb(lod=1):
    """Father walking right, his hand on his son's shoulder; the boy leads the Passover lamb on a cord."""
    F = FigDraw()
    LE = 3.0
    Lp = lambda pts: lean_pts(pts, LE)
    # ---------------- father: back foot pushing off (ankle + foot in one piece)
    F.piece('f_backfoot', [(-30, -30), (-20, -30), (-24, -18), (-16, -10), (-6, -4), (-2, 0, C), (-26, 0), (-40, -6),
                           (-50, -14, C), (-46, -22), (-36, -26)],
            hatch=[[(-30, -18), (-22, -9)], [(-40, -14), (-33, -6)]])
    F.piece('f_tunic', Lp([(-14, -306), (-26, -284), (-29, -250), (-25, -212), (-29, -178), (-32, -120), (-35, -64), (-39, -26, C),
                           (-12, -21), (16, -23), (40, -28, C), (36, -66), (30, -112), (26, -160), (25, -204), (27, -232),
                           (26, -262), (20, -286), (10, -302)]),
            hatch=[Lp([(32, -60), (36, -40), (38, -30)]), Lp([(22, -60), (24, -40), (25, -26)]), Lp([(-16, -60), (-18, -40), (-20, -24)]),
                   Lp([(4, -64), (2, -44), (2, -24)])])
    F.piece('f_frontfoot', [(14, -30), (26, -30), (28, -16), (36, -9), (50, -5), (60, -2), (62, 0, C), (12, 0, C), (9, -6), (12, -18)],
            hatch=[[(22, -15), (28, -3)], [(38, -8), (44, -1)]])
    F.piece('f_mantle', Lp([(-18, -314), (-2, -314), (8, -304), (12, -286), (8, -262), (6, -222), (8, -172), (10, -126),
                            (12, -96, C), (-8, -90), (-28, -84), (-42, -80, C), (-42, -126), (-38, -200), (-35, -252),
                            (-31, -286), (-24, -306)]),
            inner=[Lp([(-28, -280), (-31, -230), (-33, -180), (-35, -130), (-38, -88)]),
                   Lp([(-10, -288), (-13, -230), (-15, -170), (-17, -120), (-19, -92)])],
            hatch=[Lp([(-42, -82), (-46, -70)]), Lp([(-41, -82), (-40, -69)]), Lp([(-43, -82), (-48, -72)]),
                   Lp([(12, -98), (14, -86)]), Lp([(11, -98), (9, -86)]), Lp([(13, -97), (17, -88)]),
                   Lp([(0, -282), (-2, -230), (-2, -180), (-1, -130), (2, -100)])],
            shade=[(Lp([(-44, -286), (-30, -284), (-36, -86), (-44, -82)]), 80, 2.6),
                   (Lp([(-22, -270), (-12, -270), (-18, -94), (-26, -92)]), 82, 3.4)])
    F.piece('f_neck', Lp([(-10, -316), (8, -318), (12, -300), (0, -294), (-14, -298)]), edge=False)
    profile_head(F, -17 + 0.03 * 180, -364, 1.0, beard='full', hair='long', tilt=9, mouth=0.6, name='f_head', lod=lod)
    # near arm reaching forward to the boy's shoulder (sleeve to the elbow, then bare forearm)
    F.piece('f_arm', [(-2, -292), (12, -294), (24, -278), (36, -258), (44, -246), (60, -230), (78, -216), (82, -208),
                      (76, -202), (58, -214), (38, -228), (26, -236), (12, -252), (0, -266), (-6, -282)],
            inner=[[(30, -251), (38, -240), (45, -246)]],
            hatch=[[(6, -282), (20, -262)], [(2, -276), (16, -256)], [(14, -278), (24, -264)]])
    # ---------------- lamb trotting ahead
    lamb_side(F, 236, 0, 0.95, name='lamb', head_up=4)
    # ---------------- son (nearer to us)
    F.piece('s_backleg', [(74, -96), (86, -96), (78, -62), (68, -34), (64, -20), (60, -12), (52, -4), (48, 0, C), (36, 0),
                          (30, -6, C), (36, -12), (46, -20), (54, -34), (62, -62)],
            hatch=[[(52, -12), (58, -4)], [(40, -6), (46, -1)]])
    F.piece('s_tunic', [(80, -230), (70, -210), (67, -184), (69, -152), (66, -126), (62, -94, C), (82, -88), (106, -94, C),
                        (102, -124), (104, -152), (106, -184), (104, -210), (96, -226)],
            inner=[[(68, -150), (86, -146), (104, -150)]],
            hatch=[[(96, -140), (100, -116), (104, -98)], [(84, -140), (84, -116), (82, -92)], [(72, -142), (70, -118), (66, -98)]],
            shade=[([(64, -150), (78, -150), (76, -92), (62, -94)], 72, 3.0)])
    F.piece('s_frontleg', [(94, -96), (107, -96), (109, -72), (110, -46), (112, -24), (114, -14), (124, -8), (136, -4),
                           (138, 0, C), (104, 0, C), (103, -10), (100, -40), (97, -70)],
            hatch=[[(110, -12), (116, -3)], [(122, -7), (126, -2)]])
    F.piece('s_neck', [(80, -236), (94, -236), (96, -222), (82, -220)], edge=False)
    profile_head(F, 74, -270, 0.84, beard=None, hair='short', tilt=-14, mouth=1.2, name='s_head', lod=lod)
    F.piece('s_arm', [(84, -218), (96, -220), (104, -200), (112, -178), (124, -164), (136, -158), (138, -150), (124, -150),
                      (110, -156), (98, -170), (88, -192)],
            hatch=[[(92, -196), (100, -180)]])
    hand(F, 's_hand', 'grip', 134, -155, -8, 0.62)
    hand(F, 'f_hand', 'rest', 78, -212, 38, 0.95)
    F.extra_detail.append(sp([(150, -152), (172, -128), (196, -112), (226, -98), (252, -88)], step=1.0))
    return F
