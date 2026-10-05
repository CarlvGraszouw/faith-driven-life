"""Reusable figure of Jesus for Episode 1 v2 art (reference design, batch A).

    import os, sys
    sys.path.insert(0, "<ep1>/art-v2/gen")      # this folder (it also puts <ep1> on the path)
    from jesus import jesus, jesus_layers, jesus_anchors, HEIGHT, POSES

    body = jesus(x, y, scale=1.0, pose="teaching", facing="left")   # -> string of <path> elements

API (stable):
  x, y     ground point between his feet (art units, viewBox 1600x900).  For pose "seated" (x, y) is
           still the floor point under his feet; the seat top is at anchors["seat"].
  scale    1.0 = 340 units tall standing (a mid-shot adult).  Seated he is ~0.77 of that.
  pose     "standing"  relaxed, right hand at his side, left hand holding the mantle
           "teaching"  standing, right hand raised forward, open palm (explaining)
           "coin"      standing, right hand held up high showing a denarius between finger and thumb
           "seated"    sitting on a low step/bench (draw the seat yourself), right hand teaching
  facing   "left" (default, canonical: mantle over his LEFT shoulder, nearest the viewer) or "right"
           (mirror image).  Prefer "left"; mirror only when the composition needs it.
  accent   True -> mantle gets the CLOAK accent fill (multiply).  coin_wash -> light BLUE wash on coin.

jesus_layers(...) returns {"line": [...], "detail": [...], "hatch": [...]} lists of <path> strings so
you can interleave with other figures (all lines first, then details, then hatching).
jesus_anchors(...) returns useful points in art coords: head (centre of head), face (eye line,
front), hand_r (right hand), coin (cx, cy, r) for pose "coin", seat (x0, x1, y) for "seated",
bbox (x0, y0, x1, y1) and silhouette (polygon) -- clip background lines you draw AFTER him with
a_sketch.clip(d, [anchors["silhouette"]], keep="out").
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import a_sketch as K  # noqa: E402  (puts ep1 on sys.path)
from lib_v2 import L, D, H, tx, circle, ellipse, CLOAK, BLUE  # noqa: E402

HEIGHT = 340
POSES = ("standing", "teaching", "coin", "seated")
HEAD_S = 0.45          # head-space (100 tall) -> figure units


# =============================================================== part bookkeeping
class Part:
    def __init__(self, name, z, order):
        self.name, self.z, self.order = name, z, order
        self.strokes = []       # (cls, d, fill, accent, clip?)
        self.occ = []           # polygons (figure units) that hide parts with lower z

    def add(self, cls, d, fill=None, accent=False, clip=True):
        if d:
            self.strokes.append((cls, d, fill, accent, clip))
        return self


class Fig:
    def __init__(self):
        self.parts = []

    def part(self, name, z, order):
        p = Part(name, z, order)
        self.parts.append(p)
        return p

    def render(self, s, x, y, mirror):
        """-> dict line/detail/hatch of path strings in art coords."""
        out = {"line": [], "detail": [], "hatch": []}
        for p in sorted(self.parts, key=lambda q: q.order):
            front = [pg for q in self.parts if q.z > p.z for pg in q.occ]
            for cls, d, fill, accent, doclip in p.strokes:
                dd = K.clip(d, front, keep="out") if (front and doclip) else d
                if not dd:
                    continue
                dd = tx(dd, sx=(-s if mirror else s), sy=s, dx=x, dy=y)
                el = {"line": L, "detail": D, "hatch": H}[cls]
                out[cls].append(el(dd) if cls == "hatch" else el(dd, fill=fill, accent=accent))
        return out


def hs(pts, hx, hy, rot=0.0, s=HEAD_S):
    """head-space points -> figure units."""
    return K.xf(pts, s=s, dx=hx, dy=hy, rot=rot)


# =============================================================== head
def head(fig, hx, hy, rot=0.0, z=50, order=0, look=(-1.0, 0.0)):
    """Head facing left in 3/4 view.  Head-space: 100 units tall, origin at the skull centre on the
    eye line (top of skull -48, chin +52).  look = pupil offset direction."""
    P = lambda pts: hs(pts, hx, hy, rot)

    hair_out = [(-31, -27), (-31, -40), (-22, -51), (-6, -56.5), (12, -55), (29, -47), (41, -34),
                (48, -16), (51, 4), (53, 26), (56, 48), (59, 68), (62, 84), (60, 94)]
    hair_tips = [(60, 94), (55, 89), (51, 97), (45, 90), (41, 95)]
    hair_in = [(41, 95), (33, 78), (26, 60), (21, 46), (17, 36)]
    near_frame = [(-18, -43), (-9, -38), (-3, -29), (1, -14), (4, 4), (8, 21)]
    far_frame = [(-18, -43), (-26, -37), (-31, -27)]
    face_far = [(-31, -27), (-34, -20), (-37, -10), (-38.5, -5), (-37.5, 0), (-39.5, 7), (-43, 15),
                (-46.5, 22), (-45.5, 25.5), (-41, 27), (-38, 28.5)]
    beard = [(-38, 28.5), (-41.5, 33), (-42.5, 41), (-40, 50), (-34, 58), (-24, 64), (-12, 66.5),
             (0, 63), (10, 55), (16, 45), (17, 36), (13, 28), (8, 21)]
    neck_front = [(-17, 64), (-16.5, 75), (-16, 86)]

    # occluder polygons: whole head silhouette (hair + face + beard + neck strip)
    head_poly = P(hair_out + hair_tips[1:] + hair_in[1:] + list(reversed(beard))[1:-1]
                  + list(reversed(face_far)))
    ph = fig.part("head", z, order)
    ph.occ.append(head_poly)
    ph.add("line", K.sm(P(hair_out)))
    ph.add("line", K.sm(P(face_far)))
    ph.add("line", K.sm(P(beard)))
    ph.add("line", K.sm(P(hair_tips + hair_in[1:])))
    ph.add("detail", K.sm(P(near_frame)))
    ph.add("detail", K.sm(P(far_frame)))
    ph.add("detail", K.sm(P(neck_front)), clip=False)

    # ---- face details
    lx, ly = look
    feats = []
    feats.append(K.sm(P([(-20, -9), (-13, -12.5), (-5, -12), (1, -8.5)])))            # near brow
    feats.append(K.sm(P([(-37, -9.5), (-32.5, -11.5), (-27.5, -9.5)])))               # far brow
    feats.append(K.sm(P([(-18, 0.5), (-13, -3), (-7, -3), (-2, 0)])))                 # near upper lid
    feats.append(K.sm(P([(-36.5, 0.5), (-33, -2.2), (-29.5, -0.2)])))                 # far upper lid
    feats.append(K.sm(P([(-24.5, -5), (-26, 5), (-30, 15), (-34.5, 21.5), (-36.5, 24.5),
                         (-33.5, 27), (-29.5, 25.5)])))                                # nose side + wing
    feats.append(K.sm(P([(-41, 30.5), (-35, 33.5), (-27, 34.5), (-19, 33), (-13, 37)])))  # moustache
    feats.append(K.sm(P([(-34, 40.5), (-28.5, 42.5), (-22.5, 41)])))                  # lower lip
    for d in feats:
        ph.add("detail", d)
    # pupils (small rings read as dots at this size)
    cx, cy = hs([(-12 + 2.2 * lx, 0.3 + 1.0 * ly)], hx, hy, rot)[0]
    ph.add("detail", circle(cx, cy, 0.75))
    cx, cy = hs([(-33.6 + 1.4 * lx, 0.2 + 0.8 * ly)], hx, hy, rot)[0]
    ph.add("detail", circle(cx, cy, 0.55))

    # ---- hair: parting + flowing strands (dark hair -> denser strokes)
    strands = [
        [(-18, -43), (-8, -51), (6, -54)],                                  # parting
        [(-14, -46), (2, -45), (18, -38), (30, -24), (36, -4), (40, 20)],
        [(-10, -40), (4, -36), (16, -24), (24, -4), (28, 18), (31, 40), (36, 62)],
        [(-4, -33), (8, -22), (14, -4), (18, 16), (22, 34)],
        [(6, -50), (22, -44), (36, -30), (44, -10), (47, 14), (50, 40), (54, 66), (57, 86)],
        [(-24, -42), (-28, -34), (-30, -26)],
    ]
    for i, st in enumerate(strands):
        ph.add("detail" if i < 2 else "hatch", K.sm(P(st)))
    hair_shade = [(14, -30), (30, -40), (44, -22), (49, 10), (52, 40), (56, 70), (58, 88), (50, 86),
                  (40, 66), (32, 40), (26, 14), (22, -8)]
    ph.add("hatch", K.hatch(P(hair_shade), angle=72 + rot, spacing=1.9, shrink=0.3, seed=3))
    ph.add("hatch", K.hatch(P([(30, 10), (50, 20), (55, 60), (58, 86), (46, 84), (38, 50)]),
                            angle=-30 + rot, spacing=2.2, shrink=0.3, seed=4))
    # beard texture + shadow under the jaw
    beard_shade = [(-4, 30), (10, 26), (15, 38), (10, 54), (-4, 62), (-20, 63), (-30, 58), (-18, 52),
                   (-6, 44)]
    ph.add("hatch", K.hatch(P(beard_shade), angle=-62 + rot, spacing=1.7, shrink=0.2, seed=5))
    ph.add("hatch", K.hatch(P([(-40, 34), (-36, 36), (-34, 48), (-26, 58), (-36, 56), (-41, 46)]),
                            angle=-75 + rot, spacing=1.9, shrink=0.2, seed=6))
    # soft shading: near cheek below the cheekbone, eye socket
    ph.add("hatch", K.sm(P([(-4, 9), (-2, 15), (2, 20)])))
    ph.add("hatch", K.sm(P([(-16, 3.2), (-11, 4.6), (-5, 3.6)])))                       # lower lid
    ph.add("hatch", K.sm(P([(-23.5, 30), (-20, 29.5)])))                                # nostril shadow
    return ph


# =============================================================== hands
def hand_open_up(cx, cy, s=1.0, rot=0.0):
    """Open hand, palm up/forward, fingers pointing left-up (teaching).  Returns (outline, details).
    Local: wrist at (0,0), hand extends to the left (~ -20)."""
    o = [(0, -4), (-6, -6.5), (-12, -8.5), (-17, -12), (-20.5, -14.5), (-21.5, -12.8),
         (-18, -9.5), (-21, -9.8), (-22.6, -8), (-19, -5.8), (-21.6, -4.8), (-21.6, -2.8),
         (-17.5, -2.2), (-19, -0.5), (-17.5, 1.2), (-12, 1.5), (-6, 4), (0, 4)]
    fing = [[(-18, -9.5), (-12, -7.5)], [(-19, -5.8), (-12.5, -4.5)], [(-17.5, -2.2), (-12, -1.5)],
            [(-6, -6.5), (-9.5, -3.6), (-12.5, -3.2)]]
    T = lambda pts: K.xf(pts, s=s, dx=cx, dy=cy, rot=rot)
    out = K.sm(T(o))
    det = [K.sm(T(f)) for f in fing]
    return out, det, T(o)


def build(pose):
    """Build the figure in local units (facing left, origin = ground point between the feet)."""
    f = Fig()
    if pose == "seated":
        return build_seated(f)
    hx, hy, hrot = -6.0, -317.0, 0.0
    if pose == "coin":
        hrot = 4.0
    head(f, hx, hy, rot=hrot, z=60, order=0)

    # ---------------------------------------------------------- tunic (cream) body
    tun = f.part("tunic", 10, 2)
    # far shoulder + chest front (left contour) + skirt
    tun.add("line", K.sm([(-13, -281.5), (-24, -281), (-33, -277.5)]))
    tun.add("line", K.chain([(-34, -246), (-36.5, -228), (-36, -210), (-38, -192)],
                            [(-38, -192), (-41, -160), (-43.5, -120), (-45.5, -80), (-47, -40), (-48.5, -14)]))
    tun.add("line", K.sm([(-48.5, -14), (-36, -10.5), (-16, -9), (6, -9.5), (26, -11), (44, -12.5)]))
    tun.add("line", K.sm([(44, -12.5), (44.5, -40), (45, -70), (46.5, -98)]))
    tun.add("detail", K.sm([(-14, -281.5), (-9, -276), (-2, -275.5)]))                 # neckline
    tun.add("detail", K.sm([(-36, -207), (-24, -205), (-14, -206)]))                    # belt top
    tun.add("detail", K.sm([(-37, -200), (-25, -198.5), (-16, -199.5)]))               # belt bottom
    # skirt folds
    for pts in ([(-30, -96), (-31, -60), (-33, -16)], [(-10, -94), (-12, -50), (-11, -12)],
                [(14, -92), (15, -56), (17, -12)], [(32, -90), (33, -50), (33, -13)]):
        tun.add("hatch", K.sm(pts))
    tun.occ.append([(-50, -300), (50, -300), (52, 0), (-52, 0)])

    # ---------------------------------------------------------- mantle (accent) over left shoulder
    man = f.part("mantle", 30, 3)
    mantle_out = [(2, -287), (16, -288.5), (31, -285), (41, -276), (46, -258), (48.5, -230),
                  (50, -195), (51, -160), (51.5, -128), (49, -101)]
    hem = [(49, -101), (40, -96.5), (28, -95), (16, -96), (4, -98), (-10, -100.5), (-24, -103),
           (-36, -106.5), (-43, -109)]
    far_edge = [(-43, -109), (-42, -135), (-40.5, -165), (-38.5, -192), (-37, -205)]
    diag = [(-37, -205), (-27, -214), (-15, -226), (-4, -242), (4, -258), (8, -272), (6, -283), (2, -287)]
    poly = mantle_out + hem[1:] + far_edge[1:] + diag[1:]
    man.occ.append(poly)
    man.add("line", K.chain(mantle_out, hem, far_edge, diag), fill=CLOAK, accent=True)
    # rolled upper edge of the wrap (double line) and the front hanging end
    man.add("detail", K.sm([(-34, -210), (-23, -218), (-11, -231), (-1, -247), (6, -262), (10, -276)]))
    panel = [(12, -282), (10.5, -250), (9.5, -210), (8.5, -170), (8, -130), (6.5, -88)]
    panel_r = [(29, -280), (30.5, -245), (31, -200), (30.5, -150), (29.5, -105), (27, -91)]
    man.add("line", K.sm(panel))
    man.add("line", K.sm([(6.5, -88), (12, -87), (17, -90), (22, -89), (27, -91)]))
    man.add("detail", K.sm(panel_r))
    # folds of the wrap across the body (radiating from the hip toward the shoulder)
    for pts in ([(-34, -180), (-20, -196), (-6, -214), (4, -230)],
                [(-36, -150), (-20, -168), (-6, -186), (5, -200)],
                [(-38, -122), (-22, -134), (-8, -148), (5, -158)],
                [(32, -270), (38, -230), (41, -190), (42, -140), (42, -110)],
                [(14, -250), (15, -200), (16, -150), (15, -100)],
                [(23, -262), (24, -210), (25, -150), (23, -96)]):
        man.add("detail", K.sm(pts))
    # tassels (tzitzit) at the corners: front panel corner and back corner
    for (tx0, ty0, ang) in ((7, -88, 95), (49, -101, 82)):
        a = math.radians(ang)
        ex, ey = tx0 + 13 * math.cos(a), ty0 + 13 * math.sin(a)
        man.add("detail", K.sm([(tx0, ty0), (tx0 + 0.5, ty0 + 3), (tx0, ty0 + 4.5)]))
        for k in (-1.6, 0, 1.6):
            man.add("detail", K.seg((tx0 + k * 0.4, ty0 + 4), (ex + k, ey)))
    # shading: the back drape and under the rolled edge
    man.add("hatch", K.hatch([(36, -270), (46, -256), (49, -200), (50.5, -140), (49, -104), (40, -100),
                              (41, -150), (40, -210), (37, -255)], angle=80, spacing=2.6, seed=7))
    man.add("hatch", K.hatch([(-36, -196), (-24, -206), (-12, -219), (-4, -232), (-6, -222), (-18, -206),
                              (-30, -192)], angle=-30, spacing=2.4, seed=8))
    man.add("hatch", K.hatch([(-42, -112), (-28, -106), (-12, -103), (-14, -110), (-30, -114), (-41, -118)],
                             angle=10, spacing=2.2, seed=9))

    # ---------------------------------------------------------- far (right) arm per pose
    arm = f.part("arm_r", 40 if pose != "standing" else 5, 4)
    if pose == "standing":
        arm.add("line", K.sm([(-33, -277.5), (-39.5, -266), (-42.5, -246), (-44, -225), (-46, -214)]))
        arm.add("line", K.sm([(-46, -214), (-41, -211), (-36, -212)]))                  # sleeve hem
        arm.add("line", K.sm([(-45, -212), (-47.5, -192), (-49.5, -172), (-50, -163)]))
        arm.add("line", K.sm([(-39, -209), (-41.5, -190), (-43, -171), (-43.5, -164)]))
        arm.add("detail", K.sm([(-38, -246), (-39.5, -230)]))                            # sleeve fold
        # relaxed hand hanging (back of hand toward viewer), fingers slightly curled
        hand = [(-50, -163), (-52.5, -154), (-53, -146), (-51.5, -137), (-48.5, -132), (-45.5, -133.5),
                (-44.5, -140), (-42.5, -146), (-41, -153), (-43.5, -164)]
        arm.add("line", K.sm(hand), fill="#ffffff")
        for pts in ([(-50.5, -146), (-48, -139)], [(-47.5, -147), (-46.5, -139.5)], [(-44.5, -150), (-42.5, -145)]):
            arm.add("detail", K.sm(pts))
        arm.add("hatch", K.hatch([(-44, -210), (-41.5, -190), (-43, -168), (-46, -172), (-46, -205)],
                                 angle=75, spacing=2.4, seed=10))
        arm.occ.append([(-46, -215), (-36, -213), (-41, -153), (-44, -133), (-50, -132), (-54, -150), (-50, -168)])
    elif pose == "teaching":
        # upper arm forward-down, forearm rising forward, open palm at chest height
        arm.add("line", K.sm([(-33, -277.5), (-41, -268), (-48, -252), (-55, -236)]))   # top of sleeve
        arm.add("line", K.sm([(-35, -248), (-42, -236), (-48, -226)]))                  # under sleeve
        arm.add("line", K.sm([(-55, -236), (-53, -229), (-48, -226)]))                  # sleeve hem
        arm.add("line", K.sm([(-54, -233), (-62, -244), (-70, -255), (-75, -261)]))     # forearm top
        arm.add("line", K.sm([(-49, -227), (-57, -236), (-66, -247), (-72, -253)]))     # forearm under
        o, det, opts = hand_open_up(-73.5, -257.5, s=1.0, rot=-28)
        arm.add("line", o, fill="#ffffff")
        for d in det:
            arm.add("detail", d)
        arm.add("detail", K.sm([(-39, -262), (-44, -250)]))
        arm.add("hatch", K.hatch([(-35, -248), (-42, -237), (-48, -227), (-44, -240), (-38, -252)],
                                 angle=60, spacing=2.0, seed=11))
        arm.occ.append([(-33, -278), (-55, -237), (-75, -262), (-95, -275), (-95, -245), (-49, -226), (-35, -248)])
    elif pose == "coin":
        arm.add("line", K.sm([(-33, -277.5), (-42, -284), (-52, -294), (-58, -302)]))   # upper arm top
        arm.add("line", K.sm([(-37, -262), (-46, -270), (-54, -282)]))                  # under arm
        arm.add("line", K.sm([(-58, -302), (-61, -295), (-54, -282)]))                  # sleeve hem (elbow)
        arm.add("line", K.sm([(-60, -298), (-63, -314), (-65, -330), (-66, -342)]))     # forearm front
        arm.add("line", K.sm([(-55, -287), (-55.5, -306), (-56, -324), (-57, -338)]))   # forearm back
        # hand: fist-ish holding the coin up between thumb and index finger
        hand = [(-66, -342), (-69, -350), (-68.5, -358), (-65, -362), (-60.5, -361.5), (-57.5, -356),
                (-56, -348), (-57, -338)]
        arm.add("line", K.sm(hand), fill="#ffffff")
        arm.add("detail", K.sm([(-66.5, -351), (-62, -353.5), (-58.5, -350)]))
        arm.add("detail", K.sm([(-65, -357), (-61.5, -358.5)]))
        arm.occ.append([(-33, -278), (-58, -302), (-66, -342), (-70, -360), (-56, -366), (-55, -287), (-37, -262)])
    # ---------------------------------------------------------- near (left) hand holding the mantle
    lh = f.part("hand_l", 45, 5)
    lhand = [(10, -206), (6, -203), (3.5, -197), (4, -190), (7, -186.5), (12.5, -188), (15.5, -193),
             (15.5, -200), (13.5, -205.5), (10, -206)]
    lh.add("line", K.sm(lhand), fill="#ffffff")
    lh.add("detail", K.sm([(5, -195.5), (10, -196), (14.5, -194)]))
    lh.add("detail", K.sm([(6, -190), (11, -190.5)]))
    lh.occ.append(lhand)

    # ---------------------------------------------------------- feet in sandals
    ft = f.part("feet", 20, 6)
    far_foot = [(-38, -12), (-45, -8.5), (-52, -6), (-57, -3.8), (-58, -1.2), (-54, -0.2), (-40, -0.4),
                (-31, -1.2), (-28.5, -4.5)]
    near_foot = [(-6, -10.5), (-13, -6), (-19, -2.5), (-22, 0.6), (-20, 2.8), (-12, 3.2), (6, 2.6),
                 (17, 1.8), (19.5, -2), (16, -8)]
    ft.add("line", K.sm(far_foot))
    ft.add("line", K.sm(near_foot))
    ft.add("detail", K.sm([(-58, 0.6), (-44, 1.6), (-30, 0.8)]))       # soles
    ft.add("detail", K.sm([(-22, 4.4), (-4, 5.2), (19, 3.6)]))
    ft.add("detail", K.sm([(-48, -7.8), (-47, -2.5)]))                  # straps
    ft.add("detail", K.sm([(-36, -10), (-33, -3)]))
    ft.add("detail", K.sm([(-14, -6), (-11, 1.5)]))
    ft.add("detail", K.sm([(4, -9.5), (6, 1)]))
    ft.add("hatch", K.sm([(-57, -2.6), (-55.5, -1.2)]))
    ft.add("hatch", K.sm([(-21, 0.5), (-19.5, 2)]))
    ft.occ.append(far_foot)
    ft.occ.append(near_foot)

    # ground shadow
    sh = f.part("shadow", 0, 9)
    sh.add("hatch", K.cat(K.seg((-66, 6), (-30, 6)), K.seg((-24, 7.5), (30, 7.5)), K.seg((-56, 9), (24, 9.5)),
                          K.seg((-40, 11.5), (10, 11.5))), clip=False)
    return f


def build_seated(f):
    """Seated on a low step (seat top 88 units above the floor), knees toward the left,
    right hand raised in a teaching gesture, left hand resting on the knee."""
    seat_y = -88.0
    hx, hy = -14.0, -235.0
    head(f, hx, hy, rot=-4.0, z=60, order=0)
    # torso leaning slightly forward
    tun = f.part("tunic", 10, 2)
    tun.add("line", K.sm([(-20, -199.5), (-30, -199), (-39, -195)]))                    # far shoulder
    tun.add("line", K.chain([(-40, -168), (-42.5, -150), (-41, -134)]))                 # chest front
    tun.add("detail", K.sm([(-22, -199.5), (-17, -194), (-10, -193.5)]))                # neckline
    # lower legs (tunic falls from the knees to the ankles)
    tun.add("line", K.sm([(-88, -96), (-90, -70), (-90.5, -40), (-91, -14)]))           # front of shins
    tun.add("line", K.sm([(-91, -14), (-80, -11), (-66, -11.5), (-56, -13)]))           # hem
    tun.add("line", K.sm([(-56, -13), (-57, -40), (-58, -66), (-60, -86)]))             # back of calves
    tun.add("hatch", K.sm([(-76, -88), (-77, -50), (-76, -14)]))
    tun.add("hatch", K.sm([(-66, -84), (-67, -46), (-66, -14)]))
    tun.occ.append([(-95, -210), (40, -210), (40, 0), (-95, 0)])

    man = f.part("mantle", 30, 3)
    # mantle over left shoulder, round the back, across the lap and over the knees
    mantle_out = [(-6, -205), (8, -206), (22, -202), (31, -193), (35, -176), (36, -150), (36, -125),
                  (34, -100), (30, -84)]
    lap_hem = [(30, -84), (10, -84), (-12, -86), (-36, -88), (-60, -89), (-80, -91), (-91, -95)]
    knee_front = [(-91, -95), (-93, -104), (-90, -113), (-80, -118)]
    lap_top = [(-80, -118), (-64, -120), (-50, -121), (-42, -124), (-40, -132)]
    diag = [(-40, -132), (-31, -143), (-21, -158), (-11, -175), (-5, -190), (-3, -201), (-6, -205)]
    poly = mantle_out + lap_hem[1:] + knee_front[1:] + lap_top[1:] + diag[1:]
    man.occ.append(poly)
    man.add("line", K.chain(mantle_out, lap_hem, knee_front, lap_top, diag), fill=CLOAK, accent=True)
    man.add("detail", K.sm([(-37, -137), (-27, -149), (-17, -165), (-9, -181), (-4, -195)]))
    panel = [(4, -201), (2, -170), (0, -140), (-2, -122)]
    man.add("line", K.sm(panel))
    man.add("detail", K.sm([(20, -199), (22, -170), (22, -140), (20, -118)]))
    for pts in ([(-86, -100), (-70, -104), (-54, -106), (-36, -104)],
                [(-84, -110), (-70, -112), (-56, -113)],
                [(-30, -96), (-14, -100), (2, -102), (18, -100)],
                [(26, -190), (30, -160), (31, -125), (28, -96)],
                [(10, -186), (11, -150), (9, -120)]):
        man.add("detail", K.sm(pts))
    man.add("hatch", K.hatch([(27, -192), (34, -176), (35.5, -140), (34, -104), (30, -88), (26, -96),
                              (28, -130), (28, -170)], angle=78, spacing=2.6, seed=12))
    man.add("hatch", K.hatch([(-90, -96), (-62, -92), (-36, -91), (-12, -89), (-14, -94), (-40, -97),
                              (-66, -97), (-88, -101)], angle=8, spacing=2.0, seed=13))
    for (tx0, ty0, ang) in ((-91, -95, 100), (30, -84, 85)):
        a = math.radians(ang)
        ex, ey = tx0 + 12 * math.cos(a), ty0 + 12 * math.sin(a)
        man.add("detail", K.sm([(tx0, ty0), (tx0 + 0.5, ty0 + 3), (tx0, ty0 + 4.5)]))
        for k in (-1.6, 0, 1.6):
            man.add("detail", K.seg((tx0 + k * 0.4, ty0 + 4), (ex + k, ey)))

    # right arm: teaching gesture, hand raised in front of the chest toward the left
    arm = f.part("arm_r", 40, 4)
    arm.add("line", K.sm([(-39, -195), (-46, -186), (-52, -172), (-58, -158)]))
    arm.add("line", K.sm([(-41, -166), (-46, -158), (-51, -150)]))
    arm.add("line", K.sm([(-58, -158), (-56, -152), (-51, -150)]))
    arm.add("line", K.sm([(-57, -155), (-66, -166), (-74, -177), (-79, -183)]))
    arm.add("line", K.sm([(-52, -151), (-61, -159), (-70, -170), (-76, -175)]))
    o, det, opts = hand_open_up(-77.5, -180, s=1.0, rot=-30)
    arm.add("line", o, fill="#ffffff")
    for d in det:
        arm.add("detail", d)
    arm.occ.append([(-39, -196), (-58, -159), (-79, -184), (-100, -198), (-100, -168), (-51, -149), (-41, -166)])

    # left hand resting on the knee
    lh = f.part("hand_l", 45, 5)
    lhand = [(-52, -122), (-58, -124), (-66, -123.5), (-72, -121.5), (-74, -118.5), (-71, -116.5),
             (-64, -116.5), (-57, -116), (-51.5, -117)]
    lh.add("line", K.sm(lhand), fill="#ffffff")
    lh.add("detail", K.sm([(-66, -121.5), (-59, -120.5)]))
    lh.add("detail", K.sm([(-68, -118.5), (-61, -118.6)]))
    lh.occ.append(lhand)

    ft = f.part("feet", 20, 6)
    far_foot = [(-80, -12), (-88, -8.5), (-96, -5.5), (-101, -3.5), (-102, -1), (-96, 0), (-84, 0), (-75, -1),
                (-72, -5)]
    near_foot = [(-62, -12), (-70, -7), (-78, -2.5), (-82, 0.8), (-79, 3), (-68, 3.2), (-56, 2.6), (-50, 1),
                 (-50.5, -6)]
    ft.add("line", K.sm(far_foot))
    ft.add("line", K.sm(near_foot))
    ft.add("detail", K.sm([(-102, 0.8), (-88, 1.6), (-74, 0.8)]))
    ft.add("detail", K.sm([(-82, 4.4), (-66, 5), (-50, 3.4)]))
    ft.add("detail", K.sm([(-92, -6.5), (-91, -1.5)]))
    ft.add("detail", K.sm([(-72, -6), (-70, 1.5)]))
    ft.occ.append(far_foot)
    ft.occ.append(near_foot)
    return f


_ANCH_LOCAL = {
    "standing": dict(head=(-6, -317), face=(-22, -317), hand_r=(-48, -150)),
    "teaching": dict(head=(-6, -317), face=(-22, -317), hand_r=(-86, -265)),
    "coin": dict(head=(-6, -317), face=(-22, -317), hand_r=(-63, -352), coin=(-66.5, -366, 6.5)),
    "seated": dict(head=(-14, -235), face=(-30, -235), hand_r=(-88, -188), seat=(-50, 40, -88)),
}
_SIL = {
    "standing": [(-31, -342), (6, -345), (22, -330), (30, -300), (50, -278), (54, -200), (53, -100), (46, -60),
                 (46, -12), (22, 4), (-22, 5), (-60, 2), (-50, -14), (-48, -40), (-46, -110), (-52, -132),
                 (-54, -160), (-47, -230), (-38, -275), (-26, -300), (-28, -330)],
    "seated": [(-38, -258), (0, -262), (18, -246), (38, -196), (40, -100), (32, -82), (-50, -86), (-54, 0),
               (-104, 2), (-92, -14), (-94, -100), (-98, -170), (-100, -198), (-78, -190), (-48, -200),
               (-36, -245)],
}
_SIL["teaching"] = _SIL["standing"][:16] + [(-58, -236), (-98, -276), (-94, -250), (-50, -226),
                                            (-38, -275), (-26, -300), (-28, -330)]
_SIL["coin"] = _SIL["standing"][:16] + [(-50, -230), (-56, -290), (-72, -372), (-55, -372), (-26, -300),
                                        (-28, -330)]


def _place(pts, x, y, s, mirror):
    return [((-px if mirror else px) * s + x, py * s + y) for px, py in pts]


def jesus_anchors(x, y, scale=1.0, pose="standing", facing="left"):
    mirror = facing == "right"
    a = {}
    for k, v in _ANCH_LOCAL[pose].items():
        if k == "coin":
            (cx, cy), = _place([v[:2]], x, y, scale, mirror)
            a[k] = (cx, cy, v[2] * scale)
        elif k == "seat":
            x0, x1 = sorted(((-v[0] if mirror else v[0]) * scale + x, (-v[1] if mirror else v[1]) * scale + x))
            a[k] = (x0, x1, v[2] * scale + y)
        else:
            a[k] = _place([v], x, y, scale, mirror)[0]
    sil = _place(_SIL[pose], x, y, scale, mirror)
    a["silhouette"] = sil
    xs = [p[0] for p in sil]; ys = [p[1] for p in sil]
    a["bbox"] = (min(xs), min(ys), max(xs), max(ys))
    return a


def jesus_layers(x, y, scale=1.0, pose="standing", facing="left", accent=True, coin_wash=False):
    if pose not in POSES:
        raise ValueError(f"pose must be one of {POSES}")
    f = build(pose)
    if not accent:
        for p in f.parts:
            p.strokes = [(c, d, (None if fl == CLOAK else fl), (False if fl == CLOAK else ac), cl)
                         for (c, d, fl, ac, cl) in p.strokes]
    out = f.render(scale, x, y, facing == "right")
    if pose == "coin":
        cx, cy, r = jesus_anchors(x, y, scale, pose, facing)["coin"]
        out["line"].append(L(circle(cx, cy, r), fill=(BLUE if coin_wash else "#ffffff"), accent=coin_wash))
        out["detail"].append(D(circle(cx, cy, r * 0.72)))
        # tiny profile head on the coin
        hd = K.sm([(cx + 0.18 * r, cy - 0.45 * r), (cx - 0.25 * r, cy - 0.3 * r), (cx - 0.3 * r, cy + 0.05 * r),
                   (cx - 0.1 * r, cy + 0.3 * r), (cx + 0.25 * r, cy + 0.35 * r)])
        out["hatch"].append(H(hd))
    return out


def jesus(x, y, scale=1.0, pose="standing", facing="left", accent=True, coin_wash=False):
    lay = jesus_layers(x, y, scale, pose, facing, accent, coin_wash)
    return "".join(lay["line"] + lay["detail"] + lay["hatch"])


if __name__ == "__main__":
    # contact sheet of all poses -> preview/jesus-sheet.svg
    from lib_v2 import svg
    body = ""
    for i, pose in enumerate(POSES):
        body += jesus(220 + i * 380, 760, 1.6 if pose != "seated" else 1.6, pose)
    out = os.path.join(os.path.dirname(os.path.dirname(HERE)), "preview", "jesus-sheet.svg")
    open(out, "w").write(svg(body, "jesus.py contact sheet"))
    print("wrote", out)
