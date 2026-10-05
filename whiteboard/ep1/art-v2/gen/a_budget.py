"""Estimate engine hand time for an art SVG (mirrors engine/page/engine.js simulateArt).
usage: python3 a_budget.py file.svg [window_s]  -> needed pen speed for the window, per-element costs."""
import re, sys, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a_sketch as K

SC = 0.9556            # art unit -> frame px (art box 1529 px wide)
K_MOVE = 2.6
PAUSE = {"line": 0.15, "detail": 0.04}
SPEED = {"line": 1.0, "detail": 1.8}


def events(svgtext):
    ev = []
    for m in re.finditer(r'<path class="(line|detail)"([^>]*?) d="([^"]+)"', svgtext):
        cls, d = m.group(1), m.group(3)
        for pl in K.flatten(d, 1.0):
            if len(pl) < 2:
                continue
            L = sum(math.dist(a, b) for a, b in zip(pl, pl[1:])) * SC
            ev.append(dict(cls=cls, L=max(L, 3), p0=(pl[0][0] * SC, pl[0][1] * SC), p1=(pl[-1][0] * SC, pl[-1][1] * SC),
                           idx=m.start()))
    return ev


def sim(ev, v, pk=1.0):
    t, prev = 0.0, None
    for e in ev:
        if prev:
            d = math.dist(e["p0"], prev["p1"])
            t += d / (K_MOVE * v) + PAUSE[e["cls"]] * pk * min(1, max(0.35, 0.35 + d / 250))
        t += e["L"] / (v * SPEED[e["cls"]])
        prev = e
    return t


def need(ev, window):
    for v in range(1300, 5601, 50):
        if sim(ev, v) <= window:
            return v
    return None


if __name__ == "__main__":
    txt = open(sys.argv[1]).read()
    win = float(sys.argv[2]) if len(sys.argv) > 2 else None
    ev = events(txt)
    nl = sum(1 for e in ev if e["cls"] == "line"); nd = len(ev) - nl
    print(f"strokes: line {nl}, detail {nd}; pen length line {sum(e['L'] for e in ev if e['cls']=='line'):.0f}px "
          f"detail {sum(e['L'] for e in ev if e['cls']=='detail'):.0f}px")
    for v in (2200, 3000, 3600):
        print(f"  time @{v}px/s: {sim(ev, v):.2f}s")
    if win:
        print(f"  window {win}s -> needs {need(ev, win)} px/s (ok <= 3600)")
