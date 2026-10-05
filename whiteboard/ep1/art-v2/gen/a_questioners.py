"""The questioners (a04) and their exit (a11): Pharisees and Herodians, rig-built.
Designed FACING LEFT (local units, 340 = standing height); a04 mirrors them to face Jesus on the right.
Pharisees: older, long full beards, ankle-length robes with long sleeves, broad mantles (tallit) with long
tassels, head-cloth wound like a turban, phylactery box on the brow (and strap on the arm).
Herodians: Greco-Roman courtiers: cropped curly hair, trimmed beard, knee-length belted tunic, fine cloak
pinned at the right shoulder with a round brooch, rings, laced sandals."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import a_sketch as K
from a_rig import Dressed, circ, capsule, hull, robe_standing, torso, wavy_hem, place_head, smooth_ring, ext
from jesus import Fig, rig_hand, foot, tassel, WHITE
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union


def ang(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def add_dressed(fig, D, name="body", z=30, order=1, folds=(), hatch_polys=(), hem=None, lv_out="S"):
    out, inner, occ, u = D.strokes()
    p = fig.part(name, z, order)
    p.add("line", out, lv_out, clip=False)
    for d, lv in inner:
        p.add("detail", d, lv)
    for d, lv in folds:
        p.add("detail", d, lv)
    for poly, angle, sp, seed in hatch_polys:
        p.add("hatch", K.clip(K.hatch(poly, angle=angle, spacing=sp, seed=seed), [list(ext(u).coords)], keep="in"), "S")
    p.occ.append(occ)
    return p, u


# =============================================================== Q1: lead Pharisee, leaning in, asking
def pharisee_mantle(D, J, z=30, front_len=-70, back_len=-52):
    """broad mantle (tallit) over both shoulders: back drape to the calves, both ends hanging in front like
    stoles to below the knee.  -> tassel points"""
    nx, ny = J["neck"]
    shf, shn = J["shf"], J["shn"]
    back = Polygon([(nx + 4, ny - 6), (shn[0] + 10, shn[1] - 6), (shn[0] + 24, shn[1] + 30), (shn[0] + 28, -200),
                    (shn[0] + 30, -130), (shn[0] + 30, back_len), (shn[0] + 14, back_len + 6), (shn[0] + 2, -140),
                    (shn[0] - 2, -220), (shn[0] - 6, shn[1] + 18)])
    near_end = Polygon([(shn[0] - 10, shn[1] + 2), (shn[0] + 4, shn[1] + 6), (shn[0] + 8, -200), (shn[0] + 10, -130),
                        (shn[0] + 10, front_len), (shn[0] - 10, front_len - 6), (shn[0] - 12, -140), (shn[0] - 14, -220)])
    far_end = Polygon([(shf[0] + 10, shf[1] - 6), (shf[0] - 4, shf[1] + 8), (shf[0] - 2, -210), (shf[0] + 4, -140),
                       (shf[0] + 8, front_len + 8), (shf[0] + 26, front_len + 2), (shf[0] + 24, -150), (shf[0] + 22, -230),
                       (nx - 4, ny + 8)])
    D.add(z, back.buffer(1.5), "mantle_back", "S")
    D.add(z + 2, far_end.buffer(1.5), "mantle_far", "S")
    D.add(z + 4, near_end.buffer(1.5), "mantle_near", "S")
    return [(shn[0] + 0, front_len - 3), (shf[0] + 17, front_len + 5), (shn[0] + 24, back_len + 3)]


def pharisee_asking(expr="smile", level_hint="full"):
    J = dict(head=(-36, -318), neck=(-22, -287), shf=(-54, -276), shn=(14, -279), waist=(-4, -208),
             hipf=(-12, -172), hipn=(14, -174), knf=(-30, -96), knn=(12, -94),
             anf=(-38, -10), ann=(16, -9), tof=(-64, -2), ton=(-8, -1),
             elf=(-72, -224), wrf=(-98, -238), eln=(18, -228), wrn=(-12, -246))
    f = Fig()
    place_head(f, J, rot=-12, s=0.47, beard="long", cover="turban", expr=expr, gaze=-1.0, phylactery=True,
               nose_kind="hooked", age=1, z=80, order=0)
    D = Dressed()
    D.add(10, unary_union([capsule(J["shf"], J["elf"], 10, 10.5), capsule(J["elf"], J["wrf"], 10.5, 8.6)]), "farm", "S")
    skirt, (hl, hr, hy) = robe_standing(J, flare=13)
    D.add(20, unary_union([torso(J, chest=19, waist=16), skirt, circ(J["neck"], 9)]), "robe", None)
    tps = pharisee_mantle(D, J)
    D.add(40, unary_union([capsule(J["shn"], J["eln"], 10.5, 10.5), capsule(J["eln"], J["wrn"], 10.5, 8.6)]), "narm", "S")
    folds = []
    for x0, lv in ((-30, "M"), (-14, "F"), (-1, "M")):
        folds.append((K.sm([(x0, -150), (x0 - 2, -100), (x0 - 3, -50), (x0 - 2, hy - 4)]), lv))
    folds.append((K.sm([(J["elf"][0] + 4, J["elf"][1] - 8), (J["elf"][0] - 12, J["elf"][1] + 2)]), "F"))
    folds.append((K.sm([(J["shn"][0] + 16, -250), (J["shn"][0] + 20, -170), (J["shn"][0] + 22, -80)]), "F"))
    hp = [(Polygon([(hl, hy), (hl + 30, hy), (hl + 26, -120), (hl + 10, -150)]), 76, 2.6, 401),
          (Polygon([(J["shn"][0] + 16, -250), (J["shn"][0] + 34, -250), (J["shn"][0] + 34, -50), (J["shn"][0] + 16, -50)]), 82, 2.4, 402),
          (Polygon([(J["knn"][0] + 6, -64), (hr, -64), (hr, hy), (J["knn"][0] + 6, hy)]), 80, 2.6, 403)]
    hp = [(list(pg.exterior.coords), a, s_, sd) for pg, a, s_, sd in hp]
    body, u = add_dressed(f, D, folds=folds, hatch_polys=hp)
    for i, (tx_, ty_) in enumerate(tps):
        tassel(body, tx_, ty_, ang=92, length=18, lv="M" if i < 2 else "F")
    hd = f.part("hands", 90, 3)
    rig_hand(hd, "open", J["wrf"][0] - 1, J["wrf"][1], rot=ang(J["elf"], J["wrf"]) + 90 + 6, s=1.05)
    rig_hand(hd, "knee", J["wrn"][0] + 2, J["wrn"][1], rot=ang(J["eln"], J["wrn"]) - 180 + 8, s=1.05)
    ft = f.part("feet", 5, 4)
    foot(ft, J["anf"][0], J["anf"][1], J["tof"])
    foot(ft, J["ann"][0], J["ann"][1], J["ton"])
    return f, J


# =============================================================== Q2: Herodian courtier, arms folded, sly
def leg_bare(a_knee, a_ankle, front=-1):
    """calf with a muscle bulge on the back side (front=-1: the shin faces -x)."""
    kx, ky = a_knee; ax, ay = a_ankle
    mid = K.lerp(a_knee, a_ankle, 0.38)
    back = (mid[0] - front * 4.6, mid[1])
    return unary_union([capsule(a_knee, a_ankle, 7.6, 4.6), circ(back, 6.6), capsule(a_knee, back, 7.4, 6.2)]).convex_hull


def herodian_folded(expr="sly"):
    J = dict(head=(-14, -319), neck=(-8, -288), shf=(-42, -277), shn=(28, -277), waist=(-6, -206),
             hipf=(-18, -170), hipn=(12, -168), knf=(-18, -96), knn=(16, -94),
             anf=(-22, -11), ann=(18, -10), tof=(-48, -3), ton=(-6, -1),
             elf=(-50, -226), wrf=(14, -232), eln=(38, -224), wrn=(-34, -244))
    f = Fig()
    place_head(f, J, rot=5, s=0.46, beard="short", cover="curly", expr=expr, gaze=-1.0, z=80, order=0)
    D = Dressed()
    cloak = Polygon([(J["shf"][0] + 4, J["shf"][1] - 8), (J["neck"][0] + 10, J["neck"][1] - 4), (J["shn"][0] + 12, J["shn"][1] - 2),
                     (J["shn"][0] + 22, -230), (J["shn"][0] + 26, -150), (J["shn"][0] + 28, -64), (J["shn"][0] + 10, -52),
                     (J["shn"][0] - 2, -70), (J["shn"][0] - 2, -200)])
    D.add(5, cloak.buffer(1.5), "cloak", "S")
    D.add(8, unary_union([leg_bare(J["knf"], J["anf"]), leg_bare(J["knn"], J["ann"])]), "legs", "S")
    tun_skirt = hull(circ(((J["hipf"][0] + J["hipn"][0]) / 2, -170), 20), circ(J["knf"], 12), circ(J["knn"], 12),
                     Polygon([(J["knf"][0] - 17, -78), (J["knn"][0] + 15, -78), (J["knn"][0] + 15, -76), (J["knf"][0] - 17, -76)]))
    D.add(20, unary_union([torso(J, chest=19, waist=17), tun_skirt, circ(J["neck"], 8.6)]), "tunic", None)
    # folded arms: upper arms down to the elbows at the sides, forearms crossed (near one on top)
    D.add(30, unary_union([capsule(J["shf"], J["elf"], 9.8, 9.2), capsule(J["elf"], J["wrf"], 7.2, 6)]), "farm", "S")
    D.add(34, unary_union([capsule(J["shn"], J["eln"], 10, 9.4), capsule(J["eln"], J["wrn"], 7.4, 6.2)]), "narm", "S")
    folds = [(K.sm([(-28, -204), (-6, -201.6), (22, -204)]), "S"),                      # belt
             (K.sm([(-28, -197), (-6, -194.6), (22, -197)]), "M"),
             (K.sm([(J["knf"][0] - 15, -84), (0, -82.6), (J["knn"][0] + 13, -84)]), "M"),   # hem border
             (K.sm([(-26, -188), (-30, -140), (-31, -88)]), "M"), (K.sm([(4, -190), (6, -140), (6, -88)]), "F"),
             (K.sm([(-30, -262), (-22, -250), (-14, -246)]), "F")]
    hp = [(Polygon([(J["shn"][0] + 4, -230), (J["shn"][0] + 28, -230), (J["shn"][0] + 28, -60), (J["shn"][0] + 4, -60)]), 82, 2.4, 411),
          (Polygon([(-36, -190), (-24, -190), (-26, -82), (-38, -82)]), 80, 2.6, 412),
          (Polygon([(J["knn"][0] - 1, -76), (J["knn"][0] + 10, -76), (J["ann"][0] + 6, -16), (J["ann"][0] - 1, -16)]), 76, 2.2, 413),
          (Polygon([(-40, -236), (36, -232), (36, -226), (-40, -228)]), 6, 1.8, 414)]
    hp = [(list(pg.exterior.coords), a, s_, sd) for pg, a, s_, sd in hp]
    body, u = add_dressed(f, D, folds=folds, hatch_polys=hp)
    bx, by = J["shf"][0] + 8, J["shf"][1] - 2
    from lib_v2 import circle as _c
    body.add("detail", _c(bx, by, 4.4), "S")
    body.add("detail", _c(bx, by, 1.8), "M")
    hd = f.part("hands", 90, 3)
    rig_hand(hd, "knee", J["wrn"][0] + 1, J["wrn"][1] + 1, rot=ang(J["eln"], J["wrn"]) - 180 + 4, s=0.98)
    hd.add("detail", K.sm([(J["wrn"][0] - 10, J["wrn"][1] - 6), (J["wrn"][0] - 11, J["wrn"][1] + 1)]), "M")   # ring
    ft = f.part("feet", 6, 4)
    for a_, t_ in ((J["anf"], J["tof"]), (J["ann"], J["ton"])):
        foot(ft, a_[0], a_[1], t_)
        ft.add("detail", K.sm([(a_[0] - 5.4, a_[1] - 24), (a_[0] + 5, a_[1] - 17)]) + " "
               + K.sm([(a_[0] - 5.4, a_[1] - 14), (a_[0] + 5, a_[1] - 7)]), "M")
    return f, J


# =============================================================== Q3: old Pharisee, hand to his beard, skeptical
def pharisee_old(expr="frown"):
    J = dict(head=(-26, -306), neck=(-14, -276), shf=(-44, -265), shn=(24, -268), waist=(-4, -200),
             hipf=(-14, -166), hipn=(12, -165), knf=(-18, -92), knn=(14, -90),
             anf=(-22, -10), ann=(16, -9), tof=(-48, -2), ton=(-8, -1),
             elf=(-60, -220), wrf=(-44, -262), eln=(30, -212), wrn=(26, -164))
    f = Fig()
    place_head(f, J, rot=-6, s=0.46, beard="long", cover="turban", expr=expr, gaze=-1.0, phylactery=True, age=2,
               beard_dark=False, z=80, order=0)
    D = Dressed()
    skirt, (hl, hr, hy) = robe_standing(J, flare=12)
    D.add(20, unary_union([torso(J, chest=19, waist=17), skirt, circ(J["neck"], 9)]), "robe", None)
    tps = pharisee_mantle(D, J, front_len=-64, back_len=-48)
    D.add(40, unary_union([capsule(J["shf"], J["elf"], 10, 10.4), capsule(J["elf"], J["wrf"], 10.4, 8.4)]), "farm", "S")
    D.add(44, unary_union([capsule(J["shn"], J["eln"], 10, 10.2), capsule(J["eln"], J["wrn"], 10.2, 8.2)]), "narm", "S")
    folds = [(K.sm([(x0, -150), (x0 - 1, -100), (x0 - 2, -50), (x0 - 1, hy - 4)]), lv) for x0, lv in ((-28, "M"), (-12, "F"), (2, "M"))]
    hp = [(Polygon([(hl, hy), (hl + 28, hy), (hl + 24, -120), (hl + 8, -150)]), 76, 2.6, 421),
          (Polygon([(J["shn"][0] + 14, -240), (J["shn"][0] + 32, -240), (J["shn"][0] + 32, -50), (J["shn"][0] + 14, -50)]), 82, 2.4, 422)]
    hp = [(list(pg.exterior.coords), a, s_, sd) for pg, a, s_, sd in hp]
    body, u = add_dressed(f, D, folds=folds, hatch_polys=hp)
    for i, (tx_, ty_) in enumerate(tps):
        tassel(body, tx_, ty_, ang=92, length=18, lv="M" if i < 2 else "F")
    hd = f.part("hands", 90, 3)
    rig_hand(hd, "grip", J["wrf"][0], J["wrf"][1], rot=ang(J["elf"], J["wrf"]) - 180 + 20, s=1.0)
    rig_hand(hd, "relaxed", J["wrn"][0], J["wrn"][1], rot=ang(J["eln"], J["wrn"]) - 90, s=1.0)
    ft = f.part("feet", 5, 4)
    foot(ft, J["anf"][0], J["anf"][1], J["tof"])
    foot(ft, J["ann"][0], J["ann"][1], J["ton"])
    return f, J


# =============================================================== a11: walking away, amazed
def head_turned(f, J, rot, **opts):
    """head facing RIGHT (turned back over the shoulder) on a left-facing body: drawn mirrored about the head."""
    from a_people import head34
    hf = Fig()
    head34(hf, 0, 0, rot=rot, **opts)
    hp = hf.parts[0]
    hx, hy = J["head"]
    ph = f.part("head", hp.z, hp.order)
    from lib_v2 import tx as _tx
    for st in hp.strokes:
        ph.strokes.append(dict(st, d=_tx(st["d"], sx=-1, sy=1, dx=hx, dy=hy)))
    ph.occ = [[(-px + hx, py + hy) for px, py in pg] for pg in hp.occ]
    return ph


def pharisee_walk_back(expr="stunned"):
    """lead Pharisee walking away to the LEFT, glancing back over his shoulder, stunned; one hand lifted."""
    J = dict(head=(-6, -317), neck=(-12, -287), shf=(-44, -276), shn=(22, -279), waist=(-4, -207),
             hipf=(-14, -172), hipn=(12, -171), knf=(-34, -96), knn=(16, -92),
             anf=(-46, -10), ann=(30, -18), tof=(-72, -3), ton=(10, -1),
             elf=(-60, -224), wrf=(-66, -262), eln=(34, -222), wrn=(46, -176))
    f = Fig()
    head_turned(f, J, rot=6, s=0.47, beard="long", cover="turban", expr=expr, gaze=-1.0, phylactery=True,
                nose_kind="hooked", age=1, z=80, order=0)
    D = Dressed()
    D.add(10, unary_union([capsule(J["shf"], J["elf"], 10, 10.4), capsule(J["elf"], J["wrf"], 10.4, 8.4)]), "farm", "S")
    skirt, (hl, hr, hy) = robe_standing(J, flare=12)
    D.add(20, unary_union([torso(J, chest=19, waist=16), skirt, circ(J["neck"], 9)]), "robe", None)
    tps = pharisee_mantle(D, J, front_len=-72, back_len=-50)
    D.add(40, unary_union([capsule(J["shn"], J["eln"], 10.4, 10.2), capsule(J["eln"], J["wrn"], 10.2, 8.4)]), "narm", "S")
    folds = [(K.sm([(-30, -150), (-36, -100), (-42, -50), (-44, hy - 4)]), "M"), (K.sm([(-2, -150), (6, -100), (16, hy - 6)]), "F")]
    hp = [(Polygon([(J["shn"][0] + 14, -240), (J["shn"][0] + 32, -240), (J["shn"][0] + 32, -50), (J["shn"][0] + 14, -50)]), 82, 2.4, 431),
          (Polygon([(J["knn"][0] + 2, -80), (hr, -80), (hr, hy), (J["knn"][0] + 2, hy)]), 78, 2.4, 432)]
    hp = [(list(pg.exterior.coords), a, s_, sd) for pg, a, s_, sd in hp]
    body, u = add_dressed(f, D, folds=folds, hatch_polys=hp)
    for i, (tx_, ty_) in enumerate(tps):
        tassel(body, tx_, ty_, ang=96, length=18, lv="M" if i < 2 else "F")
    hd = f.part("hands", 90, 3)
    rig_hand(hd, "open", J["wrf"][0], J["wrf"][1], rot=ang(J["elf"], J["wrf"]) + 90 + 10, s=1.05)
    rig_hand(hd, "relaxed", J["wrn"][0], J["wrn"][1], rot=ang(J["eln"], J["wrn"]) - 90, s=1.0)
    ft = f.part("feet", 5, 4)
    foot(ft, J["anf"][0], J["anf"][1], J["tof"])
    foot(ft, J["ann"][0], J["ann"][1], J["ton"])
    return f, J


def herodian_walk(expr="stunned"):
    """Herodian walking away to the LEFT, hand pressed to his brow in disbelief."""
    J = dict(head=(-18, -316), neck=(-10, -287), shf=(-42, -277), shn=(26, -278), waist=(-4, -206),
             hipf=(-16, -170), hipn=(12, -169), knf=(-34, -98), knn=(18, -92),
             anf=(-44, -11), ann=(34, -20), tof=(-70, -3), ton=(14, -1),
             elf=(-54, -222), wrf=(-52, -176), eln=(12, -270), wrn=(-20, -330))
    f = Fig()
    place_head(f, J, rot=-10, s=0.46, beard="short", cover="curly", expr=expr, gaze=-1.0, z=80, order=0)
    D = Dressed()
    cloak = Polygon([(J["shf"][0] + 4, J["shf"][1] - 8), (J["neck"][0] + 10, J["neck"][1] - 4), (J["shn"][0] + 12, J["shn"][1] - 2),
                     (J["shn"][0] + 26, -230), (J["shn"][0] + 34, -150), (J["shn"][0] + 40, -66), (J["shn"][0] + 20, -54),
                     (J["shn"][0] + 4, -76), (J["shn"][0], -200)])
    D.add(5, cloak.buffer(1.5), "cloak", "S")
    D.add(8, unary_union([leg_bare(J["knf"], J["anf"]), leg_bare(J["knn"], J["ann"])]), "legs", "S")
    tun_skirt = hull(circ(((J["hipf"][0] + J["hipn"][0]) / 2, -170), 20), circ(J["knf"], 12), circ(J["knn"], 12),
                     Polygon([(J["knf"][0] - 14, -80), (J["knn"][0] + 14, -78), (J["knn"][0] + 14, -76), (J["knf"][0] - 14, -78)]))
    D.add(20, unary_union([torso(J, chest=19, waist=17), tun_skirt, circ(J["neck"], 8.6)]), "tunic", None)
    D.add(30, unary_union([capsule(J["shf"], J["elf"], 9.6, 9), capsule(J["elf"], J["wrf"], 7, 5.8)]), "farm", "S")
    D.add(34, unary_union([capsule(J["shn"], J["eln"], 9.8, 9.2), capsule(J["eln"], J["wrn"], 7.2, 6)]), "narm", "S")
    folds = [(K.sm([(-30, -204), (-6, -201.6), (22, -204)]), "S"),
             (K.sm([(J["knf"][0] - 12, -86), (-6, -84), (J["knn"][0] + 12, -84)]), "M")]
    hp = [(Polygon([(J["shn"][0] + 6, -230), (J["shn"][0] + 34, -230), (J["shn"][0] + 40, -62), (J["shn"][0] + 8, -60)]), 80, 2.4, 441),
          (Polygon([(J["knn"][0] - 1, -76), (J["knn"][0] + 12, -76), (J["ann"][0] + 6, -24), (J["ann"][0] - 2, -24)]), 70, 2.2, 442)]
    hp = [(list(pg.exterior.coords), a, s_, sd) for pg, a, s_, sd in hp]
    body, u = add_dressed(f, D, folds=folds, hatch_polys=hp)
    hd = f.part("hands", 90, 3)
    rig_hand(hd, "knee", J["wrn"][0] + 2, J["wrn"][1] + 1, rot=ang(J["eln"], J["wrn"]) - 180 + 34, s=1.0)
    rig_hand(hd, "relaxed", J["wrf"][0], J["wrf"][1], rot=ang(J["elf"], J["wrf"]) - 90, s=0.98)
    ft = f.part("feet", 6, 4)
    for a_, t_ in ((J["anf"], J["tof"]), (J["ann"], J["ton"])):
        foot(ft, a_[0], a_[1], t_)
    return f, J


def pharisee_old_walk(expr="frown"):
    """old Pharisee walking away to the LEFT, hand to his beard, shaking his head."""
    J = dict(head=(-30, -304), neck=(-18, -274), shf=(-48, -263), shn=(20, -266), waist=(-8, -199),
             hipf=(-18, -165), hipn=(8, -164), knf=(-36, -92), knn=(10, -88),
             anf=(-46, -10), ann=(22, -16), tof=(-72, -3), ton=(4, -1),
             elf=(-62, -218), wrf=(-48, -262), eln=(26, -210), wrn=(32, -164))
    f = Fig()
    place_head(f, J, rot=-8, s=0.46, beard="long", cover="turban", expr=expr, gaze=-1.0, phylactery=True, age=2,
               beard_dark=False, z=80, order=0)
    D = Dressed()
    skirt, (hl, hr, hy) = robe_standing(J, flare=12)
    D.add(20, unary_union([torso(J, chest=19, waist=17), skirt, circ(J["neck"], 9)]), "robe", None)
    tps = pharisee_mantle(D, J, front_len=-66, back_len=-50)
    D.add(40, unary_union([capsule(J["shf"], J["elf"], 10, 10.4), capsule(J["elf"], J["wrf"], 10.4, 8.4)]), "farm", "S")
    D.add(44, unary_union([capsule(J["shn"], J["eln"], 10, 10.2), capsule(J["eln"], J["wrn"], 10.2, 8.2)]), "narm", "S")
    body, u = add_dressed(f, D, folds=[(K.sm([(-30, -150), (-36, -100), (-42, hy - 4)]), "M")])
    for i, (tx_, ty_) in enumerate(tps):
        tassel(body, tx_, ty_, ang=96, length=18, lv="M")
    hd = f.part("hands", 90, 3)
    rig_hand(hd, "grip", J["wrf"][0], J["wrf"][1], rot=ang(J["elf"], J["wrf"]) - 180 + 20, s=1.0)
    rig_hand(hd, "relaxed", J["wrn"][0], J["wrn"][1], rot=ang(J["eln"], J["wrn"]) - 90, s=1.0)
    ft = f.part("feet", 5, 4)
    foot(ft, J["anf"][0], J["anf"][1], J["tof"])
    foot(ft, J["ann"][0], J["ann"][1], J["ton"])
    return f, J


