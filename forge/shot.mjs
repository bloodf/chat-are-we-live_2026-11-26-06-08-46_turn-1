import { chromium } from '@playwright/test';
const [,, url, out, w='1280', h='800', wait='6000'] = process.argv;
const b = await chromium.launch({ channel: 'chromium', args: ['--use-gl=angle','--use-angle=gl','--ignore-gpu-blocklist'] }); const p = await b.newPage({ viewport: { width: +w, height: +h } });
const seen = new Set(); p.on('console', m => { const t = m.text().slice(0, 260); if (['error', 'warning'].includes(m.type()) && !seen.has(t)) { seen.add(t); console.log(m.type(), t); } }); p.on('pageerror', e => console.log('PAGEERR', String(e).slice(0, 600)));
await p.goto(url); await p.waitForFunction('window.ready', null, { timeout: 60000 }).catch(() => console.log('not ready')); await p.waitForTimeout(+wait > 5000 ? 1500 : +wait); await p.screenshot({ path: out }); await p.evaluate('1'); console.log('fps', await p.evaluate('window.fps')); await b.close();
