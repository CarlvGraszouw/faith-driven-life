"""Architecture bits for batch A boards (all drawn as self-drawn hatch: background)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import a_sketch as K


def corinthian_column(cx, base_y, top_y, w=36.0, flutes=5):
    """Royal Stoa column: Attic base, fluted shaft with entasis, Corinthian capital (two tiers of acanthus,
    corner volutes, concave abacus with a rosette).  -> (outline/lines path, shading hatch path)."""
    r = w / 2
    cap_h = 44.0
    shaft_top = top_y + cap_h
    d = []
    # base: plinth, torus, scotia, torus
    d.append(K.seg((cx - r - 8, base_y), (cx + r + 8, base_y), (cx + r + 8, base_y - 6), (cx - r - 8, base_y - 6)) + " Z")
    d.append(K.sm([(cx - r - 6, base_y - 6), (cx - r - 7, base_y - 10), (cx - r - 4, base_y - 13), (cx + r + 4, base_y - 13),
                   (cx + r + 7, base_y - 10), (cx + r + 6, base_y - 6)]))
    d.append(K.sm([(cx - r - 3, base_y - 13), (cx - r - 1, base_y - 16), (cx - r - 3, base_y - 19), (cx + r + 3, base_y - 19),
                   (cx + r + 1, base_y - 16), (cx + r + 3, base_y - 13)]))
    # shaft with a slight entasis
    lft = [(cx - r, base_y - 19), (cx - r - 0.8, (base_y + shaft_top) / 2), (cx - r + 1.6, shaft_top + 4)]
    rgt = [(cx + r, base_y - 19), (cx + r + 0.8, (base_y + shaft_top) / 2), (cx + r - 1.6, shaft_top + 4)]
    d.append(K.sm(lft)); d.append(K.sm(rgt))
    for k in range(1, flutes + 1):
        t = k / (flutes + 1)
        x0 = cx - r + 2 * r * t
        d.append(K.seg((x0, base_y - 22), (x0 + (cx - x0) * 0.08, shaft_top + 6)))
    # astragal (necking ring)
    d.append(K.seg((cx - r + 1, shaft_top + 4), (cx + r - 1, shaft_top + 4)))
    d.append(K.seg((cx - r + 1, shaft_top + 1), (cx + r - 1, shaft_top + 1)))
    # capital bell
    bell_l = [(cx - r + 1.6, shaft_top + 1), (cx - r - 2, shaft_top - 16), (cx - r - 8, shaft_top - 34), (cx - r - 12, top_y + 6)]
    bell_r = [(cx + r - 1.6, shaft_top + 1), (cx + r + 2, shaft_top - 16), (cx + r + 8, shaft_top - 34), (cx + r + 12, top_y + 6)]
    # acanthus: lower tier (4 leaves), upper tier (3 leaves) with curled tips
    for k in range(4):
        lx = cx - r + 3 + k * (2 * r - 6) / 3
        d.append(K.sm([(lx - 5, shaft_top), (lx - 6, shaft_top - 10), (lx - 2, shaft_top - 17), (lx + 2, shaft_top - 14),
                       (lx + 1, shaft_top - 11)]))
        d.append(K.sm([(lx + 5, shaft_top), (lx + 6, shaft_top - 10), (lx + 2, shaft_top - 17)]))
    for k in range(3):
        lx = cx - r + 6 + k * (2 * r - 12) / 2
        d.append(K.sm([(lx - 6, shaft_top - 15), (lx - 7, shaft_top - 26), (lx - 2, shaft_top - 33), (lx + 3, shaft_top - 29),
                       (lx + 2, shaft_top - 26)]))
        d.append(K.sm([(lx + 6, shaft_top - 15), (lx + 7, shaft_top - 26), (lx + 2, shaft_top - 33)]))
    # corner volutes
    for sgn in (-1, 1):
        vx, vy = cx + sgn * (r + 9), top_y + 9
        spiral = [(vx + sgn * 0.0, vy - 0.0)]
        for i in range(1, 14):
            a = i * 0.62
            rr = 4.6 * (1 - i / 16)
            spiral.append((vx + sgn * rr * math.cos(a + 2.4), vy + rr * math.sin(a + 2.4)))
        d.append(K.sm([(cx + sgn * (r - 4), shaft_top - 30), (cx + sgn * (r + 4), top_y + 12)] + spiral[::-1]))
    # abacus with concave sides and a rosette
    d.append(K.sm([(cx - r - 16, top_y + 4), (cx - r - 14, top_y), (cx, top_y + 2.6), (cx + r + 14, top_y), (cx + r + 16, top_y + 4)]))
    d.append(K.sm([(cx - r - 16, top_y), (cx - r - 14, top_y - 5), (cx, top_y - 3.4), (cx + r + 14, top_y - 5), (cx + r + 16, top_y)]))
    d.append(K.sm([(cx - 2.6, top_y + 5.6), (cx, top_y + 3.4), (cx + 2.6, top_y + 5.6), (cx, top_y + 7.8), (cx - 2.6, top_y + 5.6)]))
    shade = K.hatch([(cx + r * 0.3, base_y - 22), (cx + r, base_y - 22), (cx + r, shaft_top + 6), (cx + r * 0.3, shaft_top + 6)],
                    angle=90, spacing=2.6, seed=int(cx))
    shade += " " + K.hatch([(cx + r * 0.2, shaft_top), (cx + r + 2, shaft_top), (cx + r + 11, top_y + 8), (cx + r * 0.4, top_y + 8)],
                           angle=80, spacing=2.2, seed=int(cx) + 1)
    return " ".join(d), shade
