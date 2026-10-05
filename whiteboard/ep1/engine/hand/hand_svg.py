"""Drawing hand for the whiteboard engine: a right hand holding a whiteboard marker, as a shaded SVG.

    python3 hand_svg.py              -> hand.svg + hand.json (tip = the marker nib, in image px)
    node render_png.js hand.svg hand.png

Classic whiteboard-animation pose, seen from the thumb side: the index finger arches along the top of
the barrel, the thumb presses from below/in front, the other fingers curl into the fist, and the
marker's back end pokes out above the back of the hand. Geometry is in centimetres in a marker frame
(u = along the marker from the nib towards its back end, v = across it, + = below the marker in the
picture) and mapped to image pixels. The nib is the top-left-most point; the forearm runs off to the
lower right far enough that it never ends inside a 1080p frame.
"""
import json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
K = 29.5                  # image px per cm (drawn at scale ~0.78 -> ~23 px/cm on a 1080p screen)
MARKER_ANG = 38.0         # marker axis, degrees below horizontal (nib at the upper left)
ARM_LEN = 40.0            # visible forearm length beyond the wrist (cm)
MARGIN = 4                # px around the drawing
DEBUG = False             # flat colours + joint markers

a = math.radians(MARKER_ANG)
MU = (math.cos(a), math.sin(a))        # +u in the image (towards the marker's back end)
MV = (-MU[1], MU[0])                   # +v in the image (below the marker: down-left)


def P(u, v):
    return (K * (u * MU[0] + v * MV[0]), K * (u * MU[1] + v * MV[1]))


def f(x):
    return f"{x:.1f}"


def catmull(pts, closed=False, t=0.5):
    p = list(pts)
    p = [p[-1]] + p + [p[0], p[1]] if closed else [p[0]] + p + [p[-1]]
    d = f"M{f(p[1][0])} {f(p[1][1])}"
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d += f" C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}"
    return d + (" Z" if closed else "")


def path(cm_pts, closed=True):
    return catmull([P(*q) for q in cm_pts], closed)


def poly(cm_pts):
    return 'M' + ' L'.join(f"{f(P(*q)[0])} {f(P(*q)[1])}" for q in cm_pts) + ' Z'


def finger(joints, widths, tip_round=0.62, base_extra=0.8):
    """Closed outline (cm) of a finger along joints[0] (base) .. joints[-1] (tip centre); widths per joint.
    Returns dict(outline, left, right, axis) - left/right are the two side contours from base to tip."""
    n = len(joints)
    nrm = []
    for i in range(n):
        a0, a1 = joints[max(0, i - 1)], joints[min(n - 1, i + 1)]
        tx, ty = a1[0] - a0[0], a1[1] - a0[1]
        L = math.hypot(tx, ty) or 1
        nrm.append((-ty / L, tx / L))
    left, right, axis = [], [], []
    for i in range(n):
        x, y = joints[i]
        w = widths[i] / 2
        left.append((x + nrm[i][0] * w, y + nrm[i][1] * w))
        right.append((x - nrm[i][0] * w, y - nrm[i][1] * w))
        axis.append((x, y))
        if i < n - 1:
            x2, y2 = joints[i + 1]
            mx, my = (x + x2) / 2, (y + y2) / 2
            wm = (widths[i] + widths[i + 1]) / 4 * 0.95          # shafts slimmer than the knuckles
            nx, ny = nrm[i][0] + nrm[i + 1][0], nrm[i][1] + nrm[i + 1][1]
            Ln = math.hypot(nx, ny) or 1
            left.append((mx + nx / Ln * wm, my + ny / Ln * wm))
            right.append((mx - nx / Ln * wm, my - ny / Ln * wm))
            axis.append((mx, my))
    tx, ty = joints[-1][0] - joints[-2][0], joints[-1][1] - joints[-2][1]
    L = math.hypot(tx, ty)
    ux, uy = tx / L, ty / L
    nx, ny = nrm[-1]
    w = widths[-1] / 2
    cx, cy = joints[-1]
    cap = [(cx + ux * w * tip_round * 1.9 * math.sin(math.pi * k / 6) + nx * w * math.cos(math.pi * k / 6),
            cy + uy * w * tip_round * 1.9 * math.sin(math.pi * k / 6) + ny * w * math.cos(math.pi * k / 6)) for k in range(1, 6)]
    bx, by = joints[1][0] - joints[0][0], joints[1][1] - joints[0][1]
    Lb = math.hypot(bx, by)
    bl = (left[0][0] - bx / Lb * base_extra, left[0][1] - by / Lb * base_extra)
    br = (right[0][0] - bx / Lb * base_extra, right[0][1] - by / Lb * base_extra)
    return {'outline': [bl] + left + cap + list(reversed(right)) + [br], 'left': [bl] + left, 'right': [br] + right,
            'axis': axis, 'tip': (cx + ux * w * tip_round * 1.9, cy + uy * w * tip_round * 1.9)}


# ------------------------------------------------------------------ anatomy (cm, marker frame)
MARKER_LEN = 13.4
MR = 0.88                                    # barrel radius
INDEX = finger([(10.05, -1.5), (6.9, -2.62), (4.7, -1.98), (3.05, -1.38)], [2.1, 1.82, 1.6, 1.42], base_extra=0.35)
THUMB = finger([(12.2, 3.6), (9.2, 3.12), (6.6, 2.2), (4.35, 1.52)], [2.75, 2.3, 2.02, 1.78], base_extra=0.35)
MID_TIP = finger([(6.2, 2.75), (4.65, 1.85), (3.5, 1.28)], [1.62, 1.5, 1.38], tip_round=0.7, base_extra=0.3)
PALM_TOP = [(9.2, -2.55), (10.2, -2.72), (11.2, -2.35), (12.1, -1.25), (13.2, -0.05), (14.6, 0.95), (16.4, 1.75), (18.4, 2.45)]
PALM_WRIST = [(17.4, 4.6)]
PALM_BOT = [(15.9, 6.55), (13.9, 6.95), (11.6, 6.8), (9.9, 6.45),                      # heel of the palm
            (8.3, 5.85), (7.05, 5.0), (6.1, 4.0), (5.7, 3.05)]                          # curled fingers (fist front)
PALM_WEB = [(6.6, 1.7), (8.0, 0.4), (8.95, -1.1)]                                       # web under the marker
PALM = PALM_TOP + PALM_WRIST + PALM_BOT + PALM_WEB     # back of hand + palm + fist (behind marker, index, thumb)
FIST = [  # curled middle / ring / little finger (middle phalanges), from the thumb downwards
    [(7.9, 2.35), (6.55, 2.95), (5.95, 3.9), (6.45, 4.75), (7.5, 4.85), (8.35, 4.0)],
    [(9.0, 3.65), (7.75, 4.35), (7.35, 5.2), (8.05, 5.95), (9.15, 5.95), (9.75, 4.95)],
    [(10.35, 4.75), (9.2, 5.5), (9.1, 6.3), (9.95, 6.8), (11.05, 6.65), (11.35, 5.65)],
]
WRIST_TOP, WRIST_BOT = (18.4, 2.45), (15.9, 6.55)
_wx, _wy = WRIST_TOP[0] - WRIST_BOT[0], WRIST_TOP[1] - WRIST_BOT[1]
_wl = math.hypot(_wx, _wy)
H = (-_wy / _wl, _wx / _wl) if (-_wy / _wl) > 0 else (_wy / _wl, -_wx / _wl)   # forearm direction (away from the hand)
_N = (-H[1], H[0])                                                               # across the forearm, towards its top
if _N[1] > 0:
    _N = (-_N[0], -_N[1])
WC = ((WRIST_TOP[0] + WRIST_BOT[0]) / 2, (WRIST_TOP[1] + WRIST_BOT[1]) / 2)


def arm_pt(t, side, half):
    return (WC[0] + H[0] * t + _N[0] * half * side, WC[1] + H[1] * t + _N[1] * half * side)


ARM_HALF = [(-2.4, _wl / 2 * 0.9), (-0.6, _wl / 2 * 0.98), (3.0, 2.55), (8.0, 2.95), (14.0, 3.35), (22.0, 3.55), (ARM_LEN, 3.6)]
ARM_TOP = [arm_pt(t, 1, h) for t, h in ARM_HALF]
ARM_BOT = [arm_pt(t, -1, h * (1.07 if 4 < t < 20 else 1.0)) for t, h in ARM_HALF]

# ------------------------------------------------------------------ colours
SKIN, SKIN_HI, SKIN_SH, SKIN_DEEP, OUT = '#efc6a8', '#fbe2cf', '#c98f71', '#9e6149', '#8f5b45'
NAIL, NAIL_HI = '#f2cdc3', '#fff3ee'

# ------------------------------------------------------------------ svg helpers
defs, body = [], []
_id = [0]


def nid(p):
    _id[0] += 1
    return f'{p}{_id[0]}'


_blur = {}


def blur(px):
    px = round(px, 1)
    if px not in _blur:
        _blur[px] = f'bl{len(_blur)}'
        defs.append(f'<filter id="{_blur[px]}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{px}"/></filter>')
    return f'url(#{_blur[px]})'


def clip(d):
    i = nid('cp')
    defs.append(f'<clipPath id="{i}"><path d="{d}"/></clipPath>')
    return f'url(#{i})'


def stroke(d, color, w, op=1.0, bl=0, extra=''):
    fl = f' filter="{blur(bl)}"' if bl else ''
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w:.1f}" stroke-opacity="{op}" stroke-linecap="round" stroke-linejoin="round"{fl}{extra}/>'


def fill(d, color, op=1.0, bl=0):
    fl = f' filter="{blur(bl)}"' if bl else ''
    return f'<path d="{d}" fill="{color}" fill-opacity="{op}"{fl}/>'


def offset_line(pts, k):
    """shift a cm polyline sideways by k cm (left normal)."""
    out = []
    for i, (x, y) in enumerate(pts):
        a0, a1 = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        tx, ty = a1[0] - a0[0], a1[1] - a0[1]
        L = math.hypot(tx, ty) or 1
        out.append((x - ty / L * k, y + tx / L * k))
    return out


def img_y(pts):
    return sum(P(*q)[1] for q in pts) / len(pts)


def base_fade(F, length=1.3):
    """mask that fades the finger out over its first `length` cm, so its base melts into the palm."""
    b0 = ((F['left'][0][0] + F['right'][0][0]) / 2, (F['left'][0][1] + F['right'][0][1]) / 2)
    ax = F['axis']
    dx, dy = ax[1][0] - ax[0][0], ax[1][1] - ax[0][1]
    L = math.hypot(dx, dy)
    b1 = (b0[0] + dx / L * length, b0[1] + dy / L * length)
    g, m = nid('fg'), nid('fm')
    p0, p1 = P(*b0), P(*b1)
    defs.append(f'<linearGradient id="{g}" gradientUnits="userSpaceOnUse" x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}">'
                '<stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>')
    defs.append(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="-3000" y="-3000" width="8000" height="8000">'
                f'<rect x="-3000" y="-3000" width="8000" height="8000" fill="url(#{g})"/></mask>')
    return f'url(#{m})'


def outline_from(F, j):
    """closed outline of the finger from axis point j to the tip (j counts joints+midpoints)."""
    return F['left'][1 + j:] + F['outline'][len(F['left']):len(F['left']) + 5] + list(reversed(F['right'][1 + j:]))


def warm(pt, r, op=0.22):
    """reddish flush (knuckles, fingertips)."""
    x, y = pt
    return fill(path([(x - r, y), (x, y - r), (x + r, y), (x, y + r)]), '#e48f7e', op, r * K * 0.5)


def shade_finger(F, width_cm, cp, nail=None, creases=(), tints=()):
    """airbrushed cylinder shading for a finger dict from finger(); light from the upper left."""
    up, lo = (F['left'], F['right']) if img_y(F['left']) < img_y(F['right']) else (F['right'], F['left'])
    W = width_cm * K
    g = [f'<g clip-path="{cp}">', fill(path(F['outline']), SKIN)]
    g.append(stroke(path(lo, False), SKIN_SH, W * 0.95, 0.75, W * 0.28))           # form shadow, lower side
    g.append(stroke(path(lo, False), SKIN_DEEP, W * 0.28, 0.45, W * 0.1))          # core shadow at the edge
    g.append(stroke(path(up, False), SKIN_SH, W * 0.32, 0.35, W * 0.12))           # turning edge on top
    sgn = 1 if F['left'] is up else -1
    hl = offset_line(F['axis'], -sgn * width_cm * 0.17)
    g.append(stroke(path(hl[1:], False), SKIN_HI, W * 0.2, 0.85, W * 0.09))        # highlight
    for pt, r in tints:
        g.append(warm(pt, r))
    for c in creases:
        g.append(c)
    if nail:
        g.append(nail)
    g.append('</g>')
    return g


def nail_shape(F, s_back, side_off, length, width, ang_bias=0.0):
    """nail on the finger's distal phalanx: centred s_back cm behind the tip along the axis, side_off across."""
    ax = F['axis']
    tip = F['tip']
    bx, by = ax[-1][0] - ax[-2][0], ax[-1][1] - ax[-2][1]
    L = math.hypot(bx, by)
    ux, uy = bx / L, by / L
    nx, ny = -uy, ux
    cx, cy = tip[0] - ux * s_back + nx * side_off, tip[1] - uy * s_back + ny * side_off
    pts = []
    for k in range(16):
        th = 2 * math.pi * k / 16
        x, y = length / 2 * math.cos(th), width / 2 * math.sin(th)
        if x > 0:
            x *= 1.12                                  # free edge a little longer and squarer
        pts.append((cx + ux * x + nx * y, cy + uy * x + ny * y))
    d = path(pts)
    hl = [(cx + ux * (length * 0.1) + nx * width * 0.12, cy + uy * (length * 0.1) + ny * width * 0.12),
          (cx + ux * (length * 0.42) + nx * width * 0.05, cy + uy * (length * 0.42) + ny * width * 0.05)]
    return ''.join([fill(d, NAIL), stroke(d, '#b57f6c', 1.3, 0.75),
                    stroke(path(hl, False), NAIL_HI, length * K * 0.14, 0.9, 1.6),
                    stroke(path([(cx - ux * length * 0.45 + nx * width * 0.42, cy - uy * length * 0.45 + ny * width * 0.42),
                                 (cx - ux * length * 0.5, cy - uy * length * 0.5),
                                 (cx - ux * length * 0.45 - nx * width * 0.42, cy - uy * length * 0.45 - ny * width * 0.42)], False),
                           '#c78f7b', 1.4, 0.6, 0.8)])


def crease_across(F, j, k_len=0.5, n=2, op=0.55, gap=0.12):
    """short wrinkle strokes across the finger at axis point j (on the upper/dorsal half)."""
    ax = F['axis']
    x, y = ax[j]
    a0, a1 = ax[max(0, j - 1)], ax[min(len(ax) - 1, j + 1)]
    tx, ty = a1[0] - a0[0], a1[1] - a0[1]
    L = math.hypot(tx, ty)
    ux, uy = tx / L, ty / L
    nx, ny = -uy, ux
    up = -1 if P(x + nx, y + ny)[1] > P(x - nx, y - ny)[1] else 1    # pick the normal that points up in the image
    out = []
    for i in range(n):
        o = (i - (n - 1) / 2) * gap
        c = [(x + ux * o + up * nx * 0.1, y + uy * o + up * ny * 0.1),
             (x + ux * (o + 0.04) + up * nx * k_len * 0.55, y + uy * (o + 0.04) + up * ny * k_len * 0.55),
             (x + ux * o + up * nx * k_len, y + uy * o + up * ny * k_len)]
        out.append(stroke(path(c, False), SKIN_DEEP, 1.5, op, 0.5))
    return ''.join(out)


def build():
    # ---- hand + forearm as ONE silhouette (no seam at the wrist), shaded as one form
    arm_t = [(t, h) for t, h in ARM_HALF if t >= 2.5]
    body_top = PALM_TOP + [arm_pt(t, 1, h) for t, h in arm_t]                       # index knuckle -> back of hand -> arm
    arm_bot = [arm_pt(t, -1, h * (1.07 if 4 < t < 20 else 1.0)) for t, h in arm_t]
    lower = list(reversed(PALM_BOT[:4])) + arm_bot                                   # fist bottom -> palm heel -> arm underside
    outline = body_top + list(reversed(arm_bot)) + PALM_BOT + PALM_WEB
    cpb = clip(path(outline))
    W = 6.5 * K
    body.append(f'<g clip-path="{cpb}">')
    body.append(fill(path(outline), SKIN))
    body.append(stroke(path(lower, False), SKIN_SH, W * 0.6, 0.78, W * 0.17))          # underside falls into shadow
    body.append(stroke(path(lower, False), SKIN_DEEP, W * 0.12, 0.38, W * 0.05))
    body.append(stroke(path(body_top, False), SKIN_SH, W * 0.12, 0.32, W * 0.05))      # turning edge on top
    hi = PALM_TOP[2:] + [arm_pt(t, 1, h - 1.2) for t, h in arm_t]
    body.append(stroke(path(offset_line(hi, 0.0)[1:], False), SKIN_HI, W * 0.13, 0.85, W * 0.055))   # lit back of hand + arm
    body.append(fill(path([(10.6, -1.3), (11.6, -0.6), (11.2, 0.2), (10.2, -0.4)]), SKIN_HI, 0.8, 5))  # index knuckle sheen
    body.append(fill(path([(11.0, 0.4), (13.2, 1.0), (13.6, 2.0), (11.6, 1.8)]), SKIN_HI, 0.45, 9))   # web muscle bulge
    body.append(fill(path([(9.6, 2.0), (12.6, 2.2), (14.6, 3.4), (14.0, 5.4), (11.4, 5.6), (9.4, 4.2)]), SKIN_SH, 0.45, 14))  # thenar
    # wrist: a soft fold on the palm side and a faint crease
    wb = arm_pt(0.4, -1, _wl / 2 * 0.95)
    body.append(fill(path([arm_pt(-0.6, -1, 2.4), wb, arm_pt(1.4, -1, 2.6), arm_pt(0.6, 0, 0)]), SKIN_SH, 0.35, 10))
    body.append(stroke(path([arm_pt(0.3, -1, 2.2), arm_pt(0.45, -1, 1.5), arm_pt(0.5, -1, 0.9)], False), SKIN_DEEP, 1.4, 0.35, 0.8))
    body.append('</g>')
    body.append(stroke(path(body_top, False), OUT, 1.6, 0.72))
    body.append(stroke(path(lower, False), OUT, 1.7, 0.8))

    # ---- curled fingers
    for i, fz in reversed(list(enumerate(FIST))):
        c = clip(path(fz))
        cx = sum(q[0] for q in fz) / len(fz)
        cy = sum(q[1] for q in fz) / len(fz)
        body.append(f'<g clip-path="{c}">')
        body.append(fill(path(fz), SKIN))
        body.append(stroke(path(fz[2:6] + [fz[0]], False), SKIN_SH, 0.75 * K, 0.7, 0.25 * K))
        body.append(fill(path([(cx - 0.55, cy - 0.45), (cx + 0.05, cy - 0.6), (cx - 0.05, cy - 0.15), (cx - 0.6, cy - 0.05)]), SKIN_HI, 0.9, 7))
        body.append(warm((cx - 0.75, cy - 0.1), 0.55, 0.2))
        body.append('</g>')
        body.append(stroke(path(fz[0:5], False), OUT, 1.5, 0.7))
        body.append(stroke(path([fz[1], ((fz[1][0] + fz[0][0]) / 2 + 0.2, (fz[1][1] + fz[0][1]) / 2 + 0.25)], False), SKIN_DEEP, 1.4, 0.5, 0.6))

    # ---- middle fingertip under the marker
    c = clip(path(MID_TIP['outline']))
    body.append(f'<g mask="{base_fade(MID_TIP, 1.0)}">')
    body.extend(shade_finger(MID_TIP, 1.5, c, creases=[crease_across(MID_TIP, 2, 0.45, 2, 0.35)], tints=[(MID_TIP['axis'][-1], 0.5)]))
    body.append(stroke(path(MID_TIP['outline'][1:-1], False), OUT, 1.5, 0.8))
    body.append('</g>')

    # ---- marker shadow on the hand
    skin_cp = clip(path(PALM))
    shadow = path([(9.0, -MR), (MARKER_LEN, -MR), (MARKER_LEN, MR), (9.0, MR)])
    body.append(f'<g clip-path="{skin_cp}"><g transform="translate(9 13)">{fill(shadow, SKIN_DEEP, 0.38, 6)}</g></g>')

    # ---- marker
    g0, g1 = P(0, -MR), P(0, MR)
    defs.append(f'<linearGradient id="mkBody" gradientUnits="userSpaceOnUse" x1="{g0[0]:.1f}" y1="{g0[1]:.1f}" x2="{g1[0]:.1f}" y2="{g1[1]:.1f}">'
                '<stop offset="0" stop-color="#16171a"/><stop offset="0.16" stop-color="#4b4e55"/><stop offset="0.3" stop-color="#7b7f87"/>'
                '<stop offset="0.42" stop-color="#3a3c42"/><stop offset="0.78" stop-color="#1c1d21"/><stop offset="0.93" stop-color="#2e3036"/>'
                '<stop offset="1" stop-color="#121316"/></linearGradient>')
    defs.append(f'<linearGradient id="mkCap" gradientUnits="userSpaceOnUse" x1="{g0[0]:.1f}" y1="{g0[1]:.1f}" x2="{g1[0]:.1f}" y2="{g1[1]:.1f}">'
                '<stop offset="0" stop-color="#0e0f11"/><stop offset="0.25" stop-color="#3d3f45"/><stop offset="0.38" stop-color="#5d6068"/>'
                '<stop offset="0.55" stop-color="#202125"/><stop offset="1" stop-color="#0b0b0d"/></linearGradient>')
    n0, n1 = P(0, -0.3), P(0, 0.3)
    defs.append(f'<linearGradient id="mkNib" gradientUnits="userSpaceOnUse" x1="{n0[0]:.1f}" y1="{n0[1]:.1f}" x2="{n1[0]:.1f}" y2="{n1[1]:.1f}">'
                '<stop offset="0" stop-color="#2a2a2c"/><stop offset="0.35" stop-color="#5a5a5e"/><stop offset="1" stop-color="#1a1a1c"/></linearGradient>')
    barrel = poly([(2.45, -MR), (MARKER_LEN - 0.55, -MR), (MARKER_LEN - 0.55, MR), (2.45, MR)])
    body.append(fill(barrel, 'url(#mkBody)'))
    for u0, u1 in ((5.4, 5.55), (11.6, 11.75)):                       # moulding rings
        body.append(fill(poly([(u0, -MR), (u1, -MR), (u1, MR), (u0, MR)]), '#0c0c0e', 0.55))
    body.append(fill(path([(MARKER_LEN - 0.6, -MR * 1.03), (MARKER_LEN - 0.12, -MR * 0.97), (MARKER_LEN, -0.32), (MARKER_LEN, 0.32),
                           (MARKER_LEN - 0.12, MR * 0.97), (MARKER_LEN - 0.6, MR * 1.03)]), 'url(#mkCap)'))
    body.append(fill(poly([(2.12, -MR * 0.95), (2.5, -MR * 0.95), (2.5, MR * 0.95), (2.12, MR * 0.95)]), 'url(#mkCap)'))
    body.append(fill(path([(0.78, -0.31), (1.5, -0.6), (2.16, -MR * 0.9), (2.16, MR * 0.9), (1.5, 0.6), (0.78, 0.31)]), 'url(#mkCap)'))
    body.append(fill(path([(0.0, 0.0), (0.12, -0.17), (0.45, -0.27), (0.86, -0.3), (0.86, 0.3), (0.45, 0.27), (0.12, 0.17)]), 'url(#mkNib)'))
    body.append(stroke(path([(0.16, -0.12), (0.5, -0.2), (0.82, -0.22)], False), '#8a8a8e', 1.3, 0.6, 0.5))   # felt sheen
    body.append(stroke(path([(1.0, -0.33), (1.6, -0.55), (2.1, -0.72)], False), '#9a9ca3', 1.6, 0.5, 0.8))  # cone sheen
    body.append(stroke(poly([(0.0, 0.0), (0.12, -0.17), (0.45, -0.27), (0.86, -0.3), (2.16, -MR * 0.9), (2.5, -MR * 0.95),
                             (MARKER_LEN - 0.6, -MR * 1.03), (MARKER_LEN, -0.32), (MARKER_LEN, 0.32), (MARKER_LEN - 0.6, MR * 1.03),
                             (2.5, MR * 0.95), (2.16, MR * 0.9), (0.86, 0.3), (0.45, 0.27), (0.12, 0.17)]), '#050506', 1.2, 0.6))

    # ---- index finger (on top of the barrel) with its shadow on the marker and the hand
    ip = path(INDEX['outline'])
    body.append(f'<g transform="translate(7 10)">{fill(path(outline_from(INDEX, 2)), "#000", 0.26, 6)}</g>')
    c = clip(ip)
    nail = nail_shape(INDEX, 0.62, -0.32, 1.18, 0.62)
    body.append(f'<g mask="{base_fade(INDEX, 1.1)}">')
    body.extend(shade_finger(INDEX, 1.8, c, nail=nail, creases=[crease_across(INDEX, 2, 0.55, 3, 0.45), crease_across(INDEX, 4, 0.45, 2, 0.4)],
                             tints=[(INDEX['axis'][2], 0.6), (INDEX['axis'][4], 0.45), (INDEX['axis'][6], 0.5)]))
    body.append(stroke(path(INDEX['outline'][1:-1], False), OUT, 1.6, 0.85))
    body.append('</g>')

    # ---- thumb (nearest to us), shadow on the marker and the fist
    tp = path(THUMB['outline'])
    body.append(f'<g transform="translate(6 11)">{fill(path(outline_from(THUMB, 3)), "#000", 0.24, 7)}</g>')
    c = clip(tp)
    nail = nail_shape(THUMB, 0.78, 0.18, 1.35, 0.95)
    body.append(f'<g mask="{base_fade(THUMB, 2.2)}">')
    body.extend(shade_finger(THUMB, 2.1, c, nail=nail, creases=[crease_across(THUMB, 4, 0.6, 3, 0.4)],
                             tints=[(THUMB['axis'][4], 0.6), (THUMB['axis'][6], 0.55)]))
    body.append(stroke(path(THUMB['outline'][1:-1], False), OUT, 1.7, 0.85))
    body.append('</g>')


def svg():
    defs.clear(); body.clear(); _blur.clear()
    build()
    text = '\n'.join(body)
    nums = [float(v) for v in re.findall(r'(?<=[MLC ])(-?\d+\.?\d*)', ' '.join(re.findall(r' d="([^"]+)"', text)))]
    xs, ys = nums[0::2], nums[1::2]
    pad = 26                                                  # room for blur/shadow
    x0, y0 = min(xs + [0]), min(ys + [0])
    tipx, tipy = -x0 + MARGIN, -y0 + MARGIN
    w, h = max(xs) - x0 + MARGIN + pad, max(ys) - y0 + MARGIN + pad
    e0, e1 = P(*arm_pt(ARM_LEN - 7.0, 0, 0)), P(*arm_pt(ARM_LEN - 0.5, 0, 0))
    defs.append(f'<linearGradient id="armEnd" gradientUnits="userSpaceOnUse" x1="{e0[0]:.1f}" y1="{e0[1]:.1f}" x2="{e1[0]:.1f}" y2="{e1[1]:.1f}">'
                '<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
                '<mask id="armEndMask" maskUnits="userSpaceOnUse" x="-3000" y="-3000" width="8000" height="8000">'
                '<rect x="-3000" y="-3000" width="8000" height="8000" fill="url(#armEnd)"/></mask>')
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}">\n<defs>\n'
           + '\n'.join(defs) + f'\n</defs>\n<g transform="translate({tipx:.1f} {tipy:.1f})"><g mask="url(#armEndMask)">\n{text}\n</g></g>\n</svg>\n')
    return out, (tipx, tipy), (w, h)


if __name__ == '__main__':
    text, tip, size = svg()
    open(os.path.join(HERE, 'hand.svg'), 'w').write(text)
    meta = {'image': 'hand.png', 'tip': [round(tip[0], 2), round(tip[1], 2)], 'scale': 0.78, 'angle': 0,
            '_comment': 'tip = marker nib in hand.png px (made by hand_svg.py + render_png.js); scale 0.78 -> ~23 px/cm on a 1080p frame'}
    json.dump(meta, open(os.path.join(HERE, 'hand.json'), 'w'), indent=1)
    print('hand.svg', f'{size[0]:.0f}x{size[1]:.0f}', 'tip', meta['tip'], '-> hand.json')
