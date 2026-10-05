/* engine.js - whiteboard animation renderer.
 *
 *   await loadJob(job)   build the board (called once by render.js)
 *   renderAt(seconds)    put the page in the exact state for that time
 *
 * Everything is a pure function of t: no timers, no CSS animation.  One long
 * SVG board holds every scene; a camera <g> pans/zooms across it.  Line art is
 * drawn path by path with stroke-dashoffset; the pen tip is placed with
 * getPointAtLength on the same path, so it always sits on the drawing point.
 */
(function () {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg', XL = 'http://www.w3.org/1999/xlink';
  const $ = (id) => document.getElementById(id);
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, u) => a + (b - a) * u;
  const smooth = (u) => { u = clamp(u, 0, 1); return u * u * (3 - 2 * u); };
  const smoother = (u) => { u = clamp(u, 0, 1); return u * u * u * (u * (u * 6 - 15) + 10); };
  const easeOut = (u) => { u = clamp(u, 0, 1); return 1 - Math.pow(1 - u, 3); };
  const easeIn = (u) => { u = clamp(u, 0, 1); return u * u * u; };
  const easeSine = (u) => { u = clamp(u, 0, 1); return 0.5 - 0.5 * Math.cos(Math.PI * u); };

  const FILL_FADE = 0.14;   // a path's own fill appears as its stroke completes
  const RESIDUAL = 0.22;    // per-letter clean-up fade at the end of each letter
  const OPT = {};           // job-level options

  let W = 1920, H = 1080, INK = '#1f1f1f', SAFE_BOTTOM = 860;
  let scenes = [], capParts = [], HAND = null, KITS = [];
  let uid = 0;
  const warnings = [];
  const warn = (m) => { warnings.push(m); console.warn(m); };

  function mk(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  const mul = (A, B) => [A[0] * B[0] + A[2] * B[1], A[1] * B[0] + A[3] * B[1], A[0] * B[2] + A[2] * B[3],
    A[1] * B[2] + A[3] * B[3], A[0] * B[4] + A[2] * B[5] + A[4], A[1] * B[4] + A[3] * B[5] + A[5]];
  const apply = (M, x, y) => [M[0] * x + M[2] * y + M[4], M[1] * x + M[3] * y + M[5]];
  const fromDOM = (m) => [m.a, m.b, m.c, m.d, m.e, m.f];
  const ID = [1, 0, 0, 1, 0, 0];

  // ---------------------------------------------------------------- fonts
  async function loadFonts(fonts) {
    for (const f of fonts || []) {
      const bin = Uint8Array.from(atob(f.data), (c) => c.charCodeAt(0));
      const ff = new FontFace(f.family, bin.buffer, { weight: f.weight || 'normal', style: 'normal', display: 'block' });
      await ff.load();
      document.fonts.add(ff);
    }
    await document.fonts.ready;
  }

  // ---------------------------------------------------------------- SVG input
  const SKIP = new Set(['defs', 'clipPath', 'mask', 'symbol', 'pattern', 'marker', 'linearGradient', 'radialGradient',
    'filter', 'style', 'title', 'desc', 'metadata', 'script']);
  const GEOM = new Set(['path', 'line', 'polyline', 'polygon', 'rect', 'circle', 'ellipse']);
  const BAKE = ['fill', 'fill-opacity', 'fill-rule', 'stroke', 'stroke-width', 'stroke-opacity', 'stroke-linecap',
    'stroke-linejoin', 'stroke-miterlimit', 'stroke-dasharray', 'stroke-dashoffset', 'opacity', 'display', 'visibility',
    'paint-order', 'clip-path', 'mask', 'filter', 'font-family', 'font-size', 'font-weight', 'font-style', 'text-anchor'];

  function parseSVG(text, what) {
    const doc = new DOMParser().parseFromString(text, 'image/svg+xml');
    const err = doc.querySelector('parsererror');
    if (err || doc.documentElement.localName !== 'svg') throw new Error(`${what}: not valid SVG (${err ? err.textContent.slice(0, 160) : 'no <svg> root'})`);
    return doc;
  }
  const byId = (root, id) => root.querySelector(`[id="${id.replace(/["\\]/g, '\\$&')}"]`);
  function findRef(id, file, root) {
    if (!file) { const n = byId(root, id); if (n) return { node: n, kit: null }; }
    const base = file ? file.split('/').pop() : '';
    for (const pass of [0, 1]) for (const k of KITS) {
      if (pass === 0 && base && k.name !== base) continue;
      const n = byId(k.doc.documentElement, id);
      if (n) return { node: n, kit: k };
    }
    return null;
  }
  const vbOf = (n) => {
    const v = (n.getAttribute('viewBox') || '').trim().split(/[\s,]+/).map(Number);
    return v.length === 4 && v.every(isFinite) && v[2] > 0 && v[3] > 0 ? v : null;
  };
  // Replace every <use> (local or kit.svg#symbol) with real elements so each path can be animated.
  function flattenUses(root, usedKits) {
    const doc = root.ownerDocument;
    for (let guard = 0; guard < 25; guard++) {
      const uses = Array.from(root.getElementsByTagNameNS(NS, 'use'));
      if (!uses.length) return;
      for (const u of uses) {
        if (!u.parentNode) continue;
        const href = u.getAttribute('href') || u.getAttributeNS(XL, 'href') || '';
        const h = href.indexOf('#');
        const file = h > 0 ? href.slice(0, h) : '', id = href.slice(h + 1);
        const ref = findRef(id, file, root);
        const g = doc.createElementNS(NS, 'g');
        for (const a of Array.from(u.attributes)) {
          if (['x', 'y', 'width', 'height', 'href', 'xlink:href', 'transform'].includes(a.name)) continue;
          g.setAttribute(a.name, a.value);
        }
        if (!ref) { warn(`symbol not found: ${href}`); u.replaceWith(g); continue; }
        if (ref.kit) usedKits.add(ref.kit);
        const x = parseFloat(u.getAttribute('x')) || 0, y = parseFloat(u.getAttribute('y')) || 0;
        let tr = `${u.getAttribute('transform') || ''} translate(${x},${y})`;
        const n = ref.node, inner = doc.createElementNS(NS, 'g');
        if (n.localName === 'symbol' || n.localName === 'svg') {
          const vb = vbOf(n);
          if (vb) {
            const w = parseFloat(u.getAttribute('width')) || parseFloat(n.getAttribute('width')) || vb[2];
            const hh = parseFloat(u.getAttribute('height')) || parseFloat(n.getAttribute('height')) || vb[3];
            const par = (n.getAttribute('preserveAspectRatio') || 'xMidYMid meet').trim();
            let sx = w / vb[2], sy = hh / vb[3], ox = 0, oy = 0;
            if (!par.startsWith('none')) {
              const s = par.includes('slice') ? Math.max(sx, sy) : Math.min(sx, sy);
              const al = par.split(/\s+/)[0];
              const fx = al.includes('xMin') ? 0 : al.includes('xMax') ? 1 : 0.5;
              const fy = al.includes('YMin') ? 0 : al.includes('YMax') ? 1 : 0.5;
              ox = (w - vb[2] * s) * fx; oy = (hh - vb[3] * s) * fy; sx = sy = s;
            }
            tr += ` translate(${ox},${oy}) scale(${sx},${sy}) translate(${-vb[0]},${-vb[1]})`;
          }
          for (const a of Array.from(n.attributes)) {
            if (['id', 'viewBox', 'preserveAspectRatio', 'width', 'height', 'x', 'y'].includes(a.name)) continue;
            inner.setAttribute(a.name, a.value);
          }
          for (const c of Array.from(n.childNodes)) inner.appendChild(doc.importNode(c, true));
        } else {
          const c = doc.importNode(n, true); c.removeAttribute('id'); inner.appendChild(c);
        }
        g.setAttribute('transform', tr.trim());
        g.appendChild(inner);
        u.replaceWith(g);
      }
    }
    warn('nested <use> deeper than 25 levels; stopped flattening');
  }
  // Ids must be unique on the shared board: prefix them and fix url(#..)/href references.
  function prefixIds(root, pre) {
    const map = new Map();
    root.querySelectorAll('[id]').forEach((e) => {
      const id = e.getAttribute('id');
      if (id === 'accent') e.setAttribute('data-accent', '1');
      map.set(id, pre + id); e.setAttribute('id', pre + id);
    });
    root.querySelectorAll('.accent').forEach((e) => e.setAttribute('data-accent', '1'));
    if (!map.size) return;
    const fix = (s) => s.replace(/url\(\s*(['"]?)#([^'")\s]+)\1\s*\)/g, (m, q, id) => (map.has(id) ? `url(#${map.get(id)})` : m));
    root.querySelectorAll('*').forEach((e) => {
      for (const a of Array.from(e.attributes)) {
        if ((a.localName === 'href') && a.value[0] === '#' && map.has(a.value.slice(1))) a.value = '#' + map.get(a.value.slice(1));
        else if (a.value.includes('url(')) a.value = fix(a.value);
      }
      if (e.localName === 'style') e.textContent = fix(e.textContent);
    });
  }
  // Resolve CSS classes into inline styles so scenes cannot restyle each other.
  function bakeStyles(g) {
    const all = [g, ...g.querySelectorAll('*')].filter((e) => e.localName !== 'style');
    const vals = all.map((e) => { const cs = getComputedStyle(e); return BAKE.map((p) => cs.getPropertyValue(p)); });
    all.forEach((e, i) => BAKE.forEach((p, j) => { if (vals[i][j]) e.style.setProperty(p, vals[i][j]); }));
    g.querySelectorAll('style').forEach((s) => s.remove());
  }
  const isWhite = (c) => {
    const m = /rgba?\(([^)]+)\)/.exec(c || '');
    if (!m) return false;
    const v = m[1].split(',').map(parseFloat);
    return v[0] >= 245 && v[1] >= 245 && v[2] >= 245;
  };
  // Split a multi-subpath "d" into one absolute-start "d" per subpath.
  function splitSubpaths(d) {
    const starts = [];
    const re = /[Mm]/g; let m;
    while ((m = re.exec(d))) starts.push(m.index);
    if (starts.length <= 1) return null;
    const tmp = mk('path', {}, $('defs'));
    const out = [];
    for (let i = 0; i < starts.length; i++) {
      const seg = d.slice(starts[i], i + 1 < starts.length ? starts[i + 1] : d.length);
      if (seg[0] === 'M' || i === 0) { out.push(i === 0 && seg[0] === 'm' ? 'M' + seg.slice(1) : seg); continue; }
      const nums = /^m\s*([-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?)\s*,?\s*([-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?)/.exec(seg);
      if (!nums) { tmp.remove(); return null; }
      tmp.setAttribute('d', d.slice(0, starts[i]));
      const L = tmp.getTotalLength(), P = tmp.getPointAtLength(L);
      const rest = seg.slice(nums[0].length).trim();
      out.push(`M${P.x + parseFloat(nums[1])} ${P.y + parseFloat(nums[2])}` + (rest && /^[-+.\d]/.test(rest) ? ' l' + rest : rest));
    }
    tmp.remove();
    return out;
  }
  function ctmTo(el, ref) { return fromDOM(ref.getScreenCTM().inverse().multiply(el.getScreenCTM())); }
  const linScale = (M) => Math.sqrt(Math.abs(M[0] * M[3] - M[1] * M[2])) || 1;

  // ---------------------------------------------------------------- scenes
  function layoutFrames(list) {
    const DY = [0, 0.07, -0.05, 0.05, -0.07, 0.03];
    let x = 0, y = 0;
    return list.map((sc, i) => {
      if (i > 0 && sc.camera !== 'hold') {
        const dir = sc.dir || 'right';
        if (dir === 'right') { x += W * 1.22; y = H * DY[i % DY.length]; }
        else if (dir === 'left') { x -= W * 1.22; y = H * DY[i % DY.length]; }
        else if (dir === 'down') { y += H * 1.12; x += W * DY[i % DY.length]; }
        else if (dir === 'up') { y -= H * 1.12; x += W * DY[i % DY.length]; }
      }
      return [x, y];
    });
  }

  async function buildArt(S, sc) {
    // --plan with art that does not exist yet: an empty item, so the windows can still be reported
    if (sc.missing) return { kind: 'art', mode: 'native', events: [], accents: [], toFrame: ID, box: null, D: sc.draw, at: sc.artAt, file: sc.file, missing: true };
    const doc = parseSVG(sc.svg, `scene ${sc.id}`);
    const root = doc.documentElement;
    const used = new Set();
    flattenUses(root, used);
    for (const k of used) {
      for (const d of k.doc.querySelectorAll('defs')) {
        const c = doc.importNode(d, true); c.querySelectorAll('symbol').forEach((s) => s.remove());
        if (c.childElementCount) root.insertBefore(c, root.firstChild);
      }
      for (const st of k.doc.querySelectorAll('style')) root.insertBefore(doc.importNode(st, true), root.firstChild);
    }
    prefixIds(root, `s${S.idx}_${S.items.length}_`);
    const vb = vbOf(root) || [0, 0, parseFloat(root.getAttribute('width')) || 1600, parseFloat(root.getAttribute('height')) || 900];
    const box = (sc.box || [0, 0, W, H]).slice();
    const safe = sc.safeBottom !== undefined ? sc.safeBottom : SAFE_BOTTOM;
    if (safe && box[1] + box[3] > safe) box[3] = Math.max(60, safe - box[1]); // keep art above the caption band
    const s = Math.min(box[2] / vb[2], box[3] / vb[3]);
    const ox = box[0] + (box[2] - vb[2] * s) / 2, oy = box[1] + (box[3] - vb[3] * s) / 2;
    const toFrame = [s, 0, 0, s, ox - vb[0] * s, oy - vb[1] * s];
    const rasterSrc = new XMLSerializer().serializeToString(root);

    const ag = mk('g', { class: 'art', transform: `matrix(${toFrame.join(' ')})` }, S.g);
    for (const a of Array.from(root.attributes)) {
      if (/^(xmlns|viewBox|width|height|x|y|version|preserveAspectRatio|id|transform)/.test(a.name)) continue;
      ag.setAttribute(a.name, a.value);
    }
    const content = mk('g', {}, ag);
    for (const c of Array.from(root.childNodes)) content.appendChild(document.importNode(c, true));
    bakeStyles(ag);

    const list = [];
    (function collect(node, inAccent) {
      for (const c of Array.from(node.children)) {
        if (SKIP.has(c.localName) || c.style.display === 'none') continue;
        if (!inAccent && c.getAttribute('data-accent') === '1') { list.push({ kind: 'accent', el: c }); continue; }
        if (GEOM.has(c.localName)) list.push({ kind: 'geom', el: c });
        else if (['text', 'image', 'foreignObject'].includes(c.localName)) list.push({ kind: 'fade', el: c });
        else collect(c, inAccent);
      }
    })(content, false);
    const hasStroke = (e) => {
      const st = e.style;
      return st.getPropertyValue('stroke') !== 'none' && parseFloat(st.getPropertyValue('stroke-width')) > 0 &&
        parseFloat(st.getPropertyValue('stroke-opacity') || '1') > 0;
    };
    const mode = sc.mode || (list.some((x) => x.kind === 'geom' && hasStroke(x.el)) ? 'native' : 'trace');
    const item = { kind: 'art', mode, events: [], accents: [], toFrame, box: [ox, oy, vb[2] * s, vb[3] * s], D: sc.draw, at: sc.artAt, file: sc.file };

    if (mode === 'trace') {
      // Coloured artwork without strokes (a logo): pen outlines the colour edges, then colours the shapes in.
      const strokes = await traceColourEdges(rasterSrc, vb, s);
      const ig = mk('g', { class: 'ink' }, ag);
      const sw = (sc.stroke || 4.5) / s;
      for (const st of strokes) {
        const P = st.pts;
        let d = `M${P[0].toFixed(2)} ${P[1].toFixed(2)}`;
        for (let i = 2; i < P.length; i += 2) d += `L${P[i].toFixed(2)} ${P[i + 1].toFixed(2)}`;
        const p = mk('path', { d }, ig);
        p.setAttribute('style', `fill:none;stroke:${sc.ink || INK};stroke-width:${sw};stroke-linecap:round;stroke-linejoin:round`);
        item.events.push(strokeEvent(p, toFrame));
      }
      addScribbles(item, [content], S);
      return item;
    }
    // Classes (on the path or its nearest classed group):
    //   "line"   - main contours, traced by the hand (the default for anything unclassed)
    //   "detail" - traced by the hand too, faster and with quicker hops (SPEEDK/PAUSE)
    //   "hatch"  - NOT traced by the hand: self-drawn together once the item's line/detail work is done
    //              (scheduleSelf), so it costs no hand time
    // Stroke widths/opacity come from the SVG's own <style> (baked above), e.g. v2: 2.6 / 1.5 / 0.9 @ .75.
    const clsOf = (el) => {
      const c = el.closest('.hatch, .detail, .line');
      if (!c || c.classList.contains('line')) return 'line';
      return c.classList.contains('detail') ? 'detail' : 'hatch';
    };
    const accentEls = [];
    for (const x of list) {
      const e = x.el;
      const n0 = item.events.length;
      if (x.kind === 'accent') { accentEls.push(e); continue; }
      if (x.kind === 'fade') { warn(`scene ${sc.id}: <${e.localName}> cannot be drawn by the pen; it fades in`); item.events.push({ kind: 'fade', el: e, o: parseFloat(e.style.opacity || '1') }); continue; }
      const st = e.style;
      const fill = st.getPropertyValue('fill'), fo = parseFloat(st.getPropertyValue('fill-opacity') || '1');
      const hasFill = fill && fill !== 'none' && fo > 0;
      const dashed = !['', 'none'].includes(st.getPropertyValue('stroke-dasharray'));
      const M = ctmTo(e, S.g);
      if (hasStroke(e) && !dashed) {
        const parts = e.localName === 'path' ? splitSubpaths(e.getAttribute('d') || '') : null;
        if (parts && parts.length > 1) {
          const strokeVal = st.getPropertyValue('stroke') || INK;
          if (hasFill) { e.style.stroke = 'none'; } else e.style.display = 'none';
          let after = e;
          parts.forEach((d, i) => {
            const c = e.cloneNode(false);
            c.removeAttribute('id'); c.setAttribute('d', d);
            c.style.fill = 'none'; c.style.stroke = strokeVal; c.style.display = '';
            after.after(c); after = c;
            const ev = strokeEvent(c, M);
            if (i === parts.length - 1 && hasFill) { ev.fillTarget = e; ev.fo = fo; ev.ownFill = false; e.style.visibility = 'hidden'; }
            item.events.push(ev);
          });
        } else {
          const ev = strokeEvent(e, M);
          if (hasFill) { ev.fillTarget = e; ev.fo = fo; ev.ownFill = true; }
          item.events.push(ev);
        }
      } else if (hasFill && !hasStroke(e)) {
        if (isWhite(fill)) item.events.push({ kind: 'instant', el: e });
        else {
          // solid non-white shape: pen runs round its outline while the fill fades in behind it
          const ev = strokeEvent(e, M);
          ev.kind = 'fill'; ev.fo = fo; ev.color = fill; ev.sw = 1.6 / linScale(M);
          item.events.push(ev);
        }
      } else if (dashed && hasStroke(e)) {
        // dashed line: a solid copy of the path in a mask is drawn by the pen and uncovers the dashes
        const sw = parseFloat(st.getPropertyValue('stroke-width')) || 3;
        let bb; try { bb = e.getBBox(); } catch (_) { bb = { x: -1e4, y: -1e4, width: 2e4, height: 2e4 }; }
        const id = `ds${uid++}`, pad = sw * 4;
        const mask = mk('mask', { id, maskUnits: 'userSpaceOnUse', x: bb.x - pad, y: bb.y - pad, width: bb.width + 2 * pad, height: bb.height + 2 * pad }, $('defs'));
        const resid = mk('rect', { x: bb.x - pad, y: bb.y - pad, width: bb.width + 2 * pad, height: bb.height + 2 * pad, fill: '#fff', opacity: 0 }, mask);
        const c = e.cloneNode(false);
        for (const a of ['id', 'class', 'transform', 'style', 'mask', 'clip-path']) c.removeAttribute(a);
        c.setAttribute('style', `fill:none;stroke:#fff;stroke-width:${sw + 4};stroke-linecap:round;stroke-linejoin:round`);
        mask.appendChild(c);
        e.style.setProperty('mask', `url(#${id})`);
        const ev = strokeEvent(c, M); ev.kind = 'mstroke'; ev.reveal = { target: e, id, resid };
        item.events.push(ev);
      }
      for (let k = n0; k < item.events.length; k++) {
        const ev = item.events[k];
        ev.cls = clsOf(e);
        if (ev.kind === 'stroke' || ev.kind === 'mstroke') {
          if (ev.cls === 'hatch') ev.self = true; // drawn without the hand, see scheduleSelf
          ev.swF = (parseFloat((ev.kind === 'mstroke' ? e : ev.el).style.strokeWidth) || 0) * linScale(ev.M);
        }
      }
    }
    addScribbles(item, accentEls, S);
    return item;
  }
  // per class: number of strokes and the rendered stroke width range in frame px (for the log)
  function classStats(item) {
    const out = {};
    for (const e of item.events) {
      if (!['stroke', 'mstroke', 'fill'].includes(e.kind) || !e.cls) continue;
      const o = out[e.cls] || (out[e.cls] = { n: 0, len: 0, w0: Infinity, w1: 0 });
      o.n++; o.len += e.lenF;
      if (e.swF) { o.w0 = Math.min(o.w0, e.swF); o.w1 = Math.max(o.w1, e.swF); }
    }
    for (const k in out) { const o = out[k]; o.len = Math.round(o.len); o.w0 = isFinite(o.w0) ? +o.w0.toFixed(2) : 0; o.w1 = +o.w1.toFixed(2); }
    return out;
  }

  // Colour is painted by the hand: it scribbles across each coloured shape and the colour
  // appears under the marker (a mask that the scribble stroke uncovers).
  function addScribbles(item, els, S) {
    const small = [];
    for (const a of els) {
      a.style.opacity = a.style.opacity || '1';
      const geoms = GEOM.has(a.localName) ? [a] : Array.from(a.querySelectorAll('path,line,polyline,polygon,rect,circle,ellipse'));
      for (const g of geoms) {
        if (g.closest('defs,mask,clipPath,symbol,pattern,marker')) continue;
        const cs = getComputedStyle(g);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        const hasF = cs.fill && cs.fill !== 'none' && parseFloat(cs.fillOpacity || '1') > 0;
        const hasS = cs.stroke && cs.stroke !== 'none' && parseFloat(cs.strokeWidth) > 0;
        if (!hasF && !hasS) continue;
        let bb; try { bb = g.getBBox(); } catch (_) { continue; }
        const M = ctmTo(g, S.g), k = linScale(M);
        const w = bb.width * k, h = bb.height * k;
        if (w < 8 || h < 8 || w * h < 260) { small.push(g); continue; }
        const b = clamp(Math.min(w, h) * 0.3, 16, 110) / k;          // brush width, local units
        const sp = b * 0.6, inset = b * 0.3;
        const horiz = bb.width >= bb.height;
        const L = horiz ? bb.width : bb.height, X = horiz ? bb.height : bb.width;
        const n = Math.max(1, Math.ceil((L - 2 * inset) / sp));
        let d = '';
        for (let i = 0; i <= n; i++) {
          const u = inset + ((L - 2 * Math.min(inset, L / 2)) * i) / n;
          const v = i % 2 === 0 ? Math.min(inset, X / 2) : X - Math.min(inset, X / 2);
          const P = horiz ? [bb.x + u, bb.y + v] : [bb.x + v, bb.y + u];
          d += `${i ? 'L' : 'M'}${P[0].toFixed(2)} ${P[1].toFixed(2)}`;
        }
        const id = `sc${uid++}`, pad = b * 2;
        const mask = mk('mask', { id, maskUnits: 'userSpaceOnUse', x: bb.x - pad, y: bb.y - pad, width: bb.width + 2 * pad, height: bb.height + 2 * pad }, $('defs'));
        const resid = mk('rect', { x: bb.x - pad, y: bb.y - pad, width: bb.width + 2 * pad, height: bb.height + 2 * pad, fill: '#fff', opacity: 0 }, mask);
        const p = mk('path', { d, fill: 'none', stroke: '#fff', 'stroke-width': (b * 1.35).toFixed(2), 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, mask);
        g.style.setProperty('mask', `url(#${id})`);
        const ev = strokeEvent(p, M);
        ev.kind = 'mstroke'; ev.cls = 'scribble'; ev.reveal = { target: g, id, resid };
        item.events.push(ev);
      }
    }
    // tiny coloured bits: appear right after the scribbles
    for (const g of small) { item.events.push({ kind: 'fade', el: g, o: parseFloat(g.style.opacity || '1') }); }
  }

  function strokeEvent(el, M) {
    const len = el.getTotalLength();
    const k = linScale(M);
    const a = el.getPointAtLength(0), b = el.getPointAtLength(len);
    return {
      kind: 'stroke', el, len, lenF: len * k, M, p0: apply(M, a.x, a.y), p1: apply(M, b.x, b.y),
      dash0: el.style.strokeDasharray || 'none', off0: el.style.strokeDashoffset || '0',
    };
  }

  // Rasterise the artwork, find colour boundaries, trace them into centre-line strokes.
  async function traceColourEdges(svgText, vb, s) {
    const q = Math.min(3, Math.max(1, (2 * 900) / Math.max(vb[2] * s, vb[3] * s))) * s; // raster px per user unit
    const rw = Math.ceil(vb[2] * q) + 8, rh = Math.ceil(vb[3] * q) + 8;
    const doc = parseSVG(svgText, 'raster');
    const r = doc.documentElement;
    r.setAttribute('width', rw - 8); r.setAttribute('height', rh - 8);
    r.setAttribute('viewBox', vb.join(' '));
    const url = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(new XMLSerializer().serializeToString(r));
    const img = new Image(); img.src = url; await img.decode();
    const cv = document.createElement('canvas'); cv.width = rw; cv.height = rh;
    const cx = cv.getContext('2d', { willReadFrequently: true });
    cx.drawImage(img, 4, 4, rw - 8, rh - 8);
    const px = cx.getImageData(0, 0, rw, rh).data;
    const comp = new Float32Array(rw * rh * 3), al = new Float32Array(rw * rh);
    for (let i = 0; i < rw * rh; i++) {
      const a = px[i * 4 + 3] / 255; al[i] = a;
      for (let c = 0; c < 3; c++) comp[i * 3 + c] = px[i * 4 + c] * a + 255 * (1 - a);
    }
    const bin = new Uint8Array(rw * rh);
    const diff = (i, j) => Math.abs(al[i] - al[j]) > 0.35 || Math.max(Math.abs(comp[i * 3] - comp[j * 3]),
      Math.abs(comp[i * 3 + 1] - comp[j * 3 + 1]), Math.abs(comp[i * 3 + 2] - comp[j * 3 + 2])) > 22;
    for (let y = 0; y < rh - 1; y++) for (let x = 0; x < rw - 1; x++) {
      const i = y * rw + x;
      if (diff(i, i + 1)) { bin[i] = 1; bin[i + 1] = 1; }
      if (diff(i, i + rw)) { bin[i] = 1; bin[i + rw] = 1; }
    }
    const strokes = WBTrace.trace(bin, rw, rh, { eps: 0.4, minLen: 6, extend: false, startAt: [0, 0] });
    return strokes.map((st) => ({ ...st, pts: st.pts.map((v, i) => (v - 4) / q + vb[i % 2]) }));
  }

  // Handwritten text: each letter is a crisp raster (3x) revealed through a mask of its own centre-line strokes.
  async function buildText(S, t) {
    const family = t.font || OPT.textFont || 'Caveat', weight = t.weight || 700, size = t.size || 96;
    const color = t.color || INK;
    const font = (sz) => `${weight} ${sz}px "${family}"`;
    await document.fonts.load(font(size), t.str);
    if (!document.fonts.check(font(size), t.str)) warn(`font not available: ${family}`);
    const c = document.createElement('canvas').getContext('2d');
    c.font = font(size);
    const total = c.measureText(t.str).width;
    const align = t.align || 'center';
    const left = t.at[0] - (align === 'center' ? total / 2 : align === 'right' ? total : 0), base = t.at[1];
    const q = 3, pad = Math.ceil(size * 0.1);
    const item = { kind: 'text', events: [], letters: [], D: t.draw, at: t.t, box: [left, base - size, total, size * 1.3], label: t.str };
    const tg = mk('g', { class: 'text' }, S.g);
    for (let i = 0; i < t.str.length; i++) {
      const ch = t.str[i];
      if (/\s/.test(ch)) continue;
      const x = left + c.measureText(t.str.slice(0, i)).width;
      const m = c.measureText(ch);
      const bl = Math.ceil(m.actualBoundingBoxLeft) + pad, br = Math.ceil(m.actualBoundingBoxRight) + pad;
      const ba = Math.ceil(m.actualBoundingBoxAscent) + pad, bd = Math.ceil(m.actualBoundingBoxDescent) + pad;
      const cw = (bl + br) * q, chh = (ba + bd) * q;
      const cv = document.createElement('canvas'); cv.width = cw; cv.height = chh;
      const cx = cv.getContext('2d', { willReadFrequently: true });
      cx.font = font(size * q); cx.fillStyle = color; cx.fillText(ch, bl * q, ba * q);
      const data = cx.getImageData(0, 0, cw, chh).data, bin = new Uint8Array(cw * chh);
      for (let p = 0; p < cw * chh; p++) bin[p] = data[p * 4 + 3] > 110 ? 1 : 0;
      const strokes = WBTrace.trace(bin, cw, chh, { eps: 0.6, minLen: q * 2, startAt: [0, 0] });
      const gx = x - bl, gy = base - ba;
      const mid = `tm${uid++}`;
      const mask = mk('mask', { id: mid, maskUnits: 'userSpaceOnUse', x: gx - 2, y: gy - 2, width: cw / q + 4, height: chh / q + 4 }, $('defs'));
      const resid = mk('rect', { x: gx, y: gy, width: cw / q, height: chh / q, fill: '#fff', opacity: 0 }, mask);
      const img = mk('image', { x: gx, y: gy, width: cw / q, height: chh / q, preserveAspectRatio: 'none' }, tg);
      img.setAttribute('href', cv.toDataURL('image/png'));
      img.setAttribute('mask', `url(#${mid})`);
      img.style.visibility = 'hidden';
      try { await img.decode(); } catch (_) { /* older Chrome */ }
      const L = { img, mid, resid, events: [] };
      for (const st of strokes) {
        const P = st.pts;
        let d = `M${(gx + P[0] / q).toFixed(2)} ${(gy + P[1] / q).toFixed(2)}`;
        for (let k = 2; k < P.length; k += 2) d += `L${(gx + P[k] / q).toFixed(2)} ${(gy + P[k + 1] / q).toFixed(2)}`;
        const p = mk('path', { d, fill: 'none', stroke: '#fff', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, mask);
        p.setAttribute('stroke-width', (2 * st.r / q + 1.8).toFixed(2));
        const ev = strokeEvent(p, ID);
        ev.kind = 'mstroke'; ev.letter = L;
        L.events.push(ev); item.events.push(ev);
      }
      if (!L.events.length) { img.removeAttribute('mask'); continue; }
      item.letters.push(L);
    }
    return item;
  }

  // ---------------------------------------------------------------- timing
  // pen events go through the hand queue; "self" events (class hatch) draw themselves (scheduleSelf)
  const isPen = (e) => !e.self && (e.kind === 'stroke' || e.kind === 'mstroke' || e.kind === 'fill');
  const isHand = isPen; // every pen mark on the board is made under the marker tip
  // Steady pen speed (default 2200 px/s, or whatever fits the scene's "draw" seconds).
  // Between paths the hand lifts, moves (eased) and lands: a pause of 0.15 s plus the
  // travel time at 2.6x pen speed. Handwriting strokes use a shorter 0.06 s pause.
  const K_MOVE = 2.6;
  function penStats(item) {
    const pen = item.events.filter(isPen);
    let L = 0, Dm = 0, prev = null;
    for (const e of pen) {
      L += Math.max(e.lenF, 3);
      if (prev) Dm += Math.hypot(e.p0[0] - prev.p1[0], e.p0[1] - prev.p1[1]);
      prev = e;
    }
    const pause = item.kind === 'text' ? (OPT.letterPause != null ? OPT.letterPause : 0.06) : (OPT.pathPause != null ? OPT.pathPause : 0.15);
    return { pen, L, Dm, n: Math.max(0, pen.length - 1), pause };
  }
  // Native SVG art: the hand traces every "line" and "detail" path in document order, so none of
  // them appears without the marker tip on it. "detail" strokes are drawn faster (1.8x) with quick
  // hops (0.04 s) between them; colour scribbles fast too. With a "draw" budget the pen speeds up to
  // fit (up to ART_VMAX; beyond that pauses shrink and the speed may reach ART_VHARD, with a warning).
  // "hatch" strokes are not in the hand queue at all: see scheduleSelf.
  // Tunable per timeline: options.detailSpeed / detailPause / hatchDraw / hatchStep.
  const ART_VMAX = 4000, ART_VMIN = 1300, ART_VHARD = 5600;
  const SPEEDK = { line: 1, detail: 1.8, scribble: 1.9 };
  const PAUSE = { detail: 0.04, scribble: 0.08 };
  const speedOf = (cls) => (cls === 'detail' && OPT.detailSpeed != null ? OPT.detailSpeed : SPEEDK[cls] || 1);
  const pauseOf = (e) => (e.cls === 'detail' ? (OPT.detailPause != null ? OPT.detailPause : PAUSE.detail)
    : e.cls === 'scribble' ? PAUSE.scribble : (OPT.pathPause != null ? OPT.pathPause : 0.15));
  // Hatching self-draws once the item's last line/detail stroke is done (partEnd): stroke i starts at
  // partEnd + i * min(0.012, 0.35 / n) and draws over 0.35 s (dash offset), so all of it takes <= 0.7 s.
  // It needs no hand, so it may overlap the next part or text.
  const HATCH_DRAW = 0.35, HATCH_STEP = 0.012, HATCH_SPREAD = 0.35;
  function scheduleSelf(item, at) {
    const hs = item.events.filter((e) => e.self);
    item.hatches = hs.length; item.hatchEnd = null;
    if (!hs.length) return;
    const draw = OPT.hatchDraw != null ? OPT.hatchDraw : HATCH_DRAW;
    const step = Math.min(OPT.hatchStep != null ? OPT.hatchStep : HATCH_STEP, HATCH_SPREAD / hs.length);
    hs.forEach((e, i) => { e.ts = at + i * step; e.te = e.ts + draw; });
    item.hatchEnd = hs[hs.length - 1].te;
  }
  function simulateArt(item, v, apply, start, pk) {
    pk = pk || 1;
    let t = start, lastEnd = start, prev = null;
    for (const e of item.events) {
      if (!isPen(e)) { if (apply) e.ts = e.te = lastEnd; continue; }
      const len = Math.max(e.lenF, 3), vv = v * speedOf(e.cls);
      if (prev) {
        const d = Math.hypot(e.p0[0] - prev.p1[0], e.p0[1] - prev.p1[1]);
        // short hops inside a figure are quick; long moves lift and glide
        const mt = d / (K_MOVE * v) + pauseOf(e) * pk * clamp(0.35 + d / 250, 0.35, 1);
        if (apply) { e.moveFrom = prev.p1; e.moveT = mt; }
        t += mt;
      }
      const te = t + len / vv;
      if (apply) { e.ts = t; e.te = te; }
      t = lastEnd = te; prev = e;
    }
    return t - start;
  }
  function scheduleArt(item, start, D) {
    const pen = item.events.filter(isPen);
    let v = OPT.penSpeed || 2200, pk = 1;
    item.over = 0;
    if (D != null) {
      const fits = (vv, kk) => simulateArt(item, vv, false, 0, kk) <= D + 1e-6;
      const search = (lo, hi, kk) => { for (let k = 0; k < 30; k++) { const mid = (lo + hi) / 2; if (fits(mid, kk)) hi = mid; else lo = mid; } return hi; };
      if (fits(ART_VMIN, 1)) v = ART_VMIN;
      else if (fits(ART_VMAX, 1)) v = search(ART_VMIN, ART_VMAX, 1);
      else {
        pk = 0.5;
        if (fits(ART_VMAX, pk)) v = search(ART_VMIN, ART_VMAX, pk);
        else if (fits(ART_VHARD, pk)) v = search(ART_VMAX, ART_VHARD, pk);
        else { v = ART_VHARD; item.over = simulateArt(item, v, false, 0, pk) / D; }
      }
    }
    const dur = simulateArt(item, v, true, start, pk);
    item.start = start; item.end = start + dur; item.speed = v;
    scheduleSelf(item, item.end);
    item.lines = pen.length; item.details = 0;
    item.penLen = pen.reduce((a, e) => a + e.lenF, 0);
    item.p0 = pen.length ? pen[0].p0 : null; item.p1 = pen.length ? pen[pen.length - 1].p1 : null;
    return item.end;
  }
  function naturalDur(item) {
    if (item.kind === 'art' && item.mode === 'native') return simulateArt(item, OPT.penSpeed || 2200, false, 0, 1);
    const st = penStats(item), v = OPT.penSpeed || 2200;
    return (st.L + st.Dm / K_MOVE) / v + st.n * st.pause;
  }
  function scheduleItem(item, start, D) {
    if (item.kind === 'art' && item.mode === 'native') return scheduleArt(item, start, D);
    const { pen, L, Dm, n, pause } = penStats(item);
    let v, p;
    if (D == null) { v = OPT.penSpeed || 2200; p = pause; }
    else { p = Math.min(pause, (0.5 * D) / Math.max(1, n)); v = (L + Dm / K_MOVE) / Math.max(0.25 * D, D - n * p); }
    let t = start, prev = null;
    for (const e of item.events) {
      if (!isPen(e)) { e.ts = e.te = t; continue; }
      if (prev) {
        const d = Math.hypot(e.p0[0] - prev.p1[0], e.p0[1] - prev.p1[1]);
        e.moveFrom = prev.p1; e.moveT = d / (K_MOVE * v) + p; t += e.moveT;
      }
      e.ts = t; e.te = t + Math.max(e.lenF, 3) / v; t = e.te; prev = e;
    }
    for (const Lt of item.letters || []) { Lt.ts = Lt.events[0].ts; Lt.te = Lt.events[Lt.events.length - 1].te; }
    item.start = start; item.end = t; item.speed = v;
    const first = pen[0], last = pen[pen.length - 1];
    item.p0 = first ? first.p0 : null; item.p1 = last ? last.p1 : null;
    return t;
  }

  function scheduleScenes(timelineEnd) {
    scenes.forEach((S, i) => {
      const prev = scenes[i - 1];
      S.panDur = S.pan != null ? S.pan : 1.2;
      S.panStart = i === 0 ? -1e9 : S.t0 - (S.panLead != null ? S.panLead : 0.55);
      if (S.camera === 'hold') S.panDur = 0.9;
      S.panDip = S.camera === 'hold' ? 0 : (S.dip != null ? S.dip : 0.075);
      if (prev) S.panStart = Math.max(S.panStart, prev.t0 + 0.2);
    });
    scenes.forEach((S, i) => {
      const next = scenes[i + 1];
      S.drawStart = S.t0 + (S.lead != null ? S.lead : (i === 0 ? 0.45 : 0.3));
      const limit = (next ? next.panStart : timelineEnd) - 0.75; // leave time for the hand to leave
      S.limit = limit;
      for (const it of S.items) { it.natural = naturalDur(it); it.Dwant = it.D || it.natural; }
      // items run one after another; text items may carry their own start offset "t"
      const plan = () => {
        let t = S.drawStart, prevItem = null;
        for (const it of S.items) {
          if (prevItem && prevItem.p1 && it.events.some(isHand)) {
            const first = it.events.find(isHand);
            const d = Math.hypot(first.p0[0] - prevItem.p1[0], first.p0[1] - prevItem.p1[1]);
            it.gap = clamp(0.25 + d / 2600, 0.3, 0.75);
          } else it.gap = prevItem ? 0.2 : 0;
          let st = t + it.gap;
          if (it.at != null) st = Math.max(st, S.t0 + it.at);
          // a part must be finished before the next timed part starts
          const k = S.items.indexOf(it), nx = S.items.slice(k + 1).find((x) => x.at != null);
          let D = it.Dscaled || it.D || null;
          // the item's window (for --plan): from its start until the next timed item, else the scene limit
          it.winStart = st; it.winEnd = nx ? Math.min(limit, S.t0 + nx.at - 0.35) : limit;
          if (nx) {
            const slot = Math.max(0.4, S.t0 + nx.at - st - 0.35), want = D || it.Dwant;
            if (want > slot) { D = slot; if (!it._slotWarned) { it._slotWarned = 1; if (it.Dwant / slot > 1.6) warn(`scene ${S.id}: part ${k + 1} needs ${it.Dwant.toFixed(1)}s but has ${slot.toFixed(1)}s before the next part; it is sped up`); } }
          }
          t = scheduleItem(it, st, D);
          prevItem = it;
        }
        return t;
      };
      let end = plan();
      if (end > limit && S.items.length) {
        const avail = Math.max(0.6, limit - S.drawStart - S.items.reduce((a, it) => a + (it.gap || 0), 0));
        const want = S.items.reduce((a, it) => a + it.Dwant, 0);
        let k = Math.min(1, avail / want);
        // items with a timed start ("at"/"t") cannot move earlier, so one proportional pass can still
        // overrun: tighten k until the scene fits (or nothing can go faster)
        for (let pass = 0; pass < 8; pass++) {
          S.items.forEach((it) => { it.Dscaled = it.Dwant * k; });
          const prevEnd = end;
          end = plan();
          if (end <= limit + 0.01 || Math.abs(prevEnd - end) < 0.005) break;
          k *= Math.max(0.5, (limit - S.drawStart) / Math.max(0.01, end - S.drawStart));
        }
        warn(`scene ${S.id}: drawing squeezed to ${(k * 100).toFixed(0)}% to finish before the next scene`);
      }
      S.drawEnd = end;
      S.window = limit - S.drawStart;
      // fastest possible hand time for each art item (max pen speed, halved pauses), for --plan
      for (const it of S.items) it.fast = it.kind === 'art' && it.mode === 'native' ? simulateArt(it, ART_VHARD, false, 0, 0.5) : null;
      if (end > limit + 0.05) warn(`OVER BUDGET scene ${S.id}: drawing ends at ${end.toFixed(2)}s but must end by ${limit.toFixed(2)}s; simplify the art (fewer/shorter strokes)`);
      for (const it of S.items) if (it.over > 1) warn(`OVER BUDGET scene ${S.id}: art needs ${(it.over * 100).toFixed(0)}% of its time even at ${ART_VHARD}px/s`);
      const art = S.items.find((it) => it.kind === 'art');
      S.artEnd = art ? art.end : S.drawStart;
      for (const it of S.items) {
        const accStart = it.end + 0.1;
        it.accStart = accStart; it.accDur = S.accentFade || 1.0;
      }
      buildPenSegments(S, next);
      S.pushStart = S.drawStart;
      S.pushEnd = next ? next.panStart + next.panDur * 0.5 : timelineEnd;
      S.push = S.pushAmount != null ? S.pushAmount : Math.min(0.045, 0.0042 * Math.max(0, S.pushEnd - S.pushStart));
      const boxes = S.items.map((it) => it.box).filter(Boolean);
      if (boxes.length) {
        const x0 = Math.min(...boxes.map((b) => b[0])), y0 = Math.min(...boxes.map((b) => b[1]));
        const x1 = Math.max(...boxes.map((b) => b[0] + b[2])), y1 = Math.max(...boxes.map((b) => b[1] + b[3]));
        S.focus = [(x0 + x1) / 2, (y0 + y1) / 2];
      } else S.focus = [W / 2, H / 2];
    });
  }

  function buildPenSegments(S) {
    const segs = [];
    const ENTER = 0.55, EXIT = 0.65;
    let last = null;
    for (const it of S.items) {
      for (const e of it.events) {
        if (!isHand(e)) continue;
        if (!last) segs.push({ type: 'enter', a: e.ts - ENTER, b: e.ts, to: e.p0 });
        else if (e.ts > last.te + 1e-6) segs.push({ type: 'move', a: last.te, b: e.ts, from: last.p1, to: e.p0 });
        segs.push({ type: 'draw', a: e.ts, b: e.te, ev: e });
        last = e;
      }
    }
    if (last) segs.push({ type: 'exit', a: last.te, b: last.te + EXIT, from: last.p1 });
    S.segs = segs;
    S.penStart = segs.length ? segs[0].a : Infinity;
    S.penEnd = segs.length ? segs[segs.length - 1].b : -Infinity;
  }

  // ---------------------------------------------------------------- pen
  function pointOn(e, p) {
    if (e.len < 0.01) return e.p0;
    const P = e.el.getPointAtLength(clamp(p, 0, 1) * e.len);
    return apply(e.M, P.x, P.y);
  }
  function penState(S, t) {
    const sg = S.segs;
    if (!sg.length || t < sg[0].a || t > sg[sg.length - 1].b) return null;
    let lo = 0, hi = sg.length - 1;
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (sg[mid].a <= t) lo = mid; else hi = mid - 1; }
    const s = sg[lo], u = s.b > s.a ? clamp((t - s.a) / (s.b - s.a), 0, 1) : 1;
    if (s.type === 'draw') return { pt: pointOn(s.ev, u), lift: 0 };
    if (s.type === 'move') {
      // lift first, glide with ease-in-out, then land on the new path
      const w = smoother((u - 0.12) / 0.76), d = Math.hypot(s.to[0] - s.from[0], s.to[1] - s.from[1]);
      const lift = Math.min(smooth(u / 0.3), smooth((1 - u) / 0.3)) * clamp(0.3 + d / 160, 0.3, 1);
      return { pt: [lerp(s.from[0], s.to[0], w), lerp(s.from[1], s.to[1], w)], lift };
    }
    if (s.type === 'enter') return { enter: true, u, pt: s.to };
    return { exit: true, u, pt: s.from };
  }
  function penFrame(S, t) {
    if (!S.segs.length) return S.focus;
    if (t <= S.segs[0].a) return S.segs[0].to;
    const st = penState(S, t);
    return st ? st.pt : S.segs[S.segs.length - 1].from;
  }

  // ---------------------------------------------------------------- camera
  function camScene(S, t) {
    const F = S.frame;
    let s = 1 + S.push * easeSine((t - S.pushStart) / Math.max(0.01, S.pushEnd - S.pushStart));
    const P = [F[0] + S.focus[0], F[1] + S.focus[1]], C0 = [F[0] + W / 2, F[1] + H / 2];
    let cx = P[0] + (C0[0] - P[0]) / s, cy = P[1] + (C0[1] - P[1]) / s;
    if (S.camera === 'zoom') {
      const e = 1 - smoother((t - (S.artEnd - 0.15)) / 1.6);
      if (e > 0) {
        // follow a heavily smoothed pen position (window average, so it is stateless and jitter-free)
        let sx = 0, sy = 0, sw = 0;
        for (let k = -6; k <= 6; k++) {
          const w = 7 - Math.abs(k), p = penFrame(S, Math.min(t + k * 0.15, S.artEnd));
          sx += p[0] * w; sy += p[1] * w; sw += w;
        }
        const z = s * lerp(1, S.zoomLevel || 1.35, e);
        const hw = W / (2 * z), hh = H / (2 * z);
        const tx = clamp(F[0] + sx / sw, F[0] + hw, F[0] + W - hw), ty = clamp(F[1] + sy / sw, F[1] + hh, F[1] + H - hh);
        cx = lerp(cx, tx, e); cy = lerp(cy, ty, e); s = z;
      }
    }
    return { cx, cy, s };
  }
  function camAt(t) {
    let i = 0;
    for (let k = 1; k < scenes.length; k++) if (t >= scenes[k].panStart) i = k;
    const S = scenes[i];
    let c = camScene(S, t);
    if (i > 0 && t < S.panStart + S.panDur) {
      const u = (t - S.panStart) / S.panDur, w = smoother(u), a = camScene(scenes[i - 1], t);
      const dist = Math.hypot(c.cx - a.cx, c.cy - a.cy) / W;
      const dip = S.panDip * clamp(dist, 0, 1.5) * Math.pow(Math.sin(Math.PI * u), 2);
      c = { cx: lerp(a.cx, c.cx, w), cy: lerp(a.cy, c.cy, w), s: Math.exp(lerp(Math.log(a.s), Math.log(c.s), w)) * (1 - dip) };
    }
    return c;
  }
  const toScreen = (S, p, c) => [(S.frame[0] + p[0] - c.cx) * c.s + W / 2, (S.frame[1] + p[1] - c.cy) * c.s + H / 2];

  // ---------------------------------------------------------------- state per frame
  function applyStroke(e, t) {
    const el = e.el;
    if (t < e.ts) {
      if (e._k !== 'h') { e._k = 'h'; el.style.visibility = 'hidden'; }
    } else if (t < e.te && e.len >= 0.01) {
      const p = (t - e.ts) / (e.te - e.ts);
      if (e._k !== 'p') {
        e._k = 'p'; el.style.visibility = 'visible';
        el.style.strokeDasharray = `${e.len} ${e.len + 2}`;
        if (e.kind === 'fill') { el.style.stroke = e.color; el.style.strokeWidth = String(e.sw); }
      }
      el.style.strokeDashoffset = String(e.len * (1 - p));
      if (e.kind === 'fill') el.style.fillOpacity = String(e.fo * smooth((t - e.ts) / (e.te - e.ts + 0.25)));
    } else if (e._k !== 'd' || (e.kind === 'fill' && t < e.te + 0.3)) {
      e._k = 'd'; el.style.visibility = 'visible';
      el.style.strokeDasharray = e.kind === 'fill' ? 'none' : e.dash0; el.style.strokeDashoffset = e.off0;
      if (e.kind === 'fill') {
        el.style.stroke = e.color; el.style.strokeWidth = String(e.sw);
        el.style.fillOpacity = String(e.fo * smooth((t - e.ts) / (e.te - e.ts + 0.25)));
      }
    }
    if (e.fillTarget) {
      const a = t < e.te ? 0 : smooth((t - e.te) / FILL_FADE);
      const k = a >= 1 ? 'F' : a <= 0 ? 'Z' : 'f';
      if (k === 'f' || e._fk !== k) {
        e._fk = k;
        e.fillTarget.style.fillOpacity = String(e.fo * a);
        if (!e.ownFill) e.fillTarget.style.visibility = a > 0 ? 'visible' : 'hidden';
      }
    }
  }
  function applyItem(it, t) {
    for (const e of it.events) {
      if (e.kind === 'stroke' || e.kind === 'fill' || e.kind === 'mstroke') {
        applyStroke(e, t);
        const R = e.reveal;
        if (R) {
          const a = t < e.te ? 0 : smooth((t - e.te) / 0.25), k = a >= 1 ? 'D' : a <= 0 ? 'Z' : 'f';
          if (k === 'f' || R._k !== k) {
            R._k = k; R.resid.setAttribute('opacity', String(a));
            R.target.style.setProperty('mask', k === 'D' ? 'none' : `url(#${R.id})`);
          }
        }
      }
      else if (e.kind === 'instant') { const k = t >= e.ts ? 'v' : 'h'; if (e._k !== k) { e._k = k; e.el.style.visibility = k === 'v' ? 'visible' : 'hidden'; } }
      else if (e.kind === 'fade') {
        const a = smooth((t - e.ts) / 0.35), k = a >= 1 ? 'F' : a <= 0 ? 'Z' : 'f';
        if (k === 'f' || e._k !== k) { e._k = k; e.el.style.opacity = String(e.o * a); e.el.style.visibility = a > 0 ? 'visible' : 'hidden'; }
      }
    }
    for (const L of it.letters || []) {
      const k = t < L.ts ? 'h' : t < L.te + RESIDUAL ? 'm' : 'd';
      if (k === 'm') L.resid.setAttribute('opacity', String(smooth((t - L.te) / RESIDUAL)));
      if (L._k !== k) {
        L._k = k;
        L.img.style.visibility = k === 'h' ? 'hidden' : 'visible';
        if (k === 'd') L.img.removeAttribute('mask'); else L.img.setAttribute('mask', `url(#${L.mid})`);
      }
    }
    for (const A of it.accents || []) {
      const a = smooth((t - it.accStart) / it.accDur), k = a >= 1 ? 'F' : a <= 0 ? 'Z' : 'f';
      if (k === 'f' || A._k !== k) { A._k = k; A.el.style.opacity = String(A.o * a); A.el.style.visibility = a > 0 ? 'visible' : 'hidden'; }
    }
  }

  // ---------------------------------------------------------------- hand
  function markerSVG() {
    // Clean vector whiteboard marker; tip at (0,0), barrel along +x.
    return `
    <defs>
      <linearGradient id="mkBody" x1="0" y1="-23" x2="0" y2="23" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#2a2a2c"/><stop offset="0.22" stop-color="#5b5b60"/><stop offset="0.38" stop-color="#232325"/>
        <stop offset="0.8" stop-color="#0e0e0f"/><stop offset="1" stop-color="#1b1b1c"/>
      </linearGradient>
      <linearGradient id="mkCone" x1="0" y1="-18" x2="0" y2="18" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#3a3a3d"/><stop offset="0.3" stop-color="#6a6a70"/><stop offset="0.55" stop-color="#26262a"/><stop offset="1" stop-color="#111"/>
      </linearGradient>
      <linearGradient id="mkNib" x1="0" y1="-6" x2="0" y2="6" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#2a2a2a"/><stop offset="0.4" stop-color="#4a4a4a"/><stop offset="1" stop-color="#151515"/>
      </linearGradient>
    </defs>
    <path d="M0 0 C1.5 -3.2 5 -5.6 11 -6.2 L19 -6.6 L19 6.6 L11 6.2 C5 5.6 1.5 3.2 0 0 Z" fill="url(#mkNib)"/>
    <path d="M18 -7.2 L54 -17.5 L54 17.5 L18 7.2 Z" fill="url(#mkCone)"/>
    <rect x="52" y="-19.5" width="13" height="39" rx="2.5" fill="#303033"/>
    <rect x="63" y="-21.5" width="372" height="43" rx="7" fill="url(#mkBody)"/>
    <rect x="96" y="-21.5" width="7" height="43" fill="#3c3c40" opacity="0.8"/>
    <rect x="430" y="-23" width="104" height="46" rx="11" fill="url(#mkBody)"/>
    <rect x="428" y="-23" width="8" height="46" rx="2" fill="#3a3a3e"/>
    <rect x="446" y="-29" width="82" height="8" rx="4" fill="#161617"/>
    <rect x="70" y="-15" width="356" height="3.2" rx="1.6" fill="#ffffff" opacity="0.2"/>
    <rect x="440" y="-16" width="86" height="3" rx="1.5" fill="#ffffff" opacity="0.16"/>`;
  }
  let FPS = 30;
  function setupHand(h) {
    const content = $('handContent'), layer = $('handLayer');
    $('handwrap').style.display = 'block'; // measuring needs a rendered tree
    $('handsvg').setAttribute('width', W); $('handsvg').setAttribute('height', H);
    const tmp = mk('g', {}, layer);
    HAND = null;
    if (h && h.symbolSvg) {
      // kit symbol, e.g. "hand-marker"; tip in the symbol's own coordinates
      const doc = parseSVG(h.symbolSvg, 'hand kit');
      const sym = byId(doc.documentElement, h.symbol);
      if (sym) {
        const holder = doc.createElementNS(NS, 'g');
        const use = doc.createElementNS(NS, 'use');
        use.setAttribute('href', '#' + h.symbol);
        holder.appendChild(use); doc.documentElement.appendChild(holder);
        const kitSave = KITS; KITS = [{ name: 'hand', doc }];
        flattenUses(holder, new Set());
        KITS = kitSave;
        const vb = vbOf(sym) || [0, 0, 100, 100];
        for (const st of doc.querySelectorAll('style')) tmp.appendChild(document.importNode(st, true));
        for (const d of doc.querySelectorAll('defs')) { const c = document.importNode(d, true); c.querySelectorAll('symbol').forEach((x) => x.remove()); if (c.childElementCount) tmp.appendChild(c); }
        for (const c of Array.from(holder.childNodes)) tmp.appendChild(document.importNode(c, true));
        let tip = h.tip;
        if (!tip) {
          const tipEl = byId(tmp, h.tipId || 'tip') || tmp.querySelector('[id*="tip"]');
          if (tipEl) { const bb = tipEl.getBBox(); tip = [bb.x + bb.width / 2, bb.y + bb.height / 2]; tipEl.style.display = 'none'; }
        }
        if (!tip) { warn(`hand symbol "${h.symbol}" has no tip coordinates; using the marker`); tmp.innerHTML = ''; }
        else {
          bakeStyles(tmp);
          HAND = { kind: 'symbol', tip, angle: h.angle || 0, scale: h.scale || (h.height ? h.height / vb[3] : (1.15 * 1100 / vb[3]) * (H / 1080)) };
        }
      } else warn(`hand symbol "${h.symbol}" not found in kit; using the marker`);
    }
    if (!HAND && h && h.image) {
      const im = mk('image', { x: 0, y: 0, width: h.size[0], height: h.size[1] }, tmp);
      im.setAttribute('href', h.image);
      HAND = { kind: 'image', tip: h.tip || [0, 0], angle: h.angle || 0, scale: h.scale || 1, follow: h.follow };
    }
    if (!HAND) {
      tmp.innerHTML = markerSVG();
      HAND = { kind: 'marker', tip: [0, 0], angle: h && h.angle != null ? h.angle : 57, scale: (h && h.scale) || 1 };
    }
    while (tmp.firstChild) content.appendChild(tmp.firstChild);
    tmp.remove();
    HAND.use = mk('use', { href: '#handContent' }, $('handLayer'));
    $('handwrap').style.display = 'none';
  }
  // Where the hand is at time t (screen px) and how high it is lifted (0 = pen on the board).
  function handPose(t) {
    let st = null, S = null;
    for (const sc of scenes) if (t >= sc.penStart && t <= sc.penEnd) { st = penState(sc, t); S = sc; if (st) break; }
    if (!st) return null;
    const OFF = [W * 0.9 + 420, H + 460];
    const P = toScreen(S, st.pt, camAt(t));
    let x = P[0], y = P[1], lift = st.lift || 0;
    if (st.enter) { const w = easeOut(st.u); x = lerp(OFF[0], P[0], w); y = lerp(OFF[1], P[1], w); lift = 1 - smooth((st.u - 0.55) / 0.45); }
    if (st.exit) { const w = easeIn(clamp((st.u - 0.08) / 0.92, 0, 1)); x = lerp(P[0], OFF[0], w); y = lerp(P[1], OFF[1], w); lift = smooth(st.u / 0.3); }
    return { x, y, lift };
  }
  // The hand is drawn crisp (no motion blur), above everything, with a soft drop shadow
  // that grows when the pen is lifted.
  function renderHand(t) {
    const wrap = $('handwrap');
    const c = handPose(t);
    if (!c) { if (wrap.style.display !== 'none') wrap.style.display = 'none'; return null; }
    // the forearm swings from an elbow below the lower-right corner, so it turns as the hand reaches
    const PIV = [W * 1.04, H * 1.6];
    const aRef = Math.atan2(H / 2 - PIV[1], W / 2 - PIV[0]), aNow = Math.atan2(c.y - PIV[1], c.x - PIV[0]);
    const ang = HAND.angle + ((aNow - aRef) * 180 / Math.PI) * (HAND.follow != null ? HAND.follow : 0.5);
    const sc = HAND.scale * (1 + 0.035 * c.lift);
    HAND.use.setAttribute('transform', `translate(${c.x.toFixed(2)} ${c.y.toFixed(2)}) rotate(${ang.toFixed(3)}) scale(${sc.toFixed(4)}) translate(${-HAND.tip[0]} ${-HAND.tip[1]})`);
    const dr = $('handDrop'), L = c.lift;
    dr.setAttribute('dx', (9 + 20 * L).toFixed(1)); dr.setAttribute('dy', (13 + 28 * L).toFixed(1));
    dr.setAttribute('stdDeviation', ((7 + 12 * L) / 2).toFixed(2)); dr.setAttribute('flood-opacity', (0.22 - 0.07 * L).toFixed(3));
    if (wrap.style.display !== 'block') wrap.style.display = 'block';
    return [c.x, c.y];
  }

  // ---------------------------------------------------------------- captions
  const CAP = { family: '"Avenir Next", "Inter", "Helvetica Neue", sans-serif', weight: 500, size: 40, lineH: 1.32, maxW: 1380, padX: 30, padY: 15, bottom: 58 };
  function buildCaptions(list, style) {
    Object.assign(CAP, style || {});
    const ctx = document.createElement('canvas').getContext('2d');
    ctx.font = `${CAP.weight} ${CAP.size}px ${CAP.family}`;
    const wid = (s) => ctx.measureText(s).width;
    const wrap = (words) => {
      const lines = []; let cur = '';
      for (const w of words) { const tr = cur ? cur + ' ' + w : w; if (wid(tr) > CAP.maxW && cur) { lines.push(cur); cur = w; } else cur = tr; }
      if (cur) lines.push(cur);
      return lines;
    };
    const balance = (words) => {
      const one = words.join(' ');
      if (wid(one) <= CAP.maxW) return [one];
      let best = null, bw = Infinity;
      for (let k = 1; k < words.length; k++) {
        const a = words.slice(0, k).join(' '), b = words.slice(k).join(' ');
        const m = Math.max(wid(a), wid(b)) - (/[,;:.!?]$/.test(words[k - 1]) ? 40 : 0);
        if (wid(a) <= CAP.maxW && wid(b) <= CAP.maxW && m < bw) { bw = m; best = [a, b]; }
      }
      return best || wrap(words);
    };
    const parts = [];
    for (const c of list) {
      const words = String(c.text).trim().split(/\s+/);
      let P = Math.ceil(wrap(words).length / 2), chunks = null;
      for (; P <= words.length; P++) {
        chunks = splitWords(words, P);
        if (chunks.every((ch) => balance(ch).length <= 2)) break;
      }
      const total = chunks.reduce((a, ch) => a + ch.join(' ').length, 0);
      let t = c.t0;
      for (const ch of chunks) {
        const d = ((c.t1 - c.t0) * ch.join(' ').length) / total;
        const lines = balance(ch);
        const w = Math.max(...lines.map(wid)) + 2 * CAP.padX, h = lines.length * CAP.size * CAP.lineH + 2 * CAP.padY;
        parts.push({ a: t, b: t + d, lines, w, h });
        t += d;
      }
    }
    parts.sort((p, q) => p.a - q.a);
    parts.forEach((p, i) => { p.prev = parts[i - 1]; p.next = parts[i + 1]; });
    return parts;
  }
  // split words into P parts of similar length, preferring breaks after punctuation
  function splitWords(words, P) {
    if (P <= 1) return [words];
    const lens = words.map((w) => w.length + 1), total = lens.reduce((a, b) => a + b, 0);
    const cuts = []; let acc = 0, k = 0;
    const cum = lens.map((l) => (acc += l));
    for (let p = 1; p < P; p++) {
      const target = (total * p) / P;
      let best = -1, bs = -Infinity;
      for (let i = Math.max(k + 1, 1); i < words.length - (P - p) + 1; i++) {
        const dist = Math.abs(cum[i - 1] - target) / total;
        const punct = /[.!?]$/.test(words[i - 1]) ? 0.16 : /[,;:]$/.test(words[i - 1]) ? 0.1 : 0;
        const s = punct - dist;
        if (s > bs) { bs = s; best = i; }
      }
      cuts.push(best); k = best;
    }
    const out = []; let s = 0;
    for (const c of cuts) { out.push(words.slice(s, c)); s = c; }
    out.push(words.slice(s));
    return out.filter((x) => x.length);
  }
  // Back-to-back parts swap text at the midpoint of their gap with a quick dip; the band
  // only fades at the start and end of a run and eases its size between parts.
  function renderCaption(t) {
    const band = $('capband'), txt = $('captext');
    const GAP = 0.35, close = (x, y) => !!(x && y && y.a - x.b < GAP);
    const startOf = (p) => (close(p.prev, p) ? (p.prev.b + p.a) / 2 : p.a);
    let P = null;
    for (const p of capParts) { if (startOf(p) <= t) P = p; else break; }
    const hide = () => { if (band.style.display !== 'none') band.style.display = 'none'; };
    if (!P) return hide();
    const linked = close(P, P.next);
    if (!linked && t > P.b + 0.25) return hide();
    const st = startOf(P), en = linked ? (P.b + P.next.a) / 2 : P.b;
    const fin = close(P.prev, P) ? 0.09 : 0.12, fout = linked ? 0.09 : 0.12;
    const ta = Math.min(smooth((t - st) / fin), linked ? 1 - smooth((t - (en - fout)) / fout) : 1 - smooth((t - P.b) / fout));
    const inA = close(P.prev, P) ? 1 : smooth((t - P.a) / 0.18);
    const outA = linked ? 1 : 1 - smooth((t - P.b) / 0.22);
    let w = P.w, h = P.h;
    if (close(P.prev, P)) { const u = smoother((t - st) / 0.2); w = lerp(P.prev.w, P.w, u); h = lerp(P.prev.h, P.h, u); }
    band.style.display = 'block';
    band.style.width = w.toFixed(1) + 'px'; band.style.height = h.toFixed(1) + 'px';
    band.style.transform = `translate(${((W - w) / 2).toFixed(1)}px, ${(H - CAP.bottom - h).toFixed(1)}px)`;
    band.style.opacity = String(Math.min(inA, outA));
    const key = P.lines.join('\n');
    if (txt._key !== key) { txt._key = key; txt.innerHTML = ''; for (const l of P.lines) { const d = document.createElement('div'); d.textContent = l; txt.appendChild(d); } }
    txt.style.opacity = String(Math.max(0, ta));
  }

  // ---------------------------------------------------------------- public API
  window.loadJob = async function (job) {
    W = job.width || 1920; H = job.height || 1080; INK = job.ink || INK; FPS = job.fps || 30;
    SAFE_BOTTOM = job.safeBottom !== undefined ? job.safeBottom : Math.round(H * 860 / 1080);
    Object.assign(OPT, job.options || {});
    const stage = $('stage');
    stage.style.width = W + 'px'; stage.style.height = H + 'px';
    const board = $('board'); board.setAttribute('width', W); board.setAttribute('height', H);
    document.body.style.background = (job.board && job.board.color) || '#fbfaf7';
    const vig = job.board && job.board.vignette != null ? job.board.vignette : 0.07;
    $('vignette').style.background = `radial-gradient(ellipse 75% 70% at 50% 48%, rgba(70,56,40,0) 55%, rgba(70,56,40,${vig}) 100%)`;
    await loadFonts(job.fonts);
    const cf = $('captext');
    cf.style.fontFamily = CAP.family; cf.style.fontWeight = CAP.weight;
    await document.fonts.load(`${CAP.weight} ${CAP.size}px "Avenir Next"`);
    KITS = (job.kits || []).map((k) => ({ name: k.name, doc: parseSVG(k.text, `kit ${k.name}`) }));
    const frames = layoutFrames(job.scenes);
    scenes = [];
    for (let i = 0; i < job.scenes.length; i++) {
      const sc = job.scenes[i];
      const S = Object.assign({}, sc, { idx: i, frame: frames[i], items: [] });
      S.g = mk('g', { class: 'scene', 'data-id': sc.id || i, transform: `translate(${frames[i][0]} ${frames[i][1]})` }, $('cam'));
      if (sc.svg || sc.missing) S.items.push(await buildArt(S, sc));
      // "parts": several drawings on the same board, each starting at its own time (seconds after t0)
      for (const p of sc.parts || []) {
        const it = await buildArt(S, Object.assign({}, sc, { svg: p.svg, box: p.box || sc.box, draw: p.draw, artAt: p.at != null ? p.at : null, mode: p.mode, id: `${sc.id}/${p.id || S.items.length + 1}`, file: p.file, missing: !!p.missing }));
        S.items.push(it);
      }
      for (const t of sc.text || []) S.items.push(await buildText(S, t));
      // items with an explicit start ("t" on text, "artAt" on the art) are drawn in time order
      let last = -Infinity;
      const keyed = S.items.map((it) => { const key = it.at != null ? it.at : last; last = key; return { it, key }; });
      S.items = keyed.sort((a, b) => a.key - b.key).map((k) => k.it);
      scenes.push(S);
    }
    scheduleScenes(job.end != null ? job.end : (scenes.length ? scenes[scenes.length - 1].t1 || 1e9 : 0));
    setupHand(job.hand);
    capParts = buildCaptions(job.captions || [], job.captionStyle);
    Object.assign(CAP, job.captionStyle || {});
    $('captext').style.fontSize = CAP.size + 'px'; $('captext').style.lineHeight = CAP.lineH;
    for (const S of scenes) for (const it of S.items) applyItem(it, -1e9);
    return {
      warnings,
      hand: HAND.kind,
      scenes: scenes.map((S) => ({
        id: S.id, t0: S.t0, drawStart: +S.drawStart.toFixed(2), drawEnd: +S.drawEnd.toFixed(2),
        window: +(S.window || 0).toFixed(2), limit: +S.limit.toFixed(2),
        items: S.items.map((it) => {
          const r2 = (x) => (x != null && isFinite(x) ? +x.toFixed(2) : null);
          return { kind: it.kind, mode: it.mode, events: it.events.length, strokes: it.events.filter(isPen).length, penLen: Math.round(it.events.filter(isPen).reduce((a, e) => a + e.lenF, 0)), start: r2(it.start), end: r2(it.end), penSpeed: Math.round(it.speed || 0), at: it.at, want: r2(it.Dwant), classes: it.kind === 'art' && it.mode === 'native' ? classStats(it) : null,
            file: it.file || null, label: it.label || null, missing: !!it.missing, winStart: r2(it.winStart), winEnd: r2(it.winEnd), natural: r2(it.natural), fast: r2(it.fast), hatches: it.hatches || 0, hatchEnd: r2(it.hatchEnd), over: r2(it.over) };
        }),
      })),
      captionParts: capParts.length,
    };
  };

  window.renderAt = function (t) {
    const c = camAt(t);
    $('cam').setAttribute('transform', `matrix(${c.s} 0 0 ${c.s} ${W / 2 - c.s * c.cx} ${H / 2 - c.s * c.cy})`);
    const vx0 = c.cx - W / (2 * c.s), vx1 = c.cx + W / (2 * c.s), vy0 = c.cy - H / (2 * c.s), vy1 = c.cy + H / (2 * c.s);
    for (const S of scenes) {
      const on = S.frame[0] < vx1 + 50 && S.frame[0] + W > vx0 - 50 && S.frame[1] < vy1 + 50 && S.frame[1] + H > vy0 - 50;
      if (S._on !== on) { S._on = on; S.g.style.display = on ? '' : 'none'; }
      if (on) for (const it of S.items) applyItem(it, t);
    }
    const tip = renderHand(t);
    renderCaption(t);
    return tip;
  };
  // debugging helper: where is the pen and what is drawing at time t
  window.debugAt = function (t) {
    const c = camAt(t);
    for (const S of scenes) { const st = penState(S, t); if (st) return { scene: S.id, cam: c, pt: st.pt, screen: toScreen(S, st.pt, c), st }; }
    return { cam: c };
  };
})();
