"""Small geometry kit for the v2 coin scenes: dense polylines, smoothing, clipping, zig-zag hatching.

Everything works on plain (x, y) tuples in art units. Output path data uses absolute M/L/C only,
so it passes lib_v2.check_paths. The engine lifts the pen at every M, so the helpers here try to
produce FEW, LONG sub-paths (zig-zag hatching is one continuous stroke per patch).
"""
import math, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from lib_v2 import f1, smooth  # noqa: E402


# ------------------------------------------------------------------ basic curves
def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def bez3(p0, p1, p2, p3, n=16):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return out


def cr_dense(pts, n=10, closed=False, t=0.5):
    """Catmull-Rom through pts, returned as a dense polyline (same curve as lib_v2.smooth)."""
    P = list(pts)
    if len(P) < 2:
        return P
    P = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    out = [P[1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        out += bez3(p1, c1, c2, p2, n)[1:]
    return out


def ell_pts(cx, cy, rx, ry, a0, a1, n=48, rot=0.0):
    """points on an ellipse, angles in degrees, y DOWN (0 = right, 90 = down)."""
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def plen(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def resample(pts, step):
    """evenly spaced points along a polyline (keeps both ends)."""
    if len(pts) < 2:
        return list(pts)
    L = plen(pts)
    n = max(1, int(round(L / step)))
    out, seg, acc = [pts[0]], 0, 0.0
    targets = [L * i / n for i in range(1, n)]
    d0 = 0.0
    for tgt in targets:
        while seg < len(pts) - 1:
            dl = math.dist(pts[seg], pts[seg + 1])
            if d0 + dl >= tgt and dl > 0:
                out.append(lerp(pts[seg], pts[seg + 1], (tgt - d0) / dl))
                break
            d0 += dl; seg += 1
    out.append(pts[-1])
    return out


def rdp(pts, eps):
    """Ramer-Douglas-Peucker simplification."""
    if len(pts) < 3:
        return list(pts)
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    imax, dmax = 0, -1
    for i in range(1, len(pts) - 1):
        if L < 1e-6:   # closed run: distance from the start point
            d = math.dist(pts[i], a)
        else:
            d = abs((pts[i][0] - a[0]) * dy - (pts[i][1] - a[1]) * dx) / L
        if d > dmax:
            imax, dmax = i, d
    if dmax <= eps:
        return [a, b]
    return rdp(pts[: imax + 1], eps)[:-1] + rdp(pts[imax:], eps)


# ------------------------------------------------------------------ path output
def poly_d(pts, closed=False, eps=0.25):
    """polyline -> 'M x y L ...' (simplified)."""
    p = rdp(pts, eps) if eps else pts
    d = f"M {f1(p[0][0])} {f1(p[0][1])}" + "".join(f" L {f1(x)} {f1(y)}" for x, y in p[1:])
    return d + (" Z" if closed else "")


def curve_d(pts, closed=False, step=None):
    """smooth Catmull-Rom path through pts (optionally resampled first)."""
    p = resample(pts, step) if step else pts
    return smooth(p, closed=closed)


# ------------------------------------------------------------------ transforms
def xf(pts, s=1.0, dx=0.0, dy=0.0, rot=0.0, ox=0.0, oy=0.0, sx=None, sy=None):
    sx = s if sx is None else sx
    sy = s if sy is None else sy
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for x, y in pts:
        x, y = (x - ox) * sx, (y - oy) * sy
        out.append((x * c - y * sn + dx, x * sn + y * c + dy))
    return out


# ------------------------------------------------------------------ polygons
def inside(pt, poly):
    x, y = pt
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x:
                c = not c
    return c


def clip_outside(pts, polys, step=1.5, min_len=4.0):
    """split a polyline into the runs that lie OUTSIDE every polygon in polys (occlusion)."""
    P = resample(pts, step)
    runs, cur = [], []
    for p in P:
        if any(inside(p, q) for q in polys):
            if len(cur) > 1 and plen(cur) >= min_len:
                runs.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1 and plen(cur) >= min_len:
        runs.append(cur)
    return runs


def clip_inside(pts, poly, step=1.5, min_len=4.0):
    P = resample(pts, step)
    runs, cur = [], []
    for p in P:
        if inside(p, poly):
            cur.append(p)
        else:
            if len(cur) > 1 and plen(cur) >= min_len:
                runs.append(cur)
            cur = []
    if len(cur) > 1 and plen(cur) >= min_len:
        runs.append(cur)
    return runs


# ------------------------------------------------------------------ hatching
def _scan(polys, y):
    xs = []
    for poly in polys:
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
            if (y1 > y) != (y2 > y):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    xs.sort()
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]


def zigzag(polys, angle, spacing, inset=0.0, max_link=None, wobble=0.0, seed=1, taper=0.0):
    """Parallel hatch strokes at `angle` (deg, image coords) filling the region given by polys
    (even-odd), chained boustrophedon-style into continuous zig-zag strokes.
    Returns a list of polylines. max_link: longest allowed connector before starting a new stroke.
    taper: shorten each stroke end by up to this fraction (random) so ends look hand-made."""
    import random
    rnd = random.Random(seed)
    if isinstance(polys[0][0], (int, float)):
        polys = [polys]
    a = math.radians(angle)
    ca, sa = math.cos(-a), math.sin(-a)
    R = [[(x * ca - y * sa, x * sa + y * ca) for x, y in p] for p in polys]
    ys = [y for p in R for _, y in p]
    y0, y1 = min(ys), max(ys)
    rows = []
    y = y0 + spacing * 0.5
    while y < y1:
        segs = [(xa + inset, xb - inset) for xa, xb in _scan(R, y) if xb - xa > 2 * inset + 1.0]
        rows.append((y, segs))
        y += spacing
    max_link = max_link if max_link is not None else spacing * 3.0
    chains, open_ = [], []          # open_: list of (chain, last_x_end, direction)
    for y, segs in rows:
        new_open = []
        used = set()
        for ch, xe, dirn in open_:
            best, bi = None, -1
            for i, (xa, xb) in enumerate(segs):
                if i in used:
                    continue
                xn = xb if dirn > 0 else xa       # continue from the same side
                dd = abs(xn - xe)
                if dd <= max_link and (best is None or dd < best):
                    best, bi = dd, i
            if bi >= 0:
                used.add(bi)
                xa, xb = segs[bi]
                w = rnd.uniform(-wobble, wobble)
                if dirn > 0:   # previous went left->right, so this one goes right->left
                    ch += [(xb, y + w), (xa, y - w)]
                    new_open.append((ch, xa, -1))
                else:
                    ch += [(xa, y + w), (xb, y - w)]
                    new_open.append((ch, xb, 1))
            else:
                chains.append(ch)
        for i, (xa, xb) in enumerate(segs):
            if i not in used:
                ch = [(xa, y), (xb, y)]
                new_open.append((ch, xb, 1))
        open_ = new_open
    chains += [ch for ch, _, _ in open_]
    cb, sb = math.cos(a), math.sin(a)
    out = []
    for ch in chains:
        if taper:
            ch2 = []
            for i in range(0, len(ch) - 1, 2):
                p, q = ch[i], ch[i + 1]
                k1, k2 = rnd.uniform(0, taper), rnd.uniform(0, taper)
                ch2 += [lerp(p, q, k1), lerp(q, p, k2)]
            ch = ch2
        out.append([(x * cb - y * sb, x * sb + y * cb) for x, y in ch])
    return out


def ring_poly(cx, cy, r0, r1, a0, a1, n=40):
    """annular sector polygon (angles deg, y down)."""
    outer = ell_pts(cx, cy, r1, r1, a0, a1, n)
    inner = ell_pts(cx, cy, r0, r0, a1, a0, n)
    return outer + inner


# ------------------------------------------------------------------ path sampling
import re as _re
_TOK = _re.compile(r"[MLCQZ]|-?\d*\.?\d+(?:e-?\d+)?")


def path_subpaths(d, n=12):
    """absolute M/L/C/Q/Z path data -> list of dense polylines (one per sub-path)."""
    toks = _TOK.findall(d)
    out, cur, i, cmd = [], None, 0, None
    pos = start = (0.0, 0.0)
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd == "Z":
                if cur is not None and math.dist(pos, start) > 1e-9:
                    cur.append(start)
                pos = start
                continue
            continue
        need = {"M": 2, "L": 2, "C": 6, "Q": 4}[cmd]
        nums = [float(x) for x in toks[i:i + need]]; i += need
        pts = [(nums[k], nums[k + 1]) for k in range(0, need, 2)]
        if cmd == "M":
            cur = [pts[0]]; out.append(cur); pos = start = pts[0]; cmd = "L"
        elif cmd == "L":
            cur.append(pts[0]); pos = pts[0]
        elif cmd == "C":
            cur += bez3(pos, pts[0], pts[1], pts[2], n)[1:]; pos = pts[2]
        elif cmd == "Q":
            q0, q1, q2 = pos, pts[0], pts[1]
            c1 = (q0[0] + 2 / 3 * (q1[0] - q0[0]), q0[1] + 2 / 3 * (q1[1] - q0[1]))
            c2 = (q2[0] + 2 / 3 * (q1[0] - q2[0]), q2[1] + 2 / 3 * (q1[1] - q2[1]))
            cur += bez3(q0, c1, c2, q2, n)[1:]; pos = q2
    return out


def path_pts(d, n=12):
    """all sub-paths of d joined into one polyline (use for single-subpath outlines)."""
    out = []
    for sp in path_subpaths(d, n):
        out += sp
    return out


def hatch(polys, angle, spacing, inset=0.0, jitter=0.0, seed=3, min_len=3.0, shorten=0.0, fade=0.0):
    """plain parallel hatch strokes (separate segments) clipped to the even-odd region polys.
    shorten: random fraction (0..shorten) trimmed off each end, for a hand-made edge.
    fade: extra trimming for the first and last rows, so the patch dissolves at its ends."""
    import random
    rnd = random.Random(seed)
    if isinstance(polys[0][0], (int, float)):
        polys = [polys]
    a = math.radians(angle)
    ca, sa = math.cos(-a), math.sin(-a)
    R = [[(x * ca - y * sa, x * sa + y * ca) for x, y in p] for p in polys]
    ys = [y for p in R for _, y in p]
    y0, y1 = min(ys), max(ys)
    cb, sb = math.cos(a), math.sin(a)
    segs = []
    y = y0 + spacing * 0.5
    while y < y1:
        rowk = math.sin(math.pi * min(1.0, max(0.0, (y - y0) / max(1e-6, y1 - y0))))
        sh = shorten + fade * (1 - rowk)
        for xa, xb in _scan(R, y):
            xa, xb = xa + inset, xb - inset
            if xb - xa < min_len:
                continue
            L = xb - xa
            xa += rnd.uniform(0, sh) * L; xb -= rnd.uniform(0, sh) * L
            if xb - xa < min_len:
                continue
            yy = y + rnd.uniform(-jitter, jitter)
            segs.append([(xa * cb - yy * sb, xa * sb + yy * cb), (xb * cb - yy * sb, xb * sb + yy * cb)])
        y += spacing
    return segs


def segs_d(segs):
    """many short segments -> one path data string (several sub-paths)."""
    return " ".join(f"M {f1(s[0][0])} {f1(s[0][1])} L {f1(s[-1][0])} {f1(s[-1][1])}" for s in segs)
