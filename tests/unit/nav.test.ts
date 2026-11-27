import { describe, expect, it } from 'vitest';
import fs from 'fs';
import { Nav } from '../../src/three/nav';
import { sampleProbes, type Probes } from '../../src/three/lighting';
import * as THREE from 'three/webgpu';
import { HOMES } from './helpers';
const load = (h: string) => JSON.parse(fs.readFileSync(`public/assets/env/${h}/env.json`, 'utf8'));
describe('A* on a toy room', () => {
  const n = new Nav(6, 6, [[-0.5, -2, 0.5, 2]], 0.2, 0.2);
  it('walls and blocks are not walkable', () => { expect(n.walkable(0, 0)).toBe(false); expect(n.walkable(2.95, 0)).toBe(false); expect(n.walkable(2, 2)).toBe(true); expect(n.walkable(99, 0)).toBe(false); });
  it('routes around an obstacle without cutting through', () => { const p = n.path([-2, 0], [2, 0]); expect(p.length).toBeGreaterThan(1); let a: [number, number] = [-2, 0]; for (const b of p) { expect(n.los(a, b)).toBe(true); a = b; } expect(p[p.length - 1][0]).toBeCloseTo(2); });
  it('straight lines collapse to one hop', () => expect(n.path([-2, -2.4], [-2, 2.4])).toHaveLength(1));
  it('targets inside furniture resolve to the nearest floor', () => { const [x, z] = n.nearest(0, 0); expect(n.walkable(x, z)).toBe(true); const p = n.path([-2, 0], [0, 0]); expect(n.walkable(...p[p.length - 1])).toBe(true); });
  it('same-cell paths are trivial and sealed rooms give up', () => { expect(n.path([2, 2], [2.01, 2.01])).toHaveLength(1); const s = new Nav(6, 6, [[-3, -0.2, 3, 0.2]], 0.2, 0.2); expect(s.path([0, -2], [0, 2])).toEqual([]); });
});
describe.each(HOMES)('%s layout', (h) => {
  const env = load(h); const n = new Nav(env.room[0], env.room[1], env.blocks, env.room[0] > 12 ? 0.25 : 0.18, 0.2); const spawn = env.anchors.spawn.pos;
  it('you can walk from spawn to every interaction and NPC spot', () => { for (const a of ['bed', 'food', 'door', 'wardrobe', 'router', 'breaker', 'seat', 'phone_seat', 'idle1', 'idle2', ...Object.keys(env.anchors).filter((k) => /^(work|idle|cam\d|guest|host)/.test(k))]) { const k = env.anchors[a]; expect(k, a).toBeTruthy(); const g = n.nearest(k.pos[0], k.pos[2]); expect(Math.hypot(g[0] - k.pos[0], g[1] - k.pos[2]), `${a} is too deep in furniture`).toBeLessThan(1.3); const p = n.path([spawn[0], spawn[2]], [k.pos[0], k.pos[2]]); expect(p.length, a).toBeGreaterThan(0); } });
  it('spawn is on open floor', () => expect(n.walkable(spawn[0], spawn[2])).toBe(true));
  it('light probes interpolate to finite, non-negative colours everywhere', () => { const p = env.probes as Probes; const out = Array.from({ length: 6 }, () => new THREE.Vector3()); const w = { day: new THREE.Color(1, 1, 1), lamp: new THREE.Color(1, 1, 1), led: new THREE.Color(0.5, 0.2, 1) }; let lit = 0; for (let i = 0; i < 60; i++) { const x = ((i * 37) % 100) / 100 - 0.5, z = ((i * 61) % 100) / 100 - 0.5; sampleProbes(p, x * env.room[0] * 1.1, (i % 5) * 0.5, z * env.room[1] * 1.1, out, w); for (const v of out) for (const c of [v.x, v.y, v.z]) { expect(Number.isFinite(c)).toBe(true); expect(c).toBeGreaterThanOrEqual(0); lit += c; } } expect(lit).toBeGreaterThan(1); });
  it('probe grid has the right amount of data', () => { const p = env.probes; for (const c of ['day', 'lamp', 'led']) expect(p.data[c].length).toBe(p.nx * p.ny * p.nz * 18); });
});
