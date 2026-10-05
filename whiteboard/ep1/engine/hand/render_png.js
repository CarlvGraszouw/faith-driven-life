// Render an SVG file to a transparent PNG at its own width/height with headless Chrome (via ../lib/cdp.js).
//   node render_png.js hand.svg hand.png [scale]
'use strict';
const fs = require('fs'), path = require('path');
const { launch } = require('../lib/cdp');
(async () => {
  const [src, out, sc] = process.argv.slice(2);
  const svg = fs.readFileSync(src, 'utf8');
  const w = +/width="([\d.]+)"/.exec(svg)[1], h = +/height="([\d.]+)"/.exec(svg)[1], s = +(sc || 1);
  const W = Math.round(w * s), H = Math.round(h * s);
  const chrome = await launch({ profileRoot: require('os').tmpdir(), width: W, height: H });
  try {
    const { send } = chrome;
    await send('Page.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
    await send('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } });
    const html = `<!doctype html><html><head><style>html,body{margin:0;background:transparent;overflow:hidden}svg{display:block}</style></head><body>${svg.replace(/<\?xml[^>]*>/, '').replace(/<svg /, `<svg style="width:${W}px;height:${H}px" `)}</body></html>`;
    const tmp = path.join(require('os').tmpdir(), `hand-${process.pid}.html`);
    fs.writeFileSync(tmp, html);
    const loaded = new Promise((r) => chrome.onEvent((m) => { if (m.method === 'Page.loadEventFired') r(); }));
    await send('Page.navigate', { url: 'file://' + tmp });
    await loaded;
    await new Promise((r) => setTimeout(r, 200));
    const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
    fs.writeFileSync(out, Buffer.from(shot.data, 'base64'));
    fs.unlinkSync(tmp);
    console.log(`wrote ${out} ${W}x${H}`);
  } finally { await chrome.close(); }
})().catch((e) => { console.error(e); process.exit(1); });
