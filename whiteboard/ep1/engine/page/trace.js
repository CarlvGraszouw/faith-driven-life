/* trace.js - turn a small bitmap (a handwritten letter, or the colour edges of a
 * logo) into ordered centre-line pen strokes.  Pure JS, no DOM.
 *
 *   WBTrace.trace(bin, w, h, opts) -> [{ pts:[x0,y0,x1,y1,...], r:maxRadius, closed }]
 *
 * bin is a Uint8Array (1 = ink).  Steps: distance transform -> Zhang-Suen
 * thinning -> skeleton graph -> prune spurs -> join edges that continue
 * straight through junctions -> smooth + simplify -> drawing order.
 */
(function (root) {
  'use strict';

  // Exact Euclidean distance transform (Felzenszwalb & Huttenlocher).
  function edt(bin, w, h) {
    const INF = 1e20, n = Math.max(w, h);
    const f = new Float64Array(n), d = new Float64Array(n), z = new Float64Array(n + 1);
    const v = new Int32Array(n), g = new Float64Array(w * h);
    for (let i = 0; i < w * h; i++) g[i] = bin[i] ? INF : 0;
    const pass = (len) => {
      let k = 0; v[0] = 0; z[0] = -INF; z[1] = INF;
      for (let q = 1; q < len; q++) {
        let s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]);
        while (s <= z[k]) { k--; s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]); }
        k++; v[k] = q; z[k] = s; z[k + 1] = INF;
      }
      k = 0;
      for (let q = 0; q < len; q++) { while (z[k + 1] < q) k++; d[q] = (q - v[k]) * (q - v[k]) + f[v[k]]; }
    };
    for (let x = 0; x < w; x++) { for (let y = 0; y < h; y++) f[y] = g[y * w + x]; pass(h); for (let y = 0; y < h; y++) g[y * w + x] = d[y]; }
    for (let y = 0; y < h; y++) { for (let x = 0; x < w; x++) f[x] = g[y * w + x]; pass(w); for (let x = 0; x < w; x++) g[y * w + x] = d[x]; }
    const out = new Float32Array(w * h);
    for (let i = 0; i < w * h; i++) out[i] = Math.sqrt(g[i]);
    return out;
  }

  // Zhang-Suen thinning; image border is cleared so neighbour lookups never leave the array.
  function thin(bin, w, h) {
    const img = new Uint8Array(bin);
    for (let x = 0; x < w; x++) { img[x] = 0; img[(h - 1) * w + x] = 0; }
    for (let y = 0; y < h; y++) { img[y * w] = 0; img[y * w + w - 1] = 0; }
    let list = [];
    for (let i = 0; i < w * h; i++) if (img[i]) list.push(i);
    const del = [];
    for (let changed = true; changed;) {
      changed = false;
      for (let step = 0; step < 2; step++) {
        del.length = 0;
        for (const i of list) {
          if (!img[i]) continue;
          const p2 = img[i - w], p3 = img[i - w + 1], p4 = img[i + 1], p5 = img[i + w + 1],
            p6 = img[i + w], p7 = img[i + w - 1], p8 = img[i - 1], p9 = img[i - w - 1];
          const B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9;
          if (B < 2 || B > 6) continue;
          const A = (!p2 && p3) + (!p3 && p4) + (!p4 && p5) + (!p5 && p6) + (!p6 && p7) + (!p7 && p8) + (!p8 && p9) + (!p9 && p2);
          if (A !== 1) continue;
          if (step === 0 ? (p2 && p4 && p6) || (p4 && p6 && p8) : (p2 && p4 && p8) || (p2 && p6 && p8)) continue;
          del.push(i);
        }
        for (const i of del) img[i] = 0;
        if (del.length) changed = true;
      }
      list = list.filter((i) => img[i]);
    }
    return img;
  }

  // Ring order: N NE E SE S SW W NW
  const RX = [0, 1, 1, 1, 0, -1, -1, -1], RY = [-1, -1, 0, 1, 1, 1, 0, -1];
  // Remove staircase pixels: a pixel whose neighbours form one 8-connected group
  // (and that is not a line end) can go without changing the topology.
  function removeRedundant(sk, w, h, list) {
    const on = new Array(8), par = new Array(8);
    const find = (a) => { while (par[a] !== a) a = par[a] = par[par[a]]; return a; };
    for (const i of list) {
      if (!sk[i]) continue;
      let cnt = 0;
      for (let k = 0; k < 8; k++) { on[k] = sk[i + RY[k] * w + RX[k]] ? 1 : 0; cnt += on[k]; par[k] = k; }
      if (cnt < 2) continue;
      for (let a = 0; a < 8; a++) if (on[a]) for (let b = a + 1; b < 8; b++) if (on[b] &&
        Math.abs(RX[a] - RX[b]) <= 1 && Math.abs(RY[a] - RY[b]) <= 1) par[find(a)] = find(b);
      let comps = 0;
      for (let k = 0; k < 8; k++) if (on[k] && find(k) === k) comps++;
      if (comps === 1) sk[i] = 0;
    }
  }

  function smoothPts(P, closed, passes) {
    // P: array of [x,y]; endpoints of open chains stay fixed (they are junction centres / line ends)
    const n = P.length;
    if (n < 4) return P;
    let a = P;
    for (let s = 0; s < passes; s++) {
      const b = a.map((p) => p.slice());
      for (let i = 0; i < n; i++) {
        if (!closed && (i === 0 || i === n - 1)) continue;
        const pm = a[(i - 1 + n) % n], pp = a[(i + 1) % n];
        b[i][0] = (pm[0] + 2 * a[i][0] + pp[0]) / 4;
        b[i][1] = (pm[1] + 2 * a[i][1] + pp[1]) / 4;
      }
      a = b;
    }
    return a;
  }

  function rdp(P, eps) {
    if (P.length < 3) return P;
    const n = P.length;
    if (Math.hypot(P[0][0] - P[n - 1][0], P[0][1] - P[n - 1][1]) < 1e-6) {
      // closed ring: split at the point farthest from the start
      let far = 1, fd = -1;
      for (let i = 1; i < n - 1; i++) { const d = Math.hypot(P[i][0] - P[0][0], P[i][1] - P[0][1]); if (d > fd) { fd = d; far = i; } }
      return rdp(P.slice(0, far + 1), eps).concat(rdp(P.slice(far), eps).slice(1));
    }
    const keep = new Uint8Array(P.length); keep[0] = keep[P.length - 1] = 1;
    const stack = [[0, P.length - 1]];
    while (stack.length) {
      const [a, b] = stack.pop();
      const ax = P[a][0], ay = P[a][1], dx = P[b][0] - ax, dy = P[b][1] - ay;
      const L = Math.hypot(dx, dy) || 1e-9;
      let best = -1, bi = -1;
      for (let i = a + 1; i < b; i++) {
        const d = Math.abs((P[i][0] - ax) * dy - (P[i][1] - ay) * dx) / L;
        if (d > best) { best = d; bi = i; }
      }
      if (best > eps) { keep[bi] = 1; stack.push([a, bi], [bi, b]); }
    }
    return P.filter((_, i) => keep[i]);
  }

  function polyLen(P) {
    let L = 0;
    for (let i = 1; i < P.length; i++) L += Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]);
    return L;
  }

  function trace(bin, w, h, opts) {
    opts = opts || {};
    const dist = edt(bin, w, h);
    const sk = thin(bin, w, h);
    let list = [];
    for (let i = 0; i < w * h; i++) if (sk[i]) list.push(i);
    removeRedundant(sk, w, h, list);
    list = list.filter((i) => sk[i]);
    const N8 = [-w, -w + 1, 1, w + 1, w, w - 1, -1, -w - 1];
    const deg = new Uint8Array(w * h);
    for (const i of list) { let c = 0; for (let k = 0; k < 8; k++) if (sk[i + N8[k]]) c++; deg[i] = c; }

    // junction clusters
    const cid = new Int32Array(w * h).fill(-1), clusters = [];
    for (const i of list) {
      if (deg[i] < 3 || cid[i] >= 0) continue;
      const id = clusters.length, pix = [i]; cid[i] = id;
      for (let q = 0; q < pix.length; q++) for (let k = 0; k < 8; k++) {
        const n = pix[q] + N8[k];
        if (sk[n] && deg[n] >= 3 && cid[n] < 0) { cid[n] = id; pix.push(n); }
      }
      let sx = 0, sy = 0, r = 0;
      for (const p of pix) { sx += p % w; sy += (p / w) | 0; r = Math.max(r, dist[p]); }
      clusters.push({ x: sx / pix.length + 0.5, y: sy / pix.length + 0.5, r, pix, deg: 0 });
    }

    const vis = new Uint8Array(w * h), edges = [];
    const walk = (start, prev, from) => {
      const pix = []; let cur = start, to = -1, closed = false;
      for (;;) {
        vis[cur] = 1; pix.push(cur);
        let next = -1, nextC = -1;
        for (let k = 0; k < 8; k++) {
          const n = cur + N8[k];
          if (!sk[n] || n === prev) continue;
          if (cid[n] >= 0) nextC = cid[n];
          else if (!vis[n]) { if (next < 0 || (k & 1) === 0) next = n; }
          else if (n === start && pix.length > 2) closed = true;
        }
        if (nextC >= 0 && !(pix.length === 1 && nextC === from && next >= 0)) { to = nextC; break; }
        if (next < 0) break;
        prev = cur; cur = next;
      }
      const P = [];
      if (from >= 0) P.push([clusters[from].x, clusters[from].y]);
      let rmax = 0;
      for (const p of pix) { P.push([p % w + 0.5, ((p / w) | 0) + 0.5]); rmax = Math.max(rmax, dist[p]); }
      if (to >= 0) P.push([clusters[to].x, clusters[to].y]);
      edges.push({ P, a: from, b: to, closed: closed && from < 0 && to < 0, r: rmax, alive: true });
    };
    clusters.forEach((c, id) => {
      for (const p of c.pix) for (let k = 0; k < 8; k++) {
        const n = p + N8[k];
        if (sk[n] && cid[n] < 0 && !vis[n]) walk(n, p, id);
      }
    });
    for (const i of list) if (!vis[i] && cid[i] < 0 && deg[i] <= 1) walk(i, -1, -1);
    for (const i of list) if (!vis[i] && cid[i] < 0) {
      let prev = -1;
      for (let k = 0; k < 8; k++) if (sk[i + N8[k]] && cid[i + N8[k]] < 0) { prev = i + N8[k]; break; }
      walk(i, prev, -1);
    }
    // isolated junction clusters (tiny blobs) become dots
    clusters.forEach((c, id) => {
      if (!edges.some((e) => e.a === id || e.b === id)) edges.push({ P: [[c.x, c.y]], a: -1, b: -1, closed: false, r: c.r, alive: true });
    });

    // smooth pixel stairs, measure
    for (const e of edges) { e.P = smoothPts(e.P, e.closed, 3); e.len = polyLen(e.P); }
    for (const e of edges) { if (e.a >= 0) clusters[e.a].deg++; if (e.b >= 0) clusters[e.b].deg++; }

    // prune short spurs (thinning artefacts at corners and blobs)
    const spurMin = opts.spur != null ? opts.spur : 2.5;
    const spurs = edges.filter((e) => (e.a >= 0) !== (e.b >= 0) || (e.a >= 0 && e.a === e.b));
    spurs.sort((p, q) => p.len - q.len);
    for (const e of spurs) {
      const c = clusters[e.a >= 0 ? e.a : e.b];
      const self = e.a === e.b;
      if (e.len >= Math.max(spurMin, 1.6 * c.r + 1.5) * (self ? 2 : 1)) continue;
      if (!self && c.deg < 3) continue;
      e.alive = false; c.deg -= self ? 2 : 1;
    }
    const live = edges.filter((e) => e.alive);

    // pair edges that continue straight through a junction
    const dirAt = (e, end, c) => {
      const P = end === 0 ? e.P : e.P.slice().reverse();
      const want = Math.max(3, 1.5 * c.r + 2);
      let acc = 0, q = P[P.length - 1];
      for (let i = 1; i < P.length; i++) { acc += Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); if (acc >= want) { q = P[i]; break; } }
      const dx = q[0] - c.x, dy = q[1] - c.y, L = Math.hypot(dx, dy) || 1;
      return [dx / L, dy / L];
    };
    for (const e of live) e.link = [null, null];
    clusters.forEach((c, id) => {
      const ends = [];
      for (const e of live) { if (e.a === id) ends.push({ e, end: 0 }); if (e.b === id) ends.push({ e, end: 1 }); }
      if (ends.length < 2) return;
      for (const en of ends) en.d = dirAt(en.e, en.end, c);
      const cand = [];
      for (let i = 0; i < ends.length; i++) for (let j = i + 1; j < ends.length; j++) {
        if (ends[i].e === ends[j].e) continue;
        const dot = ends[i].d[0] * ends[j].d[0] + ends[i].d[1] * ends[j].d[1];
        const dev = Math.acos(Math.max(-1, Math.min(1, -dot)));
        if (dev < 0.95) cand.push({ i, j, dev });
      }
      cand.sort((p, q) => p.dev - q.dev);
      const used = new Set();
      for (const c2 of cand) {
        if (used.has(c2.i) || used.has(c2.j)) continue;
        used.add(c2.i); used.add(c2.j);
        const A = ends[c2.i], B = ends[c2.j];
        A.e.link[A.end] = B; B.e.link[B.end] = A;
      }
    });

    // assemble strokes along the links
    const done = new Set(), strokes = [];
    const build = (e0, enter) => {
      let P = [], e = e0, ent = enter, r = 0, closed = false;
      while (e && !done.has(e)) {
        done.add(e); r = Math.max(r, e.r);
        const seg = ent === 0 ? e.P : e.P.slice().reverse();
        P = P.length ? P.concat(seg.slice(1)) : seg.slice();
        const nx = e.link[1 - ent];
        if (!nx) break;
        if (nx.e === e0 && done.has(nx.e)) { closed = true; break; }
        e = nx.e; ent = nx.end;
      }
      return { P, r, closed: closed || e0.closed };
    };
    for (const e of live) if (!done.has(e) && (!e.link[0] || !e.link[1])) strokes.push(build(e, e.link[0] ? 1 : 0));
    for (const e of live) if (!done.has(e)) strokes.push(build(e, 0));

    // extend free line ends a little (thinning eats about one radius off each end)
    const out = [];
    for (const s of strokes) {
      let P = s.P;
      if (P.length === 1) P = [P[0], [P[0][0] + 0.01, P[0][1]]];
      if (!s.closed && P.length >= 2 && opts.extend !== false) {
        const ext = (a, bIdx) => {
          const b = P[bIdx], dx = a[0] - b[0], dy = a[1] - b[1], L = Math.hypot(dx, dy);
          if (L < 0.5) return a;
          const k = (s.r * 0.6) / L;
          return [a[0] + dx * k, a[1] + dy * k];
        };
        const back = Math.min(P.length - 1, 3);
        P = [ext(P[0], back)].concat(P.slice(1, -1), [ext(P[P.length - 1], P.length - 1 - back)]);
      }
      if (s.closed && P.length > 2) P.push(P[0].slice());
      P = rdp(P, opts.eps != null ? opts.eps : 0.35);
      const len = polyLen(P);
      if (len < (opts.minLen || 0) && strokes.length > 1) continue;
      out.push({ P, r: s.r, closed: s.closed, len });
    }
    return order(out, opts);
  }

  // Drawing order: long strokes first (outlines), roughly top-to-bottom and
  // left-to-right with nearest-neighbour continuity, short details last.
  function order(strokes, opts) {
    if (!strokes.length) return [];
    for (const s of strokes) {
      let x0 = 1e9, y0 = 1e9;
      for (const p of s.P) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); }
      s.x0 = x0; s.y0 = y0;
    }
    const total = strokes.reduce((a, s) => a + s.len, 0);
    const sorted = strokes.slice().sort((a, b) => b.len - a.len);
    let acc = 0, thr = Infinity;
    for (const s of sorted) { acc += s.len; if (acc >= total * (opts.majorShare || 0.6)) { thr = s.len; break; } }
    thr = Math.max(thr * 0.999, 0);
    const majors = strokes.filter((s) => s.len >= thr), details = strokes.filter((s) => s.len < thr);
    const res = [];
    let pen = opts.startAt || [0, 0];
    const run = (set, bias) => {
      const rem = set.slice();
      while (rem.length) {
        let minY = Infinity; for (const s of rem) minY = Math.min(minY, s.y0);
        let best = null, bc = Infinity, bRev = false;
        for (const s of rem) {
          const a = s.P[0], b = s.P[s.P.length - 1];
          const da = Math.hypot(a[0] - pen[0], a[1] - pen[1]), db = s.closed ? Infinity : Math.hypot(b[0] - pen[0], b[1] - pen[1]);
          const d = Math.min(da, db), c = d + bias * (s.y0 - minY);
          if (c < bc) {
            bc = c; best = s;
            // near-equal ends: start from the top-left one (natural hand direction)
            bRev = db < da * 0.75 || (Math.abs(da - db) <= Math.max(da, db) * 0.25 && (b[0] + b[1]) < (a[0] + a[1]));
          }
        }
        rem.splice(rem.indexOf(best), 1);
        if (best.closed) {
          // start a loop at its top-most point, drawn anticlockwise like a right-handed oval
          let k = 0; best.P.forEach((p, i) => { if (p[1] + 0.3 * p[0] < best.P[k][1] + 0.3 * best.P[k][0]) k = i; });
          let ring = best.P.slice(0, -1); ring = ring.slice(k).concat(ring.slice(0, k));
          let area = 0; for (let i = 0; i < ring.length; i++) { const p = ring[i], q = ring[(i + 1) % ring.length]; area += p[0] * q[1] - q[0] * p[1]; }
          if (area > 0) ring = [ring[0]].concat(ring.slice(1).reverse());
          ring.push(ring[0].slice());
          best.P = ring;
        } else if (bRev) best.P = best.P.slice().reverse();
        res.push(best);
        pen = best.P[best.P.length - 1];
      }
    };
    run(majors, opts.bias != null ? opts.bias : 0.45);
    run(details, opts.bias != null ? opts.bias : 0.45);
    return res.map((s) => ({ pts: [].concat.apply([], s.P), r: s.r, closed: s.closed, len: s.len }));
  }

  const api = { edt, thin, trace, order, rdp };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.WBTrace = api;
})(typeof self !== 'undefined' ? self : this);
