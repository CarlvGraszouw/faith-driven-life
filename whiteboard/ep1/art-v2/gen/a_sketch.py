"""Pure-python sketch helpers for v2 art (batch A + jesus.py).  No numpy/shapely needed.

Paths are strings of ABSOLUTE M/L/C/Q/Z commands (lib_v2 conventions).
- chain(*runs)            Catmull-Rom runs joined with corners -> one path
- flatten(d)              path -> list of polylines (lists of (x,y))
- poly(d)                 closed path -> polygon (list of (x,y))
- clip(d, polys, keep)    keep the parts of d outside (keep='out') or inside ('in') polygons -> M/L path
- hatch(polygon, ...)     parallel strokes clipped to a polygon -> M/L path
- xf(pts, s, dx, dy, mirror) transform a point list
"""
import math, os, sys, random

HERE = os.path.dirname(os.path.abspath(__file__))
EP1 = os.path.dirname(os.path.dirname(HERE))
if EP1 not in sys.path:
    sys.path.insert(0, EP1)
from lib_v2 import f1, smooth, TOK  # noqa: E402


# ---------------------------------------------------------------- path building
def _strip_m(d):
    toks = d.split()
    assert toks[0] == "M"
    return " ".join(toks[3:])


def chain(*runs, closed=False, t=0.5):
    """Each run is a list of points (>=2).  Runs are joined end-to-start; a run of 2 points is a
    straight line.  Consecutive runs should share their joint point (it is skipped if equal)."""
    out = []
    cur = None
    for run in runs:
        run = [tuple(p) for p in run]
        if cur is not None and abs(run[0][0] - cur[0]) < 1e-6 and abs(run[0][1] - cur[1]) < 1e-6:
            pass
        elif cur is not None:
            out.append(f"L {f1(run[0][0])} {f1(run[0][1])}")
        else:
            out.append(f"M {f1(run[0][0])} {f1(run[0][1])}")
        if len(run) == 2:
            out.append(f"L {f1(run[1][0])} {f1(run[1][1])}")
        else:
            out.append(_strip_m(smooth(run, t=t)))
        cur = run[-1]
    if closed:
        out.append("Z")
    return " ".join(out)


def sm(pts, closed=False, t=0.5):
    return smooth([tuple(p) for p in pts], closed=closed, t=t)


def seg(*pts):
    """Polyline M/L through points."""
    return "M " + " L ".join(f"{f1(x)} {f1(y)}" for x, y in pts)


def cat(*ds):
    return " ".join(d for d in ds if d)


# ---------------------------------------------------------------- flattening
def _bez3(p0, p1, p2, p3, n):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t * t; e = t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return pts


def _bez2(p0, p1, p2, n):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        a = (1 - t) ** 2; b = 2 * (1 - t) * t; c = t * t
        pts.append((a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]))
    return pts


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def flatten(d, step=2.0):
    """-> list of polylines.  Closed subpaths repeat their first point at the end."""
    toks = TOK.findall(d)
    i = 0
    lines, cur, start, pos = [], None, None, None
    cmd = None

    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd == "Z":
                if cur is not None and start is not None:
                    cur.append(start)
                    pos = start
                continue
        if cmd == "M":
            pos = (num(), num()); start = pos
            cur = [pos]; lines.append(cur)
            cmd = "L"  # implicit lineto after moveto
        elif cmd == "L":
            p = (num(), num())
            n = max(1, int(_dist(pos, p) / step))
            for k in range(1, n + 1):
                cur.append((pos[0] + (p[0] - pos[0]) * k / n, pos[1] + (p[1] - pos[1]) * k / n))
            pos = p
        elif cmd == "C":
            p1 = (num(), num()); p2 = (num(), num()); p3 = (num(), num())
            L = _dist(pos, p1) + _dist(p1, p2) + _dist(p2, p3)
            cur.extend(_bez3(pos, p1, p2, p3, max(2, int(L / step))))
            pos = p3
        elif cmd == "Q":
            p1 = (num(), num()); p2 = (num(), num())
            L = _dist(pos, p1) + _dist(p1, p2)
            cur.extend(_bez2(pos, p1, p2, max(2, int(L / step))))
            pos = p2
        else:
            raise ValueError("bad command " + str(cmd))
    return lines


def length(d):
    return sum(sum(_dist(a, b) for a, b in zip(pl, pl[1:])) for pl in flatten(d, 1.0))


def poly(d, step=2.0):
    pls = flatten(d, step)
    return max(pls, key=len)


# ---------------------------------------------------------------- polygons
def inside(p, pg):
    x, y = p
    c = False
    n = len(pg)
    j = n - 1
    for i in range(n):
        xi, yi = pg[i]; xj, yj = pg[j]
        if (yi > y) != (yj > y):
            xc = xi + (y - yi) * (xj - xi) / (yj - yi)
            if x < xc:
                c = not c
        j = i
    return c


def _in_any(p, polys):
    return any(inside(p, pg) for pg in polys)


def clip(d, polys, keep="out", step=1.2, min_len=2.5):
    """Keep the parts of path d outside (keep='out') or inside (keep='in') the union of polys."""
    if polys and isinstance(polys[0][0], (int, float)):
        polys = [polys]
    want_in = keep == "in"
    out = []
    for pl in flatten(d, step):
        run = []
        prev = None
        for p in pl:
            ok = _in_any(p, polys) == want_in
            if ok:
                if not run and prev is not None:
                    # refine entry point
                    a, b = prev, p
                    for _ in range(10):
                        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                        if (_in_any(m, polys) == want_in):
                            b = m
                        else:
                            a = m
                    run.append(b)
                run.append(p)
            else:
                if run:
                    a, b = run[-1], p
                    for _ in range(10):
                        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                        if (_in_any(m, polys) == want_in):
                            a = m
                        else:
                            b = m
                    run.append(a)
                    out.append(run)
                    run = []
            prev = p
        if run:
            out.append(run)
    res = []
    for r in out:
        L = sum(_dist(a, b) for a, b in zip(r, r[1:]))
        if L >= min_len:
            res.append(simplify(r))
    return " ".join(seg(*r) for r in res)


def simplify(pts, tol=0.35):
    """Ramer-Douglas-Peucker."""
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1e-9
    best, bi = -1, 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        dd = abs((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / L
        if dd > best:
            best, bi = dd, i
    if best > tol:
        return simplify(pts[:bi + 1], tol)[:-1] + simplify(pts[bi:], tol)
    return [a, b]


def hatch(pg, angle=45, spacing=4.0, jitter=0.0, shrink=0.0, seed=1, offset=0.0, every=None, min_len=2.0):
    """Parallel strokes at `angle` (deg, 0 = horizontal) clipped to polygon pg -> M/L path.
    shrink: trim each stroke end by this many units; jitter: random end variation."""
    rnd = random.Random(seed)
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    # rotate polygon by -angle so strokes become horizontal
    rp = [(x * ca + y * sa, -x * sa + y * ca) for x, y in pg]
    ys = [p[1] for p in rp]
    y0, y1 = min(ys), max(ys)
    out = []
    k = 0
    y = y0 + spacing * 0.5 + offset
    while y < y1:
        xs = []
        n = len(rp)
        for i in range(n):
            (xa, ya), (xb, yb) = rp[i], rp[(i + 1) % n]
            if (ya > y) != (yb > y):
                xs.append(xa + (y - ya) * (xb - xa) / (yb - ya))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            xa, xb = xs[j] + shrink + rnd.uniform(0, jitter), xs[j + 1] - shrink - rnd.uniform(0, jitter)
            if xb - xa >= min_len and (every is None or every(k)):
                p = (xa * ca - y * sa, xa * sa + y * ca)
                q = (xb * ca - y * sa, xb * sa + y * ca)
                out.append(f"M {f1(p[0])} {f1(p[1])} L {f1(q[0])} {f1(q[1])}")
        y += spacing
        k += 1
    return " ".join(out)


# ---------------------------------------------------------------- transforms
def xf(pts, s=1.0, dx=0.0, dy=0.0, mirror=False, rot=0.0, ox=0.0, oy=0.0):
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    res = []
    for x, y in pts:
        x, y = (x - ox), (y - oy)
        x, y = x * c - y * sn, x * sn + y * c
        x *= s; y *= s
        if mirror:
            x = -x
        res.append((x + dx, y + dy))
    return res


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def line_len_of(svgtext):
    """Total length of class="line" paths in an svg string (art units)."""
    import re
    tot = 0.0
    for m in re.finditer(r'<path class="line"[^>]* d="([^"]+)"', svgtext):
        tot += length(m.group(1))
    return tot


# ---------------------------------------------------------------- curves & limbs
def resample(pts, n):
    """Resample a polyline (through the given points, Catmull-Rom smoothed) to n points by arc length."""
    pl = flatten(sm(pts), 0.5)[0] if len(pts) > 2 else [tuple(pts[0]), tuple(pts[1])]
    if len(pl) == 2:
        return [lerp(pl[0], pl[1], i / (n - 1)) for i in range(n)]
    cum = [0.0]
    for a, b in zip(pl, pl[1:]):
        cum.append(cum[-1] + _dist(a, b))
    tot = cum[-1]
    out, j = [], 0
    for i in range(n):
        s = tot * i / (n - 1)
        while j < len(cum) - 2 and cum[j + 1] < s:
            j += 1
        seg_len = (cum[j + 1] - cum[j]) or 1e-9
        out.append(lerp(pl[j], pl[j + 1], (s - cum[j]) / seg_len))
    return out


def between(a, b, n, n_pts=12, trim=(0.0, 1.0)):
    """n curves interpolated between curves a and b (exclusive) -> list of point lists."""
    A, B = resample(a, n_pts), resample(b, n_pts)
    res = []
    for k in range(1, n + 1):
        t = k / (n + 1)
        c = [lerp(p, q, t) for p, q in zip(A, B)]
        i0, i1 = int(trim[0] * (n_pts - 1)), int(round(trim[1] * (n_pts - 1)))
        res.append(c[i0:i1 + 1])
    return res


def tube(center, widths):
    """Offset a centre line by +/- width/2 along normals -> (left_pts, right_pts).
    'left' is to the left of the direction of travel (in screen coords, y down)."""
    n = len(center)
    lefts, rights = [], []
    for i, (x, y) in enumerate(center):
        a = center[max(0, i - 1)]; b = center[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1e-9
        nx, ny = dy / L, -dx / L
        w = widths[i] / 2.0
        lefts.append((x + nx * w, y + ny * w))
        rights.append((x - nx * w, y - ny * w))
    return lefts, rights
