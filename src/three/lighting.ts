import * as THREE from 'three/webgpu';
import { uniform, uniformArray } from 'three/tsl';

export const RANGE = 6;
export const MAX_OCC = 12;
/** Global light-channel colours. Baked channels are summed in-shader with these weights. */
export const L = {
  day: uniform(new THREE.Color(1, 1, 1)),
  lamp: uniform(new THREE.Color(1, 1, 1)),
  led: uniform(new THREE.Color(0, 0, 0)),
  exposure: uniform(1),
  roomMin: uniform(new THREE.Vector3(-2, 0, -2)),
  roomMax: uniform(new THREE.Vector3(2, 2.5, 2)),
  reflAt: uniform(new THREE.Vector3(0, 1.4, 0)),
  time: uniform(0),
};
export const occ = uniformArray(Array.from({ length: MAX_OCC }, () => new THREE.Vector4(0, -50, 0, 0.01)), 'vec4');

export interface Probes { nx: number; ny: number; nz: number; gx: number[]; gyz: number[]; gz: number[]; data: Record<'day' | 'lamp' | 'led', number[]> }
const tmp = new Float32Array(18);

/** Trilinear ambient-cube lookup. Returns 6 linear RGB colours (+x -x +y -y +z -z). */
export function sampleProbes(p: Probes, x: number, y: number, z: number, out: THREE.Vector3[], w: { day: THREE.Color; lamp: THREE.Color; led: THREE.Color }) {
  const ax = locate(p.gx, x), ay = locate(p.gyz, z), az = locate(p.gz, y);
  tmp.fill(0);
  for (let c = 0; c < 8; c++) {
    const ix = ax.i + (c & 1), iy = ay.i + ((c >> 1) & 1), iz = az.i + ((c >> 2) & 1);
    if (ix >= p.nx || iy >= p.ny || iz >= p.nz) continue;
    const k = ((c & 1) ? ax.t : 1 - ax.t) * ((c & 2) ? ay.t : 1 - ay.t) * ((c & 4) ? az.t : 1 - az.t);
    if (k < 1e-4) continue;
    const o = (iz * p.ny * p.nx + iy * p.nx + ix) * 18;
    for (let q = 0; q < 18; q += 3) {
      tmp[q] += k * (p.data.day[o + q] * w.day.r + p.data.lamp[o + q] * w.lamp.r + p.data.led[o + q] * w.led.r);
      tmp[q + 1] += k * (p.data.day[o + q + 1] * w.day.g + p.data.lamp[o + q + 1] * w.lamp.g + p.data.led[o + q + 1] * w.led.g);
      tmp[q + 2] += k * (p.data.day[o + q + 2] * w.day.b + p.data.lamp[o + q + 2] * w.lamp.b + p.data.led[o + q + 2] * w.led.b);
    }
  }
  for (let i = 0; i < 6; i++) out[i].set(tmp[i * 3], tmp[i * 3 + 1], tmp[i * 3 + 2]);
}
function locate(g: number[], v: number) {
  const asc = g[g.length - 1] > g[0];
  const n = g.length;
  if (n === 1) return { i: 0, t: 0 };
  for (let i = 0; i < n - 1; i++) {
    const a = g[i], b = g[i + 1];
    const t = (v - a) / (b - a);
    if (asc ? v < b : v > b) return { i, t: Math.min(1, Math.max(0, t)) };
  }
  return { i: n - 2, t: 1 };
}
