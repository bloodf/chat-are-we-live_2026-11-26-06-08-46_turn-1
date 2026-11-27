/** Seeded, serialisable RNG (mulberry32). All gameplay randomness flows through this. */
export class RNG {
  constructor(public s: number = 1) { this.s = s >>> 0; }
  next(): number { this.s = (this.s + 0x6d2b79f5) >>> 0; let t = this.s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
  range(a: number, b: number) { return a + (b - a) * this.next(); }
  int(a: number, b: number) { return Math.floor(this.range(a, b + 1)); }
  chance(p: number) { return this.next() < p; }
  pick<T>(a: readonly T[]): T { if (!a.length) throw new Error('pick from empty list'); return a[Math.floor(this.next() * a.length)]; }
  weighted<T>(items: readonly T[], w: (t: T) => number): T {
    if (!items.length) throw new Error('weighted pick from empty list');
    let total = 0; const ws = items.map((i) => { const v = Math.max(0, w(i)); total += v; return v; });
    if (total <= 0) return this.pick(items);
    let r = this.next() * total;
    for (let i = 0; i < items.length; i++) { r -= ws[i]; if (r <= 0) return items[i]; }
    return items[items.length - 1];
  }
  gauss(mu = 0, sd = 1) { const u = 1 - this.next(), v = this.next(); return mu + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  lognormal(median: number, sigma: number) { return median * Math.exp(this.gauss(0, sigma)); }
  shuffle<T>(a: readonly T[]): T[] { const r = a.slice(); for (let i = r.length - 1; i > 0; i--) { const j = this.int(0, i); [r[i], r[j]] = [r[j], r[i]]; } return r; }
  sample<T>(a: readonly T[], n: number): T[] { return this.shuffle(a).slice(0, n); }
  fork() { return new RNG(Math.floor(this.next() * 4294967296)); }
  id(prefix = '') { return prefix + Math.floor(this.next() * 0xffffffff).toString(36); }
}
export const clamp = (v: number, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
/** Poisson-ish event count for a rate over dt. */
export function countFor(rng: RNG, expected: number): number { if (expected > 30) return Math.max(0, Math.round(rng.gauss(expected, Math.sqrt(expected)))); let n = 0; let p = Math.exp(-expected); let s = p; const u = rng.next(); while (u > s && n < 200) { n++; p *= expected / n; s += p; } return n; }
export function fmt(n: number): string {
  const a = Math.abs(n); const sg = n < 0 ? '-' : '';
  if (a < 1000) return sg + Math.floor(a).toString();
  const u: [number, string][] = [[1e9, 'B'], [1e6, 'M'], [1e3, 'K']];
  for (const [v, s] of u) if (a >= v) { const x = a / v; const d = x < 10 ? 2 : x < 100 ? 1 : 0; const f = 10 ** d; return sg + (Math.floor(x * f + 1e-9) / f).toFixed(d).replace(/\.0+$|(\.\d*[1-9])0+$/, '$1') + s; }
  return sg + a;
}
export function money(n: number): string { const a = Math.abs(n); const s = n < 0 ? '-$' : '$'; if (a >= 100000) return s + fmt(a); return s + (a < 100 && a % 1 !== 0 ? a.toFixed(2) : Math.round(a).toLocaleString('en-US')); }
