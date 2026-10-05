"""Procedural hands for close-ups (a07). Anatomy in a hand frame: u runs from the wrist crease
toward the middle fingertip (1.0 = hand length), v runs across the palm (v>0 = thumb side).
`HandFrame.P(u, v)` maps to the board with a rotation and a foreshortening of v (palm tilt).

Fingers are built from joint chains (base -> PIP -> DIP -> tip) with widths; the whole hand
silhouette is returned as ONE continuous outline (wrist -> pinky side -> round every finger ->
thumb -> wrist) so the pen draws it in one go. Creases, nails and knuckles are separate details.
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from inkgeom import cr_dense, resample, lerp, bez3  # noqa: E402


def _n(x, y):
    L = math.hypot(x, y) or 1.0
    return (x / L, y / L)


class HandFrame:
    def __init__(self, wrist, direction, length, thumb_side, fv=0.8):
        self.W = wrist
        self.U = _n(*direction)
        self.V = _n(*thumb_side)
        self.L = length
        self.fv = fv

    def P(self, u, v):
        L = self.L
        return (self.W[0] + L * (u * self.U[0] + self.fv * v * self.V[0]),
                self.W[1] + L * (u * self.U[1] + self.fv * v * self.V[1]))

    def Ps(self, pts):
        return [self.P(u, v) for u, v in pts]


class Finger:
    """joint chain in (u, v): base centre, direction (deg from +u, + toward the thumb), segment lengths,
    widths at base/PIP/DIP and tip, and a bend (deg per joint, + toward the thumb side)."""

    def __init__(self, base, ang, segs, widths, bend=0.0, tip_round=0.55, waist=0.045):
        self.waist = waist
        self.joints = [base]
        a = math.radians(ang)
        p = base
        for i, s in enumerate(segs):
            p = (p[0] + s * math.cos(a), p[1] + s * math.sin(a))
            self.joints.append(p)
            a += math.radians(bend)
        self.widths = widths
        self.tip_round = tip_round

    def centre(self):
        return cr_dense(self.joints, 8)

    def sides(self, k=10):
        """left (v-) and right (v+) edges from base to tip, with gentle bulges between joints."""
        J, Wd = self.joints, self.widths
        lft, rgt = [], []
        n = len(J)
        for i in range(n - 1):
            a, b = J[i], J[i + 1]
            d = _n(b[0] - a[0], b[1] - a[1])
            nv = (-d[1], d[0])                       # toward +v when d ~ +u
            for j in range(k):
                t = j / k
                w = (Wd[i] + (Wd[i + 1] - Wd[i]) * t) * 0.5
                w *= 1.0 - self.waist * math.cos(2 * math.pi * t)   # waist at the creases, pad between
                c = lerp(a, b, t)
                lft.append((c[0] - nv[0] * w, c[1] - nv[1] * w))
                rgt.append((c[0] + nv[0] * w, c[1] + nv[1] * w))
        return lft, rgt

    def tip_cap(self, n=9):
        J = self.joints
        a, b = J[-2], J[-1]
        d = _n(b[0] - a[0], b[1] - a[1])
        nv = (-d[1], d[0])
        w = self.widths[-1] * 0.5
        c = (b[0] - d[0] * w * (1 - self.tip_round), b[1] - d[1] * w * (1 - self.tip_round))
        out = []
        for i in range(n + 1):
            t = math.pi * i / n
            # from the left edge (v-) round the tip to the right edge (v+)
            out.append((c[0] - nv[0] * w * math.cos(t) + d[0] * w * math.sin(t) * 1.05,
                        c[1] - nv[1] * w * math.cos(t) + d[1] * w * math.sin(t) * 1.05))
        return out

    def at(self, i, t, side=0.0):
        """point on segment i at fraction t, offset across by side * half width"""
        J, Wd = self.joints, self.widths
        a, b = J[i], J[i + 1]
        d = _n(b[0] - a[0], b[1] - a[1])
        nv = (-d[1], d[0])
        w = (Wd[i] + (Wd[i + 1] - Wd[i]) * t) * 0.5
        c = lerp(a, b, t)
        return (c[0] + nv[0] * w * side, c[1] + nv[1] * w * side)

    def crease(self, i, t=0.0, curve=0.25, frac=0.8):
        """flexion crease across the finger at joint i (palm side): a shallow arc"""
        p0 = self.at(i, t, -frac); p1 = self.at(i, t, frac)
        J = self.joints
        a, b = J[i], J[min(i + 1, len(J) - 1)]
        d = _n(b[0] - a[0], b[1] - a[1])
        w = self.widths[i] * 0.5
        m = ((p0[0] + p1[0]) / 2 + d[0] * w * curve, (p0[1] + p1[1]) / 2 + d[1] * w * curve)
        return cr_dense([p0, m, p1], 5)


def outline_chain(fingers, start, end, webs):
    """silhouette through a list of fingers ordered from the v- side to the v+ side:
    start -> up finger[0] outer edge -> tip -> down its inner edge -> web[0] -> next finger ... -> end"""
    pts = [start]
    for k, f in enumerate(fingers):
        lft, rgt = f.sides()
        cap = f.tip_cap()
        pts += lft[1:] + cap + list(reversed(rgt))[1:]
        if k < len(webs):
            pts.append(webs[k])
    pts.append(end)
    return pts


# ---------------------------------------------------------------- natural fingers (palm or back view)
def finger_edges(base, tip, w0, w1, bow=0.0, joints=(0.44, 0.72), pad=0.075, notch=0.05, n=36):
    """edges of a finger from base centre to tip centre (local coords).
    Returns (edge_a, cap, edge_b): edge_a runs base->tip on the LEFT of the axis (as seen walking
    base->tip in image coords, y down), the cap rounds the tip, edge_b runs tip->base on the right.
    bow bends the axis sideways (fraction of length); pads bulge between the joints, notches pinch at them."""
    bx, by = base; tx_, ty_ = tip
    dx, dy = tx_ - bx, ty_ - by
    Ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / Ln, dy / Ln
    nx, ny = uy, -ux                                  # left normal (image coords)
    def axis(t):
        b = bow * Ln * 4 * t * (1 - t)
        return (bx + dx * t + nx * b, by + dy * t + ny * b)
    def width(t):
        w = (w0 + (w1 - w0) * t) * 0.5
        # pads: bulge mid-phalanx, pinch at the creases
        marks = [0.0] + list(joints) + [1.0]
        for a, b in zip(marks, marks[1:]):
            if a <= t <= b:
                s = (t - a) / (b - a)
                w *= 1 + pad * math.sin(math.pi * s) - notch * (math.exp(-((s) / 0.12) ** 2) if a > 0 else 0)
        return w
    tend = 1 - (w1 * 0.5) / Ln * 0.9
    ts = [tend * i / n for i in range(n + 1)]
    A, B = [], []
    for t in ts:
        c = axis(t)
        c2 = axis(min(1, t + 0.01)); c1 = axis(max(0, t - 0.01))
        ax_, ay_ = c2[0] - c1[0], c2[1] - c1[1]
        al = math.hypot(ax_, ay_) or 1
        lx, ly = ay_ / al, -ax_ / al
        w = width(t)
        A.append((c[0] + lx * w, c[1] + ly * w))
        B.append((c[0] - lx * w, c[1] - ly * w))
    # elongated tip cap from the end of edge A round to the end of edge B
    c = axis(tend)
    w = width(tend)
    cap = []
    for i in range(1, 12):
        th = math.pi * i / 12
        cap.append((c[0] + nx * w * math.cos(th) + ux * w * 1.15 * math.sin(th),
                    c[1] + ny * w * math.cos(th) + uy * w * 1.15 * math.sin(th)))
    return A, cap, list(reversed(B))


def web(p, q, depth=4.0, toward=(1, 0)):
    """U-shaped web between the end of one finger edge (p) and the start of the next (q)."""
    m = ((p[0] + q[0]) / 2 + toward[0] * depth, (p[1] + q[1]) / 2 + toward[1] * depth)
    return cr_dense([p, m, q], 5)[1:-1]


def crease_across(base, tip, t, w, curve=0.2, frac=0.85):
    """short flexion crease across a finger at fraction t of its length"""
    bx, by = base; tx_, ty_ = tip
    dx, dy = tx_ - bx, ty_ - by
    Ln = math.hypot(dx, dy) or 1
    ux, uy = dx / Ln, dy / Ln
    nx, ny = uy, -ux
    c = (bx + dx * t, by + dy * t)
    h = w * 0.5 * frac
    p0 = (c[0] + nx * h, c[1] + ny * h); p1 = (c[0] - nx * h, c[1] - ny * h)
    m = (c[0] + ux * w * curve * 0.5, c[1] + uy * w * curve * 0.5)
    return cr_dense([p0, m, p1], 4)
