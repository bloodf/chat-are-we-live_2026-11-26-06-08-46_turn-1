// dev-only look viewer
import * as THREE from 'three/webgpu';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { bakedMaterial, loadTex, setReflections, assetURL, pipeline } from './three/materials';
import { L } from './three/lighting';
import { QUALITY } from './three/quality';
const q = new URLSearchParams(location.search); const qual = QUALITY[q.get('q') || 'high']; const name = q.get('env') || 'bedroom';
const r = new THREE.WebGPURenderer({ antialias: q.has('aa'), forceWebGL: true }); r.outputColorSpace = THREE.LinearSRGBColorSpace; r.setPixelRatio(qual.scale); r.setSize(innerWidth, innerHeight); document.body.append(r.domElement); await r.init();
const s = new THREE.Scene(); s.background = new THREE.Color(0x0c0b0a); const c = new THREE.PerspectiveCamera(+(q.get('fov') || 32), innerWidth / innerHeight, .1, 100);
const [env, mats] = await Promise.all([fetch(assetURL(`env/${name}/env.json`)).then(r => r.json()), fetch(assetURL('materials.json')).then(r => r.json())]);
const lm = { day: loadTex(`env/${name}/lm_day.webp`, { srgb: false, repeat: false }), lamp: loadTex(`env/${name}/lm_lamp.webp`, { srgb: false, repeat: false }), led: loadTex(`env/${name}/lm_led.webp`, { srgb: false, repeat: false }) };
setReflections({ day: loadTex(`env/${name}/refl_day.webp`, { srgb: false, flipY: true }), lamp: loadTex(`env/${name}/refl_lamp.webp`, { srgb: false, flipY: true }) });
L.reflAt.value.fromArray(env.reflAt); const [w, d, h] = env.room; L.roomMin.value.set(-w / 2, 0, -d / 2); L.roomMax.value.set(w / 2, h, d / 2);
const g = await new GLTFLoader().loadAsync(assetURL(`env/${name}/env.glb`)); const cache: any = {};
g.scene.traverse((o: any) => { if (o.isMesh) { const n = o.material.name; o.material = cache[n] ??= bakedMaterial(n, mats[n], lm, qual); } }); s.add(g.scene);
const T = (q.get('t') || 'day'); L.day.value.setScalar(T === 'day' ? 1 : .02); L.lamp.value.setScalar(T === 'day' ? 0.25 : 1); L.led.value.set(...((q.get('led') || '0,0,0').split(',').map(Number) as [number, number, number])); L.exposure.value = +(q.get('e') || 1);
const cam = env.meta.cam; const az = +(q.get('az') ?? cam.az), pol = +(q.get('pol') ?? cam.pol), dist = +(q.get('d') ?? cam.dist); const tg = q.get('tg') ? q.get('tg')!.split(',').map(Number) : cam.target;
c.position.set(tg[0] + dist * Math.sin(pol) * Math.sin(az), tg[1] + dist * Math.cos(pol), tg[2] + dist * Math.sin(pol) * Math.cos(az)); c.lookAt(tg[0], tg[1], tg[2]);
let f = 0, t0 = performance.now(); r.setAnimationLoop(() => { r.render(s, c); f++; const t = performance.now(); if (t - t0 > 2000) { document.title = (f / (t - t0) * 1000).toFixed(1) + 'fps'; (window as any).fps = f / (t - t0) * 1000; f = 0; t0 = t; if (!q.get('chars') || (window as any).cs) (window as any).ready = true; } });
import { Character } from './three/character'; import { sampleProbes } from './three/lighting';
{ const ids = (q.get('chars') || '').split(',').filter(Boolean); const acts = (q.get('acts') || 'idle').split(','); const gs = (q.get('g') || '').split(','); const em = (q.get('emo') || 'happy').split(','); const pos = (q.get('p') || '').split(';').map((s: string) => s.split(',').map(Number));
  const cs: Character[] = []; for (const [i, id] of ids.entries()) { const ch = await Character.load(id, qual); ch.action = (acts[i % acts.length] as any); ch.emotion = em[i % em.length] as any; const p = pos[i] ?? [i * .8 - (ids.length - 1) * .4, 0, 0, 0]; ch.root.position.set(p[0], p[1], p[2]); ch.root.rotation.y = p[3] || 0; if (gs[i % gs.length]) ch.play(gs[i % gs.length] as any, 1e9); if (q.get('look')) ch.look = c.position; if (ch.action === 'walk') ch.speed = 1.3; s.add(ch.root); cs.push(ch); const L_ = { day: L.day.value as any, lamp: L.lamp.value as any, led: L.led.value as any }; sampleProbes(env.probes, p[0], 1.1, p[2], ch.probe, L_); }
  const clk = performance.now(); let last = clk; const tick = () => { const n = performance.now(); for (const ch of cs) ch.update((n - last) / 1000); last = n; requestAnimationFrame(tick); }; tick(); (window as any).cs = cs; }
