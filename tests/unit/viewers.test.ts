import { describe, expect, it } from 'vitest';
import { RNG } from '../../src/core/rng';
import { attendance, bondWith, feel, makeViewer, nightly, refreshCommunity, regularCap, tickViewers } from '../../src/core/viewers';
import { fresh, rich } from './helpers';
describe('community', () => {
  it('a new channel has a handful of named regulars with distinct names', () => { const s = fresh(); expect(s.viewers.length).toBeGreaterThanOrEqual(6); expect(new Set(s.viewers.map((v) => v.name)).size).toBe(s.viewers.length); });
  it('cap grows with followers and is bounded', () => { expect(regularCap(0)).toBeLessThan(regularCap(1000)); expect(regularCap(1e9)).toBeLessThanOrEqual(48); });
  it('refresh grows toward the cap and never past 80', () => { const s = rich(); for (let i = 0; i < 20; i++) refreshCommunity(s, new RNG(i)); expect(s.viewers.filter((v) => !v.banned).length).toBe(regularCap(s.followers)); s.viewers.push(...Array.from({ length: 90 }, () => makeViewer(new RNG(3), 1, new Set()))); refreshCommunity(s, new RNG(1)); expect(s.viewers.length).toBeLessThanOrEqual(80); });
  it('banned viewers never attend; beloved ones nearly always do', () => { const s = rich(); for (const v of s.viewers) v.bond.affinity = 95; const [a] = s.viewers; a.banned = true; let n = 0; for (let i = 0; i < 100; i++) { const p = attendance(s, new RNG(i)); expect(p).not.toContain(a); n += p.length; } expect(n / 100 / (s.viewers.length - 1)).toBeGreaterThan(0.85); });
  it('people who dislike you drift away', () => { const s = rich(); for (const v of s.viewers) v.bond.affinity = -60; let n = 0; for (let i = 0; i < 60; i++) n += attendance(s, new RNG(i)).length; expect(n / 60 / s.viewers.length).toBeLessThan(0.3); });
  it('feelings change mood; bonds record why', () => { const v = makeViewer(new RNG(1), 1, new Set(), 'simp'); const p = v.mood.p; feel(v, { good: 0.9, praise: 0.9 }); expect(v.mood.p).toBeGreaterThan(p); bondWith(v, 'said my name', 9, 2); expect(v.bond.memories[0]).toMatchObject({ text: 'said my name', day: 2 }); });
  it('timeouts tick down and moods move with the crowd', () => { const v = makeViewer(new RNG(1), 1, new Set()); v.timeout = 5; v.mood = { p: 0, a: 0, d: 0 }; tickViewers([v], { p: 1, a: 1, d: 0 }, 2); expect(v.timeout).toBe(3); tickViewers([v], { p: 1, a: 1, d: 0 }, 9); expect(v.timeout).toBe(0); });
  it('nightly upkeep fades bonds and lets some subs lapse', () => { const s = rich(); for (const v of s.viewers) { v.bond.affinity = 50; v.sub = 1; } nightly(s, new RNG(4)); expect(s.viewers[0].bond.affinity).toBeLessThan(50); });
  it('every style can be generated', () => { const seen = new Set<string>(); const r = new RNG(2); for (let i = 0; i < 500; i++) seen.add(makeViewer(r, 1, new Set()).style); expect(seen.size).toBe(10); });
});
