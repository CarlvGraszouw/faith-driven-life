"""Drawing toolkit shared by the generators a02_temple.py and a05_soldiers.py (v2 whiteboard art).

Strokes are dense polylines.  Every drawable belongs to an Item with a depth `z` (bigger = nearer) and an
optional occluder polygon; at build time each stroke is clipped against the occluders of all nearer items
(so the drawing order is free and no white fills are needed), hatch regions are filled with zig-zag
strokes (one pen stroke per patch), strokes are ordered to keep pen hops short, and the SVG is written
through lib_v2.write() (absolute M/L only).
"""
import math, os, sys
import numpy as np
from shapely.geometry import (Polygon, LineString, MultiLineString, MultiPolygon, GeometryCollection,
                              Point, box as sbox)
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
EP1 = os.path.abspath(os.path.join(HERE, '..', '..'))
if EP1 not in sys.path:
    sys.path.insert(0, EP1)
import lib_v2  # noqa: E402

GOLD, ORANGE, RUST, CLOAK, BLUE = lib_v2.GOLD, lib_v2.ORANGE, lib_v2.RUST, lib_v2.CLOAK, lib_v2.BLUE


# ----------------------------------------------------------------------------- curves
def _crseg(p0, p1, p2, p3, n, alpha=0.5):
    """Centripetal Catmull-Rom from p1 to p2 (n samples, p1 excluded)."""
    def tj(t, a, b):
        return t + max(math.hypot(b[0] - a[0], b[1] - a[1]) ** alpha, 1e-4)
    t0 = 0.0; t1 = tj(t0, p0, p1); t2 = tj(t1, p1, p2); t3 = tj(t2, p2, p3)
    out = []
    for k in range(1, n + 1):
        t = t1 + (t2 - t1) * k / n
        a1 = [((t1 - t) * p0[i] + (t - t0) * p1[i]) / (t1 - t0) for i in (0, 1)]
        a2 = [((t2 - t) * p1[i] + (t - t1) * p2[i]) / (t2 - t1) for i in (0, 1)]
        a3 = [((t3 - t) * p2[i] + (t - t2) * p3[i]) / (t3 - t2) for i in (0, 1)]
        b1 = [((t2 - t) * a1[i] + (t - t0) * a2[i]) / (t2 - t0) for i in (0, 1)]
        b2 = [((t3 - t) * a2[i] + (t - t1) * a3[i]) / (t3 - t1) for i in (0, 1)]
        out.append(tuple(((t2 - t) * b1[i] + (t - t1) * b2[i]) / (t2 - t1) for i in (0, 1)))
    return out


def _run(pts, step):
    """Open smooth run through pts."""
    P = [tuple(p[:2]) for p in pts]
    if len(P) == 1:
        return P
    if len(P) == 2:
        n = max(1, int(math.hypot(P[1][0] - P[0][0], P[1][1] - P[0][1]) / step))
        return [P[0]] + [(P[0][0] + (P[1][0] - P[0][0]) * k / n, P[0][1] + (P[1][1] - P[0][1]) * k / n) for k in range(1, n + 1)]
    ext = [(2 * P[0][0] - P[1][0], 2 * P[0][1] - P[1][1])] + P + [(2 * P[-1][0] - P[-2][0], 2 * P[-1][1] - P[-2][1])]
    out = [P[0]]
    for i in range(1, len(ext) - 2):
        d = math.hypot(ext[i + 1][0] - ext[i][0], ext[i + 1][1] - ext[i][1])
        out += _crseg(ext[i - 1], ext[i], ext[i + 1], ext[i + 2], max(2, int(d / step) + 1))
    return out


def sp(pts, closed=False, step=1.2):
    """Smooth curve through pts (centripetal Catmull-Rom). A point (x, y, 1) is a sharp corner.
    Returns a dense polyline (list of (x, y))."""
    pts = [tuple(p) for p in pts]
    if closed:
        corners = [i for i, p in enumerate(pts) if len(p) > 2 and p[2]]
        if not corners:
            P = [p[:2] for p in pts]
            n = len(P)
            out = [P[0]]
            for i in range(n):
                d = math.hypot(P[(i + 1) % n][0] - P[i][0], P[(i + 1) % n][1] - P[i][1])
                out += _crseg(P[i - 1], P[i], P[(i + 1) % n], P[(i + 2) % n], max(2, int(d / step) + 1))
            return out
        k = corners[0]
        pts = pts[k:] + pts[:k] + [pts[k]]
    out, cur = [], [pts[0]]
    for p in pts[1:]:
        cur.append(p)
        if len(p) > 2 and p[2]:
            seg = _run(cur, step)
            out += seg if not out else seg[1:]
            cur = [p]
    if len(cur) > 1:
        seg = _run(cur, step)
        out += seg if not out else seg[1:]
    return out


def poly(pts):
    """Straight polyline (all corners)."""
    return [tuple(p[:2]) for p in pts]


def arc(cx, cy, rx, ry, a0, a1, rot=0.0, step=1.2):
    """Ellipse arc from angle a0 to a1 (degrees; 0 = +x, 90 = +y/down), rotated by rot degrees."""
    n = max(4, int(abs(math.radians(a1 - a0)) * max(rx, ry) / step) + 1)
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def xf(pts, s=1.0, dx=0.0, dy=0.0, rot=0.0, sx=None, sy=None, ox=0.0, oy=0.0):
    """scale about (ox, oy) (sx/sy override s; negative sx mirrors), rotate rot deg, then translate."""
    sx = s if sx is None else sx
    sy = s if sy is None else sy
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for p in pts:
        x, y = (p[0] - ox) * sx, (p[1] - oy) * sy
        out.append((x * c - y * sn + dx, x * sn + y * c + dy) + tuple(p[2:]))
    return out


def plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def resample(pts, step):
    """Uniformly resample a polyline."""
    if len(pts) < 2:
        return list(pts)
    L = plen(pts)
    n = max(1, int(L / step))
    ls = LineString(pts)
    return [tuple(ls.interpolate(L * k / n).coords[0]) for k in range(n + 1)]


def offset_pts(pts, d):
    """Offset an open polyline sideways by d (positive = left of travel in screen coords)."""
    out = []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        out.append((p[0] + ty / L * d, p[1] - tx / L * d))
    return out


def jitter(pts, amp, seed=0, wav=40.0):
    """Gentle hand wobble along a polyline (low frequency)."""
    rng = np.random.default_rng(seed)
    ph1, ph2 = rng.uniform(0, 6.28, 2)
    out, acc = [], 0.0
    for i, p in enumerate(pts):
        if i:
            acc += math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1])
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        w = amp * (0.6 * math.sin(acc / wav * 6.28 + ph1) + 0.4 * math.sin(acc / (wav * 0.37) * 6.28 + ph2))
        out.append((p[0] + ty / L * w, p[1] - tx / L * w))
    return out


def to_poly(pts):
    g = Polygon([p[:2] for p in pts])
    if not g.is_valid:
        g = g.buffer(0)
    return g


# ----------------------------------------------------------------------------- hatching
def hatch_lines(region, angle, spacing, phase=0.0, min_len=3.0):
    """Parallel hatch segments (list of [(x,y),(x,y)]) inside region at `angle` degrees (0 = horizontal,
    measured clockwise on screen), ordered line by line."""
    if region is None or region.is_empty:
        return []
    c = region.centroid
    r = affinity.rotate(region, -angle, origin=c)
    x0, y0, x1, y1 = r.bounds
    segs = []
    y = y0 + (phase % 1.0) * spacing + spacing * 0.5
    row = 0
    while y < y1:
        ln = LineString([(x0 - 5, y), (x1 + 5, y)])
        inter = r.intersection(ln)
        parts = [inter] if isinstance(inter, LineString) else [g for g in getattr(inter, 'geoms', []) if isinstance(g, LineString)]
        parts = sorted([p for p in parts if p.length >= min_len], key=lambda g: g.coords[0][0])
        for p in parts:
            back = affinity.rotate(p, angle, origin=c)
            segs.append((row, list(back.coords)))
        y += spacing
        row += 1
    return segs


def zigzag(region, angle, spacing, phase=0.0, min_len=3.0, max_link=None, tail=0.0):
    """Hatch a region with zig-zag strokes: consecutive parallel segments are joined end to end
    (boustrophedon) while the joining hop is short and stays inside the region. Returns polylines."""
    segs = hatch_lines(region, angle, spacing, phase, min_len)
    if not segs:
        return []
    max_link = max_link if max_link is not None else spacing * 2.6
    reg = region.buffer(spacing * 0.6)
    used = [False] * len(segs)
    strokes = []
    for i in range(len(segs)):
        if used[i]:
            continue
        used[i] = True
        row, s = segs[i]
        cur = list(s)
        last_row = row
        while True:
            end = cur[-1]
            best, bd = None, 1e9
            for j in range(i + 1, len(segs)):
                if used[j]:
                    continue
                rj, sj = segs[j]
                if rj <= last_row:
                    continue
                if rj > last_row + 1:
                    break
                for rev in (False, True):
                    a = sj[-1] if rev else sj[0]
                    d = math.hypot(a[0] - end[0], a[1] - end[1])
                    if d < bd:
                        bd, best = d, (j, rev)
            if best is None or bd > max_link:
                break
            j, rev = best
            sj = segs[j][1][::-1] if rev else segs[j][1]
            if not reg.contains(LineString([end, sj[0]])):
                break
            used[j] = True
            cur += list(sj)
            last_row = segs[j][0]
        strokes.append(cur)
    if tail:
        strokes = [s for s in strokes if plen(s) > tail]
    return strokes


# ----------------------------------------------------------------------------- scene graph
class Item:
    """A drawable at depth z (bigger = nearer) in drawing group `group`."""

    def __init__(self, board, z, group, name=''):
        self.board, self.z, self.group, self.name = board, z, group, name
        self.strokes = []   # (cls, pts, phase)
        self.hatches = []   # (region, angle, spacing, phase_off, cls, group, kwargs)
        self.fills = []     # (pts, colour, cls)
        self.occ = None

    def add(self, cls, pts, phase=None, closed=False):
        pts = [tuple(p[:2]) for p in pts]
        if closed and pts and pts[0] != pts[-1]:
            pts = pts + [pts[0]]
        if len(pts) >= 2:
            ph = phase if phase is not None else {'line': 0, 'detail': 1, 'hatch': 2}[cls]
            self.strokes.append((cls, pts, ph))
        return self

    def L(self, pts, **k): return self.add('line', pts, **k)
    def D(self, pts, **k): return self.add('detail', pts, **k)
    def H(self, pts, **k): return self.add('hatch', pts, **k)

    def occlude(self, geom):
        if isinstance(geom, (list, tuple)):
            geom = to_poly(geom)
        if geom is None or geom.is_empty:
            return self
        self.occ = geom if self.occ is None else self.occ.union(geom)
        return self

    def hatch(self, region, angle=45, spacing=7.0, phase=0.0, cls='hatch', group=None, **kw):
        if isinstance(region, (list, tuple)):
            region = to_poly(region)
        self.hatches.append((region, angle, spacing, phase, cls, group, kw))
        return self

    def fill(self, pts, colour, cls='detail'):
        self.fills.append((pts, colour, cls))
        return self

    def bounds(self):
        xs, ys = [], []
        for _, pts, _ in self.strokes:
            for p in pts:
                xs.append(p[0]); ys.append(p[1])
        for h in self.hatches:
            b = h[0].bounds
            xs += [b[0], b[2]]; ys += [b[1], b[3]]
        for pts, _, _ in self.fills:
            for p in pts:
                xs.append(p[0]); ys.append(p[1])
        if self.occ is not None:
            b = self.occ.bounds
            xs += [b[0], b[2]]; ys += [b[1], b[3]]
        if not xs:
            return None
        return (min(xs), min(ys), max(xs), max(ys))


def _lines_of(g):
    if g.is_empty:
        return []
    if isinstance(g, LineString):
        return [list(g.coords)]
    out = []
    for h in getattr(g, 'geoms', []):
        out += _lines_of(h)
    return out


def rings(g, min_area=4.0):
    """exterior rings of all polygons in g (largest first)"""
    ps = sorted(_polys_of(g), key=lambda q: -q.area)
    return [list(q.exterior.coords) for q in ps if q.area >= min_area]


def _polys_of(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    out = []
    for h in getattr(g, 'geoms', []):
        out += _polys_of(h)
    return out


class Board:
    def __init__(self, gap=2.2, min_piece=2.5):
        self.items = []
        self.gap, self.min_piece = gap, min_piece

    def item(self, z, group, name=''):
        it = Item(self, z, group, name)
        self.items.append(it)
        return it

    # -------------------------------------------------------------- build
    def _occ_for(self, it, tree, occs):
        b = it.bounds()
        if b is None:
            return None
        idx = tree.query(sbox(*b).buffer(self.gap + 1)) if tree is not None else []
        near = [occs[i][1] for i in idx if occs[i][0] > it.z]
        if not near:
            return None
        return unary_union(near)

    def build(self, group_order, hatch_last=True, start=(1500, 820), canvas=(-2, -2, 1602, 902)):
        cbox = sbox(*canvas)
        occs = [(it.z, it.occ) for it in self.items if it.occ is not None and not it.occ.is_empty]
        tree = STRtree([o for _, o in occs]) if occs else None
        groups = {g: [] for g in group_order}
        fills = {g: [] for g in group_order}
        for it in self.items:
            occ = self._occ_for(it, tree, occs)
            occb = occ.buffer(self.gap) if occ is not None else None
            g = it.group
            for cls, pts, ph in it.strokes:
                ls = LineString(pts)
                if not cbox.contains(ls):
                    ls = ls.intersection(cbox)
                if occb is not None and ls.intersects(occb):
                    pieces = _lines_of(ls.difference(occb))
                else:
                    pieces = _lines_of(ls)
                for pc in pieces:
                    if plen(pc) >= self.min_piece:
                        groups[g].append([cls, pc, ph])
            for region, ang, spc, phs, cls, hg, kw in it.hatches:
                reg = region.intersection(cbox)
                if occb is not None:
                    reg = reg.difference(occ.buffer(self.gap * 0.7))
                if reg.is_empty:
                    continue
                cross = kw.get('cross')
                lines = zigzag(reg, ang, spc, phs, max_link=kw.get('max_link'), tail=kw.get('tail', 0.0))
                if cross:
                    lines += zigzag(reg.buffer(-spc * 0.3) if kw.get('cross_shrink') else reg, cross, kw.get('cross_spacing', spc), phs + 0.5,
                                    max_link=kw.get('max_link'))
                tg = hg if hg is not None else ('__hatch__' if hatch_last else g)
                groups.setdefault(tg, [])
                for ln in lines:
                    groups[tg].append([cls, ln, 3 if hatch_last else 2])
            for pts, colour, cls in it.fills:
                pg = to_poly(pts)
                if occ is not None:
                    pg = pg.difference(occ)
                for p in _polys_of(pg):
                    if p.area > 4:
                        fills[g].append((cls, list(p.exterior.coords), colour))
        order = list(group_order) + (['__hatch__'] if hatch_last and '__hatch__' not in group_order else [])
        pen = start
        out = []
        self.stats = {}
        for g in order:
            for st in groups.get(g, []):
                if st[0] != 'hatch':
                    a = self.stats.setdefault((g, st[0]), [0, 0.0]); a[0] += 1; a[1] += plen(st[1])
        for g in order:
            strokes = groups.get(g, [])
            for cls, pts, colour in fills.get(g, []):
                out.append((cls, pts, colour))
            for ph in sorted(set(s[2] for s in strokes)):
                batch = [s for s in strokes if s[2] == ph]
                seq, pen = _nn_order(batch, pen)
                out += [(s[0], s[1], None) for s in seq]
        self.out = out
        return out

    # -------------------------------------------------------------- output
    def svg(self, comment='', simplify=0.12):
        body = []
        for cls, pts, colour in self.out:
            if colour is None:
                ls = LineString(pts).simplify(simplify, preserve_topology=False)
                c = list(ls.coords)
                if len(c) < 2:
                    continue
                d = 'M ' + ' L '.join(f'{lib_v2.f1(x)} {lib_v2.f1(y)}' for x, y in c)
                body.append(f'  <path class="{cls}" d="{d}"/>\n')
            else:
                pg = Polygon(pts).simplify(simplify)
                c = list(pg.exterior.coords)[:-1]
                d = 'M ' + ' L '.join(f'{lib_v2.f1(x)} {lib_v2.f1(y)}' for x, y in c) + ' Z'
                body.append(f'  <path class="{cls}" fill="{colour}" style="mix-blend-mode:multiply" d="{d}"/>\n')
        return lib_v2.svg(''.join(body), comment)

    def write(self, path, comment=''):
        txt = self.svg(comment)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        lib_v2.write(path, txt)
        return txt


def _nn_order(batch, pen):
    """Greedy nearest-neighbour ordering; open strokes may be reversed, closed ones rotated."""
    rest = list(range(len(batch)))
    seq = []
    while rest:
        best, bd, mode = None, 1e18, None
        for i in rest:
            pts = batch[i][1]
            closed = len(pts) > 3 and math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 0.5
            if closed:
                arr = np.asarray(pts)
                dd = np.hypot(arr[:, 0] - pen[0], arr[:, 1] - pen[1])
                k = int(np.argmin(dd))
                if dd[k] < bd:
                    bd, best, mode = dd[k], i, ('rot', k)
            else:
                d0 = math.hypot(pts[0][0] - pen[0], pts[0][1] - pen[1])
                d1 = math.hypot(pts[-1][0] - pen[0], pts[-1][1] - pen[1])
                if d0 < bd:
                    bd, best, mode = d0, i, ('fwd', 0)
                if d1 < bd:
                    bd, best, mode = d1, i, ('rev', 0)
        s = batch[best]
        pts = s[1]
        if mode[0] == 'rev':
            pts = pts[::-1]
        elif mode[0] == 'rot' and mode[1]:
            k = mode[1]
            pts = pts[k:-1] + pts[:k + 1]
        seq.append([s[0], pts, s[2]])
        pen = pts[-1]
        rest.remove(best)
    return seq, pen


# ----------------------------------------------------------------------------- 3D camera
class Cam:
    """Pinhole camera with zero pitch (verticals stay vertical); principal point (cx, cy) may be shifted."""

    def __init__(self, pos, az, f, cx=800.0, cy=450.0):
        self.pos = np.asarray(pos, float)
        a = math.radians(az)
        self.fwd = np.array([math.cos(a), math.sin(a), 0.0])
        self.right = np.array([math.sin(a), -math.cos(a), 0.0])
        self.f, self.cx, self.cy = f, cx, cy

    def depth(self, P):
        return float(np.dot(np.asarray(P, float) - self.pos, self.fwd))

    def p(self, P):
        d = np.asarray(P, float) - self.pos
        z = float(np.dot(d, self.fwd))
        z = max(z, 0.5)
        return (self.cx + self.f * float(np.dot(d, self.right)) / z, self.cy - self.f * d[2] / z)

    def pl(self, Ps, n=1):
        """Project a 3D polyline; each straight 3D segment is subdivided n times (n>1 only for long lines)."""
        out = []
        for i in range(len(Ps) - 1):
            a, b = np.asarray(Ps[i], float), np.asarray(Ps[i + 1], float)
            for k in range(0 if i == 0 else 1, n + 1):
                out.append(self.p(a + (b - a) * k / n))
        if len(Ps) == 1:
            out.append(self.p(Ps[0]))
        return out

    def scale(self, P):
        """screen units per metre at world point P."""
        return self.f / max(self.depth(P), 0.5)

    def _cut(self, a, b, near):
        da, db = self.depth(a), self.depth(b)
        t = (near - da) / (db - da)
        return tuple(np.asarray(a, float) + (np.asarray(b, float) - np.asarray(a, float)) * t)

    def poly3(self, Ps, near=3.0):
        """Project a 3D polygon clipped to depth >= near (Sutherland-Hodgman). Returns 2D points."""
        out = []
        n = len(Ps)
        for i in range(n):
            a, b = Ps[i], Ps[(i + 1) % n]
            ia, ib = self.depth(a) >= near, self.depth(b) >= near
            if ia:
                out.append(tuple(a))
            if ia != ib:
                out.append(self._cut(a, b, near))
        return [self.p(q) for q in out]

    def line3(self, Ps, near=3.0, n=1):
        """Project a 3D polyline clipped to depth >= near; returns a list of 2D polylines."""
        runs, cur = [], []
        for i in range(len(Ps) - 1):
            a, b = Ps[i], Ps[i + 1]
            ia, ib = self.depth(a) >= near, self.depth(b) >= near
            if not ia and not ib:
                if cur:
                    runs.append(cur); cur = []
                continue
            a2 = a if ia else self._cut(a, b, near)
            b2 = b if ib else self._cut(a, b, near)
            seg = self.pl([a2, b2], n)
            if cur and math.hypot(cur[-1][0] - seg[0][0], cur[-1][1] - seg[0][1]) < 1e-6:
                cur += seg[1:]
            else:
                if cur:
                    runs.append(cur)
                cur = list(seg)
            if not ib:
                runs.append(cur); cur = []
        if cur:
            runs.append(cur)
        return runs


# ----------------------------------------------------------------------------- timing estimate
def timing(out, S=0.9556):
    """Hand time per the coordinator's updated engine: line strokes 0.15 s lift + length at v px/s,
    detail strokes 0.04 s lift + length at 1.8 v, hatch self-draws afterwards (free).
    'flat' charges the full lift on every stroke; 'near' scales lifts by hop distance like engine.js."""
    ev = []
    for cls, pts, colour in out:
        if cls == 'hatch' and colour is None:
            continue
        L = plen(pts) * S
        ev.append((cls, L, (pts[0][0] * S, pts[0][1] * S), (pts[-1][0] * S, pts[-1][1] * S)))

    def sim(v, flat):
        t, prev = 0.0, None
        for k, L, p0, p1 in ev:
            vv = v * (1.8 if k == 'detail' else 1.0)
            if prev:
                d = math.hypot(p0[0] - prev[0], p0[1] - prev[1])
                f = 1.0 if flat else min(1, max(0.35, 0.35 + d / 250))
                t += d / (2.6 * v) + (0.04 if k == 'detail' else 0.15) * f
            t += max(L, 3) / vv
            prev = p1
        return t
    lens = {}
    for cls, pts, colour in out:
        a = lens.setdefault(cls, [0, 0.0]); a[0] += 1; a[1] += plen(pts)
    return {'counts(n, art units)': {k: (v[0], round(v[1])) for k, v in lens.items()},
            'hand@2200 flat': round(sim(2200, True), 2), 'hand@2200 near': round(sim(2200, False), 2),
            'hand@3000 flat': round(sim(3000, True), 2)}
