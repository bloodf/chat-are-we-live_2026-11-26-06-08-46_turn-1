// Zips every source file (code, tests, asset forge, assets, config) to ~/backups/chat-are-we-live/
import { execFileSync } from 'node:child_process'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'); const dir = path.join(os.homedir(), 'backups', 'chat-are-we-live'); fs.mkdirSync(dir, { recursive: true });
const stamp = new Date().toISOString().replace(/[:T]/g, '-').slice(0, 19); const out = path.join(dir, `chat-are-we-live_${stamp}${process.argv[2] ? '_' + process.argv[2].replace(/\W+/g, '-') : ''}.zip`);
execFileSync('zip', ['-rq', out, '.', '-x', 'node_modules/*', 'dist/*', 'test-results/*', 'playwright-report/*', '.git/*', '*/__pycache__/*'], { cwd: root, stdio: 'inherit' });
console.log(`backup: ${out} (${(fs.statSync(out).size / 1e6).toFixed(1)} MB)`);
