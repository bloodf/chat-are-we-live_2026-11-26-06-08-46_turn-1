// meshopt-compress every GLB in place (raw copies are kept out of the repo). Float positions/uvs keep rig + lightmap precision.
import { execFileSync } from 'child_process'; import fs from 'fs'; import path from 'path';
const root = path.resolve(import.meta.dirname, '../public/assets'); let a = 0, b = 0; const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(`${d}/${e.name}`) : e.name.endsWith('.glb') ? [`${d}/${e.name}`] : []);
for (const f of walk(root)) { const raw = fs.readFileSync(f); if (raw.includes('EXT_meshopt_compression')) continue; const s0 = raw.length; const t = f + '.tmp.glb'; execFileSync('npx', ['gltfpack', '-i', f, '-o', t, '-cc', '-kn', '-km', '-ke', '-kv', '-vpf', '-vtf', '-vn', '10', '-vc', '8'], { stdio: ['ignore', 'ignore', 'inherit'] }); const s1 = fs.statSync(t).size; a += s0; b += s1; fs.renameSync(t, f); }
console.log(`glb ${(a / 1e6).toFixed(1)} MB -> ${(b / 1e6).toFixed(1)} MB`);
// low-poly character set for software / integrated GPUs
const rawChars = process.env.RAW ?? `${process.env.HOME}/.cache/forge/assets_raw/chars`; const lo = `${root}/chars/lo`; fs.mkdirSync(lo, { recursive: true });
if (fs.existsSync(rawChars)) for (const f of fs.readdirSync(rawChars).filter((x) => x.endsWith('.glb'))) execFileSync('npx', ['gltfpack', '-i', `${rawChars}/${f}`, '-o', `${lo}/${f}`, '-cc', '-kn', '-km', '-ke', '-kv', '-vpf', '-vtf', '-vn', '10', '-vc', '8', '-si', '0.55', '-slb'], { stdio: ['ignore', 'ignore', 'inherit'] });
