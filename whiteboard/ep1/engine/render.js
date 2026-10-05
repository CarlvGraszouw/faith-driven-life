#!/usr/bin/env node
// Whiteboard animation renderer.
//   node render.js <timeline.json> <out.mp4> [--from S] [--to S] [--stills t1,t2,... --stills-dir DIR]
//                  [--placeholder art.svg] [--verbose]
// --placeholder: scene/part SVGs that do not exist yet are drawn with this file instead (with a warning).
// --check: build the board and print the per-scene schedule, stroke classes/widths and budget warnings only.
'use strict';
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { launch } = require('./lib/cdp');

const ROOT = __dirname;
const argv = process.argv.slice(2);
const flag = (name) => { const i = argv.indexOf(name); if (i < 0) return null; const v = argv[i + 1]; argv.splice(i, 2); return v; };
const bool = (name) => { const i = argv.indexOf(name); if (i < 0) return false; argv.splice(i, 1); return true; };
const verbose = bool('--verbose');
const checkOnly = bool('--check'); // build the board, print the schedule/budget log, render nothing
const fromArg = flag('--from'), toArg = flag('--to'), stillsArg = flag('--stills'), stillsDir = flag('--stills-dir');
const placeholderArg = flag('--placeholder');
const [timelinePath, outPath] = argv;
if (!timelinePath || (!outPath && !stillsArg && !checkOnly)) {
  console.error('usage: node render.js <timeline.json> <out.mp4> [--from S] [--to S] [--stills t1,t2 --stills-dir DIR] [--check] [--placeholder art.svg] [--verbose]');
  process.exit(2);
}
const placeholder = placeholderArg ? path.resolve(placeholderArg) : null;
if (placeholder && !fs.existsSync(placeholder)) { console.error(`placeholder not found: ${placeholder}`); process.exit(2); }

const tlDir = path.dirname(path.resolve(timelinePath));
const rel = (p, base = tlDir) => (p ? path.resolve(base, p.replace(/^~(?=\/)/, process.env.HOME)) : p);
const readText = (p, what) => {
  if (!fs.existsSync(p)) throw new Error(`${what} not found: ${p}`);
  return fs.readFileSync(p, 'utf8');
};
// scene art: a missing file is replaced by --placeholder when one is given
const readArt = (p, what) => {
  if (!fs.existsSync(p) && placeholder) {
    console.log(`  placeholder: ${what} (${path.relative(tlDir, p)} not found)`);
    return fs.readFileSync(placeholder, 'utf8');
  }
  return readText(p, what);
};

function pngSize(buf) {
  if (buf.readUInt32BE(0) !== 0x89504e47) throw new Error('hand image must be a PNG');
  return [buf.readUInt32BE(16), buf.readUInt32BE(20)];
}

// Find the hand tip in text such as "hand-marker ... TIP at (0,0)" (style-guide.md or the symbol <desc>).
function tipFromText(text, symbol) {
  if (!text) return null;
  const at = symbol ? text.indexOf(symbol) : -1;
  const scope = at >= 0 ? text.slice(at, at + 1500) : text;
  const num = '(-?\\d+(?:\\.\\d+)?)';
  const m = new RegExp(`tip[^0-9\\n-]{0,60}${num}[^0-9\\n-]{1,16}${num}`, 'i').exec(scope);
  return m ? [parseFloat(m[1]), parseFloat(m[2])] : null;
}

function buildJob(tl) {
  const width = tl.width || 1920, height = tl.height || 1080;
  const kits = new Map(); // abs path -> {name, text}
  const addKit = (p) => {
    if (!p || kits.has(p)) return;
    if (!fs.existsSync(p)) { console.warn(`warning: kit not found: ${p}`); return; }
    kits.set(p, { name: path.basename(p), text: fs.readFileSync(p, 'utf8') });
  };
  for (const k of [].concat(tl.kits || [], tl.kit || [])) addKit(rel(k));

  const scenes = (tl.scenes || []).map((sc, i) => {
    const out = { ...sc, id: sc.id || `scene${i + 1}` };
    const artPath = sc.svg || sc.art;
    delete out.art;
    if (artPath) {
      const p = rel(artPath);
      if (/\.(png|jpe?g)$/i.test(p)) throw new Error(`scene ${out.id}: raster art is not supported, use SVG (${p})`);
      out.svg = readArt(p, `scene ${out.id} art`);
      // kits referenced as <use href="kit.svg#symbol"> resolve next to the scene file
      const re = /href\s*=\s*["']([^"'#]+\.svg)#/g; let m;
      while ((m = re.exec(out.svg))) addKit(path.resolve(path.dirname(p), m[1]));
    }
    if (Array.isArray(sc.parts)) out.parts = sc.parts.map((pt, k) => {
      const pp = rel(pt.svg || pt.art);
      const txt = readArt(pp, `scene ${out.id} part ${k + 1}`);
      const re = /href\s*=\s*["']([^"'#]+\.svg)#/g; let m;
      while ((m = re.exec(txt))) addKit(path.resolve(path.dirname(pp), m[1]));
      return { ...pt, svg: txt };
    });
    if (sc.colour && !sc.accentFade && typeof sc.colour === 'number') out.accentFade = sc.colour;
    if (out.t0 == null) throw new Error(`scene ${out.id}: t0 missing`);
    return out;
  }).sort((a, b) => a.t0 - b.t0);

  // captions: an array of {t0,t1,text}, a path to such a JSON file, or a mix of both
  let captions = [];
  for (const c of [].concat(tl.captions || [])) {
    if (typeof c === 'string') captions.push(...JSON.parse(readText(rel(c), 'captions file')));
    else captions.push(c);
  }
  captions = captions.filter((c) => c && c.text && c.t1 > c.t0).map((c) => ({ t0: c.t0, t1: c.t1, text: c.text }));

  // Fonts: fonts/ (the original bundle) if present, else the same variable woff2 subsets from npm
  // (`npm install` in this folder: @fontsource-variable/caveat and /inter).
  const fontDir = path.join(ROOT, 'fonts');
  const npmFonts = path.join(ROOT, 'node_modules', '@fontsource-variable');
  const fonts = [];
  const addFont = (family, file, npmFile, weight) => {
    const p = [path.join(fontDir, file), path.join(npmFonts, npmFile)].find((f) => fs.existsSync(f));
    if (p) fonts.push({ family, weight, data: fs.readFileSync(p).toString('base64') });
    else console.warn(`warning: font ${file} not found (run \`npm install\` in ${ROOT}); text falls back to a system font`);
  };
  addFont('Caveat', 'Caveat-latin.woff2', 'caveat/files/caveat-latin-wght-normal.woff2', '400 700');
  addFont('Caveat', 'Caveat-latin-ext.woff2', 'caveat/files/caveat-latin-ext-wght-normal.woff2', '400 700');
  addFont('Inter', 'Inter-latin.woff2', 'inter/files/inter-latin-wght-normal.woff2', '100 900');

  let hand = null;
  const h = tl.hand || {};
  if (h.image) {
    const buf = fs.readFileSync(rel(h.image));
    hand = { image: 'data:image/png;base64,' + buf.toString('base64'), size: pngSize(buf), tip: h.tip || [0, 0], scale: h.scale, angle: h.angle, follow: h.follow };
  } else if (h.kit || h.symbol) {
    const kitPath = rel(h.kit || '');
    const symbol = h.symbol || 'hand-marker';
    if (kitPath && fs.existsSync(kitPath)) {
      const text = fs.readFileSync(kitPath, 'utf8');
      if (new RegExp(`id\\s*=\\s*["']${symbol}["']`).test(text)) {
        const guide = h.styleGuide ? rel(h.styleGuide) : path.join(path.dirname(kitPath), 'style-guide.md');
        let tip = h.tip || tipFromText(fs.existsSync(guide) ? fs.readFileSync(guide, 'utf8') : '', symbol), src = guide;
        if (!tip) {
          // the symbol's own <desc>, e.g. "Marker TIP at (0,0)"
          const i = text.search(new RegExp(`id\\s*=\\s*["']${symbol}["']`));
          const m = /<desc>([\s\S]*?)<\/desc>/.exec(text.slice(i, text.indexOf('</symbol>', i)));
          if (m) { tip = tipFromText(m[1]); src = `the <desc> of "${symbol}" in ${path.basename(kitPath)}`; }
        }
        if (!h.tip) console.log(tip ? `hand: kit symbol "${symbol}", tip ${tip.join(',')} from ${src}` : `hand: no tip found for "${symbol}"; looking for an element with id "tip" in the symbol`);
        hand = { symbolSvg: text, symbol, tip, tipId: h.tipId, scale: h.scale, height: h.height, angle: h.angle };
      } else console.log(`hand: symbol "${symbol}" not in ${kitPath} yet; using the vector marker`);
    } else console.log(`hand: kit ${kitPath} not found yet; using the vector marker`);
  }
  if (!hand) hand = { angle: h.angle, scale: h.scale };

  return {
    width, height, fps: tl.fps || 30, start: tl.start || 0, end: tl.end,
    board: tl.board || { color: '#fbfaf7' }, ink: tl.ink || '#1f1f1f', options: tl.options || {},
    safeBottom: tl.safeBottom, // px; art boxes stay above this line (default 860 at 1080p, false = off)
    fonts, kits: [...kits.values()], scenes, captions, captionStyle: tl.captionStyle, hand,
  };
}

async function main() {
  const tl = JSON.parse(readText(path.resolve(timelinePath), 'timeline'));
  const job = buildJob(tl);
  const fps = job.fps, W = job.width, H = job.height;
  const t0 = fromArg != null ? +fromArg : job.start;
  const t1 = toArg != null ? +toArg : (job.end != null ? job.end : Math.max(...job.scenes.map((s) => s.t1 || s.t0 + 5)));
  job.end = job.end != null ? job.end : t1;
  const nFrames = Math.round((t1 - t0) * fps);

  const chrome = await launch({ profileRoot: ROOT, width: W, height: H, verbose });
  const cleanup = async () => { await chrome.close(); };
  process.on('SIGINT', async () => { await cleanup(); process.exit(130); });
  try {
    const { send } = chrome;
    chrome.onEvent((m) => {
      if (m.method === 'Runtime.consoleAPICalled' && (verbose || ['error', 'warning'].includes(m.params.type))) {
        console.log(`[page ${m.params.type}]`, m.params.args.map((a) => a.value !== undefined ? a.value : a.description).join(' '));
      } else if (m.method === 'Runtime.exceptionThrown') console.log('[page exception]', m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description);
    });
    await send('Runtime.enable');
    await send('Page.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
    const loaded = new Promise((r) => chrome.onEvent((m) => { if (m.method === 'Page.loadEventFired') r(); }));
    await send('Page.navigate', { url: 'file://' + path.join(ROOT, 'page', 'index.html') });
    await loaded;
    const tl0 = Date.now();
    const res = await send('Runtime.evaluate', { expression: `loadJob(${JSON.stringify(job)})`, awaitPromise: true, returnByValue: true });
    if (res.exceptionDetails) throw new Error('loadJob failed: ' + (res.exceptionDetails.exception ? res.exceptionDetails.exception.description : res.exceptionDetails.text));
    const info = res.result.value;
    console.log(`board ready in ${((Date.now() - tl0) / 1000).toFixed(1)}s, hand: ${info.hand}, caption parts: ${info.captionParts}`);
    for (const s of info.scenes) {
      console.log(`  ${s.id}: t0 ${s.t0}  draws ${s.drawStart}-${s.drawEnd}s (window ${s.window}s)  ` + s.items.map((i) => `${i.kind}${i.mode ? '/' + i.mode : ''} ${i.strokes} strokes ${i.penLen}px ${i.start}-${i.end}s @${i.penSpeed}px/s`).join(', '));
      // per art item: strokes per class, pen length and rendered stroke width (frame px); "natural" = time at the default pen speed
      for (const i of s.items) if (i.classes) console.log(`      art${i.at != null ? ` @${i.at}s` : ''}: ` + Object.entries(i.classes).map(([k, c]) =>
        `${k} ${c.n} (${c.len}px, w ${c.w0 === c.w1 ? c.w0 : `${c.w0}-${c.w1}`}px)`).join(' | ') + `  natural ${i.want}s, given ${(i.end - i.start).toFixed(2)}s`);
    }
    for (const w of info.warnings) console.log('  warning:', w);
    for (const s of info.scenes) for (const i of s.items) if (i.kind === 'art' && i.penSpeed > 3600)
      console.log(`  note: ${s.id} pen speed ${i.penSpeed}px/s is fast; simplify the art or give it more time`);
    if (checkOnly) return;

    const render = async (t) => {
      const r = await send('Runtime.evaluate', { expression: `renderAt(${t})`, returnByValue: true });
      if (r.exceptionDetails) throw new Error(`renderAt(${t}): ${r.exceptionDetails.exception ? r.exceptionDetails.exception.description : r.exceptionDetails.text}`);
      const shot = await send('Page.captureScreenshot', { format: 'png', optimizeForSpeed: true, fromSurface: true, captureBeyondViewport: false });
      return Buffer.from(shot.data, 'base64');
    };

    if (stillsArg) {
      const dir = path.resolve(stillsDir || path.join(ROOT, 'stills'));
      fs.mkdirSync(dir, { recursive: true });
      for (const s of stillsArg.split(',').map(Number)) {
        const f = path.join(dir, `still-${s.toFixed(2)}.png`);
        fs.writeFileSync(f, await render(s));
        console.log('wrote', f);
      }
      return;
    }

    let audio = job.scenes && tl.audio ? rel(tl.audio) : null;
    if (audio && !fs.existsSync(audio)) { console.log(`audio not found: ${audio}; rendering without sound`); audio = null; }
    const args = ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', 'pipe:0'];
    if (audio) args.push('-ss', String(t0), '-t', String(t1 - t0), '-i', audio, '-map', '0:v', '-map', '1:a');
    args.push('-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd,format=yuv420p',
      '-c:v', 'libx264', '-preset', 'medium', '-tune', 'animation', '-crf', '18', '-pix_fmt', 'yuv420p',
      '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-x264-params', 'rc-lookahead=20', '-threads', '4');
    if (audio) args.push('-c:a', 'aac', '-b:a', '192k', '-shortest');
    args.push('-r', String(fps), '-movflags', '+faststart', path.resolve(outPath));
    const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'ignore', 'pipe'] });
    let ffErr = '';
    ff.stderr.on('data', (d) => { ffErr += d; });
    const ffDone = new Promise((resolve, reject) => ff.on('exit', (code) => (code === 0 ? resolve() : reject(new Error('ffmpeg failed: ' + ffErr)))));
    const write = (buf) => new Promise((resolve) => { if (ff.stdin.write(buf)) resolve(); else ff.stdin.once('drain', resolve); });

    const tStart = Date.now();
    let pendingWrite = Promise.resolve();
    for (let f = 0; f < nFrames; f++) {
      const png = await render(t0 + f / fps);
      await pendingWrite;
      pendingWrite = write(png);
      if (f % fps === 0 || f === nFrames - 1) {
        const el = (Date.now() - tStart) / 1000, rate = (f + 1) / el;
        process.stdout.write(`\rframe ${f + 1}/${nFrames}  ${rate.toFixed(1)} fps  eta ${((nFrames - f - 1) / rate).toFixed(0)}s   `);
      }
    }
    await pendingWrite;
    ff.stdin.end();
    const renderSecs = (Date.now() - tStart) / 1000;
    await ffDone;
    const total = (Date.now() - tStart) / 1000;
    console.log(`\nrendered ${nFrames} frames in ${renderSecs.toFixed(1)}s = ${(nFrames / renderSecs).toFixed(1)} fps ` +
      `(${(nFrames / fps / total).toFixed(2)}x real time incl. encode) -> ${path.resolve(outPath)}`);
  } finally {
    await cleanup();
  }
}

main().catch((e) => { console.error('\nerror:', e.message); process.exit(1); });
