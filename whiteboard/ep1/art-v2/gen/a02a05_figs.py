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
from a02a05_tools import sp, to_poly, rings, _lines_of, _polys_of, plen, zigzag, RUST, GOLD, CLOAK, BLUE

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


class RawPiece:
    """A ready-made drawing (strokes + occluder polygon), e.g. a head from a_people.head34."""

    def __init__(self, name, strokes, occ):
        self.name, self.strokes, self.occ = name, strokes, occ
        self.inner, self.hatch, self.shade, self.fill, self.edge, self.sil = [], [], [], None, False, True
        self.outline = None


class FigDraw:
    def __init__(self):
        self.pieces = []
        self.extra_detail = []            # free detail strokes drawn last (not clipped inside the figure)
        self.min_edge = 16.0              # piece edges shorter than this (authoring units) become hatch
        self.close = 1.2                  # morphological closing of the silhouette (authoring units)
        self.extra_hatch = []
        self.clip_hatch = False           # clip each piece's hatch strokes to its own outline

    def piece(self, name, pts, rigid=False, **kw):
        if rigid:
            outline = [tuple(q[:2]) for q in pts] + [tuple(pts[0][:2])]
        else:
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

        def G(p):
            if isinstance(p, RawPiece):
                g = unary_union([to_poly(T(q)) for q in p.occ if len(q) >= 3])
                return g if not g.is_empty else Point(x, y).buffer(0.01)
            return to_poly(T(p.outline))
        polys = [G(p) for p in self.pieces]
        sil = unary_union([g for g, p in zip(polys, self.pieces) if p.sil]).buffer(self.close * s).buffer(-self.close * s)
        it = board.item(z, group, name)
        it.occlude(sil)
        rs = rings(sil, 2.0)
        for k, r in enumerate(rs):
            it.add(sil_cls if (k == 0 or plen(r) > 220 * s) else 'detail', r)
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
            if isinstance(p, RawPiece):
                for cls, q in p.strokes:
                    ls = LineString(T(q)) if len(q) > 1 else None
                    if ls is None:
                        continue
                    if frb is not None:
                        ls = ls.difference(frb if cls != 'hatch' else fr)
                    if cls == 'line':
                        ls = ls.difference(silb)
                        cls = edge_cls
                    for ln in _lines_of(ls):
                        if plen(ln) > 1.2:
                            it.add(cls if cls != 'detail' else inner_cls, ln)
                continue
            if p.edge and i > 0:
                behind = unary_union(polys[:i])
                ext = unary_union([LineString(list(q.exterior.coords)) for q in _polys_of(g)])
                e = ext.intersection(behind.buffer(-0.6))
                e = e.difference(silb)
                if frb is not None:
                    e = e.difference(frb)
                for ln in _lines_of(e):
                    L = plen(ln)
                    if L > 3:
                        it.add(edge_cls if L >= self.min_edge * s else 'hatch', ln)
            for q in p.inner:
                ls = LineString(T(q))
                if frb is not None:
                    ls = ls.difference(frb)
                for ln in _lines_of(ls):
                    if plen(ln) > 1.5:
                        it.add(inner_cls, ln)
            for q in p.hatch:
                ls = LineString(T(q))
                if self.clip_hatch:
                    ls = ls.intersection(g.buffer(-0.8 * s))
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
        allp = unary_union(polys)
        for q in getattr(self, 'extra_line', []):
            ls = LineString(T(q))
            # the shaft passes behind the fist/hand pieces drawn later: clip by pieces whose name contains fist/hand
            hands = [g for g, p in zip(polys, self.pieces) if any(k in p.name for k in ('fist', 'hand'))]
            if hands:
                ls = ls.difference(unary_union(hands).buffer(gap))
            for ln in _lines_of(ls):
                if plen(ln) > 2:
                    it.add(sil_cls, ln)
        for p, g in zip(self.pieces, polys):
            if not p.sil and not isinstance(p, RawPiece):
                for r in rings(g, 1.0):
                    it.add(inner_cls, r)
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
                 name='head', hat=None, lod=2, mirror=False):
    """Adds a profile head facing right.  (ox, oy) = top of the skull, s = head height / 48.
    beard: None | 'full' | 'long';  hair: 'long' | 'short' | None;  cover: None | 'mantle' | 'veil'
    age 0..1 deepens lines; mouth -1..1 (frown..smile); brow -1..1 (worried..calm)."""
    def T(pts):
        out = []
        ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        for p in pts:
            x, y = p[0] * s, p[1] * s
            xr, yr = x * ca - y * sa, x * sa + y * ca
            if mirror:
                xr = 21.0 * s - (xr - 21.0 * s)
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


def scribe_speaking(lod=1):
    """Elder scribe facing right under his prayer mantle, phylactery on the brow, open hand making his point."""
    F = FigDraw()
    F.piece('backfoot', [(-30, -28), (-18, -28), (-16, -14), (-6, -7), (8, -3), (12, 0, C), (-32, 0, C), (-36, -6), (-33, -16)],
            hatch=[[(-22, -14), (-14, -4)]])
    F.piece('robe', [(-14, -306), (-25, -284), (-28, -250), (-26, -212), (-28, -175), (-30, -120), (-32, -64), (-36, -24, C),
                     (-10, -20), (20, -21), (34, -24, C), (32, -64), (28, -115), (25, -165), (24, -205), (25, -235), (24, -262),
                     (18, -288), (8, -304)],
            hatch=[[(26, -84), (28, -56), (30, -30)], [(10, -86), (10, -56), (10, -26)], [(-16, -86), (-18, -56), (-20, -26)]])
    F.piece('frontfoot', [(14, -28), (26, -28), (28, -14), (38, -7), (52, -3), (56, 0, C), (12, 0, C), (9, -6), (11, -16)],
            hatch=[[(22, -14), (30, -3)]])
    F.piece('mantle', [(-24, -300), (-6, -298), (12, -292), (20, -280), (21, -262), (17, -240), (15, -200), (17, -160),
                       (19, -124), (21, -100, C), (2, -96), (-20, -92), (-38, -88, C), (-38, -132), (-36, -200), (-34, -250),
                       (-31, -282)],
            inner=[[(-26, -276), (-29, -220), (-31, -160), (-33, -100)], [(0, -268), (-2, -210), (-2, -150), (0, -104)]],
            hatch=[[(21, -100), (22, -76)], [(20, -100), (18, -78)], [(22, -99), (26, -80)], [(-38, -88), (-41, -66)],
                   [(-37, -88), (-36, -66)], [(-39, -88), (-44, -70)], [(-14, -262), (-16, -200), (-17, -140), (-16, -100)]],
            shade=[([(-40, -282), (-28, -280), (-32, -92), (-40, -88)], 80, 2.6)])
    profile_head(F, -18, -366, 1.0, beard='long', hair=None, cover='mantle', age=1, tilt=-4, mouth=-0.8, brow=0.5,
                 name='head', lod=lod)
    # phylactery box on the brow, its strap under the mantle edge
    F.piece('tefillin', [(16.4, -357.0), (21.4, -358.6), (22.6, -353.0), (17.6, -351.6)])
    F.piece('arm', [(6, -272), (20, -276), (28, -252), (36, -234), (50, -242), (60, -250), (66, -244), (60, -232), (42, -220),
                    (28, -214), (20, -224), (12, -248)],
            hatch=[[(14, -258), (24, -236)], [(18, -264), (28, -244)]])
    hand(F, 'hand', 'open', 58, -244, -22, 0.95)
    return F


def scribe_listening(lod=1):
    """Younger scribe (authored facing right; place flipped) stroking his beard as he listens."""
    F = FigDraw()
    F.piece('backfoot', [(-30, -28), (-18, -28), (-16, -14), (-6, -7), (8, -3), (12, 0, C), (-32, 0, C), (-36, -6), (-33, -16)],
            hatch=[[(-22, -14), (-14, -4)]])
    F.piece('robe', [(-14, -304), (-24, -282), (-27, -250), (-24, -212), (-27, -175), (-29, -120), (-31, -64), (-34, -24, C),
                     (-8, -20), (20, -21), (32, -24, C), (30, -64), (27, -115), (24, -165), (23, -205), (24, -235), (23, -262),
                     (17, -288), (8, -302)],
            hatch=[[(24, -84), (26, -56), (28, -30)], [(8, -86), (8, -56), (8, -26)], [(-16, -86), (-18, -56), (-20, -26)]])
    F.piece('frontfoot', [(12, -28), (24, -28), (26, -14), (36, -7), (50, -3), (54, 0, C), (10, 0, C), (7, -6), (9, -16)],
            hatch=[[(20, -14), (28, -3)]])
    F.piece('mantle', [(-22, -304), (-4, -306), (10, -298), (18, -284), (20, -262), (16, -236), (12, -200), (14, -160),
                       (14, -124), (16, -104, C), (-4, -100), (-24, -96), (-36, -92, C), (-37, -132), (-35, -200), (-33, -250),
                       (-29, -284)],
            inner=[[(-24, -280), (-28, -220), (-30, -160), (-32, -100)], [(-2, -272), (-4, -210), (-4, -150), (-2, -108)]],
            hatch=[[(16, -104), (17, -80)], [(15, -104), (13, -82)], [(-36, -92), (-39, -70)], [(-35, -92), (-34, -70)]],
            shade=[([(-38, -284), (-26, -282), (-30, -96), (-38, -92)], 80, 2.6)])
    profile_head(F, -18, -364, 1.0, beard='full', hair='short', tilt=7, mouth=-0.3, brow=-0.8, name='head', lod=lod)
    # wrapped head-cloth (turban) over the short hair
    F.piece('turban', [(-20.0, -351.0), (-16.0, -362.0), (-4.0, -369.0), (10.0, -369.0), (19.0, -362.0), (22.0, -354.0),
                       (19.6, -350.4), (8.0, -353.0), (-6.0, -352.0), (-16.0, -347.0)],
            hatch=[[(-16.0, -356.0), (-2.0, -361.0), (14.0, -360.0)], [(-12.0, -350.6), (2.0, -356.0), (16.0, -355.0)]])
    # elbow tucked in, forearm raised, fingers in his beard
    F.piece('upperarm', [(0, -282), (14, -286), (18, -262), (20, -240), (16, -224), (6, -226), (2, -250)],
            hatch=[[(6, -262), (8, -236)]])
    F.piece('forearm', [(6, -232), (16, -238), (24, -262), (32, -288), (26, -294), (18, -288), (12, -262), (4, -236)])
    hand(F, 'hand', 'rest', 28, -290, -72, 0.85)
    return F


def money_changer(lod=1):
    """Money-changer seated on a stool behind his table (facing right): coin stacks, a balance, his hand on the coins."""
    F = FigDraw()
    # stool
    F.piece('stool', [(-46, -86), (12, -86), (12, -78), (6, -78), (5, 0), (-1, 0), (-2, -78), (-34, -78), (-35, 0), (-41, 0),
                      (-40, -78), (-46, -78)], rigid=True)
    # far leg (shin under the table) and near leg
    F.piece('legs', [(-20, -112), (30, -128), (52, -126), (56, -100), (54, -40), (58, -14), (72, -6), (78, 0, C), (44, 0, C),
                     (42, -14), (40, -60), (36, -96), (-10, -82), (-24, -90)],
            hatch=[[(48, -12), (54, -4)]])
    F.piece('robe', [(-12, -246), (-26, -226), (-30, -190), (-28, -150), (-32, -110), (-30, -86, C), (0, -84), (40, -96),
                     (58, -104), (60, -124, C), (30, -134), (16, -142), (20, -180), (22, -214), (18, -236), (8, -246)],
            inner=[[(-28, -150), (-8, -146), (14, -150)]],
            hatch=[[(0, -100), (30, -112), (54, -116)], [(-20, -100), (10, -110)]])
    F.piece('mantle', [(-18, -250), (-2, -252), (10, -244), (14, -228), (10, -204), (8, -170), (-6, -154), (-28, -150),
                       (-36, -160, C), (-36, -200), (-32, -232)],
            inner=[[(-24, -230), (-26, -190), (-28, -160)], [(-6, -236), (-8, -196), (-10, -162)]],
            hatch=[[(-36, -160), (-40, -146)], [(-35, -160), (-34, -146)]],
            shade=[([(-38, -232), (-26, -232), (-28, -152), (-38, -158)], 80, 2.6)])
    profile_head(F, -24, -308, 1.0, beard='full', hair='short', tilt=14, mouth=0.3, age=0.6, name='head', lod=lod)
    F.piece('turban', [(-27.0, -295.0), (-21.0, -306.0), (-8.0, -313.0), (6.0, -312.0), (15.0, -305.0), (17.0, -297.0),
                       (14.6, -293.4), (3.0, -296.0), (-11.0, -295.0), (-21.0, -290.0)],
            hatch=[[(-21.0, -299.0), (-6.0, -304.0), (10.0, -303.0)]])
    # the table with its load of coins and a small balance
    F.piece('table', [(34, -152), (178, -152), (178, -143), (170, -143), (169, 0), (162, 0), (162, -143), (52, -143), (51, 0),
                      (44, 0), (44, -143), (34, -143)], rigid=True, hatch=[[(36, -147), (176, -147)]])
    for k, (cx, n) in enumerate([(80, 6), (94, 4), (107, 7)]):
        top = -152 - n * 2.4
        F.piece(f'stack{k}', [(cx - 6, -152), (cx - 6, top), (cx - 4, top - 1.6), (cx + 4, top - 1.6), (cx + 6, top),
                               (cx + 6, -152)], rigid=True,
                hatch=[[(cx - 6, -152 - j * 2.4), (cx + 6, -152 - j * 2.4)] for j in range(1, n)])
    F.piece('loose_coin1', [(120, -152), (121, -154.4), (127, -154.4), (128, -152)], rigid=True)
    F.piece('loose_coin2', [(131, -152), (132, -154.0), (137, -154.0), (138, -152)], rigid=True)
    F.piece('balance', [(149, -152), (149, -198), (153, -198), (153, -152)], rigid=True, edge=False)
    F.extra_detail += [[(133, -198), (169, -198)], [(133, -198), (128, -178), (138, -178), (133, -198)],
                       [(169, -198), (164, -180), (174, -180), (169, -198)]]
    F.extra_hatch += [[(126, -178), (140, -178), (137, -174), (129, -174), (126, -178)],
                      [(162, -180), (176, -180), (173, -176), (165, -176), (162, -180)]]
    # near arm resting on the table, fingers on the coins
    F.piece('arm', [(-10, -238), (6, -240), (14, -218), (22, -192), (30, -176), (50, -166), (66, -162), (70, -154),
                    (60, -151), (40, -153), (22, -158), (10, -170), (0, -194), (-8, -216)],
            hatch=[[(0, -222), (10, -196)], [(4, -228), (14, -204)]])
    hand(F, 'hand', 'rest', 64, -158, 18, 0.8)
    return F


def pilgrim_paying(lod=1):
    """Pilgrim (authored facing right; place flipped) holding out a coin across the table."""
    F = FigDraw()
    F.piece('backfoot', [(-30, -28), (-18, -28), (-16, -14), (-6, -7), (8, -3), (12, 0, C), (-32, 0, C), (-36, -6), (-33, -16)])
    F.piece('robe', [(-14, -304), (-24, -282), (-26, -250), (-23, -212), (-25, -175), (-27, -120), (-29, -64), (-32, -24, C),
                     (-6, -20), (20, -21), (32, -24, C), (30, -64), (28, -115), (26, -165), (25, -205), (26, -235), (24, -262),
                     (17, -288), (8, -302)],
            hatch=[[(24, -84), (26, -56), (28, -30)], [(8, -86), (8, -56), (8, -26)], [(-14, -86), (-16, -56), (-18, -26)]])
    F.piece('frontfoot', [(12, -28), (24, -28), (26, -14), (36, -7), (50, -3), (54, 0, C), (10, 0, C), (7, -6), (9, -16)])
    F.piece('belt', [(-25, -196), (26, -200), (26, -190), (-24, -186)])
    profile_head(F, -18, -362, 1.0, beard='full', hair='long', cover='mantle', tilt=4, mouth=0.4, name='head', lod=lod)
    F.piece('mantle_fall', [(-26, -296), (-8, -294), (-4, -270), (-8, -230), (-14, -170), (-20, -140), (-32, -136, C),
                            (-33, -180), (-31, -240), (-30, -276)],
            hatch=[[(-22, -270), (-24, -200), (-26, -150)]],
            shade=[([(-34, -280), (-24, -280), (-28, -138), (-34, -138)], 80, 2.6)])
    F.piece('arm', [(4, -272), (18, -276), (24, -252), (30, -230), (46, -214), (66, -204), (70, -196), (62, -192), (42, -198),
                    (24, -210), (14, -228), (6, -250)],
            hatch=[[(12, -254), (20, -232)]])
    hand(F, 'hand', 'grip', 68, -200, 8, 0.8)
    F.piece('coin', [(84.0, -205.0), (86.6, -207.4), (89.0, -205.0), (86.6, -202.6)])
    return F


# ============================================================================ Roman legionary
def helmet_head(F, ox, oy, s=1.0, tilt=0.0, name='rhead', mouth=-0.4, lod=2):
    """Profile head facing right in an Imperial-Gallic galea (clean-shaven face)."""
    def T(pts):
        ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        out = []
        for p in pts:
            x, y = p[0] * s, p[1] * s
            out.append((ox + x * ca - y * sa, oy + x * sa + y * ca) + tuple(p[2:]))
        return out
    # face (clean-shaven, strong jaw) - same landmarks as profile_head
    face = [(22, 0), (31, 2), (37, 7), (39.4, 13), (40.4, 18), (40.9, 20.2), (39.9, 22.0, C), (41.6, 26.5), (44.6, 31.2, C),
            (42.4, 32.6), (40.4, 33.0, C), (41.3, 35.0), (41.6, 36.2), (40.0, 37.4, C), (40.8, 38.6), (40.0, 40.2),
            (38.4, 41.4, C), (39.8, 44.0), (39.2, 46.8), (35.6, 48.6), (29.0, 49.0), (22.0, 46.0), (17.0, 41.6),
            (12.0, 38.0), (6.0, 35.0), (1.6, 28.0), (0.0, 18.0), (2.6, 9.0), (9.0, 3.0)]
    inner = [[(33.0, 22.6), (35.2, 21.4), (37.6, 22.2), (38.6, 23.6), (36.4, 25.0), (34.0, 24.6)],
             [(36.6, 22.0), (36.3, 24.6)],
             [(30.8, 19.0), (34.6, 18.0), (38.4, 18.4), (40.2, 19.6)],
             [(40.4, 37.6), (37.8, 37.8 - mouth), (35.6, 37.0 - mouth * 1.6)]]
    hatch = [[(39.0, 31.0), (38.0, 32.6), (39.6, 33.2)], [(37.4, 26.0), (35.4, 30.4), (35.8, 33.4)], [(34.0, 44.0), (37.0, 45.4)]]
    F.piece(name, T(face), inner=[T(q) for q in inner], hatch=[T(q) for q in hatch])
    # helmet: dome over the skull, small brow peak in front, ribbed neck guard projecting back almost level
    bowl = [(16, -5.0), (26, -6.4), (33, -4.0), (38.6, 1.0), (41.2, 6.4), (42.0, 10.6), (44.6, 12.2, C), (43.0, 14.2),
            (38.0, 13.4), (32.0, 13.2), (26.0, 14.0), (20.6, 16.4), (14.0, 17.0), (9.0, 19.0), (6.0, 26.0), (3.0, 31.0),
            (-2.0, 34.2), (-9.6, 37.6), (-16.8, 41.6, C), (-18.4, 38.0), (-11.0, 33.2), (-5.4, 28.4), (-3.4, 20.0),
            (-2.4, 10.0), (2.0, 2.0), (8.0, -2.8)]
    F.piece(name + '_helmet', T(bowl),
            inner=[T([(41.0, 9.6), (34.0, 8.6), (26.0, 8.8), (17.0, 10.6), (9.6, 14.6)]),
                   T([(-3.2, 29.6), (-10.4, 34.0), (-17.0, 38.6)])],
            hatch=[T([(30.0, -1.6), (22.0, -2.6), (12.0, 0.0), (5.0, 7.0)]), T([(-4.0, 32.2), (-11.0, 35.6)]),
                   T([(24.0, 3.0), (16.0, 4.0), (9.0, 8.6), (5.0, 15.0)]), T([(36.0, 10.8), (39.0, 11.6)])])
    F.piece(name + '_knob', T([(20.0, -5.6), (20.4, -10.6), (25.6, -11.0), (26.0, -6.2)]), rigid=True)
    # hinged cheek piece covering the cheek down to the jaw; the ear shows in the cut-out behind it
    cheek = [(13.6, 17.0), (21.0, 16.0), (28.0, 16.8), (31.6, 21.0), (31.0, 29.0), (33.4, 37.0), (33.0, 43.8), (28.0, 47.0),
             (23.0, 46.4), (19.4, 40.0), (15.0, 32.0), (13.0, 24.0)]
    F.piece(name + '_cheek', T(cheek), inner=[T([(16.0, 22.0), (22.0, 21.0), (28.0, 22.4)])],
            hatch=[T([(16.0, 28.0), (21.0, 30.0)]), T([(19.0, 36.0), (25.0, 38.0)]), T([(23.0, 42.0), (28.0, 44.0)]),
                   T([(29.4, 26.0), (30.6, 36.0)])])
    # rivet at the hinge
    F.piece(name + '_rivet', T([(17.0, 19.6), (18.4, 18.6), (19.6, 19.8), (18.4, 21.0)]), edge=False)
    return F


def mail_rows(x0, x1, y0, y1, step=7.0, amp=2.2, w=4.4):
    """rows of small arcs suggesting riveted mail"""
    rows = []
    y = y0
    k = 0
    while y < y1:
        pts = []
        x = x0 + (w / 2 if k % 2 else 0)
        while x < x1:
            pts += [(x, y), (x + w * 0.5, y + amp)]
            x += w
        pts.append((x, y))
        rows.append(pts)
        y += step
        k += 1
    return rows


def limb(p0, p1, stations, n=None):
    """Organic limb outline along the bone p0->p1.  stations: list of (t, wl, wr) = position along the bone (0..1) and
    half-widths on the left/right of the direction of travel.  Returns a closed point list (smooth)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux                  # left normal (screen coords, y down)
    left, right = [], []
    for t, wl, wr in stations:
        cx, cy = p0[0] + dx * t, p0[1] + dy * t
        left.append((cx + nx * wl, cy + ny * wl))
        right.append((cx - nx * wr, cy - ny * wr))
    return left + right[::-1]


def legionary_a(lod=2):
    """Legionary standing guard facing us, head turned to watch the people on the right: pilum planted at his right,
    gripped at waist height; curved scutum grounded at his left with his hand resting on its rim."""
    F = FigDraw()
    F.min_edge = 18.0
    F.close = 1.6
    F.clip_hatch = True
    # ---------- legs, bare below the tunic; caligae seen from the front, toes turned slightly out
    F.piece('l_thigh', limb((17, -178), (24, -106), [(0, 19, 18), (0.4, 18, 17), (0.8, 13, 13), (1.0, 11.5, 11)]), edge=False)
    F.piece('l_shin', limb((24, -110), (29, -14), [(0, 11.5, 11), (0.1, 12, 11.5), (0.28, 11, 15), (0.5, 9, 12.5), (0.8, 6.8, 7.4),
                                                  (1.0, 7, 7)]),
            hatch=[[(19.6, -104), (21.4, -99), (24.4, -97.4), (27.4, -99), (29.0, -104)], [(36, -80), (36.6, -58)]])
    front_foot(F, 'l_foot', 29.4, -17.0, side=1)
    F.piece('r_thigh', limb((-17, -178), (-20, -106), [(0, 18, 19), (0.4, 17, 18), (0.8, 13, 13), (1.0, 11, 11.5)]), edge=False)
    F.piece('r_shin', limb((-20, -110), (-23, -14), [(0, 11, 11.5), (0.1, 11.5, 12), (0.28, 15, 11), (0.5, 12.5, 9), (0.8, 7.4, 6.8),
                                                    (1.0, 7, 7)]),
            hatch=[[(-25.0, -104), (-23.2, -99), (-20.2, -97.4), (-17.2, -99), (-15.6, -104)], [(-32, -80), (-32.6, -58)]])
    front_foot(F, 'r_foot', -23.4, -17.0, side=-1)
    # ---------- tunic skirt below the mail, a few soft folds
    F.piece('tunic', [(-41, -176), (41, -176), (44, -150), (47, -118, C), (34, -114), (18, -118), (2, -114), (-14, -118),
                      (-30, -114), (-46, -118, C), (-44, -150)],
            hatch=[[(-34, -166), (-36, -120)], [(-22, -164), (-23, -118)], [(16, -164), (17, -120)], [(30, -164), (32, -118)]],
            shade=[([(-47, -150), (47, -150), (47, -116), (-47, -116)], 75, 3.0)])
    # ---------- arms (under the short mail sleeves): right forearm forward to the pilum, left up to the shield rim
    F.piece('r_upperarm', limb((-45, -266), (-58, -222), [(0, 11, 11.5), (0.35, 12, 12), (0.75, 9.5, 10), (1.0, 8.5, 9)]), edge=False)
    F.piece('r_forearm', limb((-57, -224), (-84, -216), [(0, 9.5, 9.5), (0.3, 10, 10), (1.0, 6.6, 6.6)]),
            hatch=[[(-62, -228), (-74, -226)]])
    F.piece('l_upperarm', limb((45, -266), (58, -224), [(0, 11.5, 11), (0.35, 12, 12), (0.75, 10, 9.5), (1.0, 9, 8.5)]), edge=False)
    F.piece('l_forearm', limb((57, -226), (73, -243), [(0, 9, 8.5), (0.3, 9.5, 9.5), (1.0, 6.6, 6.6)]))
    # ---------- mail shirt: V-shaped torso, short sleeves, bloused over the belt, flared hem
    mail = [(-13, -306), (-24, -302), (-36, -296), (-45, -290), (-51, -280), (-54, -268), (-55, -254, C), (-43, -250, C),
            (-38, -244), (-35, -230), (-33, -216), (-33, -206), (-36, -199), (-39, -190), (-41, -180), (-43, -170, C), (-22, -167),
            (0, -166), (22, -167), (43, -170, C), (41, -180), (39, -190), (36, -199), (33, -206), (33, -216), (35, -230),
            (38, -244), (43, -250, C), (55, -254, C), (54, -268), (51, -280), (45, -290), (36, -296), (24, -302), (13, -306)]
    F.piece('mail', mail,
            hatch=[[(-52, -260), (-48, -258), (-44, -260)], [(48, -260), (52, -258)]] +
                  mail_rows(-34, 35, -244, -208, 9.0, amp=1.5, w=3.4) + mail_rows(-42, 43, -184, -170, 9.0, amp=1.5, w=3.4),
            shade=[([(-40, -248), (-31, -248), (-30, -168), (-44, -168)], 76, 2.6), ([(28, -248), (38, -248), (44, -168), (32, -168)], 76, 3.8)])
    # shoulder doubling (humeralia) joined on the chest by S-hooks
    F.piece('humeral', [(-13, -306), (-24, -302), (-36, -296), (-45, -290), (-51, -280), (-53, -270), (-44, -266), (-30, -264),
                        (-14, -261), (-6, -264), (0, -268), (6, -264), (14, -261), (30, -264), (44, -266), (53, -270), (51, -280),
                        (45, -290), (36, -296), (24, -302), (13, -306)],
            inner=[[(-8, -270), (-5, -266), (-8, -262), (-5, -258)], [(8, -270), (5, -266), (8, -262), (5, -258)]],
            hatch=mail_rows(-52, 53, -298, -266, 8.0, amp=1.5, w=3.4))
    # belts with plates, studded apron, gladius on the right hip, dagger on the left
    F.piece('belt', [(-35, -202), (0, -198), (35, -202), (36, -193), (0, -189), (-36, -193)],
            hatch=[[(-29, -197.6), (-24, -197.6)], [(-17, -196), (-12, -196)], [(-5, -194.8), (0, -194.8)], [(8, -195), (13, -195)],
                   [(20, -196.2), (25, -196.2)], [(29, -197.4), (33, -197.4)]])
    F.piece('belt2', [(-39, -191), (-4, -181), (37, -186), (38, -177), (-4, -172), (-40, -182)],
            hatch=[[(-28, -184), (-22, -182.4)], [(-16, -181), (-10, -179.6)], [(12, -178.6), (18, -179.4)], [(26, -180.6), (32, -181.6)]])
    ap = [(-12.5, -176)]
    for k in range(4):                               # four studded straps ending in small pendants
        xa = -12.5 + k * 5.6
        ap += [(xa, -131, C), (xa + 0.6, -127.2), (xa + 2.6, -124.6), (xa + 4.4, -127.2), (xa + 5.0, -131, C)]
    ap += [(9.9, -176)]
    studs = [[(xa + 2.6 - 0.8, yy), (xa + 2.6 + 0.8, yy)] for k in range(4) for xa in [-12.5 + k * 5.6]
             for yy in (-166.0, -156.0, -146.0, -137.0)]
    F.piece('apron', ap, rigid=False,
            inner=[[(-6.9 + 0.3, -172), (-6.9 + 0.3, -132)], [(-1.3 + 0.3, -172), (-1.3 + 0.3, -132)], [(4.3 + 0.3, -172), (4.3 + 0.3, -132)]],
            hatch=studs)
    F.piece('scabbard', [(-49, -190), (-40, -190), (-41, -128), (-44.5, -119, C), (-48, -128)],
            inner=[[(-49, -180), (-40, -180)]],
            hatch=[[(-49, -158), (-41, -158)], [(-48.6, -134), (-41.4, -134)]])
    F.piece('hilt', [(-51, -194), (-38, -194), (-40, -199), (-42, -210), (-40, -215), (-44.5, -221, C), (-49, -215), (-47, -210),
                     (-49, -199)],
            hatch=[[(-46.6, -202), (-42.4, -202)], [(-46.8, -206), (-42.2, -206)]])
    F.piece('pugio', [(39, -188), (45, -188), (44, -150), (42, -144, C), (40, -150)])
    F.piece('neck', [(-12, -322), (11, -322), (12, -304), (0, -300), (-12, -304)], edge=False,
            hatch=[[(-6, -320), (6, -306)]])
    F.piece('focale', [(-15, -306), (0, -311), (15, -306), (12, -297), (0, -293), (-12, -297)],
            hatch=[[(-9, -304), (0, -300), (9, -304)]])
    helmet_head(F, -21, -372, 1.09, tilt=0, name='head', mouth=-0.7)
    # ---------- the scutum, face on, grounded at his left: boss with eagle wings and thunderbolts
    x0 = 64
    cx = x0 + 57
    sh = [(x0, -238), (x0 + 30, -232), (x0 + 57, -230), (x0 + 84, -232), (x0 + 114, -238, C), (x0 + 116, -120),
          (x0 + 114, -6, C), (x0 + 84, 0), (x0 + 57, 2), (x0 + 30, 0), (x0, -6, C), (x0 - 2, -120)]
    F.piece('shield', sh,
            hatch=[[(x0 + 6, -230), (x0 + 32, -224.6), (x0 + 57, -222.6), (x0 + 84, -224.6), (x0 + 108, -230), (x0 + 109, -12),
                    (x0 + 84, -7), (x0 + 57, -5), (x0 + 30, -7), (x0 + 6, -12), (x0 + 6, -230)],
                   [(cx, -222), (cx, -206)], [(cx, -30), (cx, -8)]],
            fill=RUST)
    F.piece('boss', [(cx - 13, -130), (cx - 8, -139), (cx, -142), (cx + 8, -139), (cx + 13, -130), (cx + 13, -108),
                     (cx + 8, -99), (cx, -96), (cx - 8, -99), (cx - 13, -108)],
            inner=[[(cx - 7, -128), (cx, -134), (cx + 7, -128)]],
            hatch=[[(cx - 9, -114), (cx - 2, -106), (cx + 8, -108)]])
    for sg in (-1, 1):
        X = lambda u: cx + sg * u
        F.extra_detail.append(sp([(X(14), -126), (X(24), -134), (X(36), -142), (X(50), -146, C), (X(44), -136), (X(47), -133, C),
                                  (X(36), -126), (X(39), -122, C), (X(27), -118), (X(30), -114, C), (X(14), -112)], step=1.0))
        F.extra_hatch += [[(X(44), -136), (X(28), -129)], [(X(36), -126), (X(24), -121)]]
    for sg in (-1, 1):                               # thunderbolts up and down the spine
        Y = lambda v: -119 + sg * v
        F.extra_detail.append([(cx, Y(25)), (cx - 4, Y(42)), (cx + 4, Y(50)), (cx, Y(78)), (cx + 1.6, Y(70)), (cx - 1.6, Y(70)),
                               (cx, Y(78))])
        F.extra_hatch += [[(cx - 6, Y(46)), (cx - 12, Y(56))], [(cx + 6, Y(46)), (cx + 12, Y(56))]]
    # his left hand resting on the rim, fingers curled over the front of the shield
    hx, hy = x0 + 16.0, -234.4
    F.piece('l_hand', [(hx - 12, hy - 7.5), (hx - 3, hy - 10.6), (hx + 7, hy - 9.6), (hx + 11.4, hy - 5.6), (hx + 12, hy + 1),
                       (hx + 11.6, hy + 8.0), (hx + 9.4, hy + 10.6), (hx + 7.2, hy + 8.4, C), (hx + 5.0, hy + 11.2), (hx + 2.6, hy + 9.0, C),
                       (hx + 0.2, hy + 11.6), (hx - 2.2, hy + 9.4, C), (hx - 4.6, hy + 10.8), (hx - 7.2, hy + 8.0), (hx - 7.8, hy + 2.0),
                       (hx - 11.2, hy - 1.4)],
            inner=[[(hx + 7.2, hy + 2.4), (hx + 7.2, hy + 8.0)], [(hx + 2.6, hy + 2.8), (hx + 2.6, hy + 8.6)],
                   [(hx - 2.2, hy + 2.6), (hx - 2.2, hy + 9.0)]],
            hatch=[[(hx - 7.0, hy + 0.2), (hx + 1.0, hy + 1.2), (hx + 11.0, hy + 0.2)]])
    # ---------- pilum planted beside his right foot: shaft one stroke, block and iron head small shapes; fist round it
    baked_hand(F, 'r_fist', 'grip', -84, -216, 0.0, 1.3, mirror=False)
    px = -84.0 - 11.0 * 1.3
    F.extra_line = [[(px, 0), (px, -331)], [(px, -349), (px, -457)]]
    F.piece('pilum_block', [(px - 3.0, -331), (px + 3.0, -331), (px + 3.0, -346), (px + 1.0, -350), (px - 1.0, -350), (px - 3.0, -346)],
            rigid=True, edge=False, sil=False)
    F.piece('pilum_tip', [(px - 2.0, -456), (px + 2.0, -456), (px + 2.2, -462), (px, -477), (px - 2.2, -462)], rigid=True, edge=False,
            sil=False)
    return F


def legionary_b(lod=2):
    """Second legionary in profile facing right: pilum upright in his right hand, scutum on his left arm seen edge on."""
    F = FigDraw()
    F.min_edge = 20.0
    # far leg, near leg (standing, slight stride)
    F.piece('far_leg', limb((-6, -176), (-12, -16), [(0, 17, 17), (0.25, 15, 15), (0.5, 9, 11), (0.68, 9, 13), (0.85, 7, 7.5),
                                                    (1.0, 7, 7)]), edge=False)
    sandal(F, 'far_foot', (-12, -12), (20, -1), mirror=True)
    F.piece('tunic', [(-30, -180), (24, -180), (28, -150), (32, -114, C), (10, -110), (-12, -112), (-34, -116, C), (-33, -150)],
            hatch=[[(-24, -168), (-27, -118)], [(-8, -166), (-10, -114)], [(14, -166), (18, -116)]],
            shade=[([(-35, -150), (-14, -150), (-16, -112), (-35, -114)], 76, 3.0)])
    F.piece('near_leg', limb((6, -176), (14, -16), [(0, 17, 17), (0.25, 15, 15), (0.5, 9, 11), (0.68, 9, 13), (0.85, 7, 7.5),
                                                   (1.0, 7, 7)]),
            inner=[[(8, -112), (16, -104), (20, -110)]])
    sandal(F, 'near_foot', (14, -12), (46, -1), mirror=True)
    F.extra_hatch += [[(6, -30), (22, -28)], [(6, -22), (22, -20)]]
    # mail shirt in profile, bloused over the belt
    F.piece('mail', [(-14, -300), (6, -302), (20, -294), (27, -278), (28, -256), (26, -232), (25, -212), (27, -198),
                     (29, -186), (30, -170, C), (6, -166), (-18, -168), (-33, -172, C), (-32, -190), (-29, -210), (-30, -236),
                     (-32, -262), (-28, -286)],
            hatch=mail_rows(-28, 26, -248, -210, 9.0, amp=1.6, w=3.6) + mail_rows(-30, 28, -184, -174, 9.0, amp=1.6, w=3.6),
            shade=[([(-34, -270), (-20, -270), (-20, -170), (-34, -172)], 78, 2.6)])
    F.piece('belt', [(-31, -202), (27, -200), (27, -191), (-31, -193)],
            hatch=[[(-24, -197), (-19, -197)], [(-10, -196.6), (-5, -196.6)], [(6, -196), (11, -196)], [(18, -195.6), (23, -195.6)]])
    F.piece('apron', [(16, -192), (26, -192), (28, -128, C), (18, -128, C)],
            inner=[[(21, -190), (22, -130)]],
            hatch=[[(18, -160), (20, -160)], [(22, -146), (24, -146)], [(19, -138), (21, -138)]])
    F.piece('scabbard', [(-2, -196), (8, -196), (4, -128), (-2, -120, C), (-6, -128)],
            inner=[[(-3, -184), (7, -184)], [(-4, -160), (5, -160)]])
    F.piece('hilt', [(-2, -200), (10, -200), (8, -206), (6, -217), (8, -222), (3, -228, C), (-2, -222), (0, -217), (-2, -206)])
    F.piece('neck', [(-10, -318), (10, -318), (12, -298), (0, -294), (-12, -298)], edge=False)
    F.piece('focale', [(-14, -302), (4, -306), (18, -298), (16, -290), (0, -288), (-12, -292)])
    helmet_head(F, -20, -366, 1.06, tilt=-2, name='head', mouth=-0.5)
    # the scutum on his left arm, seen edge on: a curved band in front of him
    F.piece('shield', [(30, -258), (40, -262), (48, -250), (52, -200), (54, -150), (52, -90), (48, -44), (40, -32, C), (34, -38),
                       (38, -90), (40, -150), (38, -200), (34, -244)],
            inner=[[(36, -252), (44, -200), (46, -150), (44, -96), (40, -46)]],
            hatch=[[(42, -246), (48, -200)], [(46, -110), (44, -60)]],
            fill=RUST)
    F.piece('shield_boss', [(50, -168), (58, -166), (60, -150), (58, -134), (50, -132)])
    # near arm bent, fist round the pilum shaft
    F.piece('arm', limb((2, -282), (12, -228), [(0, 11, 11), (0.3, 12, 11.5), (1.0, 9, 9)]), edge=True)
    F.piece('forearm', limb((10, -232), (34, -214), [(0, 9, 9), (0.3, 9.5, 9.5), (1.0, 6.5, 6.5)]))
    F.piece('sleeve', [(-6, -288), (12, -292), (16, -268), (2, -262), (-8, -270)],
            hatch=[[(0, -270), (4, -274), (8, -270), (12, -274)]])
    px = 42.0
    F.extra_line = getattr(F, 'extra_line', []) + [[(px, 0), (px, -331)], [(px, -349), (px, -457)]]
    F.piece('pilum_block', [(px - 3.0, -331), (px + 3.0, -331), (px + 3.0, -346), (px + 1.0, -350), (px - 1.0, -350), (px - 3.0, -346)],
            rigid=True, edge=False, sil=False)
    F.piece('pilum_tip', [(px - 2.0, -456), (px + 2.0, -456), (px + 2.2, -462), (px, -477), (px - 2.2, -462)], rigid=True, edge=False,
            sil=False)
    baked_hand(F, 'fist', 'grip', 30, -214, 0.0, 1.35, mirror=True)
    return F


# ============================================================================ adapters to the shared batch-A figure kit
def parse_d(d, step=1.0):
    """absolute M/L/C/Q/Z path -> list of polylines"""
    import re
    toks = re.findall(r"[MLCQZ]|-?\d*\.?\d+(?:e-?\d+)?", d)
    out, cur, start, i, cmd = [], None, None, 0, None
    pts = None

    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v
    while i < len(toks):
        if toks[i] in 'MLCQZ':
            cmd = toks[i]; i += 1
            if cmd == 'Z':
                if pts and start:
                    pts.append(start)
                continue
        if cmd == 'M':
            if pts and len(pts) > 1:
                out.append(pts)
            cur = (num(), num()); start = cur; pts = [cur]; cmd = 'L'
        elif cmd == 'L':
            cur = (num(), num()); pts.append(cur)
        elif cmd == 'C':
            c = [num() for _ in range(6)]
            x0, y0 = cur
            n = max(3, int(math.hypot(c[4] - x0, c[5] - y0) / step) + 1)
            for k in range(1, n + 1):
                t = k / n; m = 1 - t
                pts.append((m ** 3 * x0 + 3 * m * m * t * c[0] + 3 * m * t * t * c[2] + t ** 3 * c[4],
                            m ** 3 * y0 + 3 * m * m * t * c[1] + 3 * m * t * t * c[3] + t ** 3 * c[5]))
            cur = (c[4], c[5])
        elif cmd == 'Q':
            c = [num() for _ in range(4)]
            x0, y0 = cur
            n = max(3, int(math.hypot(c[2] - x0, c[3] - y0) / step) + 1)
            for k in range(1, n + 1):
                t = k / n; m = 1 - t
                pts.append((m * m * x0 + 2 * m * t * c[0] + t * t * c[2], m * m * y0 + 2 * m * t * c[1] + t * t * c[3]))
            cur = (c[2], c[3])
        else:
            i += 1
    if pts and len(pts) > 1:
        out.append(pts)
    return out


def foreign_head(F, hx, hy, s=0.48, rot=0.0, mirror=True, name='head', lv=2, **kw):
    """Insert a 3/4 head from a_people.head34 (designed facing left; mirror=True faces it right).
    (hx, hy) = eye-line centre of the head in figure units; s = figure units per head-space unit."""
    import jesus as J
    import a_people as AP
    f = J.Fig()
    AP.head34(f, 0.0, 0.0, rot, 1.0, **kw)
    sg = -1.0 if mirror else 1.0
    T = lambda q: [(hx + sg * px * s, hy + py * s) for px, py in q]
    for part in sorted(f.parts, key=lambda q: q.order):
        strokes = []
        for st in part.strokes:
            if st['lv'] > lv:
                continue
            for pl in parse_d(st['d'], step=1.4):
                strokes.append((st['cls'], T(pl)))
        occ = [T(q) for q in part.occ]
        F.pieces.append(RawPiece(f'{name}_{part.name}', strokes, occ))
    return F


def baked_hand(F, name, kind, x, y, ang, s=2.0, mirror=True, flip=False):
    """Hand from hands_data (baked by the shared hand rig; designed for left-facing figures).  Wrist at (x, y)."""
    from hands_data import HANDS
    h = HANDS[kind]
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    sg = -1.0 if mirror else 1.0

    def T(pts):
        out = []
        for px, py in pts:
            if flip:
                py = -py
            px, py = sg * px * s, py * s
            out.append((x + px * ca - py * sa, y + px * sa + py * ca))
        return out
    inner = sorted(h['inner'], key=lambda q: -sum(math.dist(a, b) for a, b in zip(q, q[1:])))
    keep = [T(q) for q in inner[:3]]
    rest = [T(q) for q in inner[3:]]
    return F.piece(name, T(h['outline']), inner=keep, hatch=rest)


def sandal(F, name, ankle, toe, mirror=True):
    """sandalled foot in profile (shared design from jesus.foot): design ankle -> `ankle`, design toe tip -> `toe`
    (mirror=True faces right)."""
    ax, ay = ankle
    tx0, ty0 = toe
    L = math.hypot(tx0 - ax, ty0 - ay)
    dtx = 28.4 if mirror else -28.4
    ang = math.degrees(math.atan2(ty0 - ay, tx0 - ax) - math.atan2(5.2, dtx))
    sc = L / math.hypot(28.4, 5.2)
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def T(pts):
        out = []
        for px, py in pts:
            if mirror:
                px = -px
            px, py = px * sc, py * sc
            out.append((ax + px * ca - py * sa, ay + px * sa + py * ca))
        return out
    o = [(-2.6, -6.6), (-9, -3.8), (-17, -0.6), (-23.6, 1.4), (-27.4, 3), (-28.4, 5.2), (-26.6, 6.6),
         (-18, 6.8), (-8, 7), (2.6, 6.8), (6.4, 4.6), (6.6, -0.6), (5, -6)]
    sole = [(7.4, 5.8), (6.6, 8.8), (-6, 9.2), (-20, 9), (-28.6, 8.2), (-29.6, 6.4)]
    return F.piece(name, T(o + [(6.6, 8.8), (-29.6, 6.4)]),
                   inner=[T([(6.0, 6.4), (-8, 7.4), (-27.0, 6.8)]), T([(-15.6, -1.2), (-16.6, 2.6), (-15.6, 6.6)])],
                   hatch=[T([(1.6, -6.2), (-0.6, 0.4), (0.4, 6.6)]), T([(-21.2, 0.6), (-21.6, 4.0)])])


def foot(F, name, toe, right=True, lift=0.0, sc=1.25):
    """profile sandalled foot placed by its toe tip (the sole's lowest point lands ~4*sc lower);
    lift = heel raised by this many degrees (pushing off)."""
    rot = math.radians(lift if right else -lift)
    dx, dy = (-28.4 if right else 28.4) * sc, -5.2 * sc
    ca, sa = math.cos(rot), math.sin(rot)
    ankle = (toe[0] + dx * ca - dy * sa, toe[1] + dx * sa + dy * ca)
    return sandal(F, name, ankle, toe, mirror=right)


def front_foot(F, name, ax, ay, side=1, w=7.0):
    """caliga seen from the front: ankle centre (ax, ay) (~18 units above the ground y=0), toes splayed to `side`
    (+1 = viewer's right).  Open-work boot: laced instep, toes showing, thick hobnailed sole."""
    s = side
    X = lambda u: ax + s * u
    h = -ay                     # ankle height above the ground
    o = [(X(-w), ay), (X(-w - 0.8), ay + h * 0.45), (X(-w - 1.6), -3.6), (X(-w - 2.4), -1.2), (X(-w - 1.8), 0.6),
         (X(-2), 1.2), (X(6), 1.0), (X(13), 0.2), (X(w + 9.6), -1.0), (X(w + 9.8), -3.0), (X(w + 7.0), -6.0),
         (X(w + 3.2), -9.5), (X(w + 0.8), ay + h * 0.5), (X(w), ay)]
    F.piece(name, o,
            inner=[[(X(-w - 2.2), -3.2), (X(2), -2.4), (X(w + 9.2), -3.4)],
                   [(X(0.6), ay + 1.5), (X(2.2), ay + h * 0.45), (X(4.4), -6.5)]],
            hatch=[[(X(-2.2), ay + 4.0), (X(3.4), ay + 5.2)], [(X(-2.6), ay + 8.4), (X(4.6), ay + 9.4)],
                   [(X(-2.0), ay + 12.6), (X(6.0), ay + 13.2)],
                   [(X(-4.0), -3.6), (X(-3.6), -5.8)], [(X(1.0), -3.4), (X(1.6), -5.8)], [(X(6.4), -3.6), (X(7.4), -6.0)],
                   [(X(-w - 1.4), -0.4), (X(w + 8.8), -0.6)]])


def elder_glancing(lod=2):
    """Old man walking right on his staff, prayer mantle over his head, turning to look back at the soldiers."""
    F = FigDraw()
    F.min_edge = 12.0
    F.piece('backleg', [(-14, -78), (-4, -76), (-12, -52), (-22, -30), (-26, -22), (-34, -20), (-32, -34), (-24, -56)], edge=False)
    sandal(F, 'backfoot', (-28, -16), (-6, -2))
    F.piece('robe', [(-12, -300), (-24, -292), (-31, -274), (-31, -244), (-27, -214), (-30, -180), (-34, -130), (-37, -80),
                     (-41, -28, C), (-14, -22), (14, -24), (42, -32, C), (40, -64), (36, -104), (31, -150), (28, -196),
                     (30, -230), (28, -258), (22, -280), (10, -296)],
            hatch=[[(34, -70), (38, -48), (40, -34)], [(22, -72), (24, -50), (25, -28)], [(-18, -70), (-21, -48), (-24, -26)],
                   [(4, -76), (3, -50), (2, -26)]])
    F.piece('frontleg', [(18, -40), (34, -40), (36, -24), (38, -16), (22, -14), (20, -24)], edge=False)
    sandal(F, 'frontfoot', (30, -16), (66, -3))
    F.piece('mantle', [(-22, -296), (-8, -300), (8, -296), (18, -286), (24, -268), (28, -244), (30, -214), (32, -182),
                       (34, -152, C), (14, -142), (-8, -134), (-28, -124), (-44, -114, C), (-43, -150), (-40, -196),
                       (-37, -240), (-36, -270), (-30, -288)],
            inner=[[(18, -280), (8, -254), (-4, -226), (-16, -196), (-28, -162), (-42, -118)],
                   [(-28, -282), (-32, -236), (-35, -190), (-38, -150), (-42, -118)]],
            hatch=[[(10, -244), (-2, -214), (-14, -184), (-26, -152)], [(24, -232), (14, -206), (2, -176), (-10, -148)],
                   [(-20, -268), (-24, -226), (-27, -184), (-31, -140)]],
            shade=[([(-46, -284), (-30, -286), (-36, -120), (-46, -114)], 80, 2.6), ([(-12, -222), (6, -250), (-26, -150), (-36, -140)], 68, 3.6)])
    for (tx_, ty_) in ((34, -152), (-44, -114)):
        F.extra_detail.append([(tx_ - 1.4, ty_ + 1.0), (tx_, ty_ + 3.6), (tx_ + 1.4, ty_ + 1.0)])
        F.extra_hatch += [[(tx_ + o * 0.5, ty_ + 3.4), (tx_ + o, ty_ + 16)] for o in (-1.6, 0.0, 1.6)]
    foreign_head(F, 6.0, -327.0, 0.44, rot=-4.0, mirror=False, name='head', beard='long', cover='hood', expr='frown',
                 age=1, nose_kind='hooked', lv=1)
    F.piece('arm', [(4, -282), (18, -278), (24, -258), (30, -236), (40, -222), (50, -216), (50, -204), (38, -206), (24, -216),
                    (12, -238), (6, -260)],
            hatch=[[(14, -258), (22, -236)], [(10, -264), (18, -240)]])
    baked_hand(F, 'hand', 'grip', 40, -212, 0.0, 1.45, mirror=True)
    F.extra_detail.append(sp([(56, -300), (56.4, -230), (57.2, -150), (58.2, -70), (59.4, -1)], step=1.0))
    return F


def mother_and_son(lod=2):
    """Mother hurrying right, veiled, glancing back at the soldiers, her son by the hand; the boy stares back at them."""
    F = FigDraw()
    F.min_edge = 12.0
    bx = -92
    sandal(F, 'b_backfoot', (bx - 16, -12), (bx - 2, -1), mirror=True)
    F.piece('b_tunic', [(bx - 10, -198), (bx - 19, -182), (bx - 21, -156), (bx - 19, -128), (bx - 24, -96, C), (bx - 2, -92),
                        (bx + 20, -96, C), (bx + 17, -128), (bx + 18, -156), (bx + 17, -180), (bx + 9, -196)],
            inner=[[(bx - 19, -146), (bx, -143), (bx + 18, -146)]],
            hatch=[[(bx + 8, -138), (bx + 12, -104)], [(bx - 6, -138), (bx - 8, -100)]],
            shade=[([(bx - 24, -146), (bx - 10, -146), (bx - 12, -94), (bx - 25, -96)], 76, 2.8)])
    F.piece('b_leg1', limb((bx - 9, -98), (bx - 16, -14), [(0, 6.5, 6.5), (0.3, 6, 7.5), (0.55, 5, 5.5), (1.0, 4, 4)]), edge=False)
    F.piece('b_leg2', limb((bx + 7, -98), (bx + 12, -14), [(0, 6.5, 6.5), (0.3, 7.5, 6), (0.55, 5.5, 5), (1.0, 4, 4)]), edge=False)
    sandal(F, 'b_frontfoot', (bx + 10, -12), (bx + 34, -1), mirror=True)
    foreign_head(F, bx - 2.0, -222.0, 0.38, rot=8.0, mirror=False, name='b_head', beard='none', cover='none', expr='stunned', lv=1)
    F.piece('b_arm', limb((bx + 10, -186), (bx + 40, -176), [(0, 6, 6), (0.4, 5.5, 5.5), (1.0, 4.4, 4.4)]))
    sandal(F, 'm_backfoot', (-22, -14), (0, -1), mirror=True)
    F.piece('m_dress', [(-14, -290), (-24, -270), (-26, -236), (-23, -200), (-27, -160), (-32, -110), (-35, -60), (-38, -22, C),
                        (-10, -17), (16, -19), (38, -24, C), (33, -62), (28, -110), (24, -160), (24, -200), (26, -232), (24, -258),
                        (18, -280), (8, -290)],
            inner=[[(-23, -196), (0, -192), (24, -196)]],
            hatch=[[(30, -62), (33, -40), (35, -26)], [(14, -100), (18, -60), (20, -22)], [(-6, -100), (-8, -60), (-10, -20)],
                   [(-22, -110), (-26, -70), (-30, -24)]],
            shade=[([(-38, -180), (-20, -180), (-26, -22), (-40, -22)], 78, 2.8)])
    sandal(F, 'm_frontfoot', (20, -14), (48, -2), mirror=True)
    F.piece('m_shawl', [(-20, -296), (-6, -300), (6, -294), (8, -270), (2, -240), (-6, -212), (-16, -186), (-30, -176, C),
                        (-34, -206), (-32, -250), (-28, -282)],
            hatch=[[(-24, -272), (-28, -232), (-31, -196)], [(-12, -262), (-18, -226), (-24, -196)]])
    foreign_head(F, 4.0, -324.0, 0.42, rot=-6.0, mirror=False, name='m_head', beard='none', cover='veil', expr='frown', lv=1)
    F.piece('m_arm', [(-14, -262), (-2, -266), (-4, -240), (-12, -214), (-22, -196), (-32, -184), (-38, -192), (-28, -206),
                      (-20, -226), (-14, -248)],
            hatch=[[(-8, -246), (-14, -226)]])
    baked_hand(F, 'm_hand', 'grip', -30, -186, 200.0, 1.25, mirror=True)
    return F
