// Render the Kindermann film frame by frame.
//   node render.mjs --fmt 3x4                 lossless master -> out/kindermann/master-3x4.mkv
//   node render.mjs --fmt 3x4 --beats         one PNG per beat + contact sheet
//   node render.mjs --fmt 3x4 --times 0,4.2   PNG stills at those times
//   node render.mjs --fmt 3x4 --from 3 --to 7 render only that range (for re-renders)
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { join, extname, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '../..');
const OUT = join(ROOT, 'out/kindermann');
const FPS = 24;

const args = process.argv.slice(2);
const opt = (name, def) => {
  const i = args.indexOf('--' + name);
  if (i < 0) return def;
  const v = args[i + 1];
  return v === undefined || v.startsWith('--') ? true : v;
};
const fmt = opt('fmt', '3x4');

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json',
  '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2' };
const server = createServer(async (req, res) => {
  try {
    const p = join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!p.startsWith(ROOT)) throw new Error('outside root');
    const body = await readFile(p);
    res.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404); res.end();
  }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

async function launch() {
  try { return await chromium.launch(); }
  catch { return await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }); }
}
const browser = await launch();
const pageObj = await browser.newPage({ deviceScaleFactor: 1 });
await pageObj.goto(`http://127.0.0.1:${port}/films/kindermann/index.html?fmt=${fmt}`);
const info = await pageObj.evaluate(() => window.ready);
await pageObj.setViewportSize({ width: info.W, height: info.H });
await mkdir(OUT, { recursive: true });
const stage = await pageObj.$('#stage');

const warnings = new Map();
async function shot(t, path) {
  const log = await pageObj.evaluate((t) => window.seek(t), t);
  for (const c of log) {
    if (c.clamped) warnings.set(`${c.src} camera clamped`, t);
    if (c.tooBig) warnings.set(`${c.src} scale ${c.s.toFixed(3)} > 0.98`, t);
  }
  return stage.screenshot({ path, type: 'png' });
}
const run = (cmd, a, input) => new Promise((res, rej) => {
  const p = spawn(cmd, a, { stdio: [input ? 'pipe' : 'ignore', 'inherit', 'inherit'] });
  p.on('exit', (c) => (c === 0 ? res() : rej(new Error(cmd + ' exit ' + c))));
  if (input) input(p.stdin);
});

const frameT = (i) => i / FPS;
const beatsMode = opt('beats', false);
const times = opt('times', null);

if (beatsMode || times) {
  const dir = join(OUT, `stills-${fmt}`);
  await mkdir(dir, { recursive: true });
  // one frame per beat, taken 0.42 beat after the beat so motion has landed
  const list = times
    ? String(times).split(',').map(Number)
    : Array.from({ length: 32 }, (_, n) => Math.round(((n + 0.42) * 0.625) * FPS) / FPS);
  const files = [];
  for (const [i, t] of list.entries()) {
    const f = join(dir, `s${String(i).padStart(2, '0')}.png`);
    await shot(t, f);
    files.push(f);
  }
  if (beatsMode) {
    const cols = fmt === '16x9' ? 4 : 8;
    const tw = fmt === '16x9' ? 480 : 270;
    await run('python3', [join(HERE, 'tile.py'), join(OUT, `contact-${fmt}.png`), String(cols), String(tw), ...files]);
    console.log('contact sheet', join(OUT, `contact-${fmt}.png`));
  }
} else {
  const from = Number(opt('from', 0)), to = Number(opt('to', info.DUR));
  const n0 = Math.round(from * FPS), n1 = Math.round(to * FPS);
  const out = opt('out', join(OUT, from === 0 && to === info.DUR ? `master-${fmt}.mkv` : `part-${fmt}-${from}-${to}.mkv`));
  const t0 = Date.now();
  await run('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'ultrafast', out], async (stdin) => {
    for (let i = n0; i < n1; i++) {
      const buf = await shot(frameT(i));
      if (!stdin.write(buf)) await new Promise((r) => stdin.once('drain', r));
      if (i % 48 === 0) process.stdout.write(`\r${fmt} frame ${i}/${n1}`);
    }
    stdin.end();
  });
  console.log(`\n${out} (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
}

for (const [w, t] of warnings) console.warn(`WARN ${w} (t=${t.toFixed(2)})`);
await browser.close();
server.close();
