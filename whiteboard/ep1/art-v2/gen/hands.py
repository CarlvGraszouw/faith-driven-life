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

    def __init__(self, base, ang, segs, widths, bend=0.0, tip_round=0.55):
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
                w *= 1.0 + 0.06 * math.sin(math.pi * t)      # pad bulge between creases
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
