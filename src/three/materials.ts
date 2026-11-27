import * as THREE from 'three/webgpu';
import { texture, uv, vec2, vec3, vec4, float, uniform, attribute, normalWorld, normalView, positionWorld, cameraPosition, reflect, mix, max, min, abs, pow, sqrt, dot, clamp, saturate, normalize, select, Fn, Loop, textureLevel, equirectUV, normalMap, output, renderOutput, smoothstep, positionViewDirection, transformNormalToView, cameraViewMatrix, length, step, sRGBTransferOETF, varying, modelWorldMatrix, positionLocal, normalLocal } from 'three/tsl';
import { L, occ, MAX_OCC, RANGE } from './lighting';
import type { Quality } from './quality';
import { occlusion, visibleInStatic } from './cache';

export interface MatDef { tex?: string; tint: number[]; rough?: number; metal?: number; scale?: number; emit?: [number[], number]; chan?: string; art?: string; alpha?: number | boolean; bump?: number; two?: boolean }
export type MatTable = Record<string, MatDef>;
type N = any;

const base = import.meta.env.BASE_URL + 'assets/';
export const assetURL = (p: string) => base + p;
const loader = new THREE.TextureLoader();
const cache = new Map<string, THREE.Texture>();
export function loadTex(path: string, o: { srgb?: boolean; flipY?: boolean; repeat?: boolean; aniso?: number; mips?: boolean } = {}): THREE.Texture {
  const key = path + JSON.stringify(o);
  let t = cache.get(key);
  if (t) return t;
  t = loader.load(assetURL(path));
  t.colorSpace = o.srgb === false ? THREE.NoColorSpace : THREE.SRGBColorSpace;
  t.flipY = o.flipY ?? false;
  if (o.repeat !== false) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = o.aniso ?? 4;
  t.generateMipmaps = o.mips !== false;
  t.minFilter = t.generateMipmaps ? THREE.LinearMipmapLinearFilter : THREE.LinearFilter;
  cache.set(key, t);
  return t;
}
export async function preloadTextures(list: THREE.Texture[]) {
  await Promise.all(list.map((t) => t.image ? Promise.resolve() : new Promise<void>((r) => {
    const iv = setInterval(() => { if (t.image) { clearInterval(iv); r(); } }, 15);
    setTimeout(() => { clearInterval(iv); r(); }, 15000);
  })));
}

/** Filmic display transform applied in-material on the direct path (no HDR framebuffer needed). */
const tonemap = Fn(([c]: N[]) => {
  // Hable-ish / AgX-inspired punchy curve with soft shoulder, hue preserving-ish
  const x = c.mul(L.exposure).toVar();
  const m = max(x.r, max(x.g, x.b));
  x.assign(mix(x, vec3(m), smoothstep(1.2, 5.0, m).mul(0.55)));
  const a = x.mul(x.mul(2.51).add(0.03)).div(x.mul(x.mul(2.43).add(0.59)).add(0.14));
  return saturate(mix(a, a.mul(a).mul(float(3).sub(a.mul(2))), 0.12));
});
/** sRGB OETF via nested square roots: ~10x cheaper than pow() on software GL and visually identical */
const fastOETF = Fn(([x]: N[]) => { const s1 = sqrt(x), s2 = sqrt(s1), s3 = sqrt(s2); return saturate(s1.mul(0.662002687).add(s2.mul(0.684122060)).sub(s3.mul(0.323583601)).sub(x.mul(0.0225411470))); });
export const displayEncode = Fn(([c]: N[]) => fastOETF(max(tonemap(c), vec3(0.0))));

/** Whether materials write display-referred colour themselves (low tiers) or scene-linear (post chain). */
export const pipeline = { direct: true };
function finish(m: THREE.NodeMaterial, rgb: N, alpha?: N) {
  m.fog = false; m.lights = false;
  const col = pipeline.direct ? displayEncode(rgb) : rgb;
  m.outputNode = vec4(col, alpha ?? 1) as any;
  return m;
}

export interface ReflSet { day: THREE.Texture; lamp: THREE.Texture }
let refl: ReflSet | null = null;
const blank = (() => { const d = new Uint8Array([40, 40, 44, 255]); const t = new THREE.DataTexture(d, 1, 1); t.needsUpdate = true; return t; })();
export const reflDay = texture(blank), reflLamp = texture(blank);
export function setReflections(r: ReflSet) { refl = r; reflDay.value = r.day; reflLamp.value = r.lamp; }

const envSample = Fn(([dir, rough]: N[]) => {
  // parallax-corrected lookup into the room's baked panoramas
  const p = positionWorld;
  const inv = vec3(1).div(select(abs(dir).lessThan(1e-4), vec3(1e-4), dir));
  const tt = max(L.roomMin.sub(p).mul(inv), L.roomMax.sub(p).mul(inv));
  const t = max(min(tt.x, min(tt.y, tt.z)), 0.05);
  const d = normalize(p.add(dir.mul(t)).sub(L.reflAt));
  const q = equirectUV(d); const u = vec2(q.x.add(0.25), q.y);
  const lod = sqrt(rough).mul(7.0);
  const a = reflDay.sample(u).level(lod).rgb, b = reflLamp.sample(u).level(lod).rgb;
  return a.mul(a).mul(8).mul(L.day).add(b.mul(b).mul(8).mul(L.lamp)).add(vec3(0.03).mul(L.led));
});
const envBRDF = Fn(([f0, rough, nv]: N[]) => {
  const c0 = vec4(-1, -0.0275, -0.572, 0.022), c1 = vec4(1, 0.0425, 1.04, -0.04);
  const r = c0.mul(rough).add(c1);
  const a = min(r.x.mul(r.x), pow(2, nv.mul(-9.28))).mul(r.x).add(r.y);
  const ab = vec2(-1.04, 1.04).mul(a).add(r.zw);
  return f0.mul(ab.x).add(ab.y);
});
const sphereOcc = Fn(([n]: N[]) => {
  const o = float(1).toVar();
  Loop(MAX_OCC, ({ i }: any) => {
    const s = occ.element(i) as N;
    const d = s.xyz.sub(positionWorld); const l2 = dot(d, d); const l = sqrt(l2);
    const nl = dot(n, d).div(l);
    const k = clamp(nl.add(0.12), 0, 1).mul(s.w.mul(s.w)).div(l2);
    o.mulAssign(float(1).sub(clamp(k, 0, 0.72)));
  });
  return o;
});

// ---------------------------------------------------------------- static, lightmapped
export interface LMSet { day: THREE.Texture; lamp: THREE.Texture; led: THREE.Texture }
export function bakedMaterial(name: string, def: MatDef, lm: LMSet, q: Quality): THREE.NodeMaterial {
  const m = new THREE.MeshBasicNodeMaterial(); m.name = name;
  if (def.two) m.side = THREE.DoubleSide;
  const tint = vec3(def.tint[0], def.tint[1], def.tint[2]);
  let alb: N = tint;
  if (def.art) alb = texture(loadTex(`art/${def.art}.webp`, { repeat: false }), uv()).rgb.mul(tint);
  else if (def.tex) alb = texture(loadTex(`tex/${def.tex}.webp`), uv()).rgb.mul(tint);
  let rough: N = float(def.rough ?? 0.6), nrm: N = normalWorld;
  if (def.tex && q.normalMaps) {
    const nr = texture(loadTex(`tex/${def.tex}_nr.webp`, { srgb: false }), uv());
    if (def.rough == null) rough = nr.b; else rough = clamp(float(def.rough).add(nr.b.sub(0.6).mul(0.15)), 0.03, 1);
    const xy = nr.rg.mul(2).sub(1);
    const nm = vec3(xy.mul(0.5 * (def.bump ?? 1)).add(0.5), 1);
    nrm = normalize((normalMap(nm as any) as N).transformDirection(cameraViewMatrix.transpose() as any)) as N;
    nrm = normalize(vec4(normalMap(nm as any) as N, 0).mul(cameraViewMatrix as any).xyz);
  }
  const l0 = texture(lm.day, uv(1)).rgb, l1 = texture(lm.lamp, uv(1)).rgb, l2 = texture(lm.led, uv(1)).r;
  let irr: N = l0.mul(l0).mul(L.day).add(l1.mul(l1).mul(L.lamp)).add(l2.mul(l2).mul(L.led)).mul(RANGE);
  const gn = normalWorld;
  if (!q.cached) irr = irr.mul(sphereOcc(gn));
  if (q.normalMaps && def.tex) irr = irr.mul(clamp(float(1).add(nrm.sub(gn).dot(vec3(0.25, 0.75, 0.45)).mul(0.9)), 0.5, 1.5));
  const metal = def.metal ?? 0;
  const V = normalize(cameraPosition.sub(positionWorld));
  const nv = saturate(dot(nrm, V));
  let col: N = alb.mul(irr).mul(1 - metal);
  const shiny = metal > 0 || (def.rough ?? 0.5) < 0.75;
  if (shiny || q.tier >= 2) {
    const R = reflect(V.negate(), nrm);
    const f0 = metal > 0 ? alb : vec3(0.04);
    const lum = dot(irr, vec3(0.333));
    const so = saturate(lum.mul(2.2).add(0.15)); // reflections fade in occluded/dark places
    col = col.add((envSample(R, rough) as N).mul(envBRDF(f0, rough, nv)).mul(so));
    if (metal > 0) col = col.add(alb.mul(irr).mul(0.12));
  }
  if (def.emit) {
    let e: N = vec3(def.emit[0][0], def.emit[0][1], def.emit[0][2]).mul(def.emit[1]);
    if (def.art) { e = e.mul(alb); col = col.mul(0.2); }
    const ch: N = def.chan === 'lamp' ? L.lamp : def.chan === 'led' ? L.led : def.chan === 'day' ? L.day : vec3(1);
    col = col.add(e.mul(ch));
  }
  let a: N;
  if (def.alpha) { m.transparent = true; m.depthWrite = false; a = float(typeof def.alpha === 'number' ? def.alpha : 0.35); }
  return finish(m, col, a);
}

// ---------------------------------------------------------------- dynamic, probe lit
export type ProbeHost = { probe: THREE.Vector3[] };
const zero = Array.from({ length: 6 }, () => new THREE.Vector3(0.3, 0.3, 0.3));
export function findProbe(o: THREE.Object3D): THREE.Vector3[] { let p: THREE.Object3D | null = o; while (p) { const u = (p.userData as any).probe; if (u) return u; p = p.parent; } return zero; }
const cube = [0, 1, 2, 3, 4, 5].map((i) => uniform(new THREE.Vector3()).onObjectUpdate(({ object }: any, self: any) => { self.value.copy(findProbe(object)[i]); return undefined as any; })) as N[];
const ambientCube = Fn(([n]: N[]) => {
  const n2 = n.mul(n);
  return mix(cube[1], cube[0], step(0, n.x)).mul(n2.x).add(mix(cube[3], cube[2], step(0, n.y)).mul(n2.y)).add(mix(cube[5], cube[4], step(0, n.z)).mul(n2.z));
});
const ambientAvg = Fn(() => cube[0].add(cube[1]).add(cube[2]).add(cube[3]).add(cube[4]).add(cube[5]).mul(1 / 6));

export interface ProbeOpts { map?: THREE.Texture; tint?: number[]; rough?: number; metal?: number; kind?: 'solid' | 'skin' | 'hair' | 'eye' | 'cloth' | 'teeth'; alphaTest?: number; blend?: boolean; nmap?: THREE.Texture; emissive?: N; ao?: boolean; two?: boolean; colorNode?: N; specK?: number; dyn?: boolean }
export function probeMaterial(name: string, o: ProbeOpts, q: Quality): THREE.NodeMaterial {
  const m = new THREE.MeshBasicNodeMaterial(); m.name = name;
  const t = o.map ? texture(o.map, uv()) : null;
  const tint = o.tint ? vec3(o.tint[0], o.tint[1], o.tint[2]) : vec3(1);
  let alb: N = o.colorNode ?? (t ? t.rgb.mul(tint) : tint);
  const ao: N = o.ao === false ? float(1) : attribute('color', 'vec4').r;
  let n: N = normalWorld;
  if (o.two) m.side = THREE.DoubleSide;
  if (o.nmap && q.normalMaps) n = normalize(vec4(normalMap(texture(o.nmap, uv())) as N, 0).mul(cameraViewMatrix as any).xyz);
  const V = normalize(cameraPosition.sub(positionWorld));
  const nv = saturate(dot(n, V));
  let irr: N = ambientCube(n).mul(o.kind ? 1.28 : 1);
  const kind = o.kind ?? 'solid';
  let aoc: N = vec3(ao);
  if (kind === 'skin') {
    const soft = ambientAvg();
    irr = mix(irr, soft, vec3(0.34, 0.16, 0.1));
    aoc = pow(vec3(ao), vec3(0.55, 0.85, 0.95));
  } else if (kind === 'hair') irr = mix(irr, ambientAvg(), 0.25);
  else if (kind === 'teeth') aoc = vec3(ao.mul(ao));
  let col: N = alb.mul(irr).mul(aoc).mul(1 - (o.metal ?? 0));
  const rough = o.rough ?? (kind === 'skin' ? 0.52 : kind === 'hair' ? 0.55 : kind === 'eye' ? 0.08 : kind === 'cloth' ? 0.9 : 0.5);
  const sk = o.specK ?? (kind === 'cloth' ? 0.35 : kind === 'skin' ? 0.8 : kind === 'hair' ? 0.55 : 1);
  if (rough < 0.85 || q.tier >= 2) {
    const f0: N = (o.metal ?? 0) > 0 ? alb : vec3(0.04);
    const s = (envSample(reflect(V.negate(), n), float(rough)) as N).mul(envBRDF(f0, float(rough), nv)).mul(ao).mul(sk);
    col = col.add(s);
    if ((o.metal ?? 0) > 0) col = col.add(alb.mul(irr).mul(0.15));
  }
  if (kind === 'skin' || kind === 'cloth') { // soft rim fuzz picks up room light
    const rim = pow(float(1).sub(nv), 3.5).mul(kind === 'skin' ? 0.16 : 0.22);
    col = col.add(ambientCube(n).mul(rim).mul(ao).mul(mix(alb, vec3(1), 0.35)));
  }
  if (kind === 'eye') { // wet catchlight from above/front
    const h = normalize(V.add(normalize(vec3(0.35, 0.8, 0.55)))); const k = pow(saturate(dot(n, h)), 220).mul(1.6);
    col = col.add(ambientAvg().mul(k).mul(3.0));
  }
  if (o.emissive) col = col.add(o.emissive);
  let a: N;
  if (o.alphaTest && t) { m.alphaTest = o.alphaTest; m.side = THREE.DoubleSide; a = t.a; if (!o.blend) { m.maskNode = t.a.greaterThan(o.alphaTest) as any; a = float(1); } }
  if (o.dyn && occlusion.on) m.maskNode = (m.maskNode ? (m.maskNode as any).and(visibleInStatic()) : visibleInStatic()) as any;
  if (o.blend && t) { m.transparent = true; m.depthWrite = false; a = t.a; m.side = THREE.DoubleSide; m.alphaTest = 0.02; }
  return finish(m, col, a);
}
/** One-draw-call character material for software renderers. Vertex colour = (ao, skinness, hairness, roughness). */
export function uberCharMaterial(name: string, map: THREE.Texture): THREE.NodeMaterial {
  const m = new THREE.MeshBasicNodeMaterial(); m.name = name; m.side = THREE.DoubleSide; const t = texture(map, uv()); const p: N = attribute('color', 'vec4'); const n: N = normalize((modelWorldMatrix as N).mul(vec4(normalLocal, 0)).xyz); const ao = p.r, skin = p.g, hair = p.b, rough = p.a; const wp: N = (modelWorldMatrix as N).mul(vec4(positionLocal, 1)).xyz;
  const V = normalize(cameraPosition.sub(wp)); const nv = saturate(dot(n, V)); const soft = ambientAvg(); const irr: N = mix(ambientCube(n), soft, vec3(0.34, 0.16, 0.1).mul(skin).add(hair.mul(0.25))).mul(1.28); const aoc: N = mix(vec3(ao), pow(vec3(ao), vec3(0.55, 0.85, 0.95)), skin);
  const h = normalize(V.add(normalize(vec3(0.35, 0.8, 0.55)))); const gl = float(1).sub(rough); const lit: N = varying(irr.mul(aoc)); const sp: N = varying(soft.mul(pow(saturate(dot(n, h)), gl.mul(gl).mul(180).add(8)).mul(gl.mul(gl)).mul(1.1).add(pow(float(1).sub(nv), 4).mul(0.16))).mul(ao)); const col: N = t.rgb.mul(lit).add(sp);
  const cut: N = t.a.greaterThan(0.36); m.maskNode = (occlusion.on ? cut.and(visibleInStatic()) : cut) as any; return finish(m, col, float(1));
}
/** vertex-coloured, vertex-lit, single draw (dynamic props on software renderers) */
export function vertexPropMaterial(name: string): THREE.NodeMaterial { const m = new THREE.MeshBasicNodeMaterial(); m.name = name; const n: N = normalize((modelWorldMatrix as N).mul(vec4(normalLocal, 0)).xyz); const c: N = attribute('color', 'vec4'); const lit: N = varying(c.rgb.mul(mix(ambientCube(n), vec3(1.6), c.a.oneMinus()))); if (occlusion.on) m.maskNode = visibleInStatic() as any; return finish(m, lit, float(1)); }
/** Unlit material (screens, backdrops, glows). */
export function unlitMaterial(name: string, rgb: N, o: { alpha?: N; add?: boolean; side?: THREE.Side; depthWrite?: boolean; dyn?: boolean } = {}) {
  const m = new THREE.MeshBasicNodeMaterial(); m.name = name;
  if (o.side != null) m.side = o.side;
  if (o.dyn && occlusion.on) m.maskNode = visibleInStatic() as any;
  if (o.alpha || o.add) { m.transparent = true; m.depthWrite = o.depthWrite ?? false; if (o.add) m.blending = THREE.AdditiveBlending; }
  return finish(m, rgb, o.alpha);
}
/** Build a probe material from the shared material table (props). */
export function propMaterial(name: string, def: MatDef, q: Quality, dyn = false) {
  let emissive: N;
  if (def.emit) { const ch: N = def.chan === 'led' ? L.led : def.chan === 'lamp' ? L.lamp : vec3(1); emissive = vec3(def.emit[0][0], def.emit[0][1], def.emit[0][2]).mul(def.emit[1]).mul(ch); }
  const map = def.art ? loadTex(`art/${def.art}.webp`, { repeat: false }) : def.tex ? loadTex(`tex/${def.tex}.webp`) : undefined;
  return probeMaterial(name, { map, tint: def.tint, rough: def.rough ?? 0.5, metal: def.metal ?? 0, emissive, two: def.two, dyn }, q);
}
export function disposeTextures() { for (const t of cache.values()) t.dispose(); cache.clear(); }
