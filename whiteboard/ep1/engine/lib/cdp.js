// Tiny dependency-free Chrome DevTools Protocol client over --remote-debugging-pipe.
// Launches headless Chrome with its own --user-data-dir and removes it on close.
'use strict';
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
  // Windows laptop (5 Oct 2026, handover to Windows): the usual install places.
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  process.env.LOCALAPPDATA && `${process.env.LOCALAPPDATA}\\Google\\Chrome\\Application\\chrome.exe`,
].filter(Boolean);

function findChrome() {
  for (const p of CHROME_CANDIDATES) if (fs.existsSync(p)) return p;
  throw new Error('Google Chrome not found; set CHROME_PATH');
}

async function launch({ profileRoot, width = 1920, height = 1080, verbose = false } = {}) {
  const userDataDir = fs.mkdtempSync(path.join(profileRoot, '.chrome-profile-'));
  const args = [
    '--headless=new', '--remote-debugging-pipe', `--user-data-dir=${userDataDir}`,
    '--no-first-run', '--no-default-browser-check', '--disable-extensions', '--disable-sync',
    '--disable-background-networking', '--disable-component-update', '--disable-default-apps',
    '--disable-renderer-backgrounding', '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows', '--mute-audio', '--hide-scrollbars',
    '--force-device-scale-factor=1', `--window-size=${width},${height}`,
    '--force-color-profile=srgb', '--allow-file-access-from-files',
    '--js-flags=--max-old-space-size=1024', 'about:blank',
  ];
  const proc = spawn(findChrome(), args, { stdio: ['ignore', 'ignore', 'pipe', 'pipe', 'pipe'] });
  const stderrTail = [];
  proc.stderr.on('data', (d) => {
    const s = d.toString(); if (verbose) process.stderr.write(s);
    stderrTail.push(s); if (stderrTail.length > 30) stderrTail.shift();
  });
  const toChrome = proc.stdio[3], fromChrome = proc.stdio[4];
  let nextId = 1; const pending = new Map(); const listeners = [];
  let buf = Buffer.alloc(0);
  fromChrome.on('data', (chunk) => {
    buf = Buffer.concat([buf, chunk]);
    let z;
    while ((z = buf.indexOf(0)) >= 0) {
      const msg = JSON.parse(buf.subarray(0, z).toString('utf8'));
      buf = buf.subarray(z + 1);
      if (msg.id && pending.has(msg.id)) {
        const { resolve, reject, method } = pending.get(msg.id); pending.delete(msg.id);
        if (msg.error) reject(new Error(`${method}: ${msg.error.message} ${msg.error.data || ''}`)); else resolve(msg.result);
      } else if (msg.method) for (const l of listeners) l(msg);
    }
  });
  let exited = false;
  proc.on('exit', () => {
    exited = true;
    for (const { reject, method } of pending.values()) reject(new Error(`Chrome exited during ${method}\n${stderrTail.join('')}`));
    pending.clear();
  });
  const send = (method, params = {}, sessionId) => new Promise((resolve, reject) => {
    if (exited) return reject(new Error('Chrome is not running'));
    const id = nextId++;
    pending.set(id, { resolve, reject, method });
    toChrome.write(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params }) + '\0');
  });

  const { targetInfos } = await send('Target.getTargets');
  let page = targetInfos.find((t) => t.type === 'page');
  const targetId = page ? page.targetId : (await send('Target.createTarget', { url: 'about:blank' })).targetId;
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  const s = (method, params) => send(method, params, sessionId);
  const onEvent = (fn) => listeners.push(fn);

  async function close() {
    try { if (!exited) await Promise.race([send('Browser.close'), new Promise((r) => setTimeout(r, 3000))]); } catch (_) { /* ignore */ }
    if (!exited) {
      await new Promise((r) => setTimeout(r, 500));
      if (!exited) try { process.kill(proc.pid, 'SIGTERM'); } catch (_) { /* already gone */ }
      await new Promise((r) => setTimeout(r, 500));
      if (!exited) try { process.kill(proc.pid, 'SIGKILL'); } catch (_) { /* already gone */ }
    }
    for (let i = 0; i < 10; i++) {
      try { fs.rmSync(userDataDir, { recursive: true, force: true }); break; } catch (_) { await new Promise((r) => setTimeout(r, 300)); }
    }
  }
  return { send: s, browserSend: send, onEvent, close, pid: proc.pid, userDataDir };
}

module.exports = { launch };
