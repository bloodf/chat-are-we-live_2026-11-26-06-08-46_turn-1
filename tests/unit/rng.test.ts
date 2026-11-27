import { describe, expect, it } from 'vitest';
import { RNG, clamp, countFor, fmt, lerp, money } from '../../src/core/rng';
describe('RNG', () => {
  it('is deterministic per seed and differs between seeds', () => { const a = new RNG(9), b = new RNG(9), c = new RNG(10); const A = Array.from({ length: 50 }, () => a.next()); expect(A).toEqual(Array.from({ length: 50 }, () => b.next())); expect(A).not.toEqual(Array.from({ length: 50 }, () => c.next())); });
  it('resumes from serialised state', () => { const a = new RNG(3); a.next(); a.next(); const b = new RNG(a.s); expect(a.next()).toBe(b.next()); });
  it('stays in [0,1) with a sane mean', () => { const r = new RNG(1); let m = 0; for (let i = 0; i < 20000; i++) { const v = r.next(); expect(v).toBeGreaterThanOrEqual(0); expect(v).toBeLessThan(1); m += v; } expect(m / 20000).toBeCloseTo(0.5, 1); });
  it('int covers inclusive bounds', () => { const r = new RNG(2); const seen = new Set(Array.from({ length: 400 }, () => r.int(1, 6))); expect([...seen].sort()).toEqual([1, 2, 3, 4, 5, 6]); });
  it('weighted respects weights and zero totals', () => { const r = new RNG(4); let a = 0; for (let i = 0; i < 2000; i++) if (r.weighted(['a', 'b'], (x) => (x === 'a' ? 9 : 1)) === 'a') a++; expect(a).toBeGreaterThan(1650); expect(['x', 'y']).toContain(r.weighted(['x', 'y'], () => 0)); for (let i = 0; i < 200; i++) expect(r.weighted(['a', 'b'], (x) => (x === 'a' ? 0 : 1))).toBe('b'); });
  it('throws on empty picks', () => { const r = new RNG(1); expect(() => r.pick([])).toThrow(); expect(() => r.weighted([], () => 1)).toThrow(); });
  it('gauss has the right moments', () => { const r = new RNG(6); const v = Array.from({ length: 8000 }, () => r.gauss(2, 3)); const m = v.reduce((a, b) => a + b) / v.length; const sd = Math.sqrt(v.reduce((a, b) => a + (b - m) ** 2, 0) / v.length); expect(m).toBeCloseTo(2, 0); expect(sd).toBeGreaterThan(2.8); expect(sd).toBeLessThan(3.2); });
  it('shuffle is a permutation and does not mutate', () => { const r = new RNG(8); const a = [1, 2, 3, 4, 5]; const b = r.shuffle(a); expect(a).toEqual([1, 2, 3, 4, 5]); expect(b.sort()).toEqual(a); expect(r.sample(a, 2)).toHaveLength(2); });
  it('fork, chance, range, lognormal and id work', () => { const r = new RNG(5); expect(r.fork()).toBeInstanceOf(RNG); expect(r.chance(1)).toBe(true); expect(r.chance(0)).toBe(false); const v = r.range(5, 6); expect(v >= 5 && v < 6).toBe(true); expect(r.lognormal(10, 0.2)).toBeGreaterThan(0); expect(r.id('v')).toMatch(/^v/); });
  it('countFor tracks its expectation at both scales', () => { const r = new RNG(3); for (const e of [0.4, 5, 80]) { let t = 0; for (let i = 0; i < 3000; i++) t += countFor(r, e); expect(t / 3000 / e).toBeGreaterThan(0.9); expect(t / 3000 / e).toBeLessThan(1.1); } expect(countFor(r, 0)).toBe(0); });
});
describe('formatting', () => {
  it.each([[0, '0'], [999, '999'], [1000, '1K'], [1234, '1.23K'], [15600, '15.6K'], [999999, '999K'], [1e6, '1M'], [2.5e6, '2.5M'], [212e6, '212M'], [3.2e9, '3.2B'], [-1500, '-1.5K'], [10.9, '10']])('fmt(%s) = %s', (n, s) => expect(fmt(n)).toBe(s));
  it.each([[5, '$5'], [4.5, '$4.50'], [1234, '$1,234'], [-20, '-$20'], [250000, '$250K'], [4e6, '$4M']])('money(%s) = %s', (n, s) => expect(money(n)).toBe(s));
  it('clamp and lerp', () => { expect(clamp(2)).toBe(1); expect(clamp(-1)).toBe(0); expect(clamp(50, 0, 100)).toBe(50); expect(lerp(0, 10, 0.3)).toBeCloseTo(3); });
});
